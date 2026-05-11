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


class UsersFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="first_name", lookup_expr="icontains")
    age = django_filters.NumberFilter(field_name="age", lookup_expr="exact")
    marital_status = django_filters.CharFilter(field_name="marital_status", lookup_expr="iexact")
    user_status = django_filters.CharFilter(field_name="user_status", lookup_expr="iexact")
    nationality = django_filters.CharFilter(field_name="nationality", lookup_expr="icontains")
    nearest_port = django_filters.CharFilter(field_name="Nearest_Port", lookup_expr="icontains")
    
    # Position filters
    rank_name = django_filters.CharFilter(field_name="codes__name", lookup_expr="icontains")
    assigned_code = django_filters.CharFilter(field_name="user_ranks__assigned_code", lookup_expr="icontains")
    
    role = django_filters.CharFilter(field_name="role", lookup_expr="iexact")
    is_blacklisted = django_filters.BooleanFilter(field_name="is_blacklisted")
    
    # New requested filters
    # Filter by Company (ID or Name)
    company = django_filters.NumberFilter(field_name="contracts__company__id")
    company_name = django_filters.CharFilter(field_name="contracts__company__company_name", lookup_expr="icontains")
    
    # Filter by Ship (ID or Name)
    ship = django_filters.NumberFilter(field_name="contracts__ship__id")
    ship_name = django_filters.CharFilter(field_name="contracts__ship__ship_name", lookup_expr="icontains")
    
    # Filter by Job Position Name (linked to JobOrderPosition/Rank)
    job_position_name = django_filters.CharFilter(field_name="contracts__job_position__rank__name", lookup_expr="icontains")
    
    # Filter by Language
    language = django_filters.CharFilter(field_name="languages__language", lookup_expr="icontains")
    
    # Filter by Contract Status (Signed, Draft, Cancelled, etc.)
    contract_status = django_filters.AllValuesMultipleFilter(field_name="contracts__status")
    
    # Filter by Signed On/Off dates
    signed_on_from = django_filters.DateFilter(field_name="contracts__sign_on_date", lookup_expr="gte")
    signed_on_to = django_filters.DateFilter(field_name="contracts__sign_on_date", lookup_expr="lte")
    signed_off_from = django_filters.DateFilter(field_name="contracts__sign_off_date", lookup_expr="gte")
    signed_off_to = django_filters.DateFilter(field_name="contracts__sign_off_date", lookup_expr="lte")

    # Company and Ship Types
    company_type = django_filters.CharFilter(field_name="contracts__company__company_type__name", lookup_expr="icontains")
    ship_type = django_filters.CharFilter(field_name="contracts__ship__ship_type__name", lookup_expr="icontains")
    
    # Passport Details
    passport_no = django_filters.CharFilter(field_name="passport_no", lookup_expr="icontains")
    passport_expiry_from = django_filters.DateFilter(field_name="passport_expiry_date", lookup_expr="gte")
    passport_expiry_to = django_filters.DateFilter(field_name="passport_expiry_date", lookup_expr="lte")
    
    # Seaman Book Details
    seaman_book_no = django_filters.CharFilter(field_name="seaman_book_no", lookup_expr="icontains")
    seaman_book_expiry_from = django_filters.DateFilter(field_name="seaman_book_expiry_date", lookup_expr="gte")
    seaman_book_expiry_to = django_filters.DateFilter(field_name="seaman_book_expiry_date", lookup_expr="lte")
    
    # Medical Details
    medical_no = django_filters.CharFilter(field_name="health_number", lookup_expr="icontains")
    medical_expiry_from = django_filters.DateFilter(field_name="health_expiry_date", lookup_expr="gte")
    medical_expiry_to = django_filters.DateFilter(field_name="health_expiry_date", lookup_expr="lte")
    
    # Marine Courses
    course_name = django_filters.CharFilter(field_name="courses__course_name", lookup_expr="icontains")

    # Document Types (Personal Documents)
    passport_type = django_filters.CharFilter(field_name="personal_documents__document_type", lookup_expr="icontains")
    seaman_book_type = django_filters.CharFilter(field_name="personal_documents__document_type", lookup_expr="icontains")
    document_type = django_filters.CharFilter(field_name="personal_documents__document_type", lookup_expr="icontains")

    # Filter by position (Rank name or Application position)
    position = django_filters.CharFilter(method='filter_by_position')
    
    def filter_by_position(self, queryset, name, value):
        return queryset.filter(
            Q(codes__name__icontains=value) | 
            Q(application_for_position__icontains=value)
        ).distinct()

    class Meta:
        model = Users
        fields = [
            "name", "age", "marital_status", "user_status", "nationality", 
            "nearest_port", "role", "is_blacklisted", "company", "ship",
            "language", "contract_status", "position"
        ]


class CompanyFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    company_type = django_filters.CharFilter(field_name="company_type", lookup_expr="iexact")
    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")

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
    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")
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
    company = django_filters.NumberFilter(field_name="company__id")
    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")
    flag = django_filters.CharFilter(field_name="flag__name", lookup_expr="icontains")
    ship_type = django_filters.CharFilter(field_name="ship_type__name", lookup_expr="icontains")

    class Meta:
        model = Ship
        fields = ["name", "imo_number", "company", "status", "flag", "ship_type"]