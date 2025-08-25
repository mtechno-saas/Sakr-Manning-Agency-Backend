

# # api/serializers.py
# from rest_framework import serializers
# from .models import Users, UserRank, Certificate, Rank
# from tickets_papers.models import Ticket, TravelingPaper


# class TicketSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Ticket
#         fields = ["id", "ticket_number"]


# class TravelingPaperSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TravelingPaper
#         fields = ["id", "title"]


# class RankSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Rank
#         # We only need the name here, as code and assigned_code will be at the top level
#         fields = ["name"]


# class CertificateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Certificate
#         fields = ["id", "code", "name"]


# class UserRankSerializer(serializers.ModelSerializer):
#     # Nest the RankSerializer to get the rank's name
#     rank = RankSerializer(read_only=True)
#     # Expose the rank's code directly from the related rank object
#     code = serializers.CharField(source='rank.code', read_only=True)

#     class Meta:
#         model = UserRank
#         # The fields to be displayed for each rank entry
#         fields = ["assigned_code", "code", "rank"]


# class UsersSerializer(serializers.ModelSerializer):
#     # Point to the user_ranks related_name from the UserRank model
#     # This will use UserRankSerializer to represent each item
#     ranks = UserRankSerializer(source='user_ranks', many=True, read_only=True)
    
#     certificates = CertificateSerializer(many=True, read_only=True)

#     # These fields are for writing (creating/updating) ranks and certificates
#     rank_ids = serializers.PrimaryKeyRelatedField(
#         queryset=Rank.objects.all(),
#         many=True,
#         write_only=True,
#         source='codes', # Keep targeting the 'codes' M2M field on the Users model
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
#         fields = [
#             "id", "first_name", "last_name", "email",
#             "ranks", "certificates", # Read-only fields with full details
#             "rank_ids", "certificate_ids" # Write-only fields for IDs
#         ]

#     def create(self, validated_data):
#         # The 'source' argument on the write-only fields handles this automatically.
#         # 'codes' and 'certificates' data is correctly extracted.
#         codes_data = validated_data.pop('codes', [])
#         certificates_data = validated_data.pop('certificates', [])

#         user = Users.objects.create(**validated_data)

#         # Create UserRank instances for each assigned rank
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
#             # Clear existing ranks and create new ones
#             instance.user_ranks.all().delete()
#             for rank in codes_data:
#                 UserRank.objects.create(user=instance, rank=rank)

#         # Handle certificate updates
#         if certificates_data is not None:
#             instance.certificates.set(certificates_data)

#         return instance


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
        # Use '__all__' to include all model fields automatically
        fields = '__all__'

    def to_representation(self, instance):
        """
        Modify the output representation of the serializer.
        """
        # Get the default representation (which will include all model fields)
        representation = super().to_representation(instance)
        
        # Add the custom nested representations for 'ranks' and 'certificates'
        representation['ranks'] = UserRankSerializer(instance.user_ranks.all(), many=True).data
        representation['certificates'] = CertificateSerializer(instance.certificates.all(), many=True).data
        
        # The 'codes' field from the model (which is a list of Rank IDs) is not needed in the output,
        # as we have the more detailed 'ranks' field. We can remove it.
        representation.pop('codes', None)
        
        return representation

    def create(self, validated_data):
        codes_data = validated_data.pop('codes', [])
        certificates_data = validated_data.pop('certificates', [])

        user = Users.objects.create(**validated_data)

        for rank in codes_data:
            UserRank.objects.create(user=user, rank=rank)

        if certificates_data:
            user.certificates.set(certificates_data)

        return user

    def update(self, instance, validated_data):
        codes_data = validated_data.pop('codes', None)
        certificates_data = validated_data.pop('certificates', None)

        # Update standard fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Handle rank updates
        if codes_data is not None:
            instance.user_ranks.all().delete()
            for rank in codes_data:
                UserRank.objects.create(user=instance, rank=rank)

        # Handle certificate updates
        if certificates_data is not None:
            instance.certificates.set(certificates_data)

        return instance



    