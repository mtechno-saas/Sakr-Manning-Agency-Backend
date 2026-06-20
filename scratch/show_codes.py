import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saker.settings')

import django
django.setup()

from api.models import CVSubmission, Users

sub = CVSubmission.objects.get(id=170)
print(f"=== CV SUBMISSION {sub.id} ===")
print(f"User Email: {sub.user.email}")
print(f"User Phone: {sub.user.phone_number}")
