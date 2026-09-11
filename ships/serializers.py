# from rest_framework import serializers
# from .models import Ship

# class ShipSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Ship
#         fields = '__all__'


from rest_framework import serializers
from .models import Ship
# Import the Users model
from api.models import Users
from core.models import VesselType

# A simple serializer to represent a user in the crew list
class CrewMemberSerializer(serializers.ModelSerializer):
    # Canonical single-string display name (first + middle). See Users.full_name.
    # The frontend should prefer this over concatenating first_name/middle_name.
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Users
        fields = ['id', 'first_name', 'middle_name', 'full_name', 'email']


class ShipTypeNameField(serializers.PrimaryKeyRelatedField):
    """
    Like a PrimaryKeyRelatedField, but on read it returns the related
    VesselType's `name` string instead of the integer PK.

    Writes still accept either an integer ID or a string name (the serializer's
    `to_internal_value` converts string names to IDs before this field sees them).
    """
    def use_pk_only_optimization(self):
        # Force DRF to fetch the full VesselType row (so we have access to `.name`)
        # instead of the PK-only stub it would normally pass to `to_representation`.
        return False

    def to_representation(self, value):
        # value is a VesselType instance; return its name.
        if value is None:
            return None
        return value.name


class ShipSerializer(serializers.ModelSerializer):
    # Use the CrewMemberSerializer to display nested crew details (read-only)
    crew = CrewMemberSerializer(many=True, read_only=True)

    # Add a write-only field to accept a list of user IDs when creating/updating a ship
    crew_ids = serializers.PrimaryKeyRelatedField(
        queryset=Users.objects.all(),
        many=True,
        write_only=True,
        source='crew', # This links it to the 'crew' model field for writing
        required=False
    )

    # Expose the string names for ForeignKeys so the frontend doesn't just get IDs (like 105)
    # `ship_type` itself returns the VesselType.name string on read (was: the integer ID).
    # `ship_type_name` is kept as an alias for backwards compatibility.
    ship_type = ShipTypeNameField(queryset=VesselType.objects.all(), required=False, allow_null=True)
    ship_type_name = serializers.SerializerMethodField()
    flag_name = serializers.SerializerMethodField()

    def get_ship_type_name(self, obj):
        return obj.ship_type.name if obj.ship_type_id else None

    def get_flag_name(self, obj):
        return obj.flag.name if obj.flag_id else None
    
    # Expose related Job Orders and their positions
    job_orders = serializers.SerializerMethodField()
    jobs_order_count = serializers.SerializerMethodField()

    class Meta:
        model = Ship
        # Add the new fields to the list
        fields = [
            'id', 'ship_name', 'imo_number', 'ship_type', 'ship_type_name', 'flag', 'flag_name',
            'company', 'status', 'crew', 'crew_ids', 'official_no',
            'call_sign', 'mmsi_no', 'port_of_registry', 'gross_tonnage',
            'deadweight', 'year_built', 'builder', 'engine_type',
            'engine_power_kw', 'created_at', 'updated_at', 'job_orders', 'jobs_order_count'
        ]

    def to_internal_value(self, data):
        """
        Accept `ship_type` and `flag` as either integer IDs or string names.
        """
        if 'ship_type' in data:
            val = data['ship_type']
            if isinstance(val, str) and not val.isdigit() and val.strip():
                from core.models import VesselType
                vt, _ = VesselType.objects.get_or_create(name=val.strip())
                if hasattr(data, 'copy'):
                    data = data.copy()
                else:
                    data = dict(data)
                data['ship_type'] = vt.id

        if 'flag' in data:
            val = data['flag']
            if isinstance(val, str) and not val.isdigit() and val.strip():
                from core.models import Flag
                flag, _ = Flag.objects.get_or_create(name=val.strip())
                if hasattr(data, 'copy'):
                    data = data.copy()
                else:
                    data = dict(data)
                data['flag'] = flag.id

        # Handle empty strings for numeric and foreign key fields
        # This prevents validation errors when the frontend sends "" for optional numbers
        fields_to_clean = ['gross_tonnage', 'deadweight', 'year_built', 'engine_power_kw', 'company', 'ship_type', 'flag']
        for field in fields_to_clean:
            if field in data and data[field] == "":
                if hasattr(data, 'copy'):
                    data = data.copy()
                else:
                    data = dict(data)
                data[field] = None

        return super().to_internal_value(data)

    def get_jobs_order_count(self, obj):
        return obj.job_orders.count()

    def get_job_orders(self, obj):
        orders = obj.job_orders.all().prefetch_related('positions__rank')
        result = []
        for order in orders:
            positions = []
            for pos in order.positions.all():
                positions.append({
                    "id": pos.id,
                    "rank": pos.rank.id if pos.rank else None,
                    "rank_name": pos.rank.name if pos.rank else None,
                    "quantity": pos.quantity,
                    "salary_min": pos.salary_min,
                    "salary_max": pos.salary_max,
                    "currency": pos.currency,
                    "contract_duration_months": pos.contract_duration_months,
                    "remarks": pos.remarks
                })
            
            result.append({
                "id": order.id,
                "reference_number": order.reference_number,
                "request_date": order.request_date,
                "target_joining_date": order.target_joining_date,
                "status": order.status,
                "notes": order.notes,
                "positions": positions
            })
        return result
