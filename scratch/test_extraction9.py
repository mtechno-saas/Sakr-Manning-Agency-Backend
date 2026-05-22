import re

def _field(text: str, *labels: str, default: str = "") -> str:
    for label in labels:
        esc = re.escape(label)
        
        m = re.search(rf"(?<!\w){esc}\s*[:\-]\s*(.+)", text, re.IGNORECASE)
        if m: return "MATCH 1"

        for line_match in re.finditer(rf"^(.*?{esc}.*)$", text, re.MULTILINE | re.IGNORECASE):
            line = line_match.group(1)
            idx = line.lower().find(label.lower())
            
            after_line_text = text[line_match.end():]
            m_next = re.match(r"[ \t]*\n([^\n]+)", after_line_text)
            
            headers = [(m.group(), m.start()) for m in re.finditer(r"[^\s]+(?: [^\s]+)*", line)]
            next_line = m_next.group(1) if m_next else ""
            values = [(m.group(), m.start()) for m in re.finditer(r"[^\s]+(?: [^\s]+)*", next_line)]
            
            is_table = len(headers) > 1 and len(values) >= 1
            
            if is_table:
                for i, (h_text, h_pos) in enumerate(headers):
                    if label.lower() in h_text.lower():
                        valid_values = [v for v in values if abs(v[1] - h_pos) <= 20]
                        if valid_values:
                            best_val = min(valid_values, key=lambda v: abs(v[1] - h_pos))
                            val = best_val[0]
                            if len(val) > 1 and val.upper() not in [l.upper() for l in labels]: return "TABLE MATCH: " + val
                        break
            else:
                after_label = line[idx + len(label):]
                m_same = re.match(r"^[ \t]{2,}(.+)", after_label)
                if m_same: return "SAME LINE MATCH: " + m_same.group(1).strip()
                    
                if next_line: return "NEXT LINE MATCH: " + next_line.strip()

    return default

sample_text = """
1. PERSONAL DETAILS
Full Name                                          Date of Birth                Nationality
                                                   18/02/1978                   Egyptian
Marital Status                                     Height (cm)                  Weight (kg)                 Place of Birth
"""
print("Full Name:", repr(_field(sample_text, "Full Name")))
print("Date of Birth:", repr(_field(sample_text, "Date of Birth")))
