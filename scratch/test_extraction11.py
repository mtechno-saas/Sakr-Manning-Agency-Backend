import re

def _field(text: str, *labels: str, default: str = "") -> str:
    for label in labels:
        esc = re.escape(label)
        
        m = re.search(rf"(?<!\w){esc}\s*[:\-|]\s*(.+)", text, re.IGNORECASE)
        if m: return "MATCH: " + m.group(1).split("\n")[0].strip()

    return default

sample_text = """
Full Name | Mosaad Helmy
Date of Birth | 18/02/1978
"""
print("Full Name:", repr(_field(sample_text, "Full Name")))
print("Date of Birth:", repr(_field(sample_text, "Date of Birth")))
