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
        fields = ['id', 'first_name', 'last_name', 'email']


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

    class Meta:
        model = Ship
        # Add the new fields to the list
        fields = [
            'id', 'ship_name', 'imo_number', 'ship_type', 'flag_country',
            'company', 'status', 'crew', 'crew_ids', 'created_at', 'updated_at'
        ]
