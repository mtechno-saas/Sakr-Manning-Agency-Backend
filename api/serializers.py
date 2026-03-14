from datetime import datetime
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

class FlexibleDateField(serializers.DateField):
    def to_internal_value(self, value):
        if not value:
            return None
            
        if isinstance(value, str):
            for fmt in ('%Y-%m-%d', '%d-%m-%Y', '%m-%d-%Y', '%d/%m/%Y', '%m/%d/%Y'):
                try:
                    parsed_date = datetime.strptime(value.strip(), fmt).date()
                    return parsed_date
                except ValueError:
                    pass
                    
        return super().to_internal_value(value)

class UserSerializer(serializers.ModelSerializer):
    is_online = serializers.SerializerMethodField()
    
    # Case Insensitive Choices
    role = CaseInsensitiveChoiceField(choices=Users.ROLE_CHOICES, required=False)
    application_for_position = CaseInsensitiveChoiceField(choices=Users.APPLICATION_POSITION_CHOICES, required=False, allow_blank=True, allow_null=True)
    coc_certificate_name = CaseInsensitiveChoiceField(choices=Users.COC_CERTIFICATE_CHOICES, required=False, allow_blank=True, allow_null=True)
    marital_status = CaseInsensitiveChoiceField(choices=[('SINGLE', 'SINGLE'), ('MARRIED', 'MARRIED')], required=False, allow_blank=True, allow_null=True)
    user_status = CaseInsensitiveChoiceField(choices=[('VACATION', 'VACATION'), ('ON_SITE', 'ON_SITE'), ('MEDICAL VACATION', 'MEDICAL VACATION')], required=False, allow_blank=True, allow_null=True)

    # Flexible Dates
    date_of_birth = FlexibleDateField(required=False, allow_null=True)
    available_date = FlexibleDateField(required=False, allow_null=True)
    register_date = FlexibleDateField(required=False, allow_null=True)
    passport_issue_date = FlexibleDateField(required=False, allow_null=True)
    passport_expiry_date = FlexibleDateField(required=False, allow_null=True)
    seaman_book_issue_date = FlexibleDateField(required=False, allow_null=True)
    seaman_book_expiry_date = FlexibleDateField(required=False, allow_null=True)
    other_seaman_book_issue_date = FlexibleDateField(required=False, allow_null=True)
    other_seaman_book_expiry_date = FlexibleDateField(required=False, allow_null=True)
    coc_issue_date = FlexibleDateField(required=False, allow_null=True)
    coc_expiry_date = FlexibleDateField(required=False, allow_null=True)
    goc_issue_date = FlexibleDateField(required=False, allow_null=True)
    goc_expiry_date = FlexibleDateField(required=False, allow_null=True)
    health_issue_date = FlexibleDateField(required=False, allow_null=True)
    health_expiry_date = FlexibleDateField(required=False, allow_null=True)
    international_medical_issue_date = FlexibleDateField(required=False, allow_null=True)
    international_medical_expiry_date = FlexibleDateField(required=False, allow_null=True)
    yellow_fever_issue_date = FlexibleDateField(required=False, allow_null=True)
    yellow_fever_expiry_date = FlexibleDateField(required=False, allow_null=True)
    cholera_issue_date = FlexibleDateField(required=False, allow_null=True)
    cholera_expiry_date = FlexibleDateField(required=False, allow_null=True)
    covid_first_dose = FlexibleDateField(required=False, allow_null=True)
    covid_second_dose = FlexibleDateField(required=False, allow_null=True)
    declaration_date = FlexibleDateField(required=False, allow_null=True)
    marlins_test_issued_date = FlexibleDateField(required=False, allow_null=True)
    ces_test_issued_date = FlexibleDateField(required=False, allow_null=True)

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

