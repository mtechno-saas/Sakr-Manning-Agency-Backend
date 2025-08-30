


# api/serializers.py
from rest_framework import serializers
from .models import Users, UserRank, Certificate, Rank
from tickets_papers.models import Ticket, TravelingPaper


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


# class UsersSerializer(serializers.ModelSerializer):
#     # Read-only nested serializers for detailed representation
#     ranks = UserRankSerializer(source='user_ranks', many=True, read_only=True)
#     certificates = CertificateSerializer(many=True, read_only=True)

#     # Write-only fields for accepting lists of IDs during create/update
#     rank_ids = serializers.PrimaryKeyRelatedField(
#         queryset=Rank.objects.all(),
#         many=True,
#         write_only=True,
#         source='codes',
#         required=False,
#         help_text="List of Rank IDs to assign."
#     )
#     certificate_ids = serializers.PrimaryKeyRelatedField(
#         queryset=Certificate.objects.all(),
#         many=True,
#         write_only=True,
#         source='certificates',
#         required=False,
#         help_text="List of Certificate IDs to assign."
#     )

#     class Meta:
#         model = Users
#         # Use '__all__' to include all model fields automatically
#         fields = '__all__'

#     def to_representation(self, instance):
#         """
#         Modify the output representation of the serializer.
#         """
#         # Get the default representation (which will include all model fields)
#         representation = super().to_representation(instance)
        
#         # Add the custom nested representations for 'ranks' and 'certificates'
#         representation['ranks'] = UserRankSerializer(instance.user_ranks.all(), many=True).data
#         representation['certificates'] = CertificateSerializer(instance.certificates.all(), many=True).data
        
#         # The 'codes' field from the model (which is a list of Rank IDs) is not needed in the output,
#         # as we have the more detailed 'ranks' field. We can remove it.
#         representation.pop('codes', None)
        
#         return representation

#     def create(self, validated_data):
#         codes_data = validated_data.pop('codes', [])
#         certificates_data = validated_data.pop('certificates', [])

#         user = Users.objects.create(**validated_data)

#         for rank in codes_data:
#             UserRank.objects.create(user=user, rank=rank)

#         if certificates_data:
#             user.certificates.set(certificates_data)

#         return user

#     def update(self, instance, validated_data):
#         codes_data = validated_data.pop('codes', None)
#         certificates_data = validated_data.pop('certificates', None)

#         # Update standard fields
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#         instance.save()

#         # Handle rank updates
#         if codes_data is not None:
#             instance.user_ranks.all().delete()
#             for rank in codes_data:
#                 UserRank.objects.create(user=instance, rank=rank)

#         # Handle certificate updates
#         if certificates_data is not None:
#             instance.certificates.set(certificates_data)

#         return instance

# api/serializers.py

# ... (keep your other serializers: UserRankSerializer, CertificateSerializer, etc.)

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



    