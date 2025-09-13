# from rest_framework import serializers
# from .models import ParsedDocument

# class ParsedDocumentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ParsedDocument
#         fields = [
#             'id',
#             'source_file',
#             'extracted_data_yaml',
#             'status',
#             'created_at',
#             'associated_user'
#         ]
#         read_only_fields = [
#             'extracted_data_yaml',
#             'status',
#             'created_at',
#             'associated_user'
#         ]


from rest_framework import serializers
from .models import ParsedDocument
from doc_parser.ai_parser_service import extract_document_features

class ParsedDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParsedDocument
        fields = "__all__"
        # fields = [
        #     'id',
        #     'source_file',
        #     #'raw_text', # Add the new raw_text field here
        #     'extracted_data_yaml',
        #     'status',
        #     'created_at',
        #     'associated_user'
        # ]
        # read_only_fields = [
        #     #'raw_text', # Mark raw_text as read-only as it's set by the backend
        #     'extracted_data_yaml',
        #     'status',
        #     'created_at',
        #     'associated_user'
        # ]
