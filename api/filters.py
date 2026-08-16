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
from .models import Users, Company, Interview, CVSubmission, Contract
from finance.models import FinanceRecord
from companies.models import JobOrder
from logistics.models import FlightBooking, VisaApplication, JoiningInstruction
from compliance.models import Audit, IncidentReport
from ships.models import Ship


class CharInFilter(django_filters.BaseInFilter, django_filters.CharFilter):
    pass


class NumberInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    pass


class UsersFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(method='filter_by_name')
    age = django_filters.NumberFilter(field_name="age", lookup_expr="exact")
    marital_status = django_filters.CharFilter(method="filter_marital_status")
    user_status = django_filters.CharFilter(method="filter_user_status")
    nationality = django_filters.CharFilter(method="filter_nationality")
    nearest_port = django_filters.CharFilter(field_name="nearest_port", lookup_expr="icontains")

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

    def _strings_for(self, param_name):
        """Pull repeated ?key=1&key=2 values from the request as strings."""
        raw = self.request.GET.getlist(param_name)
        if not raw:
            return None
        cleaned = [v.strip() for v in raw if v is not None and str(v).strip() != ""]
        return cleaned if cleaned else []

    def filter_marital_status(self, queryset, name, value):
        vals = self._strings_for("marital_status")
        if vals is None:
            return queryset
        if not vals:
            return queryset.none()
        return queryset.filter(marital_status__in=vals)

    def filter_user_status(self, queryset, name, value):
        """
        Filter by effective user status.

        Accepts any of the 5 values defined in api.models.User_Status:
          ON_SITE, ON_BOARD, VACATION, MEDICAL_VACATION, NEW_APPLICANT

        ON_SITE / VACATION / MEDICAL_VACATION filter on the stored
        field. ON_BOARD and NEW_APPLICANT are derived from contracts:
          ON_BOARD       = stored != VACATION/MEDICAL_VACATION
                           AND has Active/Signed contract (no sign-off
                           or sign-off in the future)
          NEW_APPLICANT  = stored != VACATION/MEDICAL_VACATION
                           AND has no contracts at all
        """
        from django.utils import timezone
        from django.db.models import Exists, OuterRef
        from api.models import User_Status
        from api.models import Contract

        vals = self._strings_for("user_status")
        if vals is None:
            return queryset
        if not vals:
            return queryset.none()

        # Normalize: accept case-insensitive input, and translate
        # "MEDICAL VACATION" (the human label) to the stored value
        # "MEDICAL_VACATION".
        norm = []
        for v in vals:
            up = v.strip().upper().replace(" ", "_")
            norm.append(up)
        # Manual overrides (always-on, no contracts logic)
        manual = {
            User_Status.ON_SITE.value,
            User_Status.VACATION.value,
            User_Status.MEDICAL_VACATION.value,
        }
        # Computed values
        computed = {
            User_Status.ON_BOARD.value,
            User_Status.NEW_APPLICANT.value,
        }
        invalid = [v for v in norm if v not in manual and v not in computed]
        if invalid:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({
                "user_status": (
                    f"Invalid value(s): {invalid}. "
                    f"Allowed: {sorted(manual | computed)}"
                )
            })

        stored_vals = [v for v in norm if v in manual]
        wants_on_board = User_Status.ON_BOARD.value in norm
        wants_new_applicant = User_Status.NEW_APPLICANT.value in norm

        # Subqueries for "has any contract" and "has an active contract".
        # We always need these for the manual stored values too:
        # ON_SITE only matches users with NO active contract AND with
        # AT LEAST ONE past contract (otherwise they're NEW_APPLICANT).
        has_any_contract = Exists(
            Contract.objects.filter(user=OuterRef("pk"))
        )
        today = timezone.localdate()
        has_active_contract = Exists(
            Contract.objects.filter(
                user=OuterRef("pk"),
                status__in=("Active", "Signed"),
            ).filter(
                Q(sign_off_date__isnull=True)
                | Q(sign_off_date__gte=today)
            )
        )

        # Build a single OR'd Q so the values combine into "match any
        # of these effective statuses" semantics.
        effective_q = Q()

        if "ON_SITE" in stored_vals:
            # Effective ON_SITE = stored is ON_SITE, AND user has at
            # least one contract (so they're not NEW_APPLICANT), AND
            # has no active contract (so they're not ON_BOARD).
            effective_q |= Q(user_status=User_Status.ON_SITE.value) & Q(
                pk__in=queryset.model.objects.filter(has_any_contract).values("pk")
            ) & ~Q(
                pk__in=queryset.model.objects.filter(has_active_contract).values("pk")
            )
        for v in stored_vals:
            if v == User_Status.ON_SITE.value:
                continue
            # VACATION and MEDICAL_VACATION are admin overrides;
            # they apply regardless of contract state.
            effective_q |= Q(user_status=v)

        manual_block = (
            Q(user_status=User_Status.VACATION.value)
            | Q(user_status=User_Status.MEDICAL_VACATION.value)
        )
        if wants_on_board:
            # Has an Active/Signed contract that hasn't been signed off.
            today = timezone.localdate()
            contract_q = (
                Q(contracts__status__in=("Active", "Signed"))
                & (Q(contracts__sign_off_date__isnull=True)
                   | Q(contracts__sign_off_date__gte=today))
            )
            effective_q |= (~manual_block & contract_q)
        if wants_new_applicant:
            # "No contracts at all" — Django's contracts__isnull=True
            # checks the FK on the related row, not the absence of
            # related rows, so we need a subquery.
            no_contracts = ~Exists(
                Contract.objects.filter(user=OuterRef("pk"))
            )
            # Run the subquery against the queryset's model so this
            # works for any model the filter is mounted on (Users
            # today, possibly others later).
            effective_q |= (~manual_block & Q(
                pk__in=queryset.model.objects.filter(no_contracts).values("pk")
            ))

        return queryset.filter(effective_q).distinct()

    def filter_nationality(self, queryset, name, value):
        vals = self._strings_for("nationality")
        if vals is None:
            return queryset
        if not vals:
            return queryset.none()
        return queryset.filter(nationality__in=vals)

    rank_name = django_filters.CharFilter(field_name="codes__name", lookup_expr="icontains")
    assigned_code = django_filters.CharFilter(field_name="user_ranks__assigned_code", lookup_expr="icontains")

    role = django_filters.CharFilter(method="filter_role")
    is_blacklisted = django_filters.BooleanFilter(field_name="is_blacklisted")

    def filter_role(self, queryset, name, value):
        vals = self._strings_for("role")
        if vals is None:
            return queryset
        if not vals:
            return queryset.none()
        return queryset.filter(role__in=vals)

    company = django_filters.CharFilter(method="filter_company")
    company_name = django_filters.CharFilter(field_name="contracts__company__company_name", lookup_expr="icontains")

    def filter_company(self, queryset, name, value):
        ids = [int(v) for v in self.request.GET.getlist("company") if str(v).strip().isdigit()]
        if not ids:
            return queryset
        return queryset.filter(contracts__company__id__in=ids).distinct()

    ship = django_filters.CharFilter(method="filter_ship")
    ship_name = django_filters.CharFilter(field_name="contracts__ship__ship_name", lookup_expr="icontains")
    
    job_position_name = django_filters.CharFilter(field_name="contracts__job_position__rank__name", lookup_expr="icontains")

    def filter_ship(self, queryset, name, value):
        ids = [int(v) for v in self.request.GET.getlist("ship") if str(v).strip().isdigit()]
        if not ids:
            return queryset
        return queryset.filter(contracts__ship__id__in=ids).distinct()

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
    
    contract_status = CharInFilter(field_name="contracts__status", lookup_expr="in")
    
    signed_on_from = django_filters.DateFilter(field_name="contracts__sign_on_date", lookup_expr="gte")
    signed_on_to = django_filters.DateFilter(field_name="contracts__sign_on_date", lookup_expr="lte")
    signed_off_from = django_filters.DateFilter(field_name="contracts__sign_off_date", lookup_expr="gte")
    signed_off_to = django_filters.DateFilter(field_name="contracts__sign_off_date", lookup_expr="lte")

    contract_status = django_filters.CharFilter(method="filter_contract_status")
    company_type = django_filters.CharFilter(method="filter_company_type")
    ship_type = django_filters.CharFilter(method="filter_ship_type")

    def filter_contract_status(self, queryset, name, value):
        vals = self._strings_for("contract_status")
        if vals is None:
            return queryset
        if not vals:
            return queryset.none()
        return queryset.filter(contracts__status__in=vals).distinct()

    def filter_company_type(self, queryset, name, value):
        vals = self._strings_for("company_type")
        if vals is None:
            return queryset
        if not vals:
            return queryset.none()
        return queryset.filter(contracts__company__company_type__name__in=vals).distinct()

    def filter_ship_type(self, queryset, name, value):
        vals = self._strings_for("ship_type")
        if vals is None:
            return queryset
        if not vals:
            return queryset.none()
        return queryset.filter(contracts__ship__ship_type__name__in=vals).distinct()

    passport_no = django_filters.CharFilter(field_name="passport_no", lookup_expr="icontains")
    passport_type = django_filters.CharFilter(field_name="personal_documents__document_type", lookup_expr="icontains")
    passport_expiry_from = django_filters.DateFilter(field_name="passport_expiry_date", lookup_expr="gte")
    passport_expiry_to = django_filters.DateFilter(field_name="passport_expiry_date", lookup_expr="lte")
    
    seaman_book_no = django_filters.CharFilter(field_name="seaman_book_no", lookup_expr="icontains")
    seaman_book_type = django_filters.CharFilter(field_name="personal_documents__document_type", lookup_expr="icontains")
    seaman_book_expiry_from = django_filters.DateFilter(field_name="seaman_book_expiry_date", lookup_expr="gte")
    seaman_book_expiry_to = django_filters.DateFilter(field_name="seaman_book_expiry_date", lookup_expr="lte")
    
    document_type = django_filters.CharFilter(method="filter_document_type")

    def filter_document_type(self, queryset, name, value):
        vals = self._strings_for("document_type")
        if vals is None:
            return queryset
        if not vals:
            return queryset.none()
        return queryset.filter(personal_documents__document_type__in=vals).distinct()
    
    medical_no = django_filters.CharFilter(field_name="health_number", lookup_expr="icontains")
    medical_expiry_from = django_filters.DateFilter(field_name="health_expiry_date", lookup_expr="gte")
    medical_expiry_to = django_filters.DateFilter(field_name="health_expiry_date", lookup_expr="lte")
    
    course_name = django_filters.CharFilter(field_name="courses__course_name", lookup_expr="icontains")

    document_status = django_filters.CharFilter(field_name="documents__status", lookup_expr="iexact")
    document_title = django_filters.CharFilter(field_name="documents__title", lookup_expr="icontains")

    position = django_filters.CharFilter(method='filter_by_position')
    
    def filter_by_position(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(
            Q(codes__name__icontains=value) | 
            Q(application_for_position__icontains=value)
        ).distinct()

    class Meta:
        model = Users
        fields = [
            "name", "age", "marital_status", "user_status", "nationality", 
            "nearest_port", "role", "is_blacklisted", "company", "ship",
            "language", "contract_status", "position", "document_status", "document_title",
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
    record_type = django_filters.CharFilter(field_name="record_type", lookup_expr="iexact")
    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")
    start_date_from = django_filters.DateFilter(field_name="start_date", lookup_expr="gte")
    start_date_to = django_filters.DateFilter(field_name="start_date", lookup_expr="lte")

    class Meta:
        model = FinanceRecord
        fields = ["user", "company", "record_type", "status"]


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

class ShipFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="ship_name", lookup_expr="icontains")
    imo_number = django_filters.CharFilter(field_name="imo_number", lookup_expr="icontains")
    company = django_filters.CharFilter(method="filter_company")
    status = django_filters.AllValuesMultipleFilter(field_name="status")
    flag = CharInFilter(field_name="flag__name", lookup_expr="in")
    ship_type = CharInFilter(field_name="ship_type__name", lookup_expr="in")

    class Meta:
        model = Ship
        fields = ["name", "imo_number", "company", "status", "flag", "ship_type"]

    def filter_company(self, queryset, name, value):
        """
        Handle ?company=2&company=10 (multi-select) and ?company=2 (single).

        IMPORTANT: `name` in django-filter method callbacks is the FIELD
        name, which in older versions can resolve to the DB lookup
        ('company__id') rather than the URL param ('company'). To stay
        safe we hardcode the URL param name here.
        """
        # Always read the raw repeated values from the request.
        # Hardcoded 'company' — the URL param name, NOT the DB lookup.
        all_values = self.request.GET.getlist("company")

        if not all_values:
            return queryset

        ids = [int(v) for v in all_values if str(v).strip().isdigit()]
        if not ids:
            return queryset.none()
        return queryset.filter(company__id__in=ids)


class ContractFilter(django_filters.FilterSet):
    user = django_filters.CharFilter(method="filter_user")
    ship = django_filters.CharFilter(method="filter_ship")
    company = django_filters.CharFilter(method="filter_company_id")
    rank = django_filters.CharFilter(method="filter_rank_id")
    status = django_filters.AllValuesMultipleFilter(field_name="status")

    sign_on_from = django_filters.DateFilter(field_name="sign_on_date", lookup_expr="gte")
    sign_on_to = django_filters.DateFilter(field_name="sign_on_date", lookup_expr="lte")
    sign_off_from = django_filters.DateFilter(field_name="sign_off_date", lookup_expr="gte")
    sign_off_to = django_filters.DateFilter(field_name="sign_off_date", lookup_expr="lte")

    applicant_name = django_filters.CharFilter(field_name="user__first_name", lookup_expr="icontains")

    class Meta:
        model = Contract
        fields = ["user", "ship", "company", "rank", "status"]

    def _ids_for(self, param_name):
        """Pull repeated ?key=1&key=2 values from the request, parse as ints."""
        raw = self.request.GET.getlist(param_name)
        if not raw:
            return None
        ids = [int(v) for v in raw if str(v).strip().isdigit()]
        if not ids:
            return []
        return ids

    def filter_user(self, queryset, name, value):
        ids = self._ids_for("user")
        if ids is None:
            return queryset
        if not ids:
            return queryset.none()
        return queryset.filter(user__id__in=ids)

    def filter_ship(self, queryset, name, value):
        ids = self._ids_for("ship")
        if ids is None:
            return queryset
        if not ids:
            return queryset.none()
        return queryset.filter(ship__id__in=ids)

    def filter_company_id(self, queryset, name, value):
        ids = self._ids_for("company")
        if ids is None:
            return queryset
        if not ids:
            return queryset.none()
        return queryset.filter(company__id__in=ids)

    def filter_rank_id(self, queryset, name, value):
        ids = self._ids_for("rank")
        if ids is None:
            return queryset
        if not ids:
            return queryset.none()
        return queryset.filter(rank__id__in=ids)