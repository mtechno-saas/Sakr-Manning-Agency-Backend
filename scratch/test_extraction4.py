import re

def _field(text: str, *labels: str, default: str = "") -> str:
    for label in labels:
        esc = re.escape(label)
        
        # 1. Colon/Dash
        m = re.search(rf"(?<!\w){esc}\s*[:\-]\s*(.+)", text, re.IGNORECASE)
        if m:
            val = m.group(1).split("\n")[0].strip()
            val = re.split(r"[ \t]{2,}", val)[0].strip()
            if len(val) > 1 and val.upper() not in [l.upper() for l in labels]: return val

        # 2. Table Header Match (Same Line or Next Line)
        for line_match in re.finditer(rf"^(.*?{esc}.*)$", text, re.MULTILINE | re.IGNORECASE):
            line = line_match.group(1)
            idx = line.lower().find(label.lower())
            
            after_line_text = text[line_match.end():]
            m_next = re.match(r"\s*\n([^\n]+)", after_line_text)
            
            headers = [(m.group(), m.start()) for m in re.finditer(r"[^\s]+(?: [^\s]+)*", line.strip())]
            next_line = m_next.group(1) if m_next else ""
            values = [(m.group(), m.start()) for m in re.finditer(r"[^\s]+(?: [^\s]+)*", next_line.strip())]
            
            # Is it a table row with multiple headers and values below?
            is_table = len(headers) > 1 and len(values) >= 1
            
            if is_table:
                for i, (h_text, h_pos) in enumerate(headers):
                    if label.lower() in h_text.lower():
                        # Find the value closest in horizontal position
                        best_val = min(values, key=lambda v: abs(v[1] - h_pos), default=None)
                        if best_val:
                            val = best_val[0]
                            if len(val) > 1 and val.upper() not in [l.upper() for l in labels]: return val
                        break
            else:
                # Not a table, try same line
                after_label = line[idx + len(label):]
                m_same = re.match(r"^[ \t]{2,}(.+)", after_label)
                if m_same:
                    val = m_same.group(1).strip()
                    val = re.split(r"[ \t]{2,}", val)[0].strip()
                    if len(val) > 1 and val.upper() not in [l.upper() for l in labels]: return val
                    
                # Next line fallback
                if next_line:
                    val = next_line.strip()
                    val = re.split(r"[ \t]{2,}", val)[0].strip()
                    if len(val) > 1 and val.upper() not in [l.upper() for l in labels]: return val

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
print("Date of Birth:", repr(_field(sample_text, "Date of Birth", "DOB")))
print("Nationality:", repr(_field(sample_text, "Nationality")))
print("Marital Status:", repr(_field(sample_text, "Marital Status")))
print("Height:", repr(_field(sample_text, "Height (cm)", "Height")))
print("Nearest Port:", repr(_field(sample_text, "Nearest Port", "Port")))

