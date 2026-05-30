import os
import sys
import json

# Add the project root to the sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saker.settings')

import django
# Override logging so it doesn't try to access production logs when running locally
from django.conf import settings
settings.LOGGING_CONFIG = None
django.setup()

from api.models import Users, CVSubmission, Rank, UserRank, SeaService, Certificate
from api.serializer import CVSubmissionSerializer

def run_ingestion():
    # The full raw JSON from the AI CV Extractor
    # You can also load this from a file: json.load(open('data.json'))
    ai_data = {
        "user_name": "MOHAMED HASSAN ALI ABDOU ELSHAHAT",
        "user_email_display": "elshahatm97@yahoo.com",
        "position_name": "Master / Captain",
        "status": "Pending",
        "notes": "Auto-submitted via AI CV Extractor",
        "coded_rank": [
            {
                "assigned_code": "DO-1.002",
                "rank_code": "DO-1.000",
                "rank_name": "Master / Captain"
            }
        ],
        "user_documents": {
            "passport": {
                "passport_no": "A16531381",
                "issue_date": "2015-10-28",
                "expiry_date": "2022-10-27",
                "issued_by": "Egyptian Authority",
                "place_of_issue": "Damietta"
            },
            "seaman_book": {
                "seaman_book_no": "S00016399",
                "issue_date": "2021-07-11",
                "expiry_date": "2026-05-06",
                "issued_by": "EAMS",
                "place_of_issue": "Alex."
            },
            "other_seaman_book": {},
            "coc": {
                "certificate_name": "COC- MASTER",
                "certificate_number": "6661",
                "issue_date": "2021-07-07",
                "expiry_date": "2026-05-06",
                "issued_by": "EAMS",
                "issued_at": "Alex."
            },
            "goc": {
                "certificate_number": "",
                "issue_date": "",
                "expiry_date": "",
                "issued_by": "NTRA",
                "issued_at": "Cairo"
            },
            "sea_service": [],
            "marine_courses": []
        },
        "seafarer_application": {
            "1_personal_details": {
                "full_name": "MOHAMED HASSAN ALI ABDOU ELSHAHAT",
                "date_of_birth": "1975-09-12",
                "marital_status": {"single": False, "married": True},
                "nationality": "Egyptian",
                "place_of_birth": "Damietta",
            },
            "3_contact_details": {
                "home_address_city": "Damietta",
                "e_mail": "elshahatm97@yahoo.com",
                "mobile_tel": "01008450855"
            },
            "7_health_certificates_and_vaccinations": {
                "certificates": [
                    {
                        "type": "International Medical",
                        "number": "02734",
                        "issue_date": "2021-08-05",
                        "expiry_date": "2023-08-04",
                        "issued_by": "EAMS",
                        "issued_at": "Alex."
                    }
                ]
            },
            "8_marine_courses": [
                {
                    "course_name": "Proficiency In Personal Survival Techniques",
                    "number": "L 574096",
                    "issue_date": "2021-05-06",
                    "expiry_date": "2026-05-05",
                    "issued_by_at": "IHNS / ALEX."
                },
                {
                    "course_name": "Advanced Fire Prevention and Fire Fighting",
                    "number": "L 574509",
                    "issue_date": "2021-05-11",
                    "expiry_date": "2026-05-10",
                    "issued_by_at": "IHNS / ALEX."
                }
            ],
            "9_complete_sea_service_details": {
                "service_records": [
                    {
                        "company_name": "Successors shipping s.a",
                        "rank": "2nd off",
                        "vessel_name": "Arbalest",
                        "signed_on": "2011-06-03",
                        "signed_off": "2012-02-02",
                        "period": "7.29",
                        "vessel_type": "G.C",
                        "dwt": "6788"
                    },
                    {
                        "company_name": "Hydar shipping",
                        "rank": "Master",
                        "vessel_name": "AZZA H",
                        "signed_on": "2019-04-21",
                        "signed_off": "2020-03-23",
                        "period": "11.2",
                        "vessel_type": "G.C",
                        "dwt": "1955"
                    }
                ]
            }
        }
    }

    email = ai_data.get("user_email_display")
    if not email:
        print("Error: No email provided in data.")
        return

    # 1. FIND OR CREATE THE USER
    user, created = Users.objects.get_or_create(
        email=email,
        defaults={
            "first_name": ai_data.get("user_name", "Applicant").split(" ")[0],
            "role": "Employee"
        }
    )
    if created:
        print(f"Created new user: {email}")
    else:
        print(f"Found existing user: {email}")

    # --- Manually map additional personal details to User profile ---
    app_data = ai_data.get("seafarer_application", {})
    personal_details = app_data.get("1_personal_details", {})
    contact_details = app_data.get("3_contact_details", {})

    if personal_details.get("date_of_birth"):
        user.date_of_birth = personal_details.get("date_of_birth")
    if personal_details.get("nationality"):
        user.nationality = personal_details.get("nationality")
    if personal_details.get("place_of_birth"):
        user.Place_Of_Birth = personal_details.get("place_of_birth")
    
    marital = personal_details.get("marital_status", {})
    if marital.get("married"):
        user.marital_status = "Married"
    elif marital.get("single"):
        user.marital_status = "Single"

    if contact_details.get("home_address_city"):
        user.city = contact_details.get("home_address_city")
    if contact_details.get("mobile_tel"):
        user.phone_number = contact_details.get("mobile_tel")

    # Map Medical Certificate to User fields
    health_certs = app_data.get("7_health_certificates_and_vaccinations", {}).get("certificates", [])
    for cert in health_certs:
        if cert.get("type") == "International Medical":
            user.international_medical_number = cert.get("number")
            user.international_medical_issue_date = cert.get("issue_date") or None
            user.international_medical_expiry_date = cert.get("expiry_date") or None

    user.save()
    print("User personal details and contact info synced.")

    # 2. TRANSFORM DATA FOR THE CV SUBMISSION SERIALIZER (Passports, Seaman Book, COCs)
    name_parts = ai_data["user_name"].split(" ", 1)
    first_name = name_parts[0]
    middle_name = name_parts[1] if len(name_parts) > 1 else ""

    payload = {
        "user_first_name": first_name,
        "user_middle_name": middle_name,
        "user_email": email,
        "position": ai_data.get("position_name"),
        "status": ai_data.get("status"),
        "notes": ai_data.get("notes"),
        "coded_rank_input": ai_data.get("coded_rank"),
        "passport_update": ai_data["user_documents"].get("passport"),
        "seaman_book_update": ai_data["user_documents"].get("seaman_book"),
        "coc_update": ai_data["user_documents"].get("coc"),
        "goc_update": ai_data["user_documents"].get("goc"),
    }

    # Remove empty/null dates so serializer doesn't choke on ""
    for key in ['passport_update', 'seaman_book_update', 'coc_update', 'goc_update']:
        if payload.get(key):
            for subkey in ['issue_date', 'expiry_date']:
                if subkey in payload[key] and not payload[key][subkey]:
                    payload[key][subkey] = None

    # Determine the requested position ID/Rank
    position_name = payload.get("position")
    rank_obj = Rank.objects.filter(name__iexact=position_name).first() if position_name else None

    # Look for an existing CV Submission for this user (and position)
    if rank_obj:
        existing_submission = CVSubmission.objects.filter(user=user, position=rank_obj).first()
    else:
        existing_submission = CVSubmission.objects.filter(user=user).first()

    if existing_submission:
        print(f"Found existing CV Submission (ID: {existing_submission.id}). Updating it...")
        serializer = CVSubmissionSerializer(instance=existing_submission, data=payload, partial=True)
    else:
        print("No existing CV Submission found. Creating a new one...")
        serializer = CVSubmissionSerializer(data=payload)

    if serializer.is_valid():
        submission = serializer.save(user=user)
        print(f"Successfully ingested CV Submission ID: {submission.id} via DRF Service Layer.")
    else:
        print("Serializer validation failed:", json.dumps(serializer.errors, indent=2))
        return

    # 3. MANUALLY INGEST SEA SERVICES via ORM
    # Try user_documents first, fallback to seafarer_application
    sea_services_data = ai_data.get("user_documents", {}).get("sea_service", [])
    if not sea_services_data:
        sea_services_data = app_data.get("9_complete_sea_service_details", {}).get("service_records", [])

    if sea_services_data:
        count = 0
        for ss_data in sea_services_data:
            ss_signed_on = ss_data.get("signed_on") or None
            ss_signed_off = ss_data.get("signed_off") or None
            
            if SeaService.objects.filter(
                user=user, 
                company_name=ss_data.get("company_name", ""),
                vessel_name=ss_data.get("vessel_name", ""),
                signed_on=ss_signed_on
            ).exists():
                continue
                
            SeaService.objects.create(
                user=user,
                company_name=ss_data.get("company_name", ""),
                rank=ss_data.get("rank", ""),
                vessel_name=ss_data.get("vessel_name", ""),
                signed_on=ss_signed_on,
                signed_off=ss_signed_off,
                period=ss_data.get("period", ""),
                vessel_type=ss_data.get("vessel_type", ""),
                dwt=ss_data.get("dwt", "")
            )
            count += 1
        print(f"Ingested {count} new Sea Service records.")

    # 4. MANUALLY INGEST MARINE COURSES via ORM
    # Try user_documents first, fallback to seafarer_application
    courses_data = ai_data.get("user_documents", {}).get("marine_courses", [])
    if not courses_data:
        courses_data = app_data.get("8_marine_courses", [])

    if courses_data:
        try:
            from courses.models import Course
            count = 0
            for course_data in courses_data:
                if Course.objects.filter(user=user, course_name=course_data.get("course_name")).exists():
                    continue

                issued_by_at = course_data.get("issued_by_at", "")
                issued_by = ""
                issued_at = ""
                if issued_by_at and "/" in issued_by_at:
                    parts = issued_by_at.split("/", 1)
                    issued_by = parts[0].strip()
                    issued_at = parts[1].strip()
                elif issued_by_at:
                    issued_by = issued_by_at
                    
                Course.objects.create(
                    user=user,
                    course_name=course_data.get("course_name"),
                    course_number=course_data.get("number"),
                    issue_date=course_data.get("issue_date") or None,
                    expiry_date=course_data.get("expiry_date") or None,
                    issued_by=issued_by,
                    issued_at=issued_at
                )
                count += 1
            print(f"Ingested {count} new Marine Course records.")
        except ImportError:
            print("Warning: courses.models.Course not found.")

def cleanup_duplicates():
    from django.db.models import Count
    # Find users with multiple CV Submissions for the same position
    duplicates = CVSubmission.objects.values('user', 'position').annotate(
        count=Count('id')
    ).filter(count__gt=1)

    for dup in duplicates:
        user_id = dup['user']
        pos_id = dup['position']
        # Get all submissions for this user/position ordered by latest first
        submissions = CVSubmission.objects.filter(
            user_id=user_id, position_id=pos_id
        ).order_by('-id')
        
        # Keep the first one (most recent), delete the rest
        if submissions.count() > 1:
            to_keep = submissions.first()
            to_delete = submissions.exclude(id=to_keep.id)
            deleted_count, _ = to_delete.delete()
            print(f"Cleaned up {deleted_count} duplicate CV Submissions for User ID {user_id}.")

if __name__ == "__main__":
    run_ingestion()
    cleanup_duplicates()
