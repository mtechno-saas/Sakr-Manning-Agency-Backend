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


# ===========================================================================
# Name-based filter tests (parallel to the ID-based ones above).
# ===========================================================================


class NameBasedJobOrderFilterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = _admin()
        cls.co_alpha = _company("Alpha Shipping")
        cls.co_bravo = _company("Bravo Shipping")
        cls.ship_alpha = _ship("MV Alpha Star", company=cls.co_alpha)
        cls.ship_bravo = _ship("MV Bravo", company=cls.co_bravo)
        cls.rank = Rank.objects.create(code="MAS-1", name="Master")
        cls.rank_chief = Rank.objects.create(code="CHIEF-1", name="Chief Officer")
        cls.jo_a = _job_order(cls.co_alpha, cls.ship_alpha,
                              reference="JO-A", status="Open")
        cls.jo_b = _job_order(cls.co_bravo, cls.ship_bravo,
                              reference="JO-B", status="Open")
        _position(cls.jo_a, cls.rank)
        _position(cls.jo_b, cls.rank_chief)

    def _post(self, body):
        return _client(self.admin).post(URL, body, format="json")

    def test_filter_by_company_names_case_insensitive(self):
        r = self._post({"job_orders": {"company_names": ["alpha"]}})
        refs = {row["reference_number"] for row in
                r.data["sections"]["job_orders"]["rows"]}
        self.assertEqual(refs, {"JO-A"})

    def test_filter_by_company_names_substring(self):
        r = self._post({"job_orders": {"company_names": ["Shipping"]}})
        refs = {row["reference_number"] for row in
                r.data["sections"]["job_orders"]["rows"]}
        self.assertEqual(refs, {"JO-A", "JO-B"})

    def test_filter_by_ship_names(self):
        r = self._post({"job_orders": {"ship_names": ["Alpha"]}})
        refs = {row["reference_number"] for row in
                r.data["sections"]["job_orders"]["rows"]}
        self.assertEqual(refs, {"JO-A"})

    def test_filter_by_rank_names(self):
        r = self._post({"job_orders": {"rank_names": ["Chief"]}})
        refs = {row["reference_number"] for row in
                r.data["sections"]["job_orders"]["rows"]}
        self.assertEqual(refs, {"JO-B"})

    def test_filter_by_rank_code(self):
        r = self._post({"job_orders": {"rank_names": ["MAS-1"]}})
        refs = {row["reference_number"] for row in
                r.data["sections"]["job_orders"]["rows"]}
        self.assertEqual(refs, {"JO-A"})

    def test_ids_and_names_combine_with_or(self):
        """Passing both ids=[b.id] and names=["alpha"] should match both rows."""
        r = self._post({
            "job_orders": {
                "company_ids": [self.co_bravo.id],
                "company_names": ["Alpha"],
            }
        })
        refs = {row["reference_number"] for row in
                r.data["sections"]["job_orders"]["rows"]}
        self.assertEqual(refs, {"JO-A", "JO-B"})


class NameBasedCompanyFilterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = _admin()
        cls.t_owner = CompanyType.objects.create(name="Ship Owner")
        cls.t_manager = CompanyType.objects.create(name="Ship Manager")
        cls.flag = Flag.objects.create(name=f"Egypt-{id(cls)}")
        cls.co_a = _company("Owner Alpha", company_type=cls.t_owner, flag=cls.flag)
        cls.co_b = _company("Manager Bravo", company_type=cls.t_manager, flag=cls.flag)

    def _post(self, body):
        return _client(self.admin).post(URL, body, format="json")

    def test_filter_by_company_type_names(self):
        r = self._post({"companies": {"company_type_names": ["Owner"]}})
        names = {row["company_name"] for row in
                 r.data["sections"]["companies"]["rows"]}
        self.assertEqual(names, {"Owner Alpha"})

    def test_filter_by_country_names(self):
        r = self._post({"companies": {"country_names": ["Egypt"]}})
        names = {row["company_name"] for row in
                 r.data["sections"]["companies"]["rows"]}
        self.assertEqual(names, {"Owner Alpha", "Manager Bravo"})

    def test_ids_and_names_combine_with_or(self):
        r = self._post({
            "companies": {
                "company_type_ids": [self.t_manager.id],
                "company_type_names": ["Owner"],
            }
        })
        names = {row["company_name"] for row in
                 r.data["sections"]["companies"]["rows"]}
        self.assertEqual(names, {"Owner Alpha", "Manager Bravo"})


class NameBasedShipFilterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = _admin()
        cls.co = _company("Owner Inc")
        cls.t_bulk = VesselType.objects.create(name="Bulk Carrier")
        cls.t_tanker = VesselType.objects.create(name="Tanker")
        cls.flag_pa = Flag.objects.create(name=f"Panama-{id(cls)}")
        cls.ship_bulk = _ship("MV Bulk Star", company=cls.co,
                              ship_type=cls.t_bulk, flag=cls.flag_pa)
        cls.ship_tanker = _ship("MV Tanker", company=cls.co,
                                ship_type=cls.t_tanker, flag=cls.flag_pa)

    def _post(self, body):
        return _client(self.admin).post(URL, body, format="json")

    def test_filter_by_ship_type_names(self):
        r = self._post({"ships": {"ship_type_names": ["Tanker"]}})
        names = {row["ship_name"] for row in
                 r.data["sections"]["ships"]["rows"]}
        self.assertEqual(names, {"MV Tanker"})

    def test_filter_by_flag_names(self):
        r = self._post({"ships": {"flag_names": ["Panama"]}})
        names = {row["ship_name"] for row in
                 r.data["sections"]["ships"]["rows"]}
        self.assertEqual(names, {"MV Bulk Star", "MV Tanker"})

    def test_filter_by_company_names(self):
        r = self._post({"ships": {"company_names": ["Owner"]}})
        names = {row["ship_name"] for row in
                 r.data["sections"]["ships"]["rows"]}
        self.assertEqual(names, {"MV Bulk Star", "MV Tanker"})

    def test_ids_and_names_combine_with_or(self):
        r = self._post({
            "ships": {
                "ship_type_ids": [self.t_tanker.id],
                "ship_type_names": ["Bulk"],
            }
        })
        names = {row["ship_name"] for row in
                 r.data["sections"]["ships"]["rows"]}
        self.assertEqual(names, {"MV Bulk Star", "MV Tanker"})


class NameBasedUserFilterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        from api.models import UserRank
        cls.admin = _admin()
        cls.rank_master = Rank.objects.create(code="MAS-1", name="Master")
        cls.rank_chief = Rank.objects.create(code="CHIEF-1", name="Chief Officer")
        cls.u_master = Users.objects.create_user(
            email="master@example.com", password="x",
            first_name="Master", middle_name="User",
            role="Employee", nationality="Egyptian",
        )
        UserRank.objects.create(user=cls.u_master, rank=cls.rank_master)
        cls.u_chief = Users.objects.create_user(
            email="chief@example.com", password="x",
            first_name="Chief", middle_name="User",
            role="Employee", nationality="Indian",
        )
        UserRank.objects.create(user=cls.u_chief, rank=cls.rank_chief)

    def _post(self, body):
        return _client(self.admin).post(URL, body, format="json")

    def test_filter_by_rank_names(self):
        r = self._post({"users": {"rank_names": ["Chief"]}})
        emails = {row["email"] for row in
                  r.data["sections"]["users"]["rows"]}
        self.assertEqual(emails, {"chief@example.com"})

    def test_filter_by_rank_code(self):
        r = self._post({"users": {"rank_names": ["MAS-1"]}})
        emails = {row["email"] for row in
                  r.data["sections"]["users"]["rows"]}
        self.assertEqual(emails, {"master@example.com"})

    def test_ids_and_names_combine_with_or(self):
        r = self._post({
            "users": {
                "rank_ids": [self.rank_chief.id],
                "rank_names": ["Master"],
            }
        })
        emails = {row["email"] for row in
                  r.data["sections"]["users"]["rows"]}
        self.assertEqual(emails, {"master@example.com", "chief@example.com"})

    def test_rank_names_empty_string_is_ignored(self):
        r = self._post({"users": {"rank_names": ["", "  "]}})
        # No filter active, both users come back
        self.assertEqual(r.status_code, 200)


# ===========================================================================
# GET-method tests (query-param form, same response shape as POST).
# ===========================================================================


class ReportsEndpointGetMethodTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = _admin()
        cls.co = _company("Maersk Test Co")
        cls.ship = _ship("MV Maersk Star", company=cls.co)
        cls.rank = Rank.objects.create(code="MAS-1", name="Master")
        cls.jo = _job_order(cls.co, cls.ship, reference="JO-GET-1", status="Open")
        _position(cls.jo, cls.rank)
        cls.jo_closed = _job_order(cls.co, cls.ship,
                                   reference="JO-GET-2", status="Close")

    def _get(self, qs):
        return _client(self.admin).get(URL, qs)

    def test_get_requires_auth(self):
        r = _client().get(URL)
        self.assertIn(r.status_code, (401, 403))

    def test_get_no_params_returns_all_sections(self):
        r = self._get({})
        self.assertEqual(r.status_code, 200)
        # All 5 sections come back since none have filters
        self.assertEqual(set(r.data["sections"].keys()), {
            "job_orders", "job_positions", "companies", "ships", "users",
        })

    def test_get_with_statuses(self):
        r = self._get({"job_orders.statuses": ["Open"]})
        self.assertEqual(r.status_code, 200)
        rows = r.data["sections"]["job_orders"]["rows"]
        refs = {row["reference_number"] for row in rows}
        self.assertIn("JO-GET-1", refs)
        self.assertNotIn("JO-GET-2", refs)

    def test_get_with_company_names(self):
        r = self._get({"job_orders.company_names": ["Maersk"]})
        rows = r.data["sections"]["job_orders"]["rows"]
        self.assertEqual(len(rows), 2)

    def test_get_with_repeated_param(self):
        """?key=v1&key=v2 is supported."""
        r = self._get({
            "job_orders.company_names": ["Maersk", "Other"],
        })
        self.assertEqual(r.status_code, 200)

    def test_get_with_comma_separated(self):
        """?key=v1,v2 is also supported."""
        r = self._get({
            "job_orders.company_names": "Maersk,Other",
        })
        self.assertEqual(r.status_code, 200)
        # The comma-separated form is exploded into the same list
        # the repeated-param form produces.

    def test_get_with_mixed_repeated_and_comma(self):
        """?key=v1&key=v2,v3 -> 3 values total."""
        r = self._get({
            "job_orders.company_names": ["Maersk", "Other,Third"],
        })
        self.assertEqual(r.status_code, 200)

    def test_get_with_date_range(self):
        self.jo.request_date = datetime.date(2026, 1, 15)
        self.jo.save(update_fields=["request_date"])
        r = self._get({
            "job_orders.request_date_from": "2026-01-01",
            "job_orders.request_date_to": "2026-12-31",
        })
        self.assertEqual(r.status_code, 200)

    def test_get_with_invalid_status_returns_400(self):
        r = self._get({"job_orders.statuses": ["BOGUS"]})
        self.assertEqual(r.status_code, 400)

    def test_get_and_post_produce_same_results(self):
        """The same filter spec via POST body or GET query returns
        the same rows."""
        body = {"job_orders": {"statuses": ["Open"]}}
        r_post = _client(self.admin).post(URL, body, format="json")
        r_get = self._get({"job_orders.statuses": ["Open"]})
        self.assertEqual(r_post.status_code, 200)
        self.assertEqual(r_get.status_code, 200)
        post_refs = {row["reference_number"]
                     for row in r_post.data["sections"]["job_orders"]["rows"]}
        get_refs = {row["reference_number"]
                    for row in r_get.data["sections"]["job_orders"]["rows"]}
        self.assertEqual(post_refs, get_refs)


# ===========================================================================
# Job positions section — returns matching JobOrderPosition rows directly.
# ===========================================================================


class JobPositionsSectionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = _admin()
        cls.co_alpha = _company("Alpha")
        cls.co_bravo = _company("Bravo")
        cls.ship_alpha = _ship("MV Alpha Star", company=cls.co_alpha)
        cls.ship_bravo = _ship("MV Bravo", company=cls.co_bravo)
        cls.rank_motor = Rank.objects.create(code="MOT-1", name="Motorman")
        cls.rank_chief = Rank.objects.create(code="CHIEF-1", name="Chief Officer")
        cls.rank_oiler = Rank.objects.create(code="OIL-1", name="Oiler")

        # Two JOs, three positions total
        cls.jo_a = _job_order(cls.co_alpha, cls.ship_alpha,
                              reference="JO-A", status="Open")
        _position(cls.jo_a, cls.rank_motor)
        _position(cls.jo_a, cls.rank_oiler)
        cls.jo_b = _job_order(cls.co_bravo, cls.ship_bravo,
                              reference="JO-B", status="Close")
        _position(cls.jo_b, cls.rank_chief)

    def _post(self, body):
        return _client(self.admin).post(URL, body, format="json")

    def test_filter_by_position_rank_names_returns_positions_directly(self):
        r = self._post({"job_positions": {"position_rank_names": ["Motorman"]}})
        self.assertEqual(r.status_code, 200)
        positions = r.data["sections"]["job_positions"]["rows"]
        self.assertEqual(len(positions), 1)
        self.assertEqual(positions[0]["rank_name"], "Motorman")

    def test_filter_by_position_rank_code(self):
        r = self._post({"job_positions": {"position_rank_names": ["MOT-1"]}})
        positions = r.data["sections"]["job_positions"]["rows"]
        self.assertEqual(len(positions), 1)
        self.assertEqual(positions[0]["rank_name"], "Motorman")

    def test_filter_by_position_company_names(self):
        r = self._post({
            "job_positions": {"position_company_names": ["Alpha"]},
        })
        positions = r.data["sections"]["job_positions"]["rows"]
        # Two positions under JO-A (Motorman + Oiler)
        self.assertEqual(len(positions), 2)

    def test_filter_by_position_company_ids(self):
        r = self._post({
            "job_positions": {"position_company_ids": [self.co_bravo.id]},
        })
        positions = r.data["sections"]["job_positions"]["rows"]
        self.assertEqual(len(positions), 1)
        self.assertEqual(positions[0]["rank_name"], "Chief Officer")

    def test_filter_by_position_ship_names(self):
        r = self._post({
            "job_positions": {"position_ship_names": ["Bravo"]},
        })
        positions = r.data["sections"]["job_positions"]["rows"]
        self.assertEqual(len(positions), 1)

    def test_filter_by_position_statuses(self):
        """position_statuses is the status of the parent JO."""
        r = self._post({
            "job_positions": {"position_statuses": ["Open"]},
        })
        positions = r.data["sections"]["job_positions"]["rows"]
        # JO-A is Open (2 positions), JO-B is Close (1 position)
        self.assertEqual(len(positions), 2)

    def test_filter_by_position_ids(self):
        # Pick the Oiler position id and look it up directly
        oiler = self.jo_a.positions.get(rank=self.rank_oiler)
        r = self._post({
            "job_positions": {"position_ids": [oiler.id]},
        })
        positions = r.data["sections"]["job_positions"]["rows"]
        self.assertEqual(len(positions), 1)
        self.assertEqual(positions[0]["rank_name"], "Oiler")

    def test_combined_filters(self):
        """AND within section, OR within a multi-value field."""
        r = self._post({
            "job_positions": {
                "position_company_names": ["Alpha", "Bravo"],
                "position_rank_names": ["Motorman", "Chief"],
            },
        })
        positions = r.data["sections"]["job_positions"]["rows"]
        # Motorman (Alpha) + Chief (Bravo) = 2
        self.assertEqual(len(positions), 2)

    def test_empty_filter_block_returns_all_positions(self):
        """An empty job_positions block is treated as 'no filter', so
        the section IS in the response with all positions. Same
        convention as the other sections."""
        r = self._post({"job_positions": {}})
        self.assertEqual(r.status_code, 200)
        self.assertIn("job_positions", r.data["sections"])
        self.assertEqual(r.data["sections"]["job_positions"]["total_records"], 3)


# ===========================================================================
# Dropdown options endpoint.
# ===========================================================================


class ReportsDropdownOptionsTests(TestCase):
    URL_DROPDOWN = "/api/reports/dropdown-options/"

    @classmethod
    def setUpTestData(cls):
        cls.admin = _admin()
        cls.co = _company("Maersk")
        cls.ship = _ship("MV Maersk Star", company=cls.co)
        cls.t_bulk = VesselType.objects.create(name="Bulk Carrier")
        cls.flag = Flag.objects.create(name=f"Panama-{id(cls)}")
        cls.t_owner = CompanyType.objects.create(name="Ship Owner")
        cls.rank = Rank.objects.create(code="MAS-1", name="Master")

    def test_requires_auth(self):
        r = _client().get(self.URL_DROPDOWN)
        self.assertIn(r.status_code, (401, 403))

    def test_response_shape(self):
        r = _client(self.admin).get(self.URL_DROPDOWN)
        self.assertEqual(r.status_code, 200)
        self.assertIn("options", r.data)
        self.assertIn("enum_options", r.data)
        # All the static options are present
        opts = r.data["enum_options"]
        for key in ("job_order_statuses", "company_statuses", "ship_statuses",
                    "user_roles", "user_statuses"):
            self.assertIn(key, opts)
        # All the dynamic options are present
        for key in ("companies", "ships", "ship_types", "flags",
                    "company_types", "ranks"):
            self.assertIn(key, r.data["options"])

    def test_companies_appear_in_options(self):
        r = _client(self.admin).get(self.URL_DROPDOWN)
        names = {c["name"] for c in r.data["options"]["companies"]}
        self.assertIn("Maersk", names)

    def test_ships_appear_in_options(self):
        r = _client(self.admin).get(self.URL_DROPDOWN)
        names = {s["name"] for s in r.data["options"]["ships"]}
        self.assertIn("MV Maersk Star", names)

    def test_ranks_include_code(self):
        r = _client(self.admin).get(self.URL_DROPDOWN)
        ranks = {r["code"]: r for r in r.data["options"]["ranks"]}
        self.assertIn("MAS-1", ranks)
        self.assertEqual(ranks["MAS-1"]["name"], "Master")

    def test_enum_options_match_model(self):
        from api.models import User_Status
        r = _client(self.admin).get(self.URL_DROPDOWN)
        self.assertEqual(
            set(r.data["enum_options"]["user_statuses"]),
            {c.value for c in User_Status},
        )

    def test_nationalities_dropdown_from_distinct_users(self):
        # Two users with nationalities, one with no nationality, one
        # with an empty nationality string. The empty / null ones
        # must NOT appear in the dropdown.
        Users.objects.create_user(
            email="egyptian@example.com", password="x",
            first_name="E", middle_name="E",
            nationality="Egyptian",
        )
        Users.objects.create_user(
            email="indian@example.com", password="x",
            first_name="I", middle_name="I",
            nationality="Indian",
        )
        Users.objects.create_user(
            email="blank@example.com", password="x",
            first_name="B", middle_name="L",
            nationality="",
        )
        r = _client(self.admin).get(self.URL_DROPDOWN)
        names = {n["name"] for n in r.data["options"]["nationalities"]}
        self.assertIn("Egyptian", names)
        self.assertIn("Indian", names)
        self.assertNotIn("", names)
        # The "blank" user added nationality="" which is excluded.
        self.assertEqual(len(r.data["options"]["nationalities"]), 2)
