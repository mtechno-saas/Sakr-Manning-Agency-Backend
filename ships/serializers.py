# from rest_framework import serializers
# from .models import Ship

# class ShipSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Ship
#         fields = '__all__'


from rest_framework import serializers
from .models import Ship
# Import the Users model
from api.models import Users

# A simple serializer to represent a user in the crew list
class CrewMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'first_name', 'middle_name', 'email']


class ShipSerializer(serializers.ModelSerializer):
    # Use the CrewMemberSerializer to display nested crew details (read-only)
    crew = CrewMemberSerializer(many=True, read_only=True)

    # Add a write-only field to accept a list of user IDs when creating/updating a ship
    crew_ids = serializers.PrimaryKeyRelatedField(
        queryset=Users.objects.all(),
        many=True,
        write_only=True,
        source='crew', # This links it to the 'crew' model field for writing
        required=False
    )

    # Expose the string names for ForeignKeys so the frontend doesn't just get IDs (like 105)
    flag_name = serializers.CharField(source='flag.name', read_only=True)
    ship_type_name = serializers.CharField(source='ship_type.name', read_only=True)

    class Meta:
        model = Ship
        # Add the new fields to the list
        fields = [
            'id', 'ship_name', 'imo_number', 'ship_type', 'ship_type_name', 'flag', 'flag_name',
            'company', 'status', 'crew', 'crew_ids', 'official_no',
            'call_sign', 'mmsi_no', 'port_of_registry', 'gross_tonnage',
            'deadweight', 'year_built', 'builder', 'engine_type',
            'engine_power_kw', 'created_at', 'updated_at'
        ]
