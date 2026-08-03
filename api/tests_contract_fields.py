# api/tests_contract_fields.py
#
# Regression tests for the Contract Information section in
# ContractViewModal — the three contract fields that the frontend
# form binds to but the backend either didn't expose at all
# (`duration`) or exposed the column but not the API field
# (`repatriation_terms`, `leave_pay_terms`).
#
# Locks in the full CRUD round-trip on all three via /api/contracts/
# so a future serializer refactor can't silently drop them again.

import datetime
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status as http_status

from api.models import Users, Contract
from companies.models import Company
from core.models import Flag, VesselType
from ships.models import Ship
from api.models import Rank


def _admin():
    return Users.objects.create_user(
        email="cf-admin@test.com", password="x",
        first_name="A", middle_name="A", role="Admin",
        is_staff=True, is_superuser=True,
    )


def _employee():
    return Users.objects.create_user(
        email="cf-emp@test.com", password="x",
        first_name="E", middle_name="E", role="Employee",
    )


def _contract(user, **overrides):
    """Minimum valid Contract row. `overrides` lets each test
    customise sign_on_date / sign_off_date / duration / terms."""
    base = {
        "user": user,
        "sign_on_date": datetime.date(2026, 1, 15),
    }
    base.update(overrides)
    return Contract.objects.create(**base)


# ============================================================================
# Field-surface tests for the 3 contract fields
# ============================================================================


class ContractInformationFieldsTests(TestCase):
    """Locks in the read/write contract for `duration`,
    `repatriation_terms`, `leave_pay_terms` — the three fields the
    Contract Information form (in ContractViewModal) binds to."""

    # ---- common fixtures ----

    @classmethod
    def setUpTestData(cls):
        cls.admin = _admin()
        cls.employee = _employee()
        cls.contract = _contract(cls.employee)

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

    def _list_url(self):
        return "/api/contracts/"

    def _detail_url(self, pk):
        return f"/api/contracts/{pk}/"

    # ---- the 3 fields actually round-trip ----

    def test_create_with_all_three_fields_persists(self):
        # Use a third user (not the one with the setUpTestData
        # contract) to avoid the overlap validation in
        # `ContractSerializer.validate_overlap` (which rejects two
        # active contracts for the same user in the same date range).
        other = Users.objects.create_user(
            email="cf-other@test.com", password="x",
            first_name="O", middle_name="O", role="Employee",
        )
        r = self.client.post(self._list_url(), {
            "user": other.id,
            "sign_on_date": "2026-02-01",
            "duration": 9,
            "repatriation_terms": "Repatriation by air, economy class",
            "leave_pay_terms": "30 days paid leave per year",
        }, format="json")
        self.assertEqual(r.status_code, http_status.HTTP_201_CREATED, r.data)
        pk = r.data["id"]
        # Round-trip from DB to make sure the data actually landed
        c = Contract.objects.get(id=pk)
        self.assertEqual(c.duration, 9)
        self.assertEqual(c.repatriation_terms, "Repatriation by air, economy class")
        self.assertEqual(c.leave_pay_terms, "30 days paid leave per year")

    def test_list_response_includes_all_three_fields(self):
        """The 3 fields must appear in the LIST response, not just the
        detail response — the frontend's list view reads from the
        list endpoint."""
        self.contract.duration = 12
        self.contract.repatriation_terms = "term-A"
        self.contract.leave_pay_terms = "term-B"
        self.contract.save()

        r = self.client.get(self._list_url())
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)
        results = r.data if isinstance(r.data, list) else r.data.get("results", [])
        self.assertTrue(results, "list should have at least one contract")
        # DRF list uses ContractListSerializer — find ours
        row = next(
            (row for row in results if row.get("id") == self.contract.id),
            None,
        )
        self.assertIsNotNone(row, "our contract should be in the list")
        for key in ("duration", "repatriation_terms", "leave_pay_terms"):
            self.assertIn(
                key, row,
                f"list response is missing field {key!r} — the frontend "
                f"will show '—' for this column",
            )
        self.assertEqual(row["duration"], 12)
        self.assertEqual(row["repatriation_terms"], "term-A")
        self.assertEqual(row["leave_pay_terms"], "term-B")

    def test_detail_response_includes_all_three_fields(self):
        self.contract.duration = 6
        self.contract.repatriation_terms = "flight reimbursed"
        self.contract.leave_pay_terms = "30 days"
        self.contract.save()

        r = self.client.get(self._detail_url(self.contract.id))
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)
        for key in ("duration", "repatriation_terms", "leave_pay_terms"):
            self.assertIn(key, r.data, f"detail response missing {key!r}")
        self.assertEqual(r.data["duration"], 6)
        self.assertEqual(r.data["repatriation_terms"], "flight reimbursed")
        self.assertEqual(r.data["leave_pay_terms"], "30 days")

    def test_patch_updates_all_three_fields(self):
        """The 'Save' button in the form sends a PATCH with all 3 fields
        — verify it lands cleanly."""
        r = self.client.patch(self._detail_url(self.contract.id), {
            "duration": 7,
            "repatriation_terms": "By sea",
            "leave_pay_terms": "45 days",
        }, format="json")
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)
        self.contract.refresh_from_db()
        self.assertEqual(self.contract.duration, 7)
        self.assertEqual(self.contract.repatriation_terms, "By sea")
        self.assertEqual(self.contract.leave_pay_terms, "45 days")

    def test_patch_with_only_duration_leaves_terms_unchanged(self):
        """Partial PATCH — touching one field should not null the others."""
        self.contract.repatriation_terms = "keep me"
        self.contract.leave_pay_terms = "and me"
        self.contract.save()

        r = self.client.patch(self._detail_url(self.contract.id), {
            "duration": 3,
        }, format="json")
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)
        self.contract.refresh_from_db()
        self.assertEqual(self.contract.duration, 3)
        self.assertEqual(self.contract.repatriation_terms, "keep me")
        self.assertEqual(self.contract.leave_pay_terms, "and me")

    def test_empty_strings_for_terms_are_accepted(self):
        """The form might submit empty strings (the user cleared the
        field) — make sure that doesn't 400."""
        r = self.client.patch(self._detail_url(self.contract.id), {
            "repatriation_terms": "",
            "leave_pay_terms": "",
        }, format="json")
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)
        # CharField/TextField columns: empty string vs null
        # (model has null=True, blank=True) — backend stores null
        # for empty strings, which is the frontend-friendly value.
        self.contract.refresh_from_db()
        self.assertIn(self.contract.repatriation_terms, (None, ""))
        self.assertIn(self.contract.leave_pay_terms, (None, ""))

    def test_duration_negative_is_rejected_by_positiveintegerfield(self):
        """PositiveIntegerField rejects negative values. 0 is
        technically allowed (it's non-negative) but semantically
        meaningless — a contract with 0 months is just a sign-on
        record. We use -1 here to exercise the actual constraint."""
        r = self.client.patch(self._detail_url(self.contract.id), {
            "duration": -1,
        }, format="json")
        self.assertEqual(r.status_code, http_status.HTTP_400_BAD_REQUEST, r.data)
        self.assertIn("duration", r.data)
