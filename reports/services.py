"""
Service layer for the Reports endpoint.

``generate_report`` takes a validated filter spec and returns a
dict with one section per entity, each section being a paginated
list of matching rows.

Sections are built independently — there's no cross-entity JOIN.
The frontend can render each section however it likes (table, list,
side-by-side columns, etc.).

For any feature with both a numeric id and a human name (e.g.
``company_ids`` and ``company_names``), the two forms are
OR'd into a single Q so the user can mix and match.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List

from django.db.models import Exists, OuterRef, Q, QuerySet
from django.utils import timezone

from api.models import Contract, User_Status, Users
from companies.models import Company, JobOrder, JobOrderPosition
from companies.serializers import CompanySerializer, JobOrderPositionSerializer, JobOrderSerializer
from core.models import Flag
from ships.models import Ship
from ships.serializers import ShipSerializer
from api.serializer import UsersSerializer


# Cap rows per section so a careless frontend can't accidentally
# pull 100k records in one request. The frontend can paginate /
# re-filter for more.
DEFAULT_LIMIT = 500


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _or_id_name(
    *,
    ids: Iterable,
    names: Iterable,
    id_q: Q,
    name_q_for: List[Q],
) -> Q:
    """
    Build ``id_q | OR(name_q)``.

    Returns an empty Q when both inputs are empty, so callers can
    use ``qs = qs.filter(q) if q else qs`` to keep the queryset
    untouched when the caller didn't supply either form.
    """
    q = Q()
    if ids:
        q |= id_q
    for nq in name_q_for:
        q |= nq
    return q


# ---------------------------------------------------------------------------
# Per-entity queryset builders
# ---------------------------------------------------------------------------


def _job_orders_qs(filters: Dict[str, Any]) -> QuerySet:
    qs = JobOrder.objects.select_related("company", "ship").prefetch_related(
        "positions__rank",
    )

    # Company: id OR name
    company_q = _or_id_name(
        ids=filters.get("company_ids"),
        names=filters.get("company_names"),
        id_q=Q(company_id__in=list(filters.get("company_ids") or [])),
        name_q_for=[
            Q(company__company_name__icontains=n)
            for n in (filters.get("company_names") or [])
            if str(n).strip()
        ],
    )
    qs = qs.filter(company_q) if company_q else qs

    # Ship: id OR name
    ship_q = _or_id_name(
        ids=filters.get("ship_ids"),
        names=filters.get("ship_names"),
        id_q=Q(ship_id__in=list(filters.get("ship_ids") or [])),
        name_q_for=[
            Q(ship__ship_name__icontains=n)
            for n in (filters.get("ship_names") or [])
            if str(n).strip()
        ],
    )
    qs = qs.filter(ship_q) if ship_q else qs

    if filters.get("statuses"):
        qs = qs.filter(status__in=filters["statuses"])

    # Rank: id OR name (name matches either Rank.name or Rank.code)
    rank_ids = filters.get("rank_ids") or []
    rank_names = [n for n in (filters.get("rank_names") or []) if str(n).strip()]
    if rank_ids or rank_names:
        rank_filter = Q()
        if rank_ids:
            # Job order has at least one position with one of these ranks.
            rank_filter |= Exists(
                JobOrderPosition.objects.filter(
                    job_order=OuterRef("pk"),
                    rank_id__in=rank_ids,
                )
            )
        if rank_names:
            name_q = Q()
            for n in rank_names:
                name_q |= Q(positions__rank__name__icontains=n) | Q(
                    positions__rank__code__icontains=n
                )
            # Wrap as a single Exists for the position-with-rank subquery
            rank_filter &= Exists(
                JobOrderPosition.objects.filter(
                    Q(job_order=OuterRef("pk")) & (
                        Q(rank__name__icontains=rank_names[0])
                        | Q(rank__code__icontains=rank_names[0])
                    )
                )
            )
            # If multiple names, OR them inside the Exists
            if len(rank_names) > 1:
                or_q = Q()
                for n in rank_names:
                    or_q |= Q(rank__name__icontains=n) | Q(rank__code__icontains=n)
                rank_filter = Exists(
                    JobOrderPosition.objects.filter(
                        Q(job_order=OuterRef("pk")) & or_q
                    )
                )
        qs = qs.filter(rank_filter)

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

    company_type_q = _or_id_name(
        ids=filters.get("company_type_ids"),
        names=filters.get("company_type_names"),
        id_q=Q(company_type_id__in=list(filters.get("company_type_ids") or [])),
        name_q_for=[
            Q(company_type__name__icontains=n)
            for n in (filters.get("company_type_names") or [])
            if str(n).strip()
        ],
    )
    qs = qs.filter(company_type_q) if company_type_q else qs

    country_q = _or_id_name(
        ids=filters.get("country_ids"),
        names=filters.get("country_names"),
        id_q=Q(company_flag_id__in=list(filters.get("country_ids") or [])),
        name_q_for=[
            Q(company_flag__name__icontains=n)
            for n in (filters.get("country_names") or [])
            if str(n).strip()
        ],
    )
    qs = qs.filter(country_q) if country_q else qs

    if filters.get("statuses"):
        qs = qs.filter(status__in=filters["statuses"])
    return qs.order_by("company_name")[:DEFAULT_LIMIT]


def _ships_qs(filters: Dict[str, Any]) -> QuerySet:
    qs = Ship.objects.select_related("company", "ship_type", "flag")

    company_q = _or_id_name(
        ids=filters.get("company_ids"),
        names=filters.get("company_names"),
        id_q=Q(company_id__in=list(filters.get("company_ids") or [])),
        name_q_for=[
            Q(company__company_name__icontains=n)
            for n in (filters.get("company_names") or [])
            if str(n).strip()
        ],
    )
    qs = qs.filter(company_q) if company_q else qs

    ship_type_q = _or_id_name(
        ids=filters.get("ship_type_ids"),
        names=filters.get("ship_type_names"),
        id_q=Q(ship_type_id__in=list(filters.get("ship_type_ids") or [])),
        name_q_for=[
            Q(ship_type__name__icontains=n)
            for n in (filters.get("ship_type_names") or [])
            if str(n).strip()
        ],
    )
    qs = qs.filter(ship_type_q) if ship_type_q else qs

    flag_q = _or_id_name(
        ids=filters.get("flag_ids"),
        names=filters.get("flag_names"),
        id_q=Q(flag_id__in=list(filters.get("flag_ids") or [])),
        name_q_for=[
            Q(flag__name__icontains=n)
            for n in (filters.get("flag_names") or [])
            if str(n).strip()
        ],
    )
    qs = qs.filter(flag_q) if flag_q else qs

    if filters.get("year_built_from") is not None:
        qs = qs.filter(year_built__gte=filters["year_built_from"])
    if filters.get("year_built_to") is not None:
        qs = qs.filter(year_built__lte=filters["year_built_to"])
    return qs.order_by("ship_name")[:DEFAULT_LIMIT]


def _job_positions_qs(filters: Dict[str, Any]) -> QuerySet:
    """
    Build the ``JobOrderPosition`` queryset for the ``job_positions``
    section. Unlike ``_job_orders_qs`` which matches at the parent
    JO level, this one matches at the position level — every row
    is an individual position.
    """
    qs = JobOrderPosition.objects.select_related(
        "job_order__company",
        "job_order__ship",
        "rank",
    )
    if filters.get("position_ids"):
        qs = qs.filter(id__in=filters["position_ids"])

    rank_names = [n for n in (filters.get("position_rank_names") or []) if str(n).strip()]
    if rank_names:
        or_q = Q()
        for n in rank_names:
            or_q |= Q(rank__name__icontains=n) | Q(rank__code__icontains=n)
        qs = qs.filter(or_q)

    if filters.get("position_company_ids"):
        qs = qs.filter(job_order__company_id__in=filters["position_company_ids"])
    company_names = [n for n in (filters.get("position_company_names") or []) if str(n).strip()]
    if company_names:
        or_q = Q()
        for n in company_names:
            or_q |= Q(job_order__company__company_name__icontains=n)
        qs = qs.filter(or_q)

    if filters.get("position_ship_ids"):
        qs = qs.filter(job_order__ship_id__in=filters["position_ship_ids"])
    ship_names = [n for n in (filters.get("position_ship_names") or []) if str(n).strip()]
    if ship_names:
        or_q = Q()
        for n in ship_names:
            or_q |= Q(job_order__ship__ship_name__icontains=n)
        qs = qs.filter(or_q)

    if filters.get("position_statuses"):
        qs = qs.filter(job_order__status__in=filters["position_statuses"])

    return qs.order_by("job_order__request_date", "rank__name")[:DEFAULT_LIMIT]


def _users_qs(filters: Dict[str, Any]) -> QuerySet:
    """
    Build the user queryset. For ``user_statuses`` we filter on the
    effective 5-state status, which requires the same logic as
    api.filters.filter_user_status — duplicated here so the report
    can run without going through the list endpoint.
    """
    from api.models import UserRank
    qs = Users.objects.all()

    if filters.get("roles"):
        qs = qs.filter(role__in=filters["roles"])

    # Rank: id OR name (name matches Rank.name OR Rank.code)
    rank_ids = filters.get("rank_ids") or []
    rank_names = [n for n in (filters.get("rank_names") or []) if str(n).strip()]
    if rank_ids or rank_names:
        or_q = Q()
        if rank_ids:
            or_q |= Q(rank_id__in=rank_ids)
        for n in rank_names:
            or_q |= Q(rank__name__icontains=n) | Q(rank__code__icontains=n)
        qs = qs.filter(
            Exists(UserRank.objects.filter(Q(user=OuterRef("pk")) & or_q))
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

    jp_filters = validated.get("job_positions") or {}
    if jp_filters:
        rows = JobOrderPositionSerializer(
            _job_positions_qs(jp_filters), many=True
        ).data
        sections["job_positions"] = {
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
