"""
Service layer for the Reports endpoint.

``generate_report`` takes a validated filter spec and returns a
dict with one section per entity, each section being a paginated
list of matching rows.

Sections are built independently — there's no cross-entity JOIN.
The frontend can render each section however it likes (table, list,
side-by-side columns, etc.).
"""
from __future__ import annotations

from typing import Any, Dict

from django.db.models import Exists, OuterRef, Q, QuerySet
from django.utils import timezone

from api.models import Contract, User_Status, Users
from companies.models import Company, JobOrder, JobOrderPosition
from companies.serializers import CompanySerializer, JobOrderSerializer
from core.models import Flag
from ships.models import Ship
from ships.serializers import ShipSerializer
from api.serializer import UsersSerializer


# Cap rows per section so a careless frontend can't accidentally
# pull 100k records in one request. The frontend can paginate /
# re-filter for more.
DEFAULT_LIMIT = 500


# ---------------------------------------------------------------------------
# Per-entity queryset builders
# ---------------------------------------------------------------------------


def _job_orders_qs(filters: Dict[str, Any]) -> QuerySet:
    qs = JobOrder.objects.select_related("company", "ship").prefetch_related(
        "positions__rank",
    )
    if filters.get("company_ids"):
        qs = qs.filter(company_id__in=filters["company_ids"])
    if filters.get("ship_ids"):
        qs = qs.filter(ship_id__in=filters["ship_ids"])
    if filters.get("statuses"):
        qs = qs.filter(status__in=filters["statuses"])
    if filters.get("rank_ids"):
        # Job order has at least one position with one of these ranks.
        qs = qs.filter(
            Exists(
                JobOrderPosition.objects.filter(
                    job_order=OuterRef("pk"),
                    rank_id__in=filters["rank_ids"],
                )
            )
        )
    if filters.get("request_date_from"):
        qs = qs.filter(request_date__gte=filters["request_date_from"])
    if filters.get("request_date_to"):
        qs = qs.filter(request_date__lte=filters["request_date_to"])
    if filters.get("target_join_date_from"):
        qs = qs.filter(target_joining_date__gte=filters["target_join_date_from"])
    if filters.get("target_join_date_to"):
        qs = qs.filter(target_joining_date__lte=filters["target_join_date_to"])
    return qs.order_by("-request_date", "reference_number")[:DEFAULT_LIMIT]


def _companies_qs(filters: Dict[str, Any]) -> QuerySet:
    qs = Company.objects.select_related("company_type", "company_flag")
    if filters.get("company_type_ids"):
        qs = qs.filter(company_type_id__in=filters["company_type_ids"])
    if filters.get("country_ids"):
        qs = qs.filter(company_flag_id__in=filters["country_ids"])
    if filters.get("statuses"):
        qs = qs.filter(status__in=filters["statuses"])
    return qs.order_by("company_name")[:DEFAULT_LIMIT]


def _ships_qs(filters: Dict[str, Any]) -> QuerySet:
    qs = Ship.objects.select_related("company", "ship_type", "flag")
    if filters.get("company_ids"):
        qs = qs.filter(company_id__in=filters["company_ids"])
    if filters.get("ship_type_ids"):
        qs = qs.filter(ship_type_id__in=filters["ship_type_ids"])
    if filters.get("flag_ids"):
        qs = qs.filter(flag_id__in=filters["flag_ids"])
    if filters.get("year_built_from") is not None:
        qs = qs.filter(year_built__gte=filters["year_built_from"])
    if filters.get("year_built_to") is not None:
        qs = qs.filter(year_built__lte=filters["year_built_to"])
    return qs.order_by("ship_name")[:DEFAULT_LIMIT]


def _users_qs(filters: Dict[str, Any]) -> QuerySet:
    """
    Build the user queryset. For ``user_statuses`` we filter on the
    effective 5-state status, which requires the same logic as
    api.filters.filter_user_status — duplicated here so the report
    can run without going through the list endpoint.
    """
    qs = Users.objects.all()
    if filters.get("roles"):
        qs = qs.filter(role__in=filters["roles"])
    if filters.get("rank_ids"):
        # Users with a UserRank row pointing at any of these ranks.
        from api.models import UserRank
        qs = qs.filter(
            Exists(
                UserRank.objects.filter(
                    user=OuterRef("pk"),
                    rank_id__in=filters["rank_ids"],
                )
            )
        )
    if filters.get("nationalities"):
        nat_q = Q()
        for n in filters["nationalities"]:
            nat_q |= Q(nationality__icontains=n)
        qs = qs.filter(nat_q)
    if filters.get("is_blacklisted") is not None:
        qs = qs.filter(is_blacklisted=filters["is_blacklisted"])

    # Effective-status filtering
    statuses = filters.get("user_statuses") or []
    if statuses:
        manual_block = (
            Q(user_status=User_Status.VACATION.value)
            | Q(user_status=User_Status.MEDICAL_VACATION.value)
        )
        stored_vals = [s for s in statuses
                       if s in ("ON_SITE", "VACATION", "MEDICAL_VACATION")]
        wants_on_board = "ON_BOARD" in statuses
        wants_new_applicant = "NEW_APPLICANT" in statuses

        status_q = Q()
        for s in stored_vals:
            if s == User_Status.ON_SITE.value:
                # Effective ON_SITE = stored=ON_SITE, has any contract,
                # has no active contract.
                has_any_contract = Exists(
                    Contract.objects.filter(user=OuterRef("pk"))
                )
                today = timezone.localdate()
                has_active = Exists(
                    Contract.objects.filter(
                        user=OuterRef("pk"),
                        status__in=("Active", "Signed"),
                    ).filter(
                        Q(sign_off_date__isnull=True)
                        | Q(sign_off_date__gte=today)
                    )
                )
                status_q |= (
                    Q(user_status=User_Status.ON_SITE.value)
                    & Q(pk__in=Users.objects.filter(has_any_contract).values("pk"))
                    & ~Q(pk__in=Users.objects.filter(has_active).values("pk"))
                )
            else:
                # VACATION / MEDICAL_VACATION are admin overrides
                status_q |= Q(user_status=s)
        if wants_on_board:
            today = timezone.localdate()
            contract_q = (
                Q(contracts__status__in=("Active", "Signed"))
                & (Q(contracts__sign_off_date__isnull=True)
                   | Q(contracts__sign_off_date__gte=today))
            )
            status_q |= (~manual_block & contract_q)
        if wants_new_applicant:
            no_contracts = ~Exists(
                Contract.objects.filter(user=OuterRef("pk"))
            )
            status_q |= (
                ~manual_block
                & Q(pk__in=Users.objects.filter(no_contracts).values("pk"))
            )
        qs = qs.filter(status_q).distinct()

    return qs.order_by("-created_at")[:DEFAULT_LIMIT]


# ---------------------------------------------------------------------------
# Top-level entry point
# ---------------------------------------------------------------------------


def generate_report(validated: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build the report response.

    ``validated`` is the dict produced by
    ``ReportGenerateRequestSerializer.validated_data``.
    """
    sections: Dict[str, Any] = {}

    jo_filters = validated.get("job_orders") or {}
    if jo_filters:
        rows = JobOrderSerializer(_job_orders_qs(jo_filters), many=True).data
        sections["job_orders"] = {
            "total_records": len(rows),
            "rows": rows,
        }

    co_filters = validated.get("companies") or {}
    if co_filters:
        rows = CompanySerializer(_companies_qs(co_filters), many=True).data
        sections["companies"] = {
            "total_records": len(rows),
            "rows": rows,
        }

    sh_filters = validated.get("ships") or {}
    if sh_filters:
        rows = ShipSerializer(_ships_qs(sh_filters), many=True).data
        sections["ships"] = {
            "total_records": len(rows),
            "rows": rows,
        }

    us_filters = validated.get("users") or {}
    if us_filters:
        rows = UsersSerializer(_users_qs(us_filters), many=True).data
        sections["users"] = {
            "total_records": len(rows),
            "rows": rows,
        }

    return {
        "generated_at": timezone.now().isoformat(),
        "limit_per_section": DEFAULT_LIMIT,
        "sections": sections,
    }
