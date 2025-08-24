import django_filters
from .models import Users

class UsersFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="first_name", lookup_expr="icontains")
    age = django_filters.NumberFilter(field_name="age")
    marital_status = django_filters.CharFilter(field_name="marital_status", lookup_expr="iexact")
    user_status = django_filters.CharFilter(field_name="user_status", lookup_expr="iexact")
    nationality = django_filters.CharFilter(field_name="nationality", lookup_expr="icontains")
    Nearest_Port = django_filters.CharFilter(field_name="Nearest_Port", lookup_expr="icontains")
    codes = django_filters.CharFilter(field_name="codes__name", lookup_expr="icontains")  

    class Meta:
        model = Users
        fields = ["name", "age", "marital_status", "user_status", "nationality", "Nearest_Port", "codes"]
