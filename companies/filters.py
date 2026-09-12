import django_filters
from .models import Company, JobOrderPosition


class CompanyFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="company_name", lookup_expr="icontains")
    # `company_type` is a ForeignKey to CompanyType; filter on the related
    # `name` (the string the API exposes), not the FK ID. Supports BOTH
    # repeated params (?company_type=A&company_type=B) and a single
    # comma-separated value (?company_type=A,B). Without this method, the
    # default CharFilter only sees the last value when the param is repeated.
    company_type = django_filters.CharFilter(method="filter_company_type")
    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")

    class Meta:
        model = Company
        fields = ["name", "company_type", "status"]

    def filter_company_type(self, queryset, name, value):
        # CharFilter hands us only one value, so read all repetitions
        # straight from the query string. Also split each value on commas
        # so a single-param call (?company_type=A,B) works too.
        raw = self.request.GET.getlist("company_type")
        cleaned = []
        for v in raw:
            if v is None:
                continue
            for piece in str(v).split(","):
                piece = piece.strip()
                if piece:
                    cleaned.append(piece)
        if not cleaned:
            return queryset
        return queryset.filter(company_type__name__in=cleaned).distinct()


class JobOrderPositionFilter(django_filters.FilterSet):
    """
    Mirrors the JobOrderPositionSerializer.to_internal_value() behavior:
    - rank     can be a numeric ID OR a name (case-insensitive)
    - status   filters on the related job_order.status (supports multiple values)
    - company  filters on the related job_order.company.company_name (or numeric ID)
    """
    rank = django_filters.CharFilter(method="filter_rank")
    # Use a method-based filter instead of CharFilter so that repeated
    # ?status=A&status=B query params (and the comma-separated form) both
    # work — CharFilter only sees the LAST value for repeated params.
    status = django_filters.CharFilter(method="filter_status")
    company = django_filters.CharFilter(method="filter_company")

    class Meta:
        model = JobOrderPosition
        fields = ["rank", "status", "company"]

    def _split_values(self, param_name):
        """
        Read repeated (?key=A&key=B) and/or comma-separated (?key=A,B)
        values from the query string. Returns an empty list if the param
        is absent, or a list of stripped non-empty strings otherwise.
        """
        raw = self.request.GET.getlist(param_name)
        cleaned = []
        for v in raw:
            if v is None:
                continue
            for piece in str(v).split(","):
                piece = piece.strip()
                if piece:
                    cleaned.append(piece)
        return cleaned

    def filter_status(self, queryset, name, value):
        cleaned = self._split_values("status")
        if not cleaned:
            return queryset
        return queryset.filter(job_order__status__in=cleaned).distinct()

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
