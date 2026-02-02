from django.test import TestCase
from rest_framework.test import APIClient
from api.models import Users
from rest_framework import status
import json
from datetime import date

class ContractFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/register/'
        self.login_url = '/api/login/'
        
    def test_full_contract_generation_flow(self):
        # 1. Quick Apply (Registration)
        print("\n--- Step 1: Quick Apply (Registration) ---")
        user_data = {
            "email": "testcandidate@example.com",
            "password": "StrongPassword123!",
            "first_name": "Test"
        }
        response = self.client.post(self.register_url, user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # ID might not be in response if not in serializer fields
        user = Users.objects.get(email=user_data['email'])
        user_id = user.id
        print(f"User created with ID: {user_id}")
        
        # 2. Login to get Token
        print("\n--- Step 2: Login ---")
        login_data = {
            "email": "testcandidate@example.com",
            "password": "StrongPassword123!"
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access_token = response.data['access']
        print("Logged in, token received.")
        
        # Authenticate client
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        
        # 3. Fill All Fields (Update Profile)
        print("\n--- Step 3: Fill Profile Fields ---")
        # We need to set IsAuthenticated permissions/roles or similar if needed
        # By default new users might be 'Employee'.
        # Let's update the user profile.
        
        profile_data = {
            "middle_name": "Candidate",
            "date_of_birth": "1995-05-15",
            "marital_status": "Single",
            "nationality": "Egyptian",
            "Height_Cm": 180,
            "Weight_Kg": 75,
            "Place_Of_Birth": "Alexandria",
            "shirt_size": "L",
            "trouser_size": "32",
            "shoes_size": "42",
            "address": "123 Corniche Road",
            "phone_number": "+201000000000",
            
            # Education
            "college_or_school": "Maritime Academy",
            "english_language_level": "Fluent",
            
            # Passport
            "passport_no": "A12345678",
            "passport_issue_date": "2020-01-01",
            "passport_expiry_date": "2030-01-01",
            "passport_issued_by": "Egypt Immigration",
            
            # Seaman Book
            "seaman_book_no": "SB123456",
            "seaman_book_issue_date": "2021-01-01",
            "seaman_book_expiry_date": "2026-01-01",
            "seaman_book_issued_by": "EAMS",
            
            # Next of Kin
            "next_of_kin_full_name": "Parent Name",
            "next_of_kin_relationship": "Father",
            "next_of_kin_address_country": "Alexandria, Egypt",
            "next_of_kin_phone": "+201222222222"
        }
        
        update_url = f'/api/users/{user_id}/' 
        response = self.client.patch(update_url, profile_data, format='json')
        # Note: If Employee role restricts updating some fields, we might need to check permissions.
        # Assuming Employee can update own profile.
        if response.status_code != status.HTTP_200_OK:
            print(f"Update failed: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("Profile updated successfully.")
        
        # 4. Generate Contract
        print("\n--- Step 4: Generate Contract ---")
        generate_url = f'/api/contracts/generate/{user_id}/'
        response = self.client.post(generate_url)
        
        if response.status_code != status.HTTP_200_OK:
            print(f"Generation failed: {response.data}")
            
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('file_url', response.data)
        print(f"Contract generated! URL: {response.data['file_url']}")
