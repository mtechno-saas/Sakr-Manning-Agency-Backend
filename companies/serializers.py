from rest_framework import serializers
from .models import Company, JobOrder, JobOrderPosition

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'
        extra_kwargs = {
            'website': {
                'required': False,
                'allow_null': True,
                'allow_blank': True,
            },
            'company_flag': {
                'required': False,
                'allow_null': True,
                'allow_blank': True,
            },
        }


class JobOrderPositionSerializer(serializers.ModelSerializer):
    rank_name = serializers.CharField(source='rank.name', read_only=True)
    
    class Meta:
        model = JobOrderPosition
        fields = '__all__'

    def to_internal_value(self, data):
        """
        Accept `rank` as either an integer ID or a string name.
        Examples:
            "rank": 7           → looks up Rank with id=7
            "rank": "2nd. Officer" → looks up Rank with name (case-insensitive)
        """
        if 'rank' in data:
            rank_val = data['rank']
            if isinstance(rank_val, str) and not rank_val.isdigit():
                from api.models import Rank
                rank = Rank.objects.filter(name__iexact=rank_val.strip()).first()
                if not rank:
                    raise serializers.ValidationError({
                        'rank': f'Rank "{rank_val}" not found. Use a valid rank name or ID.'
                    })
                # Replace the string with the resolved ID
                if hasattr(data, 'copy'):
                    data = data.copy()
                else:
                    data = dict(data)
                data['rank'] = rank.id
        return super().to_internal_value(data)


class JobOrderSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    ship_name = serializers.CharField(source='ship.ship_name', read_only=True)
    positions = JobOrderPositionSerializer(many=True, read_only=True)

    class Meta:
        model = JobOrder
        fields = '__all__'

