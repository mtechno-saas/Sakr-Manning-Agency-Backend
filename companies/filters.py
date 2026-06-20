import django_filters
from django_filters.widgets import QueryArrayWidget
from .models import Company


# ---------- Multi-value filter base classes ----------
# See api/filters.py for the rationale — django_filters' default BaseCSVWidget
# silently drops repeated query keys (only keeps the LAST value). QueryArrayWidget
# supports the repeated-key, array-notation, and CSV formats the frontend uses.
class CharInFilter(django_filters.BaseInFilter, django_filters.CharFilter):
    """CharFilter that accepts repeated query keys (?k=a&k=b) and array notation (?k[]=a&k[]=b).
    See api/filters.py for why we inject the widget via __init__ kwargs instead of as a class attr.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", QueryArrayWidget)
        super().__init__(*args, **kwargs)


class NumberInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    """NumberFilter that accepts repeated query keys / array notation."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", QueryArrayWidget)
        super().__init__(*args, **kwargs)


class CompanyFilter(django_filters.FilterSet):
    """
    Per global_filters_reference.md:
      - name           string  icontains   ?name=maersk
      - company_type   list    multiple    ?company_type=Agency&company_type=Owner
      - status         list    multiple    ?status=Active&status=Inactive
    """
    name = django_filters.CharFilter(field_name="company_name", lookup_expr="icontains")
    company_type = CharInFilter(field_name="company_type__name", lookup_expr="in")
    status = CharInFilter(field_name="status", lookup_expr="in")

    class Meta:
        model = Company
        fields = ["name", "company_type", "status"]
