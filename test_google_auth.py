import os
import django
from unittest.mock import patch

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "saker.settings")
django.setup()

from rest_framework.test import APIClient
from django.urls import reverse
from api.models import Users

def run_tests():
    client = APIClient(SERVER_NAME='localhost')
    url = reverse('google-auth') # Assuming the name is 'google-auth'
    
    # Test 1: Invalid/Missing Token
    print("Test 1: Missing Token")
    response = client.post(url, {}, format='json')
    assert response.status_code == 400
    print("Result: Passed (Status 400)")

    # Test 2: Valid Token (Mocked)
    print("\nTest 2: Valid Token")
    mock_payload = {
        "email": "testuser@gmail.com",
        "email_verified": True,
        "given_name": "Test",
        "family_name": "User",
        "picture": "https://example.com/pic.jpg"
    }
    
    with patch('api.google_auth_serializer.google_id_token.verify_oauth2_token') as mock_verify:
        mock_verify.return_value = mock_payload
        
        response = client.post(url, {"id_token": "fake_valid_token"}, format='json')
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.content}"
        data = response.json()
        assert "access" in data
        assert "refresh" in data
        assert "user" in data
        assert data["user"]["email"] == "testuser@gmail.com"
        assert data["user"]["first_name"] == "Test"
        assert data["user"]["role"] == "Employee"
        print("Result: Passed (Status 200, JWT returned)")
        
        # Verify user was created in DB
        user = Users.objects.get(email="testuser@gmail.com")
        print(f"Verified user created in DB: {user.email}, Role: {user.role}, is_active: {user.is_active}")

if __name__ == "__main__":
    run_tests()
