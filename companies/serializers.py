from rest_framework import serializers
from .models import Company, JobOrder, JobOrderPosition
from core.models import CompanyType, Flag


def _filled(position):
    """
    Mirror of JobOrderPositionSerializer.get_filled_slots().

    Counts contracts whose status is Active or Signed. Used by the
    vacancy rollups on JobOrderSerializer to avoid double-querying
    through the nested serializer just to read filled_slots.
    """
    return sum(
        1 for c in position.contracts.all()
        if c.status in ("Active", "Signed")
    )


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

    # company_flag is now also exposed as a string (the Flag.name) on both
    # request and response. SlugRelatedField handles the string<->instance
    # conversion; to_internal_value below still auto-creates a Flag if a
    # name is passed that doesn't exist yet.
    company_flag = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Flag.objects.all(),
        required=False,
        allow_null=True,
    )
    # Read-only int id (useful for React keys, joins, etc.)
    company_flag_id = serializers.IntegerField(source='company_flag.id', read_only=True)
    # Kept for backwards compatibility -- now mirrors company_flag.
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

    # Override the model field's URLField with a plain CharField so
    # bare domains ("www.example.com") are accepted without forcing a
    # scheme. The frontend / user owns the protocol; we just store
    # the string. The CharField keeps the same max_length as the
    # underlying column so DB writes still pass.
    website = serializers.CharField(
        max_length=200, required=False, allow_null=True, allow_blank=True,
    )

    def to_internal_value(self, data):
        """
        Normalise `company_flag` (accepts an integer ID, a string name, or
        auto-creates a new Flag if the name is unknown) before DRF
        field validation.

        Note
        ----
        `website` is stored as the user submitted it — no auto-prefix,
        no protocol stripping. This keeps the form round-trip clean:
        type "www.example.com", save, re-edit, see "www.example.com".
        If you want a protocol guaranteed on the value, do it on
        the frontend or in a separate normaliser.
        `company_type` is handled natively by SlugRelatedField.
        """
        if 'company_flag' in data:
            val = data['company_flag']
            # If a numeric string is sent (e.g. "3"), coerce to int so the
            # SlugRelatedField treats it as a primary key lookup and returns
            # the matching Flag's name.
            if isinstance(val, str) and val.isdigit():
                if hasattr(data, 'copy'):
                    data = data.copy()
                else:
                    data = dict(data)
                data['company_flag'] = int(val)
            # If a non-numeric string is sent, auto-create the Flag if it
            # doesn't already exist (preserves the legacy auto-create
            # behaviour from before the SlugRelatedField migration).
            elif isinstance(val, str) and val.strip():
                flag, _ = Flag.objects.get_or_create(name=val.strip())
                if hasattr(data, 'copy'):
                    data = data.copy()
                else:
                    data = dict(data)
                data['company_flag'] = flag.name

        return super().to_internal_value(data)



    def get_open_positions(self, obj):
        # Calculate remaining open slots by subtracting filled contracts from quantity
        from .models import JobOrderPosition
        from django.db.models import Count, Q
        
        positions = JobOrderPosition.objects.filter(
            job_order__company=obj,
            job_order__status__in=['Open']
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
            job_order__status__in=['Open']
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
        """
        One entry per Active/Signed contract under this position,
        each entry being the assigned crew member's full name.

        We use the canonical ``Users.full_name`` property rather than
        hand-rolling ``f"{first} {middle}"`` because Users.full_name
        is the single source of truth for the display name and
        already handles blank / missing pieces. If for any reason
        full_name is empty (legacy row with no first/middle), we
        fall back to email so the UI still has something to show.
        """
        rows = []
        for c in obj.contracts.all():
            if c.status not in ('Active', 'Signed'):
                continue
            user = getattr(c, "user", None)
            if not user:
                continue
            name = (getattr(user, "full_name", "") or "").strip()
            if not name:
                name = getattr(user, "email", None) or f"user#{user.id}"
            rows.append(name)
        return rows

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

    # Vacancy rollups across the nested positions. Computed via
    # SerializerMethodFields so they stay in sync with whatever
    # positions are currently nested under this job order.
    #
    #   total_open_vacancies       — count of positions still
    #                                recruiting (remaining_slots > 0)
    #   total_closed_vacancies     — count of positions no longer
    #                                recruiting (remaining_slots == 0)
    #   total_fully_filled_vacancies — count of positions where
    #                                every requested slot has been
    #                                filled (filled_slots == quantity
    #                                and quantity > 0)
    total_open_vacancies = serializers.SerializerMethodField()
    total_closed_vacancies = serializers.SerializerMethodField()
    total_fully_filled_vacancies = serializers.SerializerMethodField()

    # Flat list of every crew member that has been assigned to a
    # position under this job order, regardless of contract status.
    # Each row carries the user's id / name / email and the ship
    # recorded on the contract (i.e. the vessel they were placed on),
    # plus the rank, contract status and sign-on/off dates for context.
    #
    # Viewset prefetches positions__contracts__user, __ship and
    # __job_position__rank so this stays a constant number of queries
    # regardless of how many crew are assigned.
    assigned_crew = serializers.SerializerMethodField()

    class Meta:
        model = JobOrder
        fields = '__all__'

    def _positions(self, obj):
        # `positions` is the reverse-relation from JobOrderPosition.
        # Use `.all()` to avoid double-querying through the nested
        # serializer (which prefetches via the `positions` field on
        # the serializer's Meta.source).
        return obj.positions.all()

    def get_total_open_vacancies(self, obj):
        return sum(
            1 for p in self._positions(obj) if (p.quantity - _filled(p)) > 0
        )

    def get_total_closed_vacancies(self, obj):
        # remaining_slots <= 0 covers both the "all filled" case
        # and the broken-data case (quantity=0, filled>0 → negative
        # remaining). Either way the position is no longer
        # recruiting.
        return sum(
            1 for p in self._positions(obj) if (p.quantity - _filled(p)) <= 0
        )

    def get_total_fully_filled_vacancies(self, obj):
        n = 0
        for p in self._positions(obj):
            if p.quantity > 0 and _filled(p) >= p.quantity:
                n += 1
        return n

    # ----------------------------------------------------------------
    # assigned_crew
    # ----------------------------------------------------------------

    @staticmethod
    def _user_name(user):
        """Best-effort human label for a Users row."""
        if not user:
            return None
        full = getattr(user, "full_name", "") or ""
        if not full:
            first = getattr(user, "first_name", "") or ""
            middle = getattr(user, "middle_name", "") or ""
            full = f"{first} {middle}".strip()
        if full:
            return full
        return (
            getattr(user, "email", None)
            or getattr(user, "username", None)
            or f"user#{getattr(user, 'id', '?')}"
        )

    def get_assigned_crew(self, obj):
        """
        One row per Contract that points to a position under this job
        order. The list is flat (not nested under positions) so the
        frontend can render it directly as a single table.

        Returns [] when nothing is assigned yet (the common case for a
        brand-new "Open" job order).
        """
        # Pulled off `obj` once so each crew row can re-use it.
        request_number = getattr(obj, "reference_number", None)
        target_joining_date = (
            obj.target_joining_date.isoformat()
            if getattr(obj, "target_joining_date", None)
            else None
        )

        rows = []
        for pos in self._positions(obj):
            for c in pos.contracts.all():
                user = getattr(c, "user", None)
                ship = getattr(c, "ship", None)
                # ``salary`` is a Decimal on the contract; we want it
                # to serialize as a plain string so the API doesn't
                # surprise clients with float-vs-decimal quirks.
                salary = getattr(c, "salary", None)
                salary_str = str(salary) if salary is not None else None
                currency = getattr(c, "currency", None) or None
                rows.append({
                    "contract_id": c.id,
                    "user_id": getattr(user, "id", None),
                    "user_name": self._user_name(user),
                    "user_email": getattr(user, "email", None),
                    "ship_id": getattr(ship, "id", None),
                    "ship_name": getattr(ship, "ship_name", None),
                    "rank": (
                        getattr(getattr(pos, "rank", None), "name", None)
                        or getattr(c, "rank", None)
                        and getattr(c.rank, "name", None)
                    ),
                    "contract_status": c.status,
                    "salary": salary_str,
                    "currency": currency,
                    "availability_date": (
                        user.available_date.isoformat()
                        if user is not None
                        and getattr(user, "available_date", None)
                        else None
                    ),
                    "sign_on_date": (
                        c.sign_on_date.isoformat()
                        if getattr(c, "sign_on_date", None)
                        else None
                    ),
                    "sign_off_date": (
                        c.sign_off_date.isoformat()
                        if getattr(c, "sign_off_date", None)
                        else None
                    ),
                    # Job-order context, repeated on every crew row so
                    # the flat list is self-describing.
                    "request_number": request_number,
                    "target_join_date": target_joining_date,
                })
        return rows

