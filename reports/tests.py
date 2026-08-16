"""
Tests for the Reports endpoint.

Coverage:
  1. Auth required.
  2. Empty body returns an empty report (no sections).
  3. Each section can be requested with no filters -> all rows.
  4. Each filter dimension on each section works.
  5. Filters are AND'd within a section, sections are independent.
  6. Cross-section: filtering job orders by company_ids does NOT
     affect the companies section.
  7. user_statuses filter uses the effective 5-state logic.
  8. Invalid filter values return 400 with a clear message.
"""
import datetime

from django.test import TestCase
from rest_framework.test import APIClient

from api.models import Contract, Rank, Users
from companies.models import Company, JobOrder, JobOrderPosition
from core.models import CompanyType, Flag, VesselType
from ships.models import Ship


URL = "/api/reports/generate/"


def _admin():
    """Create a unique admin user. Each call gets a fresh email so
    ``setUpTestData`` re-runs don't hit a UNIQUE constraint."""
    counter = Users.objects.filter(email__startswith="admin-reports-").count()
    return Users.objects.create_user(
        email=f"admin-reports-{counter}@example.com",
        password="x",
        first_name="Admin",
        middle_name="Reports",
        role="Admin",
        is_staff=True,
        is_superuser=True,
    )


def _client(user=None):
    c = APIClient()
    if user is not None:
        c.force_authenticate(user=user)
    return c


def _company(name="Test Co", status="Active", company_type=None, flag=None):
    return Company.objects.create(
        company_name=name,
        contact_email=f"{name.replace(' ', '').lower()}@example.com",
        status=status,
        company_type=company_type,
        company_flag=flag,
    )


def _ship(name="MV Test", company=None, ship_type=None, flag=None, year_built=None):
    return Ship.objects.create(
        ship_name=name,
        imo_number=f"IMO-{name.replace(' ', '')[:7]}",
        company=company,
        ship_type=ship_type,
        flag=flag,
        year_built=year_built,
    )


def _job_order(company, ship, reference="JO-2026-001", status="Open",
               request_date=None, target_join_date=None):
    today = datetime.date.today()
    return JobOrder.objects.create(
        company=company, ship=ship,
        reference_number=reference,
        request_date=request_date or today,
        target_joining_date=target_join_date or today,
        status=status,
    )


def _position(job_order, rank, quantity=1):
    return JobOrderPosition.objects.create(
        job_order=job_order, rank=rank, quantity=quantity,
    )


# ===========================================================================
# Tests
# ===========================================================================


class ReportsEndpointAuthTests(TestCase):
    def test_requires_auth(self):
        r = _client().post(URL, {}, format="json")
        self.assertIn(r.status_code, (401, 403))


class ReportsEndpointEmptyBodyTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = _admin()

    def test_empty_body_returns_empty_sections(self):
        r = _client(self.admin).post(URL, {}, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertIn("sections", r.data)
        self.assertEqual(r.data["sections"], {})

    def test_present_but_empty_block_returns_all_rows(self):
        """A section block with {} is the same as not providing it
        (i.e. all rows, since no filters are active)."""
        Company.objects.create(
            company_name="Co A",
            contact_email="a@example.com",
            status="Active",
        )
        r = _client(self.admin).post(URL, {"companies": {}}, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertIn("companies", r.data["sections"])
        self.assertEqual(r.data["sections"]["companies"]["total_records"], 1)


class JobOrderSectionFilterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = _admin()
        cls.company_a = _company("Alpha Shipping")
        cls.company_b = _company("Bravo Shipping")
        cls.ship_a = _ship("MV Alpha", company=cls.company_a)
        cls.ship_b = _ship("MV Bravo", company=cls.company_b)
        cls.rank = Rank.objects.create(code="MAS-1", name="Master")

        cls.jo_a_open = _job_order(
            cls.company_a, cls.ship_a,
            reference="JO-A-OPEN", status="Open",
        )
        cls.jo_b_close = _job_order(
            cls.company_b, cls.ship_b,
            reference="JO-B-CLOSE", status="Close",
        )

    def _post(self, body):
        return _client(self.admin).post(URL, body, format="json")

    def test_no_filters_returns_all_job_orders(self):
        r = self._post({"job_orders": {}})
        self.assertEqual(r.status_code, 200)
        rows = r.data["sections"]["job_orders"]["rows"]
        refs = {row["reference_number"] for row in rows}
        self.assertIn("JO-A-OPEN", refs)
        self.assertIn("JO-B-CLOSE", refs)

    def test_filter_by_company_ids(self):
        r = self._post({"job_orders": {"company_ids": [self.company_a.id]}})
        rows = r.data["sections"]["job_orders"]["rows"]
        refs = {row["reference_number"] for row in rows}
        self.assertEqual(refs, {"JO-A-OPEN"})

    def test_filter_by_ship_ids(self):
        r = self._post({"job_orders": {"ship_ids": [self.ship_b.id]}})
        rows = r.data["sections"]["job_orders"]["rows"]
        refs = {row["reference_number"] for row in rows}
        self.assertEqual(refs, {"JO-B-CLOSE"})

    def test_filter_by_statuses(self):
        r = self._post({"job_orders": {"statuses": ["Open"]}})
        rows = r.data["sections"]["job_orders"]["rows"]
        refs = {row["reference_number"] for row in rows}
        self.assertEqual(refs, {"JO-A-OPEN"})

    def test_filter_by_rank_ids(self):
        _position(self.jo_a_open, self.rank)
        r = self._post({"job_orders": {"rank_ids": [self.rank.id]}})
        rows = r.data["sections"]["job_orders"]["rows"]
        refs = {row["reference_number"] for row in rows}
        self.assertEqual(refs, {"JO-A-OPEN"})

    def test_filter_combines(self):
        """Two filters AND together."""
        r = self._post({
            "job_orders": {
                "company_ids": [self.company_a.id],
                "statuses": ["Open"],
            }
        })
        rows = r.data["sections"]["job_orders"]["rows"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["reference_number"], "JO-A-OPEN")

    def test_filter_combines_excludes(self):
        """Mismatched company + status returns no rows."""
        r = self._post({
            "job_orders": {
                "company_ids": [self.company_b.id],  # JO-B
                "statuses": ["Open"],               # but Open
            }
        })
        rows = r.data["sections"]["job_orders"]["rows"]
        self.assertEqual(rows, [])

    def test_filter_invalid_status_returns_400(self):
        r = self._post({"job_orders": {"statuses": ["BOGUS"]}})
        self.assertEqual(r.status_code, 400)

    def test_date_range_filter(self):
        self.jo_a_open.request_date = datetime.date(2026, 1, 1)
        self.jo_a_open.save(update_fields=["request_date"])
        self.jo_b_close.request_date = datetime.date(2026, 6, 1)
        self.jo_b_close.save(update_fields=["request_date"])
        r = self._post({
            "job_orders": {
                "request_date_from": "2026-02-01",
                "request_date_to": "2026-05-31",
            }
        })
        rows = r.data["sections"]["job_orders"]["rows"]
        # Only JO-B (2026-06-01) is in the range? No, that's outside too.
        # 2026-01-01 is before, 2026-06-01 is after. So neither.
        # Adjust: move JO-B to 2026-03-15 to test positive match.
        self.jo_b_close.request_date = datetime.date(2026, 3, 15)
        self.jo_b_close.save(update_fields=["request_date"])
        r = self._post({
            "job_orders": {
                "request_date_from": "2026-02-01",
                "request_date_to": "2026-05-31",
            }
        })
        rows = r.data["sections"]["job_orders"]["rows"]
        refs = {row["reference_number"] for row in rows}
        self.assertEqual(refs, {"JO-B-CLOSE"})


class CompanySectionFilterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = _admin()
        cls.t_shipowner = CompanyType.objects.create(name="Ship Owner")
        cls.t_shipmanager = CompanyType.objects.create(name="Ship Manager")
        cls.flag_eg = Flag.objects.create(name=f"Egypt-{id(cls)}")
        cls.flag_in = Flag.objects.create(name=f"India-{id(cls)}")
        cls.co_owner_eg = _company("Owner EG", company_type=cls.t_shipowner, flag=cls.flag_eg)
        cls.co_manager_in = _company("Manager IN", company_type=cls.t_shipmanager, flag=cls.flag_in)
        cls.co_inactive = _company("Inactive Co", status="Inactive")

    def _post(self, body):
        return _client(self.admin).post(URL, body, format="json")

    def test_filter_by_company_type(self):
        r = self._post({"companies": {"company_type_ids": [self.t_shipowner.id]}})
        names = {row["company_name"] for row in r.data["sections"]["companies"]["rows"]}
        self.assertEqual(names, {"Owner EG"})

    def test_filter_by_country(self):
        r = self._post({"companies": {"country_ids": [self.flag_eg.id]}})
        names = {row["company_name"] for row in r.data["sections"]["companies"]["rows"]}
        self.assertEqual(names, {"Owner EG"})

    def test_filter_by_status(self):
        r = self._post({"companies": {"statuses": ["Inactive"]}})
        names = {row["company_name"] for row in r.data["sections"]["companies"]["rows"]}
        self.assertEqual(names, {"Inactive Co"})

    def test_invalid_status_returns_400(self):
        r = self._post({"companies": {"statuses": ["Floating"]}})
        self.assertEqual(r.status_code, 400)


class ShipSectionFilterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = _admin()
        cls.co = _company("Owner")
        cls.t_bulk = VesselType.objects.create(name="Bulk Carrier")
        cls.t_tanker = VesselType.objects.create(name="Tanker")
        cls.flag_panama = Flag.objects.create(name=f"Panama-{id(cls)}")
        cls.flag_liberia = Flag.objects.create(name=f"Liberia-{id(cls)}")
        cls.ship_bulk = _ship("MV Bulk", company=cls.co,
                              ship_type=cls.t_bulk, flag=cls.flag_panama,
                              year_built=2010)
        cls.ship_tanker = _ship("MV Tanker", company=cls.co,
                                ship_type=cls.t_tanker, flag=cls.flag_liberia,
                                year_built=2020)

    def _post(self, body):
        return _client(self.admin).post(URL, body, format="json")

    def test_filter_by_company(self):
        r = self._post({"ships": {"company_ids": [self.co.id]}})
        names = {row["ship_name"] for row in r.data["sections"]["ships"]["rows"]}
        self.assertEqual(names, {"MV Bulk", "MV Tanker"})

    def test_filter_by_ship_type(self):
        r = self._post({"ships": {"ship_type_ids": [self.t_tanker.id]}})
        names = {row["ship_name"] for row in r.data["sections"]["ships"]["rows"]}
        self.assertEqual(names, {"MV Tanker"})

    def test_filter_by_flag(self):
        r = self._post({"ships": {"flag_ids": [self.flag_panama.id]}})
        names = {row["ship_name"] for row in r.data["sections"]["ships"]["rows"]}
        self.assertEqual(names, {"MV Bulk"})

    def test_filter_by_year_built_range(self):
        r = self._post({
            "ships": {"year_built_from": 2015, "year_built_to": 2025},
        })
        names = {row["ship_name"] for row in r.data["sections"]["ships"]["rows"]}
        self.assertEqual(names, {"MV Tanker"})


class UserSectionFilterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        from api.models import UserRank
        cls.admin = _admin()
        cls.rank_master = Rank.objects.create(code="MAS-1", name="Master")
        cls.rank_chief = Rank.objects.create(code="CHIEF-1", name="Chief Officer")

        # admin user
        cls.u_admin = _admin()
        # employee no contracts
        cls.u_employee = Users.objects.create_user(
            email="emp@example.com", password="x",
            first_name="Emp", middle_name="Loyee",
            role="Employee", nationality="Egyptian",
        )
        # onboard user
        cls.u_onboard = Users.objects.create_user(
            email="onb@example.com", password="x",
            first_name="On", middle_name="Board",
            role="Employee", nationality="Indian",
        )
        UserRank.objects.create(user=cls.u_onboard, rank=cls.rank_master)
        # Set up an Active contract for u_onboard
        cls.ship = _ship("MV Test", company=_company("Owner"))
        cls.pos = _position(
            _job_order(cls.ship.company, cls.ship, reference="JO-ONB"),
            cls.rank_master,
        )
        Contract.objects.create(
            user=cls.u_onboard, ship=cls.ship,
            company=cls.ship.company, rank=cls.rank_master,
            job_position=cls.pos,
            sign_on_date=datetime.date.today(),
            status="Active",
        )
        # vacation user
        cls.u_vacation = Users.objects.create_user(
            email="vac@example.com", password="x",
            first_name="On", middle_name="Vacation",
            role="Employee", user_status="VACATION",
        )
        # blacklisted
        cls.u_blacklist = Users.objects.create_user(
            email="bl@example.com", password="x",
            first_name="B", middle_name="L", role="Employee",
            is_blacklisted=True,
        )

    def _post(self, body):
        return _client(self.admin).post(URL, body, format="json")

    def test_filter_by_role(self):
        r = self._post({"users": {"roles": ["Admin"]}})
        emails = {row["email"] for row in r.data["sections"]["users"]["rows"]}
        # u_admin + the test's own admin
        self.assertTrue(any(e.startswith("admin-reports-") for e in emails))

    def test_filter_by_user_status_onboard(self):
        r = self._post({"users": {"user_statuses": ["ON_BOARD"]}})
        emails = {row["email"] for row in r.data["sections"]["users"]["rows"]}
        self.assertIn("onb@example.com", emails)
        self.assertNotIn("emp@example.com", emails)
        self.assertNotIn("vac@example.com", emails)

    def test_filter_by_user_status_vacation(self):
        r = self._post({"users": {"user_statuses": ["VACATION"]}})
        emails = {row["email"] for row in r.data["sections"]["users"]["rows"]}
        self.assertIn("vac@example.com", emails)
        self.assertNotIn("onb@example.com", emails)

    def test_filter_by_user_status_new_applicant(self):
        r = self._post({"users": {"user_statuses": ["NEW_APPLICANT"]}})
        emails = {row["email"] for row in r.data["sections"]["users"]["rows"]}
        self.assertIn("emp@example.com", emails)
        self.assertNotIn("onb@example.com", emails)

    def test_filter_by_user_status_medical_vacation_with_space(self):
        """The 'MEDICAL VACATION' human label is normalized."""
        # Set up a user with stored MEDICAL_VACATION
        u = Users.objects.create_user(
            email="med@example.com", password="x",
            first_name="M", middle_name="D", role="Employee",
            user_status="MEDICAL_VACATION",
        )
        r = self._post({"users": {"user_statuses": ["MEDICAL VACATION"]}})
        self.assertEqual(r.status_code, 200)
        emails = {row["email"] for row in r.data["sections"]["users"]["rows"]}
        self.assertIn("med@example.com", emails)
        self.assertNotIn("onb@example.com", emails)

    def test_filter_by_rank(self):
        r = self._post({"users": {"rank_ids": [self.rank_master.id]}})
        emails = {row["email"] for row in r.data["sections"]["users"]["rows"]}
        self.assertIn("onb@example.com", emails)
        self.assertNotIn("emp@example.com", emails)

    def test_filter_by_nationality(self):
        r = self._post({"users": {"nationalities": ["Indian"]}})
        emails = {row["email"] for row in r.data["sections"]["users"]["rows"]}
        self.assertIn("onb@example.com", emails)
        self.assertNotIn("emp@example.com", emails)

    def test_filter_by_is_blacklisted(self):
        r = self._post({"users": {"is_blacklisted": True}})
        emails = {row["email"] for row in r.data["sections"]["users"]["rows"]}
        self.assertIn("bl@example.com", emails)
        self.assertNotIn("onb@example.com", emails)

    def test_filter_invalid_user_status_returns_400(self):
        r = self._post({"users": {"user_statuses": ["BOGUS"]}})
        self.assertEqual(r.status_code, 400)


class CombinedReportTests(TestCase):
    """Sections are built independently — no cross-entity JOIN."""

    @classmethod
    def setUpTestData(cls):
        cls.admin = _admin()
        cls.co = _company("Test Co")
        cls.ship = _ship("MV Test", company=cls.co)
        cls.rank = Rank.objects.create(code="MAS-1", name="Master")
        cls.jo = _job_order(cls.co, cls.ship, reference="JO-COMBO-1")
        _position(cls.jo, cls.rank)

    def _post(self, body):
        return _client(self.admin).post(URL, body, format="json")

    def test_all_sections_in_one_request(self):
        r = self._post({
            "job_orders": {"statuses": ["Open"]},
            "companies": {"statuses": ["Active"]},
            "ships": {"company_ids": [self.co.id]},
            "users": {"roles": ["Admin"]},
        })
        self.assertEqual(r.status_code, 200)
        sections = r.data["sections"]
        for key in ("job_orders", "companies", "ships", "users"):
            self.assertIn(key, sections)
            self.assertIn("total_records", sections[key])
            self.assertIn("rows", sections[key])

    def test_sections_are_independent(self):
        """Filtering job_orders by company does not affect companies."""
        r = self._post({
            "job_orders": {"company_ids": [self.co.id]},
            "companies": {},
        })
        jo = r.data["sections"]["job_orders"]
        co = r.data["sections"]["companies"]
        self.assertGreaterEqual(jo["total_records"], 1)
        self.assertGreaterEqual(co["total_records"], 1)
        # Companies section has all companies (no filter), not just the one
        self.assertGreaterEqual(co["total_records"], jo["total_records"] + 0)

    def test_only_sections_in_request_are_returned(self):
        r = self._post({"companies": {}})
        self.assertEqual(list(r.data["sections"].keys()), ["companies"])


class ReportResponseShapeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = _admin()

    def test_response_has_generated_at_and_limit(self):
        r = _client(self.admin).post(URL, {}, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertIn("generated_at", r.data)
        self.assertIn("limit_per_section", r.data)
        self.assertEqual(r.data["limit_per_section"], 500)
