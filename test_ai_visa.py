import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saker.settings')
django.setup()

from ai_agents.endpoint_query_engine import plan_query, execute_query
from langchain_google_genai import ChatGoogleGenerativeAI

model = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite", 
    google_api_key=os.environ.get("GOOGLE_API_KEY", "missing_key_please_add_to_env"),
)

question = "which one has got US Visa B1/B2 visa"
plan = plan_query(question, model)
print(f"Plan: {plan}")

if plan:
    results = execute_query(plan)
    print(f"Results: {results}")
