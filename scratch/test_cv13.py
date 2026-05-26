"""
Investigate CV Submission 13 on production server via API.
"""
import requests
import json

BASE = "https://backend.sakrshipping.com/api"

# Try to get CV 13 data (the detail endpoint requires auth, 
# but the download endpoint is now AllowAny)
# Let's first try downloading to see the error messages

print("="*60)
print("CV SUBMISSION 13 - DOWNLOAD TESTS (NO AUTH)")
print("="*60)

# Test all document types
tests = [
    # Singleton (User-level attachments)
    ("Passport", f"{BASE}/cv-submissions/13/download-document/?type=passport"),
    ("Seaman Book", f"{BASE}/cv-submissions/13/download-document/?type=seaman_book"),
    ("Other Seaman Book", f"{BASE}/cv-submissions/13/download-document/?type=other_seaman_book"),
    ("Marlins", f"{BASE}/cv-submissions/13/download-document/?type=marlins"),
    ("CES", f"{BASE}/cv-submissions/13/download-document/?type=ces"),
    ("COC", f"{BASE}/cv-submissions/13/download-document/?type=coc"),
    ("GOC", f"{BASE}/cv-submissions/13/download-document/?type=goc"),
    ("Health Certificate", f"{BASE}/cv-submissions/13/download-document/?type=health_certificate"),
]

# Test all singletons first
for name, url in tests:
    try:
        resp = requests.get(url, timeout=10)
        ct = resp.headers.get("Content-Type", "")
        cd = resp.headers.get("Content-Disposition", "")
        if resp.status_code == 200:
            fn = cd.split("filename=")[-1].strip('"') if "filename=" in cd else "?"
            print(f"✅ {name}: 200 OK ({len(resp.content)}b, {fn})")
        else:
            try:
                err = resp.json()
            except:
                err = resp.text[:200]
            print(f"❌ {name}: {resp.status_code} - {err}")
    except Exception as e:
        print(f"❌ {name}: {e}")

# Now try related docs - we need to guess IDs
# Let's try a range of IDs for each type
print()
print("="*60)
print("CV 13 - RELATED DOCUMENTS (trying various doc_ids)")
print("="*60)

related_types = ['license', 'vaccination', 'course', 'sea_service', 'personal_document']
for doc_type in related_types:
    print(f"\n--- {doc_type.upper()} ---")
    found = False
    for doc_id in range(1, 30):
        url = f"{BASE}/cv-submissions/13/download-document/?type={doc_type}&doc_id={doc_id}"
        try:
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                cd = resp.headers.get("Content-Disposition", "")
                fn = cd.split("filename=")[-1].strip('"') if "filename=" in cd else "?"
                print(f"  ✅ doc_id={doc_id}: 200 OK ({len(resp.content)}b, {fn})")
                found = True
            elif resp.status_code == 404:
                err = resp.json().get("error", "") if resp.headers.get("Content-Type","").startswith("application/json") else resp.text[:80]
                # Only print "not found" for first few, skip the rest
                if "not found" in str(err).lower() and doc_id <= 3:
                    print(f"  ⚠️  doc_id={doc_id}: {err}")
                elif "No file" in str(err):
                    print(f"  ⚠️  doc_id={doc_id}: {err}")
        except:
            pass
    if not found:
        print(f"  ❌ No downloadable {doc_type} found for any doc_id 1-29")

# Also check if CV 13 even exists
print()
print("="*60)
print("CHECK IF CV 13 EXISTS")
print("="*60)

# The 404 on download-document might mean the CV itself doesn't exist
resp = requests.get(f"{BASE}/cv-submissions/13/download-document/?type=passport")
print(f"Response status: {resp.status_code}")
try:
    print(f"Response body: {resp.json()}")
except:
    print(f"Response body: {resp.text[:200]}")

print("\n✅ Test complete!")
