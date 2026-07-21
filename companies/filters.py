import django_filters
from .models import Company, JobOrderPosition


class CompanyFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="company_name", lookup_expr="icontains")
    company_type = django_filters.CharFilter(field_name="company_type", lookup_expr="iexact")
    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")

    class Meta:
        model = Company
        fields = ["name", "company_type", "status"]


class JobOrderPositionFilter(django_filters.FilterSet):
    """
    Mirrors the JobOrderPositionSerializer.to_internal_value() behavior:
    - rank     can be a numeric ID OR a name (case-insensitive)
    - status   filters on the related job_order.status
    - company  filters on the related job_order.company.company_name (or numeric ID)
    """
    rank = django_filters.CharFilter(method="filter_rank")
    status = django_filters.CharFilter(field_name="job_order__status", lookup_expr="iexact")
    company = django_filters.CharFilter(method="filter_company")

    class Meta:
        model = JobOrderPosition
        fields = ["rank", "status", "company"]

    def filter_rank(self, queryset, name, value):
        if not value:
            return queryset
        value = value.strip()
        if value.isdigit():
            return queryset.filter(rank_id=int(value))
        return queryset.filter(rank__name__iexact=value)

    def filter_company(self, queryset, name, value):
        if not value:
            return queryset
        value = value.strip()
        if value.isdigit():
            return queryset.filter(job_order__company_id=int(value))
        return queryset.filter(job_order__company__company_name__icontains=value)
