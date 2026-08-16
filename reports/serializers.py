"""
Filter validation for the Reports endpoint.

Each entity has a corresponding filter serializer. All filter
fields are optional. Multi-select fields accept a list of values
(empty list = no filter).

For any feature that has a numeric id AND a human name, both
``<feature>_ids`` and ``<feature>_names`` are accepted. Names are
matched case-insensitive contains (so "Maersk" hits both
"Maersk Line" and "Maersk Shipping"). The two forms OR together
when both are provided in the same request.
"""
from rest_framework import serializers


# ---------------------------------------------------------------------------
# Custom fields
# ---------------------------------------------------------------------------


class _NormalisedStatusField(serializers.ChoiceField):
    """
    ChoiceField that normalises the human label ``MEDICAL VACATION``
    (with space) to the stored value ``MEDICAL_VACATION`` (with
    underscore) so the rest of the pipeline only ever sees one
    canonical form.
    """
    def to_internal_value(self, data):
        s = str(data).strip().upper().replace(" ", "_")
        return super().to_internal_value(s)


# ---------------------------------------------------------------------------
# Per-entity filter serializers
# ---------------------------------------------------------------------------


class JobOrderReportFilters(serializers.Serializer):
    # Companies
    company_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False, default=list,
    )
    company_names = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False, default=list,
        help_text="Case-insensitive contains-match on Company.company_name.",
    )
    # Ships
    ship_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False, default=list,
    )
    ship_names = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False, default=list,
        help_text="Case-insensitive contains-match on Ship.ship_name.",
    )
    # Status
    statuses = serializers.ListField(
        child=serializers.ChoiceField(choices=[
            "Open", "Close", "Full Filled",
        ]),
        required=False, default=list,
    )
    # Ranks
    rank_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False, default=list,
    )
    rank_names = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False, default=list,
        help_text=(
            "Case-insensitive contains-match on Rank.name OR Rank.code. "
            "Example: 'Master' or 'MAS-1'."
        ),
    )
    # Dates
    request_date_from = serializers.DateField(required=False, allow_null=True)
    request_date_to = serializers.DateField(required=False, allow_null=True)
    target_join_date_from = serializers.DateField(required=False, allow_null=True)
    target_join_date_to = serializers.DateField(required=False, allow_null=True)


class CompanyReportFilters(serializers.Serializer):
    company_type_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False, default=list,
    )
    company_type_names = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False, default=list,
        help_text="Case-insensitive contains-match on CompanyType.name.",
    )
    country_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False, default=list,
        help_text="Flag / country ids (api.models.Flag).",
    )
    country_names = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False, default=list,
        help_text="Case-insensitive contains-match on Flag.name.",
    )
    statuses = serializers.ListField(
        child=serializers.ChoiceField(choices=[
            "Active", "Inactive", "Prospect",
        ]),
        required=False, default=list,
    )


class ShipReportFilters(serializers.Serializer):
    company_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False, default=list,
    )
    company_names = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False, default=list,
        help_text="Case-insensitive contains-match on Company.company_name.",
    )
    ship_type_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False, default=list,
    )
    ship_type_names = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False, default=list,
        help_text="Case-insensitive contains-match on VesselType.name.",
    )
    flag_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False, default=list,
    )
    flag_names = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False, default=list,
        help_text="Case-insensitive contains-match on Flag.name.",
    )
    year_built_from = serializers.IntegerField(
        required=False, allow_null=True, min_value=1900, max_value=2100,
    )
    year_built_to = serializers.IntegerField(
        required=False, allow_null=True, min_value=1900, max_value=2100,
    )


class UserReportFilters(serializers.Serializer):
    roles = serializers.ListField(
        child=serializers.ChoiceField(choices=[
            "Admin", "HR Manager", "Recruiter", "Employee",
        ]),
        required=False, default=list,
    )
    user_statuses = serializers.ListField(
        child=_NormalisedStatusField(choices=[
            "ON_SITE", "ON_BOARD", "VACATION",
            "MEDICAL_VACATION", "NEW_APPLICANT",
        ]),
        required=False, default=list,
        help_text=(
            "Effective 5-state status. Computed from stored + contracts. "
            "Accepts 'MEDICAL_VACATION' or 'MEDICAL VACATION' (we normalize)."
        ),
    )
    rank_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False, default=list,
    )
    rank_names = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False, default=list,
        help_text=(
            "Case-insensitive contains-match on Rank.name OR Rank.code. "
            "Example: 'Chief' or 'CHIEF-1'."
        ),
    )
    nationalities = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False, default=list,
        help_text="Case-insensitive contains-match on Users.nationality.",
    )
    is_blacklisted = serializers.BooleanField(
        required=False, allow_null=True,
    )


# ---------------------------------------------------------------------------
# Top-level request
# ---------------------------------------------------------------------------


class ReportGenerateRequestSerializer(serializers.Serializer):
    """
    Wraps all four entity filter blocks.

    Every block is optional. An entity block left out of the request
    is treated as 'no filters' and the corresponding section is
    included in the response with all rows.

    Each feature that has a numeric id and a human name accepts
    BOTH forms in the same request — the service ORs them.
    """
    job_orders = JobOrderReportFilters(required=False)
    companies = CompanyReportFilters(required=False)
    ships = ShipReportFilters(required=False)
    users = UserReportFilters(required=False)
