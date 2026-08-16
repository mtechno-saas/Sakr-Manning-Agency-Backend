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

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

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
