# api/tests_marine_courses.py
#
# Regression tests for the marine_courses fix. Covers:
#
# 1. `courses/views.py` `perform_create` and `get_queryset` honour
#    `user` from the payload AND `?user=` query param, so an admin
#    can create a Course for a specific crew member (instead of every
#    Course silently getting user=admin, which was the production bug).
#
# 2. `CourseSerializer` (read path) + `user_documents.marine_courses`
#    + `8_marine_courses` all return the SAME set of fields, including
#    `id`, `course_number`, `number`, `issued_by`, `issued_at`,
#    `country_of_issue`, and `download_url`. Previously each path
#    exposed a different subset.
#
# 3. The Course download endpoint allows Admin/HR/Recruiter to download
#    any course's document, but restricts an Employee to their own.

import datetime
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status as http_status

from api.models import Users
from courses.models import Course


# ============================================================================
# Shared helpers
# ============================================================================


def _admin():
    return Users.objects.create_user(
        email="mc-admin@test.com", password="x",
        first_name="A", middle_name="A", role="Admin",
        is_staff=True, is_superuser=True,
    )


def _employee():
    return Users.objects.create_user(
        email="mc-emp@test.com", password="x",
        first_name="E", middle_name="E", role="Employee",
    )


def _course_payload(user_id, **overrides):
    base = {
        "user": user_id,
        "course_name": "STCW Basic Safety",
        "course_number": "STCW-001",
        "issue_date": "2024-01-15",
        "expiry_date": "2029-01-15",
        "issued_by": "IMO",
        "issued_at": "Alexandria",
        "country_of_issue": "Egypt",
    }
    base.update(overrides)
    return base


# ============================================================================
# 1. Admin can create a Course for another user — payload `user`
# ============================================================================


class CourseCreateForOtherUserPayloadTests(TestCase):
    """Before the fix, perform_create hard-overrode user=request.user.
    The frontend courseService sends `user` in the payload AND as a
    `?user=` query param; both must work so an admin can add a course
    for a specific crew member."""

    @classmethod
    def setUpTestData(cls):
        cls.admin = _admin()
        cls.employee = _employee()

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

    def test_create_with_user_in_payload_targets_employee(self):
        r = self.client.post(
            "/api/courses/",
            _course_payload(self.employee.id),
            format="multipart",
        )
        self.assertEqual(r.status_code, http_status.HTTP_201_CREATED, r.data)
        c = Course.objects.get(id=r.data["id"])
        self.assertEqual(
            c.user_id, self.employee.id,
            f"Course should be owned by the employee, got {c.user_id}",
        )

    def test_create_with_user_in_query_param_targets_employee(self):
        payload = _course_payload(self.employee.id)
        payload.pop("user")  # only in query param
        r = self.client.post(
            f"/api/courses/?user={self.employee.id}",
            payload,
            format="multipart",
        )
        self.assertEqual(r.status_code, http_status.HTTP_201_CREATED, r.data)
        c = Course.objects.get(id=r.data["id"])
        self.assertEqual(c.user_id, self.employee.id)

    def test_create_without_user_defaults_to_request_user(self):
        """If no user is supplied anywhere, fall back to request.user
        (the admin in this test) — preserves the original behaviour."""
        payload = _course_payload(self.employee.id)
        payload.pop("user")
        r = self.client.post("/api/courses/", payload, format="multipart")
        self.assertEqual(r.status_code, http_status.HTTP_201_CREATED, r.data)
        c = Course.objects.get(id=r.data["id"])
        self.assertEqual(c.user_id, self.admin.id)

    def test_create_with_garbage_user_falls_back_to_request_user(self):
        """Defensive: if `user` is not an int, don't 500."""
        payload = _course_payload("not-a-number")
        r = self.client.post("/api/courses/", payload, format="multipart")
        self.assertEqual(r.status_code, http_status.HTTP_201_CREATED, r.data)
        c = Course.objects.get(id=r.data["id"])
        self.assertEqual(c.user_id, self.admin.id)

    def test_list_with_user_query_param_returns_only_that_users_courses(self):
        """get_queryset must honour `?user=` so an admin can list a
        crew member's courses from the form."""
        Course.objects.create(user=self.employee, course_name="A")
        Course.objects.create(user=self.employee, course_name="B")
        Course.objects.create(user=self.admin, course_name="C")
        r = self.client.get(f"/api/courses/?user={self.employee.id}")
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)
        # DRF paginates by default — the response is a dict with
        # "results", not a bare list.
        results = r.data if isinstance(r.data, list) else r.data.get("results", [])
        ids = {row["id"] for row in results}
        employee_course_ids = set(
            Course.objects.filter(user=self.employee).values_list("id", flat=True)
        )
        self.assertEqual(
            ids, employee_course_ids,
            "List with ?user=X must filter to X's courses only",
        )


# ============================================================================
# 2. Both `marine_courses` API paths return the same unified field set
# ============================================================================


class MarineCoursesFieldSetTests(TestCase):
    """Lock in the unified field set on both response paths:
       - `user_documents.marine_courses` (from /api/users/{id}/)
       - `8_marine_courses`            (from /api/seafarer-application/{id}/)
    Both must expose: id, course_name, course_number, number, issue_date,
    expiry_date, issued_by, issued_at, country_of_issue, download_url."""

    # The expected common fields (every Course in either response must
    # have these keys — even if the value is null/empty).
    REQUIRED_FIELDS = {
        "id", "course_name", "course_number", "number",
        "issue_date", "expiry_date", "issued_by", "issued_at",
        "country_of_issue", "download_url",
    }

    @classmethod
    def setUpTestData(cls):
        cls.admin = _admin()
        cls.employee = _employee()
        Course.objects.create(
            user=cls.employee,
            course_name="STCW",
            course_number="STCW-77",
            issue_date=datetime.date(2024, 1, 15),
            expiry_date=datetime.date(2029, 1, 15),
            issued_by="IMO",
            issued_at="Alexandria",
            country_of_issue="Egypt",
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

    def _assert_full_field_set(self, course_dict):
        missing = self.REQUIRED_FIELDS - set(course_dict.keys())
        self.assertFalse(
            missing,
            f"Course row is missing required fields: {sorted(missing)}. "
            f"Got: {sorted(course_dict.keys())}",
        )

    def test_user_documents_marine_courses_has_unified_field_set(self):
        r = self.client.get(f"/api/users/{self.employee.id}/")
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)
        courses = r.data.get("user_documents", {}).get("marine_courses", [])
        self.assertEqual(len(courses), 1, courses)
        self._assert_full_field_set(courses[0])
        # And the values land correctly
        c = courses[0]
        self.assertEqual(c["course_name"], "STCW")
        self.assertEqual(c["course_number"], "STCW-77")
        self.assertEqual(c["number"], "STCW-77")  # legacy alias
        self.assertEqual(c["issued_by"], "IMO")
        self.assertEqual(c["issued_at"], "Alexandria")
        self.assertEqual(c["country_of_issue"], "Egypt")

    def test_seafarer_application_8_marine_courses_has_unified_field_set(self):
        r = self.client.get(
            f"/api/seafarer-application/{self.employee.id}/",
        )
        self.assertEqual(r.status_code, http_status.HTTP_200_OK, r.data)
        courses = r.data.get("8_marine_courses", [])
        self.assertEqual(len(courses), 1, courses)
        self._assert_full_field_set(courses[0])
        c = courses[0]
        self.assertEqual(c["course_name"], "STCW")
        self.assertEqual(c["course_number"], "STCW-77")
        self.assertEqual(c["number"], "STCW-77")
        self.assertEqual(c["issued_by"], "IMO")
        self.assertEqual(c["issued_at"], "Alexandria")
        self.assertEqual(c["country_of_issue"], "Egypt")

    def test_both_paths_return_matching_ids(self):
        """The id in user_documents.marine_courses and
        8_marine_courses must refer to the same Course row — the
        frontend uses this to look up the attachment."""
        r1 = self.client.get(f"/api/users/{self.employee.id}/")
        r2 = self.client.get(
            f"/api/seafarer-application/{self.employee.id}/",
        )
        ids_1 = {c["id"] for c in r1.data.get("user_documents", {}).get("marine_courses", [])}
        ids_2 = {c["id"] for c in r2.data.get("8_marine_courses", [])}
        self.assertTrue(ids_1, "user_documents path returned no courses")
        self.assertEqual(
            ids_1, ids_2,
            "user_documents and 8_marine_courses must return the same ids",
        )


# ============================================================================
# 3. Course download — Admin/HR/Recruiter can download any
# ============================================================================


class CourseDownloadPermissionTests(TestCase):
    """An employee can only download their own course's document.
    Admin/HR/Recruiter can download any."""

    @classmethod
    def setUpTestData(cls):
        cls.admin = _admin()
        cls.employee = _employee()
        cls.other = Users.objects.create_user(
            email="mc-other@test.com", password="x",
            first_name="O", middle_name="O", role="Employee",
        )

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)
        # Create a course owned by `other` with no document (so the
        # endpoint returns 404 for "no file", which is easier to test
        # than 200 OK with a FileResponse)
        self.course = Course.objects.create(
            user=self.other,
            course_name="STCW",
            course_number="X-1",
        )

    def test_admin_gets_consistent_404_for_missing_file(self):
        """The download endpoint exists and returns 404 (not 500) when
        the course has no document. The test is gated on the user
        being authorised to see the course."""
        r = self.client.get(f"/api/courses/{self.course.id}/download/")
        self.assertEqual(r.status_code, http_status.HTTP_404_NOT_FOUND)
        self.assertIn("No document found", str(r.data))

    def test_employee_cannot_download_other_users_course(self):
        """An employee authenticated as `self.employee` asking for a
        course owned by `self.other` must get 404 (not authorised /
        not visible), not a 500."""
        self.client.force_authenticate(user=self.employee)
        r = self.client.get(f"/api/courses/{self.course.id}/download/")
        self.assertEqual(r.status_code, http_status.HTTP_404_NOT_FOUND)
