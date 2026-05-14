from rest_framework import serializers
from .models import Company, JobOrder, JobOrderPosition

class CompanySerializer(serializers.ModelSerializer):
    ships = serializers.SerializerMethodField()
    company_type_name = serializers.CharField(source='company_type.name', read_only=True)
    company_flag_name = serializers.CharField(source='company_flag.name', read_only=True)

    open_positions = serializers.SerializerMethodField()
    open_position_names = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = '__all__'
        extra_kwargs = {
            'website': {
                'required': False,
                'allow_null': True,
                'allow_blank': True,
            },
        }

    def to_internal_value(self, data):
        """
        Accept `company_type` and `company_flag` as either integer IDs or string names.
        """
        if 'company_type' in data:
            val = data['company_type']
            if isinstance(val, str) and not val.isdigit() and val.strip():
                from core.models import CompanyType
                ct, _ = CompanyType.objects.get_or_create(name=val.strip())
                if hasattr(data, 'copy'):
                    data = data.copy()
                else:
                    data = dict(data)
                data['company_type'] = ct.id

        if 'company_flag' in data:
            val = data['company_flag']
            if isinstance(val, str) and not val.isdigit() and val.strip():
                from core.models import Flag
                flag, _ = Flag.objects.get_or_create(name=val.strip())
                if hasattr(data, 'copy'):
                    data = data.copy()
                else:
                    data = dict(data)
                data['company_flag'] = flag.id

        if 'website' in data and data['website']:
            website_val = data['website']
            if isinstance(website_val, str) and website_val.strip():
                website_val = website_val.strip()
                if not website_val.startswith(('http://', 'https://')):
                    if hasattr(data, 'copy'):
                        data = data.copy()
                    else:
                        data = dict(data)
                    data['website'] = f'https://{website_val}'

        return super().to_internal_value(data)

    def validate_contact_email(self, value):
        if not value:
            return value
        allowed_suffixes = ['.de', '.dk', '.no', '.nl', '.it', '.gr', '.ch', '.co.uk', '.com']
        value_lower = value.lower()
        if not any(value_lower.endswith(suffix) for suffix in allowed_suffixes):
            raise serializers.ValidationError(
                f"Email must end with one of the allowed domains: {', '.join(allowed_suffixes)}"
            )
        return value

    def validate_website(self, value):
        if not value:
            return value
        allowed_suffixes = ['.de', '.dk', '.no', '.nl', '.it', '.gr', '.ch', '.co.uk', '.com']
        
        # Simple check for the domain suffix in the URL
        from urllib.parse import urlparse
        parsed = urlparse(value)
        # If no netloc (e.g. "example.com"), check the path
        domain = parsed.netloc.lower() or parsed.path.lower().split('/')[0]
        
        if not any(domain.endswith(suffix) for suffix in allowed_suffixes):
            raise serializers.ValidationError(
                f"Website must end with one of the allowed domains: {', '.join(allowed_suffixes)}"
            )
        return value

    def get_open_positions(self, obj):
        # Calculate the total number of position entries across all non-cancelled job orders
        from .models import JobOrderPosition
        return JobOrderPosition.objects.filter(
            job_order__company=obj,
            job_order__status__in=['Open', 'Active', 'Pending', 'In Progress']
        ).count()

    def get_open_position_names(self, obj):
        # Return unique ranks required in open/active job orders
        from .models import JobOrderPosition
        positions = JobOrderPosition.objects.filter(
            job_order__company=obj,
            job_order__status__in=['Open', 'Active', 'Pending', 'In Progress']
        ).select_related('rank').distinct()
        
        ranks = []
        seen_rank_ids = set()
        for pos in positions:
            if pos.rank and pos.rank.id not in seen_rank_ids:
                ranks.append({
                    "id": pos.rank.id,
                    "name": pos.rank.name
                })
                seen_rank_ids.add(pos.rank.id)
        return ranks

    def get_ships(self, obj):
        ships = obj.ships.all()
        return [
            {
                "id": ship.id,
                "ship_name": ship.ship_name,
                "imo_number": ship.imo_number,
                "ship_type": ship.ship_type.name if ship.ship_type else None,
                "flag": ship.flag.name if ship.flag else None,
                "status": ship.status,
                "official_no": ship.official_no,
                "call_sign": ship.call_sign,
                "year_built": ship.year_built
            }
            for ship in ships
        ]


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

