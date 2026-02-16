import django_filters
from .models import Company


class CompanyFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="company_name", lookup_expr="icontains")
    company_type = django_filters.CharFilter(field_name="company_type", lookup_expr="iexact")
    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")

    class Meta:
        model = Company
        fields = ["name", "company_type", "status"]
