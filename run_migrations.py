import os
import sys
import traceback
from django.core.management import execute_from_command_line

# Add the project directory to the sys.path
sys.path.append('/run/media/storm/TECNO SQUEARE/django test')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saker.settings')

with open('migration_log.txt', 'w') as f:
    sys.stdout = f
    sys.stderr = f
    print("Starting migrations...")
    try:
        print("Running makemigrations...")
        execute_from_command_line(['manage.py', 'makemigrations'])
        print("Running migrate...")
        execute_from_command_line(['manage.py', 'migrate'])
        print("Migrations completed successfully.")
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
