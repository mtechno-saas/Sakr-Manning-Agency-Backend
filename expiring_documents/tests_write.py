"""
Tests for the write paths on the Expiring Documents endpoint:

  POST  /api/expiring-documents/             (create a new personal document)
  PATCH /api/expiring-documents/<item_id>/   (update by id)

The id format is matched from the GET response and used as the
routing key:
  user_<user_id>_<expiry_field>   -> updates the Users field
  pd_<doc_id>                     -> updates a PersonalDocument row
"""
import io
from datetime import timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone

from rest_framework.test import APIClient

from api.models import PersonalDocument, Users


def _login_as(role):
    user = Users.objects.create_user(
        email=f"{role.lower().replace(' ', '')}-writer@example.com",
        password="x",
        first_name=role.split()[0],
        middle_name="writer",
        role=role,
    )
    client = APIClient()
    client.force_authenticate(user=user)
    return client, user


class ExpiringDocumentsCreateTests(TestCase):
    """POST /api/expiring-documents/ creates a new PersonalDocument."""

    def setUp(self):
        self.user = Users.objects.create_user(
            email="crew-write@example.com",
            password="x",
            first_name="Crew",
            middle_name="Member",
        )

    def _multipart(self, **fields):
        if "file" not in fields:
            fields["file"] = SimpleUploadedFile(
                "visa.pdf",
                b"%PDF-1.4 fake",
                content_type="application/pdf",
            )
        return fields

    def test_post_creates_personal_document(self):
        client, _ = _login_as("Admin")
        r = client.post(
            "/api/expiring-documents/",
            self._multipart(
                user=self.user.id,
                document_type="Australian Visa Crew",
                document_number="V-998877",
                expiry_date="2027-01-15",
            ),
            format="multipart",
        )
        self.assertEqual(r.status_code, 201, r.data)
        self.assertEqual(PersonalDocument.objects.count(), 1)
        doc = PersonalDocument.objects.first()
        self.assertEqual(doc.user_id, self.user.id)
        self.assertEqual(doc.document_type, "Australian Visa Crew")
        self.assertEqual(str(doc.expiry_date), "2027-01-15")

    def test_posted_doc_appears_in_subsequent_get(self):
        client, _ = _login_as("Admin")
        # Use a date within the default 30-day window so the doc
        # is included in the GET response without needing a
        # `days=` query param.
        near_future = (
            timezone.localdate() + timedelta(days=10)
        ).isoformat()
        post_r = client.post(
            "/api/expiring-documents/",
            self._multipart(
                user=self.user.id,
                document_type="Australian Visa Crew",
                expiry_date=near_future,
            ),
            format="multipart",
        )
        # Sanity: POST must have actually created a row.
        self.assertEqual(post_r.status_code, 201, post_r.data)
        # And that row must have a non-null expiry_date.
        from api.models import PersonalDocument as _PD
        created = _PD.objects.filter(user=self.user).first()
        self.assertIsNotNone(created)
        self.assertIsNotNone(created.expiry_date, "expiry_date was not saved")

        r = client.get("/api/expiring-documents/")
        self.assertEqual(r.status_code, 200)
        ids = [item["id"] for item in r.data["results"]]
        self.assertTrue(
            any(i.startswith("pd_") for i in ids),
            f"Expected a pd_ id in the GET results, got {ids}",
        )

    def test_post_rejects_employee(self):
        client, _ = _login_as("Employee")
        r = client.post(
            "/api/expiring-documents/",
            self._multipart(
                user=self.user.id,
                document_type="Australian Visa Crew",
                expiry_date="2027-06-30",
            ),
            format="multipart",
        )
        self.assertEqual(r.status_code, 403)

    def test_post_rejects_unauthenticated(self):
        client = APIClient()
        r = client.post(
            "/api/expiring-documents/",
            self._multipart(
                user=self.user.id,
                document_type="Australian Visa Crew",
                expiry_date="2027-06-30",
            ),
            format="multipart",
        )
        self.assertIn(r.status_code, (401, 403))

    def test_post_to_detail_url_returns_400_not_500(self):
        """
        Regression: posting to /api/expiring-documents/<id>/ (a
        detail URL meant for PATCH/DELETE) used to crash with
        TypeError because post() didn't accept the item_id kwarg.
        Now it returns a clean 400 explaining the right URL.
        """
        client, _ = _login_as("Admin")
        r = client.post(
            f"/api/expiring-documents/{self.user.id}/",
            self._multipart(
                user=self.user.id,
                document_type="Australian Visa Crew",
                expiry_date="2027-06-30",
            ),
            format="multipart",
        )
        self.assertEqual(r.status_code, 400, r.data)
        self.assertIn("/api/expiring-documents/", r.data.get("error", ""))
        # Nothing should have been created
        self.assertEqual(PersonalDocument.objects.count(), 0)


class ExpiringDocumentsUpdateTests(TestCase):
    """PATCH /api/expiring-documents/<id>/ updates by id."""

    def setUp(self):
        self.user = Users.objects.create_user(
            email="crew-patch@example.com",
            password="x",
            first_name="Patch",
            middle_name="Tester",
        )
        # A personal document to patch
        self.doc = PersonalDocument.objects.create(
            user=self.user,
            document_type="Australian Visa Crew",
            document_number="V-111111",
            expiry_date=timezone.localdate() + timedelta(days=30),
        )

    # ---- pd_<id> updates ----------------------------------------------

    def test_patch_pd_updates_expiry(self):
        client, _ = _login_as("Admin")
        url = f"/api/expiring-documents/pd_{self.doc.id}/"
        r = client.patch(
            url,
            {"expiry_date": "2027-12-31"},
            format="json",
        )
        self.assertEqual(r.status_code, 200, r.data)
        self.doc.refresh_from_db()
        self.assertEqual(str(self.doc.expiry_date), "2027-12-31")

    def test_patch_pd_updates_other_fields(self):
        client, _ = _login_as("Admin")
        url = f"/api/expiring-documents/pd_{self.doc.id}/"
        r = client.patch(
            url,
            {"document_number": "V-NEW", "issued_by": "Immigration Dept"},
            format="json",
        )
        self.assertEqual(r.status_code, 200, r.data)
        self.doc.refresh_from_db()
        self.assertEqual(self.doc.document_number, "V-NEW")
        self.assertEqual(self.doc.issued_by, "Immigration Dept")

    def test_patch_pd_404_for_nonexistent(self):
        client, _ = _login_as("Admin")
        r = client.patch(
            "/api/expiring-documents/pd_999999/",
            {"expiry_date": "2027-01-01"},
            format="json",
        )
        self.assertEqual(r.status_code, 404)

    # ---- user_<id>_<field> updates ------------------------------------

    def test_patch_user_field_updates_passport_expiry(self):
        client, _ = _login_as("Admin")
        url = f"/api/expiring-documents/user_{self.user.id}_passport_expiry_date/"
        r = client.patch(
            url,
            {"expiry_date": "2027-01-15"},
            format="json",
        )
        self.assertEqual(r.status_code, 200, r.data)
        self.user.refresh_from_db()
        self.assertEqual(str(self.user.passport_expiry_date), "2027-01-15")

    def test_patch_user_field_accepts_field_name_directly(self):
        client, _ = _login_as("Admin")
        url = f"/api/expiring-documents/user_{self.user.id}_seaman_book_expiry_date/"
        r = client.patch(
            url,
            {"seaman_book_expiry_date": "2028-05-20"},
            format="json",
        )
        self.assertEqual(r.status_code, 200, r.data)
        self.user.refresh_from_db()
        self.assertEqual(str(self.user.seaman_book_expiry_date), "2028-05-20")

    def test_patch_user_field_400_for_unknown_field(self):
        client, _ = _login_as("Admin")
        url = f"/api/expiring-documents/user_{self.user.id}_not_a_field/"
        r = client.patch(
            url,
            {"expiry_date": "2027-01-01"},
            format="json",
        )
        self.assertEqual(r.status_code, 400, r.data)

    def test_patch_user_field_400_when_no_value(self):
        client, _ = _login_as("Admin")
        url = f"/api/expiring-documents/user_{self.user.id}_passport_expiry_date/"
        r = client.patch(url, {}, format="json")
        self.assertEqual(r.status_code, 400)

    def test_patch_user_field_404_for_nonexistent_user(self):
        client, _ = _login_as("Admin")
        url = "/api/expiring-documents/user_999999_passport_expiry_date/"
        r = client.patch(
            url,
            {"expiry_date": "2027-01-01"},
            format="json",
        )
        self.assertEqual(r.status_code, 404)

    def test_patch_user_field_all_9_known_fields(self):
        """All 9 USER_EXPIRY_FIELDS entries must be writable via PATCH."""
        client, _ = _login_as("Admin")
        cases = [
            ("passport_expiry_date", "2027-02-01"),
            ("seaman_book_expiry_date", "2027-03-01"),
            ("other_seaman_book_expiry_date", "2027-04-01"),
            ("coc_expiry_date", "2027-05-01"),
            ("goc_expiry_date", "2027-06-01"),
            ("health_expiry_date", "2027-07-01"),
            ("international_medical_expiry_date", "2027-08-01"),
            ("yellow_fever_expiry_date", "2027-09-01"),
            ("cholera_expiry_date", "2027-10-01"),
        ]
        for field, new_date in cases:
            url = f"/api/expiring-documents/user_{self.user.id}_{field}/"
            r = client.patch(url, {"expiry_date": new_date}, format="json")
            self.assertEqual(r.status_code, 200, f"{field}: {r.data}")
            self.user.refresh_from_db()
            self.assertEqual(
                str(getattr(self.user, field)), new_date,
                f"{field} should be {new_date}",
            )

    # ---- Auth ----------------------------------------------------------

    def test_patch_rejects_employee(self):
        client, _ = _login_as("Employee")
        r = client.patch(
            f"/api/expiring-documents/pd_{self.doc.id}/",
            {"expiry_date": "2027-01-01"},
            format="json",
        )
        self.assertEqual(r.status_code, 403)

    def test_patch_rejects_unauthenticated(self):
        client = APIClient()
        r = client.patch(
            f"/api/expiring-documents/pd_{self.doc.id}/",
            {"expiry_date": "2027-01-01"},
            format="json",
        )
        self.assertIn(r.status_code, (401, 403))

    # ---- Bad id format -------------------------------------------------

    def test_patch_invalid_id_format_returns_400(self):
        client, _ = _login_as("Admin")
        r = client.patch(
            "/api/expiring-documents/garbage_id/",
            {"expiry_date": "2027-01-01"},
            format="json",
        )
        self.assertEqual(r.status_code, 400, r.data)


class ExpiringDocumentsDeleteTests(TestCase):
    """DELETE /api/expiring-documents/<id>/ removes a PersonalDocument."""

    def setUp(self):
        self.user = Users.objects.create_user(
            email="crew-del@example.com",
            password="x",
            first_name="Del",
            middle_name="Eter",
        )
        self.doc = PersonalDocument.objects.create(
            user=self.user,
            document_type="Australian Visa Crew",
            document_number="V-DEL-1",
            expiry_date=timezone.localdate() + timedelta(days=10),
        )

    # ---- pd_<id> delete -----------------------------------------------

    def test_delete_pd_removes_row(self):
        client, _ = _login_as("Admin")
        r = client.delete(f"/api/expiring-documents/pd_{self.doc.id}/")
        self.assertEqual(r.status_code, 204)
        self.assertFalse(
            PersonalDocument.objects.filter(pk=self.doc.id).exists(),
            "PersonalDocument row must be hard-deleted",
        )

    def test_deleted_doc_no_longer_in_get(self):
        client, _ = _login_as("Admin")
        doc_id = self.doc.id
        client.delete(f"/api/expiring-documents/pd_{doc_id}/")
        r = client.get("/api/expiring-documents/?days=60")
        ids = [item["id"] for item in r.data["results"]]
        self.assertNotIn(f"pd_{doc_id}", ids)

    def test_delete_pd_404_for_nonexistent(self):
        client, _ = _login_as("Admin")
        r = client.delete("/api/expiring-documents/pd_999999/")
        self.assertEqual(r.status_code, 404)

    # ---- user_profile delete is rejected ------------------------------

    def test_delete_user_profile_returns_400(self):
        """Cannot DELETE a user_profile row — must PATCH to null instead."""
        client, _ = _login_as("Admin")
        url = f"/api/expiring-documents/user_{self.user.id}_passport_expiry_date/"
        r = client.delete(url)
        self.assertEqual(r.status_code, 400, r.data)
        self.assertIn("PATCH", r.data.get("error", ""))

    # ---- Auth ----------------------------------------------------------

    def test_delete_rejects_employee(self):
        client, _ = _login_as("Employee")
        r = client.delete(f"/api/expiring-documents/pd_{self.doc.id}/")
        self.assertEqual(r.status_code, 403)

    def test_delete_rejects_unauthenticated(self):
        client = APIClient()
        r = client.delete(f"/api/expiring-documents/pd_{self.doc.id}/")
        self.assertIn(r.status_code, (401, 403))

    # ---- Bad id format -------------------------------------------------

    def test_delete_invalid_id_format_returns_400(self):
        client, _ = _login_as("Admin")
        r = client.delete("/api/expiring-documents/garbage_id/")
        self.assertEqual(r.status_code, 400)


class ExpiringDocumentsGetStillWorksTests(TestCase):
    """Sanity check that the GET endpoint behavior is unchanged after refactor."""

    def setUp(self):
        self.user = Users.objects.create_user(
            email="crew-get@example.com",
            password="x",
            first_name="Get",
            middle_name="Tester",
        )
        # Passport expires in 5 days -> 'critical' bucket
        self.user.passport_expiry_date = (
            timezone.localdate() + timedelta(days=5)
        )
        self.user.save()

    def test_get_returns_aggregated_data(self):
        client, _ = _login_as("Admin")
        r = client.get("/api/expiring-documents/")
        self.assertEqual(r.status_code, 200)
        self.assertIn("counts", r.data)
        self.assertIn("results", r.data)
        self.assertIn("days_window", r.data)
        # The passport item should be in the critical bucket
        passport_items = [
            i for i in r.data["results"]
            if i["id"] == f"user_{self.user.id}_passport_expiry_date"
        ]
        self.assertEqual(len(passport_items), 1)
        self.assertEqual(passport_items[0]["category"], "critical")


class ExpiringDocumentsDaysWindowConfigTests(TestCase):
    """
    Verify the ?days=N query param and Django settings
    (EXPIRING_DOCUMENTS_DEFAULT_DAYS / MIN_DAYS / MAX_DAYS) interact
    correctly. The view reads the limits from settings and clamps
    out-of-range values, falling back to the default.
    """

    def setUp(self):
        self.user = Users.objects.create_user(
            email="crew-window@example.com",
            password="x",
            first_name="W",
            middle_name="indow",
        )
        # Passport in 5 days (always in the critical bucket
        # regardless of the window)
        self.user.passport_expiry_date = (
            timezone.localdate() + timedelta(days=5)
        )
        self.user.save()

    def test_default_window_echoed_in_response(self):
        client, _ = _login_as("Admin")
        r = client.get("/api/expiring-documents/")
        self.assertEqual(r.status_code, 200)
        # Default from settings is 30 (or whatever override)
        from django.conf import settings as dj_settings
        self.assertEqual(
            r.data["days_window"],
            getattr(dj_settings, "EXPIRING_DOCUMENTS_DEFAULT_DAYS", 30),
        )

    def test_explicit_days_param_wins(self):
        client, _ = _login_as("Admin")
        r = client.get("/api/expiring-documents/?days=7")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["days_window"], 7)

    def test_days_below_min_falls_back_to_default(self):
        client, _ = _login_as("Admin")
        from django.conf import settings as dj_settings
        default = getattr(dj_settings, "EXPIRING_DOCUMENTS_DEFAULT_DAYS", 30)
        r = client.get("/api/expiring-documents/?days=0")
        self.assertEqual(r.data["days_window"], default)

    def test_days_above_max_clamps_to_max(self):
        client, _ = _login_as("Admin")
        from django.conf import settings as dj_settings
        max_d = getattr(dj_settings, "EXPIRING_DOCUMENTS_MAX_DAYS", 365)
        r = client.get("/api/expiring-documents/?days=99999")
        self.assertEqual(r.data["days_window"], max_d)

    def test_invalid_days_string_falls_back_to_default(self):
        client, _ = _login_as("Admin")
        from django.conf import settings as dj_settings
        default = getattr(dj_settings, "EXPIRING_DOCUMENTS_DEFAULT_DAYS", 30)
        r = client.get("/api/expiring-documents/?days=notanumber")
        self.assertEqual(r.data["days_window"], default)
