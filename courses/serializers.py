from rest_framework import serializers
from django.core.files.uploadedfile import UploadedFile
from api.serializers import FlexibleDateField
from .models import Course

class CourseSerializer(serializers.ModelSerializer):
    document = serializers.FileField(required=False, allow_null=True, default=None)
    issue_date = FlexibleDateField(required=False, allow_null=True)
    expiry_date = FlexibleDateField(required=False, allow_null=True)
    download_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ['user', 'download_url']

    def get_download_url(self, obj):
        if getattr(obj, 'document', None) and getattr(obj, 'user', None):
            path = f"/api/users/{obj.user.id}/download-course/{obj.id}/"
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(path)
            return path
        return None

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.document and instance.user:
            ret['document'] = self.get_download_url(instance)
        return ret

    def to_internal_value(self, data):
        """Strip document field if it's not an actual file upload"""
        if isinstance(data, dict):
            doc = data.get('document')
            if doc is not None and not isinstance(doc, UploadedFile):
                data = data.copy()
                data.pop('document', None)
        return super().to_internal_value(data)