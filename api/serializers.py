from django.core.cache import cache
from rest_framework import serializers
from .models import Users, Document

class CaseInsensitiveChoiceField(serializers.ChoiceField):
    def to_internal_value(self, data):
        if data == '' and self.allow_blank:
            return ''
        
        try:
            data_str = str(data).strip().lower()
            for choice_value, choice_label in self.choices.items():
                if str(choice_value).strip().lower() == data_str:
                    return choice_value
        except (TypeError, ValueError):
            pass
            
        self.fail('invalid_choice', input=data)

class UserSerializer(serializers.ModelSerializer):
    is_online = serializers.SerializerMethodField()
    
    role = CaseInsensitiveChoiceField(choices=Users.ROLE_CHOICES, required=False)
    application_for_position = CaseInsensitiveChoiceField(choices=Users.APPLICATION_POSITION_CHOICES, required=False, allow_blank=True, allow_null=True)
    coc_certificate_name = CaseInsensitiveChoiceField(choices=Users.COC_CERTIFICATE_CHOICES, required=False, allow_blank=True, allow_null=True)
    marital_status = CaseInsensitiveChoiceField(choices=[('SINGLE', 'SINGLE'), ('MARRIED', 'MARRIED')], required=False, allow_blank=True, allow_null=True)
    user_status = CaseInsensitiveChoiceField(choices=[('VACATION', 'VACATION'), ('ON_SITE', 'ON_SITE'), ('MEDICAL VACATION', 'MEDICAL VACATION')], required=False, allow_blank=True, allow_null=True)

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

