import sys, django, os
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saker.settings')
django.setup()

from ai_agents.sql_agent import process_database_question

def obfuscate_emails(text):
    import re
    emails = re.findall(r'[\w\.-]+@[\w\.-]+', text)
    mapping = {}
    obfuscated = text
    for i, email in enumerate(emails):
        placeholder = f"REDACTED_EMAIL_{i}"
        mapping[placeholder] = email
        obfuscated = obfuscated.replace(email, placeholder)
    return obfuscated, mapping

q = "tell me all about BODYEBED6@GMAIL.COM"
obf_q, mapping = obfuscate_emails(q)
print("Obf:", obf_q)
