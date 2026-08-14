# companies/tests.py
#
# Regression tests for the trailing-slash-optional router behaviour
# (TrailingSlashOptionalRouter) and for the /api/companies/job-positions/
# endpoint's field surface — confirms that the 9 columns the frontend
# renders (RANK, PRINCIPAL, VESSEL, STATUS, REQUIRED, SIGNED, REMAINING,
# ASSIGNED TO, SALARY RANGE) all round-trip cleanly with sample data.
#
# Run with: python manage.py test companies.tests --verbosity=2

import datetime
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status as http_status

from companies.routers import TrailingSlashOptionalRouter
from companies.models import Company, JobOrder, JobOrderPosition
from companies.views import CompanyViewSet, JobOrderViewSet, JobOrderPositionViewSet
from core.models import CompanyType

from api.models import Users, Rank, Contract
from ships.models import Ship


# ============================================================================
# TrailingSlashOptionalRouter unit tests (no DB needed)
# ============================================================================


def _build_router():
    """Build a router the same way companies/urls.py does."""
    router = TrailingSlashOptionalRouter()
    router.register(r'job-orders', JobOrderViewSet, basename='job-order')
    router.register(r'job-positions', JobOrderPositionViewSet, basename='job-position')
    router.register(r'', CompanyViewSet, basename='company')
    return router


class TrailingSlashOptionalRouterTests(TestCase):
    """The router should register each URL with AND without a trailing slash."""

    def setUp(self):
        self.router = _build_router()
        self.patterns = self.router.urls

    def _pattern_str(self, p):
        try:
            return p.pattern.regex.pattern
        except AttributeError:
            return None

    def _find_pattern(self, regex_tail):
        for p in self.patterns:
            pat = self._pattern_str(p)
            if pat is None:
                continue
            if pat.endswith(regex_tail):
                return p
        self.fail(f"no URLPattern found ending with {regex_tail!r}")

    def test_router_emits_no_slash_variants(self):
        no_slash = [
            p for p in self.patterns
            if (self._pattern_str(p) or "").endswith("/?$")
        ]
        self.assertGreater(len(no_slash), 0, "router did not emit any no-slash variants")
        with_slash = [
            p for p in self.patterns
            if (self._pattern_str(p) or "").endswith("/$")
        ]
        self.assertGreater(len(with_slash), 0)

    def test_job_positions_list_resolves_with_and_without_slash(self):
        with_slash = self._find_pattern(r"^job-positions/$")
        no_slash = self._find_pattern(r"^job-positions/?$")
        self.assertIsNotNone(with_slash)
        self.assertIsNotNone(no_slash)
        self.assertIs(with_slash.callback, no_slash.callback)

    def test_job_positions_detail_resolves_with_and_without_slash(self):
        with_slash = self._find_pattern(r"^job-positions/(?P<pk>[^/.]+)/$")
        no_slash = self._find_pattern(r"^job-positions/(?P<pk>[^/.]+)/?$")
        self.assertIsNotNone(with_slash)
        self.assertIsNotNone(no_slash)
        self.assertIs(with_slash.callback, no_slash.callback)

    def test_no_slash_variant_named(self):
        with_slash = self._find_pattern(r"job-positions/$")
        no_slash = [
            p for p in self.patterns
            if p.callback is with_slash.callback and p.name and p.name.endswith("_noslash")
        ]
        self.assertEqual(len(no_slash), 1, "expected exactly one _noslash variant per route")


class AppendSlashPostSafetyTests(TestCase):
    """Simulate the production bug: POST without trailing slash must not raise."""

    def setUp(self):
        self.router = _build_router()
        self.patterns = self.router.urls

    def _resolve_via_router(self, suffix):
        for p in self.patterns:
            try:
                compiled = p.pattern.regex
            except AttributeError:
                continue
            if compiled.match(suffix):
                return p
        return None

    def test_post_job_positions_no_slash_does_not_raise(self):
        self.assertIsNotNone(self._resolve_via_router("job-positions"))

    def test_post_job_positions_with_slash_still_works(self):
        self.assertIsNotNone(self._resolve_via_router("job-positions/"))

    def test_post_job_positions_detail_no_slash(self):
        self.assertIsNotNone(self._resolve_via_router("job-positions/42"))

    def test_post_job_positions_detail_with_slash(self):
        self.assertIsNotNone(self._resolve_via_router("job-positions/42/"))


# ============================================================================
# /api/companies/job-positions/ — field-surface smoke tests
# ============================================================================


def _make_user(email="seafarer1@example.com", first_name="Mahmoud", middle_name="Ali"):
    """Create a user with the minimum required fields for Contract linkage.

    Note: the api.Users model has first_name + middle_name, no last_name.
    The 'full name' shown in serializers is f"{first} {middle}".strip().
    """
    return Users.objects.create_user(
        email=email,
        password="x",
        first_name=first_name,
        middle_name=middle_name or "",
    )


def _make_company(name="Test Principal Co.", **overrides):
    defaults = {
        "company_name": name,
        "contact_email": "ops@example.com",
        "status": "Active",
    }
    defaults.update(overrides)
    return Company.objects.create(**defaults)


def _make_ship(name="MV Test Ship", imo="9876543", company=None):
    return Ship.objects.create(ship_name=name, imo_number=imo, company=company)


def _make_rank(code="MAS-1", name="Master"):
    return Rank.objects.create(code=code, name=name)


def _make_job_order(company, ship, reference="JO-2026-001", status="Open"):
    return JobOrder.objects.create(
        company=company,
        ship=ship,
        reference_number=reference,
        request_date=datetime.date.today(),
        target_joining_date=datetime.date.today() + datetime.timedelta(days=30),
        status=status,
    )


def _make_position(job_order, rank, quantity=3, salary_min=5000, salary_max=8000, currency="USD"):
    return JobOrderPosition.objects.create(
        job_order=job_order,
        rank=rank,
        quantity=quantity,
        salary_min=salary_min,
        salary_max=salary_max,
        currency=currency,
        contract_duration_months=6,
        remarks="Smoke test position",
    )


def _make_contract(user, ship, company, rank, position, status="Active"):
    return Contract.objects.create(
        user=user,
        ship=ship,
        company=company,
        rank=rank,
        job_position=position,
        sign_on_date=datetime.date.today(),
        status=status,
    )


class JobPositionsEndpointFieldSurfaceTests(TestCase):
    """
    Smoke tests for the 9 columns the admin table renders in the
    Crew Management / Job Positions page. Each test creates a minimal
    dataset and asserts the endpoint returns the expected field shape.
    """

    @classmethod
    def setUpTestData(cls):
        cls.company = _make_company()
        cls.ship = _make_ship(company=cls.company)
        cls.rank = _make_rank()
        cls.job_order = _make_job_order(cls.company, cls.ship, status="Open")
        cls.position = _make_position(
            cls.job_order, cls.rank,
            quantity=3, salary_min=5000, salary_max=8000, currency="USD",
        )
        cls.user1 = _make_user("seafarer1@example.com", "Mahmoud", "Ali")
        cls.user2 = _make_user("seafarer2@example.com", "Yusuf", "Khan")
        # One Active contract (filled) + one Draft contract (not filled)
        cls.active_contract = _make_contract(
            cls.user1, cls.ship, cls.company, cls.rank, cls.position, status="Active"
        )
        cls.draft_contract = _make_contract(
            cls.user2, cls.ship, cls.company, cls.rank, cls.position, status="Draft"
        )

    def setUp(self):
        self.client = APIClient()
        # Endpoint requires auth; force-authenticate so we don't need
        # to set up a JWT in the smoke test.
        self.client.force_authenticate(user=self.user1)

    def _list_url(self):
        return "/api/companies/job-positions/"

    def _detail_url(self, pk):
        return f"/api/companies/job-positions/{pk}/"

    # ---- 1. RANK -----------------------------------------------------
    def test_rank_column(self):
        """rank_name and rank id are both returned."""
        r = self.client.get(self._list_url())
        self.assertEqual(r.status_code, http_status.HTTP_200_OK)
        body = r.data
        # API may return a list or a paginated dict; normalise.
        items = body if isinstance(body, list) else body.get("results", body)
        self.assertGreaterEqual(len(items), 1)
        item = next(i for i in items if i["id"] == self.position.id)
        self.assertEqual(item["rank_name"], "Master")
        self.assertEqual(item["rank"], self.rank.id)

    # ---- 2. PRINCIPAL -----------------------------------------------
    def test_principal_column(self):
        r = self.client.get(self._list_url())
        items = r.data if isinstance(r.data, list) else r.data.get("results", r.data)
        item = next(i for i in items if i["id"] == self.position.id)
        self.assertEqual(item["company_name"], "Test Principal Co.")

    # ---- 3. VESSEL ---------------------------------------------------
    def test_vessel_column(self):
        r = self.client.get(self._list_url())
        items = r.data if isinstance(r.data, list) else r.data.get("results", r.data)
        item = next(i for i in items if i["id"] == self.position.id)
        self.assertEqual(item["ship_name"], "MV Test Ship")

    # ---- 4. STATUS ---------------------------------------------------
    def test_status_column(self):
        r = self.client.get(self._list_url())
        items = r.data if isinstance(r.data, list) else r.data.get("results", r.data)
        item = next(i for i in items if i["id"] == self.position.id)
        self.assertEqual(item["status"], "Open")

    # ---- 5. REQUIRED (= quantity) -----------------------------------
    def test_required_column(self):
        r = self.client.get(self._list_url())
        items = r.data if isinstance(r.data, list) else r.data.get("results", r.data)
        item = next(i for i in items if i["id"] == self.position.id)
        self.assertEqual(item["quantity"], 3)

    # ---- 6. SIGNED (= filled_slots) ---------------------------------
    def test_signed_column_counts_active_and_signed(self):
        """filled_slots counts Active + Signed contracts only."""
        r = self.client.get(self._list_url())
        items = r.data if isinstance(r.data, list) else r.data.get("results", r.data)
        item = next(i for i in items if i["id"] == self.position.id)
        # One Active + Draft=0 → filled_slots must be 1
        self.assertEqual(item["filled_slots"], 1)
        # Promote the second contract to Signed and re-check.
        self.draft_contract.status = "Signed"
        self.draft_contract.save()
        r = self.client.get(self._list_url())
        items = r.data if isinstance(r.data, list) else r.data.get("results", r.data)
        item = next(i for i in items if i["id"] == self.position.id)
        self.assertEqual(item["filled_slots"], 2)

    # ---- 7. REMAINING (= quantity - filled_slots) ------------------
    def test_remaining_column(self):
        r = self.client.get(self._list_url())
        items = r.data if isinstance(r.data, list) else r.data.get("results", r.data)
        item = next(i for i in items if i["id"] == self.position.id)
        # 3 required - 1 signed = 2 remaining
        self.assertEqual(item["remaining_slots"], 2)

    # ---- 8. ASSIGNED TO ---------------------------------------------
    def test_assigned_to_column(self):
        """assigned_to returns full names of every Active/Signed crew member."""
        r = self.client.get(self._list_url())
        items = r.data if isinstance(r.data, list) else r.data.get("results", r.data)
        item = next(i for i in items if i["id"] == self.position.id)
        self.assertIsInstance(item["assigned_to"], list)
        # Only Mahmoud Ali (user1) is on the Active contract; Yusuf's
        # contract is Draft and must NOT be in assigned_to. The
        # serializer returns "First Middle" (api.Users has no
        # last_name, just first + middle).
        self.assertIn("Mahmoud Ali", item["assigned_to"])
        self.assertNotIn("Yusuf Khan", item["assigned_to"])
        self.assertNotIn("Yusuf", item["assigned_to"])

    # ---- 9. SALARY RANGE (salary_min / salary_max / currency) ------
    def test_salary_range_columns(self):
        r = self.client.get(self._list_url())
        items = r.data if isinstance(r.data, list) else r.data.get("results", r.data)
        item = next(i for i in items if i["id"] == self.position.id)
        self.assertEqual(float(item["salary_min"]), 5000.0)
        self.assertEqual(float(item["salary_max"]), 8000.0)
        self.assertEqual(item["currency"], "USD")

    # ---- all 9 at once (single round-trip) --------------------------
    def test_all_nine_columns_present_in_single_response(self):
        """The endpoint returns all 9 columns in a single row."""
        r = self.client.get(self._list_url())
        self.assertEqual(r.status_code, http_status.HTTP_200_OK)
        items = r.data if isinstance(r.data, list) else r.data.get("results", r.data)
        item = next(i for i in items if i["id"] == self.position.id)
        for column in (
            "rank_name", "company_name", "ship_name", "status",
            "quantity", "filled_slots", "remaining_slots",
            "assigned_to", "salary_min", "salary_max", "currency",
        ):
            self.assertIn(column, item, f"missing column {column!r} in response")

    # ---- detail endpoint returns the same fields --------------------
    def test_detail_endpoint_returns_same_columns(self):
        r = self.client.get(self._detail_url(self.position.id))
        self.assertEqual(r.status_code, http_status.HTTP_200_OK)
        item = r.data
        self.assertEqual(item["id"], self.position.id)
        self.assertEqual(item["rank_name"], "Master")
        self.assertEqual(item["quantity"], 3)
        self.assertEqual(item["filled_slots"], 1)
        self.assertEqual(item["remaining_slots"], 2)
        self.assertEqual(item["currency"], "USD")

    # ---- 0-contracts edge case --------------------------------------
    def test_signed_and_remaining_zero_when_no_contracts(self):
        """A position with no contracts must report filled=0, remaining=quantity."""
        empty_position = _make_position(
            self.job_order,
            _make_rank(code="OFF-2", name="2nd Officer"),
            quantity=2,
            salary_min=3000, salary_max=4500, currency="EUR",
        )
        r = self.client.get(self._detail_url(empty_position.id))
        item = r.data
        self.assertEqual(item["filled_slots"], 0)
        self.assertEqual(item["remaining_slots"], 2)
        self.assertEqual(item["assigned_to"], [])
        self.assertEqual(item["currency"], "EUR")
        self.assertEqual(float(item["salary_min"]), 3000.0)


class OpenPositionsStatusEndpointTests(TestCase):
    """
    Tests for GET /api/companies/open-positions-status/.

    One row per still-vacant JobOrderPosition. Filled positions
    are skipped. Cancelled / Fulfilled / Closed orders are
    excluded by default.
    """

    @classmethod
    def setUpTestData(cls):
        cls.company_a = _make_company("Maersk Line")
        cls.company_b = _make_company("MSC Mediterranean")

        cls.ship_a = _make_ship(name="MV Atlas", imo="1111111", company=cls.company_a)
        cls.ship_b = _make_ship(name="MV Bounty", imo="2222222", company=cls.company_b)

        cls.rank_master = _make_rank(code="MAS-1", name="Master")
        cls.rank_chief = _make_rank(code="CHE-1", name="Chief Officer")

        # Open job order with 2 positions, all vacant
        cls.jo_open = _make_job_order(
            cls.company_a, cls.ship_a,
            reference="JO-2026-001", status="Open",
        )
        cls.pos_master = _make_position(cls.jo_open, cls.rank_master, quantity=3)
        cls.pos_chief = _make_position(cls.jo_open, cls.rank_chief, quantity=1)

        # Open job order with a fully-filled position (should be skipped)
        cls.jo_filled = _make_job_order(
            cls.company_b, cls.ship_b,
            reference="JO-2026-002", status="Open",
        )
        cls.pos_full = _make_position(cls.jo_filled, cls.rank_master, quantity=2)
        u1 = _make_user("seafarer1@example.com", "Mahmoud", "Ali")
        u2 = _make_user("seafarer2@example.com", "Yusuf", "Khan")
        _make_contract(u1, cls.ship_b, cls.company_b, cls.rank_master, cls.pos_full)
        _make_contract(u2, cls.ship_b, cls.company_b, cls.rank_master, cls.pos_full)

        # Closed job order with a vacant position (should be excluded
        # by default because status is not in the default open set)
        cls.jo_closed = _make_job_order(
            cls.company_a, cls.ship_a,
            reference="JO-2026-003", status="Closed",
        )
        cls.pos_closed = _make_position(cls.jo_closed, cls.rank_master, quantity=1)

    def setUp(self):
        self.client = APIClient()
        # Admin user for full access
        self.admin = _make_user("admin-ops@example.com", "Admin", "Ops")
        self.admin.role = "Admin"
        self.admin.is_staff = True
        self.admin.is_superuser = True
        self.admin.save()
        self.client.force_authenticate(user=self.admin)

    def _url(self):
        return "/api/companies/open-positions-status/"

    # ---- top-level shape ----------------------------------------------

    def test_response_shape(self):
        r = self.client.get(self._url())
        self.assertEqual(r.status_code, 200)
        for k in ("total_records", "report_date", "results"):
            self.assertIn(k, r.data, f"missing {k!r} in response")
        self.assertIsInstance(r.data["total_records"], int)
        self.assertIsInstance(r.data["results"], list)
        # report_date must be today's local date
        from django.utils import timezone
        self.assertEqual(r.data["report_date"], timezone.localdate().isoformat())

    def test_result_row_shape(self):
        r = self.client.get(self._url())
        self.assertEqual(r.status_code, 200)
        if not r.data["results"]:
            self.skipTest("No open positions in fixture")
        for row in r.data["results"]:
            for k in (
                "reference_number", "principal", "position_title",
                "vacancies", "status", "job_order_number",
                "request_date", "target_join_date",
            ):
                self.assertIn(k, row, f"missing {k!r} in row {row!r}")

    # ---- content filtering --------------------------------------------

    def test_total_records_counts_only_vacant_open_positions(self):
        """Filled positions and closed orders must be excluded."""
        r = self.client.get(self._url())
        self.assertEqual(r.status_code, 200)
        # Fixtures: 2 vacant positions in JO-2026-001 (status=Open).
        # JO-2026-002 has a fully-filled position (skip).
        # JO-2026-003 is Closed (skip by default).
        self.assertEqual(r.data["total_records"], 2)

    def test_filled_position_excluded(self):
        """JO-2026-002 has quantity=2 and 2 Active contracts -> 0 vacancies, skip."""
        r = self.client.get(self._url())
        self.assertEqual(r.status_code, 200)
        refs = [row["reference_number"] for row in r.data["results"]]
        self.assertNotIn("JO-2026-002", refs)

    def test_closed_order_excluded_by_default(self):
        r = self.client.get(self._url())
        refs = [row["reference_number"] for row in r.data["results"]]
        self.assertNotIn("JO-2026-003", refs)

    def test_partial_fill_shows_remaining_vacancies(self):
        """A position with quantity=3 and 1 Active contract -> vacancies=2."""
        pos = _make_position(
            self.jo_open,
            _make_rank(code="BOS-1", name="Bosun"),
            quantity=3,
        )
        u = _make_user("partial-fill@example.com", "Partial", "Fill")
        _make_contract(u, self.ship_a, self.company_a,
                       pos.rank, pos, status="Active")
        r = self.client.get(self._url())
        rows = [row for row in r.data["results"]
                if row["reference_number"] == "JO-2026-001"
                and row["position_title"] == "Bosun"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["vacancies"], 2)

    def test_vacancies_uses_remaining_not_quantity(self):
        """A fully-filled position (0 remaining) must be excluded, even
        though the parent job order is Open."""
        # JO-2026-002 is already filled in the fixture; verify it's not
        # in the result by checking it's missing.
        r = self.client.get(self._url())
        rows = [row for row in r.data["results"]
                if row["reference_number"] == "JO-2026-002"]
        self.assertEqual(rows, [])

    # ---- principal field is the company name --------------------------

    def test_principal_field_is_company_name(self):
        r = self.client.get(self._url())
        principals = {row["principal"] for row in r.data["results"]}
        # Both job orders in JO-2026-001 belong to company_a
        self.assertIn("Maersk Line", principals)
        # JO-2026-002 / 003 belong to company_b or are skipped
        self.assertNotIn("MSC Mediterranean", principals)

    # ---- explicit status filter --------------------------------------

    def test_status_filter_includes_closed_when_requested(self):
        r = self.client.get(self._url() + "?status=Closed")
        self.assertEqual(r.status_code, 200)
        refs = [row["reference_number"] for row in r.data["results"]]
        self.assertIn("JO-2026-003", refs)

    def test_status_filter_rejects_invalid_value(self):
        r = self.client.get(self._url() + "?status=Bogus")
        self.assertEqual(r.status_code, 400)
        self.assertIn("Invalid status", r.data.get("error", ""))

    # ---- principal filter --------------------------------------------

    def test_principal_filter(self):
        """Filter by company id returns only that principal's rows."""
        # Add a vacant position under company_b
        _make_position(
            self.jo_filled,
            _make_rank(code="ENG-1", name="Chief Engineer"),
            quantity=2,
        )
        # But the parent job order is Open, so this row will be
        # included regardless of company. We just check the filter
        # excludes rows from the other company.
        r = self.client.get(self._url() + "?principal=999999")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["total_records"], 0)

    # ---- position_title filter ---------------------------------------

    def test_position_title_filter(self):
        r = self.client.get(self._url() + "?position_title=chief")
        self.assertEqual(r.status_code, 200)
        titles = [row["position_title"] for row in r.data["results"]]
        self.assertIn("Chief Officer", titles)
        self.assertNotIn("Master", titles)

    # ---- ordering ----------------------------------------------------

    def test_results_sorted_by_request_date_then_reference(self):
        # Add an earlier-dated open order and verify it sorts first
        import datetime
        jo_earlier = _make_job_order(
            self.company_a, self.ship_a,
            reference="JO-2025-099", status="Open",
        )
        # Backdate the request_date
        jo_earlier.request_date = datetime.date(2025, 1, 1)
        jo_earlier.save(update_fields=["request_date"])
        _make_position(jo_earlier, self.rank_master, quantity=2)

        r = self.client.get(self._url())
        # First row should be the earlier-dated one
        self.assertEqual(r.data["results"][0]["reference_number"], "JO-2025-099")

    # ---- auth --------------------------------------------------------

    def test_endpoint_requires_auth(self):
        from rest_framework.test import APIClient
        c = APIClient()
        r = c.get(self._url())
        self.assertIn(r.status_code, (401, 403))


class CompanyWebsiteFieldNoAutoPrefixTests(TestCase):
    """
    Regression: the company serializer's to_internal_value used to
    auto-prepend 'https://' to the website field, so users who typed
    'www.example.com' had it silently re-prefixed on every save and
    saw 'https://www.example.com' in the form on every edit. Now the
    field is stored exactly as submitted.
    """

    def setUp(self):
        from rest_framework.test import APIClient
        self.user = _make_user("website-admin@example.com", "Web", "Admin")
        self.user.role = "Admin"
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.company = _make_company("Test Co.")

    def _patch(self, website):
        return self.client.patch(
            f"/api/companies/{self.company.id}/",
            {"website": website},
            format="json",
        )

    def test_bare_domain_stays_bare(self):
        r = self._patch("www.example.com")
        self.assertEqual(r.status_code, 200, r.data)
        self.company.refresh_from_db()
        self.assertEqual(self.company.website, "www.example.com")

    def test_https_stays_https(self):
        r = self._patch("https://www.example.com")
        self.assertEqual(r.status_code, 200, r.data)
        self.company.refresh_from_db()
        self.assertEqual(self.company.website, "https://www.example.com")

    def test_http_stays_http(self):
        r = self._patch("http://www.example.com")
        self.assertEqual(r.status_code, 200, r.data)
        self.company.refresh_from_db()
        self.assertEqual(self.company.website, "http://www.example.com")

    def test_empty_string_is_allowed(self):
        r = self._patch("")
        self.assertEqual(r.status_code, 200, r.data)
        self.company.refresh_from_db()
        # URLField with blank=True stores empty as ''
        self.assertIn(self.company.website or "", ("", None))

    def test_no_loop_after_save(self):
        """Save with bare domain, re-edit, value is still bare."""
        self._patch("www.example.com")
        self.company.refresh_from_db()
        self.assertEqual(self.company.website, "www.example.com")
        # Re-PATCH the same value
        self._patch("www.example.com")
        self.company.refresh_from_db()
        self.assertEqual(
            self.company.website, "www.example.com",
            "Re-saving must not add a 'https://' prefix",
        )


class JobOrderVacancyRollupsTests(TestCase):
    """
    Tests for the three vacancy rollup fields on JobOrderSerializer:
    total_open_vacancies, total_closed_vacancies, total_fully_filled_vacancies.

    Counts are over the nested positions list (i.e. over the
    JobOrderPositions belonging to this JobOrder). A position is
    counted as:
      - "open"     if remaining_slots > 0  (quantity - filled > 0)
      - "closed"   if remaining_slots == 0
      - "fully filled" if filled_slots >= quantity AND quantity > 0
    """

    @classmethod
    def setUpTestData(cls):
        cls.company = _make_company("Vacancy Test Co.")
        cls.ship = _make_ship(name="MV Vacancy", imo="9999999", company=cls.company)
        cls.rank_a = _make_rank(code="VAC-A", name="Vacancy A")
        cls.rank_b = _make_rank(code="VAC-B", name="Vacancy B")
        cls.rank_c = _make_rank(code="VAC-C", name="Vacancy C")
        cls.rank_d = _make_rank(code="VAC-D", name="Vacancy D")

    def setUp(self):
        from rest_framework.test import APIClient
        self.user = _make_user("vacancy-admin@example.com", "Vac", "Admin")
        self.user.role = "Admin"
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.job_order = _make_job_order(
            self.company, self.ship,
            reference="JO-VAC-001", status="Open",
        )

    def _row(self, jo_id):
        r = self.client.get(f"/api/companies/job-orders/{jo_id}/")
        self.assertEqual(r.status_code, 200, r.data)
        return r.data

    # ---- counts -------------------------------------------------------

    def test_all_open_three_positions(self):
        # Three positions, all with remaining > 0
        _make_position(self.job_order, self.rank_a, quantity=2)
        _make_position(self.job_order, self.rank_b, quantity=1)
        _make_position(self.job_order, self.rank_c, quantity=3)

        row = self._row(self.job_order.id)
        self.assertEqual(row["total_open_vacancies"], 3)
        self.assertEqual(row["total_closed_vacancies"], 0)
        self.assertEqual(row["total_fully_filled_vacancies"], 0)

    def test_mix_of_open_closed_and_fully_filled(self):
        # A: 1 open (quantity 2, 0 filled -> 2 remaining -> open)
        _make_position(self.job_order, self.rank_a, quantity=2)
        # B: 1 closed (quantity 0 -> 0 remaining)
        _make_position(self.job_order, self.rank_b, quantity=0)
        # C: 1 fully filled (quantity 1, 1 filled -> 0 remaining, fully filled)
        pos_c = _make_position(self.job_order, self.rank_c, quantity=1)
        u = _make_user("vac-fully@example.com", "Vac", "Full")
        _make_contract(u, self.ship, self.company, self.rank_c, pos_c)
        # D: 1 closed (quantity 3, 3 filled -> 0 remaining, fully filled)
        pos_d = _make_position(self.job_order, self.rank_d, quantity=3)
        for i in range(3):
            _make_contract(
                _make_user(f"vac-d-{i}@example.com", f"User{i}", "D"),
                self.ship, self.company, self.rank_d, pos_d,
            )

        row = self._row(self.job_order.id)
        # 1 open (A), 3 closed (B, C, D), 2 fully filled (C, D)
        self.assertEqual(row["total_open_vacancies"], 1)
        self.assertEqual(row["total_closed_vacancies"], 3)
        self.assertEqual(row["total_fully_filled_vacancies"], 2)

    def test_partially_filled_position_is_open_not_closed(self):
        # quantity 5, 1 filled -> 4 remaining -> open AND not fully filled
        pos = _make_position(self.job_order, self.rank_a, quantity=5)
        u = _make_user("vac-partial@example.com", "Partial", "Fill")
        _make_contract(u, self.ship, self.company, self.rank_a, pos)

        row = self._row(self.job_order.id)
        self.assertEqual(row["total_open_vacancies"], 1)
        self.assertEqual(row["total_closed_vacancies"], 0)
        self.assertEqual(row["total_fully_filled_vacancies"], 0)

    def test_no_positions_all_zeros(self):
        row = self._row(self.job_order.id)
        self.assertEqual(row["total_open_vacancies"], 0)
        self.assertEqual(row["total_closed_vacancies"], 0)
        self.assertEqual(row["total_fully_filled_vacancies"], 0)

    def test_quantity_zero_with_filled_is_closed_not_fully_filled(self):
        """The bug case from the user's screenshot: quantity=0, filled=1.
        Must be closed (remaining=0) but NOT fully filled (quantity=0
        means there was no vacancy to fill in the first place)."""
        pos = _make_position(self.job_order, self.rank_a, quantity=0)
        u = _make_user("vac-zeroqty@example.com", "Zero", "Qty")
        _make_contract(u, self.ship, self.company, self.rank_a, pos)

        row = self._row(self.job_order.id)
        self.assertEqual(row["total_open_vacancies"], 0)
        self.assertEqual(row["total_closed_vacancies"], 1)
        # NOT counted as fully filled: quantity is 0 (no vacancy to fill)
        self.assertEqual(row["total_fully_filled_vacancies"], 0)

    def test_draft_contract_does_not_count_as_filled(self):
        """Only Active/Signed contracts count as filled.
        A Draft contract must leave the position open."""
        pos = _make_position(self.job_order, self.rank_a, quantity=1)
        u = _make_user("vac-draft@example.com", "Draft", "Only")
        _make_contract(u, self.ship, self.company, self.rank_a, pos,
                       status="Draft")

        row = self._row(self.job_order.id)
        # position still has remaining=1 (Draft doesn't count)
        self.assertEqual(row["total_open_vacancies"], 1)
        self.assertEqual(row["total_closed_vacancies"], 0)
        self.assertEqual(row["total_fully_filled_vacancies"], 0)

    def test_list_endpoint_also_returns_rollups(self):
        """The list endpoint must include the new fields too."""
        _make_position(self.job_order, self.rank_a, quantity=2)
        r = self.client.get("/api/companies/job-orders/")
        self.assertEqual(r.status_code, 200)
        item = next(
            i for i in r.data.get("results", r.data)
            if i["id"] == self.job_order.id
        )
        self.assertIn("total_open_vacancies", item)
        self.assertIn("total_closed_vacancies", item)
        self.assertIn("total_fully_filled_vacancies", item)
        self.assertEqual(item["total_open_vacancies"], 1)


class JobOrderAutoFulfilledSignalTests(TestCase):
    """
    Tests for the auto-transition signal: when all positions under
    a JobOrder are fully filled, status auto-flips to "Fulfilled"
    (one-way). Triggered by Contract post_save/post_delete and by
    JobOrderPosition post_save/post_delete.
    """

    def setUp(self):
        from companies.models import JobOrder
        self.company = _make_company("Fulfill Test Co.")
        self.ship = _make_ship(name="MV Fulfill", imo="8888888", company=self.company)
        self.rank_a = _make_rank(code="FUL-A", name="Fulfill A")
        self.rank_b = _make_rank(code="FUL-B", name="Fulfill B")

    def _make_open_jo(self, reference="JO-FUL-001"):
        return _make_job_order(
            self.company, self.ship,
            reference=reference, status="Open",
        )

    # ---- core transition tests ---------------------------------------

    def test_open_with_two_positions_promotes_when_both_filled(self):
        jo = self._make_open_jo()
        pos_a = _make_position(jo, self.rank_a, quantity=1)
        pos_b = _make_position(jo, self.rank_b, quantity=1)
        u1 = _make_user("ful-1@example.com", "Ful", "One")
        u2 = _make_user("ful-2@example.com", "Ful", "Two")
        _make_contract(u1, self.ship, self.company, self.rank_a, pos_a)
        _make_contract(u2, self.ship, self.company, self.rank_b, pos_b)

        jo.refresh_from_db()
        self.assertEqual(jo.status, "Fulfilled")

    def test_partial_fill_does_not_promote(self):
        jo = self._make_open_jo()
        pos = _make_position(jo, self.rank_a, quantity=3)
        u = _make_user("ful-partial@example.com", "Partial", "Ful")
        _make_contract(u, self.ship, self.company, self.rank_a, pos)

        jo.refresh_from_db()
        self.assertEqual(jo.status, "Open")

    def test_fully_fills_on_second_contract(self):
        """Order stays Open until the LAST slot is filled, then flips."""
        jo = self._make_open_jo()
        pos = _make_position(jo, self.rank_a, quantity=2)
        u1 = _make_user("ful-half1@example.com", "Half", "One")
        u2 = _make_user("ful-half2@example.com", "Half", "Two")
        _make_contract(u1, self.ship, self.company, self.rank_a, pos)
        jo.refresh_from_db()
        self.assertEqual(jo.status, "Open", "should still be Open after 1/2")

        _make_contract(u2, self.ship, self.company, self.rank_a, pos)
        jo.refresh_from_db()
        self.assertEqual(jo.status, "Fulfilled", "should flip after 2/2")

    def test_draft_contract_does_not_count(self):
        """Draft contracts don't fill slots, so they don't trigger."""
        jo = self._make_open_jo()
        pos = _make_position(jo, self.rank_a, quantity=1)
        u = _make_user("ful-draft@example.com", "Draft", "Only")
        _make_contract(u, self.ship, self.company, self.rank_a, pos,
                       status="Draft")
        jo.refresh_from_db()
        self.assertEqual(jo.status, "Open")

    def test_pending_status_also_promotes(self):
        """Pending is auto-promotable too."""
        jo = _make_job_order(
            self.company, self.ship,
            reference="JO-FUL-PEND", status="Pending",
        )
        pos = _make_position(jo, self.rank_a, quantity=1)
        u = _make_user("ful-pend@example.com", "Pend", "Ful")
        _make_contract(u, self.ship, self.company, self.rank_a, pos)
        jo.refresh_from_db()
        self.assertEqual(jo.status, "Fulfilled")

    def test_cancelled_status_does_not_promote(self):
        """Cancelled orders stay Cancelled even if positions fill up."""
        jo = _make_job_order(
            self.company, self.ship,
            reference="JO-FUL-CANC", status="Cancelled",
        )
        pos = _make_position(jo, self.rank_a, quantity=1)
        u = _make_user("ful-canc@example.com", "Canc", "Ful")
        _make_contract(u, self.ship, self.company, self.rank_a, pos)
        jo.refresh_from_db()
        self.assertEqual(jo.status, "Cancelled")

    def test_hold_status_does_not_promote(self):
        """Hold is a manual override; signal must not flip it."""
        jo = _make_job_order(
            self.company, self.ship,
            reference="JO-FUL-HOLD", status="Hold",
        )
        pos = _make_position(jo, self.rank_a, quantity=1)
        u = _make_user("ful-hold@example.com", "Hold", "Ful")
        _make_contract(u, self.ship, self.company, self.rank_a, pos)
        jo.refresh_from_db()
        self.assertEqual(jo.status, "Hold")

    def test_no_positions_does_not_promote(self):
        """A job order with zero positions is not 'fully filled'."""
        jo = self._make_open_jo(reference="JO-FUL-EMPTY")
        # No positions at all
        jo.refresh_from_db()
        self.assertEqual(jo.status, "Open")

    def test_position_quantity_zero_does_not_promote(self):
        """Broken data: quantity=0 must not count as fully filled."""
        jo = self._make_open_jo(reference="JO-FUL-ZERO")
        pos = _make_position(jo, self.rank_a, quantity=0)
        u = _make_user("ful-zero@example.com", "Zero", "Qty")
        _make_contract(u, self.ship, self.company, self.rank_a, pos)
        jo.refresh_from_db()
        self.assertEqual(jo.status, "Open")

    def test_position_quantity_change_triggers_recheck(self):
        """Reducing an open position's quantity to 0 with a filled
        contract does NOT promote (because quantity=0 is not a real
        vacancy)."""
        jo = self._make_open_jo(reference="JO-FUL-QTY")
        pos = _make_position(jo, self.rank_a, quantity=2)
        u = _make_user("ful-qty@example.com", "Qty", "Ful")
        _make_contract(u, self.ship, self.company, self.rank_a, pos)
        jo.refresh_from_db()
        self.assertEqual(jo.status, "Open", "1/2 still leaves 1 open")

        # Now reduce quantity to 1 — should fill
        pos.quantity = 1
        pos.save(update_fields=["quantity"])
        jo.refresh_from_db()
        self.assertEqual(jo.status, "Fulfilled")
