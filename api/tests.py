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