import re

def _field(text: str, *labels: str, default: str = "") -> str:
    for label in labels:
        esc = re.escape(label)
        
        # 1. Colon/Dash
        m = re.search(rf"(?i)(?<!\w){esc}\s*[:\-]\s*(.+)", text)
        if m:
            val = m.group(1).split("\n")[0].strip()
            val = re.split(r"[ \t]{2,}", val)[0].strip()
            if len(val) > 1 and val.upper() not in [l.upper() for l in labels]: return val

        # 2. Table Header Match (Same Line or Next Line)
        # Find the line containing the label
        for line_match in re.finditer(rf"^(.*?(?i){esc}.*)$", text, re.MULTILINE):
            line = line_match.group(1)
            # Find where the label starts in this line
            idx = line.lower().find(label.lower())
            
            # Is there a value on the SAME line after 2+ spaces?
            # E.g. "Label    Value"
            after_label = line[idx + len(label):]
            m_same = re.match(r"^[ \t]{2,}(.+)", after_label)
            if m_same:
                val = m_same.group(1).strip()
                val = re.split(r"[ \t]{2,}", val)[0].strip()
                if len(val) > 1 and val.upper() not in [l.upper() for l in labels]: return val
                
            # Otherwise, look at the NEXT line
            # Get the full text after this line
            after_line_text = text[line_match.end():]
            m_next = re.match(r"\s*\n([^\n]+)", after_line_text)
            if m_next:
                next_line = m_next.group(1)
                
                # If the current line has multiple headers separated by 2+ spaces, 
                # we need to map the column index
                headers = [h for h in re.split(r"[ \t]{2,}", line.strip()) if h]
                if len(headers) > 1:
                    # It's a table row
                    # Try to find which column our label is in
                    col_idx = -1
                    for i, h in enumerate(headers):
                        if label.lower() in h.lower():
                            col_idx = i
                            break
                    
                    if col_idx != -1:
                        # Split the next line by 2+ spaces to get values
                        values = [v for v in re.split(r"[ \t]{2,}", next_line.strip()) if v]
                        if col_idx < len(values):
                            val = values[col_idx].strip()
                            if len(val) > 1 and val.upper() not in [l.upper() for l in labels]: return val
                
                # If not a table row (or column parsing failed), just take the next line's first chunk
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
print("Nearest Port:", repr(_field(sample_text, "Nearest Port", "Port")))

