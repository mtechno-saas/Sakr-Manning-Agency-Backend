"""
Service layer for the Historical Data for Companies endpoint.

All four analysis sections (summary / time_series / top_n /
breakdowns / per_company_timeline) are built here from the same
filtered base querysets so they all respect the same date range
and company filter.

Date semantics
--------------
- ``date_from`` is inclusive
- ``date_to`` is inclusive
- A "contract signed" event falls in the range if its
  ``sign_on_date`` is in [date_from, date_to]
- A "contract ended" event falls in the range if its
  ``sign_off_date`` is in [date_from, date_to]
- A "job order" event falls in the range if its
  ``request_date`` is in [date_from, date_to]
- For summary / breakdown sections, the date range still
  filters contracts/positions; companies themselves are NOT
  filtered by the date range (a company that exists outside the
  range still shows up in the breakdowns).
"""
from __future__ import annotations

import datetime
from collections import OrderedDict
from typing import Any, Dict, List

from django.db.models import (
    Count, Exists, F, OuterRef, Q, Sum, Value,
)
from django.db.models.functions import Coalesce, TruncMonth, TruncQuarter, TruncYear

from api.models import Contract, Rank, Users
from companies.models import Company, JobOrder, JobOrderPosition
from core.models import Flag


# ---------------------------------------------------------------------------
# Date helpers
# ---------------------------------------------------------------------------


def _parse_date(s: str) -> datetime.date:
    return datetime.date.fromisoformat(s)


def _default_range() -> tuple:
    """Last 12 months, inclusive."""
    today = datetime.date.today()
    first = today.replace(day=1)
    # 12 months back
    year = first.year
    month = first.month - 11
    while month <= 0:
        month += 12
        year -= 1
    return datetime.date(year, month, 1), today


# ---------------------------------------------------------------------------
# Period helpers (for time-series bucketing)
# ---------------------------------------------------------------------------


def _trunc_for_granularity(granularity: str):
    """Map a granularity name to a Trunc* expression."""
    return {
        "month": TruncMonth,
        "quarter": TruncQuarter,
        "year": TruncYear,
    }.get(granularity, TruncMonth)


def _period_label(d: datetime.date, granularity: str) -> str:
    """Stable string key for one bucket (used to merge rows in Python)."""
    if not d:
        return ""
    if granularity == "month":
        return d.strftime("%Y-%m")
    if granularity == "quarter":
        q = (d.month - 1) // 3 + 1
        return f"{d.year}-Q{q}"
    if granularity == "year":
        return str(d.year)
    return d.isoformat()


# ---------------------------------------------------------------------------
# Filtered base querysets
# ---------------------------------------------------------------------------


def _company_qs(filters: Dict[str, Any]):
    """Companies matching the company_id/name filters (if any).
    Used as the basis for company-scoped analyses."""
    qs = Company.objects.all()
    if filters.get("company_ids"):
        qs = qs.filter(id__in=filters["company_ids"])
    company_names = [n for n in (filters.get("company_names") or []) if str(n).strip()]
    if company_names:
        or_q = Q()
        for n in company_names:
            or_q |= Q(company_name__icontains=n)
        qs = qs.filter(or_q)
    return qs


def _contract_qs(filters: Dict[str, Any]):
    """Contracts whose sign_on_date falls in [date_from, date_to],
    scoped to the filtered companies (if any)."""
    qs = Contract.objects.all()
    if filters.get("date_from"):
        qs = qs.filter(sign_on_date__gte=filters["date_from"])
    if filters.get("date_to"):
        qs = qs.filter(sign_on_date__lte=filters["date_to"])
    company_qs = _company_qs(filters)
    if company_qs.explain().__class__ and (filters.get("company_ids") or filters.get("company_names")):
        # Restrict contracts to those whose `company` is in the
        # filtered set. We also include contracts where the
        # JO's company is filtered (since contracts can hang off
        # a JO whose company is the filtered one).
        from companies.models import JobOrderPosition
        qs = qs.filter(
            Q(company__in=company_qs) |
            Q(job_position__job_order__company__in=company_qs)
        )
    return qs


def _job_order_qs(filters: Dict[str, Any]):
    """Job orders whose request_date falls in [date_from, date_to]."""
    qs = JobOrder.objects.all()
    if filters.get("date_from"):
        qs = qs.filter(request_date__gte=filters["date_from"])
    if filters.get("date_to"):
        qs = qs.filter(request_date__lte=filters["date_to"])
    if filters.get("company_ids") or filters.get("company_names"):
        company_qs = _company_qs(filters)
        qs = qs.filter(company__in=company_qs)
    return qs


# ---------------------------------------------------------------------------
# 1. summary
# ---------------------------------------------------------------------------


def _build_summary(filters: Dict[str, Any]) -> Dict[str, Any]:
    companies_total = _company_qs(filters).count()
    companies_active = _company_qs(filters).filter(status="Active").count()
    job_orders = _job_order_qs(filters).count()
    contracts = _contract_qs(filters).count()
    # Crew placed = distinct users with at least one contract in range
    crew_placed = _contract_qs(filters).values("user_id").distinct().count()
    # Open positions: sum of quantity for positions under job orders
    # in the date range, where filled_slots < quantity.
    jo_qs = _job_order_qs(filters)
    positions = JobOrderPosition.objects.filter(job_order__in=jo_qs)
    position_rows = positions.annotate(
        n_contracts=Count(
            "contracts",
            filter=Q(contracts__status__in=["Active", "Signed"]),
        )
    )
    open_positions = 0
    for p in position_rows:
        remaining = max(0, (p.quantity or 0) - (p.n_contracts or 0))
        if remaining > 0:
            open_positions += remaining
    return {
        "companies_total": companies_total,
        "companies_active": companies_active,
        "job_orders": job_orders,
        "contracts": contracts,
        "crew_placed": crew_placed,
        "open_positions": open_positions,
        "date_from": filters["date_from"].isoformat(),
        "date_to": filters["date_to"].isoformat(),
        "granularity": filters.get("granularity", "month"),
    }


# ---------------------------------------------------------------------------
# 2. time_series
# ---------------------------------------------------------------------------


def _build_time_series(filters: Dict[str, Any]) -> Dict[str, Any]:
    granularity = filters.get("granularity", "month")
    trunc = _trunc_for_granularity(granularity)
    date_from = filters["date_from"]
    date_to = filters["date_to"]

    # Contracts signed per period
    contracts_qs = _contract_qs(filters).annotate(
        period=trunc("sign_on_date"),
    ).values("period").annotate(
        signed=Count("id"),
        active_signed=Count("id", filter=Q(status__in=["Active", "Signed"])),
    ).order_by("period")

    # Contracts ended per period (sign_off_date in range)
    contracts_ended_qs = Contract.objects.all()
    if filters.get("date_from"):
        contracts_ended_qs = contracts_ended_qs.filter(
            sign_off_date__gte=filters["date_from"]
        )
    if filters.get("date_to"):
        contracts_ended_qs = contracts_ended_qs.filter(
            sign_off_date__lte=filters["date_to"]
        )
    if filters.get("company_ids") or filters.get("company_names"):
        company_qs = _company_qs(filters)
        contracts_ended_qs = contracts_ended_qs.filter(
            Q(company__in=company_qs) |
            Q(job_position__job_order__company__in=company_qs)
        )
    ended_agg = dict(
        contracts_ended_qs.exclude(sign_off_date__isnull=True)
        .annotate(period=trunc("sign_off_date"))
        .values_list("period")
        .annotate(n=Count("id"))
    )

    # Job orders created per period
    jo_qs = _job_order_qs(filters).annotate(
        period=trunc("request_date"),
    ).values("period").annotate(
        created=Count("id"),
    ).order_by("period")

    # Build a unified period list spanning the full date range so
    # the chart has no gaps.
    periods = list(_iter_periods(date_from, date_to, granularity))
    period_index = {p: i for i, p in enumerate(periods)}

    # Trunc* returns a date object (e.g. 2026-01-01 for Jan 2026);
    # _iter_periods yields a string key (e.g. "2026-01"). Convert
    # the queryset rows' period into the string form so the dict
    # lookups below work.
    def _key(d):
        if d is None:
            return None
        return _period_label(d, granularity)

    signed_map = {
        _key(p["period"]): p for p in contracts_qs if p["period"]
    }
    jo_map = {
        _key(p["period"]): p for p in jo_qs if p["period"]
    }

    # ended_agg has date keys too
    ended_by_key = {_key(k): v for k, v in ended_agg.items()}

    contracts_over_time: List[Dict[str, Any]] = []
    for p in periods:
        signed_row = signed_map.get(p)
        contracts_over_time.append({
            "period": p,
            "signed": (signed_row or {}).get("signed", 0) or 0,
            "active_signed": (signed_row or {}).get("active_signed", 0) or 0,
            "ended": ended_by_key.get(p, 0) or 0,
        })

    job_orders_over_time: List[Dict[str, Any]] = []
    for p in periods:
        jo_row = jo_map.get(p)
        job_orders_over_time.append({
            "period": p,
            "created": (jo_row or {}).get("created", 0) or 0,
        })

    return {
        "granularity": granularity,
        "contracts_over_time": contracts_over_time,
        "job_orders_over_time": job_orders_over_time,
    }


def _iter_periods(date_from: datetime.date, date_to: datetime.date,
                   granularity: str):
    """Yield canonical period keys covering [date_from, date_to]."""
    if granularity == "month":
        y, m = date_from.year, date_from.month
        while True:
            yield f"{y:04d}-{m:02d}"
            if (y, m) == (date_to.year, date_to.month):
                break
            m += 1
            if m == 13:
                m = 1
                y += 1
    elif granularity == "quarter":
        y = date_from.year
        q_from = (date_from.month - 1) // 3 + 1
        q_to = (date_to.month - 1) // 3 + 1
        while True:
            yield f"{y}-Q{q_from}"
            if (y, q_from) == (date_to.year, q_to):
                break
            q_from += 1
            if q_from == 5:
                q_from = 1
                y += 1
    else:  # year
        for y in range(date_from.year, date_to.year + 1):
            yield str(y)


# ---------------------------------------------------------------------------
# 3. top_n
# ---------------------------------------------------------------------------


def _build_top_n(filters: Dict[str, Any]) -> Dict[str, Any]:
    n = int(filters.get("top_n", 10))
    contracts_qs = _contract_qs(filters)

    # Top companies by contract count
    top_by_contracts = list(
        contracts_qs.values("company_id", "company__company_name")
        .annotate(count=Count("id"))
        .order_by("-count")[:n]
    )
    top_by_contracts = [
        {
            "company_id": r["company_id"],
            "company_name": r["company__company_name"],
            "count": r["count"],
        }
        for r in top_by_contracts if r["company_id"]
    ]

    # Top companies by crew placed (distinct users per company)
    top_by_crew = list(
        contracts_qs.values("company_id", "company__company_name")
        .annotate(
            crew_count=Count("user_id", distinct=True),
        )
        .order_by("-crew_count")[:n]
    )
    top_by_crew = [
        {
            "company_id": r["company_id"],
            "company_name": r["company__company_name"],
            "crew_count": r["crew_count"],
        }
        for r in top_by_crew if r["company_id"]
    ]

    # Top companies by total salary
    top_by_salary = list(
        contracts_qs.values("company_id", "company__company_name")
        .annotate(total=Sum("salary"))
        .order_by("-total")[:n]
    )
    top_by_salary = [
        {
            "company_id": r["company_id"],
            "company_name": r["company__company_name"],
            "total_salary": str(r["total"]) if r["total"] is not None else "0",
        }
        for r in top_by_salary if r["company_id"]
    ]

    # Top ranks by demand (count of positions in date range, by rank)
    positions_qs = JobOrderPosition.objects.filter(
        job_order__in=_job_order_qs(filters)
    )
    top_ranks = list(
        positions_qs.values("rank_id", "rank__name", "rank__code")
        .annotate(demand=Count("id"))
        .order_by("-demand")[:n]
    )
    top_ranks = [
        {
            "rank_id": r["rank_id"],
            "rank_name": r["rank__name"],
            "rank_code": r["rank__code"],
            "demand": r["demand"],
        }
        for r in top_ranks if r["rank_id"]
    ]

    return {
        "top_companies_by_contracts": top_by_contracts,
        "top_companies_by_crew_placed": top_by_crew,
        "top_companies_by_total_salary": top_by_salary,
        "top_ranks_by_demand": top_ranks,
    }


# ---------------------------------------------------------------------------
# 4. breakdowns
# ---------------------------------------------------------------------------


def _build_breakdowns(filters: Dict[str, Any]) -> Dict[str, Any]:
    # Company-related breakdowns are NOT date-filtered (companies
    # exist regardless of the date range). The user's company
    # filter still applies.
    companies_qs = _company_qs(filters)

    by_company_status = dict(
        companies_qs.values_list("status").annotate(n=Count("id"))
    )
    by_company_type = dict(
        companies_qs
        .exclude(company_type__isnull=True)
        .values_list("company_type__name")
        .annotate(n=Count("id"))
    )
    by_country = dict(
        companies_qs
        .exclude(company_flag__isnull=True)
        .values_list("company_flag__name")
        .annotate(n=Count("id"))
    )

    # Contract status breakdown IS date-filtered
    contracts_qs = _contract_qs(filters)
    by_contract_status = dict(
        contracts_qs.values_list("status").annotate(n=Count("id"))
    )

    # Rank breakdown
    positions_qs = JobOrderPosition.objects.filter(
        job_order__in=_job_order_qs(filters)
    )
    by_rank = dict(
        positions_qs
        .exclude(rank__isnull=True)
        .values_list("rank__name")
        .annotate(n=Count("id"))
    )

    return {
        "by_company_status": by_company_status,
        "by_company_type": by_company_type,
        "by_country": by_country,
        "by_contract_status": by_contract_status,
        "by_rank": by_rank,
    }


# ---------------------------------------------------------------------------
# 5. per-company timeline (opt-in, off by default)
# ---------------------------------------------------------------------------


def _build_per_company_timeline(filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """For each company, a chronological list of every job order
    and every contract (with sign_on_date or sign_off_date in range).
    Used by the "drill into one company" view on the frontend.
    """
    companies = list(_company_qs(filters).values("id", "company_name")[:50])
    if not companies:
        return []

    date_from = filters["date_from"]
    date_to = filters["date_to"]
    company_ids = [c["id"] for c in companies]

    # Job orders in range
    jos = list(
        JobOrder.objects.filter(
            company_id__in=company_ids,
            request_date__gte=date_from,
            request_date__lte=date_to,
        ).values("id", "company_id", "reference_number",
                 "request_date", "target_joining_date", "status")
        .order_by("company_id", "request_date")
    )

    # Contracts in range
    contracts = list(
        Contract.objects.filter(
            company_id__in=company_ids,
            sign_on_date__gte=date_from,
            sign_on_date__lte=date_to,
        ).values("id", "company_id", "user_id", "rank_id",
                 "sign_on_date", "sign_off_date", "status", "salary")
        .order_by("company_id", "sign_on_date")
    )

    # Group by company
    by_company: Dict[int, Dict[str, Any]] = {
        c["id"]: {
            "company_id": c["id"],
            "company_name": c["company_name"],
            "events": [],
        }
        for c in companies
    }
    for jo in jos:
        by_company[jo["company_id"]]["events"].append({
            "type": "job_order",
            "id": jo["id"],
            "reference_number": jo["reference_number"],
            "request_date": jo["request_date"].isoformat() if jo["request_date"] else None,
            "target_joining_date": jo["target_joining_date"].isoformat() if jo["target_joining_date"] else None,
            "status": jo["status"],
        })
    for c in contracts:
        by_company[c["company_id"]]["events"].append({
            "type": "contract",
            "id": c["id"],
            "user_id": c["user_id"],
            "rank_id": c["rank_id"],
            "sign_on_date": c["sign_on_date"].isoformat() if c["sign_on_date"] else None,
            "sign_off_date": c["sign_off_date"].isoformat() if c["sign_off_date"] else None,
            "status": c["status"],
            "salary": str(c["salary"]) if c["salary"] is not None else None,
        })

    # Sort each company's events by date (events missing a date
    # are pushed to the end).
    for c in by_company.values():
        c["events"].sort(
            key=lambda e: (
                e.get("request_date")
                or e.get("sign_on_date")
                or "9999-12-31",
                e["type"],
            )
        )
    return list(by_company.values())


# ---------------------------------------------------------------------------
# Top-level entry point
# ---------------------------------------------------------------------------


def build_historical_report(filters: Dict[str, Any]) -> Dict[str, Any]:
    """Compose the full report. ``filters`` keys:
      - date_from (date)
      - date_to (date)
      - granularity (str: month|quarter|year)
      - company_ids (list[int])
      - company_names (list[str])
      - top_n (int)
      - include_timeline (bool)
    """
    out: Dict[str, Any] = {
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "filters": {
            "date_from": filters["date_from"].isoformat(),
            "date_to": filters["date_to"].isoformat(),
            "granularity": filters.get("granularity", "month"),
            "company_ids": filters.get("company_ids") or [],
            "company_names": filters.get("company_names") or [],
            "top_n": int(filters.get("top_n", 10)),
        },
        "summary": _build_summary(filters),
        "time_series": _build_time_series(filters),
        "top_n": _build_top_n(filters),
        "breakdowns": _build_breakdowns(filters),
    }
    if filters.get("include_timeline"):
        out["per_company_timeline"] = _build_per_company_timeline(filters)
    return out
