"""Tests for the Expiring Documents app."""
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from api.models import Users, PersonalDocument


class ExpiringDocumentsEndpointTestCase(TestCase):
    """Smoke tests for the aggregated expiring-documents endpoint."""

    def setUp(self):
        # Create a test user
        self.user = Users.objects.create_user(
            email="crew@example.com",
            password="test1234",
            first_name="Hisham",
            middle_name="Hassan",
        )

    def test_endpoint_requires_auth(self):
        from rest_framework.test import APIClient
        client = APIClient()
        resp = client.get("/api/expiring-documents/")
        # No auth -> 401 or 403 depending on DRF settings
        self.assertIn(resp.status_code, (401, 403))

    def test_endpoint_rejects_employee_role(self):
        from rest_framework.test import APIClient
        self.user.role = "Employee"
        self.user.save()
        client = APIClient()
        client.force_authenticate(user=self.user)
        resp = client.get("/api/expiring-documents/")
        self.assertEqual(resp.status_code, 403)

    def test_endpoint_returns_counts(self):
        from rest_framework.test import APIClient
        self.user.role = "Admin"
        self.user.save()
        client = APIClient()
        client.force_authenticate(user=self.user)
        resp = client.get("/api/expiring-documents/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("counts", data)
        self.assertIn("results", data)
        self.assertIn("days_window", data)
        self.assertIn("today", data)
        self.assertIn("category_filter", data)

    def test_expired_passport_is_returned(self):
        from rest_framework.test import APIClient
        self.user.role = "Admin"
        self.user.passport_expiry_date = timezone.localdate() - timedelta(days=5)
        self.user.save()

        client = APIClient()
        client.force_authenticate(user=self.user)
        resp = client.get("/api/expiring-documents/?days=30")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertGreater(data["counts"]["expired"], 0)
