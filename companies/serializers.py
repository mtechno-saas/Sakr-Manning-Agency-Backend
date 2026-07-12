from rest_framework import serializers
from .models import Company, JobOrder, JobOrderPosition
from core.models import CompanyType, Flag


class CompanySerializer(serializers.ModelSerializer):
    ships = serializers.SerializerMethodField()

    # company_type is exposed as a string (the CompanyType.name) on both
    # request and response. SlugRelatedField handles string↔instance
    # conversion natively, so the previous to_internal_value string→ID
    # shim is no longer needed.
    company_type = serializers.SlugRelatedField(
        slug_field='name',
        queryset=CompanyType.objects.all(),
        required=False,
        allow_null=True,
    )
    # Kept for backwards compatibility — now mirrors company_type.
    company_type_name = serializers.CharField(source='company_type.name', read_only=True)

    # company_flag still accepts either an integer ID or a string name
    # (handled in to_internal_value below) and serialises back to the ID.
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
        Normalise `company_flag` (accepts either an integer ID or a string name)
        and `website` (auto-prefix https:// if missing) before DRF field
        validation. `company_type` is handled natively by SlugRelatedField.
        """
        if 'company_flag' in data:
            val = data['company_flag']
            if isinstance(val, str) and not val.isdigit() and val.strip():
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



    def get_open_positions(self, obj):
        # Calculate remaining open slots by subtracting filled contracts from quantity
        from .models import JobOrderPosition
        from django.db.models import Count, Q
        
        positions = JobOrderPosition.objects.filter(
            job_order__company=obj,
            job_order__status__in=['Open', 'Active', 'Pending', 'In Progress']
        ).annotate(
            filled_slots=Count('contracts', filter=Q(contracts__status__in=['Active', 'Signed']))
        )
        
        total_remaining = 0
        for pos in positions:
            total_remaining += max(0, pos.quantity - pos.filled_slots)
        return total_remaining

    def get_open_position_names(self, obj):
        # Return unique ranks and the total remaining slots for each
        from .models import JobOrderPosition
        from django.db.models import Count, Q
        
        positions = JobOrderPosition.objects.filter(
            job_order__company=obj,
            job_order__status__in=['Open', 'Active', 'Pending', 'In Progress']
        ).select_related('rank').annotate(
            filled_slots=Count('contracts', filter=Q(contracts__status__in=['Active', 'Signed']))
        )
        
        rank_data = {}
        for pos in positions:
            if pos.rank:
                remaining = max(0, pos.quantity - pos.filled_slots)
                if remaining > 0:
                    rank_id = pos.rank.id
                    if rank_id not in rank_data:
                        rank_data[rank_id] = {
                            "id": rank_id,
                            "name": pos.rank.name,
                            "count": remaining
                        }
                    else:
                        rank_data[rank_id]["count"] += remaining
        return list(rank_data.values())

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
    status = serializers.CharField(source='job_order.status', read_only=True)
    company_name = serializers.CharField(source='job_order.company.company_name', read_only=True)
    ship_name = serializers.CharField(source='job_order.ship.ship_name', read_only=True, default=None)
    
    filled_slots = serializers.SerializerMethodField()
    remaining_slots = serializers.SerializerMethodField()
    assigned_to = serializers.SerializerMethodField()
    
    class Meta:
        model = JobOrderPosition
        fields = '__all__'

    def get_filled_slots(self, obj):
        if hasattr(obj, 'filled_slots'):
            return getattr(obj, 'filled_slots')
        return len([c for c in obj.contracts.all() if c.status in ['Active', 'Signed']])

    def get_remaining_slots(self, obj):
        filled = self.get_filled_slots(obj)
        return max(0, obj.quantity - filled)

    def get_assigned_to(self, obj):
        contracts = [c for c in obj.contracts.all() if c.status in ['Active', 'Signed']]
        return [f"{c.user.first_name} {c.user.middle_name}".strip() for c in contracts if c.user]

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

