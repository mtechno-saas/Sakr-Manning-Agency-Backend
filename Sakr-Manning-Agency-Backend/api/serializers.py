from django.core.cache import cache
from rest_framework import serializers
from .models import Users, UserCertificate, Certificate

class UserSerializer(serializers.ModelSerializer):
    is_online = serializers.SerializerMethodField()

    class Meta:
        model = Users
        exclude = ['middle_name']

    def get_is_online(self, obj):
        # Check cache for user activity
        # Key matches what we set in middleware
        return cache.get(f'online_user_{obj.id}') is not None


class UserCertificateSerializer(serializers.ModelSerializer):
    """
    Serializer for UserCertificate model.
    Includes nested certificate type information and calculated fields.
    """
    certificate_type_name = serializers.CharField(source='certificate_type.name', read_only=True, allow_null=True)
    certificate_type_code = serializers.CharField(source='certificate_type.code', read_only=True, allow_null=True)
    rank_name = serializers.CharField(source='rank.name', read_only=True, allow_null=True)
    is_expired = serializers.ReadOnlyField()
    
    class Meta:
        model = UserCertificate
        fields = [
            'id',
            'user',
            'certificate_type',
            'certificate_type_name',
            'certificate_type_code',
            'document_name',
            'document_number',
            'country_of_issue',
            'issue_date',
            'expiry_date',
            'issued_by',
            'issued_at',
            'certificate_file',
            'category',
            'rank',
            'rank_name',
            'is_expired',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at', 'is_expired']

