import os
import sys
import django

# Add the project directory to the sys.path
sys.path.append('/run/media/storm/TECNO SQUEARE/django test')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saker.settings')

try:
    django.setup()
    print("Django setup successful")
    from api.models import Users
    print("Users model imported")
    from interviews.models import Interview
    print("Interview model imported")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
