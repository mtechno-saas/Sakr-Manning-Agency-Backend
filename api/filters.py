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
import django_filters
from .models import Users

class UsersFilter(django_filters.FilterSet):
    # Filter by first_name or last_name containing the value
    name = django_filters.CharFilter(field_name="first_name", lookup_expr="icontains")
    
    # Filter by exact age
    age = django_filters.NumberFilter(field_name="age", lookup_expr="exact")
    
    # Filter by exact marital status (case-insensitive)
    marital_status = django_filters.CharFilter(field_name="marital_status", lookup_expr="iexact")
    
    # Filter by exact user status (case-insensitive)
    user_status = django_filters.CharFilter(field_name="user_status", lookup_expr="iexact")
    
    # Filter by nationality containing the value
    nationality = django_filters.CharFilter(field_name="nationality", lookup_expr="icontains")
    
    # Filter by nearest port containing the value
    nearest_port = django_filters.CharFilter(field_name="Nearest_Port", lookup_expr="icontains")
    
    # Filter by the name of the assigned rank (via the 'codes' M2M relationship)
    rank_name = django_filters.CharFilter(field_name="codes__name", lookup_expr="icontains")
    
    # Filter by the assigned_code from the UserRank model (via the 'user_ranks' relationship)
    assigned_code = django_filters.CharFilter(field_name="user_ranks__assigned_code", lookup_expr="icontains")

    class Meta:
        model = Users
        # The 'fields' list should only contain fields that are directly on the Users model
        # or filters that you want to be auto-generated.
        # Since we defined all our filters above, we can even make this list empty.
        # However, it's good practice to list the model fields you are filtering on.
        fields = [
            "name", 
            "age", 
            "marital_status", 
            "user_status", 
            "nationality", 
            "nearest_port",
            # 'rank_name' and 'assigned_code' are removed from here because they are not
            # direct fields on the Users model. The filter still works because they are
            # defined explicitly above.
        ]

