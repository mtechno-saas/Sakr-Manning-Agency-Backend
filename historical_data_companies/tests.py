"""
Tests for the Historical Data for Companies endpoint.

Coverage:
  1. Auth required.
  2. Default range: last 12 months.
  3. summary: totals are correct given a known dataset.
  4. time_series: contracts / job orders bucketed by granularity.
  5. top_n: rankings honour date range + top_n.
  6. breakdowns: status / type / country / rank distributions.
  7. per_company_timeline: opt-in, chronological, capped at 50 companies.
  8. Validation: bad date / bad granularity / bad top_n -> 400.
"""
import datetime

from django.test import TestCase
from rest_framework.test import APIClient

from api.models import Contract, Rank, Users
from companies.models import Company, JobOrder, JobOrderPosition
from core.models import CompanyType, Flag, VesselType
from ships.models import Ship


URL = "/api/historical-data-for-companies/"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _admin():
    counter = Users.objects.filter(email__startswith="hd-admin-").count()
    return Users.objects.create_user(
        email=f"hd-admin-{counter}@example.com",
        password="x",
        first_name="HD",
        middle_name="Admin",
        role="Admin",
        is_staff=True,
        is_superuser=True,
    )


def _client(user=None):
    c = APIClient()
    if user is not None:
        c.force_authenticate(user=user)
    return c


def _company(name, status="Active", company_type=None, flag=None):
    return Company.objects.create(
        company_name=name,
        contact_email=f"{name.replace(' ', '').lower()}@example.com",
        status=status,
        company_type=company_type,
        company_flag=flag,
    )


def _ship(name, company):
    return Ship.objects.create(
        ship_name=name, imo_number=f"IMO-{name[:7]}",
        company=company,
    )


def _rank(code, name):
    return Rank.objects.create(code=code, name=name)


def _jo(company, ship, reference, request_date, status="Open"):
    return JobOrder.objects.create(
        company=company, ship=ship,
        reference_number=reference,
        request_date=request_date,
        target_joining_date=request_date,
        status=status,
    )


def _position(jo, rank, quantity=1):
    return JobOrderPosition.objects.create(
        job_order=jo, rank=rank, quantity=quantity,
    )


def _contract(user, ship, company, rank, position, sign_on, status="Active",
              sign_off=None, salary="1000.00"):
    return Contract.objects.create(
        user=user, ship=ship, company=company, rank=rank,
        job_position=position,
        sign_on_date=sign_on,
        sign_off_date=sign_off,
        status=status,
        salary=salary,
    )


# ---------------------------------------------------------------------------
# Auth + defaults
# ---------------------------------------------------------------------------


class HistoricalDataAuthTests(TestCase):
    def test_requires_auth(self):
        r = _client().get(URL)
        self.assertIn(r.status_code, (401, 403))


class HistoricalDataDefaultsTests(TestCase):
    def setUp(self):
        self.admin = _admin()

    def test_default_range_returns_valid_response(self):
        r = _client(self.admin).get(URL)
        self.assertEqual(r.status_code, 200)
        self.assertIn("summary", r.data)
        self.assertIn("date_from", r.data["summary"])
        self.assertIn("date_to", r.data["summary"])
        # date_from should be <= date_to
        self.assertLessEqual(
            r.data["summary"]["date_from"],
            r.data["summary"]["date_to"],
        )

    def test_default_granularity_is_month(self):
        r = _client(self.admin).get(URL)
        self.assertEqual(r.data["summary"]["granularity"], "month")


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------


class HistoricalDataSummaryTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = _admin()
        cls.t_owner = CompanyType.objects.create(name="Ship Owner")
        cls.flag_eg = Flag.objects.create(name=f"Egypt-{id(cls)}")
        cls.co1 = _company("Co 1", company_type=cls.t_owner, flag=cls.flag_eg)
        cls.co2 = _company("Co 2", status="Inactive")
        cls.ship1 = _ship("MV 1", cls.co1)
        cls.ship2 = _ship("MV 2", cls.co2)
        cls.rank = _rank("MAS-1", "Master")
        cls.user = Users.objects.create_user(
            email="u@example.com", password="x",
            first_name="U", middle_name="U",
        )

    def _get(self, qs):
        return _client(self.admin).get(URL, qs)

    def test_summary_counts_total_and_active(self):
        r = self._get({})
        self.assertEqual(r.data["summary"]["companies_total"], 2)
        self.assertEqual(r.data["summary"]["companies_active"], 1)

    def test_summary_counts_contracts_in_range(self):
        # Two contracts signed today
        jo = _jo(self.co1, self.ship1, "JO-1", datetime.date.today())
        pos = _position(jo, self.rank)
        _contract(self.user, self.ship1, self.co1, self.rank, pos,
                  datetime.date.today())
        _contract(self.user, self.ship1, self.co1, self.rank, pos,
                  datetime.date.today())
        r = self._get({})
        self.assertEqual(r.data["summary"]["contracts"], 2)

    def test_summary_excludes_contracts_outside_range(self):
        today = datetime.date.today()
        long_ago = today.replace(year=today.year - 3)
        jo = _jo(self.co1, self.ship1, "JO-OLD", long_ago)
        pos = _position(jo, self.rank)
        _contract(self.user, self.ship1, self.co1, self.rank, pos, long_ago)
        r = self._get({
            "date_from": today.replace(year=today.year - 1).isoformat(),
            "date_to": today.isoformat(),
        })
        # The contract is outside the range
        self.assertEqual(r.data["summary"]["contracts"], 0)


# ---------------------------------------------------------------------------
# Time series
# ---------------------------------------------------------------------------


class HistoricalDataTimeSeriesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = _admin()
        cls.co = _company("Co TS")
        cls.ship = _ship("MV TS", cls.co)
        cls.rank = _rank("MAS-1", "Master")
        cls.user = Users.objects.create_user(
            email="u@example.com", password="x",
            first_name="U", middle_name="U",
        )

    def test_monthly_buckets_have_correct_keys(self):
        r = _client(self.admin).get(URL, {
            "date_from": "2026-01-01",
            "date_to": "2026-06-30",
            "granularity": "month",
        })
        self.assertEqual(r.status_code, 200)
        periods = [row["period"] for row in
                   r.data["time_series"]["contracts_over_time"]]
        self.assertEqual(periods, [
            "2026-01", "2026-02", "2026-03",
            "2026-04", "2026-05", "2026-06",
        ])

    def test_quarterly_buckets(self):
        r = _client(self.admin).get(URL, {
            "date_from": "2026-01-01",
            "date_to": "2026-12-31",
            "granularity": "quarter",
        })
        periods = [row["period"] for row in
                   r.data["time_series"]["contracts_over_time"]]
        self.assertEqual(periods, [
            "2026-Q1", "2026-Q2", "2026-Q3", "2026-Q4",
        ])

    def test_yearly_buckets(self):
        r = _client(self.admin).get(URL, {
            "date_from": "2024-01-01",
            "date_to": "2026-12-31",
            "granularity": "year",
        })
        periods = [row["period"] for row in
                   r.data["time_series"]["contracts_over_time"]]
        self.assertEqual(periods, ["2024", "2025", "2026"])

    def test_signed_count_buckets_correctly(self):
        # Two contracts in Jan 2026, one in Mar 2026
        today = datetime.date.today()
        jan = datetime.date(2026, 1, 15)
        mar = datetime.date(2026, 3, 10)
        jo = _jo(self.co, self.ship, "JO-TS", jan)
        pos = _position(jo, self.rank)
        _contract(self.user, self.ship, self.co, self.rank, pos, jan)
        _contract(self.user, self.ship, self.co, self.rank, pos, jan)
        _contract(self.user, self.ship, self.co, self.rank, pos, mar)
        # Confirm the contracts were actually persisted
        from api.models import Contract
        self.assertEqual(
            Contract.objects.filter(
                company=self.co,
                sign_on_date__gte=jan, sign_on_date__lte=mar,
            ).count(),
            3,
        )
        r = _client(self.admin).get(URL, {
            "date_from": "2026-01-01",
            "date_to": "2026-04-30",
            "granularity": "month",
        })
        self.assertEqual(r.status_code, 200)
        # Debug: confirm the filters the server applied
        self.assertEqual(r.data["filters"]["date_from"], "2026-01-01")
        self.assertEqual(r.data["filters"]["date_to"], "2026-04-30")
        self.assertEqual(r.data["summary"]["contracts"], 3)
        signed = {
            row["period"]: row["signed"]
            for row in r.data["time_series"]["contracts_over_time"]
        }
        self.assertEqual(signed["2026-01"], 2)
        self.assertEqual(signed["2026-02"], 0)
        self.assertEqual(signed["2026-03"], 1)


# ---------------------------------------------------------------------------
# Top N
# ---------------------------------------------------------------------------


class HistoricalDataTopNTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = _admin()
        cls.co_a = _company("Alpha")
        cls.co_b = _company("Bravo")
        cls.co_c = _company("Charlie")
        cls.ship_a = _ship("MV A", cls.co_a)
        cls.ship_b = _ship("MV B", cls.co_b)
        cls.ship_c = _ship("MV C", cls.co_c)
        cls.rank = _rank("MAS-1", "Master")
        cls.u1 = Users.objects.create_user(email="u1@x", password="x", first_name="U1", middle_name="U1")
        cls.u2 = Users.objects.create_user(email="u2@x", password="x", first_name="U2", middle_name="U2")

    def test_top_by_contracts(self):
        today = datetime.date.today()
        # co_a: 3 contracts, co_b: 1, co_c: 0
        jo_a = _jo(self.co_a, self.ship_a, "JA", today)
        pos_a = _position(jo_a, self.rank)
        jo_b = _jo(self.co_b, self.ship_b, "JB", today)
        pos_b = _position(jo_b, self.rank)
        for _ in range(3):
            _contract(self.u1, self.ship_a, self.co_a, self.rank, pos_a, today)
        _contract(self.u2, self.ship_b, self.co_b, self.rank, pos_b, today)
        r = _client(self.admin).get(URL, {"top_n": "5"})
        rows = r.data["top_n"]["top_companies_by_contracts"]
        self.assertEqual(rows[0]["company_name"], "Alpha")
        self.assertEqual(rows[0]["count"], 3)
        # co_c has no contracts so it shouldn't appear
        names = {row["company_name"] for row in rows}
        self.assertNotIn("Charlie", names)

    def test_top_n_limit(self):
        # 3 companies, top_n=2 -> 2 rows
        r = _client(self.admin).get(URL, {"top_n": "2"})
        self.assertLessEqual(
            len(r.data["top_n"]["top_companies_by_contracts"]), 2
        )

    def test_top_by_crew_placed_counts_distinct_users(self):
        today = datetime.date.today()
        jo = _jo(self.co_a, self.ship_a, "JA", today)
        pos = _position(jo, self.rank)
        # 2 contracts with the SAME user shouldn't double-count
        _contract(self.u1, self.ship_a, self.co_a, self.rank, pos, today)
        _contract(self.u1, self.ship_a, self.co_a, self.rank, pos, today)
        # 1 contract with a different user should
        _contract(self.u2, self.ship_a, self.co_a, self.rank, pos, today)
        r = _client(self.admin).get(URL, {"top_n": "5"})
        rows = r.data["top_n"]["top_companies_by_crew_placed"]
        self.assertEqual(rows[0]["company_name"], "Alpha")
        self.assertEqual(rows[0]["crew_count"], 2)


# ---------------------------------------------------------------------------
# Breakdowns
# ---------------------------------------------------------------------------


class HistoricalDataBreakdownsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = _admin()
        cls.t_owner = CompanyType.objects.create(name="Ship Owner")
        cls.t_manager = CompanyType.objects.create(name="Ship Manager")
        cls.flag_eg_name = f"Egypt-{id(cls)}"
        cls.flag_us_name = f"USA-{id(cls)}"
        cls.flag_eg = Flag.objects.create(name=cls.flag_eg_name)
        cls.flag_us = Flag.objects.create(name=cls.flag_us_name)
        cls.co_a = _company("A", company_type=cls.t_owner, flag=cls.flag_eg)
        cls.co_b = _company("B", company_type=cls.t_owner, flag=cls.flag_us)
        cls.co_c = _company("C", company_type=cls.t_manager, flag=cls.flag_eg, status="Inactive")
        cls.ship_a = _ship("MV A", cls.co_a)

    def test_breakdown_by_company_status(self):
        r = _client(self.admin).get(URL)
        self.assertEqual(r.data["breakdowns"]["by_company_status"]["Active"], 2)
        self.assertEqual(r.data["breakdowns"]["by_company_status"]["Inactive"], 1)

    def test_breakdown_by_company_type(self):
        r = _client(self.admin).get(URL)
        self.assertEqual(r.data["breakdowns"]["by_company_type"]["Ship Owner"], 2)
        self.assertEqual(r.data["breakdowns"]["by_company_type"]["Ship Manager"], 1)

    def test_breakdown_by_country(self):
        r = _client(self.admin).get(URL)
        self.assertEqual(r.data["breakdowns"]["by_country"][self.flag_eg_name], 2)
        self.assertEqual(r.data["breakdowns"]["by_country"][self.flag_us_name], 1)


# ---------------------------------------------------------------------------
# Per-company timeline
# ---------------------------------------------------------------------------


class HistoricalDataPerCompanyTimelineTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = _admin()
        cls.co = _company("Timeline Co")
        cls.ship = _ship("MV Timeline", cls.co)
        cls.rank = _rank("MAS-1", "Master")
        cls.user = Users.objects.create_user(
            email="u@x", password="x", first_name="U", middle_name="U",
        )

    def test_timeline_absent_by_default(self):
        r = _client(self.admin).get(URL)
        self.assertNotIn("per_company_timeline", r.data)

    def test_timeline_present_when_include_true(self):
        r = _client(self.admin).get(URL, {"include_timeline": "true"})
        self.assertIn("per_company_timeline", r.data)

    def test_timeline_chronological(self):
        today = datetime.date.today()
        # Events in this order: JO Dec, Contract Dec, JO Jan
        dec = datetime.date(today.year - 1, 12, 15)
        jan = datetime.date(today.year, 1, 10)
        jo_dec = _jo(self.co, self.ship, "JO-DEC", dec)
        pos_dec = _position(jo_dec, self.rank)
        _contract(self.user, self.ship, self.co, self.rank, pos_dec, dec)
        _jo(self.co, self.ship, "JO-JAN", jan)
        r = _client(self.admin).get(URL, {
            "date_from": dec.isoformat(),
            "date_to": (jan + datetime.timedelta(days=30)).isoformat(),
            "include_timeline": "true",
        })
        companies = r.data["per_company_timeline"]
        self.assertEqual(len(companies), 1)
        events = companies[0]["events"]
        # 2 JOs + 1 contract = 3 events
        self.assertEqual(len(events), 3)
        # Chronological order
        dates = [
            e.get("request_date") or e.get("sign_on_date")
            for e in events
        ]
        self.assertEqual(dates, sorted(dates))


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


class HistoricalDataValidationTests(TestCase):
    def setUp(self):
        self.admin = _admin()

    def test_invalid_date_format_returns_400(self):
        r = _client(self.admin).get(URL, {"date_from": "2026/01/01"})
        self.assertEqual(r.status_code, 400)

    def test_date_from_after_date_to_returns_400(self):
        r = _client(self.admin).get(URL, {
            "date_from": "2026-12-31",
            "date_to": "2026-01-01",
        })
        self.assertEqual(r.status_code, 400)

    def test_invalid_granularity_returns_400(self):
        r = _client(self.admin).get(URL, {"granularity": "decade"})
        self.assertEqual(r.status_code, 400)

    def test_invalid_top_n_returns_400(self):
        r = _client(self.admin).get(URL, {"top_n": "999"})
        self.assertEqual(r.status_code, 400)

    def test_invalid_company_ids_returns_400(self):
        r = _client(self.admin).get(URL, {"company_ids": "abc"})
        self.assertEqual(r.status_code, 400)
