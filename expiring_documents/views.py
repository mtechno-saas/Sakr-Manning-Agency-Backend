"""Views for the Expiring Documents app."""
from datetime import timedelta

from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------

def _categorize(days_to_expiry):
    """
    Bucket an item by how soon it expires.

      expired : days < 0      (already past)
      critical: 0 - 14 days   (renew now)
      warning : 15 - 30 days  (plan renewal)
      notice  : 31 - 90 days  (heads up)
      active  : > 90 days    (not flagged by default window)
    """
    if days_to_expiry is None:
        return "unknown"
    if days_to_expiry < 0:
        return "expired"
    if days_to_expiry <= 14:
        return "critical"
    if days_to_expiry <= 30:
        return "warning"
    if days_to_expiry <= 90:
        return "notice"
    return "active"


def _user_position(user):
    """
    Return the most-recent UserRank's display name for a user, e.g. "Able Seaman".
    Returns None if the user has no rank assigned.
    """
    user_rank = (
        user.user_ranks.select_related("rank").order_by("-id").first()
        if hasattr(user, "user_ranks")
        else None
    )
    if user_rank and user_rank.rank:
        return user_rank.rank.name
    return None


# ----------------------------------------------------------------------------
# User-profile expiry fields (9 fields on the Users model)
# ----------------------------------------------------------------------------

USER_EXPIRY_FIELDS = [
    # (model_field,                  display_type,                number_field)
    ("passport_expiry_date",            "Passport",                          "passport_no"),
    ("seaman_book_expiry_date",         "Seaman's Book",                     "seaman_book_no"),
    ("other_seaman_book_expiry_date",   "Other Seaman's Book",                "other_seaman_book_no"),
    ("coc_expiry_date",                 "Certificate of Competency (COC)",   "coc_certificate_number"),
    ("goc_expiry_date",                 "General Operator Certificate (GOC)", "goc_certificate_number"),
    ("health_expiry_date",              "Health Certificate",                "health_number"),
    ("international_medical_expiry_date", "International Medical",           "international_medical_number"),
    ("yellow_fever_expiry_date",        "Yellow Fever Vaccination",          "yellow_fever_number"),
    ("cholera_expiry_date",             "Cholera Vaccination",               None),
]


# ----------------------------------------------------------------------------
# Endpoint
# ----------------------------------------------------------------------------

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def expiring_documents(request):
    """
    Aggregate all expiring or expired documents across all users in a single
    response. Combines:

      - 9 expiry date fields on the Users model
      - All rows in `PersonalDocument` (any of 30 document types)

    Each item in the response includes:
      - the document name + number
      - the user's full name, email, and primary rank
      - the expiry date
      - days remaining (negative if expired)
      - a category bucket (expired / critical / warning / notice / active)
      - a `source` flag indicating which table it came from

    Query params
    -----------
    days (int, default 30)
        Look-ahead window in days (1 - 365). An item with `expiry_date` in
        `[today, today + days]` AND already-expired items are returned.

    category (str, optional)
        Restrict results to one bucket. Allowed values:
        `expired`, `critical`, `warning`, `notice`, `active`, `all` (default).

    Auth
    ----
    Bearer JWT required. Admin / HR Manager only. Employee and Recruiter
    roles return 403.
    """
    # ---- parse query params ----
    try:
        days = int(request.query_params.get("days", 30))
    except (TypeError, ValueError):
        days = 30
    if days < 1:
        days = 30
    if days > 365:
        days = 365

    category_filter = request.query_params.get("category", None)

    # ---- auth & role check ----
    if not request.user or not request.user.is_authenticated:
        return Response(
            {"error": "Authentication required."},
            status=status.HTTP_401_UNAUTHORIZED,
        )
    if getattr(request.user, "role", None) not in ("Admin", "HR Manager"):
        return Response(
            {"error": "Only Admin and HR Manager can view expiring documents."},
            status=status.HTTP_403_FORBIDDEN,
        )

    today = timezone.localdate()
    soon = today + timedelta(days=days)

    all_items = []

    # =====================================================================
    # Source 1: 9 expiry fields on the Users model
    # =====================================================================
    from api.models import Users, PersonalDocument

    user_q = Q()
    for field, _, _ in USER_EXPIRY_FIELDS:
        user_q |= Q(**{f"{field}__lt": today})
        user_q |= Q(**{f"{field}__gte": today, f"{field}__lte": soon})

    users_with_expiring = (
        Users.objects.filter(user_q)
        .distinct()
        .prefetch_related("user_ranks__rank")
    )

    for user in users_with_expiring:
        user_name = (
            f"{getattr(user, 'first_name', '')} {getattr(user, 'middle_name', '')}"
            .strip()
            or getattr(user, "email", "")
        )
        user_position = _user_position(user)
        for field, doc_type, number_field in USER_EXPIRY_FIELDS:
            expiry = getattr(user, field, None)
            if not expiry:
                continue
            if not (expiry < today or today <= expiry <= soon):
                continue

            days_to_expiry = (expiry - today).days
            cat = _categorize(days_to_expiry)
            if category_filter and category_filter != "all" and cat != category_filter:
                continue

            doc_number = getattr(user, number_field, None) if number_field else None
            all_items.append({
                "id": f"user_{user.id}_{field}",
                "type": doc_type,
                "name": f"{doc_type} - {doc_number or 'N/A'}",
                "number": doc_number or "N/A",
                "user": user_name,
                "userId": user.id,
                "userEmail": user.email,
                "userPosition": user_position,
                "expiryDate": expiry.isoformat(),
                "daysToExpiry": days_to_expiry,
                "category": cat,
                "source": "user_profile",
            })

    # =====================================================================
    # Source 2: PersonalDocument table (30 document types)
    # =====================================================================
    personal_docs = (
        PersonalDocument.objects
        .select_related("user")
        .prefetch_related("user__user_ranks__rank")
        .filter(expiry_date__lte=soon)
    )

    for doc in personal_docs:
        if not doc.expiry_date:
            continue
        days_to_expiry = (doc.expiry_date - today).days
        cat = _categorize(days_to_expiry)
        if category_filter and category_filter != "all" and cat != category_filter:
            continue

        if doc.user:
            user_name = (
                f"{getattr(doc.user, 'first_name', '')} {getattr(doc.user, 'middle_name', '')}"
                .strip()
                or getattr(doc.user, "email", "Unknown")
            )
            user_email = doc.user.email
            user_id = doc.user_id
            user_position = _user_position(doc.user)
        else:
            user_name = "Unknown"
            user_email = None
            user_id = None
            user_position = None

        all_items.append({
            "id": f"pd_{doc.id}",
            "type": doc.document_type or "Personal Document",
            "name": f"{doc.document_type or 'Document'} - {doc.document_number or 'N/A'}",
            "number": doc.document_number or "N/A",
            "user": user_name,
            "userId": user_id,
            "userEmail": user_email,
            "userPosition": user_position,
            "expiryDate": doc.expiry_date.isoformat(),
            "daysToExpiry": days_to_expiry,
            "category": cat,
            "source": "personal_document",
        })

    # ---- sort by urgency: most overdue first, then earliest expiry ----
    all_items.sort(key=lambda x: x["daysToExpiry"])

    counts = {
        "expired":  sum(1 for x in all_items if x["category"] == "expired"),
        "critical": sum(1 for x in all_items if x["category"] == "critical"),
        "warning":  sum(1 for x in all_items if x["category"] == "warning"),
        "notice":   sum(1 for x in all_items if x["category"] == "notice"),
        "active":   sum(1 for x in all_items if x["category"] == "active"),
        "total":    len(all_items),
    }

    return Response({
        "counts": counts,
        "days_window": days,
        "today": today.isoformat(),
        "category_filter": category_filter or "all",
        "results": all_items,
    })
