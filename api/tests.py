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
from django.test import TestCase
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
