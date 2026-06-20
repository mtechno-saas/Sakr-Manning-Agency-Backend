import re

def obfuscate_emails(text):
    emails = re.findall(r'[\w\.-]+@[\w\.-]+', text)
    mapping = {}
    obfuscated = text
    for i, email in enumerate(emails):
        placeholder = f"USER_EMAIL_{i}"
        mapping[placeholder] = email
        obfuscated = obfuscated.replace(email, placeholder)
    return obfuscated, mapping

def deobfuscate_emails(text, mapping):
    for placeholder, email in mapping.items():
        text = text.replace(placeholder, email)
    return text

print(obfuscate_emails("tell me all about BODYEBED6@GMAIL.COM"))
