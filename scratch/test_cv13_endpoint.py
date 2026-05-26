import requests
import json

BASE = "https://backend.sakrshipping.com/api"

# Login to get token
login_resp = requests.post(f"{BASE}/login/", json={
    "email": "admin@sakrshipping.com",
    "password": "admin"
})

if login_resp.status_code == 200:
    token = login_resp.json().get("access")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try fetching CV 13
    resp = requests.get(f"{BASE}/cv-submissions/13/", headers=headers)
    print(f"Status Code CV 13: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print("Keys returned for CV 13:")
        print(list(data.keys()))
        if "user_documents" in data:
            print("user_documents keys:")
            print(list(data["user_documents"].keys()))
            
            # Print specifically the download URLs to see what they look like
            docs = data["user_documents"]
            print(f"Passport file_url: {docs.get('passport', {}).get('file_url')}")
            print(f"Passport download_url: {docs.get('passport', {}).get('download_url')}")
        else:
            print("❌ user_documents MISSING!")
    else:
        print("Response:", resp.text[:500])
        
    print("\n--------------------------")
    # Try fetching CV 55 (the one user pasted)
    resp55 = requests.get(f"{BASE}/cv-submissions/55/", headers=headers)
    print(f"Status Code CV 55: {resp55.status_code}")
    if resp55.status_code == 200:
        data55 = resp55.json()
        print("Keys returned for CV 55:")
        print(list(data55.keys()))
    else:
        print("Response:", resp55.text[:500])
else:
    print("Login failed:", login_resp.text)
