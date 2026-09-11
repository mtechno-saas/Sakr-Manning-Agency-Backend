from django.test import TestCase

from api.models import Users
from core.models import Flag, VesselType
from ships.models import Ship
from ships.serializers import ShipSerializer, ShipTypeNameField
from companies.models import Company


class ShipTypeAsStringTests(TestCase):
    """
    Regression: GET /api/ships/<id>/ and the list endpoint must return
    `ship_type` as the string VesselType.name, NOT the integer ID.
    """

    @classmethod
    def setUpTestData(cls):
        cls.vtype, _ = VesselType.objects.get_or_create(name="Container Ship")
        cls.flag, _ = Flag.objects.get_or_create(name="Panama")
        cls.company = Company.objects.create(company_name="Test Shipping Co")
        cls.ship = Ship.objects.create(
            ship_name="MV Test Vessel",
            imo_number="9876543",
            ship_type=cls.vtype,
            flag=cls.flag,
            company=cls.company,
        )

    def test_ship_type_is_string_in_serializer_output(self):
        data = ShipSerializer(self.ship).data
        self.assertIsInstance(data["ship_type"], str)
        self.assertEqual(data["ship_type"], "Container Ship")

    def test_ship_type_name_alias_still_present(self):
        """ship_type_name kept as backwards-compat alias."""
        data = ShipSerializer(self.ship).data
        self.assertEqual(data["ship_type_name"], "Container Ship")

    def test_ship_type_is_null_when_unset(self):
        self.ship.ship_type = None
        self.ship.save()
        data = ShipSerializer(self.ship).data
        self.assertIsNone(data["ship_type"])
        self.assertIsNone(data["ship_type_name"])

    def test_ship_type_accepts_id_on_write(self):
        """Write side still accepts the integer ID."""
        payload = {
            "ship_name": "MV Write ID",
            "imo_number": "1111111",
            "ship_type": self.vtype.id,
            "flag": self.flag.id,
            "company": self.company.id,
        }
        serializer = ShipSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        ship = serializer.save()
        self.assertEqual(ship.ship_type_id, self.vtype.id)
        self.assertEqual(ShipSerializer(ship).data["ship_type"], "Container Ship")

    def test_ship_type_accepts_name_on_write(self):
        """Write side still accepts a string name (auto-creates if new)."""
        payload = {
            "ship_name": "MV Write Name",
            "imo_number": "2222222",
            "ship_type": "Bulk Carrier",
            "flag": "Liberia",
            "company": self.company.id,
        }
        serializer = ShipSerializer(data=payload)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        ship = serializer.save()
        self.assertEqual(ship.ship_type.name, "Bulk Carrier")
        self.assertEqual(ShipSerializer(ship).data["ship_type"], "Bulk Carrier")


class ShipTypeNameFieldUnitTests(TestCase):
    """Direct unit tests for the ShipTypeNameField class."""

    def test_to_representation_returns_name(self):
        vtype = VesselType.objects.create(name="Reefer")
        field = ShipTypeNameField(queryset=VesselType.objects.all())
        self.assertEqual(field.to_representation(vtype), "Reefer")

    def test_to_representation_returns_none_for_none(self):
        field = ShipTypeNameField(queryset=VesselType.objects.all())
        self.assertIsNone(field.to_representation(None))


class ShipListEndpointReturnsStringTests(TestCase):
    """
    End-to-end: the /api/ships/ list endpoint (DRF default router) must
    return `ship_type` as a string for every record.
    """

    @classmethod
    def setUpTestData(cls):
        cls.vtype, _ = VesselType.objects.get_or_create(name="Tanker")
        cls.flag, _ = Flag.objects.get_or_create(name="Marshall Islands")
        cls.company = Company.objects.create(company_name="Tankers Co")
        cls.ship = Ship.objects.create(
            ship_name="MV Tanker One",
            imo_number="5555555",
            ship_type=cls.vtype,
            flag=cls.flag,
            company=cls.company,
        )
        cls.user = Users.objects.create_user(
            email="ship_list_tester@example.com",
            password="x",
            first_name="Tester",
        )

    def setUp(self):
        from rest_framework.test import APIClient
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_endpoint_returns_ship_type_as_string(self):
        from django.urls import reverse
        # The ships router is mounted under /api/ships/ — hit it through the API client.
        resp = self.client.get("/api/ships/")
        self.assertEqual(resp.status_code, 200, resp.content)
        results = resp.json()
        # router response can be a plain list or a paginated dict depending on config
        items = results if isinstance(results, list) else results.get("results", [])
        self.assertGreater(len(items), 0, "list endpoint returned no ships")
        for row in items:
            self.assertIsInstance(
                row["ship_type"],
                str,
                f"ship_type for {row.get('ship_name')} was not a string: {row['ship_type']!r}",
            )

    def test_detail_endpoint_returns_ship_type_as_string(self):
        resp = self.client.get(f"/api/ships/{self.ship.id}/")
        self.assertEqual(resp.status_code, 200, resp.content)
        body = resp.json()
        self.assertIsInstance(body["ship_type"], str)
        self.assertEqual(body["ship_type"], "Tanker")
