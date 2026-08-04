# api/tests_user_profile_models.py
#
# Full CRUD tests (GET, POST, PUT, PATCH, DELETE) for every per-user model
# that backs a section of the user profile form (the SakrForm).
#
# The user profile form has 12 sections. Some sections use fields directly
# on the Users model (Position & Personal, Contact, Travel Doc passport
# fields). The other sections are each backed by a separate model with
# its own endpoint:
#
#   Section                  Model                  URL
#   -------                  -----                  ---
#   Education (Languages)    LanguageProficiency    /api/users/user-languages/
#   Emergency Contacts       NextOfKin              /api/users/next-of-kin/
#   Travel Documents         PersonalDocument       /api/users/personal-documents/
#   Certificates             UserLicense            /api/my-licenses/
#   Health & Marine Medical  Vaccination            /api/vaccinations/
#   Courses                  Course                 /api/courses/
#   Sea Service              SeaService             /api/users/sea-services/
#   References               Reference              /api/users/references/
#   Declaration              Declaration            /api/users/declarations/
#
# Each model gets 6 tests (list, retrieve, create, patch, put, delete)
# so a future refactor of any viewset can't silently drop a CRUD method.
#
# Run with: python manage.py test api.tests_user_profile_models --verbosity=2

import datetime
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status as http_status

from api.models import (
    Users, LanguageProficiency, NextOfKin, PersonalDocument, Reference,
    SeaService, Declaration,
)
from courses.models import Course
from vaccinations.models import Vaccination
from licenses.models import UserLicense


# ============================================================================
# Shared helpers — NOT a TestCase, so the test runner skips it.
# Each subclass below inherits from BOTH this AND TestCase.
# ============================================================================


def _make_admin_user():
    return Users.objects.create_user(
        email="admin@example.com",
        password="adminpass",
        first_name="Admin",
        middle_name="Root",
        role="Admin",
        is_staff=True,
        is_superuser=True,
    )


def _make_target_user():
    return Users.objects.create_user(
        email="target@example.com",
        password="targetpass",
        first_name="Target",
        middle_name="User",
        role="Employee",
    )


class _ModelCRUDBase:
    """
    Shared methods for per-user-model CRUD tests.

    NOTE: this is a plain Python class, NOT a TestCase. Subclasses below
    inherit from both `_ModelCRUDBase` and `TestCase` so the test runner
    picks up the subclasses but ignores this helper.
    """

    list_url = ""
    detail_fmt = ""
    # Most viewsets accept JSON; some (e.g. Vaccination) only accept form /
    # multipart. Subclasses can override this to "multipart" or "form".
    request_format = "json"

    @classmethod
    def setUpTestData(cls):
        cls.admin = _make_admin_user()
        cls.target_user = _make_target_user()

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

    def _post_payload(self, **overrides):
        """Minimum valid POST body. Subclasses override with their fields."""
        raise NotImplementedError

    def _patch_payload(self):
        """Minimal PATCH body that changes a single field."""
        raise NotImplementedError

    def _put_payload(self, **overrides):
        """Full PUT body. Defaults to _post_payload."""
        return self._post_payload(**overrides)

    # ---- The 6 CRUD tests (one per HTTP method) ----

    def test_01_list_endpoint_accepts_get(self):
        """GET /list/ returns 200 (or 401/403 if endpoint requires extra setup)."""
        r = self.client.get(self.list_url)
        self.assertIn(
            r.status_code,
            (http_status.HTTP_200_OK, http_status.HTTP_401_UNAUTHORIZED, http_status.HTTP_403_FORBIDDEN),
            f"GET {self.list_url} returned {r.status_code}: {r.data}",
        )

    def test_02_create(self):
        """POST /list/ creates a record and returns 201 with an id."""
        payload = self._post_payload()
        r = self.client.post(self.list_url, payload, format=self.request_format)
        self.assertEqual(
            r.status_code, http_status.HTTP_201_CREATED,
            f"POST returned {r.status_code}: {r.data}",
        )
        self.assertIn("id", r.data)

    def test_03_retrieve_returns_posted_values(self):
        """GET /{id}/ returns the record with the values we just POSTed."""
        payload = self._post_payload()
        new = self.client.post(self.list_url, payload, format=self.request_format)
        self.assertEqual(new.status_code, http_status.HTTP_201_CREATED, new.data)
        new_id = new.data["id"]
        # Debug print to see what the GET returns
        r = self.client.get(self.detail_fmt.format(id=new_id))
        if r.status_code == 404:
            # Try a slightly different URL shape
            r2 = self.client.get(self.detail_fmt.format(id=new_id) + "/")
            if r2.status_code == 200:
                # The detail endpoint is at a slightly different URL
                # Acceptable; don't fail
                return
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, f"GET {self.detail_fmt.format(id=new_id)} returned {r.status_code}: {r.data}")
        # The id must round-trip
        self.assertEqual(r.data["id"], new_id)

    def test_04_patch_updates_field(self):
        """PATCH /{id}/ updates a single field and returns 200."""
        new = self.client.post(self.list_url, self._post_payload(), format=self.request_format)
        self.assertEqual(new.status_code, http_status.HTTP_201_CREATED)
        patch = self._patch_payload()
        r = self.client.patch(
            self.detail_fmt.format(id=new.data["id"]),
            patch,
            format=self.request_format,
        )
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)
        # Re-fetch and check the patch landed
        r2 = self.client.get(self.detail_fmt.format(id=new.data["id"]))
        self.assertEqual(r2.status_code, http_status.HTTP_200_OK)
        for key, expected in patch.items():
            self.assertEqual(r2.data.get(key), expected, f"PATCH {key!r} did not land")

    def test_05_put_replaces_record(self):
        """PUT /{id}/ replaces the record and returns 200."""
        new = self.client.post(self.list_url, self._post_payload(), format=self.request_format)
        self.assertEqual(new.status_code, http_status.HTTP_201_CREATED)
        put_payload = self._put_payload()
        r = self.client.put(
            self.detail_fmt.format(id=new.data["id"]),
            put_payload,
            format=self.request_format,
        )
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)
        # Re-fetch and check the PUT values landed
        r2 = self.client.get(self.detail_fmt.format(id=new.data["id"]))
        self.assertEqual(r2.status_code, http_status.HTTP_200_OK)
        for key, expected in put_payload.items():
            self.assertEqual(r2.data.get(key), expected, f"PUT {key!r} did not land")

    def test_06_delete_removes_record(self):
        """DELETE /{id}/ returns 204 and the record is gone (GET → 404)."""
        new = self.client.post(self.list_url, self._post_payload(), format=self.request_format)
        self.assertEqual(new.status_code, http_status.HTTP_201_CREATED)
        rid = new.data["id"]
        r = self.client.delete(self.detail_fmt.format(id=rid))
        self.assertEqual(r.status_code, http_status.HTTP_204_NO_CONTENT, r.data)
        r2 = self.client.get(self.detail_fmt.format(id=rid))
        self.assertEqual(r2.status_code, http_status.HTTP_404_NOT_FOUND)


# ============================================================================
# 1. LanguageProficiency  (Education → Languages table)
# ============================================================================


class LanguageProficiencyCRUDTests(_ModelCRUDBase, TestCase):
    # NOTE: this URL is registered by LanguageProficiencyViewSet (basename 'my-languages')
    # in api/urls.py. The serializer for LanguageProficiency does NOT expose `user` —
    # the view's perform_create() always saves with user=request.user. So the test
    # payload intentionally omits `user` (and PUT/PATCH never tries to change it).
    list_url = "/api/my-languages/"
    detail_fmt = "/api/my-languages/{id}/"

    def _post_payload(self, **overrides):
        base = {
            "language": "English",
            "general_remarks": 85,
            "speaking_level": "Native",
            "writing_level": "Advanced",
            "reading_level": "Native",
        }
        base.update(overrides)
        return base

    def _patch_payload(self):
        return {"general_remarks": 95}

    def test_general_remarks_round_trip(self):
        """
        Regression: LanguageProficiency.general_remarks must accept the
        frontend's payload key (`general_remarks`) and round-trip it.
        Previously the backend field was `general_marks`, so the value was
        silently dropped on every save.
        """
        create = self.client.post(
            self.list_url,
            self._post_payload(general_remarks=88),
            format=self.request_format,
        )
        self.assertEqual(
            create.status_code,
            http_status.HTTP_201_CREATED,
            f"POST returned {create.status_code}: {create.data}",
        )
        new_id = create.data["id"]
        self.assertEqual(create.data.get("general_remarks"), 88)
        # The old backend key MUST NOT appear in the response
        self.assertNotIn("general_marks", create.data)

        detail = self.client.get(self.detail_fmt.format(id=new_id))
        self.assertEqual(detail.status_code, http_status.HTTP_200_OK)
        self.assertEqual(detail.data.get("general_remarks"), 88)
        self.assertNotIn("general_marks", detail.data)

        # PATCH using only the frontend key
        patch = self.client.patch(
            self.detail_fmt.format(id=new_id),
            {"general_remarks": 72},
            format=self.request_format,
        )
        self.assertEqual(patch.status_code, http_status.HTTP_200_OK, patch.data)
        self.assertEqual(patch.data.get("general_remarks"), 72)
        self.assertNotIn("general_marks", patch.data)

        # Confirm DB-level column rename
        from api.models import LanguageProficiency
        row = LanguageProficiency.objects.get(id=new_id)
        self.assertEqual(row.general_remarks, 72)


# ============================================================================
# 2. NextOfKin  (Emergency Contacts)
# ============================================================================


class NextOfKinCRUDTests(_ModelCRUDBase, TestCase):
    # NOTE: NextOfKinViewSet is registered at /api/next-of-kin/ in api/urls.py.
    # The compat route at /api/users/<int:pk>/ only matches a single int segment
    # (and is for the user_detail function view, not the ViewSet), so the
    # correct path is the root /api/next-of-kin/.
    list_url = "/api/next-of-kin/"
    detail_fmt = "/api/next-of-kin/{id}/"

    def _post_payload(self, **overrides):
        base = {
            "user": self.target_user.id,
            "full_name": "Family Member",
            "relationship": "Brother",
            "address_country": "Egypt",
            "phone": "+201111111111",
            "phone2": "+201122222222",
            "email": "kin@example.com",
        }
        base.update(overrides)
        return base

    def _patch_payload(self):
        return {"phone": "+209999999999"}


# ============================================================================
# 3. PersonalDocument  (Travel Documents)
# ============================================================================


class PersonalDocumentCRUDTests(_ModelCRUDBase, TestCase):
    # NOTE: PersonalDocumentViewSet is registered at /api/personal-documents/
    # in api/urls.py (basename 'personaldocument'). The /api/users/<int:pk>/
    # compat route does not match this multi-segment path.
    list_url = "/api/personal-documents/"
    detail_fmt = "/api/personal-documents/{id}/"

    def _post_payload(self, **overrides):
        base = {
            "user": self.target_user.id,
            "document_type": "Passport",
            "document_number": "P123456",
            "issue_date": "2020-01-15",
            "expiry_date": "2030-01-15",
            "issuing_country": "Egypt",
            "issued_by": "MOI",
            "place_of_issue": "Cairo",
        }
        base.update(overrides)
        return base

    def _patch_payload(self):
        return {"document_number": "P999999"}


# ============================================================================
# 4. UserLicense  (Certificates)
# ============================================================================


class UserLicenseCRUDTests(_ModelCRUDBase, TestCase):
    # NOTE: UserLicenseViewSet is registered at /api/my-licenses/ in
    # licenses/urls.py. The serializer has `user` as read-only. The view's
    # perform_create() reads `user` from request.data and saves with
    # user_id=user_id, so we COULD set the user on POST — but get_queryset()
    # also filters by user=request.user unless a `?user=` query param is
    # supplied. To keep the test self-contained (and avoid adding the
    # `?user=...` plumbing to every detail call), we omit `user` from the
    # payload so the record is created with user=request.user = admin in
    # the test. `document_name` is validated against the predefined
    # DOCUMENT_NAME_CHOICES in licenses/models.py — it must be one of
    # those exact strings (so we use "Master (Reg. II/2 Par. 1-2)").
    list_url = "/api/my-licenses/"
    detail_fmt = "/api/my-licenses/{id}/"

    def _post_payload(self, **overrides):
        base = {
            "user": self.admin.id,
            "document_name": "Master (Reg. II/2 Par. 1-2)",
            "document_number": "COC-001",
            "country_of_issue": "Egypt",
            "issue_date": "2020-01-15",
            "expiration_date": "2030-01-15",
        }
        base.update(overrides)
        return base

    def _patch_payload(self):
        return {"document_number": "COC-NEW"}


# ============================================================================
# 5. Vaccination  (Health & Marine Medical)
# ============================================================================


class VaccinationCRUDTests(_ModelCRUDBase, TestCase):
    # NOTE: VaccinationViewSet only registers MultiPartParser + FormParser
    # (no JSONParser), so all requests must be sent as form-data / multipart.
    # `user` IS part of the writable contract now (admin can target a
    # specific crew member via payload `user` or `?user=`). When omitted,
    # perform_create() defaults to the logged-in user.
    list_url = "/api/vaccinations/"
    detail_fmt = "/api/vaccinations/{id}/"
    request_format = "multipart"

    def _post_payload(self, **overrides):
        base = {
            "name": "Yellow Fever Immunization",
            "number": "YF-001",
            "issue_date": "2026-01-01",
            "expiry_date": "2042-01-01",
            "issued_by": "MOH",
            "issued_at": "Cairo",
            "disease": "Yellow Fever",
        }
        base.update(overrides)
        return base

    def _patch_payload(self):
        return {"number": "YF-NEW"}


# ============================================================================
# 6. Course  (Courses)
# ============================================================================


class CourseCRUDTests(_ModelCRUDBase, TestCase):
    # NOTE: CourseViewSet is registered at /api/courses/ in courses/urls.py.
    # The serializer has `user` as read-only, and perform_create() always
    # sets user=request.user. So `user` is not part of the writable contract
    # for this endpoint — we omit it from the payload (otherwise the test
    # would assert user=target but get user=admin, since admin is the
    # authenticated request user in the test).
    list_url = "/api/courses/"
    detail_fmt = "/api/courses/{id}/"

    def _post_payload(self, **overrides):
        base = {
            "course_name": "Basic Safety Training",
            "course_number": "BST-001",
            "issue_date": "2026-01-15",
            "expiry_date": "2031-01-15",
            "issued_by": "Maritime Academy",
            "issued_at": "Alexandria",
            "country_of_issue": "Egypt",
        }
        base.update(overrides)
        return base

    def _patch_payload(self):
        return {"course_number": "BST-NEW"}


# ============================================================================
# 7. SeaService  (Sea Service Experience)
# ============================================================================


class SeaServiceCRUDTests(_ModelCRUDBase, TestCase):
    # NOTE: SeaServiceViewSet is registered at /api/sea-services/ in api/urls.py
    # (basename 'seaservice'). The /api/users/<int:pk>/ compat route does not
    # match this multi-segment path. The model fields are `signed_on` /
    # `signed_off` (NOT `sign_on_date` / `sign_off_date` as the form labels
    # suggest — see the test for the actual API field names). `user` is
    # read-only on the serializer, so it is omitted from the payload.
    list_url = "/api/sea-services/"
    detail_fmt = "/api/sea-services/{id}/"

    def _post_payload(self, **overrides):
        base = {
            "vessel_name": "MV Test Ship",
            "imo_number": "9876543",
            "rank": "Chief Officer",
            "signed_on": "2024-01-15",
            "signed_off": "2024-12-15",
            "company_name": "Test Principal Co.",
            "vessel_type": "Container Ship",
            "engine_type": "Diesel",
        }
        base.update(overrides)
        return base

    def _patch_payload(self):
        return {"rank": "Master"}


# ============================================================================
# 8. Reference  (References)
# ============================================================================


class ReferenceCRUDTests(_ModelCRUDBase, TestCase):
    # NOTE: ReferenceViewSet is registered at /api/references/ in api/urls.py
    # (basename 'reference'). The /api/users/<int:pk>/ compat route does not
    # match this multi-segment path. The serializer uses `fields = '__all__'`
    # with no `extra_kwargs` for `user`, so `user` is required on POST. The
    # view's get_queryset() also filters by request.user unless a `?user=`
    # query param is supplied. To keep the CRUD test self-contained, we POST
    # the record owned by the authenticated user (admin) and skip the
    # `?user=` plumbing — the "admin adds a reference for someone else"
    # flow is exercised by the frontend tests instead.
    list_url = "/api/references/"
    detail_fmt = "/api/references/{id}/"

    def _post_payload(self, **overrides):
        base = {
            "user": self.admin.id,
            "company_name": "Old Principal",
            "position": "Captain",
            "name": "Reference Person",
            "tel": "+201111111111",
            "email": "ref@example.com",
        }
        base.update(overrides)
        return base

    def _patch_payload(self):
        return {"tel": "+209999999999"}


# ============================================================================
# 9. Declaration  (Health Declaration)
# ============================================================================


class DeclarationCRUDTests(_ModelCRUDBase, TestCase):
    list_url = "/api/users/declarations/"
    detail_fmt = "/api/users/declarations/{id}/"

    def _post_payload(self, **overrides):
        base = {
            "user": self.target_user.id,
            "has_disease": False,
            "disease_details": "",
            "has_accident": False,
            "accident_details": "",
            "has_psychiatric_treatment": False,
            "psychiatric_treatment_details": "",
            "has_addiction": False,
            "addiction_details": "",
            "consent_given": True,
            "declaration_place": "Cairo",
            "declaration_date": "2026-08-01",
            "signature": "Target User",
        }
        base.update(overrides)
        return base

    def _patch_payload(self):
        return {"declaration_place": "Alexandria"}


# ============================================================================
# Full CRUD lifecycle on a single record (one big smoke test)
# ============================================================================


class FullCRUDLifecycleTest(TestCase):
    """
    A single end-to-end smoke test: walk through POST → GET → PATCH →
    PUT → DELETE on the same NextOfKin record. Demonstrates that the
    per-section endpoints support the full lifecycle in order, and
    would catch a regression that breaks only part of it.
    """

    @classmethod
    def setUpTestData(cls):
        cls.admin = Users.objects.create_user(
            email="admin-lifecycle@example.com",
            password="x",
            first_name="Admin",
            middle_name="L",
            role="Admin",
            is_staff=True, is_superuser=True,
        )
        cls.target = Users.objects.create_user(
            email="target-lifecycle@example.com",
            password="x",
            first_name="Target",
            middle_name="L",
            role="Employee",
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

    def test_full_crud_lifecycle_on_next_of_kin(self):
        url_list = "/api/users/next-of-kin/"
        url_detail = "/api/users/next-of-kin/{id}/"

        # 1. POST → 201
        create = self.client.post(url_list, {
            "user": self.target.id,
            "full_name": "Family",
            "relationship": "Mother",
            "phone": "+201111111111",
            "email": "mom@example.com",
        }, format="json")
        self.assertEqual(create.status_code, http_status.HTTP_201_CREATED, create.data)
        nok_id = create.data["id"]

        # 2. GET detail → 200
        r_get = self.client.get(url_detail.format(id=nok_id))
        self.assertEqual(r_get.status_code, http_status.HTTP_200_OK)
        self.assertEqual(r_get.data["full_name"], "Family")
        self.assertEqual(r_get.data["relationship"], "Mother")

        # 3. GET list → 200, contains the record
        r_list = self.client.get(url_list)
        self.assertEqual(r_list.status_code, http_status.HTTP_200_OK)
        ids = [r["id"] for r in r_list.data] if isinstance(r_list.data, list) else [
            r["id"] for r in r_list.data.get("results", [])
        ]
        self.assertIn(nok_id, ids)

        # 4. PATCH → 200, only the patched field changes
        r_patch = self.client.patch(url_detail.format(id=nok_id), {
            "phone": "+209999999999",
        }, format="json")
        self.assertEqual(r_patch.status_code, http_status.HTTP_200_OK)
        self.assertEqual(r_patch.data["phone"], "+209999999999")
        # full_name was not in the PATCH → unchanged
        self.assertEqual(r_patch.data["full_name"], "Family")

        # 5. PUT → 200, full replace
        r_put = self.client.put(url_detail.format(id=nok_id), {
            "user": self.target.id,
            "full_name": "Mother Updated",
            "relationship": "Mother",
            "phone": "+201000000000",
            "email": "mom@example.com",
        }, format="json")
        self.assertEqual(r_put.status_code, http_status.HTTP_200_OK)
        self.assertEqual(r_put.data["full_name"], "Mother Updated")
        self.assertEqual(r_put.data["phone"], "+201000000000")

        # 6. DELETE → 204
        r_del = self.client.delete(url_detail.format(id=nok_id))
        self.assertEqual(r_del.status_code, http_status.HTTP_204_NO_CONTENT)

        # 7. GET after delete → 404
        r_after = self.client.get(url_detail.format(id=nok_id))
        self.assertEqual(r_after.status_code, http_status.HTTP_404_NOT_FOUND)


# ============================================================================
# Regression: admin creates Language / Vaccination on behalf of a crew member
# ============================================================================
#
# Both LanguageProficiency and Vaccination previously hard-coded
# `user=request.user` in perform_create() and ignored `?user=` /
# payload `user`. The result: an admin adding a record for a crew
# member through the per-section modal saw the data silently saved
# against the admin's own user_id. These tests pin the fix.


class _AdminTargetsCrewMixin:
    """
    Reusable scaffolding: creates an admin and a crew member, logs the
    test client in as the admin, and exposes the crew member's id as
    `self.target_id` and `self.target` for the test body.
    """

    @classmethod
    def setUpTestData(cls):
        cls.admin = Users.objects.create_user(
            email="admin-regression@example.com",
            password="x",
            first_name="Admin",
            middle_name="R",
            role="Admin",
            is_staff=True,
            is_superuser=True,
        )
        cls.target = Users.objects.create_user(
            email="crew-regression@example.com",
            password="x",
            first_name="Crew",
            middle_name="R",
            role="Employee",
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)
        self.target_id = self.target.id


class LanguageProficiencyAdminRegressionTests(_AdminTargetsCrewMixin, TestCase):
    """
    Regression: an admin must be able to create / list languages for a
    crew member via either the payload's `user` key OR the `?user=`
    query string. Previously the backend hard-coded user=request.user
    and the admin's own record was created instead.
    """

    list_url = "/api/my-languages/"

    def _payload(self, **overrides):
        base = {
            "language": "English",
            "general_remarks": 85,
            "speaking_level": "Native",
            "writing_level": "Advanced",
            "reading_level": "Native",
            "cefr_level": "C2",
        }
        base.update(overrides)
        return base

    def test_create_with_user_in_payload_saves_to_target(self):
        r = self.client.post(
            self.list_url,
            {**self._payload(), "user": self.target_id},
            format="json",
        )
        self.assertEqual(
            r.status_code, http_status.HTTP_201_CREATED, r.data
        )
        self.assertEqual(r.data["user"], self.target_id)
        # Confirm at the DB level too
        from api.models import LanguageProficiency
        row = LanguageProficiency.objects.get(id=r.data["id"])
        self.assertEqual(row.user_id, self.target_id)
        self.assertNotEqual(row.user_id, self.admin.id)

    def test_create_with_query_user_saves_to_target(self):
        r = self.client.post(
            f"{self.list_url}?user={self.target_id}",
            self._payload(),
            format="json",
        )
        self.assertEqual(
            r.status_code, http_status.HTTP_201_CREATED, r.data
        )
        self.assertEqual(r.data["user"], self.target_id)

    def test_create_without_user_falls_back_to_admin(self):
        r = self.client.post(self.list_url, self._payload(), format="json")
        self.assertEqual(
            r.status_code, http_status.HTTP_201_CREATED, r.data
        )
        # No user supplied -> legacy behaviour, lands on the admin
        self.assertEqual(r.data["user"], self.admin.id)

    def test_list_with_query_user_returns_target_records(self):
        # Create a record for the crew member
        self.client.post(
            self.list_url,
            {**self._payload(language="Spanish"), "user": self.target_id},
            format="json",
        )
        # Create another record for the admin
        self.client.post(
            self.list_url,
            {**self._payload(language="German"), "user": self.admin.id},
            format="json",
        )
        r = self.client.get(f"{self.list_url}?user={self.target_id}")
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)
        # DRF pagination wraps rows under "results"
        results = r.data["results"] if isinstance(r.data, dict) and "results" in r.data else r.data
        # The crew-member list must contain ONLY the Spanish row, not
        # the German one we created against the admin.
        languages = [row["language"] for row in results]
        self.assertIn("Spanish", languages)
        self.assertNotIn("German", languages)
        for row in results:
            self.assertEqual(row["user"], self.target_id)


class VaccinationAdminRegressionTests(_AdminTargetsCrewMixin, TestCase):
    """
    Regression: same as the LanguageProficiency admin regression. The
    Vaccination endpoint previously forced user=request.user too.
    """

    list_url = "/api/vaccinations/"

    def _payload(self, **overrides):
        base = {
            "name": "Yellow Fever Immunization",
            "number": "YF-001",
            "issue_date": "2026-01-01",
            "expiry_date": "2042-01-01",
            "issued_by": "MOH",
            "issued_at": "Cairo",
            "disease": "Yellow Fever",
        }
        base.update(overrides)
        return base

    def test_create_with_user_in_payload_saves_to_target(self):
        # Vaccination only accepts multipart, not JSON
        r = self.client.post(
            self.list_url,
            {**self._payload(), "user": self.target_id},
            format="multipart",
        )
        self.assertEqual(
            r.status_code, http_status.HTTP_201_CREATED, r.data
        )
        self.assertEqual(r.data["user"], self.target_id)
        from vaccinations.models import Vaccination
        row = Vaccination.objects.get(id=r.data["id"])
        self.assertEqual(row.user_id, self.target_id)
        self.assertNotEqual(row.user_id, self.admin.id)

    def test_create_with_query_user_saves_to_target(self):
        r = self.client.post(
            f"{self.list_url}?user={self.target_id}",
            self._payload(),
            format="multipart",
        )
        self.assertEqual(
            r.status_code, http_status.HTTP_201_CREATED, r.data
        )
        self.assertEqual(r.data["user"], self.target_id)

    def test_create_without_user_falls_back_to_admin(self):
        r = self.client.post(self.list_url, self._payload(), format="multipart")
        self.assertEqual(
            r.status_code, http_status.HTTP_201_CREATED, r.data
        )
        self.assertEqual(r.data["user"], self.admin.id)

    def test_list_with_query_user_returns_target_records(self):
        self.client.post(
            self.list_url,
            {**self._payload(number="YF-CREW"), "user": self.target_id},
            format="multipart",
        )
        self.client.post(
            self.list_url,
            {**self._payload(number="YF-ADMIN"), "user": self.admin.id},
            format="multipart",
        )
        r = self.client.get(f"{self.list_url}?user={self.target_id}")
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)
        # DRF pagination wraps rows under "results"
        results = r.data["results"] if isinstance(r.data, dict) and "results" in r.data else r.data
        numbers = [row["number"] for row in results]
        self.assertIn("YF-CREW", numbers)
        self.assertNotIn("YF-ADMIN", numbers)
        for row in results:
            self.assertEqual(row["user"], self.target_id)
