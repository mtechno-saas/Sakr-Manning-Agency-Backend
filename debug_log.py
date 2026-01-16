import os
import sys
import django
import traceback

# Add the project directory to the sys.path
sys.path.append('/run/media/storm/TECNO SQUEARE/django test')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saker.settings')

with open('debug_log.txt', 'w') as f:
    f.write("Starting debug script\n")
    try:
        django.setup()
        f.write("Django setup successful\n")
        from api.models import Users
        f.write("Users model imported\n")
        from interviews.models import Interview
        f.write("Interview model imported\n")
    except Exception as e:
        f.write(f"Error: {e}\n")
        f.write(traceback.format_exc())
    f.write("Finished\n")
