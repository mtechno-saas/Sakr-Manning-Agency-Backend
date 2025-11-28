#!/usr/bin/env python
"""
Test script for Create User endpoint (POST /api/users/)
This script tests the user creation functionality with all required fields.
"""

import requests
import json
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"  # Adjust if your server runs on a different port
API_ENDPOINT = f"{BASE_URL}/api/users/create/"

# Test data matching the requirements
test_user_data = {
    "email": "captain@example.com",
    "password": "SecurePassword123!",  # Added password field
    "first_name": "James",
    "middle_name": "Robert",
    "phone_number": "+1234567890",
    "nationality": "Egypt",
    "date_of_birth": "1985-05-15",
    "role": "Employee",  # Valid roles: Admin, HR Manager, Recruiter, Employee
}

def test_create_user_basic():
    """Test basic user creation without rank_ids and certificate_ids"""
    print("=" * 60)
    print("Test 1: Basic User Creation (without ranks/certificates)")
    print("=" * 60)
    
    response = requests.post(
        API_ENDPOINT,
        data=test_user_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        print("✅ Basic user creation PASSED")
        return response.json()
    else:
        print("❌ Basic user creation FAILED")
        return None

def test_create_user_with_relations():
    """Test user creation with rank_ids and certificate_ids"""
    print("\n" + "=" * 60)
    print("Test 2: User Creation with Ranks and Certificates")
    print("=" * 60)
    
    # Modified email to avoid duplicate
    data_with_relations = test_user_data.copy()
    data_with_relations["email"] = "captain2@example.com"
    data_with_relations["rank_ids"] = [1, 2]  # Note: these IDs must exist in DB
    data_with_relations["certificate_ids"] = [5, 10, 15]  # Note: these IDs must exist in DB
    
    response = requests.post(
        API_ENDPOINT,
        json=data_with_relations
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        print("✅ User creation with relations PASSED")
        return response.json()
    else:
        print(f"❌ User creation with relations FAILED")
        print(f"Error details: {response.text}")
        return None

def test_create_user_with_image():
    """Test user creation with profile_image (multipart/form-data)"""
    print("\n" + "=" * 60)
    print("Test 3: User Creation with Profile Image")
    print("=" * 60)
    
    # Create a simple test image file if it doesn't exist
    test_image_path = Path("/tmp/test_profile.jpg")
    if not test_image_path.exists():
        # Create a minimal valid JPEG file
        with open(test_image_path, "wb") as f:
            # Minimal JPEG header (not a real image, but valid for testing)
            f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xd9')
    
    # Modified email to avoid duplicate
    form_data = test_user_data.copy()
    form_data["email"] = "captain3@example.com"
    
    files = {
        'profile_image': ('profile.jpg', open(test_image_path, 'rb'), 'image/jpeg')
    }
    
    response = requests.post(
        API_ENDPOINT,
        data=form_data,
        files=files
    )
    
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    
    if response.status_code == 201:
        print("✅ User creation with image PASSED")
        return response.json()
    else:
        print("❌ User creation with image FAILED")
        return None

def test_create_user_different_roles():
    """Test user creation with different role values"""
    print("\n" + "=" * 60)
    print("Test 4: User Creation with Different Roles")
    print("=" * 60)
    
    roles = ['Admin', 'HR Manager', 'Recruiter', 'Employee']
    
    for i, role in enumerate(roles, start=4):
        data = test_user_data.copy()
        data["email"] = f"user{i}@example.com"
        data["role"] = role
        
        response = requests.post(
            API_ENDPOINT,
            json=data
        )
        
        print(f"\nRole: {role}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            print(f"✅ Role '{role}' - PASSED")
        else:
            print(f"❌ Role '{role}' - FAILED")
            print(f"Response: {response.text}")

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("STARTING CREATE USER ENDPOINT TESTS")
    print("=" * 60)
    print(f"API Endpoint: {API_ENDPOINT}")
    print("\nNOTE: Make sure your Django server is running before executing tests!")
    print("=" * 60)
    
    try:
        # Test 1: Basic user creation
        test_create_user_basic()
        
        # Test 2: User creation with relations
        test_create_user_with_relations()
        
        # Test 3: User creation with profile image
        test_create_user_with_image()
        
        # Test 4: User creation with different roles
        test_create_user_different_roles()
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to the server.")
        print(f"Make sure your Django server is running on {BASE_URL}")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")

if __name__ == "__main__":
    main()
