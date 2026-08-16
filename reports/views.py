"""
Views for the Reports endpoint.

The frontend can hit the endpoint with either POST or GET. POST
takes a JSON body, GET takes the same filter spec flattened into
query parameters. The two go through the same service layer so
the response shape is identical.

Why both?
  - POST: cleanest for large multi-select filter specs (the
    Reports page typically sends all 4 sections).
  - GET: easier for ad-hoc Postman debugging, browser bookmarks,
    and CDN caching when the filter spec is small.
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import User_Status, Users
from companies.models import Company, JobOrder, JobOrderPosition
from core.models import CompanyType, Flag, VesselType
from ships.models import Ship

from .serializers import ReportGenerateRequestSerializer
from .services import generate_report


# Field map: query-param prefix -> the nested section it belongs to.
# Keep this explicit so typos in the URL are caught as "no filters
# for that section" rather than silently dropping user input.
_GET_FIELDS_BY_SECTION: Dict[str, List[str]] = {
    "job_orders": [
        "company_ids", "company_names",
        "ship_ids", "ship_names",
        "statuses",
        "rank_ids", "rank_names",
        "request_date_from", "request_date_to",
        "target_join_date_from", "target_join_date_to",
    ],
    "job_positions": [
        "position_ids", "position_rank_names",
        "position_company_ids", "position_company_names",
        "position_ship_ids", "position_ship_names",
        "position_statuses",
    ],
    "companies": [
        "company_type_ids", "company_type_names",
        "country_ids", "country_names",
        "statuses",
    ],
    "ships": [
        "company_ids", "company_names",
        "ship_type_ids", "ship_type_names",
        "flag_ids", "flag_names",
        "year_built_from", "year_built_to",
    ],
    "users": [
        "roles",
        "user_statuses",
        "rank_ids", "rank_names",
        "nationalities",
        "is_blacklisted",
    ],
}


def _list_from_query(get_params, key: str):
    """
    Pull a multi-value list from the request's query params.

    Accepts BOTH:
      ?key=v1&key=v2   (Django's standard repeated param)
      ?key=v1,v2       (comma-separated for readability)
      ?key=v1&key=v2,v3  (mixed)
    Returns a list of raw strings; the serializer does type
    coercion.
    """
    raw = get_params.getlist(key)
    out: List[str] = []
    for v in raw:
        if v is None:
            continue
        for piece in str(v).split(","):
            piece = piece.strip()
            if piece:
                out.append(piece)
    return out


def _build_spec_from_query(request: Request) -> Dict[str, Any]:
    """
    Flatten the request's query string into the same nested dict
    shape that POST accepts. Only sections that have at least one
    non-empty filter are included; missing sections default to
    "all rows" via the empty dict branch in generate_report().

    Query key grammar: ``<section>.<field>``
    e.g. ``?job_orders.statuses=Open&job_orders.statuses=Close``
    """
    spec: Dict[str, Any] = {}
    for key in request.query_params.keys():
        if "." not in key:
            continue  # unknown / non-namespaced param, ignore
        section, _, field = key.partition(".")
        if section not in _GET_FIELDS_BY_SECTION:
            continue
        if field not in _GET_FIELDS_BY_SECTION[section]:
            continue
        values = _list_from_query(request.query_params, key)
        if not values:
            continue
        block = spec.setdefault(section, {})
        # If a single value came in for a ListField, wrap it.
        # If a single value came in for a scalar field, leave as
        # scalar (the serializer will coerce).
        if field in _SCALAR_FIELDS:
            # Multiple values for a scalar — last non-empty wins.
            block[field] = next((x for x in reversed(values) if x), values[0])
        else:
            block[field] = values
    return spec


# Field names that should be a single value, not a list, in the
# nested spec. These are the DateField / IntegerField / BooleanField
# fields in the per-section filter serializers.
_SCALAR_FIELDS = {
    "request_date_from", "request_date_to",
    "target_join_date_from", "target_join_date_to",
    "year_built_from", "year_built_to",
    "is_blacklisted",
}


class ReportsGenerateView(APIView):
    """
    POST /api/reports/generate/  -- JSON body
    GET  /api/reports/generate/  -- query params

    The two methods produce identical response shapes. See
    docs/reports-api.md for the full body / query grammar.
    """

    permission_classes = [IsAuthenticated]

    # ------------------------------------------------------------------
    # POST: JSON body
    # ------------------------------------------------------------------

    def post(self, request: Request, *args, **kwargs):
        serializer = ReportGenerateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report = generate_report(serializer.validated_data)
        return Response(report, status=status.HTTP_200_OK)

    # ------------------------------------------------------------------
    # GET: query params
    # ------------------------------------------------------------------

    def get(self, request: Request, *args, **kwargs):
        spec = _build_spec_from_query(request)
        # "No filters anywhere" via GET is a common "give me
        # everything" call from Postman. Treat it the same as
        # ``{}`` via POST (which only includes sections whose
        # filter block is non-empty). To force ALL four sections
        # the user can pass ``?sections=job_orders,companies,...``
        # or just supply at least one filter per section.
        if not spec:
            for section in _GET_FIELDS_BY_SECTION:
                spec[section] = {}
        serializer = ReportGenerateRequestSerializer(data=spec)
        serializer.is_valid(raise_exception=True)
        report = generate_report(serializer.validated_data)
        return Response(report, status=status.HTTP_200_OK)


class ReportsDropdownOptionsView(APIView):
    """
    GET /api/reports/dropdown-options/

    Lightweight, single-shot response that the Reports page uses to
    populate every filter dropdown. The frontend calls this once
    when the page loads, then uses the returned ids / names as the
    values for the multi-select filter UI.

    Each list is a flat ``[{"id": ..., "name": ...}]`` (or
    ``{"id": ..., "name": ..., "code": ...}`` for ranks, since
    Ranks have a structured code as well as a human name) so the
    dropdown can show either, and the request can use either form.

    Auth: IsAuthenticated (same as the rest of the reports app).
    Caching: this endpoint is cache-friendly. The data only
    changes when an admin adds a new Company / Rank / Ship etc.
    If you want server-side caching, the recommended TTL is 1 hour
    with cache invalidation on the corresponding admin POSTs.
    """
    permission_classes = [IsAuthenticated]

    # Hard caps so a misconfigured deployment can't return megabytes
    # of dropdown options. The page is for human filter selection;
    # 1000 entries is already more than any sane UI shows.
    _CAP = 1000

    def get(self, request: Request, *args, **kwargs):
        companies = list(
            Company.objects.order_by("company_name").values(
                "id", "company_name"
            )[:self._CAP]
        )
        companies = [
            {"id": c["id"], "name": c["company_name"]} for c in companies
        ]

        ships = list(
            Ship.objects.order_by("ship_name").values(
                "id", "ship_name"
            )[:self._CAP]
        )
        ships = [{"id": s["id"], "name": s["ship_name"]} for s in ships]

        ship_types = list(
            VesselType.objects.order_by("name").values("id", "name")[:self._CAP]
        )
        flags = list(
            Flag.objects.order_by("name").values("id", "name")[:self._CAP]
        )
        company_types = list(
            CompanyType.objects.order_by("name").values("id", "name")[:self._CAP]
        )
        # Ranks: include code so the dropdown can show "Master (MAS-1)"
        from api.models import Rank
        ranks = list(
            Rank.objects.order_by("code").values("id", "name", "code")[:self._CAP]
        )

        # Nationalities: Users.nationality is a free-form char field,
        # not an FK to a nationalities table. Build the dropdown from
        # the distinct values already present on the Users rows so the
        # frontend can offer "what's in the DB right now" without a
        # separate lookup. Empty / null nationalities are excluded.
        from django.db.models import F, Value
        from django.db.models.functions import Coalesce
        nationalities = list(
            Users.objects
            .exclude(nationality__isnull=True)
            .exclude(nationality__exact="")
            .annotate(name=Coalesce("nationality", Value("")))
            .order_by("name")
            .values_list("name", flat=True)
            .distinct()[:self._CAP]
        )
        # Normalise to the same {id, name} shape the other options
        # use, so the frontend has a single render path. We don't have
        # a stable id for nationalities (it's free-form), so we
        # synthesise one from the index — the filter endpoint still
        # matches on the name.
        nationalities = [
            {"id": idx, "name": n} for idx, n in enumerate(nationalities)
        ]

        return Response({
            "generated_at": timezone.now().isoformat(),
            "options": {
                "companies": companies,
                "ships": ships,
                "ship_types": ship_types,
                "flags": flags,
                "company_types": company_types,
                "ranks": ranks,
                "nationalities": nationalities,
            },
            "enum_options": {
                # Static choices for the value-based filters
                "job_order_statuses": [c[0] for c in JobOrder.STATUS_CHOICES],
                "company_statuses":   [c[0] for c in Company.STATUS_CHOICES],
                "ship_statuses":      [c[0] for c in Ship.SHIP_STATUS],
                "user_roles":         ["Admin", "HR Manager", "Recruiter", "Employee"],
                "user_statuses":      [c.value for c in User_Status],
            },
        })
