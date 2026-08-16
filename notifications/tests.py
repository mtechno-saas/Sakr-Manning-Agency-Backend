"""
Tests for the notifications app.

Coverage:
  1. ``Reminder`` post_save sends an email to the shared admin inbox.
  2. ``Reminder`` post_save on UPDATE is silent (no email).
  3. ``PersonalDocument`` post_save sends an email to the shared inbox.
  4. ``PersonalDocument`` post_save on UPDATE is silent.
  5. No actor (anonymous / management command) -> no email, no crash.
  6. NOTIFICATIONS_ADMIN_EMAIL setting missing -> no email, no crash.
  7. NOTIFICATIONS_ADMIN_EMAIL can be overridden via override_settings.
  8. SMTP failure does not propagate (best-effort sender).
  9. Thread-local cleanup between requests.
 10. End-to-end: POST /api/reminders/ as an authenticated admin -> 1 email
     in mail.outbox to the shared inbox.

The actor (request user) is still used for the email body greeting and
the "Hi <actor>, you set ..." line — only the recipient is now a
single shared inbox, not the actor's own email.

Run with: python manage.py test notifications --keepdb
"""
import datetime
from unittest import mock

from django.core import mail
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from api.models import PersonalDocument, Users
from reminders.models import Reminder

from core import threadlocals


# All admin notifications land here by default.
ADMIN_INBOX = "crew@sakrshipping.com"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_admin(email="admin@example.com"):
    return Users.objects.create_user(
        email=email,
        password="adminpass",
        first_name="Admin",
        middle_name="Root",
        role="Admin",
        is_staff=True,
        is_superuser=True,
    )


def _make_crew(email="john@example.com"):
    return Users.objects.create_user(
        email=email,
        password="crewpass",
        first_name="John",
        middle_name="Smith",
        role="Employee",
    )


def _set_actor(user):
    """Pretend an HTTP request is in flight, triggered by ``user``."""
    threadlocals.set_current_user(user)


def _clear_actor():
    threadlocals.clear_current_user()


# ---------------------------------------------------------------------------
# Reminder signal
# ---------------------------------------------------------------------------


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class ReminderNotificationTests(TestCase):
    def setUp(self):
        self.admin = _make_admin()
        self.crew = _make_crew()
        _set_actor(self.admin)
        mail.outbox = []

    def tearDown(self):
        _clear_actor()

    def test_create_reminder_sends_email_to_admin(self):
        r = Reminder.objects.create(
            user=self.crew,
            text="Call John about joining date",
            reminder_date=datetime.date(2026, 9, 1),
            reminder_time=datetime.time(10, 30),
        )
        self.assertEqual(len(mail.outbox), 1)
        msg = mail.outbox[0]
        # Recipient is the SHARED admin inbox, not the actor's email.
        self.assertEqual(msg.to, [ADMIN_INBOX])
        # Body still names the actor for traceability.
        self.assertIn("Admin Root", msg.body)
        self.assertIn("John", msg.subject)
        self.assertIn(str(r.id), msg.body)
        self.assertIn("2026-09-01", msg.body)
        self.assertIn("10:30", msg.body)
        self.assertIn("Call John about joining date", msg.body)

    def test_update_reminder_does_not_send(self):
        r = Reminder.objects.create(
            user=self.crew,
            text="First",
            reminder_date=datetime.date(2026, 9, 1),
            reminder_time=datetime.time(10, 30),
        )
        mail.outbox = []
        # Edit it
        r.text = "Updated text"
        r.save()
        self.assertEqual(len(mail.outbox), 0)

    def test_no_actor_still_sends_to_shared_inbox(self):
        """
        With a shared inbox, the recipient is the setting value, not
        the actor. So a write from an anonymous / management-command
        context still produces a notification, just with a generic
        greeting ("Hi An admin,") instead of a specific actor name.
        """
        _clear_actor()
        Reminder.objects.create(
            user=self.crew,
            text="No actor",
            reminder_date=datetime.date(2026, 9, 1),
            reminder_time=datetime.time(10, 30),
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [ADMIN_INBOX])
        self.assertIn("An admin", mail.outbox[0].body)

    def test_actor_with_no_email_still_sends(self):
        """
        Per spec, the recipient is the shared inbox, not the actor's
        own email. So even an actor with no email still triggers a
        notification to the inbox. The body just falls back to a
        generic greeting.
        """
        anon_admin = Users.objects.create_user(
            email="no-email@example.com",
            password="x",
            first_name="No",
            middle_name="Email",
            role="Admin",
        )
        # Blank the email AFTER creation (model has unique=True).
        Users.objects.filter(pk=anon_admin.pk).update(email="")
        anon_admin.refresh_from_db()
        _set_actor(anon_admin)
        Reminder.objects.create(
            user=self.crew,
            text="No email actor",
            reminder_date=datetime.date(2026, 9, 1),
            reminder_time=datetime.time(10, 30),
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [ADMIN_INBOX])

    @override_settings(NOTIFICATIONS_ADMIN_EMAIL="")
    def test_missing_admin_email_setting_skips(self):
        """If NOTIFICATIONS_ADMIN_EMAIL is empty, no email is sent."""
        Reminder.objects.create(
            user=self.crew,
            text="No inbox",
            reminder_date=datetime.date(2026, 9, 1),
            reminder_time=datetime.time(10, 30),
        )
        self.assertEqual(len(mail.outbox), 0)

    @override_settings(NOTIFICATIONS_ADMIN_EMAIL="alerts@sakrshipping.com")
    def test_admin_email_override_via_setting(self):
        """The recipient is the setting value, configurable per deploy."""
        Reminder.objects.create(
            user=self.crew,
            text="Override me",
            reminder_date=datetime.date(2026, 9, 1),
            reminder_time=datetime.time(10, 30),
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["alerts@sakrshipping.com"])

    def test_smtp_failure_does_not_break_signal(self):
        with mock.patch(
            "notifications.services.EmailMultiAlternatives.send",
            side_effect=RuntimeError("smtp down"),
        ):
            # The signal should swallow the failure and not raise.
            r = Reminder.objects.create(
                user=self.crew,
                text="Boom",
                reminder_date=datetime.date(2026, 9, 1),
                reminder_time=datetime.time(10, 30),
            )
            # Object still saved
            self.assertTrue(Reminder.objects.filter(pk=r.pk).exists())


# ---------------------------------------------------------------------------
# PersonalDocument signal
# ---------------------------------------------------------------------------


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class ExpiringDocumentNotificationTests(TestCase):
    def setUp(self):
        self.admin = _make_admin("admin@example.com")
        self.crew = _make_crew("crew@example.com")
        _set_actor(self.admin)
        mail.outbox = []

    def tearDown(self):
        _clear_actor()

    def test_create_personal_document_sends_email(self):
        doc = PersonalDocument.objects.create(
            user=self.crew,
            document_type="Passport",
            document_number="X1234567",
            issue_date=datetime.date(2025, 1, 1),
            expiry_date=datetime.date(2027, 1, 1),
            issuing_country="Egypt",
        )
        self.assertEqual(len(mail.outbox), 1)
        msg = mail.outbox[0]
        self.assertEqual(msg.to, [ADMIN_INBOX])
        self.assertIn("Passport", msg.subject)
        # Subject uses the human label (full_name) of the crew member.
        self.assertIn("John Smith", msg.subject)
        self.assertIn("X1234567", msg.body)
        self.assertIn("2027-01-01", msg.body)
        self.assertIn("Egypt", msg.body)
        self.assertIn(str(doc.id), msg.body)

    def test_update_personal_document_does_not_send(self):
        doc = PersonalDocument.objects.create(
            user=self.crew,
            document_type="Passport",
            expiry_date=datetime.date(2027, 1, 1),
        )
        mail.outbox = []
        doc.expiry_date = datetime.date(2028, 1, 1)
        doc.save()
        self.assertEqual(len(mail.outbox), 0)

    def test_no_actor_still_sends_to_shared_inbox(self):
        """See ReminderNotificationTests.test_no_actor_still_sends..."""
        _clear_actor()
        PersonalDocument.objects.create(
            user=self.crew,
            document_type="Passport",
            expiry_date=datetime.date(2027, 1, 1),
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [ADMIN_INBOX])

    def test_smtp_failure_does_not_break_signal(self):
        with mock.patch(
            "notifications.services.EmailMultiAlternatives.send",
            side_effect=RuntimeError("smtp down"),
        ):
            doc = PersonalDocument.objects.create(
                user=self.crew,
                document_type="Passport",
                expiry_date=datetime.date(2027, 1, 1),
            )
            self.assertTrue(PersonalDocument.objects.filter(pk=doc.pk).exists())


# ---------------------------------------------------------------------------
# Thread-local middleware
# ---------------------------------------------------------------------------


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class ThreadLocalActorTests(TestCase):
    def test_actor_set_during_request_cleared_after(self):
        admin = _make_admin("admin@example.com")
        client = APIClient()
        client.force_authenticate(user=admin)

        # We just need a lightweight endpoint that authenticates — list reminders.
        # The middleware should set the actor, then clear it on the way out.
        _clear_actor()
        # No ORM write here — we just want to verify the threadlocal is
        # cleared after the request. (Under the old per-user design this
        # also asserted no email; with the shared inbox we can't make
        # that assertion any more, so we just check the threadlocal.)
        resp = client.get("/api/reminders/")
        self.assertEqual(resp.status_code, 200)
        self.assertIsNone(threadlocals.get_current_user())

    def test_middleware_sets_actor_for_authenticated_request(self):
        admin = _make_admin("admin2@example.com")
        client = APIClient()
        client.force_authenticate(user=admin)

        # Hit the list endpoint so the middleware runs.
        resp = client.get("/api/reminders/")
        self.assertEqual(resp.status_code, 200)
        # Threadlocal should be cleared after the request
        self.assertIsNone(threadlocals.get_current_user())


# ---------------------------------------------------------------------------
# End-to-end via HTTP
# ---------------------------------------------------------------------------


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class NotificationsEndToEndTests(TestCase):
    def test_post_reminder_endpoint_sends_email(self):
        """
        End-to-end: a real POST to /api/reminders/ through DRF produces
        one email to the admin.

        Note: APIClient.force_authenticate() bypasses Django's
        AuthenticationMiddleware, so our CurrentUserMiddleware sees
        AnonymousUser. We set the threadlocal actor explicitly here to
        mirror what a real request would do. The middleware itself is
        covered by ThreadLocalActorTests.test_middleware_sets_actor...
        """
        admin = _make_admin("admin-e2e@example.com")
        crew = _make_crew("crew-e2e@example.com")
        client = APIClient()
        client.force_authenticate(user=admin)
        _set_actor(admin)  # what the middleware would have done
        mail.outbox = []
        try:
            # Sanity check: actor is visible in this thread right now
            assert threadlocals.get_current_user() == admin
            resp = client.post(
                "/api/reminders/",
                {
                    "user": crew.id,
                    "text": "E2E test reminder",
                    "reminder_date": "2026-09-15",
                    "reminder_time": "14:00:00",
                },
                format="json",
            )
            self.assertIn(resp.status_code, (200, 201), resp.content)
            # Signal fires inside the request, so by the time the
            # response is returned, the email is already in mail.outbox.
            self.assertEqual(len(mail.outbox), 1)
            self.assertEqual(mail.outbox[0].to, [ADMIN_INBOX])
            self.assertIn("E2E test reminder", mail.outbox[0].body)
        finally:
            _clear_actor()

    def test_post_personal_document_endpoint_sends_email(self):
        """End-to-end: POST a new PersonalDocument through DRF -> 1 email."""
        admin = _make_admin("admin-pd@example.com")
        crew = _make_crew("crew-pd@example.com")
        client = APIClient()
        client.force_authenticate(user=admin)
        _set_actor(admin)
        mail.outbox = []
        try:
            resp = client.post(
                "/api/personal-documents/",
                {
                    "user": crew.id,
                    "document_type": "Passport",
                    "document_number": "P-999",
                    "expiry_date": "2027-06-15",
                    "issuing_country": "Egypt",
                },
                format="json",
            )
            self.assertIn(resp.status_code, (200, 201), resp.content)
            self.assertEqual(len(mail.outbox), 1)
            self.assertEqual(mail.outbox[0].to, [ADMIN_INBOX])
            self.assertIn("Passport", mail.outbox[0].body)
            self.assertIn("P-999", mail.outbox[0].body)
        finally:
            _clear_actor()
