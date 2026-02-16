from rest_framework import serializers
from .models import Course

class CourseSerializer(serializers.ModelSerializer):
    document = serializers.FileField(required=False, allow_null=True, default=None)
    
    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ['user']

    def validate_document(self, value):
        """Accept empty strings as None for JSON submissions"""
        if value == '' or value is None:
            return None
        return value