import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saker.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from api.models import Users, Rank
import json

def run_test():
    client = APIClient()
    user, _ = Users.objects.get_or_create(email="admin2@test.com", role="Admin")
    rank, _ = Rank.objects.get_or_create(id=1, code="CO", name="Chief Officer")
    client.force_authenticate(user=user)
    
    payload = {
      'email': 'mahmoud123@gmail.com', 
      'first_name': 'mahmoud', 
      'middle_name': 'Ahmed', 
      'phone_number': '21546546421645', 
      'nationality': 'Egyption', 
      'date_of_birth': '1985-04-01', 
      'marital_status': 'SINGLE', 
      'user_status': 'ON_SITE', 
      'certificate_ids': [], 
      'rank_ids': [1]
    }
    
    response = client.post('/api/users/users/', data=payload, format='json')
    print("STATUS", response.status_code)
    print("RESPONSE", response.json())

if __name__ == "__main__":
    run_test()
