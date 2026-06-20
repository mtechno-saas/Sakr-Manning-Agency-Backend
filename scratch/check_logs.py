import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saker.settings')
django.setup()

from ai_agents.models import FailedQueryLog

logs = FailedQueryLog.objects.all()
if not logs:
    print("No failed queries logged.")
else:
    for log in logs:
        print(f"Question: {log.question}")
        print(f"SQL: {log.generated_sql}")
        print(f"Error: {log.error_message}")
        print("-" * 50)
