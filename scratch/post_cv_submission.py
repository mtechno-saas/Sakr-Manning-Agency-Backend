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

def run_ingestion(ai_data, file_name=""):
    email = ai_data.get("user_email_display")
    if not email:
        print(f"[{file_name}] Error: No email provided in data.")
        return False

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
        print(f"[{file_name}] Successfully ingested CV Submission ID: {submission.id} via DRF Service Layer.")
    else:
        print(f"[{file_name}] Serializer validation failed:", json.dumps(serializer.errors, indent=2))
        return False

    # 3. MANUALLY INGEST SEA SERVICES via ORM
    # Try user_documents first, fallback to seafarer_application
    sea_services_data = ai_data.get("user_documents", {}).get("sea_service", [])
    if not sea_services_data:
        sea_services_data = app_data.get("9_complete_sea_service_details", {}).get("service_records", [])

    if sea_services_data:
        count = 0
        for ss_data in sea_services_data:
            ss_signed_on = ss_data.get("signed_on")
            if ss_signed_on and (ss_signed_on == "XXXXX" or ss_signed_on == "UNLIMITED"):
                ss_signed_on = None
            else:
                ss_signed_on = ss_signed_on or None

            ss_signed_off = ss_data.get("signed_off")
            if ss_signed_off and (ss_signed_off == "XXXXX" or ss_signed_off == "UNLIMITED"):
                ss_signed_off = None
            else:
                ss_signed_off = ss_signed_off or None
            
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
                    
                issue_date = course_data.get("issue_date")
                if issue_date and (issue_date == "XXXXX" or issue_date == "UNLIMITED"):
                    issue_date = None
                    
                expiry_date = course_data.get("expiry_date")
                if expiry_date and (expiry_date == "XXXXX" or expiry_date == "UNLIMITED"):
                    expiry_date = None

                Course.objects.create(
                    user=user,
                    course_name=course_data.get("course_name"),
                    course_number=course_data.get("number"),
                    issue_date=issue_date or None,
                    expiry_date=expiry_date or None,
                    issued_by=issued_by,
                    issued_at=issued_at
                )
                count += 1
            print(f"Ingested {count} new Marine Course records.")
        except ImportError:
            print("Warning: courses.models.Course not found.")

    return True

def process_folder(folder_path="json"):
    import shutil
    
    # Ensure folder paths exist
    folder_path = os.path.join(project_root, folder_path)
    processed_folder = os.path.join(project_root, f"{folder_path}_processed")
    os.makedirs(processed_folder, exist_ok=True)
    
    if not os.path.exists(folder_path):
        print(f"Folder not found: {folder_path}")
        return

    json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
    print(f"Found {len(json_files)} JSON files in {folder_path}. Starting batch processing...\n")

    success_count = 0
    fail_count = 0

    for filename in json_files:
        file_path = os.path.join(folder_path, filename)
        print(f"--- Processing {filename} ---")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                ai_data = json.load(f)
            
            success = run_ingestion(ai_data, file_name=filename)
            
            if success:
                # Move to processed folder
                shutil.move(file_path, os.path.join(processed_folder, filename))
                success_count += 1
            else:
                fail_count += 1
        except Exception as e:
            print(f"[{filename}] Error reading or processing file: {e}")
            fail_count += 1

    print(f"\nBatch processing complete! Success: {success_count}, Failed: {fail_count}")

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
    process_folder("json")
    print("Running duplicate cleanup just in case...")
    cleanup_duplicates()
