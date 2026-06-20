import os
import sys

# Set the Django settings module
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saker.settings')

import django
django.setup()

from api.models import CVSubmission, SeaService
from courses.models import Course

def show(submission_id):
    sub = CVSubmission.objects.get(id=submission_id)
    print(f"=== CV SUBMISSION {sub.id} ===")
    print(f"User Email: {sub.user.email}")
    print(f"Position: {sub.position.name if sub.position else 'N/A'}")
    
    services = SeaService.objects.filter(user=sub.user)
    print(f"\n--- Sea Services ({services.count()}) ---")
    for s in services:
        print(f"{s.vessel_name} | {s.rank} | {s.company_name} | {s.signed_on} to {s.signed_off}")
        
    courses = Course.objects.filter(user=sub.user)
    print(f"\n--- Marine Courses ({courses.count()}) ---")
    for c in courses:
        print(f"{c.course_name} | {c.course_number} | Issue: {c.issue_date} | Exp: {c.expiry_date}")

if __name__ == "__main__":
    show(139)
