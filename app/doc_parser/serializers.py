from rest_framework import serializers
from .models import ParsedDocument

class ParsedDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParsedDocument
        fields = [
            'id',
            'source_file',
            'extracted_data_yaml',
            'status',
            'created_at',
            'associated_user'
        ]
        read_only_fields = [
            'extracted_data_yaml',
            'status',
            'created_at',
            'associated_user'
        ]