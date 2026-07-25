"""Tests for the Reminders app."""
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from reminders.models import Reminder

User = get_user_model()


class ReminderAPITestCase(TestCase):
    """End-to-end tests for the /api/reminders/ endpoint."""

    def setUp(self):
        # Admin user
        self.admin = User.objects.create_user(
            email="admin@example.com",
            password="test1234",
            first_name="Admin",
            role="Admin",
        )
        # Crew member
        self.crew = User.objects.create_user(
            email="crew@example.com",
            password="test1234",
            first_name="Hisham",
            middle_name="Hassan",
        )
        # Another crew member
        self.crew2 = User.objects.create_user(
            email="crew2@example.com",
            password="test1234",
            first_name="Sara",
        )

    def _client(self, user):
        c = APIClient()
        c.force_authenticate(user=user)
        return c

    # ----- Auth -----

    def test_anonymous_request_blocked(self):
        client = APIClient()
        resp = client.get("/api/reminders/")
        self.assertIn(resp.status_code, (401, 403))

    def test_employee_sees_only_own(self):
        # Crew creates a reminder for themselves
        Reminder.objects.create(
            user=self.crew,
            text="Submit medical form",
            reminder_date=timezone.localdate() + timedelta(days=2),
            reminder_time=timezone.now().time(),
        )
        # Crew2 creates one
        Reminder.objects.create(
            user=self.crew2,
            text="Other thing",
            reminder_date=timezone.localdate() + timedelta(days=3),
            reminder_time=timezone.now().time(),
        )

        client = self._client(self.crew)
        resp = client.get("/api/reminders/")
        self.assertEqual(resp.status_code, 200)
        # Crew should only see their own
        data = resp.json()
        results = data if isinstance(data, list) else data.get('results', [])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['user'], self.crew.id)

    def test_admin_sees_all(self):
        for user in (self.crew, self.crew2):
            Reminder.objects.create(
                user=user,
                text="Reminder for " + user.email,
                reminder_date=timezone.localdate() + timedelta(days=1),
                reminder_time=timezone.now().time(),
            )
        client = self._client(self.admin)
        resp = client.get("/api/reminders/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        results = data if isinstance(data, list) else data.get('results', [])
        self.assertEqual(len(results), 2)

    # ----- CRUD -----

    def test_create_reminder(self):
        client = self._client(self.admin)
        resp = client.post("/api/reminders/", {
            "user": self.crew.id,
            "text": "Renew visa before 2026-08-01",
            "reminder_date": (timezone.localdate() + timedelta(days=5)).isoformat(),
            "reminder_time": "09:00:00",
        }, format="json")
        self.assertEqual(resp.status_code, 201, resp.content)
        data = resp.json()
        self.assertEqual(data['text'], "Renew visa before 2026-08-01")
        self.assertEqual(data['user_name'], "Hisham Hassan")
        self.assertFalse(data['is_completed'])

    def test_create_missing_required_field_fails(self):
        client = self._client(self.admin)
        resp = client.post("/api/reminders/", {
            "text": "Missing user and date",
        }, format="json")
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        # Should have errors for user, reminder_date, reminder_time
        self.assertIn('user', data)
        self.assertIn('reminder_date', data)
        self.assertIn('reminder_time', data)

    def test_patch_partial_update(self):
        r = Reminder.objects.create(
            user=self.crew,
            text="Original text",
            reminder_date=timezone.localdate() + timedelta(days=1),
            reminder_time=timezone.now().time(),
        )
        client = self._client(self.admin)
        resp = client.patch(f"/api/reminders/{r.id}/", {
            "text": "Updated text",
        }, format="json")
        self.assertEqual(resp.status_code, 200, resp.content)
        r.refresh_from_db()
        self.assertEqual(r.text, "Updated text")
        # Other fields unchanged
        self.assertEqual(r.user, self.crew)

    def test_delete(self):
        r = Reminder.objects.create(
            user=self.crew,
            text="To be deleted",
            reminder_date=timezone.localdate() + timedelta(days=1),
            reminder_time=timezone.now().time(),
        )
        client = self._client(self.admin)
        resp = client.delete(f"/api/reminders/{r.id}/")
        self.assertEqual(resp.status_code, 204)
        self.assertFalse(Reminder.objects.filter(pk=r.id).exists())

    # ----- Custom actions -----

    def test_upcoming_action(self):
        # Past reminder (should not appear)
        Reminder.objects.create(
            user=self.crew,
            text="Past",
            reminder_date=timezone.localdate() - timedelta(days=2),
            reminder_time=timezone.now().time(),
        )
        # Today reminder (should appear)
        Reminder.objects.create(
            user=self.crew,
            text="Today",
            reminder_date=timezone.localdate(),
            reminder_time=timezone.now().time(),
        )
        # Future reminder (should appear)
        Reminder.objects.create(
            user=self.crew,
            text="Future",
            reminder_date=timezone.localdate() + timedelta(days=2),
            reminder_time=timezone.now().time(),
        )
        # Already completed (should NOT appear)
        Reminder.objects.create(
            user=self.crew,
            text="Done",
            reminder_date=timezone.localdate() + timedelta(days=1),
            reminder_time=timezone.now().time(),
            is_completed=True,
        )

        client = self._client(self.crew)
        resp = client.get("/api/reminders/upcoming/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        texts = [r['text'] for r in data]
        self.assertIn("Today", texts)
        self.assertIn("Future", texts)
        self.assertNotIn("Past", texts)
        self.assertNotIn("Done", texts)

    def test_mark_done(self):
        r = Reminder.objects.create(
            user=self.crew,
            text="Do this",
            reminder_date=timezone.localdate() + timedelta(days=1),
            reminder_time=timezone.now().time(),
        )
        client = self._client(self.crew)
        resp = client.post(f"/api/reminders/{r.id}/mark_done/")
        self.assertEqual(resp.status_code, 200)
        r.refresh_from_db()
        self.assertTrue(r.is_completed)

    # ----- User field flexibility -----

    def test_user_field_accepts_int(self):
        client = self._client(self.admin)
        resp = client.post("/api/reminders/", {
            "user": self.crew.id,  # int
            "text": "Int user id",
            "reminder_date": (timezone.localdate() + timedelta(days=1)).isoformat(),
            "reminder_time": "09:00:00",
        }, format="json")
        self.assertEqual(resp.status_code, 201, resp.content)
        self.assertEqual(resp.json()['user'], self.crew.id)

    def test_user_field_accepts_string_int(self):
        """Form may submit the id as a string from a <select> value."""
        client = self._client(self.admin)
        resp = client.post("/api/reminders/", {
            "user": str(self.crew.id),  # stringified int
            "text": "String user id",
            "reminder_date": (timezone.localdate() + timedelta(days=1)).isoformat(),
            "reminder_time": "10:00:00",
        }, format="json")
        self.assertEqual(resp.status_code, 201, resp.content)
        self.assertEqual(resp.json()['user'], self.crew.id)

    def test_user_field_rejects_invalid(self):
        """Bogus values return 400, not 500."""
        client = self._client(self.admin)
        resp = client.post("/api/reminders/", {
            "user": "not-a-user-id",
            "text": "Bogus user",
            "reminder_date": (timezone.localdate() + timedelta(days=1)).isoformat(),
            "reminder_time": "11:00:00",
        }, format="json")
        self.assertEqual(resp.status_code, 400)
        self.assertIn('user', resp.json())

    def test_user_field_rejects_nonexistent_int_string(self):
        """String that looks like an int but doesn't exist → 400."""
        client = self._client(self.admin)
        resp = client.post("/api/reminders/", {
            "user": "99999",
            "text": "Nonexistent user",
            "reminder_date": (timezone.localdate() + timedelta(days=1)).isoformat(),
            "reminder_time": "12:00:00",
        }, format="json")
        self.assertEqual(resp.status_code, 400)
        self.assertIn('user', resp.json())

    def test_user_field_accepts_email(self):
        """Frontend may submit email instead of id."""
        client = self._client(self.admin)
        resp = client.post("/api/reminders/", {
            "user": self.crew.email,
            "text": "Email-based user lookup",
            "reminder_date": (timezone.localdate() + timedelta(days=1)).isoformat(),
            "reminder_time": "13:00:00",
        }, format="json")
        self.assertEqual(resp.status_code, 201, resp.content)
        self.assertEqual(resp.json()['user'], self.crew.id)

    def test_user_field_accepts_email_case_insensitive(self):
        """Email lookup is case-insensitive."""
        client = self._client(self.admin)
        resp = client.post("/api/reminders/", {
            "user": self.crew.email.upper(),
            "text": "Uppercase email",
            "reminder_date": (timezone.localdate() + timedelta(days=1)).isoformat(),
            "reminder_time": "14:00:00",
        }, format="json")
        self.assertEqual(resp.status_code, 201, resp.content)
        self.assertEqual(resp.json()['user'], self.crew.id)

    def test_user_field_accepts_full_name(self):
        """Frontend may submit full name (first + middle)."""
        client = self._client(self.admin)
        resp = client.post("/api/reminders/", {
            "user": "Hisham Hassan",  # first_name="Hisham", middle_name="Hassan"
            "text": "Full name lookup",
            "reminder_date": (timezone.localdate() + timedelta(days=1)).isoformat(),
            "reminder_time": "15:00:00",
        }, format="json")
        self.assertEqual(resp.status_code, 201, resp.content)
        self.assertEqual(resp.json()['user'], self.crew.id)

    def test_user_field_accepts_first_name_only(self):
        """When the name is unique, first-name-only lookup works."""
        client = self._client(self.admin)
        resp = client.post("/api/reminders/", {
            "user": "Hisham",
            "text": "First name only",
            "reminder_date": (timezone.localdate() + timedelta(days=1)).isoformat(),
            "reminder_time": "16:00:00",
        }, format="json")
        self.assertEqual(resp.status_code, 201, resp.content)
        self.assertEqual(resp.json()['user'], self.crew.id)

    # ----- Date format flexibility -----

    def test_date_accepts_iso_format(self):
        """YYYY-MM-DD (the default, should still work)."""
        client = self._client(self.admin)
        resp = client.post("/api/reminders/", {
            "user": self.crew.id,
            "text": "ISO date",
            "reminder_date": "2026-08-15",
            "reminder_time": "10:00:00",
        }, format="json")
        self.assertEqual(resp.status_code, 201, resp.content)

    def test_date_accepts_slash_format(self):
        """YYYY/MM/DD — the format the frontend was sending."""
        client = self._client(self.admin)
        resp = client.post("/api/reminders/", {
            "user": self.crew.id,
            "text": "Slash date",
            "reminder_date": "2026/11/11",
            "reminder_time": "11:00:00",
        }, format="json")
        self.assertEqual(resp.status_code, 201, resp.content)

    def test_date_accepts_us_format(self):
        """MM/DD/YYYY when unambiguous."""
        client = self._client(self.admin)
        resp = client.post("/api/reminders/", {
            "user": self.crew.id,
            "text": "US date",
            "reminder_date": "08/15/2026",  # 15 > 12 → not US, but 15 is day, so EU
            "reminder_time": "12:00:00",
        }, format="json")
        # 15/08/2026 (EU) or 08/15/2026 (US) — 15 > 12 so it's clearly day, EU
        self.assertEqual(resp.status_code, 201, resp.content)

    def test_date_accepts_eu_format(self):
        """DD/MM/YYYY (day first) — common in Europe."""
        client = self._client(self.admin)
        resp = client.post("/api/reminders/", {
            "user": self.crew.id,
            "text": "EU date",
            "reminder_date": "15/08/2026",
            "reminder_time": "13:00:00",
        }, format="json")
        self.assertEqual(resp.status_code, 201, resp.content)

    def test_date_rejects_invalid(self):
        """Bogus date format returns 400 with helpful error."""
        client = self._client(self.admin)
        resp = client.post("/api/reminders/", {
            "user": self.crew.id,
            "text": "Invalid date",
            "reminder_date": "not-a-date",
            "reminder_time": "14:00:00",
        }, format="json")
        self.assertEqual(resp.status_code, 400)
        data = resp.json()
        self.assertIn('reminder_date', data)
        # Error message should mention valid formats
        error_text = str(data['reminder_date'])
        self.assertTrue('YYYY' in error_text or 'format' in error_text.lower())
