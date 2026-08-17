"""
View for the Historical Data for Companies endpoint.

Single GET endpoint that returns every analysis section in one
response. See services.build_historical_report for the response
shape and services module docstring for the date semantics.
"""
import datetime

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import _default_range, _parse_date, build_historical_report


class HistoricalDataForCompaniesView(APIView):
    """
    GET /api/historical-data-for-companies/

    Query params
    ------------
    date_from (YYYY-MM-DD, optional)
        Inclusive start of the date range. Default: 12 months back.
    date_to (YYYY-MM-DD, optional)
        Inclusive end of the date range. Default: today.
    granularity (month|quarter|year, optional)
        Bucket size for the time-series charts. Default: month.
    company_ids (int, optional, repeated)
        Restrict the analysis to these company ids.
    company_names (str, optional, repeated or comma-separated)
        Restrict by company name (case-insensitive contains).
    top_n (int, optional)
        How many entries to return in each top-N section. Default: 10.
    include_timeline (true|false, optional)
        Include the per-company timeline section. Off by default
        since it can return a lot of data.

    Response 200 OK
    ---------------
    {
      "generated_at": "2026-08-17T...",
      "filters": { ...echo of normalized filters... },
      "summary": { ... },
      "time_series": { ... },
      "top_n": { ... },
      "breakdowns": { ... },
      "per_company_timeline": [ ... ]   # only if include_timeline=true
    }
    """

    permission_classes = [IsAuthenticated]

    def get(self, request: Request, *args, **kwargs):
        # ---- date range ------------------------------------------------
        date_from_raw = request.query_params.get("date_from")
        date_to_raw = request.query_params.get("date_to")
        if date_from_raw:
            try:
                date_from = _parse_date(date_from_raw)
            except ValueError:
                return Response(
                    {"error": f"Invalid date_from {date_from_raw!r}; use YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            date_from, _ = _default_range()
        if date_to_raw:
            try:
                date_to = _parse_date(date_to_raw)
            except ValueError:
                return Response(
                    {"error": f"Invalid date_to {date_to_raw!r}; use YYYY-MM-DD."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            _, date_to = _default_range()
        if date_from > date_to:
            return Response(
                {"error": "date_from must be on or before date_to."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ---- granularity ----------------------------------------------
        granularity = (request.query_params.get("granularity") or "month").lower()
        if granularity not in ("month", "quarter", "year"):
            return Response(
                {"error": (
                    f"Invalid granularity {granularity!r}. "
                    "Allowed: month, quarter, year."
                )},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ---- company filter -------------------------------------------
        company_ids = []
        for v in request.query_params.getlist("company_ids"):
            try:
                company_ids.append(int(v))
            except (TypeError, ValueError):
                return Response(
                    {"error": f"Invalid company_ids {v!r}; must be int."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        company_names = []
        for v in request.query_params.getlist("company_names"):
            for piece in str(v).split(","):
                piece = piece.strip()
                if piece:
                    company_names.append(piece)

        # ---- top_n ----------------------------------------------------
        top_n_raw = request.query_params.get("top_n", "10")
        try:
            top_n = int(top_n_raw)
            if top_n < 1 or top_n > 100:
                raise ValueError
        except (TypeError, ValueError):
            return Response(
                {"error": f"Invalid top_n {top_n_raw!r}; must be 1-100."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ---- include_timeline -----------------------------------------
        include_timeline = (
            request.query_params.get("include_timeline", "").lower()
            in ("1", "true", "yes")
        )

        filters = {
            "date_from": date_from,
            "date_to": date_to,
            "granularity": granularity,
            "company_ids": company_ids,
            "company_names": company_names,
            "top_n": top_n,
            "include_timeline": include_timeline,
        }
        report = build_historical_report(filters)
        return Response(report, status=status.HTTP_200_OK)
