import re
from rest_framework import serializers
from .models import Company, Vacancy


class FlexibleURLField(serializers.CharField):
    """
    A lenient URL field that:
    - Accepts URLs with or without http/https prefix
    - Auto-prepends https:// if no scheme is provided
    - Accepts all country-code TLDs (.ph, .in, .ua, .eg, .gr, .ae, .cy, .mt, etc.)
    """
    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        if not value:
            return value

        value = value.strip()

        # Auto-prepend https:// if no scheme
        if value and not re.match(r'^https?://', value, re.IGNORECASE):
            value = f'https://{value}'

        # Basic URL validation: scheme + domain with at least one dot
        url_pattern = re.compile(
            r'^https?://'           # http:// or https://
            r'[a-zA-Z0-9-]+\.'     # domain
            r'[a-zA-Z]{2,}'        # TLD (2+ chars covers all country codes)
            r'(/.*)?$',            # optional path
            re.IGNORECASE
        )
        if not url_pattern.match(value):
            raise serializers.ValidationError('Enter a valid website URL.')

        return value


class CompanySerializer(serializers.ModelSerializer):
    website = FlexibleURLField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Company
        fields = '__all__'

class VacancySerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    
    class Meta:
        model = Vacancy
        fields = '__all__'

