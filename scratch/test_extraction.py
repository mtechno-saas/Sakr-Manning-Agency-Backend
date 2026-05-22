import re

def _field(text: str, *labels: str, default: str = "") -> str:
    for label in labels:
        esc = re.escape(label)
        patterns = [
            rf"(?i)(?<!\w){esc}\s*[:\-]\s*(.+)",
            rf"(?i)(?<!\w){esc}[ \t]{{2,}}([^\n]+)",
            rf"(?i)(?<!\w){esc}\s*\n\s*([^\n]+)",
        ]
        for pattern in patterns:
            m = re.search(pattern, text)
            if m:
                value = m.group(1).strip()
                value = value.split("\n")[0].strip()
                value = re.split(r"[ \t]{2,}", value)[0].strip()
                if value and len(value) > 2 and value.upper() not in [l.upper() for l in labels]:
                    return value
    return default

sample_text = """
1. PERSONAL DETAILS
Full Name                                          Date of Birth                Nationality
MOSAAD HELMY IBRAHIM ELAFANY HELMY IBRAHIM         18/02/1978                   Egyptian
Marital Status                                     Height (cm)                  Weight (kg)                 Place of Birth
[ ] Single [x] Married                             178                          75                          Egyptian
Overall Size                Shirt Size             Trouser Size                 Shoes Size                  Nearest Port
M                           M                      36                           44                          cairo airport

2. EDUCATION & QUALIFICATIONS
"""

print("Full Name:", repr(_field(sample_text, "Full Name")))
print("Date of Birth:", repr(_field(sample_text, "Date of Birth")))
print("Nationality:", repr(_field(sample_text, "Nationality")))
print("Marital Status:", repr(_field(sample_text, "Marital Status")))
print("Nearest Port:", repr(_field(sample_text, "Nearest Port", "Port")))

