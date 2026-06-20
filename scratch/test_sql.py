import os, sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saker.settings')

import django
django.setup()

from ai_agents.sql_agent import generate_sql

try:
    sql = generate_sql("How many Motorman seafarers do we have?")
    print("SQL:", sql)
except Exception as e:
    import traceback
    traceback.print_exc()
