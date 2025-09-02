


# api/serializers.py
from rest_framework import serializers
from .models import Users, UserRank, Certificate, Rank , Contract
from tickets_papers.models import Ticket, TravelingPaper
from django.contrib.auth.models import User                   # Or your custom Users model
from rest_framework import serializers, validators
from ships.serializers import ShipSerializer # To show ship details in contract


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["id", "ticket_number"]


class TravelingPaperSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelingPaper
        fields = ["id", "title"]


class RankSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rank
        fields = ["name"]


class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = ["id", "code", "name"]


class UserRankSerializer(serializers.ModelSerializer):
    rank = RankSerializer(read_only=True)
    code = serializers.CharField(source='rank.code', read_only=True)

    class Meta:
        model = UserRank
        fields = ["assigned_code", "code", "rank"]



class UsersSerializer(serializers.ModelSerializer):
    # Read-only nested serializers for detailed representation
    ranks = UserRankSerializer(source='user_ranks', many=True, read_only=True)
    certificates = CertificateSerializer(many=True, read_only=True)

    # Write-only fields for accepting lists of IDs during create/update
    rank_ids = serializers.PrimaryKeyRelatedField(
        queryset=Rank.objects.all(),
        many=True,
        write_only=True,
        source='codes',
        required=False,
        help_text="List of Rank IDs to assign."
    )
    certificate_ids = serializers.PrimaryKeyRelatedField(
        queryset=Certificate.objects.all(),
        many=True,
        write_only=True,
        source='certificates',
        required=False,
        help_text="List of Certificate IDs to assign."
    )

    class Meta:
        model = Users
        fields = '__all__'
        # The 'profile_image' field is automatically included by '__all__'.
        # We make it not required so users can be created/updated without changing the image.
        extra_kwargs = {
            'profile_image': {'required': False}
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['ranks'] = UserRankSerializer(instance.user_ranks.all(), many=True).data
        representation['certificates'] = CertificateSerializer(instance.certificates.all(), many=True).data
        representation.pop('codes', None)
        return representation

    def create(self, validated_data):
        # Pop the relationship data first
        codes_data = validated_data.pop('codes', [])
        certificates_data = validated_data.pop('certificates', [])
        # Explicitly pop the profile_image data
        profile_image_data = validated_data.pop('profile_image', None)

        # Create the user instance with the remaining standard fields
        user = Users.objects.create(**validated_data)

        # Handle the profile image if it was provided
        if profile_image_data:
            user.profile_image = profile_image_data
            user.save()

        # Handle the M2M relationships
        for rank in codes_data:
            UserRank.objects.create(user=user, rank=rank)
        if certificates_data:
            user.certificates.set(certificates_data)

        return user

    def update(self, instance, validated_data):
        # Pop relationship and file data
        codes_data = validated_data.pop('codes', None)
        certificates_data = validated_data.pop('certificates', None)
        profile_image_data = validated_data.pop('profile_image', None)

        # Update standard fields using the default DRF update method
        # This is safer and more efficient than a manual setattr loop.
        instance = super().update(instance, validated_data)

        # Handle the profile image update separately if a new image was provided
        if profile_image_data is not None:
            instance.profile_image = profile_image_data
            instance.save()

        # Handle relationship updates
        if codes_data is not None:
            instance.user_ranks.all().delete()
            for rank in codes_data:
                UserRank.objects.create(user=instance, rank=rank)
        if certificates_data is not None:
            instance.certificates.set(certificates_data)

        return instance

# Create a new Serializer for Registration

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ('email', 'password', 'first_name', 'last_name')

        extra_kwargs = {
            "password": {"write_only": True},
            "email": {
                "required": True,
                "allow_blank": False,
                "validators": [
                    validators.UniqueValidator(
                        Users.objects.all(),
                        # --- This is the line to add/change ---
                        message="This email is already registered."
                    )
                ]
            }
        }

    def create(self, validated_data):
        user = Users.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        return user
    


# --- New ContractSerializer ---
class ContractSerializer(serializers.ModelSerializer):
    # Use nested serializers for readable output
    user = serializers.StringRelatedField() # Show user's email
    ship = serializers.StringRelatedField() # Show ship's name
    rank = serializers.StringRelatedField() # Show rank's name

    # Use IDs for writable input
    user_id = serializers.IntegerField(write_only=True)
    ship_id = serializers.IntegerField(write_only=True)
    rank_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Contract
        fields = [
            'id',
            'user', 'user_id',
            'ship', 'ship_id',
            'rank', 'rank_id',
            'sign_on_date', 'sign_off_date', 'salary', 'status',
            'created_at', 'updated_at'
        ]

# --- Updated UsersSerializer ---
class UsersSerializer(serializers.ModelSerializer):
    # Add the new ContractSerializer to show a user's employment history
    contracts = ContractSerializer(many=True, read_only=True)

    # ... (keep all your other nested serializers like ranks, certificates)

    class Meta:
        model = Users
        fields = [
            # ... (include all your existing fields: id, email, first_name, etc.)
            'id', 'email', 'first_name', 'middle_name', 'last_name', 'gender',
            'blood_type', 'smoker', 'us_visa_status', 'schengen_visa_status',
            # ... (and all other fields)
            'contracts' # <-- Add the new contracts field
        ]
        # If you are using fields = '__all__', this will be included automatically.



