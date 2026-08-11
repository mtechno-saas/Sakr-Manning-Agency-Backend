"""Views for the Expiring Documents app."""
import re

from datetime import timedelta

from django.conf import settings
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


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

USER_EXPIRY_FIELD_NAMES = {f[0] for f in USER_EXPIRY_FIELDS}

# IDs in the GET response look like:
#   user_<user_id>_<expiry_field>   -> Users model field
#   pd_<doc_id>                     -> PersonalDocument row
_ID_USER_RE = re.compile(r"^user_(\d+)_(.+)$")
_ID_PD_RE = re.compile(r"^pd_(\d+)$")


# ----------------------------------------------------------------------------
# Endpoint
# ----------------------------------------------------------------------------

class ExpiringDocumentsView(APIView):
    """
    Combined endpoint for the Expiring Documents dashboard.

    Methods
    -------
    GET  /api/expiring-documents/
        Aggregate all expiring/expired documents across all users.
        Combines 9 expiry date fields on Users + every PersonalDocument
        row. Each item includes the document name + number, the user's
        full name, email, primary rank, expiry date, days remaining,
        a category bucket, and a `source` flag.

    POST /api/expiring-documents/
        Upload a NEW personal document (file + metadata + expiry_date).
        Multipart form data. Creates a PersonalDocument row that will
        appear in subsequent GET responses.

    PATCH /api/expiring-documents/<id>/
        Update the expiry date (and other mutable fields) of an
        existing item, where `<id>` matches one of the `id` values
        returned by GET:
          - `user_<user_id>_<field>`   -> updates the corresponding
            expiry field on the Users model
          - `pd_<doc_id>`              -> updates the PersonalDocument
        Body for personal documents: any subset of PersonalDocument
        fields (expiry_date, document_number, etc.).
        Body for user_profile: `{"expiry_date": "YYYY-MM-DD"}` — the
        endpoint writes it to the right field on the right user.

    Query params (GET only)
    -----------------------
    days (int, default 30)
        Look-ahead window in days (1 - 365). Items with `expiry_date`
        in `[today, today + days]` AND already-expired items are
        returned.
    category (str, optional)
        Restrict results to one bucket. Allowed values: `expired`,
        `critical`, `warning`, `notice`, `active`, `all` (default).

    Auth
    ----
    Bearer JWT required. Admin / HR Manager only. Employee and
    Recruiter roles return 403 (Recruiter can read individual users
    and personal docs through their own endpoints, but not this
    cross-user aggregator).
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def _role_check(self, request):
        """Returns a Response if rejected, None if allowed."""
        if not request.user or not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if getattr(request.user, "role", None) not in ("Admin", "HR Manager"):
            return Response(
                {"error": "Only Admin and HR Manager can access this."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return None

    # ------------------------------------------------------------------------
    # GET
    # ------------------------------------------------------------------------

    def get(self, request):
        """List all expiring/expired items across all users."""
        role_err = self._role_check(request)
        if role_err is not None:
            return role_err

        # ---- parse query params ----
        # Read the look-ahead window defaults from Django settings so
        # ops can tune them via env vars without a code change.
        default_days = getattr(
            settings, "EXPIRING_DOCUMENTS_DEFAULT_DAYS", 30
        )
        min_days = max(1, getattr(settings, "EXPIRING_DOCUMENTS_MIN_DAYS", 1))
        max_days = max(min_days, getattr(
            settings, "EXPIRING_DOCUMENTS_MAX_DAYS", 365
        ))

        try:
            days = int(request.query_params.get("days", default_days))
        except (TypeError, ValueError):
            days = default_days
        if days < min_days:
            days = default_days
        if days > max_days:
            days = max_days

        category_filter = request.query_params.get("category", None)

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

        # ---- sort by urgency ----
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

    # ------------------------------------------------------------------------
    # POST  -> create a NEW personal document
    # ------------------------------------------------------------------------

    def post(self, request, *args, **kwargs):
        """
        Create a new PersonalDocument row. The body is the same as
        `POST /api/personal-documents/` — multipart with at minimum
        `user`, `document_type`, `expiry_date`, and `file`.

        The newly created row will show up in subsequent GET
        responses with id `pd_<new_id>`.

        Note
        ----
        POST must be sent to the BASE URL (`/api/expiring-documents/`).
        If the requester hits a detail URL by mistake (e.g.
        `/api/expiring-documents/56/`) we return 400 with a clear
        message instead of crashing the view. The base URL has no
        URL kwargs; the detail URL always has `item_id`.
        """
        # Reject POSTs sent to the detail URL by mistake. The
        # `item_id` kwarg is only present on the detail route.
        if kwargs.get("item_id"):
            return Response(
                {"error": (
                    "POST must be sent to /api/expiring-documents/ "
                    "(no id in the URL). The 'user' field belongs in "
                    "the request body, not the URL."
                )},
                status=status.HTTP_400_BAD_REQUEST,
            )

        role_err = self._role_check(request)
        if role_err is not None:
            return role_err

        from api.models import PersonalDocument
        from api.serializer import PersonalDocumentSerializer

        serializer = PersonalDocumentSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # ------------------------------------------------------------------------
    # PATCH /<id>/  -> update an existing item
    # ------------------------------------------------------------------------

    def patch(self, request, item_id):
        """
        Update the expiry (and other fields) of an item identified
        by `id` from the GET response.

        - `user_<user_id>_<field>`: writes `expiry_date` (or any
          other allowed field) onto the Users row.
        - `pd_<doc_id>`: standard PersonalDocumentSerializer
          partial update — any subset of fields.
        """
        role_err = self._role_check(request)
        if role_err is not None:
            return role_err

        from api.models import PersonalDocument, Users
        from api.serializer import PersonalDocumentSerializer

        # --- PersonalDocument: pd_<id> -------------------------------------
        m_pd = _ID_PD_RE.match(item_id or "")
        if m_pd:
            doc_id = int(m_pd.group(1))
            doc = get_object_or_404(PersonalDocument, pk=doc_id)
            serializer = PersonalDocumentSerializer(
                doc, data=request.data, partial=True,
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

        # --- Users field: user_<id>_<field> --------------------------------
        m_user = _ID_USER_RE.match(item_id or "")
        if m_user:
            user_id = int(m_user.group(1))
            field = m_user.group(2)

            if field not in USER_EXPIRY_FIELD_NAMES:
                return Response(
                    {"error": (
                        f"Unknown user_profile field {field!r}. "
                        f"Allowed: {sorted(USER_EXPIRY_FIELD_NAMES)}"
                    )},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Accept either the canonical field name or the friendlier
            # "expiry_date" alias.
            value = request.data.get(field)
            if value is None:
                value = request.data.get("expiry_date")
            if value is None:
                return Response(
                    {"error": (
                        f"Provide a value for {field!r} (or use the "
                        f"alias 'expiry_date')."
                    )},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user = get_object_or_404(Users, pk=user_id)
            setattr(user, field, value)
            user.save(update_fields=[field, "updated_at"] if hasattr(user, "updated_at") else [field])
            return Response({
                "id": item_id,
                "source": "user_profile",
                "field": field,
                "userId": user.id,
                "value": value,
            })

        return Response(
            {"error": (
                f"Unrecognised id {item_id!r}. Expected "
                f"'user_<user_id>_<field>' or 'pd_<doc_id>'."
            )},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ------------------------------------------------------------------------
    # DELETE /<id>/  -> delete an existing item
    # ------------------------------------------------------------------------

    def delete(self, request, item_id):
        """
        Delete the item identified by `id`.

        - `pd_<doc_id>`: hard-deletes the PersonalDocument row. The
          row stops appearing in subsequent GET responses.
        - `user_<id>_<field>`: returns 400 — you cannot "delete" a
          user-profile field, only clear it (use PATCH with
          `{"expiry_date": null}` for that).
        """
        role_err = self._role_check(request)
        if role_err is not None:
            return role_err

        from api.models import PersonalDocument

        m_pd = _ID_PD_RE.match(item_id or "")
        if m_pd:
            doc_id = int(m_pd.group(1))
            doc = get_object_or_404(PersonalDocument, pk=doc_id)
            doc.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        m_user = _ID_USER_RE.match(item_id or "")
        if m_user:
            return Response(
                {"error": (
                    "Cannot DELETE a user_profile row. To clear an "
                    "expiry date on a user field, use PATCH with "
                    "{\"expiry_date\": null}."
                )},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"error": (
                f"Unrecognised id {item_id!r}. Expected "
                f"'user_<user_id>_<field>' or 'pd_<doc_id>'."
            )},
            status=status.HTTP_400_BAD_REQUEST,
        )
