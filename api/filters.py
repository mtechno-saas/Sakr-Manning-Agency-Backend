# import django_filters
# from .models import Users

# class UsersFilter(django_filters.FilterSet):
#     name = django_filters.CharFilter(field_name="first_name", lookup_expr="icontains")
#     age = django_filters.NumberFilter(field_name="age")
#     marital_status = django_filters.CharFilter(field_name="marital_status", lookup_expr="iexact")
#     user_status = django_filters.CharFilter(field_name="user_status", lookup_expr="iexact")
#     nationality = django_filters.CharFilter(field_name="nationality", lookup_expr="icontains")
#     Nearest_Port = django_filters.CharFilter(field_name="Nearest_Port", lookup_expr="icontains")
#     codes = django_filters.CharFilter(field_name="codes__name", lookup_expr="icontains")  

#     class Meta:
#         model = Users
#         fields = ["name", "age", "marital_status", "user_status", "nationality", "Nearest_Port", "assigned_code"]


# api/filters.py
# import django_filters
# from .models import Users

# class UsersFilter(django_filters.FilterSet):
#     # Filter by first_name or last_name containing the value
#     name = django_filters.CharFilter(field_name="first_name", lookup_expr="icontains")
    
#     # Filter by exact age
#     age = django_filters.NumberFilter(field_name="age", lookup_expr="exact")
    
#     # Filter by exact marital status (case-insensitive)
#     marital_status = django_filters.CharFilter(field_name="marital_status", lookup_expr="iexact")
    
#     # Filter by exact user status (case-insensitive)
#     user_status = django_filters.CharFilter(field_name="user_status", lookup_expr="iexact")
    
#     # Filter by nationality containing the value
#     nationality = django_filters.CharFilter(field_name="nationality", lookup_expr="icontains")
    
#     # Filter by nearest port containing the value
#     nearest_port = django_filters.CharFilter(field_name="Nearest_Port", lookup_expr="icontains")
    
#     # Filter by the name of the assigned rank (via the 'codes' M2M relationship)
#     rank_name = django_filters.CharFilter(field_name="codes__name", lookup_expr="icontains")
    
#     # Filter by the assigned_code from the UserRank model (via the 'user_ranks' relationship)
#     assigned_code = django_filters.CharFilter(field_name="user_ranks__assigned_code", lookup_expr="icontains")

#     class Meta:
#         model = Users
#         # The 'fields' list should only contain fields that are directly on the Users model
#         # or filters that you want to be auto-generated.
#         # Since we defined all our filters above, we can even make this list empty.
#         # However, it's good practice to list the model fields you are filtering on.
#         fields = [
#             "name", 
#             "age", 
#             "marital_status", 
#             "user_status", 
#             "nationality", 
#             "nearest_port",
#             # 'rank_name' and 'assigned_code' are removed from here because they are not
#             # direct fields on the Users model. The filter still works because they are
#             # defined explicitly above.
#         ]





import django_filters
from django.db.models import Q
from django_filters.widgets import QueryArrayWidget
from .models import Users, Company, Interview, CVSubmission, Contract, SeaService
from finance.models import FinanceRecord
from companies.models import JobOrder
from logistics.models import FlightBooking, VisaApplication, JoiningInstruction
from compliance.models import Audit, IncidentReport
from ships.models import Ship


# ---------- Multi-value filter base classes ----------
#
# Why a custom widget?
# django_filters' built-in BaseInFilter / BaseCSVWidget only splits the value
# on commas (CSV format). It does NOT honour repeated query keys like
# `?nationality=Egypt&nationality=Syria` — it would silently keep only the
# LAST value, which is exactly the bug that turned
# `?user_status=ON_SITE&user_status=VACATION` into a single-value filter.
#
# QueryArrayWidget supports all three formats the frontend uses:
#   - repeated keys:    ?foo=bar&foo=baz
#   - array notation:   ?foo[]=bar&foo[]=baz
#   - CSV (partial):    ?foo=bar,baz
#
# See: https://django-filter.readthedocs.io/en/stable/ref/widgets.html#queryarraywidget
class CharInFilter(django_filters.BaseInFilter, django_filters.CharFilter):
    """CharFilter that accepts repeated query keys (?k=a&k=b) and array notation (?k[]=a&k[]=b).

    django_filters' default BaseCSVWidget only splits on commas; it silently drops
    repeated query keys and keeps only the LAST value. We override __init__ to
    inject QueryArrayWidget via kwargs so the form field actually uses it.

    (Setting `widget = QueryArrayWidget` as a class attribute does NOT work —
    django forms' MediaDefiningClass wraps it and Filter.field ignores it.)
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", QueryArrayWidget)
        super().__init__(*args, **kwargs)


class NumberInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    """NumberFilter that accepts repeated query keys / array notation."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", QueryArrayWidget)
        super().__init__(*args, **kwargs)


class IexactInFilter(django_filters.BaseInFilter, django_filters.CharFilter):
    """Multi-value CharFilter that does a case-insensitive match per value.

    CharInFilter does a SQL `IN (...)` lookup, which is case-sensitive — that
    breaks `?marital_status=SINGLE` against a DB row stored as 'Single'.
    This variant splits repeated query keys / array notation / CSV exactly
    like CharInFilter does, but then ORs `iexact` lookups per value instead
    of a single `IN` lookup.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", QueryArrayWidget)
        super().__init__(*args, **kwargs)

    def filter(self, qs, value):
        if not value:
            return qs
        # BaseInFilter has already split repeated keys / array notation into a list.
        if isinstance(value, str):
            values = [v.strip() for v in value.split(',') if v.strip()]
        else:
            values = [str(v).strip() for v in value if str(v).strip()]
        if not values:
            return qs
        q = Q()
        for v in values:
            q |= Q(**{self.field_name + "__iexact": v})
        return qs.filter(q).distinct()


class UsersFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(method='filter_by_name')
    age = django_filters.NumberFilter(field_name="age", lookup_expr="exact")
    marital_status = IexactInFilter(field_name="marital_status")
    user_status = CharInFilter(field_name="user_status", lookup_expr="in")
    nationality = CharInFilter(field_name="nationality", lookup_expr="in")
    nearest_port = django_filters.CharFilter(field_name="Nearest_Port", lookup_expr="icontains")
    
    def filter_by_name(self, queryset, name, value):
        if not value:
            return queryset
        
        terms = value.split(',')
        query = Q()
        
        for term in terms:
            term = term.strip()
            if not term:
                continue
            
            term_query = Q(first_name__icontains=term) | Q(middle_name__icontains=term) | Q(email__icontains=term)
            
            parts = term.split()
            if len(parts) >= 2:
                term_query |= (Q(first_name__icontains=parts[0]) & Q(middle_name__icontains=parts[-1]))
            
            query |= term_query
            
        return queryset.filter(query).distinct()
    
    rank_name = django_filters.CharFilter(method='filter_by_rank_name')
    assigned_code = django_filters.CharFilter(field_name="user_ranks__assigned_code", lookup_expr="icontains")

    def filter_by_rank_name(self, queryset, name, value):
        """
        Match `value` against every place a rank/position might live on or
        related to a user:
          - codes (M2M)            → codes__name
          - UserRank (FK)          → user_ranks__rank__name
          - SeaService (FK)        → sea_services__rank        (free-text field!)
          - Contract (FK)          → contracts__rank__name
          - User.application_for_position (legacy)
          - User.position          (synced from Document.position)
        Then collapse duplicates with .distinct() so M2M joins don't inflate counts.
        """
        if not value:
            return queryset
        return queryset.filter(
            Q(codes__name__icontains=value) |
            Q(user_ranks__rank__name__icontains=value) |
            Q(sea_services__rank__icontains=value) |
            Q(contracts__rank__name__icontains=value) |
            Q(application_for_position__icontains=value) |
            Q(position__icontains=value)
        ).distinct()
    
    role = CharInFilter(field_name="role", lookup_expr="in")
    is_blacklisted = django_filters.BooleanFilter(field_name="is_blacklisted")
    
    company = django_filters.NumberFilter(method='filter_by_company')
    company_name = django_filters.CharFilter(method='filter_by_company_name')

    def filter_by_company(self, queryset, name, value):
        """
        Accept either a numeric Company ID (`?company=5`) or a name
        (`?company=ROMALEX MARINE`). Numeric values match by id; everything
        else falls back to icontains on company_name.
        """
        if not value:
            return queryset
        value = str(value).strip()
        if value.isdigit():
            return queryset.filter(contracts__company__id=int(value)).distinct()
        return queryset.filter(contracts__company__company_name__icontains=value).distinct()

    def filter_by_company_name(self, queryset, name, value):
        """
        Match `value` against every place a company name might live on or
        related to a user:
          - Company (FK via Contract) → contracts__company__company_name
          - SeaService (FK)           → sea_services__company_name  (free-text!)
        Then collapse duplicates with .distinct().
        """
        if not value:
            return queryset
        return queryset.filter(
            Q(contracts__company__company_name__icontains=value) |
            Q(sea_services__company_name__icontains=value)
        ).distinct()

    ship = django_filters.CharFilter(method='filter_by_ship')
    ship_name = django_filters.CharFilter(field_name="contracts__ship__ship_name", lookup_expr="icontains")

    def filter_by_ship(self, queryset, name, value):
        """
        Accept either a numeric Ship ID (`?ship=5`) or a name
        (`?ship=Northern Star`). Numeric values match by id; everything else
        falls back to icontains on ship_name. This means a strict numeric
        filter is preserved (so `?ship=1234` won't accidentally match a ship
        whose name happens to contain "1234").
        """
        if not value:
            return queryset
        value = str(value).strip()
        if value.isdigit():
            return queryset.filter(contracts__ship__id=int(value)).distinct()
        return queryset.filter(contracts__ship__ship_name__icontains=value).distinct()
    
    job_position_name = django_filters.CharFilter(field_name="contracts__job_position__rank__name", lookup_expr="icontains")
    
    # Filter by Language - Search in both LanguageProficiency and UserLanguage models
    language = django_filters.CharFilter(method='filter_by_language')

    def filter_by_language(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(languages__language__icontains=value) |
            Q(user_languages__language__icontains=value) |
            Q(english_language_level__icontains=value) |
            Q(other_language__icontains=value)
        ).distinct()

    has_language = django_filters.BooleanFilter(method='filter_by_has_language')

    def filter_by_has_language(self, queryset, name, value):
        """
        ?has_language=true   → users with at least one language record
                                (any LanguageProficiency, any UserLanguage,
                                 a non-empty english_language_level, or a
                                 non-empty other_language free-text field)
        ?has_language=false  → users with NO language records at all
        """
        if value is None:
            return queryset

        has_any = (
            Q(languages__isnull=False) |            # ≥1 LanguageProficiency row
            Q(user_languages__isnull=False) |      # ≥1 UserLanguage row
            Q(english_language_level__isnull=False, english_language_level__gt='') |
            Q(other_language__isnull=False, other_language__gt='')
        )

        if value:
            return queryset.filter(has_any).distinct()
        return queryset.exclude(has_any).distinct()
    
    contract_status = CharInFilter(field_name="contracts__status", lookup_expr="in")
    
    signed_on_from = django_filters.DateFilter(field_name="contracts__sign_on_date", lookup_expr="gte")
    signed_on_to = django_filters.DateFilter(field_name="contracts__sign_on_date", lookup_expr="lte")
    signed_off_from = django_filters.DateFilter(field_name="contracts__sign_off_date", lookup_expr="gte")
    signed_off_to = django_filters.DateFilter(field_name="contracts__sign_off_date", lookup_expr="lte")

    company_type = django_filters.CharFilter(field_name="contracts__company__company_type__name", lookup_expr="icontains")
    ship_type = django_filters.CharFilter(field_name="contracts__ship__ship_type__name", lookup_expr="icontains")
    
    passport_no = django_filters.CharFilter(field_name="passport_no", lookup_expr="icontains")
    passport_type = django_filters.CharFilter(field_name="personal_documents__document_type", lookup_expr="icontains")
    passport_expiry_from = django_filters.DateFilter(field_name="passport_expiry_date", lookup_expr="gte")
    passport_expiry_to = django_filters.DateFilter(field_name="passport_expiry_date", lookup_expr="lte")
    
    seaman_book_no = django_filters.CharFilter(field_name="seaman_book_no", lookup_expr="icontains")
    seaman_book_type = django_filters.CharFilter(field_name="personal_documents__document_type", lookup_expr="icontains")
    seaman_book_expiry_from = django_filters.DateFilter(field_name="seaman_book_expiry_date", lookup_expr="gte")
    seaman_book_expiry_to = django_filters.DateFilter(field_name="seaman_book_expiry_date", lookup_expr="lte")
    
    document_type = django_filters.CharFilter(field_name="personal_documents__document_type", lookup_expr="icontains")
    
    medical_no = django_filters.CharFilter(method='filter_by_medical_no')
    medical_expiry_from = django_filters.DateFilter(method='filter_by_medical_expiry')
    medical_expiry_to = django_filters.DateFilter(method='filter_by_medical_expiry')

    def filter_by_medical_no(self, queryset, name, value):
        """
        Multi-source medical-number search. Medical data lives in four
        separate field groups on the User model (none of them in
        PersonalDocument), so we OR across all of them:

          - health_number
          - international_medical_number
          - yellow_fever_number
          - cholera_number

        A user matches if any of those contains the value (icontains).
        """
        if not value:
            return queryset
        return queryset.filter(
            Q(health_number__icontains=value) |
            Q(international_medical_number__icontains=value) |
            Q(yellow_fever_number__icontains=value) |
            Q(cholera_number__icontains=value)
        ).distinct()

    def filter_by_medical_expiry(self, queryset, name, value):
        """
        Multi-source expiry date range. The from/to direction is inferred
        from the filter name (medical_expiry_from -> gte, medical_expiry_to -> lte).

        Matches if ANY of the four medical expiry dates is in range:
          - health_expiry_date
          - international_medical_expiry_date
          - yellow_fever_expiry_date
          - cholera_expiry_date

        So a user with a `yellow_fever_expiry_date` of 2026-03-01 matches
        ?medical_expiry_from=2025-01-01, even if their `health_expiry_date`
        is null. Combined with `?medical_expiry_to=`, the two filters are
        AND'd (so a user must have at least one medical expiry in range).
        """
        if not value:
            return queryset
        lookup = 'gte' if name == 'medical_expiry_from' else 'lte'

        expiry_fields = [
            'health_expiry_date',
            'international_medical_expiry_date',
            'yellow_fever_expiry_date',
            'cholera_expiry_date',
        ]
        q = Q()
        for field in expiry_fields:
            q |= Q(**{f'{field}__{lookup}': value})
        return queryset.filter(q).distinct()
    
    course_name = django_filters.CharFilter(field_name="courses__course_name", lookup_expr="icontains")

    document_status = django_filters.CharFilter(field_name="documents__status", lookup_expr="iexact")
    document_title = django_filters.CharFilter(field_name="documents__title", lookup_expr="icontains")

    position = django_filters.CharFilter(method='filter_by_position')
    
    def filter_by_position(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(codes__name__icontains=value) | 
            Q(application_for_position__icontains=value) |
            Q(position__icontains=value)
        ).distinct()

    @property
    def qs(self):
        """
        Many UsersFilter fields traverse FK / M2M relations
        (contracts__, personal_documents__, documents__, user_ranks__, codes__, courses__,
         languages__, user_languages__). Joining across those without a DISTINCT
        produces duplicate rows whenever a user has more than one related record
        (e.g. multiple contracts for the same company).
        Apply .distinct() so list / pagination never inflates counts.
        """
        qs = super().qs
        return qs.distinct()

    class Meta:
        model = Users
        fields = [
            "name", "age", "marital_status", "user_status", "nationality",
            "nearest_port", "role", "is_blacklisted", "company", "ship",
            "language", "has_language", "contract_status", "position",
            "document_status", "document_title",
            "passport_no", "seaman_book_no", "medical_no", "course_name"
        ]


class CompanyFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    company_type = django_filters.AllValuesMultipleFilter(field_name="company_type")
    status = django_filters.AllValuesMultipleFilter(field_name="status")

    class Meta:
        model = Company
        fields = ["name", "company_type", "status"]


class InterviewFilter(django_filters.FilterSet):
    candidate = django_filters.NumberFilter(field_name="candidate__id")
    company = django_filters.NumberFilter(field_name="company__id")
    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")
    scheduled_date = django_filters.DateFilter(field_name="scheduled_date")
    scheduled_date_from = django_filters.DateFilter(field_name="scheduled_date", lookup_expr="gte")
    scheduled_date_to = django_filters.DateFilter(field_name="scheduled_date", lookup_expr="lte")

    class Meta:
        model = Interview
        fields = ["candidate", "company", "status", "scheduled_date"]


class FinanceRecordFilter(django_filters.FilterSet):
    user = django_filters.NumberFilter(field_name="user__id")
    company = django_filters.NumberFilter(field_name="company__id")
    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")
    start_date_from = django_filters.DateFilter(field_name="start_date", lookup_expr="gte")
    start_date_to = django_filters.DateFilter(field_name="start_date", lookup_expr="lte")

    class Meta:
        model = FinanceRecord
        fields = ["user", "company", "status"]


class CVSubmissionFilter(django_filters.FilterSet):
    user = django_filters.NumberFilter(field_name="user__id")
    position = django_filters.NumberFilter(field_name="position__id")
    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")
    submitted_date_from = django_filters.DateFilter(field_name="submitted_date", lookup_expr="gte")
    submitted_date_to = django_filters.DateFilter(field_name="submitted_date", lookup_expr="lte")

    class Meta:
        model = CVSubmission
        fields = ["user", "position", "status"]


class JobOrderFilter(django_filters.FilterSet):
    company = django_filters.NumberFilter(field_name="company__id")
    ship = django_filters.NumberFilter(field_name="ship__id")
    status = django_filters.AllValuesMultipleFilter(field_name="status")
    reference_number = django_filters.CharFilter(field_name="reference_number", lookup_expr="icontains")
    request_date_from = django_filters.DateFilter(field_name="request_date", lookup_expr="gte")
    request_date_to = django_filters.DateFilter(field_name="request_date", lookup_expr="lte")

    class Meta:
        model = JobOrder
        fields = ["company", "ship", "status", "reference_number"]


class FlightBookingFilter(django_filters.FilterSet):
    user = django_filters.NumberFilter(field_name="user__id")
    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")
    airline = django_filters.CharFilter(field_name="airline", lookup_expr="icontains")
    departure_date = django_filters.DateFilter(field_name="departure_time", lookup_expr="date")

    class Meta:
        model = FlightBooking
        fields = ["user", "status", "airline"]


class VisaApplicationFilter(django_filters.FilterSet):
    user = django_filters.NumberFilter(field_name="user__id")
    country = django_filters.CharFilter(field_name="country", lookup_expr="icontains")
    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")
    visa_type = django_filters.CharFilter(field_name="visa_type", lookup_expr="iexact")

    class Meta:
        model = VisaApplication
        fields = ["user", "country", "status", "visa_type"]


class AuditFilter(django_filters.FilterSet):
    company = django_filters.NumberFilter(field_name="company__id")
    ship = django_filters.NumberFilter(field_name="ship__id")
    audit_type = django_filters.CharFilter(field_name="audit_type", lookup_expr="iexact")
    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")
    audit_date_from = django_filters.DateFilter(field_name="audit_date", lookup_expr="gte")
    audit_date_to = django_filters.DateFilter(field_name="audit_date", lookup_expr="lte")

    class Meta:
        model = Audit
        fields = ["company", "ship", "audit_type", "status"]


class IncidentReportFilter(django_filters.FilterSet):
    ship = django_filters.NumberFilter(field_name="ship__id")
    incident_type = django_filters.CharFilter(field_name="incident_type", lookup_expr="iexact")
    severity = django_filters.CharFilter(field_name="severity", lookup_expr="iexact")
    is_closed = django_filters.BooleanFilter(field_name="is_closed")

    class Meta:
        model = IncidentReport
        fields = ["ship", "incident_type", "severity", "is_closed"]


class ShipFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="ship_name", lookup_expr="icontains")
    imo_number = django_filters.CharFilter(field_name="imo_number", lookup_expr="icontains")
    company = django_filters.NumberFilter(field_name="company__id")
    status = django_filters.AllValuesMultipleFilter(field_name="status")
    flag = django_filters.CharFilter(field_name="flag__name", lookup_expr="icontains")
    ship_type = django_filters.CharFilter(field_name="ship_type__name", lookup_expr="icontains")

    class Meta:
        model = Ship
        fields = ["name", "imo_number", "company", "status", "flag", "ship_type"]


class ContractFilter(django_filters.FilterSet):
    user = django_filters.NumberFilter(field_name="user__id")
    ship = django_filters.NumberFilter(field_name="ship__id")
    company = django_filters.NumberFilter(field_name="company__id")
    rank = django_filters.NumberFilter(field_name="rank__id")
    status = django_filters.AllValuesMultipleFilter(field_name="status")

    sign_on_from = django_filters.DateFilter(field_name="sign_on_date", lookup_expr="gte")
    sign_on_to = django_filters.DateFilter(field_name="sign_on_date", lookup_expr="lte")
    sign_off_from = django_filters.DateFilter(field_name="sign_off_date", lookup_expr="gte")
    sign_off_to = django_filters.DateFilter(field_name="sign_off_date", lookup_expr="lte")

    applicant_name = django_filters.CharFilter(field_name="user__first_name", lookup_expr="icontains")

    class Meta:
        model = Contract
        fields = ["user", "ship", "company", "rank", "status"]


class SeaServiceFilter(django_filters.FilterSet):
    """
    Filter SeaService records (a user's per-vessel work history).
    SeaService.rank is a free-text CharField (NOT an FK to Rank), so we expose
    it as plain `rank` (icontains) — that lets the frontend search "A.B" the
    same way it does on the existing /api/users/?rank_name=A.B endpoint.
    """
    user = django_filters.NumberFilter(field_name="user__id")
    rank = django_filters.CharFilter(field_name="rank", lookup_expr="icontains")
    vessel_name = django_filters.CharFilter(field_name="vessel_name", lookup_expr="icontains")
    vessel_name_imo = django_filters.CharFilter(field_name="vessel_name_imo", lookup_expr="icontains")
    imo_number = django_filters.CharFilter(field_name="imo_number", lookup_expr="icontains")
    company_name = django_filters.CharFilter(field_name="company_name", lookup_expr="icontains")
    flag = django_filters.CharFilter(field_name="flag", lookup_expr="icontains")
    vessel_type = django_filters.CharFilter(field_name="vessel_type", lookup_expr="icontains")

    signed_on_from = django_filters.DateFilter(field_name="signed_on", lookup_expr="gte")
    signed_on_to = django_filters.DateFilter(field_name="signed_on", lookup_expr="lte")
    signed_off_from = django_filters.DateFilter(field_name="signed_off", lookup_expr="gte")
    signed_off_to = django_filters.DateFilter(field_name="signed_off", lookup_expr="lte")

    applicant_name = django_filters.CharFilter(field_name="user__first_name", lookup_expr="icontains")

    class Meta:
        model = SeaService
        fields = [
            "user", "rank", "vessel_name", "vessel_name_imo", "imo_number",
            "company_name", "flag", "vessel_type",
        ]