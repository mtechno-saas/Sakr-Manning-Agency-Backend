from rest_framework import serializers
from django.core.files.uploadedfile import UploadedFile
from api.serializers import FlexibleDateField
from .models import Course

class CourseSerializer(serializers.ModelSerializer):
    document = serializers.FileField(required=False, allow_null=True, default=None)
    issue_date = FlexibleDateField(required=False, allow_null=True)
    expiry_date = FlexibleDateField(required=False, allow_null=True)
    
    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ['user']

    def to_internal_value(self, data):
        """Strip document field if it's not an actual file upload"""
        if isinstance(data, dict):
            doc = data.get('document')
            if doc is not None and not isinstance(doc, UploadedFile):
                data = data.copy()
                data.pop('document', None)
        return super().to_internal_value(data)