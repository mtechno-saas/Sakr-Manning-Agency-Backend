"""
Test all CV Submission download links on the live server.
Tests: Travel Docs, Certificates, Vaccination, Marine Courses, Sea-Service
"""
import requests

BASE = "https://backend.sakrshipping.com/api"
CV_ID = 12  # user 27 - karlson

# First, get a JWT token
login_resp = requests.post(f"{BASE}/token/", json={
    "email": "admin@sakrshipping.com",
    "password": "admin"
})

if login_resp.status_code != 200:
    # Try another common admin login
    login_resp = requests.post(f"{BASE}/token/", json={
        "email": "admin@admin.com",
        "password": "admin"
    })

if login_resp.status_code == 200:
    token = login_resp.json().get("access")
    print(f"✅ Login successful, token: {token[:30]}...")
else:
    print(f"❌ Login failed: {login_resp.status_code} - {login_resp.text[:200]}")
    token = None

headers = {"Authorization": f"Bearer {token}"} if token else {}

# ============================================================
# Test download links WITHOUT auth (how <a href> works)
# ============================================================
print("\n" + "="*60)
print("TESTING CV SUBMISSION DOWNLOAD LINKS (NO AUTH - like <a href>)")
print("="*60)

tests = [
    # Travel Documents
    ("Passport", f"{BASE}/cv-submissions/{CV_ID}/download-document/?type=passport"),
    ("Seaman Book", f"{BASE}/cv-submissions/{CV_ID}/download-document/?type=seaman_book"),
    ("Other Seaman Book", f"{BASE}/cv-submissions/{CV_ID}/download-document/?type=other_seaman_book"),
    ("Personal Doc (UAE visa)", f"{BASE}/cv-submissions/{CV_ID}/download-document/?type=personal_document&doc_id=11"),
    
    # Certificates
    ("COC Certificate", f"{BASE}/cv-submissions/{CV_ID}/download-document/?type=coc"),
    ("GOC Certificate", f"{BASE}/cv-submissions/{CV_ID}/download-document/?type=goc"),
    ("License (id=1)", f"{BASE}/cv-submissions/{CV_ID}/download-document/?type=license&doc_id=1"),
    
    # Vaccination
    ("Vaccination (id=5)", f"{BASE}/cv-submissions/{CV_ID}/download-document/?type=vaccination&doc_id=5"),
    
    # Marine Courses
    ("Course (id=8)", f"{BASE}/cv-submissions/{CV_ID}/download-document/?type=course&doc_id=8"),
    
    # Sea-Service
    ("Sea Service (id=7)", f"{BASE}/cv-submissions/{CV_ID}/download-document/?type=sea_service&doc_id=7"),
]

for name, url in tests:
    try:
        resp = requests.get(url, timeout=10)
        content_type = resp.headers.get("Content-Type", "unknown")
        content_disp = resp.headers.get("Content-Disposition", "")
        
        if resp.status_code == 200:
            size = len(resp.content)
            filename = ""
            if "filename=" in content_disp:
                filename = content_disp.split("filename=")[-1].strip('"')
            print(f"✅ {name}: OK (status=200, type={content_type}, size={size}b, file={filename})")
        elif resp.status_code == 404:
            try:
                err = resp.json().get("error", "")
            except:
                err = resp.text[:100]
            print(f"⚠️  {name}: 404 - {err}")
        elif resp.status_code == 401:
            print(f"❌ {name}: 401 UNAUTHORIZED - Auth still required!")
        elif resp.status_code == 403:
            print(f"❌ {name}: 403 FORBIDDEN - Permission denied!")
        else:
            print(f"❌ {name}: {resp.status_code} - {resp.text[:100]}")
    except Exception as e:
        print(f"❌ {name}: EXCEPTION - {e}")

# ============================================================
# Test User endpoint download links WITH auth (how downloadsApi works)
# ============================================================
if token:
    print("\n" + "="*60)
    print("TESTING USER DOWNLOAD LINKS (WITH AUTH - like downloadsApi)")
    print("="*60)
    
    user_id = 27
    user_tests = [
        ("Passport", f"{BASE}/users/users/{user_id}/download-document/?type=passport"),
        ("Seaman Book", f"{BASE}/users/users/{user_id}/download-document/?type=seaman_book"),
        ("Personal Doc (id=11)", f"{BASE}/users/users/{user_id}/download-document/?type=personal_document&doc_id=11"),
        ("License (id=1)", f"{BASE}/users/users/{user_id}/download-document/?type=license&doc_id=1"),
        ("Vaccination (id=5)", f"{BASE}/users/users/{user_id}/download-document/?type=vaccination&doc_id=5"),
        ("Course (id=8)", f"{BASE}/users/users/{user_id}/download-document/?type=course&doc_id=8"),
        ("Sea Service (id=7)", f"{BASE}/users/users/{user_id}/download-document/?type=sea_service&doc_id=7"),
        ("Marlins", f"{BASE}/users/users/{user_id}/download-document/?type=marlins"),
        ("CES", f"{BASE}/users/users/{user_id}/download-document/?type=ces"),
    ]
    
    for name, url in user_tests:
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            content_type = resp.headers.get("Content-Type", "unknown")
            content_disp = resp.headers.get("Content-Disposition", "")
            
            if resp.status_code == 200:
                size = len(resp.content)
                filename = ""
                if "filename=" in content_disp:
                    filename = content_disp.split("filename=")[-1].strip('"')
                print(f"✅ {name}: OK (status=200, type={content_type}, size={size}b, file={filename})")
            elif resp.status_code == 404:
                try:
                    err = resp.json().get("error", "")
                except:
                    err = resp.text[:100]
                print(f"⚠️  {name}: 404 - {err}")
            elif resp.status_code == 401:
                print(f"❌ {name}: 401 UNAUTHORIZED")
            elif resp.status_code == 403:
                print(f"❌ {name}: 403 FORBIDDEN")
            else:
                print(f"❌ {name}: {resp.status_code} - {resp.text[:100]}")
        except Exception as e:
            print(f"❌ {name}: EXCEPTION - {e}")

# ============================================================
# Test direct media URLs
# ============================================================
print("\n" + "="*60)
print("TESTING DIRECT MEDIA URLs (public /media/ paths)")
print("="*60)

media_tests = [
    ("Vaccination file", "https://backend.sakrshipping.com/media/vaccinations/marlins_82-1.pdf"),
    ("License file", "https://backend.sakrshipping.com/media/user_27/licenses/WhatsApp_Image_2026-05-16_at_2.09.48_PM.jpeg"),
    ("Course file", "https://backend.sakrshipping.com/media/course_docs/Screenshot_From_2026-05-18_21-24-25.png"),
    ("Sea Service file", "https://backend.sakrshipping.com/media/sea_services/ahmed_tarek_abd_el_aziez_Application-3.pdf"),
    ("Personal Doc file", "https://backend.sakrshipping.com/media/personal_documents/marlins_82.pdf"),
    ("Marlins file", "https://backend.sakrshipping.com/media/marlins_tests/Screenshot_From_2026-05-18_21-24-25.png"),
]

for name, url in media_tests:
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            print(f"✅ {name}: OK (size={len(resp.content)}b, type={resp.headers.get('Content-Type', 'unknown')})")
        else:
            print(f"❌ {name}: {resp.status_code}")
    except Exception as e:
        print(f"❌ {name}: EXCEPTION - {e}")

print("\n✅ Test complete!")
