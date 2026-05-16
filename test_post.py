import requests
import json
import time
import subprocess
import os

proc = subprocess.Popen(["python", "manage.py", "runserver", "8080"])
time.sleep(3)

try:
    # 1. Login
    resp = requests.post("http://localhost:8080/api/login/", json={
        "email": "admin@test.com",
        "password": "adminpass"
    })
    token = resp.json().get("access")
    print("Token:", bool(token))

    # 2. Create user
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
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
    res = requests.post("http://localhost:8080/api/users/users/", json=payload, headers=headers)
    print("Status:", res.status_code)
    print("Response:", res.text)
finally:
    proc.terminate()
