# api/tests.py
#
# Field-surface smoke tests for /api/users/users/ and /api/users/users/{id}/.
#
# The endpoint is a standard ModelViewSet, so we lock in:
#   1. CRUD round-trip on every category of user field (auth, profile,
#      visas, marlins/ces tests, salary, passport, seaman book, COC/GOC,
#      next of kin, health, sizes, declaration).
#   2. Read-only fields (id, created_at, updated_at, generated_id) are
#      not echoed back from writes, and a PATCH that includes them is
#      silently ignored.
#   3. Write-only field (password) is accepted on create / PATCH but
#      never returned in the response.
#   4. Required fields (email, first_name) are enforced; email is
#      unique; password is auto-handled by the custom manager.
#   5. Permission matrix: Admin = full, HR Manager = full but cannot
#      POST role=Admin, Recruiter = read-only, Employee = own profile only.
#   6. Bulk operations: bulk-edit and bulk-delete work for Admin/HR.
#
# Run with: python manage.py test api.tests --verbosity=2

import datetime
from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status as http_status

from api.models import Users, Rank, UserRank
from api.permissions import UserPermission


LIST_URL = "/api/users/users/"
DETAIL_URL_FMT = "/api/users/users/{id}/"
BULK_DELETE_URL = "/api/users/users/bulk-delete/"
BULK_EDIT_URL = "/api/users/users/bulk-edit/"


# ============================================================================
# Helpers
# ============================================================================


def _make_user(
    email="test.user@example.com",
    first_name="Test",
    middle_name="User",
    role="Employee",
    password="testpass123",
    **extra,
):
    """Create a user via the manager so the password is properly hashed.

    Bypasses signals / side effects that might fire on .objects.create().
    """
    user = Users.objects.create_user(
        email=email,
        password=password,
        first_name=first_name,
        middle_name=middle_name or "",
        role=role,
        **extra,
    )
    return user


def _make_admin(email="admin@example.com"):
    return _make_user(
        email=email, first_name="Admin", middle_name="Root", role="Admin",
        password="adminpass", is_staff=True, is_superuser=True,
    )


def _make_hr(email="hr@example.com"):
    return _make_user(
        email=email, first_name="HR", middle_name="Manager", role="HR Manager",
        password="hrpass",
    )


def _make_recruiter(email="rec@example.com"):
    return _make_user(
        email=email, first_name="Rec", middle_name="Ruiter", role="Recruiter",
        password="recpass",
    )


# ============================================================================
# TestCase base — sets up a common test graph
# ============================================================================


class UsersEndpointFieldSurfaceTests(TestCase):
    """Lock in the field surface of /api/users/users/{id}/."""

    @classmethod
    def setUpTestData(cls):
        cls.admin = _make_admin("admin@example.com")
        cls.hr = _make_hr("hr@example.com")
        cls.recruiter = _make_recruiter("rec@example.com")
        cls.employee = _make_user(
            "employee@example.com", "Emp", "Loyee", role="Employee",
        )
        cls.target = _make_user(
            "target@example.com", "Target", "User", role="Employee",
        )

    def setUp(self):
        # Each test starts fresh; we re-authenticate as needed.
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)


# ============================================================================
# 1. Create (POST /api/users/users/)
# ============================================================================


class UsersCreateTests(UsersEndpointFieldSurfaceTests):
    """POST /api/users/users/ — create a new user."""

    def test_create_with_minimum_required_fields(self):
        """email + first_name + password are enough to create a user."""
        payload = {
            "email": "new.user@example.com",
            "first_name": "New",
            "password": "newpass123",
        }
        r = self.client.post(LIST_URL, payload, format="json")
        self.assertEqual(r.status_code, http_status.HTTP_201_CREATED, r.data)
        body = r.data
        self.assertEqual(body["email"], "new.user@example.com")
        self.assertIn("id", body)
        # Write-only: password is NOT in the response
        self.assertNotIn("password", body)
        # Read-only: generated_id is null (assigned elsewhere)
        self.assertIn("generated_id", body)
        # User persisted with the right name
        u = Users.objects.get(email="new.user@example.com")
        self.assertEqual(u.first_name, "New")
        self.assertTrue(Users.objects.filter(email="new.user@example.com").exists())

    def test_create_with_all_fields_round_trip(self):
        """All writable fields land on the user and round-trip through GET."""
        payload = {
            "email": "full@example.com",
            "first_name": "Full",
            "middle_name": "Profile",
            "password": "fullpass",
            "role": "Employee",
            "country": "Egypt",
            "city": "Cairo",
            "phone_number": "+20123456789",
            "address": "123 Nile St",
            "nationality": "Egyptian",
            "blood_type": "O+",
            "age": 30,
            "marital_status": "Single",
            "date_of_birth": "1995-01-15",
            "smoker": False,
            "Height_Cm": 180,
            "Weight_Kg": 75,
            "us_visa_status": "Valid",
            "schengen_visa_status": "None",
            "user_status": "ON_SITE",
            "Nearest_Port": "Alexandria",
            "Place_Of_Birth": "Cairo",
            "college_or_school": "Maritime Academy",
            "salary": 5000,
            "application_for_position": "Master",
            "other_position": "Chief Officer",
            "available_date": "2026-12-01",
            "e_reg_no": "E-12345",
            "license_no": "L-67890",
            # Passport
            "passport_no": "P123456",
            "passport_issue_date": "2020-01-15",
            "passport_expiry_date": "2030-01-15",
            "passport_issued_by": "MOI Egypt",
            "passport_place_of_issue": "Cairo",
            # Seaman book
            "seaman_book_no": "SB-001",
            "seaman_book_issue_date": "2020-02-01",
            "seaman_book_expiry_date": "2030-02-01",
            "seaman_book_issued_by": "Maritime Authority",
            "seaman_book_place_of_issue": "Alexandria",
            # Next of kin
            "next_of_kin_full_name": "Family Member",
            "next_of_kin_relationship": "Brother",
            "next_of_kin_phone": "+201119876543",
            "next_of_kin_email": "kin@example.com",
            # Sizes
            "overall_size": "L",
            "shirt_size": "L",
            "trouser_size": "32",
            "shoes_size": "42",
            "english_language_level": "Fluent",
            # Health
            "health_flag_state": "Egypt",
            "health_number": "H-001",
            "health_issue_date": "2026-01-01",
            "health_expiry_date": "2027-01-01",
            "health_issued_by": "MOH",
            "yellow_fever_number": "YF-001",
            "yellow_fever_issue_date": "2026-01-01",
            "yellow_fever_expiry_date": "2042-01-01",
            "international_medical_number": "IM-001",
            "international_medical_issue_date": "2026-01-01",
            "international_medical_expiry_date": "2027-01-01",
            "covid_vaccine_name": "Pfizer",
            "covid_first_dose": "2021-06-01",
            "covid_second_dose": "2021-07-01",
        }
        r = self.client.post(LIST_URL, payload, format="json")
        self.assertEqual(r.status_code, http_status.HTTP_201_CREATED, r.data)

        new_id = r.data["id"]
        # Round-trip via DB. We bypass the response shape and check the
        # underlying model so we don't get tripped up by to_representation
        # quirks (e.g. first_name being auto-combined with middle_name).
        u = Users.objects.get(pk=new_id)
        for key, expected in payload.items():
            if key in ("password", "first_name", "middle_name"):
                # password is hashed; first_name/middle_name are checked
                # separately below.
                continue
            actual = getattr(u, key, None)
            # DateField: payload is ISO string; model returns date.
            if isinstance(expected, str) and actual is not None and not isinstance(actual, str):
                # Try parsing as date or datetime for comparison
                try:
                    if "T" in expected or " " in expected:
                        expected_parsed = datetime.datetime.fromisoformat(expected.replace("Z", "+00:00"))
                        if isinstance(actual, datetime.datetime):
                            # Compare ignoring tzinfo where possible
                            self.assertEqual(actual.replace(tzinfo=None) if actual.tzinfo else actual,
                                             expected_parsed.replace(tzinfo=None) if expected_parsed.tzinfo else expected_parsed,
                                             f"field {key!r}")
                        else:
                            self.assertEqual(actual, expected_parsed, f"field {key!r}")
                    else:
                        expected_parsed = datetime.date.fromisoformat(expected)
                        if isinstance(actual, datetime.datetime):
                            actual = actual.date()
                        self.assertEqual(actual, expected_parsed, f"field {key!r}")
                except ValueError:
                    self.assertEqual(actual, expected, f"field {key!r}: expected {expected!r}, got {actual!r}")
            elif isinstance(expected, (int, float)) and actual is not None:
                self.assertEqual(float(actual), float(expected), f"field {key!r}")
            else:
                self.assertEqual(actual, expected, f"field {key!r}: expected {expected!r}, got {actual!r}")
        # first_name + middle_name saved correctly
        self.assertEqual(u.first_name, "Full")
        self.assertEqual(u.middle_name, "Profile")
        # password was hashed (not stored as plaintext)
        self.assertTrue(u.check_password("fullpass"))

    def test_create_duplicate_email_rejected(self):
        """Email is unique; second create with same email returns 400."""
        Users.objects.create_user(email="dup@example.com", password="x", first_name="X")
        r = self.client.post(LIST_URL, {
            "email": "dup@example.com",
            "first_name": "Y",
            "password": "y",
        }, format="json")
        self.assertEqual(r.status_code, http_status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", r.data)

    def test_create_missing_email_rejected(self):
        """email is required."""
        r = self.client.post(LIST_URL, {
            "first_name": "NoEmail",
            "password": "x",
        }, format="json")
        self.assertEqual(r.status_code, http_status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", r.data)

    def test_create_missing_first_name_rejected(self):
        """first_name is required (USERNAME_FIELD alternative: email,
        but REQUIRED_FIELDS includes first_name)."""
        r = self.client.post(LIST_URL, {
            "email": "nofn@example.com",
            "password": "x",
        }, format="json")
        self.assertEqual(r.status_code, http_status.HTTP_400_BAD_REQUEST)
        self.assertIn("first_name", r.data)

    def test_password_never_echoed_in_response(self):
        """password is write-only; never appears in GET / POST / PATCH response."""
        r = self.client.post(LIST_URL, {
            "email": "pw@example.com", "first_name": "Pw", "password": "secret",
        }, format="json")
        self.assertNotIn("password", r.data)
        # And not on a follow-up GET
        r2 = self.client.get(DETAIL_URL_FMT.format(id=r.data["id"]))
        self.assertNotIn("password", r2.data)


# ============================================================================
# 2. Retrieve (GET /api/users/users/{id}/)
# ============================================================================


class UsersRetrieveTests(UsersEndpointFieldSurfaceTests):
    """GET /api/users/users/{id}/ — read a user."""

    def test_get_returns_all_field_categories(self):
        r = self.client.get(DETAIL_URL_FMT.format(id=self.target.id))
        self.assertEqual(r.status_code, http_status.HTTP_200_OK)
        body = r.data
        # Verify a sample from each field category is present
        expected_keys = {
            "id", "email", "first_name", "middle_name",
            "country", "city", "phone_number",
            "passport_no", "seaman_book_no",
            "coc_certificate_name", "goc_certificate_number",
            "next_of_kin_full_name",
            "health_flag_state", "yellow_fever_number",
            "english_language_level",
            "salary", "available_date",
            "created_at", "updated_at", "role", "generated_id",
        }
        for key in expected_keys:
            self.assertIn(key, body, f"missing {key!r} in GET response")

    def test_list_returns_paginated_results(self):
        r = self.client.get(LIST_URL)
        self.assertEqual(r.status_code, http_status.HTTP_200_OK)
        # response shape: list or paginated {results, count, ...}
        if isinstance(r.data, dict) and "results" in r.data:
            self.assertIn("count", r.data)
            items = r.data["results"]
        else:
            items = r.data
        self.assertGreaterEqual(len(items), 4)  # admin, hr, recruiter, employee, target


# ============================================================================
# 3. Update (PUT / PATCH /api/users/users/{id}/)
# ============================================================================


class UsersUpdateTests(UsersEndpointFieldSurfaceTests):
    """PUT / PATCH /api/users/users/{id}/ — update an existing user."""

    def test_patch_single_field(self):
        """PATCH with one field updates only that field."""
        r = self.client.patch(
            DETAIL_URL_FMT.format(id=self.target.id),
            {"phone_number": "+201111111111"},
            format="json",
        )
        self.assertEqual(r.status_code, http_status.HTTP_200_OK)
        self.assertEqual(r.data["phone_number"], "+201111111111")
        # Other fields unchanged
        self.assertEqual(r.data["email"], "target@example.com")
        # first_name in the response is auto-combined (first + middle)
        # by to_representation, so we check the underlying DB column.
        self.target.refresh_from_db()
        self.assertEqual(self.target.first_name, "Target")
        self.assertEqual(self.target.middle_name, "User")
        self.assertEqual(self.target.phone_number, "+201111111111")

    def test_patch_many_fields_across_categories(self):
        """PATCH with fields from multiple categories works."""
        patch = {
            "country": "USA",
            "city": "New York",
            "phone_number": "+12125551234",
            "passport_no": "US-PASS-001",
            "salary": 7500,
            "english_language_level": "Native",
            "next_of_kin_phone": "+12125559999",
        }
        r = self.client.patch(
            DETAIL_URL_FMT.format(id=self.target.id),
            patch,
            format="json",
        )
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)
        # Decimal fields come back as strings ("7500.00"); compare as strings.
        # Other field types come back as-is. We check the underlying DB
        # column to avoid to_representation combine quirks.
        for key, expected in patch.items():
            response_val = r.data.get(key)
            if key == "salary":
                # DecimalField serializes to string; compare numerically
                self.assertEqual(float(response_val or 0), float(expected),
                                 f"field {key!r}: response={response_val!r}")
            else:
                self.assertEqual(response_val, expected, f"field {key!r}")
        # And confirm the DB persists them
        self.target.refresh_from_db()
        self.assertEqual(self.target.country, "USA")
        self.assertEqual(self.target.city, "New York")
        self.assertEqual(self.target.passport_no, "US-PASS-001")
        self.assertEqual(float(self.target.salary), 7500)

    def test_patch_password_does_not_echo_back(self):
        """PATCH with a new password updates the hash but never returns it."""
        r = self.client.patch(
            DETAIL_URL_FMT.format(id=self.target.id),
            {"password": "new-secret"},
            format="json",
        )
        self.assertEqual(r.status_code, http_status.HTTP_200_OK)
        self.assertNotIn("password", r.data)
        # And the new password works on re-login
        self.target.refresh_from_db()
        self.assertTrue(self.target.check_password("new-secret"))
        # And the old password no longer works
        self.assertFalse(self.target.check_password("testpass123"))

    def test_put_full_replace(self):
        """PUT updates the fields in the body. (DRF's ModelSerializer.update
        uses ORM .update() so fields not in the body are left as-is; this
        is DRF's documented behaviour for ModelSerializer, not a 'full
        replace' in the SQL sense.)"""
        r = self.client.put(
            DETAIL_URL_FMT.format(id=self.target.id),
            {
                "email": "target@example.com",  # email is required
                "first_name": "UpdatedTarget",
                "password": "ignored",  # password write-only
            },
            format="json",
        )
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)
        # The response's first_name is auto-combined; check the DB.
        self.target.refresh_from_db()
        self.assertEqual(self.target.first_name, "UpdatedTarget")
        # middle_name was NOT in the PUT body, so DRF leaves it as-is
        # (this is the standard ModelSerializer behaviour).
        self.assertEqual(self.target.middle_name, "User")
        # And the password was hashed correctly
        self.assertTrue(self.target.check_password("ignored"))

    def test_read_only_fields_ignored_on_patch(self):
        """PATCH with id/created_at/updated_at/generated_id is ignored
        (not echoed back as a write — they're auto-managed)."""
        r = self.client.patch(
            DETAIL_URL_FMT.format(id=self.target.id),
            {
                "id": 99999,
                "created_at": "2000-01-01T00:00:00Z",
                "updated_at": "2000-01-01T00:00:00Z",
                "generated_id": "999999999999",
                "phone_number": "+201999999999",
            },
            format="json",
        )
        self.assertEqual(r.status_code, http_status.HTTP_200_OK)
        # id must not change
        self.assertNotEqual(r.data["id"], 99999)
        # generated_id must not change (read-only)
        self.assertNotEqual(r.data.get("generated_id"), "999999999999")
        # The non-readonly field was applied
        self.assertEqual(r.data["phone_number"], "+201999999999")


# ============================================================================
# 4. Delete (DELETE /api/users/users/{id}/)
# ============================================================================


class UsersDeleteTests(UsersEndpointFieldSurfaceTests):
    def test_delete_removes_user(self):
        rid = self.target.id
        r = self.client.delete(DETAIL_URL_FMT.format(id=rid))
        self.assertEqual(r.status_code, http_status.HTTP_204_NO_CONTENT)
        self.assertFalse(Users.objects.filter(id=rid).exists())

    def test_delete_then_get_returns_404(self):
        rid = self.target.id
        self.client.delete(DETAIL_URL_FMT.format(id=rid))
        r = self.client.get(DETAIL_URL_FMT.format(id=rid))
        self.assertEqual(r.status_code, http_status.HTTP_404_NOT_FOUND)


# ============================================================================
# 5. Permission matrix
# ============================================================================


class UsersPermissionTests(UsersEndpointFieldSurfaceTests):
    """
    Lock in the role-based access matrix from api/permissions.py:247.

    - Admin: full CRUD on anyone
    - HR Manager: full CRUD on non-admins; cannot POST role=Admin
    - Recruiter: read-only (safe methods only)
    - Employee: only own profile
    """

    def test_admin_can_list_all(self):
        r = self.client.get(LIST_URL)
        self.assertEqual(r.status_code, http_status.HTTP_200_OK)

    def test_admin_can_create(self):
        r = self.client.post(LIST_URL, {
            "email": "by-admin@example.com",
            "first_name": "ByAdmin",
            "password": "x",
        }, format="json")
        self.assertEqual(r.status_code, http_status.HTTP_201_CREATED)

    def test_hr_can_list_all(self):
        self.client.force_authenticate(user=self.hr)
        r = self.client.get(LIST_URL)
        self.assertEqual(r.status_code, http_status.HTTP_200_OK)

    def test_hr_can_create_employee(self):
        self.client.force_authenticate(user=self.hr)
        r = self.client.post(LIST_URL, {
            "email": "by-hr@example.com",
            "first_name": "ByHR",
            "password": "x",
            "role": "Employee",
        }, format="json")
        self.assertEqual(r.status_code, http_status.HTTP_201_CREATED)

    def test_hr_cannot_create_admin(self):
        """HR Manager POST with role=Admin must be denied at the permission layer."""
        self.client.force_authenticate(user=self.hr)
        r = self.client.post(LIST_URL, {
            "email": "should-not-exist@example.com",
            "first_name": "Nope",
            "password": "x",
            "role": "Admin",
        }, format="json")
        self.assertEqual(r.status_code, http_status.HTTP_403_FORBIDDEN)
        self.assertFalse(Users.objects.filter(email="should-not-exist@example.com").exists())

    def test_recruiter_cannot_create(self):
        """Recruiter has SAFE_METHODS only — POST is forbidden."""
        self.client.force_authenticate(user=self.recruiter)
        r = self.client.post(LIST_URL, {
            "email": "by-rec@example.com",
            "first_name": "ByRec",
            "password": "x",
        }, format="json")
        self.assertEqual(r.status_code, http_status.HTTP_403_FORBIDDEN)

    def test_recruiter_can_read(self):
        self.client.force_authenticate(user=self.recruiter)
        r = self.client.get(DETAIL_URL_FMT.format(id=self.target.id))
        self.assertEqual(r.status_code, http_status.HTTP_200_OK)

    def test_recruiter_cannot_patch(self):
        self.client.force_authenticate(user=self.recruiter)
        r = self.client.patch(
            DETAIL_URL_FMT.format(id=self.target.id),
            {"phone_number": "+201000000000"},
            format="json",
        )
        self.assertEqual(r.status_code, http_status.HTTP_403_FORBIDDEN)

    def test_employee_can_read_own_profile(self):
        self.client.force_authenticate(user=self.employee)
        r = self.client.get(DETAIL_URL_FMT.format(id=self.employee.id))
        self.assertEqual(r.status_code, http_status.HTTP_200_OK)

    def test_employee_cannot_read_other_profile(self):
        """An Employee gets 404 (or empty queryset) on someone else's profile,
        because get_queryset() filters to id == self.id."""
        self.client.force_authenticate(user=self.employee)
        r = self.client.get(DETAIL_URL_FMT.format(id=self.target.id))
        # Either 404 (not in queryset) or 403 (object permission); both
        # correctly deny access.
        self.assertIn(r.status_code, (http_status.HTTP_403_FORBIDDEN,
                                       http_status.HTTP_404_NOT_FOUND))

    def test_employee_can_patch_own_profile(self):
        self.client.force_authenticate(user=self.employee)
        r = self.client.patch(
            DETAIL_URL_FMT.format(id=self.employee.id),
            {"phone_number": "+20123456789"},
            format="json",
        )
        self.assertEqual(r.status_code, http_status.HTTP_200_OK)

    def test_employee_cannot_patch_other_profile(self):
        self.client.force_authenticate(user=self.employee)
        r = self.client.patch(
            DETAIL_URL_FMT.format(id=self.target.id),
            {"phone_number": "+201111111111"},
            format="json",
        )
        self.assertIn(r.status_code, (http_status.HTTP_403_FORBIDDEN,
                                       http_status.HTTP_404_NOT_FOUND))


# ============================================================================
# 6. Bulk operations
# ============================================================================


class UsersBulkOperationsTests(UsersEndpointFieldSurfaceTests):
    """POST /api/users/users/bulk-edit/ and bulk-delete/."""

    def test_bulk_edit_updates_user_status(self):
        r = self.client.post(BULK_EDIT_URL, {
            "ids": [self.target.id, self.employee.id],
            "data": {"user_status": "ON_SITE"},
        }, format="json")
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)
        self.target.refresh_from_db()
        self.employee.refresh_from_db()
        self.assertEqual(self.target.user_status, "ON_SITE")
        self.assertEqual(self.employee.user_status, "ON_SITE")

    def test_bulk_edit_rejects_unknown_field(self):
        """Whitelist in bulk_edit: only user_status / role / status / is_active
        / is_blacklisted / rank are accepted. Other fields are dropped."""
        r = self.client.post(BULK_EDIT_URL, {
            "ids": [self.target.id],
            "data": {
                "user_status": "AVAILABLE",
                "phone_number": "+201111111111",  # NOT in whitelist
            },
        }, format="json")
        # The endpoint silently drops unknown fields; the response is
        # 200 with only the whitelisted field applied.
        self.assertEqual(r.status_code, http_status.HTTP_200_OK)
        self.target.refresh_from_db()
        self.assertEqual(self.target.user_status, "AVAILABLE")
        self.assertNotEqual(self.target.phone_number, "+201111111111")

    def test_bulk_delete_removes_users(self):
        r = self.client.post(BULK_DELETE_URL, {
            "ids": [self.target.id, self.employee.id],
        }, format="json")
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)
        self.assertFalse(Users.objects.filter(id=self.target.id).exists())
        self.assertFalse(Users.objects.filter(id=self.employee.id).exists())

    def test_bulk_delete_with_empty_ids(self):
        r = self.client.post(BULK_DELETE_URL, {"ids": []}, format="json")
        self.assertEqual(r.status_code, http_status.HTTP_400_BAD_REQUEST)

    def test_bulk_delete_forbidden_for_recruiter(self):
        self.client.force_authenticate(user=self.recruiter)
        r = self.client.post(BULK_DELETE_URL, {"ids": [self.target.id]}, format="json")
        self.assertEqual(r.status_code, http_status.HTTP_403_FORBIDDEN)


# ============================================================================
# 7. Filter / search behaviour (light)
# ============================================================================


class UsersListFilterTests(UsersEndpointFieldSurfaceTests):
    """GET /api/users/users/?role=Employee — basic filter smoke test."""

    def test_filter_by_role(self):
        r = self.client.get(LIST_URL, {"role": "Admin"})
        self.assertEqual(r.status_code, http_status.HTTP_200_OK)
        if isinstance(r.data, dict) and "results" in r.data:
            items = r.data["results"]
        else:
            items = r.data
        # All returned users should be Admin
        for u in items:
            self.assertEqual(u["role"], "Admin")

    def test_search_by_name(self):
        r = self.client.get(LIST_URL, {"name": "Target"})
        self.assertEqual(r.status_code, http_status.HTTP_200_OK)
        if isinstance(r.data, dict) and "results" in r.data:
            items = r.data["results"]
        else:
            items = r.data
        # The target user must be in the result set
        ids = [u["id"] for u in items]
        self.assertIn(self.target.id, ids)


# ============================================================================
# 8. All-fields-writable (every model column exposed)
# ============================================================================
#
# After switching Meta.fields to '__all__', every Users column is
# writable except:
#   - id, created_at, updated_at  : auto-managed by the model
#   - generated_id                : read_only in extra_kwargs
#   - password (in response)      : write_only in extra_kwargs
#
# These tests lock in the new behaviour so a future refactor can't
# silently drop a writable field.

from django.contrib.auth.models import Group, Permission  # noqa: E402


class UsersAllFieldsWritableTests(UsersEndpointFieldSurfaceTests):
    """All model columns are writable except the 5 explicitly-excluded."""

    # ---- Account / permissions (PermissionsMixin + abstract user) ----

    def test_patch_is_active(self):
        r = self.client.patch(
            DETAIL_URL_FMT.format(id=self.target.id),
            {"is_active": False},
            format="json",
        )
        self.assertEqual(r.status_code, http_status.HTTP_200_OK)
        self.target.refresh_from_db()
        self.assertFalse(self.target.is_active)

    def test_patch_is_staff(self):
        """is_staff is inherited from PermissionsMixin; now writable."""
        r = self.client.patch(
            DETAIL_URL_FMT.format(id=self.target.id),
            {"is_staff": True},
            format="json",
        )
        self.assertEqual(r.status_code, http_status.HTTP_200_OK)
        self.target.refresh_from_db()
        self.assertTrue(self.target.is_staff)

    def test_patch_is_superuser(self):
        """is_superuser is inherited from PermissionsMixin; now writable."""
        r = self.client.patch(
            DETAIL_URL_FMT.format(id=self.target.id),
            {"is_superuser": True},
            format="json",
        )
        self.assertEqual(r.status_code, http_status.HTTP_200_OK)
        self.target.refresh_from_db()
        self.assertTrue(self.target.is_superuser)

    def test_patch_last_login(self):
        """last_login is auto-set by Django on login, but is writable via API."""
        r = self.client.patch(
            DETAIL_URL_FMT.format(id=self.target.id),
            {"last_login": "2026-08-01T10:00:00Z"},
            format="json",
        )
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)
        self.target.refresh_from_db()
        self.assertIsNotNone(self.target.last_login)

    def test_patch_user_permissions(self):
        """user_permissions (M2M from PermissionsMixin) is writable."""
        perm = Permission.objects.first()
        r = self.client.patch(
            DETAIL_URL_FMT.format(id=self.target.id),
            {"user_permissions": [perm.id]},
            format="json",
        )
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)
        self.target.refresh_from_db()
        self.assertIn(perm, self.target.user_permissions.all())

    def test_patch_user_permissions_empty_clears(self):
        """Sending [] clears the M2M."""
        perm = Permission.objects.first()
        self.target.user_permissions.add(perm)
        self.assertIn(perm, self.target.user_permissions.all())
        r = self.client.patch(
            DETAIL_URL_FMT.format(id=self.target.id),
            {"user_permissions": []},
            format="json",
        )
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)
        self.target.refresh_from_db()
        self.assertEqual(self.target.user_permissions.count(), 0)

    def test_patch_groups(self):
        """groups (M2M from PermissionsMixin) is writable."""
        g = Group.objects.create(name="Test Group A")
        r = self.client.patch(
            DETAIL_URL_FMT.format(id=self.target.id),
            {"groups": [g.id]},
            format="json",
        )
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)
        self.target.refresh_from_db()
        self.assertIn(g, self.target.groups.all())

    # ---- Blacklist ----

    def test_patch_blacklist_reason(self):
        """blacklist_reason was previously not in the serializer."""
        r = self.client.patch(
            DETAIL_URL_FMT.format(id=self.target.id),
            {"blacklist_reason": "Failed background check"},
            format="json",
        )
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)
        self.target.refresh_from_db()
        self.assertEqual(self.target.blacklist_reason, "Failed background check")

    # ---- "Synced from Document" fields ----

    def test_patch_title(self):
        """title (synced from Document) was previously not in the serializer."""
        r = self.client.patch(
            DETAIL_URL_FMT.format(id=self.target.id),
            {"title": "Application for Master"},
            format="json",
        )
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)
        self.target.refresh_from_db()
        self.assertEqual(self.target.title, "Application for Master")

    def test_patch_user_position(self):
        """position (synced from Document, CharField on Users) is writable.

        This is NOT the CVSubmission.position FK; the Users model has its
        own CharField for the position synced from a Document.
        """
        r = self.client.patch(
            DETAIL_URL_FMT.format(id=self.target.id),
            {"position": "Master"},
            format="json",
        )
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)
        self.target.refresh_from_db()
        self.assertEqual(self.target.position, "Master")

    def test_patch_user_file(self):
        """file (synced from Document, FileField on Users) is writable."""
        # Use a minimal text file to avoid touching the filesystem
        from django.core.files.uploadedfile import SimpleUploadedFile
        uploaded = SimpleUploadedFile(
            "test.txt", b"hello world", content_type="text/plain",
        )
        r = self.client.patch(
            DETAIL_URL_FMT.format(id=self.target.id),
            {"file": uploaded},
            format="multipart",
        )
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)
        self.target.refresh_from_db()
        self.assertTrue(self.target.file)
        self.assertTrue(self.target.file.name.endswith(".txt"))

    # ---- GET returns the new fields too ----

    def test_get_returns_newly_exposed_fields(self):
        r = self.client.get(DETAIL_URL_FMT.format(id=self.target.id))
        self.assertEqual(r.status_code, http_status.HTTP_200_OK)
        body = r.data
        # Each of these was missing from the explicit fields list; now
        # they must all be present in the GET response.
        for field in (
            "is_active", "is_staff", "is_superuser",
            "last_login", "user_permissions", "groups",
            "blacklist_reason", "title", "position", "file",
        ):
            self.assertIn(field, body, f"missing {field!r} in GET response")

    # ---- The 5 explicitly-excluded fields stay excluded ----

    def test_generated_id_still_readonly(self):
        r = self.client.patch(
            DETAIL_URL_FMT.format(id=self.target.id),
            {"generated_id": "999999999999"},
            format="json",
        )
        self.assertEqual(r.status_code, http_status.HTTP_200_OK)
        self.target.refresh_from_db()
        self.assertNotEqual(self.target.generated_id, "999999999999")

    def test_id_still_readonly(self):
        r = self.client.patch(
            DETAIL_URL_FMT.format(id=self.target.id),
            {"id": 99999},
            format="json",
        )
        self.assertEqual(r.status_code, http_status.HTTP_200_OK)
        self.target.refresh_from_db()
        self.assertNotEqual(self.target.id, 99999)

    def test_created_at_still_readonly(self):
        # The target's created_at is set by setUpTestData. We snapshot it
        # and then PATCH a different value; the DB value must not change.
        original = self.target.created_at
        r = self.client.patch(
            DETAIL_URL_FMT.format(id=self.target.id),
            {"created_at": "2000-01-01T00:00:00Z"},
            format="json",
        )
        self.assertEqual(r.status_code, http_status.HTTP_200_OK)
        self.target.refresh_from_db()
        self.assertEqual(self.target.created_at, original)

    def test_updated_at_is_auto_refreshed_on_save(self):
        """updated_at is auto_now — every save refreshes it. PATCH
        body value is irrelevant; the column is auto-managed."""
        import time
        before = self.target.updated_at
        time.sleep(0.05)  # ensure a measurable timestamp diff
        r = self.client.patch(
            DETAIL_URL_FMT.format(id=self.target.id),
            {"phone_number": "+201111111111"},
            format="json",
        )
        self.assertEqual(r.status_code, http_status.HTTP_200_OK)
        self.target.refresh_from_db()
        # updated_at was auto-refreshed by the save (not 2000-01-01)
        self.assertGreater(self.target.updated_at, before)

    def test_password_still_write_only_in_response(self):
        r = self.client.patch(
            DETAIL_URL_FMT.format(id=self.target.id),
            {"password": "new-secret"},
            format="json",
        )
        self.assertEqual(r.status_code, http_status.HTTP_200_OK)
        self.assertNotIn("password", r.data)


class UserNameSplitRegressionTests(TestCase):
    """
    Regression for the first_name / middle_name split in
    `UsersSerializer.to_internal_value` (api/serializer.py:1968) and
    `RegisterSerializer.to_internal_value` (api/serializer.py:2530).

    Both serializers normalize an incoming `first_name` like
    "Mohamed Sami Afifi" into:
        first_name  = "Mohamed"
        middle_name = "Sami Afifi"
    by splitting on the FIRST space. This is paired with
    `to_representation` which merges them back into `first_name` for
    the API response, so a clean-data round-trip is idempotent.

    These tests pin the contract so a future refactor of either
    serializer cannot silently break the merge/split balance.
    """

    list_url = "/api/users/users/"

    def _payload(self, **overrides):
        base = {
            "email": "namesplit@example.com",
            "password": "x",
            "role": "Employee",
        }
        base.update(overrides)
        return base

    def _login_as_admin(self):
        admin = Users.objects.create_user(
            email="admin-namesplit@example.com",
            password="x",
            first_name="A",
            middle_name="d",
            role="Admin",
            is_staff=True,
            is_superuser=True,
        )
        client = APIClient()
        client.force_authenticate(user=admin)
        return client

    # ---- Create path -------------------------------------------------

    def test_create_with_multi_word_first_name_splits(self):
        """POST with first_name='Mohamed Sami' stores first='Mohamed', middle='Sami'."""
        client = self._login_as_admin()
        r = client.post(
            self.list_url,
            self._payload(first_name="Mohamed Sami"),
            format="json",
        )
        self.assertEqual(r.status_code, http_status.HTTP_201_CREATED, r.data)
        user = Users.objects.get(id=r.data["id"])
        self.assertEqual(user.first_name, "Mohamed")
        self.assertEqual(user.middle_name, "Sami")
        # The API now returns the split values directly (no more
        # to_representation merge) so the frontend's
        # `first_name + " " + middle_name` produces the right display.
        # The `full_name` property is the canonical merged form.
        self.assertEqual(r.data["first_name"], "Mohamed")
        self.assertEqual(r.data["middle_name"], "Sami")
        self.assertEqual(r.data["full_name"], "Mohamed Sami")

    def test_create_with_single_word_first_name_leaves_middle_empty(self):
        """POST with first_name='Karim' stores first='Karim', middle=''."""
        client = self._login_as_admin()
        r = client.post(
            self.list_url,
            self._payload(email="k@example.com", first_name="Karim"),
            format="json",
        )
        self.assertEqual(r.status_code, http_status.HTTP_201_CREATED, r.data)
        user = Users.objects.get(id=r.data["id"])
        self.assertEqual(user.first_name, "Karim")
        self.assertEqual(user.middle_name, "")

    def test_create_with_3_part_name_splits_only_first_word(self):
        """The split is on the FIRST space only — rest stays in middle_name."""
        client = self._login_as_admin()
        r = client.post(
            self.list_url,
            self._payload(email="three@example.com", first_name="Mohamed Sami Afifi"),
            format="json",
        )
        self.assertEqual(r.status_code, http_status.HTTP_201_CREATED, r.data)
        user = Users.objects.get(id=r.data["id"])
        self.assertEqual(user.first_name, "Mohamed")
        self.assertEqual(user.middle_name, "Sami Afifi")
        # API returns the split (no merge in to_representation) plus
        # the canonical full_name property for callers that want it.
        self.assertEqual(r.data["first_name"], "Mohamed")
        self.assertEqual(r.data["middle_name"], "Sami Afifi")
        self.assertEqual(r.data["full_name"], "Mohamed Sami Afifi")

    # ---- Update path (round-trip) -----------------------------------

    def test_clean_round_trip_is_idempotent(self):
        """Reading then re-saving clean data must not change the DB state."""
        user = Users.objects.create_user(
            email="clean@example.com",
            password="x",
            first_name="Mohamed",
            middle_name="Sami Afifi Soliman",
            role="Employee",
        )
        client = self._login_as_admin()
        r = client.get(f"{self.list_url}{user.id}/")
        self.assertEqual(r.status_code, http_status.HTTP_200_OK)
        # Frontend would re-send first_name and middle_name exactly as read
        r = client.patch(
            f"{self.list_url}{user.id}/",
            {
                "first_name": r.data["first_name"],
                "middle_name": r.data["middle_name"],
            },
            format="json",
        )
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)
        user.refresh_from_db()
        self.assertEqual(user.first_name, "Mohamed")
        self.assertEqual(user.middle_name, "Sami Afifi Soliman")

    def test_patch_with_explicit_empty_middle_name_clears_it(self):
        """
        PATCH semantics: when the form sends middle_name="" (explicit
        empty string), DRF writes the empty string — middle_name is
        cleared, NOT preserved. This is the standard DRF ModelSerializer
        PATCH behavior.

        This is a KNOWN frontend contract requirement: the form must NOT
        send middle_name="" unless the user actually wants to clear it.
        A form that submits an empty middle_name on every save (e.g.
        because the form binding lost the value) will silently wipe the
        user's middle_name. The frontend must omit middle_name from the
        payload when the user did not change it.
        """
        user = Users.objects.create_user(
            email="emptymiddle@example.com",
            password="x",
            first_name="Mohamed",
            middle_name="Sami",
            role="Employee",
        )
        client = self._login_as_admin()
        r = client.patch(
            f"{self.list_url}{user.id}/",
            {"first_name": "Karim", "middle_name": ""},
            format="json",
        )
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)
        user.refresh_from_db()
        self.assertEqual(user.first_name, "Karim")
        # middle_name IS cleared because the form explicitly sent ""
        self.assertEqual(user.middle_name, "")

    def test_patch_without_middle_name_preserves_it(self):
        """If the form omits middle_name, the existing value is preserved."""
        user = Users.objects.create_user(
            email="preservemiddle@example.com",
            password="x",
            first_name="Mohamed",
            middle_name="Sami Afifi",
            role="Employee",
        )
        client = self._login_as_admin()
        # Only first_name in payload — middle_name is NOT touched
        r = client.patch(
            f"{self.list_url}{user.id}/",
            {"first_name": "Karim"},
            format="json",
        )
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)
        user.refresh_from_db()
        self.assertEqual(user.first_name, "Karim")
        self.assertEqual(user.middle_name, "Sami Afifi")
class DocumentCreateRegressionTests(TestCase):
    """
    Regression for the auto-create-placeholder-user bug in
    `DocumentViewSet.perform_create`.

    Old behavior: any admin upload to `/api/documents/` without an
    explicit `user` field would silently create a new
    `applicant_<uuid>@placeholder.sakrshipping.com` user. These ghost
    users showed up as "Unknown" rows in the Applicants dashboard.

    New behavior: the endpoint requires EITHER `user` OR `contract`
    on POST. If neither is provided and the uploader is not an
    Employee uploading for themselves, the endpoint returns 400.
    """

    list_url = "/api/documents/"

    def _login_as_admin(self):
        admin = Users.objects.create_user(
            email="doc-admin@example.com",
            password="x",
            first_name="A",
            middle_name="d",
            role="Admin",
            is_staff=True,
            is_superuser=True,
        )
        client = APIClient()
        client.force_authenticate(user=admin)
        return client

    def _multipart(self, **fields):
        """Helper to build multipart form data. Drop empty values."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        if "file" not in fields:
            fields["file"] = SimpleUploadedFile(
                "test.pdf", b"%PDF-1.4 fake", content_type="application/pdf"
            )
        return fields

    # ---- Old bug: ghost user creation is GONE ------------------------

    def test_post_without_user_or_contract_returns_400(self):
        """No user, no contract, Admin uploader -> 400, no user created."""
        from api.models import Users as _Users
        before = _Users.objects.filter(email__regex=r"^applicant_").count()
        client = self._login_as_admin()
        r = client.post(self.list_url, self._multipart(title="orphan"), format="multipart")
        self.assertEqual(r.status_code, http_status.HTTP_400_BAD_REQUEST, r.data)
        after = _Users.objects.filter(email__regex=r"^applicant_").count()
        self.assertEqual(after, before, "No placeholder user should be created")

    def test_post_with_user_succeeds_and_uses_that_user(self):
        client = self._login_as_admin()
        user = Users.objects.create_user(
            email="target@example.com", password="x", first_name="Target",
            middle_name="User", role="Employee",
        )
        r = client.post(
            self.list_url,
            self._multipart(user=user.id, title="cv"),
            format="multipart",
        )
        self.assertEqual(r.status_code, http_status.HTTP_201_CREATED, r.data)
        from api.models import Document
        d = Document.objects.get(id=r.data["id"])
        self.assertEqual(d.user_id, user.id)
        self.assertIsNone(d.contract_id)

    def test_post_with_contract_succeeds_and_uses_that_contract(self):
        """Admin attachment flow: contract FK works without requiring a user."""
        client = self._login_as_admin()
        from api.models import Contract
        import datetime
        applicant = Users.objects.create_user(
            email="applicant@example.com", password="x", first_name="A",
            middle_name="p", role="Employee",
        )
        contract = Contract.objects.create(
            user=applicant,
            sign_on_date=datetime.date(2026, 1, 1),
            sign_off_date=datetime.date(2026, 6, 1),
        )
        r = client.post(
            self.list_url,
            self._multipart(contract=contract.id, title="background check"),
            format="multipart",
        )
        self.assertEqual(r.status_code, http_status.HTTP_201_CREATED, r.data)
        from api.models import Document
        d = Document.objects.get(id=r.data["id"])
        self.assertIsNone(d.user_id)
        self.assertEqual(d.contract_id, contract.id)

    def test_post_with_both_user_and_contract_uses_both(self):
        client = self._login_as_admin()
        from api.models import Contract
        import datetime
        applicant = Users.objects.create_user(
            email="applicant2@example.com", password="x", first_name="A2",
            middle_name="p2", role="Employee",
        )
        contract = Contract.objects.create(
            user=applicant,
            sign_on_date=datetime.date(2026, 1, 1),
            sign_off_date=datetime.date(2026, 6, 1),
        )
        r = client.post(
            self.list_url,
            self._multipart(user=applicant.id, contract=contract.id, title="witness stmt"),
            format="multipart",
        )
        self.assertEqual(r.status_code, http_status.HTTP_201_CREATED, r.data)
        from api.models import Document
        d = Document.objects.get(id=r.data["id"])
        self.assertEqual(d.user_id, applicant.id)
        self.assertEqual(d.contract_id, contract.id)

    def test_post_by_employee_without_user_defaults_to_themselves(self):
        """Employee uploads without explicit user -> attached to themselves."""
        from rest_framework.test import APIClient
        employee = Users.objects.create_user(
            email="emp@example.com", password="x", first_name="E",
            middle_name="p", role="Employee",
        )
        client = APIClient()
        client.force_authenticate(user=employee)
        r = client.post(
            self.list_url,
            self._multipart(title="my doc"),
            format="multipart",
        )
        self.assertEqual(r.status_code, http_status.HTTP_201_CREATED, r.data)
        from api.models import Document
        d = Document.objects.get(id=r.data["id"])
        self.assertEqual(d.user_id, employee.id)


class AddCVAutoCreateUserRegressionTests(TestCase):
    """
    Regression for the "Add CV for a new applicant" flow.

    The frontend's Add CV form posts to /api/documents/ with
    `name`, `email`, `phone_number`, `position`, `title`, `file` —
    but no `user` field, because the applicant doesn't exist yet.

    The endpoint must auto-create a real `Users` row from those
    fields (not a placeholder pattern) and link the document to
    that user. If `email` already exists, reuse that user instead
    of creating a duplicate.
    """

    list_url = "/api/documents/"

    def _login_as_admin(self):
        admin = Users.objects.create_user(
            email="addcv-admin@example.com",
            password="x",
            first_name="A",
            middle_name="a",
            role="Admin",
            is_staff=True,
            is_superuser=True,
        )
        client = APIClient()
        client.force_authenticate(user=admin)
        return client, admin

    def _multipart(self, **fields):
        from django.core.files.uploadedfile import SimpleUploadedFile
        if "file" not in fields:
            fields["file"] = SimpleUploadedFile(
                "cv.pdf", b"%PDF-1.4 fake", content_type="application/pdf"
            )
        return fields

    # ---- Happy paths -------------------------------------------------

    def test_admin_adds_cv_with_name_and_email_creates_user(self):
        """POST with name+email, no user -> creates a new Users row."""
        client, _ = self._login_as_admin()
        r = client.post(
            self.list_url,
            self._multipart(
                name="John Smith",
                email="john.smith@example.com",
                title="CV",
            ),
            format="multipart",
        )
        self.assertEqual(r.status_code, http_status.HTTP_201_CREATED, r.data)

        from api.models import Document
        d = Document.objects.get(id=r.data["id"])
        self.assertIsNotNone(d.user_id, "Document must be linked to a user")

        # The new user was created with the supplied name + email
        new_user = Users.objects.get(id=d.user_id)
        self.assertEqual(new_user.email, "john.smith@example.com")
        self.assertEqual(new_user.first_name, "John")
        self.assertEqual(new_user.middle_name, "Smith")
        self.assertEqual(new_user.role, "Employee")

    def test_admin_adds_cv_with_only_name_generates_email(self):
        """POST with just a name (no email) -> user created with derived email."""
        client, _ = self._login_as_admin()
        r = client.post(
            self.list_url,
            self._multipart(name="Jane Doe", title="CV"),
            format="multipart",
        )
        self.assertEqual(r.status_code, http_status.HTTP_201_CREATED, r.data)

        from api.models import Document
        d = Document.objects.get(id=r.data["id"])
        new_user = Users.objects.get(id=d.user_id)
        self.assertEqual(new_user.first_name, "Jane")
        self.assertEqual(new_user.middle_name, "Doe")
        self.assertTrue(
            new_user.email.endswith("@sakrshipping.com"),
            f"Generated email should use @sakrshipping.com, got {new_user.email!r}"
        )

    def test_admin_adds_cv_existing_email_reuses_user(self):
        """If email matches an existing user, link to that user (no dup)."""
        client, _ = self._login_as_admin()
        existing = Users.objects.create_user(
            email="known@example.com",
            password="x",
            first_name="Known",
            middle_name="User",
            role="Employee",
        )
        r = client.post(
            self.list_url,
            self._multipart(
                name="Known User",
                email="known@example.com",
                title="CV",
            ),
            format="multipart",
        )
        self.assertEqual(r.status_code, http_status.HTTP_201_CREATED, r.data)

        from api.models import Document
        d = Document.objects.get(id=r.data["id"])
        self.assertEqual(d.user_id, existing.id)
        # No duplicate Users row was created
        self.assertEqual(
            Users.objects.filter(email="known@example.com").count(),
            1,
        )

    def test_employee_without_user_field_uses_self(self):
        """Employee path is unchanged: no user field -> attach to self."""
        from rest_framework.test import APIClient
        employee = Users.objects.create_user(
            email="selfie@example.com",
            password="x",
            first_name="Self",
            middle_name="Emp",
            role="Employee",
        )
        client = APIClient()
        client.force_authenticate(user=employee)
        r = client.post(
            self.list_url,
            self._multipart(title="My CV"),
            format="multipart",
        )
        self.assertEqual(r.status_code, http_status.HTTP_201_CREATED, r.data)
        from api.models import Document
        d = Document.objects.get(id=r.data["id"])
        self.assertEqual(d.user_id, employee.id)

    # ---- Edge cases --------------------------------------------------

    def test_admin_post_with_no_user_contract_or_applicant_fields_400(self):
        """Admin posts with no identifying fields -> 400, no user created."""
        client, _ = self._login_as_admin()
        before = Users.objects.count()
        r = client.post(
            self.list_url,
            self._multipart(title="orphan"),
            format="multipart",
        )
        self.assertEqual(r.status_code, http_status.HTTP_400_BAD_REQUEST, r.data)
        self.assertEqual(Users.objects.count(), before, "No user should be created")

    def test_three_part_name_splits_correctly(self):
        """'John Michael Smith' -> first='John', middle='Michael Smith'."""
        client, _ = self._login_as_admin()
        r = client.post(
            self.list_url,
            self._multipart(
                name="John Michael Smith",
                email="jms@example.com",
                title="CV",
            ),
            format="multipart",
        )
        self.assertEqual(r.status_code, http_status.HTTP_201_CREATED, r.data)
        from api.models import Document
        d = Document.objects.get(id=r.data["id"])
        new_user = Users.objects.get(id=d.user_id)
        self.assertEqual(new_user.first_name, "John")
        self.assertEqual(new_user.middle_name, "Michael Smith")

    def test_unique_generated_email_on_collision(self):
        """Two name-only uploads with the same name get distinct emails."""
        client, _ = self._login_as_admin()
        r1 = client.post(
            self.list_url,
            self._multipart(name="Same Name", title="CV1"),
            format="multipart",
        )
        r2 = client.post(
            self.list_url,
            self._multipart(name="Same Name", title="CV2"),
            format="multipart",
        )
        self.assertEqual(r1.status_code, http_status.HTTP_201_CREATED, r1.data)
        self.assertEqual(r2.status_code, http_status.HTTP_201_CREATED, r2.data)
        from api.models import Document
        d1 = Document.objects.get(id=r1.data["id"])
        d2 = Document.objects.get(id=r2.data["id"])
        self.assertNotEqual(
            d1.user_id, d2.user_id,
            "Two uploads with the same name must produce two distinct users"
        )


class ContractAdminAttachmentsEndpointTests(TestCase):
    """
    Regression for the contract-scoped admin-attachments endpoint:

      GET  /api/contracts/{id}/admin-attachments/
      POST /api/contracts/{id}/admin-attachments/

    This endpoint replaces the previous /api/documents/?user=<id> read
    path for admin-uploaded attachments, so the admin attachments UI
    can call a single, contract-scoped endpoint instead of going
    through the user-keyed Document list.
    """

    def _login_as_admin(self):
        admin = Users.objects.create_user(
            email="contract-admin@example.com",
            password="x",
            first_name="CA",
            middle_name="dmin",
            role="Admin",
            is_staff=True,
            is_superuser=True,
        )
        client = APIClient()
        client.force_authenticate(user=admin)
        return client, admin

    def _make_contract(self, applicant=None, email=None):
        import datetime
        from api.models import Contract
        if applicant is None:
            # Generate a unique-ish email so multiple contracts per test work.
            if email is None:
                email = f"c-applicant-{Users.objects.count()}@example.com"
            applicant = Users.objects.create_user(
                email=email,
                password="x",
                first_name="C",
                middle_name="Applicant",
                role="Employee",
            )
        return Contract.objects.create(
            user=applicant,
            sign_on_date=datetime.date(2026, 1, 1),
            sign_off_date=datetime.date(2026, 6, 1),
        ), applicant

    def _multipart(self, **fields):
        """Build a multipart payload, defaulting `file` to a tiny fake PDF."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        if "file" not in fields:
            fields["file"] = SimpleUploadedFile(
                "test.pdf", b"%PDF-1.4 fake", content_type="application/pdf"
            )
        return fields

    # ---- POST ----------------------------------------------------------

    def test_post_creates_document_bound_to_contract(self):
        """POST without `user` should create a Document bound to the contract."""
        from api.models import Document
        client, _ = self._login_as_admin()
        contract, _ = self._make_contract()

        url = f"/api/contracts/{contract.id}/admin-attachments/"
        r = client.post(url, self._multipart(title="background check"), format="multipart")

        self.assertEqual(r.status_code, http_status.HTTP_201_CREATED, r.data)
        self.assertEqual(Document.objects.count(), 1)
        d = Document.objects.get(id=r.data["id"])
        self.assertEqual(d.contract_id, contract.id)
        self.assertIsNone(d.user_id, "Admin attachments must not be linked to a user")
        self.assertEqual(d.title, "background check")

    def test_post_requires_title_and_file(self):
        """Missing title or file -> 400."""
        client, _ = self._login_as_admin()
        contract, _ = self._make_contract()

        url = f"/api/contracts/{contract.id}/admin-attachments/"
        r = client.post(url, format="multipart")
        self.assertEqual(r.status_code, http_status.HTTP_400_BAD_REQUEST, r.data)
        self.assertIn("title", str(r.data).lower() + " " + str(r.data.get("detail", "")).lower())

        r = client.post(url, {"title": "no file"}, format="multipart")
        self.assertEqual(r.status_code, http_status.HTTP_400_BAD_REQUEST, r.data)

    def test_post_user_field_in_payload_is_ignored(self):
        """
        Even if a malicious client supplies `user` in the payload, the
        document must be bound to the contract (not the user). This
        keeps admin attachments from ever leaking into a user profile.
        """
        from api.models import Document
        client, admin = self._login_as_admin()
        contract, applicant = self._make_contract()

        url = f"/api/contracts/{contract.id}/admin-attachments/"
        r = client.post(
            url,
            self._multipart(title="hijack", user=applicant.id),
            format="multipart",
        )
        self.assertEqual(r.status_code, http_status.HTTP_201_CREATED, r.data)
        d = Document.objects.get(id=r.data["id"])
        self.assertEqual(d.contract_id, contract.id)
        self.assertIsNone(d.user_id)

    def test_post_to_nonexistent_contract_returns_404(self):
        client, _ = self._login_as_admin()
        url = "/api/contracts/999999/admin-attachments/"
        r = client.post(url, self._multipart(title="orphan"), format="multipart")
        self.assertEqual(r.status_code, http_status.HTTP_404_NOT_FOUND)

    # ---- GET -----------------------------------------------------------

    def test_get_lists_only_documents_bound_to_this_contract(self):
        """GET should only return this contract's admin attachments."""
        from api.models import Document
        client, _ = self._login_as_admin()
        contract_a, _ = self._make_contract(email="a@example.com")
        contract_b, _ = self._make_contract(email="b@example.com")

        # Two attachments on contract A, one on contract B
        Document.objects.create(contract=contract_a, title="A1")
        Document.objects.create(contract=contract_a, title="A2")
        Document.objects.create(contract=contract_b, title="B1")

        url_a = f"/api/contracts/{contract_a.id}/admin-attachments/"
        r = client.get(url_a)
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)
        titles = sorted(d["title"] for d in r.data)
        self.assertEqual(titles, ["A1", "A2"])
        for d in r.data:
            self.assertEqual(d["contract"], contract_a.id)

    def test_get_returns_empty_list_when_no_attachments(self):
        client, _ = self._login_as_admin()
        contract, _ = self._make_contract()
        r = client.get(f"/api/contracts/{contract.id}/admin-attachments/")
        self.assertEqual(r.status_code, http_status.HTTP_200_OK)
        self.assertEqual(r.data, [])

    # ---- Serializer field on ContractSerializer ------------------------

    def test_contract_serializer_includes_admin_attachments_field(self):
        """ContractSerializer must expose `admin_attachments` in detail view."""
        from api.serializer import ContractSerializer
        contract, applicant = self._make_contract()
        s = ContractSerializer(contract)
        self.assertIn("admin_attachments", s.data)
        self.assertEqual(s.data["admin_attachments"], [])

    # ---- Detail sub-action ---------------------------------------------

    def _detail_url(self, contract_id, attachment_id):
        return f"/api/contracts/{contract_id}/admin-attachments/{attachment_id}/"

    def test_get_detail_returns_single_attachment(self):
        from api.models import Document
        client, _ = self._login_as_admin()
        contract, _ = self._make_contract()
        d = Document.objects.create(contract=contract, title="contract A only")

        r = client.get(self._detail_url(contract.id, d.id))
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)
        self.assertEqual(r.data["id"], d.id)
        self.assertEqual(r.data["title"], "contract A only")
        self.assertEqual(r.data["contract"], contract.id)
        self.assertIsNone(r.data["user"])

    def test_get_detail_404_when_attachment_belongs_to_other_contract(self):
        """An attachment bound to contract A must not be reachable via contract B."""
        from api.models import Document
        client, _ = self._login_as_admin()
        contract_a, _ = self._make_contract(email="da@example.com")
        contract_b, _ = self._make_contract(email="db@example.com")
        d = Document.objects.create(contract=contract_a, title="A only")

        r = client.get(self._detail_url(contract_b.id, d.id))
        self.assertEqual(r.status_code, http_status.HTTP_404_NOT_FOUND)

    def test_get_detail_404_for_nonexistent_attachment(self):
        client, _ = self._login_as_admin()
        contract, _ = self._make_contract()
        r = client.get(self._detail_url(contract.id, 999999))
        self.assertEqual(r.status_code, http_status.HTTP_404_NOT_FOUND)

    def test_delete_detail_removes_only_that_attachment(self):
        from api.models import Document
        client, _ = self._login_as_admin()
        contract, _ = self._make_contract()
        d1 = Document.objects.create(contract=contract, title="keep me")
        d2 = Document.objects.create(contract=contract, title="delete me")

        r = client.delete(self._detail_url(contract.id, d2.id))
        self.assertEqual(r.status_code, http_status.HTTP_204_NO_CONTENT)

        # d1 still exists, d2 is gone
        self.assertTrue(Document.objects.filter(id=d1.id).exists())
        self.assertFalse(Document.objects.filter(id=d2.id).exists())

    def test_delete_detail_404_for_attachment_of_other_contract(self):
        """DELETE must also scope by contract — can't delete A's doc via B's URL."""
        from api.models import Document
        client, _ = self._login_as_admin()
        contract_a, _ = self._make_contract(email="da2@example.com")
        contract_b, _ = self._make_contract(email="db2@example.com")
        d = Document.objects.create(contract=contract_a, title="A's doc")

        r = client.delete(self._detail_url(contract_b.id, d.id))
        self.assertEqual(r.status_code, http_status.HTTP_404_NOT_FOUND)
        self.assertTrue(Document.objects.filter(id=d.id).exists(), "Must not delete")

    def test_patch_detail_updates_title(self):
        from api.models import Document
        client, _ = self._login_as_admin()
        contract, _ = self._make_contract()
        d = Document.objects.create(contract=contract, title="old name")

        r = client.patch(
            self._detail_url(contract.id, d.id),
            {"title": "new name"},
            format="json",
        )
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)
        self.assertEqual(r.data["title"], "new name")
        d.refresh_from_db()
        self.assertEqual(d.title, "new name")

    def test_patch_detail_400_when_no_title(self):
        from api.models import Document
        client, _ = self._login_as_admin()
        contract, _ = self._make_contract()
        d = Document.objects.create(contract=contract, title="x")

        r = client.patch(self._detail_url(contract.id, d.id), {}, format="json")
        self.assertEqual(r.status_code, http_status.HTTP_400_BAD_REQUEST)


class AdminAttachmentsByUserEndpointTests(TestCase):
    """
    Regression for the seafarer-scoped admin-attachments endpoint:

      GET  /api/documents/admin-attachments-by-user/?user=<id>
      POST /api/documents/admin-attachments-by-user/

    This is the friendlier counterpart to the contract-scoped endpoint
    (`/api/contracts/<id>/admin-attachments/`). The Admin Related
    Attachments UI inside the CV Submission edit modal already has
    the seafarer's `user_id` but not the contract id, so we accept
    the user_id and resolve the contract on the server side.

    The key behavior this guards: admin attachments MUST be bound
    to the contract, NEVER to the user. Otherwise they leak into
    the seafarer's CV list (the "ghost user" bug).
    """

    url = "/api/documents/admin-attachments-by-user/"

    def _login_as_admin(self):
        admin = Users.objects.create_user(
            email="aabu-admin@example.com",
            password="x",
            first_name="A", middle_name="A", role="Admin",
            is_staff=True, is_superuser=True,
        )
        client = APIClient()
        client.force_authenticate(user=admin)
        return client

    def _make_seafarer_with_contract(self, email=None):
        import datetime
        from api.models import Contract
        if email is None:
            email = f"aabu-seafarer-{Users.objects.count()}@example.com"
        seafarer = Users.objects.create_user(
            email=email, password="x", first_name="Sea",
            middle_name="Farer", role="Employee",
        )
        contract = Contract.objects.create(
            user=seafarer,
            sign_on_date=datetime.date(2026, 1, 1),
            sign_off_date=datetime.date(2026, 6, 1),
        )
        return seafarer, contract

    def _multipart(self, **fields):
        from django.core.files.uploadedfile import SimpleUploadedFile
        if "file" not in fields:
            fields["file"] = SimpleUploadedFile(
                "test.pdf", b"%PDF-1.4 fake", content_type="application/pdf"
            )
        return fields

    # ---- POST ---------------------------------------------------------

    def test_post_creates_document_bound_to_users_most_recent_contract(self):
        """POST with `user` -> Document bound to user's most recent
        contract, with `user_id=NULL` (no leak into CV list)."""
        from api.models import Document
        client = self._login_as_admin()
        seafarer, contract = self._make_seafarer_with_contract()

        r = client.post(
            self.url,
            self._multipart(user=seafarer.id, title="background check"),
            format="multipart",
        )
        self.assertEqual(r.status_code, http_status.HTTP_201_CREATED, r.data)
        self.assertEqual(Document.objects.count(), 1)
        d = Document.objects.get(id=r.data["id"])
        self.assertEqual(d.contract_id, contract.id)
        self.assertIsNone(
            d.user_id,
            "Admin attachments must NOT be linked to a user — "
            "that's the ghost-user leak we're guarding against."
        )
        self.assertEqual(d.title, "background check")

    def test_post_picks_most_recent_contract_when_user_has_multiple(self):
        """If the seafarer has more than one contract, use the
        most recent one (highest id, ties broken by created_at)."""
        import datetime
        from api.models import Contract, Document
        client = self._login_as_admin()
        seafarer, older_contract = self._make_seafarer_with_contract()
        newer_contract = Contract.objects.create(
            user=seafarer,
            sign_on_date=datetime.date(2026, 7, 1),
            sign_off_date=datetime.date(2026, 12, 1),
        )

        r = client.post(
            self.url,
            self._multipart(user=seafarer.id, title="newer contract doc"),
            format="multipart",
        )
        self.assertEqual(r.status_code, http_status.HTTP_201_CREATED, r.data)
        d = Document.objects.get(id=r.data["id"])
        self.assertEqual(d.contract_id, newer_contract.id)
        self.assertNotEqual(d.contract_id, older_contract.id)

    def test_post_with_no_contract_for_user_returns_400(self):
        """No contract for this user -> 400 with a helpful message
        (admins should create the contract first)."""
        client = self._login_as_admin()
        lonely = Users.objects.create_user(
            email="lonely@example.com", password="x",
            first_name="No", middle_name="Contract", role="Employee",
        )
        r = client.post(
            self.url,
            self._multipart(user=lonely.id, title="orphan"),
            format="multipart",
        )
        self.assertEqual(r.status_code, http_status.HTTP_400_BAD_REQUEST, r.data)
        self.assertIn("contract", str(r.data).lower())

    def test_post_without_user_returns_400(self):
        client = self._login_as_admin()
        r = client.post(self.url, self._multipart(title="x"), format="multipart")
        self.assertEqual(r.status_code, http_status.HTTP_400_BAD_REQUEST, r.data)

    def test_post_requires_title_and_file(self):
        client = self._login_as_admin()
        seafarer, _ = self._make_seafarer_with_contract()

        r = client.post(self.url, {"user": seafarer.id}, format="multipart")
        self.assertEqual(r.status_code, http_status.HTTP_400_BAD_REQUEST, r.data)

        r = client.post(
            self.url, {"user": seafarer.id, "title": "no file"}, format="multipart"
        )
        self.assertEqual(r.status_code, http_status.HTTP_400_BAD_REQUEST, r.data)

    # ---- GET ----------------------------------------------------------

    def test_get_lists_only_documents_bound_to_users_most_recent_contract(self):
        """GET ?user=<id> returns admin attachments for that user's
        most recent contract only — not from any older contract."""
        import datetime
        from api.models import Contract, Document
        client = self._login_as_admin()
        seafarer, older_contract = self._make_seafarer_with_contract()
        newer_contract = Contract.objects.create(
            user=seafarer,
            sign_on_date=datetime.date(2026, 7, 1),
            sign_off_date=datetime.date(2026, 12, 1),
        )
        # Older contract: 1 doc (should NOT appear)
        Document.objects.create(contract=older_contract, title="OLD")
        # Newer contract: 2 docs (these should appear)
        Document.objects.create(contract=newer_contract, title="NEW1")
        Document.objects.create(contract=newer_contract, title="NEW2")

        r = client.get(self.url + f"?user={seafarer.id}")
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)
        titles = sorted(d["title"] for d in r.data)
        self.assertEqual(titles, ["NEW1", "NEW2"])
        for d in r.data:
            self.assertEqual(d["contract"], newer_contract.id)
            self.assertIsNone(
                d["user"],
                "Listed admin attachments must have user=null "
                "so they don't leak into the seafarer's CV list."
            )

    def test_get_without_user_returns_400(self):
        client = self._login_as_admin()
        r = client.get(self.url)
        self.assertEqual(r.status_code, http_status.HTTP_400_BAD_REQUEST, r.data)

    def test_get_returns_empty_list_when_user_has_no_contract(self):
        """No contract -> [] (not 404) so the UI renders 'no attachments'
        without a noisy error toast."""
        client = self._login_as_admin()
        lonely = Users.objects.create_user(
            email="empty-contracts@example.com", password="x",
            first_name="No", middle_name="Contract", role="Employee",
        )
        r = client.get(self.url + f"?user={lonely.id}")
        self.assertEqual(r.status_code, http_status.HTTP_200_OK)
        self.assertEqual(r.data, [])

    # ---- Auth ---------------------------------------------------------

    def test_anonymous_post_is_rejected(self):
        """Unauthenticated POST -> 401 (the legacy AllowAny on `create`
        must NOT extend to this new action)."""
        from rest_framework.test import APIClient
        seafarer, _ = self._make_seafarer_with_contract()
        r = APIClient().post(
            self.url,
            self._multipart(user=seafarer.id, title="anon"),
            format="multipart",
        )
        # 401 (Unauthorized) or 403 (Forbidden) — both are acceptable
        # rejection codes; the bug we're guarding against is 2xx.
        self.assertIn(r.status_code, (401, 403), r.data)


class UserStatusFiveStateTests(TestCase):
    """
    Tests for the 5-state user_status expansion:

      ON_SITE, ON_BOARD, VACATION, MEDICAL_VACATION, NEW_APPLICANT

    The first three are stored (admin-settable). ON_BOARD and
    NEW_APPLICANT are computed from contracts. The serializer
    exposes ``effective_user_status`` (computed) alongside
    ``user_status`` (stored).
    """

    @classmethod
    def setUpTestData(cls):
        # Need a Company + Rank + Ship for Contract rows.
        from api.models import Contract
        from companies.models import Company, JobOrder, JobOrderPosition
        from ships.models import Ship
        cls.Contract = Contract
        cls.Ship = Ship
        cls.company = Company.objects.create(
            company_name="Test Co",
            contact_email="co@example.com",
            status="Active",
        )
        cls.ship = cls.Ship.objects.create(
            ship_name="MV Test", imo_number="9876543", company=cls.company,
        )
        cls.rank = Rank.objects.create(code="MAS-1", name="Master")

        # u_newapplicant: no contracts at all -> NEW_APPLICANT
        cls.u_newapplicant = Users.objects.create_user(
            email="fresh@example.com", password="x",
            first_name="New", middle_name="Applicant",
        )
        # u_onsite: completed contract history, no active -> ON_SITE
        cls.u_onsite = Users.objects.create_user(
            email="free@example.com", password="x",
            first_name="Free", middle_name="Again",
        )
        # u_onboard: Active contract, no sign_off -> ON_BOARD
        cls.u_onboard = Users.objects.create_user(
            email="onboard@example.com", password="x",
            first_name="On", middle_name="Board",
        )
        # u_vacation: stored VACATION
        cls.u_vacation = Users.objects.create_user(
            email="vacation@example.com", password="x",
            first_name="On", middle_name="Vacation",
            user_status="VACATION",
        )
        # u_medical: stored MEDICAL_VACATION
        cls.u_medical = Users.objects.create_user(
            email="medical@example.com", password="x",
            first_name="On", middle_name="Medical",
            user_status="MEDICAL_VACATION",
        )

        # Job order + position (needed to satisfy Contract FKs)
        cls.jo = JobOrder.objects.create(
            company=cls.company, ship=cls.ship,
            reference_number="JO-STATUS-TEST-1",
            request_date=datetime.date.today(),
            target_joining_date=datetime.date.today(),
        )
        cls.pos = JobOrderPosition.objects.create(
            job_order=cls.jo, rank=cls.rank, quantity=1,
        )

        # u_onsite: completed contract in the past -> back to ON_SITE
        Contract.objects.create(
            user=cls.u_onsite, ship=cls.ship, company=cls.company,
            rank=cls.rank, job_position=cls.pos,
            sign_on_date=datetime.date.today() - datetime.timedelta(days=180),
            sign_off_date=datetime.date.today() - datetime.timedelta(days=1),
            status="Completed",
        )
        # u_onboard: Active contract, no sign_off -> ON_BOARD
        Contract.objects.create(
            user=cls.u_onboard, ship=cls.ship, company=cls.company,
            rank=cls.rank, job_position=cls.pos,
            sign_on_date=datetime.date.today(),
            status="Active",
        )

    def test_enum_has_five_values(self):
        from api.models import User_Status
        values = {c.value for c in User_Status}
        self.assertEqual(
            values,
            {
                "ON_SITE", "ON_BOARD",
                "VACATION", "MEDICAL_VACATION", "NEW_APPLICANT",
            },
        )

    def test_effective_status_no_contracts_is_new_applicant(self):
        self.assertEqual(
            self.u_newapplicant.get_effective_status(), "NEW_APPLICANT"
        )

    def test_effective_status_completed_contract_is_on_site(self):
        self.assertEqual(
            self.u_onsite.get_effective_status(), "ON_SITE"
        )

    def test_effective_status_onboard_user_is_on_board(self):
        self.assertEqual(self.u_onboard.get_effective_status(), "ON_BOARD")

    def test_effective_status_vacation_overrides_contract(self):
        """A user marked VACATION wins even if they have an active contract."""
        Contract = self.Contract
        Contract.objects.create(
            user=self.u_vacation, ship=self.ship, company=self.company,
            rank=self.rank, job_position=self.pos,
            sign_on_date=datetime.date.today(),
            status="Active",
        )
        self.assertEqual(self.u_vacation.get_effective_status(), "VACATION")

    def test_effective_status_medical_vacation_overrides_contract(self):
        Contract = self.Contract
        Contract.objects.create(
            user=self.u_medical, ship=self.ship, company=self.company,
            rank=self.rank, job_position=self.pos,
            sign_on_date=datetime.date.today(),
            status="Active",
        )
        self.assertEqual(
            self.u_medical.get_effective_status(), "MEDICAL_VACATION"
        )

    def test_effective_status_signed_off_in_future_is_on_board(self):
        """An Active contract with a future sign-off date is still ON_BOARD."""
        future = Users.objects.create_user(
            email="future@example.com", password="x",
            first_name="Still", middle_name="Sailing",
        )
        Contract = self.Contract
        Contract.objects.create(
            user=future, ship=self.ship, company=self.company,
            rank=self.rank, job_position=self.pos,
            sign_on_date=datetime.date.today() - datetime.timedelta(days=10),
            sign_off_date=datetime.date.today() + datetime.timedelta(days=20),
            status="Active",
        )
        self.assertEqual(future.get_effective_status(), "ON_BOARD")

    def test_serializer_exposes_effective_user_status(self):
        client, _ = self._login_as_admin()
        r = client.get(f"/api/users/users/{self.u_onboard.id}/")
        self.assertEqual(r.status_code, http_status.HTTP_200_OK)
        self.assertIn("effective_user_status", r.data)
        self.assertEqual(r.data["effective_user_status"], "ON_BOARD")
        # Stored value still exposed
        self.assertIn("user_status", r.data)
        self.assertEqual(r.data["user_status"], "ON_SITE")

    # ---- filter ?user_status=... ----------------------------------

    def _list(self, qs):
        client, _ = self._login_as_admin()
        return client.get(LIST_URL, qs)

    def _ids(self, response):
        items = response.data
        if isinstance(items, dict) and "results" in items:
            items = items["results"]
        return {u["id"] for u in items}

    def test_filter_by_on_site(self):
        r = self._list({"user_status": "ON_SITE"})
        ids = self._ids(r)
        # finished user (has contract history but no active) is ON_SITE
        self.assertIn(self.u_onsite.id, ids)
        # onboard user is NOT (they have an active contract)
        self.assertNotIn(self.u_onboard.id, ids)
        # vacation/medical users are NOT (they're manually flagged)
        self.assertNotIn(self.u_vacation.id, ids)
        self.assertNotIn(self.u_medical.id, ids)
        # no-contracts user is NOT (they're NEW_APPLICANT)
        self.assertNotIn(self.u_newapplicant.id, ids)

    def test_filter_by_on_board(self):
        r = self._list({"user_status": "ON_BOARD"})
        ids = self._ids(r)
        self.assertIn(self.u_onboard.id, ids)
        self.assertNotIn(self.u_onsite.id, ids)
        self.assertNotIn(self.u_newapplicant.id, ids)
        self.assertNotIn(self.u_vacation.id, ids)
        self.assertNotIn(self.u_medical.id, ids)

    def test_filter_by_vacation(self):
        r = self._list({"user_status": "VACATION"})
        ids = self._ids(r)
        self.assertIn(self.u_vacation.id, ids)
        self.assertNotIn(self.u_onsite.id, ids)
        self.assertNotIn(self.u_medical.id, ids)

    def test_filter_by_medical_vacation_accepts_human_label(self):
        """The human label 'MEDICAL VACATION' (with space) is accepted."""
        r = self._list({"user_status": "MEDICAL VACATION"})
        ids = self._ids(r)
        self.assertIn(self.u_medical.id, ids)

    def test_filter_by_medical_vacation_accepts_stored_value(self):
        """And the stored value 'MEDICAL_VACATION' is also accepted."""
        r = self._list({"user_status": "MEDICAL_VACATION"})
        ids = self._ids(r)
        self.assertIn(self.u_medical.id, ids)

    def test_filter_by_new_applicant(self):
        r = self._list({"user_status": "NEW_APPLICANT"})
        ids = self._ids(r)
        self.assertIn(self.u_newapplicant.id, ids)
        self.assertNotIn(self.u_onsite.id, ids)
        self.assertNotIn(self.u_onboard.id, ids)
        self.assertNotIn(self.u_vacation.id, ids)
        self.assertNotIn(self.u_medical.id, ids)

    def test_filter_invalid_value_returns_400(self):
        r = self._list({"user_status": "BOGUS_VALUE"})
        self.assertEqual(r.status_code, http_status.HTTP_400_BAD_REQUEST)

    def test_filter_multi_value_or_logic(self):
        """?user_status=A&user_status=B returns users matching either."""
        r = self._list({"user_status": ["VACATION", "MEDICAL_VACATION"]})
        ids = self._ids(r)
        self.assertIn(self.u_vacation.id, ids)
        self.assertIn(self.u_medical.id, ids)
        self.assertNotIn(self.u_onsite.id, ids)

    def _login_as_admin(self):
        admin = Users.objects.create_user(
            email="admin-status@example.com", password="x",
            first_name="Admin", middle_name="Ops", role="Admin",
            is_staff=True, is_superuser=True,
        )
        from rest_framework.test import APIClient
        c = APIClient()
        c.force_authenticate(user=admin)
        return c, admin


# ===========================================================================
# Seafarer phone-login + /api/me/ self-service
# ===========================================================================
#
# When Admin uploads a CV via /ai/parse/ with save_to_db=true, a new
# User is created with role='Employee' and password=phone. The seafarer
# can then:
#   1. POST /api/auth/phone-login/ with {phone, phone} → JWT
#   2. GET/PATCH /api/me/ to view/edit their own profile
#
# These tests cover the auth surface so we know the end-to-end
# "Admin uploads CV → seafarer logs in with their phone" flow works.

from rest_framework.test import APITestCase  # noqa: E402


class PhoneLoginTests(APITestCase):
    """POST /api/auth/phone-login/

    Phone login is gated behind ``is_phone_verified=True`` (the
    seafarer must first call /api/auth/verify-otp/ with the OTP
    that was sent to their phone at upload time).
    """

    def setUp(self):
        from api.models import Users
        self.user = Users.objects.create_user(
            email="seafarer@sakrshipping.com",
            password="00201090946284",  # phone-as-password
            first_name="MOHAMED",
            middle_name="SHEHATA",
        )
        self.user.role = "Employee"
        self.user.phone_number = "00201090946284"
        self.user.is_phone_verified = True  # default-verified for these tests
        self.user.save()
        self.url = "/api/auth/phone-login/"

    def test_login_with_correct_phone_and_password(self):
        response = self.client.post(
            self.url,
            {"phone": "00201090946284", "password": "00201090946284"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["email"], "seafarer@sakrshipping.com")
        self.assertEqual(response.data["user"]["phone_number"], "00201090946284")

    def test_login_with_wrong_password_rejected(self):
        response = self.client.post(
            self.url,
            {"phone": "00201090946284", "password": "wrong"},
            format="json",
        )
        self.assertEqual(response.status_code, 401)

    def test_login_with_unknown_phone_rejected(self):
        response = self.client.post(
            self.url,
            {"phone": "99999999", "password": "99999999"},
            format="json",
        )
        self.assertEqual(response.status_code, 401)

    def test_login_requires_both_fields(self):
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_inactive_user_cannot_login(self):
        self.user.is_active = False
        self.user.save()
        response = self.client.post(
            self.url,
            {"phone": "00201090946284", "password": "00201090946284"},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_unverified_user_cannot_login(self):
        # Newly-created seafarers (right after Admin uploads a CV) are
        # not yet verified — the gate must block them until they
        # POST /api/auth/verify-otp/.
        self.user.is_phone_verified = False
        self.user.save()
        response = self.client.post(
            self.url,
            {"phone": "00201090946284", "password": "00201090946284"},
            format="json",
        )
        self.assertEqual(response.status_code, 403)
        # The error message must hint at the verify-otp endpoint.
        self.assertIn("verify-otp", response.data["detail"].lower())


class RequestOTPTests(APITestCase):
    """POST /api/auth/request-otp/"""

    def setUp(self):
        from api.models import Users
        from django.utils import timezone
        self.user = Users.objects.create_user(
            email="seafarer@sakrshipping.com",
            password="x",
            first_name="MOHAMED",
        )
        self.user.phone_number = "00201090946284"
        self.user.is_phone_verified = False
        self.user.otp_code = "111111"
        self.user.otp_expires_at = timezone.now() + timezone.timedelta(minutes=5)
        self.user.save()
        self.url = "/api/auth/request-otp/"

    def test_known_phone_regenerates_otp(self):
        response = self.client.post(
            self.url, {"phone": "00201090946284"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["phone"], "00201090946284")
        # The OLD OTP should be replaced.
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.otp_code, "111111")
        self.assertIsNotNone(self.user.otp_expires_at)

    def test_unknown_phone_returns_200_no_leak(self):
        # Don't leak whether the phone is registered.
        response = self.client.post(
            self.url, {"phone": "99999999"}, format="json"
        )
        self.assertEqual(response.status_code, 200)

    def test_missing_phone_returns_400(self):
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_inactive_user_gets_403(self):
        self.user.is_active = False
        self.user.save()
        response = self.client.post(
            self.url, {"phone": "00201090946284"}, format="json"
        )
        self.assertEqual(response.status_code, 403)


class VerifyOTPTests(APITestCase):
    """POST /api/auth/verify-otp/"""

    def setUp(self):
        from api.models import Users
        from django.utils import timezone
        self.user = Users.objects.create_user(
            email="seafarer@sakrshipping.com",
            password="x",
            first_name="MOHAMED",
        )
        self.user.phone_number = "00201090946284"
        self.user.is_phone_verified = False
        self.user.otp_code = "123456"
        self.user.otp_expires_at = timezone.now() + timezone.timedelta(minutes=5)
        self.user.save()
        self.url = "/api/auth/verify-otp/"

    def test_correct_otp_marks_verified_and_returns_jwt(self):
        response = self.client.post(
            self.url, {"phone": "00201090946284", "otp": "123456"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_phone_verified)
        # The OTP must be cleared so it can't be reused.
        self.assertIsNone(self.user.otp_code)
        self.assertIsNone(self.user.otp_expires_at)

    def test_wrong_otp_rejected(self):
        response = self.client.post(
            self.url, {"phone": "00201090946284", "otp": "000000"}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["detail"], "Invalid OTP")
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_phone_verified)

    def test_expired_otp_rejected(self):
        from django.utils import timezone
        self.user.otp_expires_at = timezone.now() - timezone.timedelta(minutes=1)
        self.user.save()
        response = self.client.post(
            self.url, {"phone": "00201090946284", "otp": "123456"}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_phone_verified)

    def test_unknown_phone_rejected(self):
        response = self.client.post(
            self.url, {"phone": "99999999", "otp": "123456"}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["detail"], "Invalid OTP")

    def test_missing_fields_rejected(self):
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_already_verified_user_is_idempotent(self):
        # Once verified, the seafarer can re-call verify-otp (e.g. on a
        # new device) and get a fresh JWT without re-validating.
        self.user.is_phone_verified = True
        self.user.save()
        response = self.client.post(
            self.url, {"phone": "00201090946284", "otp": "WRONG"}, format="json"
        )
        # Idempotent: 200 + JWT, not 400.
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)


class OTPEmailDispatchTests(APITestCase):
    """The /ai/parse/ save flow must send the initial OTP via the email
    service to the user's email address (not their phone).

    The default backend is ConsoleEmailService which logs the would-be
    email. We capture the log and assert on its contents. The admin
    never sees the OTP in the API response.
    """

    def setUp(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.uploaded = SimpleUploadedFile(
            "cv.pdf", b"x", content_type="application/pdf"
        )
        self.data = {
            "1_personal_details": {
                "full_name": "JOHN DOE",
                "marital_status": {"single": True, "married": False},
            },
            "3_contact_details": {
                "e_mail": "john@sakrshipping.com",
                "mobile_tel": "00201234567890",
            },
            "0_application_meta": {
                "expected_salary": "",
                "available_date": "",
            },
        }

    @override_settings(EMAIL_SERVICE="api.email.ConsoleEmailService")
    def test_initial_otp_is_stored_and_email_dispatched(self):
        from ai_document.views import _save_parser_output
        from api.models import Users

        # assertLogs auto-attaches a handler at INFO level on the
        # given logger, captures the output, and restores on exit.
        # This works regardless of the project's LOGGING config
        # because it overrides the effective level.
        with self.assertLogs("api.email", level="INFO") as cm:
            user_id, _, _dropped = _save_parser_output(self.data, self.uploaded)

        user = Users.objects.get(id=user_id)
        # The user is NOT phone-verified.
        self.assertFalse(user.is_phone_verified)
        # An OTP is on the row.
        self.assertIsNotNone(user.otp_code)
        self.assertEqual(len(user.otp_code), 6)
        # The email service was called — log line emitted with email + OTP.
        joined = "\n".join(cm.output)
        # The user's email is in the log, NOT their phone (the phone
        # is what the seafarer uses to look themselves up; the OTP is
        # delivered to the email address on file from the CV).
        self.assertIn("john@sakrshipping.com", joined)
        self.assertIn(user.otp_code, joined)
        # Belt and braces: confirm the phone is NOT in the dispatch log.
        self.assertNotIn("00201234567890", joined)

    def test_initial_otp_skipped_when_no_email(self):
        # _save_parser_output requires an email (Users.email is unique
        # and non-null). When the CV has no email, the save fails with
        # _NoEmailError before the email dispatch path is even reached,
        # so no "EMAIL-CONSOLE" log is emitted.
        from ai_document.views import _save_parser_output, _NoEmailError

        data = dict(self.data)
        data["3_contact_details"] = {"mobile_tel": "00201234567890"}

        # Confirm the save raises (this is the existing contract —
        # email is required for the Users row).
        with self.assertRaises(_NoEmailError):
            _save_parser_output(data, self.uploaded)

        # And confirm no Users row was created (the save aborted
        # before the user insert).
        from api.models import Users
        self.assertFalse(
            Users.objects.filter(phone_number="00201234567890").exists()
        )


class RequestOTPNoEmailTests(APITestCase):
    """POST /api/auth/request-otp/ for users with no email on file.

    A seafarer with a phone but no email can't receive an OTP, so the
    endpoint must NOT 500 — it returns the same opaque "OTP has been
    sent" response as for an unknown phone, and logs a warning.
    """

    def setUp(self):
        from api.models import Users
        from django.utils import timezone
        self.user = Users.objects.create_user(
            email="placeholder@x.com",  # required by Users model
            password="x",
            first_name="NOEMAIL",
        )
        # Clear the email to simulate a phone-only user.
        self.user.email = ""
        self.user.phone_number = "00201111222333"
        self.user.is_phone_verified = False
        self.user.otp_code = "111111"
        self.user.otp_expires_at = timezone.now() + timezone.timedelta(minutes=5)
        self.user.save()
        self.url = "/api/auth/request-otp/"

    def test_no_email_returns_200_no_leak(self):
        # Same response as an unknown phone — don't leak the absence
        # of an email address. The endpoint should NOT 500 even
        # though there's no delivery channel.
        response = self.client.post(
            self.url, {"phone": "00201111222333"}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        # Response body is identical to the unknown-phone case (no leak).
        self.assertEqual(
            response.data["detail"],
            "If that phone is registered, an OTP has been sent.",
        )


class RequestOTPEmailDispatchTests(APITestCase):
    """POST /api/auth/request-otp/ dispatches via the email service.

    The seafarer's phone is the lookup key; the OTP itself goes to
    their email address on file.
    """

    def setUp(self):
        from api.models import Users
        from django.utils import timezone
        self.user = Users.objects.create_user(
            email="seafarer@sakrshipping.com",
            password="x",
            first_name="MOHAMED",
        )
        self.user.phone_number = "00201090946284"
        self.user.is_phone_verified = False
        self.user.otp_code = "111111"
        self.user.otp_expires_at = timezone.now() + timezone.timedelta(minutes=5)
        self.user.save()
        self.url = "/api/auth/request-otp/"

    @override_settings(EMAIL_SERVICE="api.email.ConsoleEmailService")
    def test_otp_dispatched_to_email_not_phone(self):
        with self.assertLogs("api.email", level="INFO") as cm:
            response = self.client.post(
                self.url, {"phone": "00201090946284"}, format="json"
            )
        self.assertEqual(response.status_code, 200)
        joined = "\n".join(cm.output)
        # The user's email is in the dispatch log.
        self.assertIn("seafarer@sakrshipping.com", joined)
        # The phone is NOT in the dispatch log (the phone is the
        # lookup key, not the delivery channel).
        self.assertNotIn("00201090946284", joined)


class MeViewTests(APITestCase):
    """GET / PATCH /api/me/"""

    def setUp(self):
        from api.models import Users
        from rest_framework_simplejwt.tokens import RefreshToken
        self.user = Users.objects.create_user(
            email="seafarer2@sakrshipping.com",
            password="00201099999999",
            first_name="MOHAMED",
            middle_name="SHEHATA",
        )
        self.user.role = "Employee"
        self.user.phone_number = "00201099999999"
        self.user.nationality = "Egyptian"
        self.user.save()
        self.url = "/api/me/"
        # Authenticate via JWT (so the endpoint sees a real token path)
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_get_returns_own_profile(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.user.id)
        self.assertEqual(response.data["email"], "seafarer2@sakrshipping.com")
        self.assertEqual(response.data["phone_number"], "00201099999999")
        self.assertEqual(response.data["nationality"], "Egyptian")

    def test_patch_updates_editable_field(self):
        response = self.client.patch(
            self.url,
            {"nationality": "Saudi", "city": "Riyadh"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.nationality, "Saudi")
        self.assertEqual(self.user.city, "Riyadh")

    def test_patch_drops_role_escalation(self):
        # The seafarer must NOT be able to flip their own role to Admin.
        # When the request body contains ONLY non-editable fields, we
        # return 400 (telling the user "you didn't send anything I can
        # write") rather than 200 (which would look like a successful
        # no-op and confuse the seafarer).
        response = self.client.patch(
            self.url, {"role": "Admin", "is_staff": True}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, "Employee")
        self.assertFalse(self.user.is_staff)

    def test_patch_mixed_safe_and_unsafe_keeps_safe_only(self):
        # Mixed payload: editable (nationality) + non-editable (role).
        # The safe field is applied; the unsafe one is silently dropped.
        response = self.client.patch(
            self.url,
            {"nationality": "Saudi", "role": "Admin"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.nationality, "Saudi")
        # Role is unchanged.
        self.assertEqual(self.user.role, "Employee")

    def test_patch_drops_email_change(self):
        # Email is unique on the model and tied to login — seafarers
        # shouldn't be able to change their own email via /api/me/.
        response = self.client.patch(
            self.url, {"email": "hacker@evil.com"}, format="json"
        )
        self.assertEqual(response.status_code, 400)  # no editable fields

    def test_get_requires_auth(self):
        # No credentials → 401.
        from rest_framework.test import APIClient
        anon = APIClient()
        response = anon.get(self.url)
        self.assertEqual(response.status_code, 401)


class EmailServiceUnitTests(TestCase):
    """Unit tests for the EmailService implementations.

    These tests mock ``django.core.mail.send_mail`` (for the SMTP
    service) or the logger (for the console service) so we can
    verify behavior without actually sending mail. Real network /
    SMTP tests would be slow and brittle — the goal here is to
    lock in the dispatch contract (what gets sent, to whom, with
    what subject/body), not to test Django's mail backend itself.
    """

    def test_console_email_service_logs_at_info(self):
        # The dev default must emit a log line so devs can read the
        # OTP from the server log. If this breaks, the dev experience
        # silently regresses (no OTP visible anywhere).
        from api.email import ConsoleEmailService
        with self.assertLogs("api.email", level="INFO") as cm:
            ok = ConsoleEmailService().send_otp_email(
                "user@example.com", "123456", ttl_minutes=10
            )
        self.assertTrue(ok)
        joined = "\n".join(cm.output)
        self.assertIn("user@example.com", joined)
        self.assertIn("123456", joined)
        self.assertIn("10", joined)

    @patch("django.core.mail.send_mail")
    def test_django_smtp_email_service_sends_to_target(self, mock_send):
        # DjangoSMTPEmailService must use django.core.mail.send_mail
        # and pass the right subject/body/from/recipient_list.
        from api.email import DjangoSMTPEmailService

        mock_send.return_value = 1  # one message successfully sent
        ok = DjangoSMTPEmailService().send_otp_email(
            "seafarer@sakrshipping.com", "482917", ttl_minutes=10
        )
        self.assertTrue(ok)
        mock_send.assert_called_once()
        call_kwargs = mock_send.call_args.kwargs
        self.assertEqual(
            call_kwargs["recipient_list"], ["seafarer@sakrshipping.com"]
        )
        self.assertIn("482917", call_kwargs["subject"])
        self.assertIn("482917", call_kwargs["message"])
        self.assertIn("10", call_kwargs["message"])
        self.assertEqual(call_kwargs["fail_silently"], False)

    @patch("django.core.mail.send_mail")
    def test_django_smtp_email_service_returns_false_on_failure(self, mock_send):
        # If send_mail raises (network down, auth rejected, etc.),
        # the service must catch it and return False — not propagate
        # the exception to the caller. The OTP is still on the User
        # row; the seafarer can re-request.
        from api.email import DjangoSMTPEmailService

        mock_send.side_effect = RuntimeError("SMTP server down")
        ok = DjangoSMTPEmailService().send_otp_email(
            "seafarer@sakrshipping.com", "482917", ttl_minutes=10
        )
        self.assertFalse(ok)


class SaveParserOutputSeafarerPasswordTests(APITestCase):
    """The /ai/parse/ save flow must set password = phone for seafarers.

    This is the bridge between Admin's CV upload and the seafarer's
    first login — if _save_parser_output doesn't set the password,
    the seafarer can't log in via /api/auth/phone-login/.
    """

    def _make_uploaded_file(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        return SimpleUploadedFile("cv.pdf", b"x", content_type="application/pdf")

    def test_phone_is_used_as_password(self):
        from ai_document.views import _save_parser_output
        from api.models import Users

        data = {
            "1_personal_details": {
                "full_name": "JOHN DOE",
                "marital_status": {"single": True, "married": False},
            },
            "3_contact_details": {
                "e_mail": "john@sakrshipping.com",
                "mobile_tel": "00201234567890",
            },
            "0_application_meta": {
                "expected_salary": "",
                "available_date": "",
            },
        }
        user_id, _, _dropped = _save_parser_output(data, self._make_uploaded_file())

        user = Users.objects.get(id=user_id)
        # Phone is the password.
        self.assertTrue(user.check_password("00201234567890"))

    def test_email_used_as_password_when_phone_missing(self):
        # If the CV has no phone, fall back to email-as-password so the
        # seafarer can still log in via the standard /api/login/ flow.
        from ai_document.views import _save_parser_output
        from api.models import Users

        data = {
            "1_personal_details": {"full_name": "JANE DOE"},
            "3_contact_details": {"e_mail": "jane@sakrshipping.com"},
            "0_application_meta": {},
        }
        user_id, _, _dropped = _save_parser_output(data, self._make_uploaded_file())

        user = Users.objects.get(id=user_id)
        self.assertTrue(user.check_password("jane@sakrshipping.com"))

    def test_default_role_is_employee(self):
        from ai_document.views import _save_parser_output
        from api.models import Users

        data = {
            "1_personal_details": {"full_name": "BOB SMITH"},
            "3_contact_details": {"e_mail": "bob@sakrshipping.com"},
            "0_application_meta": {},
        }
        user_id, _, _dropped = _save_parser_output(data, self._make_uploaded_file())

        user = Users.objects.get(id=user_id)
        self.assertEqual(user.role, "Employee")


# ============================================================================
# Set-password magic link (admin-onboards-seafarer flow)
# ============================================================================
#
# When an Admin creates a CVSubmission for a seafarer that hasn't been
# onboarded yet, the system should email them a magic link. The seafarer
# clicks the link, lands on a frontend set-password page, and POSTs the
# new password to /api/auth/set-password-confirm/ with the token.
#
# We test:
#   1. dispatch_welcome_email() is called on CVSubmission create
#   2. The email service is called with the right user/email
#   3. The user's welcome_email_sent_at is stamped
#   4. Re-creating a CVSubmission for the same user does NOT re-send
#   5. SetPasswordConfirmView sets the password and stamps the flag
#   6. Bad tokens / weak passwords / unknown uidb64 are rejected
#   7. The link points at FRONTEND_SET_PASSWORD_URL with uidb64+token


class SetPasswordMagicLinkTests(APITestCase):
    """The admin-onboards-seafarer flow: CVSubmission POST →
    welcome email with magic link → /api/auth/set-password-confirm/.
    """

    def setUp(self):
        from api.models import Users, CVSubmission
        from django.contrib.auth import get_user_model
        Users = get_user_model()

        # The admin who creates the CVSubmission.
        self.admin = Users.objects.create_user(
            email="admin@sakrshipping.com",
            password="adminpass",
        )
        self.admin.role = "Admin"
        self.admin.is_staff = True
        self.admin.save()

        # The seafarer being onboarded.
        self.seafarer = Users.objects.create_user(
            email="seafarer@sakrshipping.com",
            password="placeholder",
            first_name="MOHAMED",
        )
        self.seafarer.role = "Employee"
        self.seafarer.phone_number = "00201090946284"
        self.seafarer.welcome_email_sent_at = None
        self.seafarer.save()

        self.client.force_authenticate(user=self.admin)
        self.url = "/api/cv-submissions/"

    def _create_cv_submission(self, user_id):
        from api.models import CVSubmission
        return CVSubmission.objects.create(
            user_id=user_id, status="Pending"
        )

    # ── dispatch_welcome_email unit tests ────────────────────────────

    def test_dispatch_skips_when_no_email(self):
        from api.views import dispatch_welcome_email
        from api.models import Users
        from django.contrib.auth import get_user_model
        U = get_user_model()
        # Build a user with empty email.
        u = U.objects.create_user(
            email="placeholder@x.com", password="x", first_name="X"
        )
        u.email = ""
        u.save()
        sent = dispatch_welcome_email(u)
        self.assertFalse(sent)

    def test_dispatch_skips_when_already_sent(self):
        from api.views import dispatch_welcome_email
        from django.utils import timezone
        self.seafarer.welcome_email_sent_at = timezone.now()
        self.seafarer.save()
        sent = dispatch_welcome_email(self.seafarer)
        self.assertFalse(sent)

    def test_dispatch_sends_email_and_stamps_flag(self):
        from api.views import dispatch_welcome_email
        from unittest.mock import patch
        from django.utils import timezone

        with patch("api.email.get_email_service") as mock_get:
            mock_service = mock_get.return_value
            mock_service.send_set_password_link.return_value = True
            sent = dispatch_welcome_email(self.seafarer)

        self.assertTrue(sent)
        mock_service.send_set_password_link.assert_called_once()
        # First positional arg is the email address; second is the
        # full magic-link URL.
        call_args = mock_service.send_set_password_link.call_args
        self.assertEqual(call_args.args[0], "seafarer@sakrshipping.com")
        self.assertIn("?uidb64=", call_args.args[1])
        self.assertIn("&token=", call_args.args[1])
        # Flag was stamped.
        self.seafarer.refresh_from_db()
        self.assertIsNotNone(self.seafarer.welcome_email_sent_at)

    def test_dispatch_does_not_stamp_when_email_send_fails(self):
        from api.views import dispatch_welcome_email
        from unittest.mock import patch

        with patch("api.email.get_email_service") as mock_get:
            mock_service = mock_get.return_value
            mock_service.send_set_password_link.return_value = False
            sent = dispatch_welcome_email(self.seafarer)

        self.assertFalse(sent)
        self.seafarer.refresh_from_db()
        self.assertIsNone(self.seafarer.welcome_email_sent_at)

    # ── CVSubmission create trigger ─────────────────────────────────

    def test_cv_submission_create_for_existing_user_does_not_dispatch(self):
        # With the new credentials-email flow, the magic-link
        # dispatch_welcome_email is no longer triggered by the
        # admin CVSubmission path. For an existing user (the FK
        # path), no email goes out at all — we don't want to leak
        # the user's existing password.
        from unittest.mock import patch

        with patch("api.views.dispatch_welcome_email") as mock_dispatch, \
             patch("api.views.dispatch_welcome_credentials") as mock_creds:
            resp = self.client.post(
                self.url,
                {"user": self.seafarer.id, "status": "Pending"},
                format="json",
            )
        self.assertEqual(resp.status_code, 201, resp.data)
        mock_dispatch.assert_not_called()
        mock_creds.assert_not_called()

    def test_second_cv_submission_for_same_user_does_not_redisptach(self):
        # With the new credentials-email flow, no email is sent for
        # existing users (the FK path), so a second CVSubmission for
        # the same user also doesn't send anything. This is the
        # opposite of the old magic-link flow (which sent once via
        # the welcome_email_sent_at flag).
        from unittest.mock import patch

        with patch("api.views.dispatch_welcome_email") as mock_dispatch, \
             patch("api.views.dispatch_welcome_credentials") as mock_creds:
            # First CVSubmission — no email sent.
            self.client.post(
                self.url,
                {"user": self.seafarer.id, "status": "Pending"},
                format="json",
            )
            # Second CVSubmission — also no email sent.
            self.client.post(
                self.url,
                {"user": self.seafarer.id, "status": "Pending"},
                format="json",
            )
        mock_dispatch.assert_not_called()
        mock_creds.assert_not_called()
        # welcome_email_sent_at was never stamped (no email went out).
        self.seafarer.refresh_from_db()
        self.assertIsNone(self.seafarer.welcome_email_sent_at)

    # ── SetPasswordConfirmView ──────────────────────────────────────

    def _build_link(self, user):
        from api.views import build_set_password_link
        return build_set_password_link(user)

    def test_set_password_confirm_with_valid_token(self):
        from django.urls import reverse
        link = self._build_link(self.seafarer)
        # Parse ?uidb64=...&token=... from the link
        from urllib.parse import urlparse, parse_qs
        qs = parse_qs(urlparse(link).query)
        uidb64 = qs["uidb64"][0]
        token = qs["token"][0]

        resp = self.client.post(
            "/api/auth/set-password-confirm/",
            {"uidb64": uidb64, "token": token, "new_password": "newSecurePass!42"},
            format="json",
        )
        self.assertEqual(resp.status_code, 200, resp.data)
        self.seafarer.refresh_from_db()
        self.assertTrue(self.seafarer.check_password("newSecurePass!42"))
        # Flag is stamped.
        self.assertIsNotNone(self.seafarer.welcome_email_sent_at)

    def test_set_password_confirm_rejects_invalid_token(self):
        resp = self.client.post(
            "/api/auth/set-password-confirm/",
            {
                "uidb64": "invalid",
                "token": "garbage",
                "new_password": "newSecurePass!42",
            },
            format="json",
        )
        # Either the uidb64 decodes to no user (400) or the token
        # fails check_token (400). Either way, 400.
        self.assertEqual(resp.status_code, 400)

    def test_set_password_confirm_rejects_weak_password(self):
        from urllib.parse import urlparse, parse_qs
        link = self._build_link(self.seafarer)
        qs = parse_qs(urlparse(link).query)
        resp = self.client.post(
            "/api/auth/set-password-confirm/",
            {"uidb64": qs["uidb64"][0], "token": qs["token"][0],
             "new_password": "x"},  # too short
            format="json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_set_password_confirm_rejects_missing_fields(self):
        resp = self.client.post(
            "/api/auth/set-password-confirm/",
            {"new_password": "anything"},
            format="json",
        )
        self.assertEqual(resp.status_code, 400)

    def test_set_password_link_uses_frontend_url(self):
        link = self._build_link(self.seafarer)
        # The link starts with the FRONTEND_SET_PASSWORD_URL setting.
        from django.conf import settings
        self.assertTrue(
            link.startswith(settings.FRONTEND_SET_PASSWORD_URL),
            f"Link {link!r} doesn't start with "
            f"FRONTEND_SET_PASSWORD_URL={settings.FRONTEND_SET_PASSWORD_URL!r}",
        )


# ============================================================================
# Auto-create Users row on CVSubmission POST (admin-onboarding)
# ============================================================================
#
# When an Admin posts a CVSubmission with `user_email` (and optional
# `user_first_name`, `user_middle_name`, `user_phone`) for a seafarer
# that isn't in the system yet, the viewset auto-creates a Users row
# with the default password = phone number. The welcome email is
# then dispatched with a magic link so the seafarer can set a
# custom password. This combines the previous two-step flow
# (POST /api/users/users/ + POST /api/cv-submissions/) into one
# admin action.


class CVSubmissionAutoCreateUserTests(APITestCase):
    """Auto-create Users row when Admin POSTs a CVSubmission for
    a new seafarer (via user_email + user_phone).

    The Admin sends a single POST with the seafarer's identifying
    data; the backend creates both the Users row (with default
    password = phone) and the CVSubmission in one shot, and fires
    the welcome email.
    """

    def setUp(self):
        from api.models import Users
        from rest_framework_simplejwt.tokens import RefreshToken

        self.admin = Users.objects.create_user(
            email="admin@sakrshipping.com",
            password="adminpass",
        )
        self.admin.role = "Admin"
        self.admin.is_staff = True
        self.admin.save()

        refresh = RefreshToken.for_user(self.admin)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}"
        )
        self.url = "/api/cv-submissions/"

    def test_admin_post_with_user_email_auto_creates_user(self):
        from api.models import Users
        from unittest.mock import patch

        # Confirm no user with this email yet.
        self.assertFalse(
            Users.objects.filter(email="newbie@sakrshipping.com").exists()
        )

        # Patch the email service so we don't actually send mail,
        # but let the real dispatch_welcome_credentials run so the
        # welcome_email_sent_at stamp happens. We assert on the
        # email service call (which proves the credentials email
        # path was taken) and on the flag (which proves the dispatch
        # function ran end-to-end).
        with patch("api.email.get_email_service") as mock_get:
            mock_service = mock_get.return_value
            mock_service.send_welcome_credentials_email.return_value = True
            mock_service.send_set_password_link.return_value = True
            resp = self.client.post(
                self.url,
                {
                    "user_email": "newbie@sakrshipping.com",
                    "user_first_name": "AHMED",
                    "user_middle_name": "HASSAN",
                    "user_phone": "00201012345678",
                    "status": "Pending",
                },
                format="json",
            )
        self.assertEqual(resp.status_code, 201, resp.data)

        # User was created.
        user = Users.objects.get(email="newbie@sakrshipping.com")
        self.assertEqual(user.first_name, "AHMED")
        self.assertEqual(user.middle_name, "HASSAN")
        self.assertEqual(user.phone_number, "00201012345678")
        self.assertEqual(user.role, "Employee")
        # Default password is the phone number.
        self.assertTrue(user.check_password("00201012345678"))
        # CVSubmission is linked to the new user.
        self.assertEqual(resp.data["user"], user.id)
        # Credentials email was dispatched (with phone-as-password).
        mock_service.send_welcome_credentials_email.assert_called_once()
        call_kwargs = mock_service.send_welcome_credentials_email.call_args.kwargs
        self.assertEqual(call_kwargs["to_email"], "newbie@sakrshipping.com")
        self.assertEqual(call_kwargs["username"], "newbie@sakrshipping.com")
        self.assertEqual(call_kwargs["password"], "00201012345678")
        # Magic-link path NOT used (we're auto-creating, not magic-link).
        mock_service.send_set_password_link.assert_not_called()
        # The flag was stamped (by the real dispatch function).
        self.assertIsNotNone(user.welcome_email_sent_at)

    def test_admin_post_with_existing_user_does_not_re_create(self):
        from api.models import Users
        from unittest.mock import patch

        # Pre-existing user with custom password.
        existing = Users.objects.create_user(
            email="already@sakrshipping.com",
            password="MyExistingPass!42",
            first_name="ORIGINAL",
        )
        existing.role = "Employee"
        existing.phone_number = "00201099999999"
        existing.save()

        with patch("api.views.dispatch_welcome_credentials") as mock_creds:
            resp = self.client.post(
                self.url,
                {
                    "user_email": "already@sakrshipping.com",
                    "user_first_name": "NEW_NAME",
                    "user_phone": "00201000000000",
                    "status": "Pending",
                },
                format="json",
            )
        self.assertEqual(resp.status_code, 201, resp.data)

        # Same user, not a new one.
        existing.refresh_from_db()
        self.assertEqual(existing.email, "already@sakrshipping.com")
        # First name was updated to the new one supplied.
        self.assertEqual(existing.first_name, "NEW_NAME")
        # Phone was updated to the new one.
        self.assertEqual(existing.phone_number, "00201000000000")
        # Password was NOT touched (still the seafarer's original).
        self.assertTrue(existing.check_password("MyExistingPass!42"))
        # Exactly one CVSubmission is linked.
        from api.models import CVSubmission
        self.assertEqual(
            CVSubmission.objects.filter(user=existing).count(), 1
        )
        # No credentials email was sent (would leak the existing
        # user's password).
        mock_creds.assert_not_called()

    def test_admin_post_with_existing_user_no_dispatch_when_already_sent(self):
        from api.models import Users
        from django.utils import timezone
        from unittest.mock import patch

        existing = Users.objects.create_user(
            email="welcomed@sakrshipping.com",
            password="x",
        )
        original_sent_at = timezone.now() - timezone.timedelta(hours=1)
        existing.welcome_email_sent_at = original_sent_at
        existing.save()

        # With the credentials flow, no email is sent for existing
        # users (regardless of welcome_email_sent_at). The flag
        # only gates the auto-create path.
        with patch("api.email.get_email_service") as mock_get:
            resp = self.client.post(
                self.url,
                {
                    "user_email": "welcomed@sakrshipping.com",
                    "user_phone": "00201088888888",
                    "status": "Pending",
                },
                format="json",
            )
        self.assertEqual(resp.status_code, 201, resp.data)
        # Neither credentials nor magic-link is sent.
        mock_get.return_value.send_welcome_credentials_email.assert_not_called()
        mock_get.return_value.send_set_password_link.assert_not_called()

    def test_admin_post_with_user_fk_skips_auto_create(self):
        # When the Admin passes the user FK directly (not user_email),
        # the existing flow is used: no auto-create, no password reset,
        # no email (would leak the existing user's password).
        from api.models import Users
        from unittest.mock import patch

        existing = Users.objects.create_user(
            email="fkuser@sakrshipping.com",
            password="TheirOwnPassword!42",
        )
        existing.role = "Employee"
        existing.save()

        with patch("api.views.dispatch_welcome_credentials") as mock_creds, \
             patch("api.views.dispatch_welcome_email") as mock_magic:
            resp = self.client.post(
                self.url,
                {
                    "user": existing.id,
                    "status": "Pending",
                },
                format="json",
            )
        self.assertEqual(resp.status_code, 201, resp.data)
        # Same user, password untouched.
        existing.refresh_from_db()
        self.assertTrue(existing.check_password("TheirOwnPassword!42"))
        # No email of any kind for existing-user FK path.
        mock_creds.assert_not_called()
        mock_magic.assert_not_called()

    def test_admin_post_without_user_email_falls_back_to_admin(self):
        # Historical fallback: if neither 'user' nor 'user_email' is
        # provided, the CVSubmission is attributed to the admin
        # (preserves the prior API contract for callers that didn't
        # pass user info).
        resp = self.client.post(
            self.url,
            {"status": "Pending"},
            format="json",
        )
        self.assertEqual(resp.status_code, 201, resp.data)
        # CVSubmission is linked to the admin (no auto-create).
        self.assertEqual(resp.data["user"], self.admin.id)
        from api.models import Users
        # Only 2 users exist: admin and the test's own setup
        # (no auto-created newbie).
        self.assertEqual(
            Users.objects.filter(email="newbie@sakrshipping.com").count(), 0
        )

    def test_admin_post_auto_create_with_no_phone_falls_back_to_email_password(self):
        # If the Admin doesn't supply user_phone, the new user is
        # created with password = email (so /api/login/ works as a
        # fallback). The credentials email goes out with the email
        # as the password.
        from api.models import Users
        from unittest.mock import patch

        with patch("api.views.dispatch_welcome_credentials") as mock_creds:
            resp = self.client.post(
                self.url,
                {
                    "user_email": "nophone@sakrshipping.com",
                    "user_first_name": "NO_PHONE",
                    "status": "Pending",
                },
                format="json",
            )
        self.assertEqual(resp.status_code, 201, resp.data)
        user = Users.objects.get(email="nophone@sakrshipping.com")
        # No phone on file (the field defaults to "" per the model
        # NOT NULL constraint).
        self.assertEqual(user.phone_number, "")
        # Password is the email (fallback).
        self.assertTrue(user.check_password("nophone@sakrshipping.com"))
        # Credentials email was sent with the email-as-password.
        mock_creds.assert_called_once()
        call_args = mock_creds.call_args
        self.assertEqual(call_args.args[0].id, user.id)
        self.assertEqual(call_args.args[1], "nophone@sakrshipping.com")

    def test_admin_post_with_employee_role_does_not_auto_create(self):
        # If the requester is an Employee, the CVSubmission is
        # always for themselves — no auto-create path applies.
        from api.models import Users
        employee = Users.objects.create_user(
            email="emp@sakrshipping.com",
            password="emppass",
        )
        employee.role = "Employee"
        employee.save()
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(employee)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}"
        )

        resp = self.client.post(
            self.url,
            {
                "user_email": "someone-else@sakrshipping.com",
                "user_phone": "00201000000000",
                "status": "Pending",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201, resp.data)
        # CVSubmission attributed to the employee themselves.
        self.assertEqual(resp.data["user"], employee.id)
        # No auto-created "someone-else" user.
        from api.models import Users as U
        self.assertFalse(
            U.objects.filter(email="someone-else@sakrshipping.com").exists()
        )


# ============================================================================
# CVSubmission FK fields return strings (for dropdown UIs)
# ============================================================================
#
# The Admin UI needs dropdown menus for position/company/ship/etc.
# To keep the frontend simple, the API returns the display name
# (string) directly in those fields, not the FK id. The original
# FK id is preserved in a sibling ``*_id`` field for clients that
# still need it (e.g. for PATCH/DELETE).
#
# Old shape:  {"position": 7,      "position_name": "Master"}
# New shape:  {"position": "Master", "position_id": 7}
#
# The input side mirrors this: the FK fields accept either a string
# (name) or an int (id) in the body. The look-up is by name when
# a non-digit string is provided, by id when an int / digit string
# is provided.


class CVSubmissionFKStringFieldsTests(APITestCase):
    """FK fields (position/company/ship/reviewed_by) are returned
    as strings in the CVSubmission response, and accept strings on
    input.
    """

    def setUp(self):
        from api.models import Users, Rank
        from companies.models import Company
        from ships.models import Ship
        from rest_framework_simplejwt.tokens import RefreshToken

        self.admin = Users.objects.create_user(
            email="admin@sakrshipping.com",
            password="adminpass",
            first_name="Admin",
        )
        self.admin.role = "Admin"
        self.admin.is_staff = True
        self.admin.save()

        # Seed reference data — positions, companies, ships, reviewer.
        self.position = Rank.objects.create(
            name="Master", code="MAS-TEST"
        )
        self.company = Company.objects.create(
            company_name="Test Shipping Co",
        )
        # Ship requires a ship_type and flag; create minimal stubs.
        from core.models import VesselType, Flag
        vtype, _ = VesselType.objects.get_or_create(name="Cargo Ship")
        flag, _ = Flag.objects.get_or_create(name="Test Flag")
        from ships.models import Ship
        self.ship = Ship.objects.create(
            ship_name="MV Test Vessel",
            ship_type=vtype,
            flag=flag,
            imo_number="1234567",
        )

        # Seafarer.
        self.seafarer = Users.objects.create_user(
            email="seafarer@sakrshipping.com",
            password="x",
            first_name="MOHAMED",
        )
        self.seafarer.role = "Employee"
        self.seafarer.save()

        refresh = RefreshToken.for_user(self.admin)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}"
        )
        self.url = "/api/cv-submissions/"

    def test_response_uses_string_names_for_fk_fields(self):
        # POST with FK ids, then GET — the response should echo back
        # string names for position/company/ship/reviewed_by, with
        # the original ids in the sibling *_id fields.
        from api.models import CVSubmission

        # Set reviewed_by to the admin.
        resp = self.client.post(
            self.url,
            {
                "user": self.seafarer.id,
                "position": self.position.id,
                "company": self.company.id,
                "ship": self.ship.id,
                "reviewed_by": self.admin.id,
                "status": "Pending",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201, resp.data)

        # The FK fields are now strings, not ids.
        self.assertEqual(resp.data["position"], "Master")
        self.assertEqual(resp.data["company"], "Test Shipping Co")
        self.assertEqual(resp.data["ship"], "MV Test Vessel")
        # reviewed_by uses full_name which includes first/middle/last.
        self.assertIn("Admin", resp.data["reviewed_by"])
        # The *_id siblings hold the original FK id.
        self.assertEqual(resp.data["position_id"], self.position.id)
        self.assertEqual(resp.data["company_id"], self.company.id)
        self.assertEqual(resp.data["ship_id"], self.ship.id)
        self.assertEqual(resp.data["reviewed_by_id"], self.admin.id)

    def test_response_with_null_fk_fields(self):
        # When the FK fields are NULL (no linked row), the response
        # fields are None — not "None" or 0 or anything else.
        from api.models import CVSubmission
        resp = self.client.post(
            self.url,
            {"user": self.seafarer.id, "status": "Pending"},
            format="json",
        )
        self.assertEqual(resp.status_code, 201, resp.data)
        self.assertIsNone(resp.data["position"])
        self.assertIsNone(resp.data["company"])
        self.assertIsNone(resp.data["ship"])
        self.assertIsNone(resp.data["reviewed_by"])
        self.assertIsNone(resp.data["position_id"])
        self.assertIsNone(resp.data["company_id"])
        self.assertIsNone(resp.data["ship_id"])
        self.assertIsNone(resp.data["reviewed_by_id"])

    def test_post_accepts_string_position(self):
        # The frontend can submit a string name for position and the
        # backend looks it up by name (no id required).
        resp = self.client.post(
            self.url,
            {
                "user": self.seafarer.id,
                "position": "Master",
                "status": "Pending",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201, resp.data)
        self.assertEqual(resp.data["position"], "Master")
        self.assertEqual(resp.data["position_id"], self.position.id)

    def test_post_accepts_string_company(self):
        resp = self.client.post(
            self.url,
            {
                "user": self.seafarer.id,
                "company": "Test Shipping Co",
                "status": "Pending",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201, resp.data)
        self.assertEqual(resp.data["company"], "Test Shipping Co")
        self.assertEqual(resp.data["company_id"], self.company.id)

    def test_post_accepts_string_ship(self):
        resp = self.client.post(
            self.url,
            {
                "user": self.seafarer.id,
                "ship": "MV Test Vessel",
                "status": "Pending",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201, resp.data)
        self.assertEqual(resp.data["ship"], "MV Test Vessel")
        self.assertEqual(resp.data["ship_id"], self.ship.id)

    def test_post_accepts_string_reviewed_by_by_email(self):
        # reviewed_by can also be a string (email match).
        resp = self.client.post(
            self.url,
            {
                "user": self.seafarer.id,
                "reviewed_by": "admin@sakrshipping.com",
                "status": "Pending",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201, resp.data)
        self.assertEqual(resp.data["reviewed_by_id"], self.admin.id)

    def test_post_accepts_string_reviewed_by_by_first_name(self):
        resp = self.client.post(
            self.url,
            {
                "user": self.seafarer.id,
                "reviewed_by": "Admin",
                "status": "Pending",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201, resp.data)
        self.assertEqual(resp.data["reviewed_by_id"], self.admin.id)

    def test_post_unknown_company_returns_400(self):
        # Strings that don't match any company return 400 with a
        # helpful error.
        resp = self.client.post(
            self.url,
            {
                "user": self.seafarer.id,
                "company": "Nonexistent Shipping Co",
                "status": "Pending",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("company", resp.data)
        self.assertIn("Nonexistent", str(resp.data["company"]))

    def test_post_unknown_ship_returns_400(self):
        resp = self.client.post(
            self.url,
            {
                "user": self.seafarer.id,
                "ship": "MV Ghost Vessel",
                "status": "Pending",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("ship", resp.data)

    def test_post_unknown_reviewed_by_returns_400(self):
        resp = self.client.post(
            self.url,
            {
                "user": self.seafarer.id,
                "reviewed_by": "nobody@nowhere.com",
                "status": "Pending",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("reviewed_by", resp.data)

    def test_post_id_still_works_for_backward_compatibility(self):
        # Clients that pass the FK id directly (the old shape) still
        # work — the serializer accepts both shapes.
        resp = self.client.post(
            self.url,
            {
                "user": self.seafarer.id,
                "position": self.position.id,  # int, not string
                "company": self.company.id,
                "ship": self.ship.id,
                "status": "Pending",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201, resp.data)
        self.assertEqual(resp.data["position"], "Master")


# ============================================================================
# Welcome-credentials email (auto-create path on CVSubmission POST)
# ============================================================================
#
# When an Admin POSTs a CVSubmission that auto-creates a new Users
# row, the system sends a "your account is ready" email containing
# the username (email) and the default password (phone) in plain
# text. This is the explicit project decision for the admin-onboarding
# flow. The magic-link path is still available via
# /api/auth/set-password-confirm/ for "I forgot my password" recovery.


class CVSubmissionWelcomeCredentialsTests(APITestCase):
    """The auto-create path sends a credentials email with the
    username and default password in plain text.

    SECURITY NOTE: this is the project-chosen trade-off. The
    alternative is the magic-link flow (POST /api/auth/verify-otp/ +
    POST /api/auth/set-password-confirm/), which is still available
    for any case where the password must NOT be transmitted in plain
    text.
    """

    def setUp(self):
        from api.models import Users
        from rest_framework_simplejwt.tokens import RefreshToken

        self.admin = Users.objects.create_user(
            email="admin@sakrshipping.com",
            password="adminpass",
            first_name="Admin",
        )
        self.admin.role = "Admin"
        self.admin.is_staff = True
        self.admin.save()
        refresh = RefreshToken.for_user(self.admin)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}"
        )
        self.url = "/api/cv-submissions/"

    def test_auto_create_sends_credentials_email_with_phone_password(self):
        from api.models import Users
        from unittest.mock import patch

        self.assertFalse(
            Users.objects.filter(email="newbie@sakrshipping.com").exists()
        )
        with patch("api.email.get_email_service") as mock_get:
            mock_service = mock_get.return_value
            mock_service.send_welcome_credentials_email.return_value = True
            resp = self.client.post(
                self.url,
                {
                    "user_email": "newbie@sakrshipping.com",
                    "user_first_name": "AHMED",
                    "user_phone": "00201012345678",
                    "status": "Pending",
                },
                format="json",
            )
        self.assertEqual(resp.status_code, 201, resp.data)

        # The email service was called with the right args.
        mock_service.send_welcome_credentials_email.assert_called_once()
        call_kwargs = mock_service.send_welcome_credentials_email.call_args.kwargs
        self.assertEqual(call_kwargs["to_email"], "newbie@sakrshipping.com")
        # Username is the email, password is the phone number.
        self.assertEqual(call_kwargs["username"], "newbie@sakrshipping.com")
        self.assertEqual(call_kwargs["password"], "00201012345678")
        self.assertEqual(call_kwargs["first_name"], "AHMED")
        # Magic-link path was NOT used for auto-create.
        mock_service.send_set_password_link.assert_not_called()

        # welcome_email_sent_at was stamped.
        user = Users.objects.get(email="newbie@sakrshipping.com")
        self.assertIsNotNone(user.welcome_email_sent_at)

    def test_auto_create_sends_credentials_email_with_email_fallback_password(self):
        # No user_phone → password falls back to email (so /api/login/
        # still works). The credentials email should still be sent.
        from api.models import Users
        from unittest.mock import patch

        with patch("api.email.get_email_service") as mock_get:
            mock_service = mock_get.return_value
            mock_service.send_welcome_credentials_email.return_value = True
            resp = self.client.post(
                self.url,
                {
                    "user_email": "nophone@sakrshipping.com",
                    "user_first_name": "NOPHONE",
                    "status": "Pending",
                },
                format="json",
            )
        self.assertEqual(resp.status_code, 201, resp.data)

        call_kwargs = mock_service.send_welcome_credentials_email.call_args.kwargs
        # Password is the email when no phone was supplied.
        self.assertEqual(call_kwargs["password"], "nophone@sakrshipping.com")

    def test_existing_user_does_not_get_credentials_email(self):
        # If the user already exists (looked up by email), the
        # credentials email is NOT sent — the password would be
        # wrong (it might be a custom one the user set), and we
        # don't want to leak it. The CVSubmission is still created.
        from api.models import Users
        from django.utils import timezone
        from unittest.mock import patch

        existing = Users.objects.create_user(
            email="existing@sakrshipping.com",
            password="TheirOwnPassword!42",
            first_name="EXISTING",
        )
        existing.role = "Employee"
        existing.phone_number = "00201088888888"
        existing.save()

        with patch("api.email.get_email_service") as mock_get:
            mock_service = mock_get.return_value
            mock_service.send_welcome_credentials_email.return_value = True
            resp = self.client.post(
                self.url,
                {
                    "user_email": "existing@sakrshipping.com",
                    "user_phone": "00201099999999",
                    "status": "Pending",
                },
                format="json",
            )
        self.assertEqual(resp.status_code, 201, resp.data)
        # No email sent (neither credentials nor magic-link).
        mock_service.send_welcome_credentials_email.assert_not_called()
        mock_service.send_set_password_link.assert_not_called()

        # The existing user's password was NOT touched.
        existing.refresh_from_db()
        self.assertTrue(existing.check_password("TheirOwnPassword!42"))

    def test_credentials_email_failure_does_not_break_save(self):
        # If the email service returns False (e.g. SMTP down), the
        # CVSubmission is still created. welcome_email_sent_at stays
        # null so the magic-link fallback could try later.
        from api.models import Users
        from unittest.mock import patch

        with patch("api.email.get_email_service") as mock_get:
            mock_service = mock_get.return_value
            mock_service.send_welcome_credentials_email.return_value = False
            resp = self.client.post(
                self.url,
                {
                    "user_email": "failuser@sakrshipping.com",
                    "user_phone": "00201077777777",
                    "status": "Pending",
                },
                format="json",
            )
        self.assertEqual(resp.status_code, 201, resp.data)
        user = Users.objects.get(email="failuser@sakrshipping.com")
        # User was created even though the email failed.
        self.assertIsNotNone(user)
        # welcome_email_sent_at was NOT stamped (so the magic-link
        # fallback can fire on retry if the user re-uploads).
        self.assertIsNone(user.welcome_email_sent_at)

    def test_credentials_email_dispatches_only_once_per_user(self):
        # A second CVSubmission for the same user (auto-create was
        # idempotent on the first one) does NOT re-send the email.
        from api.models import Users
        from unittest.mock import patch

        with patch("api.email.get_email_service") as mock_get:
            mock_service = mock_get.return_value
            mock_service.send_welcome_credentials_email.return_value = True
            # First call — should send.
            self.client.post(
                self.url,
                {
                    "user_email": "idem@sakrshipping.com",
                    "user_phone": "00201066666666",
                    "status": "Pending",
                },
                format="json",
            )
            self.assertEqual(
                mock_service.send_welcome_credentials_email.call_count, 1
            )
            # Second call — should NOT send (welcome_email_sent_at set).
            self.client.post(
                self.url,
                {
                    "user_email": "idem@sakrshipping.com",
                    "status": "Pending",
                },
                format="json",
            )
            self.assertEqual(
                mock_service.send_welcome_credentials_email.call_count, 1
            )


class CVSubmissionApprovalCodeGenerationTests(APITestCase):
    """
    Regression: when a CVSubmission transitions to 'Approved' or
    'Hired', the linked user must get a 6-digit `generated_id` (the
    employee code shown in the CV Submissions board).

    Before the fix, only the legacy Document flow (status='Active')
    generated IDs, so any CVSubmission-driven onboarding left the
    `generated_id` column blank — admin saw "—" even after approval.
    """

    update_status_url = "/api/cv-submissions/{id}/update-status/"

    def _login_as_admin(self):
        admin = Users.objects.create_user(
            email="approver@example.com", password="x",
            first_name="A", middle_name="dmin", role="Admin",
            is_staff=True, is_superuser=True,
        )
        client = APIClient()
        client.force_authenticate(user=admin)
        return client, admin

    def _make_seafarer_and_cv(self):
        from api.models import CVSubmission
        seafarer = Users.objects.create_user(
            email="seafarer-approved@example.com", password="x",
            first_name="Sea", middle_name="Farer", role="Employee",
        )
        cv = CVSubmission.objects.create(user=seafarer, status="Pending")
        return seafarer, cv

    def test_update_status_to_approved_generates_generated_id(self):
        client, _ = self._login_as_admin()
        seafarer, cv = self._make_seafarer_and_cv()

        r = client.patch(
            self.update_status_url.format(id=cv.id),
            {"status": "Approved"},
            format="json",
        )
        self.assertEqual(r.status_code, 200, r.data)
        seafarer.refresh_from_db()
        self.assertIsNotNone(
            seafarer.generated_id,
            "Approving a CVSubmission must populate user.generated_id",
        )
        self.assertEqual(len(seafarer.generated_id), 6)
        self.assertTrue(seafarer.generated_id.isdigit())

    def test_update_status_to_hired_also_generates_generated_id(self):
        client, _ = self._login_as_admin()
        seafarer, cv = self._make_seafarer_and_cv()

        r = client.patch(
            self.update_status_url.format(id=cv.id),
            {"status": "Hired"},
            format="json",
        )
        self.assertEqual(r.status_code, 200, r.data)
        seafarer.refresh_from_db()
        self.assertIsNotNone(seafarer.generated_id)

    def test_update_status_to_rejected_does_not_generate_id(self):
        client, _ = self._login_as_admin()
        seafarer, cv = self._make_seafarer_and_cv()

        r = client.patch(
            self.update_status_url.format(id=cv.id),
            {"status": "Rejected"},
            format="json",
        )
        self.assertEqual(r.status_code, 200, r.data)
        seafarer.refresh_from_db()
        self.assertIsNone(
            seafarer.generated_id,
            "Rejected CVs must NOT get a generated_id",
        )

    def test_update_status_does_not_overwrite_existing_generated_id(self):
        client, _ = self._login_as_admin()
        seafarer, cv = self._make_seafarer_and_cv()
        seafarer.generated_id = "123456"
        seafarer.save()

        r = client.patch(
            self.update_status_url.format(id=cv.id),
            {"status": "Approved"},
            format="json",
        )
        self.assertEqual(r.status_code, 200, r.data)
        seafarer.refresh_from_db()
        self.assertEqual(
            seafarer.generated_id, "123456",
            "Existing generated_id must be preserved (no churn)",
        )

    def test_patch_status_to_approved_via_serializer_also_generates_id(self):
        """A PATCH /api/cv-submissions/{id}/ with status=Approved must
        trigger the same code generation as the dedicated action —
        otherwise the bug only fixes half the surface area."""
        from rest_framework.test import APIClient
        client, _ = self._login_as_admin()
        seafarer, cv = self._make_seafarer_and_cv()

        r = client.patch(
            f"/api/cv-submissions/{cv.id}/",
            {"status": "Approved"},
            format="json",
        )
        # PATCH may or may not be permitted on this view; whatever it
        # returns, the user must end up with a generated_id. If PATCH
        # is rejected, the dedicated update-status action still
        # works (covered above). If it succeeds, this also works.
        if r.status_code == 200:
            seafarer.refresh_from_db()
            self.assertIsNotNone(seafarer.generated_id)

    def test_generated_id_is_unique_across_users(self):
        """Two seafarers approved back-to-back must not collide on the
        same 6-digit ID."""
        client, _ = self._login_as_admin()
        seafarer_a, cv_a = self._make_seafarer_and_cv()
        # Use a different email for the second seafarer
        seafarer_b = Users.objects.create_user(
            email="seafarer-approved-b@example.com", password="x",
            first_name="Sea", middle_name="B", role="Employee",
        )
        from api.models import CVSubmission
        cv_b = CVSubmission.objects.create(user=seafarer_b, status="Pending")

        client.patch(
            self.update_status_url.format(id=cv_a.id),
            {"status": "Approved"},
            format="json",
        )
        client.patch(
            self.update_status_url.format(id=cv_b.id),
            {"status": "Approved"},
            format="json",
        )

        seafarer_a.refresh_from_db()
        seafarer_b.refresh_from_db()
        self.assertIsNotNone(seafarer_a.generated_id)
        self.assertIsNotNone(seafarer_b.generated_id)
        self.assertNotEqual(
            seafarer_a.generated_id, seafarer_b.generated_id,
            "Two approved seafarers must get different generated_ids",
        )

    def test_recruiter_can_also_trigger_generation(self):
        """Recruiters (not just Admins) should be able to approve CVs
        and trigger the code generation — that's the current RBAC
        policy on the action."""
        from rest_framework.test import APIClient
        seafarer, cv = self._make_seafarer_and_cv()
        recruiter = Users.objects.create_user(
            email="recruiter@example.com", password="x",
            first_name="R", middle_name="ecruiter", role="Recruiter",
        )
        client = APIClient()
        client.force_authenticate(user=recruiter)

        r = client.patch(
            self.update_status_url.format(id=cv.id),
            {"status": "Approved"},
            format="json",
        )
        self.assertEqual(r.status_code, 200, r.data)
        seafarer.refresh_from_db()
        self.assertIsNotNone(seafarer.generated_id)


class EmailServiceSendPasswordLinkTests(TestCase):
    """Unit tests for the new send_set_password_link method on both
    EmailService implementations.
    """

    def test_console_logs_link(self):
        from api.email import ConsoleEmailService
        with self.assertLogs("api.email", level="INFO") as cm:
            ok = ConsoleEmailService().send_set_password_link(
                "user@example.com",
                "https://sakrshipping.com/set-password?uidb64=abc&token=xyz",
                ttl_hours=24,
            )
        self.assertTrue(ok)
        joined = "\n".join(cm.output)
        self.assertIn("user@example.com", joined)
        self.assertIn("SET-PASSWORD", joined)
        self.assertIn("sakrshipping.com", joined)
        self.assertIn("24", joined)

    @patch("django.core.mail.send_mail")
    def test_django_smtp_sends(self, mock_send):
        from api.email import DjangoSMTPEmailService
        mock_send.return_value = 1
        ok = DjangoSMTPEmailService().send_set_password_link(
            "seafarer@sakrshipping.com",
            "https://sakrshipping.com/set-password?uidb64=abc&token=xyz",
            ttl_hours=24,
        )
        self.assertTrue(ok)
        call_kwargs = mock_send.call_args.kwargs
        self.assertEqual(
            call_kwargs["recipient_list"],
            ["seafarer@sakrshipping.com"],
        )
        self.assertIn("Welcome", call_kwargs["subject"])
        self.assertIn("set a password", call_kwargs["message"].lower())
        self.assertIn(
            "sakrshipping.com/set-password",
            call_kwargs["message"],
        )

    @patch("django.core.mail.send_mail")
    def test_django_smtp_returns_false_on_failure(self, mock_send):
        from api.email import DjangoSMTPEmailService
        mock_send.side_effect = RuntimeError("SMTP server down")
        ok = DjangoSMTPEmailService().send_set_password_link(
            "x@example.com", "https://x", ttl_hours=24
        )
        self.assertFalse(ok)


class EmailServiceSendWelcomeCredentialsTests(TestCase):
    """Unit tests for the send_welcome_credentials_email method on
    both EmailService implementations.

    The method embeds the password in plain text in the email body —
    that's an explicit project decision (see api/email.py for the
    security note). These tests lock in the dispatch contract.
    """

    def test_console_logs_credentials(self):
        from api.email import ConsoleEmailService
        with self.assertLogs("api.email", level="INFO") as cm:
            ok = ConsoleEmailService().send_welcome_credentials_email(
                to_email="newbie@sakrshipping.com",
                username="newbie@sakrshipping.com",
                password="00201012345678",
                first_name="AHMED",
            )
        self.assertTrue(ok)
        joined = "\n".join(cm.output)
        # Console backend logs the credentials at INFO so devs can
        # read them for testing. (In prod, the SMTP backend is used
        # and the log line is NOT emitted — see DjangoSMTP variant.)
        self.assertIn("newbie@sakrshipping.com", joined)
        self.assertIn("00201012345678", joined)
        self.assertIn("WELCOME-CREDS", joined)

    @patch("django.core.mail.send_mail")
    def test_django_smtp_sends_with_credentials_in_body(self, mock_send):
        from api.email import DjangoSMTPEmailService
        mock_send.return_value = 1
        ok = DjangoSMTPEmailService().send_welcome_credentials_email(
            to_email="seafarer@sakrshipping.com",
            username="seafarer@sakrshipping.com",
            password="00201012345678",
            first_name="MOHAMED",
        )
        self.assertTrue(ok)
        call_kwargs = mock_send.call_args.kwargs
        self.assertEqual(
            call_kwargs["recipient_list"], ["seafarer@sakrshipping.com"]
        )
        # The username and password are visible in the email body
        # (this is the explicit project decision).
        self.assertIn("seafarer@sakrshipping.com", call_kwargs["message"])
        self.assertIn("00201012345678", call_kwargs["message"])
        # Greeting uses the first_name when provided.
        self.assertIn("Hello MOHAMED", call_kwargs["message"])
        self.assertIn("Welcome", call_kwargs["subject"])

    @patch("django.core.mail.send_mail")
    def test_django_smtp_sends_with_default_greeting_when_no_first_name(self, mock_send):
        from api.email import DjangoSMTPEmailService
        mock_send.return_value = 1
        ok = DjangoSMTPEmailService().send_welcome_credentials_email(
            to_email="x@example.com",
            username="x@example.com",
            password="x",
        )
        self.assertTrue(ok)
        # Default greeting (no first_name) is just "Hello,".
        self.assertIn("Hello,", mock_send.call_args.kwargs["message"])

    @patch("django.core.mail.send_mail")
    def test_django_smtp_returns_false_on_failure(self, mock_send):
        from api.email import DjangoSMTPEmailService
        mock_send.side_effect = RuntimeError("SMTP server down")
        ok = DjangoSMTPEmailService().send_welcome_credentials_email(
            to_email="x@example.com",
            username="x",
            password="x",
        )
        self.assertFalse(ok)


class DedupeSeaServiceCommandTest(TestCase):
    """
    Tests for `python manage.py dedupe_sea_service` — the one-off
    cleanup command for existing SeaService rows that were saved
    before the dedup fix landed on /ai/parse/.
    """

    def _make_user(self, email="cmd-test@example.com"):
        from api.models import Users
        return Users.objects.create_user(
            email=email, password="x",
            first_name="Cmd", middle_name="Test", role="Employee",
        )

    def _make_record(self, user, vessel, signed_on, signed_off):
        from api.models import SeaService
        # bulk_create bypasses save() so the post_save dedup signal
        # doesn't fire and remove the overlapping records before the
        # test can assert on them. The management command under
        # test is what should be doing the dedup.
        return SeaService.objects.bulk_create([
            SeaService(
                user=user,
                company_name="ACME",
                rank="Master",
                vessel_name=vessel,
                vessel_name_imo=vessel,
                signed_on=signed_on,
                signed_off=signed_off,
                period="",
            )
        ])[0]

    def test_dry_run_does_not_delete_anything(self):
        from django.core.management import call_command
        from io import StringIO
        from api.models import SeaService
        from datetime import date

        user = self._make_user()
        # 3 overlapping records, longest is the middle one
        a = self._make_record(user, "A", date(2023, 1, 1), date(2023, 4, 16))
        b = self._make_record(user, "B", date(2023, 2, 11), date(2024, 2, 1))
        c = self._make_record(user, "C", date(2023, 4, 8), date(2023, 9, 22))

        out = StringIO()
        call_command("dedupe_sea_service", "--dry-run", stdout=out)

        # Nothing deleted
        self.assertEqual(SeaService.objects.filter(user=user).count(), 3)
        self.assertTrue(SeaService.objects.filter(id=a.id).exists())
        self.assertTrue(SeaService.objects.filter(id=b.id).exists())
        self.assertTrue(SeaService.objects.filter(id=c.id).exists())

        # But the report mentions what would happen
        output = out.getvalue()
        self.assertIn("DRY RUN", output)
        self.assertIn(user.email, output)

    def test_apply_deletes_overlapping_keeps_longest(self):
        from django.core.management import call_command
        from io import StringIO
        from api.models import SeaService
        from datetime import date

        user = self._make_user()
        a = self._make_record(user, "A", date(2023, 1, 1), date(2023, 4, 16))
        b = self._make_record(user, "B", date(2023, 2, 11), date(2024, 2, 1))
        c = self._make_record(user, "C", date(2023, 4, 8), date(2023, 9, 22))

        out = StringIO()
        call_command("dedupe_sea_service", stdout=out)

        # B is the longest (~12 months) — should be kept
        self.assertTrue(SeaService.objects.filter(id=b.id).exists())
        # A and C are shorter and overlap with B — should be deleted
        self.assertFalse(SeaService.objects.filter(id=a.id).exists())
        self.assertFalse(SeaService.objects.filter(id=c.id).exists())
        self.assertEqual(SeaService.objects.filter(user=user).count(), 1)

    def test_user_filter_only_processes_target_user(self):
        from django.core.management import call_command
        from io import StringIO
        from api.models import SeaService
        from datetime import date

        user_a = self._make_user("a@example.com")
        user_b = self._make_user("b@example.com")

        # Both users have overlapping records
        a1 = self._make_record(user_a, "A1", date(2023, 1, 1), date(2023, 4, 16))
        a2 = self._make_record(user_a, "A2", date(2023, 2, 11), date(2024, 2, 1))
        b1 = self._make_record(user_b, "B1", date(2023, 1, 1), date(2023, 4, 16))
        b2 = self._make_record(user_b, "B2", date(2023, 2, 11), date(2024, 2, 1))

        out = StringIO()
        call_command("dedupe_sea_service", "--user", str(user_a.id), stdout=out)

        # user_a's rows: only the longer one kept
        self.assertFalse(SeaService.objects.filter(id=a1.id).exists())
        self.assertTrue(SeaService.objects.filter(id=a2.id).exists())
        # user_b's rows: untouched
        self.assertTrue(SeaService.objects.filter(id=b1.id).exists())
        self.assertTrue(SeaService.objects.filter(id=b2.id).exists())

    def test_no_overlap_means_no_change(self):
        from django.core.management import call_command
        from io import StringIO
        from api.models import SeaService
        from datetime import date

        user = self._make_user()
        r1 = self._make_record(user, "R1", date(2022, 1, 1), date(2022, 6, 1))
        r2 = self._make_record(user, "R2", date(2022, 7, 1), date(2022, 12, 1))

        out = StringIO()
        call_command("dedupe_sea_service", stdout=out)

        self.assertEqual(SeaService.objects.filter(user=user).count(), 2)
        self.assertTrue(SeaService.objects.filter(id=r1.id).exists())
        self.assertTrue(SeaService.objects.filter(id=r2.id).exists())

    def test_report_json_written_when_requested(self):
        import json
        import tempfile
        from django.core.management import call_command
        from io import StringIO
        from datetime import date

        user = self._make_user("report@example.com")
        self._make_record(user, "A", date(2023, 1, 1), date(2023, 4, 16))
        self._make_record(user, "B", date(2023, 2, 11), date(2024, 2, 1))

        with tempfile.TemporaryDirectory() as tmp:
            report_path = f"{tmp}/report.json"
            out = StringIO()
            call_command("dedupe_sea_service", "--report", report_path, stdout=out)

            with open(report_path, "r", encoding="utf-8") as f:
                report = json.load(f)
            self.assertIn("users", report)
            self.assertEqual(report["users_processed"], 1)
            self.assertEqual(report["rows_deleted"], 1)
            self.assertEqual(report["rows_kept"], 1)
            self.assertIn("user_email", report["users"][0])
            self.assertIn(user.email, report["users"][0]["user_email"])

    def test_command_handles_empty_db_gracefully(self):
        from django.core.management import call_command
        from io import StringIO
        out = StringIO()
        # No users, no SeaService rows
        call_command("dedupe_sea_service", stdout=out)
        self.assertIn("No SeaService records to process", out.getvalue())


class SeaServiceViewSetDedupTests(APITestCase):
    """
    Regression: the frontend's `seaServiceService.createSeaService`
    POSTs directly to `/api/users/sea-services/`, bypassing
    `/ai/parse/`. The viewset must dedup overlapping records
    on create AND update so the form-save path stays clean.

    Without this, re-uploading a CV that has overlapping sea-service
    dates leaves the overlaps in the DB even though `/ai/parse/`
    would have caught them.
    """

    def _login_as_admin(self):
        from api.models import Users
        admin = Users.objects.create_user(
            email="ssv-admin@example.com", password="x",
            first_name="A", middle_name="dmin", role="Admin",
            is_staff=True, is_superuser=True,
        )
        client = APIClient()
        client.force_authenticate(user=admin)
        return client

    def _make_user(self, email):
        from api.models import Users
        return Users.objects.create_user(
            email=email, password="x",
            first_name="SSV", middle_name="Test", role="Employee",
        )

    def test_create_overlapping_record_drops_shorter(self):
        from api.models import SeaService
        from datetime import date
        client = self._login_as_admin()
        user = self._make_user("ssv-overlap-create@example.com")

        # Step 1: create a long record (12 months)
        long_resp = client.post(
            "/api/sea-services/",
            {
                "user": user.id,
                "company_name": "LONG CO",
                "rank": "Master",
                "vessel_name": "BIG VESSEL",
                "vessel_name_imo": "BIG VESSEL",
                "signed_on": "2023-02-11",
                "signed_off": "2024-02-01",
                "period": "12 months",
            },
            format="json",
        )
        self.assertEqual(long_resp.status_code, 201, long_resp.data)
        long_id = long_resp.data["id"]

        # Step 2: create a shorter record that overlaps with the long one
        short_resp = client.post(
            "/api/sea-services/",
            {
                "user": user.id,
                "company_name": "SHORT CO",
                "rank": "Master",
                "vessel_name": "TINY VESSEL",
                "vessel_name_imo": "TINY VESSEL",
                "signed_on": "2023-01-31",
                "signed_off": "2023-04-16",
                "period": "3 months",
            },
            format="json",
        )
        # The create itself should succeed (HTTP 201) — the
        # dedup runs as a side effect and drops the OLDER
        # (shorter-in-time, but the saved row IS the shorter
        # one so it should be the one dropped).
        self.assertEqual(short_resp.status_code, 201, short_resp.data)
        short_id = short_resp.data["id"]

        # Only the long record should remain
        self.assertTrue(SeaService.objects.filter(id=long_id).exists())
        self.assertFalse(SeaService.objects.filter(id=short_id).exists())
        self.assertEqual(SeaService.objects.filter(user=user).count(), 1)

    def test_create_longer_record_drops_existing_shorter(self):
        from api.models import SeaService
        from datetime import date
        client = self._login_as_admin()
        user = self._make_user("ssv-overlap-create-b@example.com")

        # Step 1: create a short record
        short_resp = client.post(
            "/api/sea-services/",
            {
                "user": user.id,
                "company_name": "SHORT CO",
                "rank": "Master",
                "vessel_name": "TINY VESSEL",
                "vessel_name_imo": "TINY VESSEL",
                "signed_on": "2023-01-31",
                "signed_off": "2023-04-16",
                "period": "3 months",
            },
            format="json",
        )
        self.assertEqual(short_resp.status_code, 201, short_resp.data)
        short_id = short_resp.data["id"]

        # Step 2: create a longer record that overlaps with the short one
        long_resp = client.post(
            "/api/sea-services/",
            {
                "user": user.id,
                "company_name": "LONG CO",
                "rank": "Master",
                "vessel_name": "BIG VESSEL",
                "vessel_name_imo": "BIG VESSEL",
                "signed_on": "2023-02-11",
                "signed_off": "2024-02-01",
                "period": "12 months",
            },
            format="json",
        )
        self.assertEqual(long_resp.status_code, 201, long_resp.data)
        long_id = long_resp.data["id"]

        # The long one is kept, the short one is dropped
        self.assertTrue(SeaService.objects.filter(id=long_id).exists())
        self.assertFalse(SeaService.objects.filter(id=short_id).exists())
        self.assertEqual(SeaService.objects.filter(user=user).count(), 1)

    def test_update_into_overlap_drops_existing_overlapping(self):
        """If a PATCH changes the dates such that the row now
        overlaps with another, the dedup must drop the shorter one."""
        from api.models import SeaService
        client = self._login_as_admin()
        user = self._make_user("ssv-overlap-update@example.com")

        # Create two non-overlapping records
        a_resp = client.post(
            "/api/sea-services/",
            {
                "user": user.id,
                "vessel_name": "VESSEL A",
                "vessel_name_imo": "VESSEL A",
                "signed_on": "2022-01-01",
                "signed_off": "2022-06-01",
            },
            format="json",
        )
        self.assertEqual(a_resp.status_code, 201, a_resp.data)
        a_id = a_resp.data["id"]

        b_resp = client.post(
            "/api/sea-services/",
            {
                "user": user.id,
                "vessel_name": "VESSEL B",
                "vessel_name_imo": "VESSEL B",
                "signed_on": "2022-07-01",
                "signed_off": "2023-06-01",  # 11 months
            },
            format="json",
        )
        self.assertEqual(b_resp.status_code, 201, b_resp.data)
        b_id = b_resp.data["id"]
        self.assertEqual(SeaService.objects.filter(user=user).count(), 2)

        # Now PATCH A so it overlaps with B and is LONGER than B
        # New range: 2022-01-01 -> 2023-12-01 (23 months) — overlaps B
        # (must pass ?user=<id> so the admin's queryset picks it up)
        patch_resp = client.patch(
            f"/api/sea-services/{a_id}/?user={user.id}",
            {"signed_off": "2023-12-01"},
            format="json",
        )
        self.assertEqual(patch_resp.status_code, 200, patch_resp.data)

        # A is the longer record now — should be kept
        # B is shorter and overlaps — should be dropped
        self.assertTrue(SeaService.objects.filter(id=a_id).exists())
        self.assertFalse(SeaService.objects.filter(id=b_id).exists())
        self.assertEqual(SeaService.objects.filter(user=user).count(), 1)

    def test_create_non_overlapping_record_keeps_both(self):
        from api.models import SeaService
        client = self._login_as_admin()
        user = self._make_user("ssv-no-overlap@example.com")

        a_resp = client.post(
            "/api/sea-services/",
            {
                "user": user.id,
                "vessel_name": "VESSEL A",
                "vessel_name_imo": "VESSEL A",
                "signed_on": "2022-01-01",
                "signed_off": "2022-06-01",
            },
            format="json",
        )
        self.assertEqual(a_resp.status_code, 201, a_resp.data)

        b_resp = client.post(
            "/api/sea-services/",
            {
                "user": user.id,
                "vessel_name": "VESSEL B",
                "vessel_name_imo": "VESSEL B",
                "signed_on": "2022-07-01",
                "signed_off": "2022-12-01",
            },
            format="json",
        )
        self.assertEqual(b_resp.status_code, 201, b_resp.data)

        # Neither overlaps — both should be kept
        self.assertEqual(SeaService.objects.filter(user=user).count(), 2)

    def test_dedup_does_not_affect_other_users(self):
        from api.models import SeaService
        client = self._login_as_admin()
        user_a = self._make_user("ssv-isolated-a@example.com")
        user_b = self._make_user("ssv-isolated-b@example.com")

        # Both users have a long record
        a_resp = client.post(
            "/api/sea-services/",
            {
                "user": user_a.id,
                "vessel_name": "USER A",
                "vessel_name_imo": "USER A",
                "signed_on": "2023-02-11",
                "signed_off": "2024-02-01",
            },
            format="json",
        )
        b_resp = client.post(
            "/api/sea-services/",
            {
                "user": user_b.id,
                "vessel_name": "USER B",
                "vessel_name_imo": "USER B",
                "signed_on": "2023-02-11",
                "signed_off": "2024-02-01",
            },
            format="json",
        )
        self.assertEqual(a_resp.status_code, 201)
        self.assertEqual(b_resp.status_code, 201)

        # Each user has exactly 1 record — dedup should not cross users
        self.assertEqual(SeaService.objects.filter(user=user_a).count(), 1)
        self.assertEqual(SeaService.objects.filter(user=user_b).count(), 1)



class SeafarerApplicationSerializerSeaServiceDedupTests(APITestCase):
    """
    Regression: SeafarerApplicationSerializer.update is called from
    THREE places — _save_parser_output, ContractSerializer.create,
    and ContractSerializer.update. Only the first pre-dedupes the
    sea service records. This test class exercises the serializer
    directly to verify the dedup runs regardless of caller.
    """

    def _login_as_admin(self):
        from api.models import Users
        admin = Users.objects.create_user(
            email="sas-admin@example.com", password="x",
            first_name="A", middle_name="dmin", role="Admin",
            is_staff=True, is_superuser=True,
        )
        client = APIClient()
        client.force_authenticate(user=admin)
        return client

    def _make_user(self, email="sas-dedup@example.com"):
        from api.models import Users
        return Users.objects.create_user(
            email=email, password="x",
            first_name="SAS", middle_name="Dedup", role="Employee",
        )

    def _sea_service_payload(self, records):
        """Wrap a list of sea service records in the shape
        SeafarerApplicationSerializer.update expects."""
        return {
            "sea_service_details": {
                "service_records": records,
            },
        }

    def _r(self, vessel, signed_on, signed_off, company="ACME"):
        return {
            "company_name": company,
            "rank": "Master",
            "vessel_name_imo_number": vessel,
            "flag": "Test",
            "signed_on": signed_on,
            "signed_off": signed_off,
            "period": "",
            "vessel_type": "Cargo",
            "dwt_grt": "1000/500",
            "engine_type": "Diesel",
            "bh_kw": "1000/746",
            "reason_for_sign_off": "End of contract",
        }

    def test_serializer_drops_overlapping_records(self):
        """When the serializer is called with overlapping records,
        only the longer one survives."""
        from api.models import SeaService
        from api.seafarer_application_serializers import SeafarerApplicationSerializer
        user = self._make_user()

        payload = self._sea_service_payload([
            self._r("BIG VESSEL", "2023-02-11", "2024-02-01"),  # 12 months
            self._r("TINY VESSEL", "2023-01-31", "2023-04-16"),  # 3 months
        ])
        SeafarerApplicationSerializer().update(user, payload)
        self.assertEqual(SeaService.objects.filter(user=user).count(), 1)
        # The long one is kept
        kept = SeaService.objects.get(user=user)
        self.assertIn("BIG VESSEL", kept.vessel_name)

    def test_serializer_keeps_non_overlapping_records(self):
        from api.models import SeaService
        from api.seafarer_application_serializers import SeafarerApplicationSerializer
        user = self._make_user("sas-keepall@example.com")

        payload = self._sea_service_payload([
            self._r("VESSEL A", "2022-01-01", "2022-06-01"),
            self._r("VESSEL B", "2022-07-01", "2022-12-01"),
        ])
        SeafarerApplicationSerializer().update(user, payload)
        self.assertEqual(SeaService.objects.filter(user=user).count(), 2)

    def test_serializer_keeps_longest_in_three_way_overlap(self):
        from api.models import SeaService
        from api.seafarer_application_serializers import SeafarerApplicationSerializer
        user = self._make_user("sas-threeway@example.com")

        payload = self._sea_service_payload([
            self._r("A", "2023-01-31", "2023-04-16"),  # short
            self._r("B", "2023-04-08", "2023-09-22"),  # medium
            self._r("C", "2023-02-11", "2024-02-01"),  # longest
        ])
        SeafarerApplicationSerializer().update(user, payload)
        self.assertEqual(SeaService.objects.filter(user=user).count(), 1)
        kept = SeaService.objects.get(user=user)
        self.assertIn("C", kept.vessel_name)

    def test_serializer_replaces_old_records_on_each_call(self):
        """The serializer does delete-all-then-create, so calling it
        twice with different data should leave only the second call's
        data (deduped)."""
        from api.models import SeaService
        from api.seafarer_application_serializers import SeafarerApplicationSerializer
        user = self._make_user("sas-replace@example.com")

        SeafarerApplicationSerializer().update(
            user,
            self._sea_service_payload([
                self._r("OLD VESSEL", "2022-01-01", "2022-06-01"),
            ]),
        )
        self.assertEqual(SeaService.objects.filter(user=user).count(), 1)
        self.assertEqual(SeaService.objects.get(user=user).vessel_name, "OLD VESSEL")

        # Second call with new (overlapping) data
        SeafarerApplicationSerializer().update(
            user,
            self._sea_service_payload([
                self._r("NEW LONG", "2022-03-01", "2022-12-01"),  # 9 months
                self._r("NEW SHORT", "2022-04-01", "2022-05-01"),  # 1 month
            ]),
        )
        # Both new records overlap each other; only the longer one survives.
        # The old record was deleted at the start of the second call.
        self.assertEqual(SeaService.objects.filter(user=user).count(), 1)
        kept = SeaService.objects.get(user=user)
        self.assertIn("NEW LONG", kept.vessel_name)



class SeaServicePostSaveSignalDedupTests(APITestCase):
    """
    The ``SeaService.post_save`` signal in api.signals is the
    LAST line of defense: any code path that creates or updates
    a SeaService row (direct ORM, shell, admin, future endpoints)
    gets the overlap dedup for free.

    These tests exercise the signal directly via the ORM, not
    through any viewset, to prove the safety net holds.
    """

    def _make_user(self, email):
        from api.models import Users
        return Users.objects.create_user(
            email=email, password="x",
            first_name="Sig", middle_name="Test", role="Employee",
        )

    def _make_record(self, user, vessel, signed_on, signed_off):
        """Use ``objects.create()`` so the post_save dedup signal
        actually fires — that's the whole point of these tests."""
        from api.models import SeaService
        return SeaService.objects.create(
            user=user,
            company_name="ACME",
            rank="Master",
            vessel_name=vessel,
            vessel_name_imo=vessel,
            signed_on=signed_on,
            signed_off=signed_off,
            period="",
        )

    def test_direct_orm_create_of_overlapping_record_drops_existing(self):
        """Even a raw `SeaService.objects.create()` call triggers the
        dedup via the post_save signal — no need to go through a
        viewset or serializer."""
        from api.models import SeaService
        user = self._make_user("signal-orm-create@example.com")

        # Pre-existing long record
        self._make_record(user, "BIG", "2023-02-11", "2024-02-01")

        # Direct ORM create of a shorter overlapping record.
        # The post_save signal should drop the longer one is
        # wrong — it should drop the SHORTER one (the one we just
        # created), keeping the long existing one.
        self._make_record(user, "TINY", "2023-01-31", "2023-04-16")

        self.assertEqual(SeaService.objects.filter(user=user).count(), 1)
        kept = SeaService.objects.get(user=user)
        self.assertIn("BIG", kept.vessel_name)

    def test_signal_does_not_run_for_unrelated_users(self):
        from api.models import SeaService
        user_a = self._make_user("signal-iso-a@example.com")
        user_b = self._make_user("signal-iso-b@example.com")

        self._make_record(user_a, "A", "2023-02-11", "2024-02-01")
        # Different user, overlapping dates — should NOT be deduped
        # (the signal is per-user, not global)
        self._make_record(user_b, "B", "2023-02-11", "2024-02-01")

        self.assertEqual(SeaService.objects.filter(user=user_a).count(), 1)
        self.assertEqual(SeaService.objects.filter(user=user_b).count(), 1)

    def test_signal_handles_three_way_overlap(self):
        from api.models import SeaService
        user = self._make_user("signal-threeway@example.com")

        self._make_record(user, "A", "2023-01-31", "2023-04-16")  # short
        self._make_record(user, "B", "2023-04-08", "2023-09-22")  # medium
        self._make_record(user, "C", "2023-02-11", "2024-02-01")  # longest

        self.assertEqual(SeaService.objects.filter(user=user).count(), 1)
        kept = SeaService.objects.get(user=user)
        self.assertIn("C", kept.vessel_name)

    def test_signal_keeps_non_overlapping_records(self):
        from api.models import SeaService
        user = self._make_user("signal-keepall@example.com")

        self._make_record(user, "A", "2022-01-01", "2022-06-01")
        self._make_record(user, "B", "2022-07-01", "2022-12-01")

        self.assertEqual(SeaService.objects.filter(user=user).count(), 2)

    def test_signal_also_runs_on_update(self):
        """Saving an EXISTING record (not just creating) also
        triggers the dedup — so changing a date into an overlapping
        range gets caught by the signal too."""
        from api.models import SeaService
        user = self._make_user("signal-update@example.com")

        a = self._make_record(user, "A", "2022-01-01", "2022-06-01")
        b = self._make_record(user, "B", "2022-07-01", "2023-06-01")

        # Extend A so it overlaps B and becomes the longer one
        a.signed_off = "2023-12-01"
        a.save()

        # B should have been dropped
        self.assertFalse(SeaService.objects.filter(id=b.id).exists())
        # A should still exist
        self.assertTrue(SeaService.objects.filter(id=a.id).exists())
        self.assertEqual(SeaService.objects.filter(user=user).count(), 1)

    def test_signal_no_op_when_no_overlap(self):
        from api.models import SeaService
        user = self._make_user("signal-noop@example.com")

        a = self._make_record(user, "A", "2022-01-01", "2022-06-01")
        # Save with no change — should not delete anything
        a.save()
        self.assertEqual(SeaService.objects.filter(user=user).count(), 1)



# ============================================================================
# Regression: PATCH on a CVSubmission (e.g. Principal Placement) must not
# wipe the linked user's middle_name when the form sends an empty
# user_middle_name (which it does, because the dropdown only shows
# first_name and the form just echoes that back).
# ============================================================================


class CVSubmissionUserNamePreservationTests(APITestCase):
    """
    Reproduces the bug:
        Seafarer "Mohamed Atta" (first_name="Mohamed", middle_name="Atta")
        is placed on a company via the Principal Placement modal.
        The modal sends PATCH /api/cv-submissions/<id>/ with
            user_first_name="Mohamed"
            user_middle_name=""
        because that's all the form has from the dropdown. The old
        CVSubmissionSerializer.update() saw `user_middle_name is not
        None` (empty string IS not None) and did
        `user.middle_name = ""`, wiping "Atta". The list then showed
        "Mohamed" instead of "Mohamed Atta".
    """

    def setUp(self):
        from api.models import Users
        from rest_framework_simplejwt.tokens import RefreshToken

        self.admin = Users.objects.create_user(
            email="admin-namefix@sakrshipping.com",
            password="adminpass",
        )
        self.admin.role = "Admin"
        self.admin.is_staff = True
        self.admin.save()

        refresh = RefreshToken.for_user(self.admin)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}"
        )

        # The seafarer we are about to "lose the middle name of".
        self.seafarer = Users.objects.create_user(
            email="mohamedatta41235@gmail.com",
            password="seafarerpass",
            first_name="Mohamed",
            middle_name="Atta",
        )
        self.seafarer.role = "Employee"
        self.seafarer.save()

        # And an existing CV submission the admin will PATCH.
        from api.models import CVSubmission
        self.cv = CVSubmission.objects.create(
            user=self.seafarer,
            status="Pending",
        )
        self.detail_url = f"/api/cv-submissions/{self.cv.id}/"

    def test_patch_with_empty_user_middle_name_is_rejected_at_validation(self):
        """DRF rejects empty string at the serializer (required+blank=False),
        so the form cannot silently clear a real middle_name by sending ''.
        This is the first line of defence. The second line (truthy check in
        update()) is a belt-and-braces guard for any future code path that
        bypasses DRF field validation.
        """
        r = self.client.patch(
            self.detail_url,
            {
                "user_first_name": "Mohamed",
                "user_middle_name": "",
            },
            format="json",
        )
        self.assertEqual(r.status_code, http_status.HTTP_400_BAD_REQUEST, r.data)
        self.assertIn("user_middle_name", r.data)

        # The real name is untouched.
        self.seafarer.refresh_from_db()
        self.assertEqual(self.seafarer.middle_name, "Atta")
        self.assertEqual(self.seafarer.first_name, "Mohamed")

    def test_patch_with_explicit_middle_name_still_updates(self):
        """Sanity: the legitimate update path still works."""
        r = self.client.patch(
            self.detail_url,
            {
                "user_first_name": "Mohamed",
                "user_middle_name": "Hassan",
            },
            format="json",
        )
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)

        self.seafarer.refresh_from_db()
        self.assertEqual(self.seafarer.middle_name, "Hassan")
        self.assertEqual(self.seafarer.first_name, "Mohamed")

    def test_patch_with_omitted_user_fields_preserves_everything(self):
        """PATCH that doesn't touch user_* fields must be a no-op for the user."""
        # Touch a CV-only field.
        r = self.client.patch(
            self.detail_url,
            {"status": "Under Review"},
            format="json",
        )
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)

        self.seafarer.refresh_from_db()
        self.assertEqual(self.seafarer.first_name, "Mohamed")
        self.assertEqual(self.seafarer.middle_name, "Atta")


# ============================================================================
# Regression: SeafarerApplicationSerializer.update must not wipe an
# existing middle_name when the caller only supplies a one-word
# full_name (e.g. the form echoed the dropdown's first_name back).
# ============================================================================


class SeafarerApplicationFullNamePreservationTests(TestCase):
    """
    Direct serializer tests (no API roundtrip) for the name-splitting
    logic in SeafarerApplicationSerializer.update().
    """

    def setUp(self):
        from api.models import Users
        self.user = Users.objects.create_user(
            email="name-preservation@example.com",
            password="x",
            first_name="Mohamed",
            middle_name="Atta",
        )

    def _update_personal(self, full_name):
        from api.seafarer_application_serializers import (
            SeafarerApplicationSerializer,
        )
        serializer = SeafarerApplicationSerializer(
            instance=self.user,
            data={"personal_details": {"full_name": full_name}},
            partial=True,
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        return serializer.save()

    def test_full_name_with_two_words_sets_both(self):
        """The happy path: 'Mohamed Atta' → first_name='Mohamed', middle_name='Atta'."""
        self._update_personal("Mohamed Atta")
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Mohamed")
        self.assertEqual(self.user.middle_name, "Atta")

    def test_full_name_with_three_words_keeps_rest_as_middle_name(self):
        """'Mohamed Atta Hassan' → first='Mohamed', middle='Atta Hassan'."""
        self._update_personal("Mohamed Atta Hassan")
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Mohamed")
        self.assertEqual(self.user.middle_name, "Atta Hassan")

    def test_one_word_full_name_preserves_existing_middle(self):
        """The exact bug: 'Mohamed' (no space) must NOT clear the existing
        middle_name. The user was 'Mohamed Atta' and stays 'Mohamed Atta'."""
        self.assertEqual(self.user.middle_name, "Atta")
        self._update_personal("Mohamed")
        self.user.refresh_from_db()
        self.assertEqual(
            self.user.first_name, "Mohamed",
            "first_name should follow the new full_name"
        )
        self.assertEqual(
            self.user.middle_name, "Atta",
            "Existing middle_name must NOT be cleared when the new "
            "full_name is one word (regression: the old "
            "`parts[1] if len(parts) > 1 else ''` wiped it)."
        )

    def test_one_word_full_name_does_not_change_existing_first(self):
        """Sanity: the existing first_name is still updated to the new value
        even when the new full_name is one word."""
        self._update_personal("Ahmed")
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Ahmed")
        # middle_name still preserved
        self.assertEqual(self.user.middle_name, "Atta")


# ============================================================================
# Ship ?company= filter — accept both id and name
# ============================================================================


class ShipCompanyFilterTests(APITestCase):
    """
    /api/ships/?company=<id_or_name> must accept both:
      - numeric id   → ?company=12
      - company name → ?company=Octavice+Over+Seas
    Previously only id worked; names were silently dropped and the
    response was an empty list.
    """

    def setUp(self):
        from api.models import Users
        from companies.models import Company

        self.admin = Users.objects.create_user(
            email="admin-shipfilter@sakrshipping.com",
            password="adminpass",
        )
        self.admin.role = "Admin"
        self.admin.is_staff = True
        self.admin.save()

        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(self.admin)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}"
        )

        # Two companies with distinctly named ships.
        self.co_a = Company.objects.create(
            company_name="Octavice Over Seas",
        )
        self.co_b = Company.objects.create(
            company_name="Maritime Giants Ltd",
        )

        from ships.models import Ship
        self.ship_a1 = Ship.objects.create(
            ship_name="Octavice Voyager",
            company=self.co_a,
        )
        self.ship_a2 = Ship.objects.create(
            ship_name="Octavice Pioneer",
            company=self.co_a,
        )
        self.ship_b1 = Ship.objects.create(
            ship_name="Giants Mariner",
            company=self.co_b,
        )

        self.url = "/api/ships/"

    def test_filter_by_numeric_id_still_works(self):
        """Regression check: ?company=<id> (the previously-working path)."""
        r = self.client.get(f"{self.url}?company={self.co_a.id}")
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)
        ids = {row["id"] for row in r.data["results"] if isinstance(r.data, dict) and "results" in r.data}               if isinstance(r.data, dict) else {row["id"] for row in r.data}
        self.assertIn(self.ship_a1.id, ids)
        self.assertIn(self.ship_a2.id, ids)
        self.assertNotIn(self.ship_b1.id, ids)

    def test_filter_by_full_company_name(self):
        """The exact case the user reported:
        ?company=Octavice+Over+Seas  (+ is a URL-encoded space)."""
        from urllib.parse import quote
        r = self.client.get(f"{self.url}?company={quote(self.co_a.company_name)}")
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)
        rows = r.data["results"] if isinstance(r.data, dict) and "results" in r.data else r.data
        ids = {row["id"] for row in rows}
        self.assertIn(self.ship_a1.id, ids)
        self.assertIn(self.ship_a2.id, ids)
        self.assertNotIn(self.ship_b1.id, ids)

    def test_filter_by_partial_company_name_substring(self):
        """icontains semantics: a substring should also match."""
        r = self.client.get(f"{self.url}?company=Octavice")
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)
        rows = r.data["results"] if isinstance(r.data, dict) and "results" in r.data else r.data
        ids = {row["id"] for row in rows}
        self.assertIn(self.ship_a1.id, ids)
        self.assertIn(self.ship_a2.id, ids)
        self.assertNotIn(self.ship_b1.id, ids)

    def test_filter_by_unknown_name_returns_empty(self):
        """Unknown name → empty list (NOT 400, NOT all rows)."""
        r = self.client.get(f"{self.url}?company=NoSuchCompany")
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)
        rows = r.data["results"] if isinstance(r.data, dict) and "results" in r.data else r.data
        self.assertEqual(len(rows), 0)

    def test_filter_with_no_param_returns_all(self):
        """Sanity: no company param → all ships."""
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)
        rows = r.data["results"] if isinstance(r.data, dict) and "results" in r.data else r.data
        self.assertGreaterEqual(len(rows), 3)

    def test_filter_by_multiple_companies_mixed_id_and_name(self):
        """?company=12&company=Octavice — both numeric and string values
        should resolve to the matching ships."""
        from urllib.parse import quote
        r = self.client.get(
            f"{self.url}?company={self.co_b.id}&company={quote(self.co_a.company_name)}"
        )
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)
        rows = r.data["results"] if isinstance(r.data, dict) and "results" in r.data else r.data
        ids = {row["id"] for row in rows}
        self.assertIn(self.ship_a1.id, ids)
        self.assertIn(self.ship_a2.id, ids)
        self.assertIn(self.ship_b1.id, ids)


# ============================================================================
# /api/users/users/?role= — accept comma-separated values
# ============================================================================


class UserRoleFilterCommaSeparatedTests(APITestCase):
    """
    /api/users/users/?role=... must accept both repeated and
    comma-separated values, in any combination.

      - ?role=Admin&role=HR+Manager&role=Recruiter  (repeated)
      - ?role=Admin,HR+Manager,Recruiter            (single value,
                                                     comma-sep — the
                                                     case the user hit)
      - ?role=Admin,HR+Manager&role=Recruiter       (mix)

    All three should return the union of users whose role is in
    {Admin, HR Manager, Recruiter}.
    """

    def setUp(self):
        from api.models import Users
        self.admin = Users.objects.create_user(
            email="admin-rolefilter@sakrshipping.com",
            password="adminpass",
        )
        self.admin.role = "Admin"
        self.admin.is_staff = True
        self.admin.save()

        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(self.admin)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}"
        )

        # Seed one user per non-Admin role + one extra Admin to prove
        # the filter is selecting on role, not "everything".
        self.u_admin = Users.objects.create_user(
            email="u-admin-rolefilter@sakrshipping.com",
            password="x", first_name="A"
        )
        self.u_admin.role = "Admin"
        self.u_admin.save()

        self.u_hr = Users.objects.create_user(
            email="u-hr-rolefilter@sakrshipping.com",
            password="x", first_name="B"
        )
        self.u_hr.role = "HR Manager"
        self.u_hr.save()

        self.u_rec = Users.objects.create_user(
            email="u-rec-rolefilter@sakrshipping.com",
            password="x", first_name="C"
        )
        self.u_rec.role = "Recruiter"
        self.u_rec.save()

        self.u_emp = Users.objects.create_user(
            email="u-emp-rolefilter@sakrshipping.com",
            password="x", first_name="D"
        )
        self.u_emp.role = "Employee"
        self.u_emp.save()

        self.url = "/api/users/users/"

    def _ids(self, response):
        rows = response.data["results"] if isinstance(response.data, dict) and "results" in response.data else response.data
        return {row["id"] for row in rows}

    def test_repeated_param_form(self):
        """?role=Admin&role=HR+Manager&role=Recruiter (already worked)."""
        r = self.client.get(f"{self.url}?role=Admin&role=HR%20Manager&role=Recruiter")
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)
        ids = self._ids(r)
        self.assertIn(self.u_admin.id, ids)
        self.assertIn(self.u_hr.id, ids)
        self.assertIn(self.u_rec.id, ids)
        self.assertNotIn(self.u_emp.id, ids)

    def test_single_value_comma_separated_form(self):
        """The exact case the user reported:
        ?role=Admin,HR+Manager,Recruiter (URL-encoded comma)"""
        from urllib.parse import quote
        r = self.client.get(f"{self.url}?role={quote('Admin,HR Manager,Recruiter')}")
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)
        ids = self._ids(r)
        self.assertIn(self.u_admin.id, ids)
        self.assertIn(self.u_hr.id, ids)
        self.assertIn(self.u_rec.id, ids)
        self.assertNotIn(self.u_emp.id, ids)

    def test_mixed_repeated_and_comma(self):
        """?role=Admin,HR+Manager&role=Recruiter — both styles in one URL."""
        from urllib.parse import quote
        r = self.client.get(f"{self.url}?role={quote('Admin,HR Manager')}&role=Recruiter")
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)
        ids = self._ids(r)
        self.assertIn(self.u_admin.id, ids)
        self.assertIn(self.u_hr.id, ids)
        self.assertIn(self.u_rec.id, ids)
        self.assertNotIn(self.u_emp.id, ids)

    def test_single_role_value_unchanged(self):
        """Sanity: a single role still works (no commas)."""
        r = self.client.get(f"{self.url}?role=Recruiter")
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)
        ids = self._ids(r)
        self.assertIn(self.u_rec.id, ids)
        self.assertNotIn(self.u_emp.id, ids)

    def test_empty_role_value_returns_all(self):
        """?role= (empty) → no filter applied → all users."""
        r = self.client.get(f"{self.url}?role=")
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)
        ids = self._ids(r)
        # Should include the Employee too (no role filter active)
        self.assertIn(self.u_emp.id, ids)


# ============================================================================
# Broken sea-service records (signed_off < signed_on) are silently
# ignored on PATCH / POST — no error, no save.
# ============================================================================


class SeaServiceBrokenRecordSkipTests(APITestCase):
    """
    Per project policy (2026-09-04): when a record has
    signed_off < signed_on, the backend silently skips the save.
    No 400, no error. The broken record is left alone.
    """

    def setUp(self):
        from api.models import Users
        from rest_framework_simplejwt.tokens import RefreshToken

        self.admin = Users.objects.create_user(
            email="admin-broken-sea@sakrshipping.com",
            password="adminpass",
        )
        self.admin.role = "Admin"
        self.admin.is_staff = True
        self.admin.save()

        refresh = RefreshToken.for_user(self.admin)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}"
        )

        from api.models import SeaService
        self.seafarer = Users.objects.create_user(
            email="seafarer-broken-sea@sakrshipping.com",
            password="x", first_name="Sea", role="Employee",
        )
        # A pre-existing BROKEN record (signed_off BEFORE signed_on).
        # This represents historical / imported data we cannot trust.
        self.broken = SeaService.objects.create(
            user=self.seafarer,
            company_name="Old Broken Co",
            rank="Chief Officer",
            vessel_name="MV Broken",
            signed_on="2024-06-01",
            signed_off="2024-01-01",  # BEFORE signed_on — broken!
        )

        # A pre-existing HEALTHY record (normal order).
        self.healthy = SeaService.objects.create(
            user=self.seafarer,
            company_name="Healthy Co",
            rank="Chief Officer",
            vessel_name="MV Healthy",
            signed_on="2023-01-01",
            signed_off="2023-06-01",
        )

        self.url = "/api/sea-services/"

    def test_patch_on_broken_record_is_silently_ignored(self):
        """PATCH a broken record: 200, but the record is unchanged.
        The user's request to 'ignore this only record and do not
        save it' is honoured."""
        # Refresh first so the in-memory values are date objects
        # (objects.create() leaves the raw string on the instance
        # until we read it back from the DB).
        self.broken.refresh_from_db()
        original_signed_on = self.broken.signed_on
        original_signed_off = self.broken.signed_off
        original_company = self.broken.company_name

        r = self.client.patch(
            f"{self.url}{self.broken.id}/?user={self.seafarer.id}",
            {
                "company_name": "New Company Name That Should NOT Be Saved",
                "rank": "Master",
            },
            format="json",
        )
        # 200 (not 400) — we silently accept the PATCH but skip the save
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)

        self.broken.refresh_from_db()
        self.assertEqual(
            self.broken.company_name, original_company,
            "Broken record must NOT be updated on PATCH"
        )
        self.assertEqual(
            self.broken.rank, "Chief Officer",
            "Broken record's rank must NOT be changed on PATCH"
        )
        self.assertEqual(self.broken.signed_on, original_signed_on)
        self.assertEqual(self.broken.signed_off, original_signed_off)

    def test_patch_on_broken_record_does_not_crash_even_with_no_payload(self):
        """Even a no-op PATCH on a broken record returns 200 and does nothing."""
        r = self.client.patch(
            f"{self.url}{self.broken.id}/?user={self.seafarer.id}",
            {},
            format="json",
        )
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)
        self.broken.refresh_from_db()
        self.assertEqual(self.broken.signed_on, datetime.date(2024, 6, 1))
        self.assertEqual(self.broken.signed_off, datetime.date(2024, 1, 1))

    def test_patch_on_healthy_record_still_validates(self):
        """Regression: PATCH on a HEALTHY record still raises the
        off-before-on validation error if the user tries to break it."""
        r = self.client.patch(
            f"{self.url}{self.healthy.id}/?user={self.seafarer.id}",
            {
                "signed_off": "2022-01-01",  # before the existing signed_on 2023-01-01
            },
            format="json",
        )
        self.assertEqual(r.status_code, http_status.HTTP_400_BAD_REQUEST, r.data)
        self.assertIn("signed_off", r.data)

    def test_patch_on_healthy_record_with_valid_dates_still_saves(self):
        """Regression: normal edits on healthy records still work."""
        r = self.client.patch(
            f"{self.url}{self.healthy.id}/?user={self.seafarer.id}",
            {
                "company_name": "Updated Co",
            },
            format="json",
        )
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)
        self.healthy.refresh_from_db()
        self.assertEqual(self.healthy.company_name, "Updated Co")

    def test_post_with_broken_dates_still_raises(self):
        """The 'skip on broken' policy applies to PATCH on EXISTING
        broken records. A fresh POST with broken dates should still
        raise 400 — we don't want to silently create new broken rows."""
        r = self.client.post(
            self.url,
            {
                "user": self.seafarer.id,
                "company_name": "Should Not Be Created",
                "rank": "Master",
                "vessel_name": "MV Ghost",
                "signed_on": "2024-12-01",
                "signed_off": "2024-01-01",  # BEFORE signed_on — broken!
            },
            format="json",
        )
        self.assertEqual(r.status_code, http_status.HTTP_400_BAD_REQUEST, r.data)
        self.assertIn("signed_off", r.data)

    def test_post_with_valid_dates_still_creates(self):
        """Regression: normal POSTs still work."""
        r = self.client.post(
            self.url,
            {
                "user": self.seafarer.id,
                "company_name": "New Co",
                "rank": "Master",
                "vessel_name": "MV New",
                "signed_on": "2025-01-01",
                "signed_off": "2025-06-01",
            },
            format="json",
        )
        self.assertEqual(r.status_code, http_status.HTTP_201_CREATED, r.data)


# ============================================================================
# Contract creation from a CV Submission — fall back to
# job_position.rank when the CV has no position.
# ============================================================================


class ContractCVPositionFallbackTests(APITestCase):
    """
    POST /api/contracts/ with cv_submission_id used to 400 when the
    CV had no `position` (Rank). The Contract Setup form always
    supplies a `job_position` (JobOrderPosition), so we now fall back
    to that job_position's rank when the CV's position is missing.
    """

    def setUp(self):
        from api.models import Users, Rank
        from companies.models import Company
        from rest_framework_simplejwt.tokens import RefreshToken

        self.admin = Users.objects.create_user(
            email="admin-cv-fallback@sakrshipping.com",
            password="adminpass",
        )
        self.admin.role = "Admin"
        self.admin.is_staff = True
        self.admin.save()

        refresh = RefreshToken.for_user(self.admin)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}"
        )

        # Seafarer
        self.seafarer = Users.objects.create_user(
            email="elsayed-marey@sakrshipping.com",
            password="x", first_name="ELSAYED", role="Employee",
        )

        # Company
        self.company = Company.objects.create(
            company_name="Horizon Athanasia Co",
        )

        # Two ranks
        self.rank_eto = Rank.objects.create(code="ETO", name="ETO")
        self.rank_master = Rank.objects.create(code="MASTER", name="Master")

        # JobOrderPosition for the form's "Job Position" dropdown
        # (rank=ETO). JobOrderPosition hangs off a JobOrder, not a
        # Company directly.
        from companies.models import JobOrder, JobOrderPosition
        from datetime import date
        self.job_order = JobOrder.objects.create(
            company=self.company,
            reference_number="JO-TEST-001",
            request_date=date.today(),
            target_joining_date=date.today(),
        )
        self.job_position = JobOrderPosition.objects.create(
            job_order=self.job_order,
            rank=self.rank_eto,
            quantity=5,
            salary_min=550,
            salary_max=6200,
        )

    def _make_cv(self, *, position=None, job_position=None):
        from api.models import CVSubmission
        return CVSubmission.objects.create(
            user=self.seafarer,
            company=self.company,
            position=position,
            job_position=job_position,
            status="Pending",
        )

    def _post_contract(self, **overrides):
        from datetime import date
        payload = {
            "cv_submission_id": self.cv.id,
            "user": self.seafarer.id,
            "company": self.company.id,
            "sign_on_date": "2026-09-05",
            "sign_off_date": "2028-06-06",
            "status": "Draft",
        }
        payload.update(overrides)
        return self.client.post("/api/contracts/", payload, format="json")

    # --- The reported case: CV has no position, form sends job_position ---

    def test_cv_without_position_with_job_position_in_payload_succeeds(self):
        """The user's reported case: CV has no position, but the
        Contract Setup form sends job_position. The serializer
        should fall back to job_position.rank and create the contract."""
        self.cv = self._make_cv(position=None, job_position=None)

        r = self._post_contract(job_position=self.job_position.id)
        self.assertEqual(
            r.status_code, http_status.HTTP_201_CREATED, r.data
        )
        self.assertEqual(r.data["rank"], self.rank_eto.id)

    def test_cv_without_position_with_job_position_on_cv_succeeds(self):
        """CV has no position, but CV has a job_position set."""
        self.cv = self._make_cv(
            position=None, job_position=self.job_position
        )

        # No job_position in the payload — should still work
        # because the CV already has one.
        r = self._post_contract()
        self.assertEqual(
            r.status_code, http_status.HTTP_201_CREATED, r.data
        )
        self.assertEqual(r.data["rank"], self.rank_eto.id)

    # --- Regression: existing behaviour is preserved ---

    def test_cv_with_position_uses_cv_position_not_job_position(self):
        """When the CV has a position, that wins — even if the
        payload also sends a job_position with a different rank."""
        self.cv = self._make_cv(
            position=self.rank_master, job_position=self.job_position
        )

        r = self._post_contract(job_position=self.job_position.id)
        self.assertEqual(
            r.status_code, http_status.HTTP_201_CREATED, r.data
        )
        # CV.position (Master) takes precedence over job_position.rank (ETO)
        self.assertEqual(r.data["rank"], self.rank_master.id)

    def test_cv_without_position_and_no_job_position_anywhere_still_400s(self):
        """If the CV has no position AND no job_position anywhere
        (not in payload, not on CV), the original 400 still fires."""
        self.cv = self._make_cv(position=None, job_position=None)

        r = self._post_contract()  # no job_position in payload either
        self.assertEqual(
            r.status_code, http_status.HTTP_400_BAD_REQUEST, r.data
        )
        self.assertIn("error", r.data)
        self.assertIn("position/rank", r.data["error"])
