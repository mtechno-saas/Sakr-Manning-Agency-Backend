from rest_framework import serializers
from .models import Course

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'
        read_only_fields = ['user']
        extra_kwargs = {
            'document': {'required': False, 'allow_null': True},
        }