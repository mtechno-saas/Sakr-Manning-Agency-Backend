from django.core.cache import cache
from rest_framework import serializers
from .models import Users, Document

class UserSerializer(serializers.ModelSerializer):
    is_online = serializers.SerializerMethodField()

    class Meta:
        model = Users
        fields = '__all__'

    def get_is_online(self, obj):
        # Check cache for user activity
        # Key matches what we set in middleware
        return cache.get(f'online_user_{obj.id}') is not None


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'user', 'title', 'file', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']

