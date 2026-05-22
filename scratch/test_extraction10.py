import re

def _field(text: str, *labels: str, default: str = "") -> str:
    for label in labels:
        esc = re.escape(label)
        
        # 1. Colon/Dash
        m = re.search(rf"(?<!\w){esc}\s*[:\-]\s*(.+)", text, re.IGNORECASE)
        if m: return "MATCH 1"

        # 2. Table Header Match (Same Line or Next Line)
        for line_match in re.finditer(rf"^(.*?{esc}.*)$", text, re.MULTILINE | re.IGNORECASE):
            line = line_match.group(1)
            idx = line.lower().find(label.lower())
            
            after_line_text = text[line_match.end():]
            m_next = re.match(r"[ \t]*\n([^\n]+)", after_line_text)
            
            # SPLIT BY LARGE SPACES OR PIPE SYMBOL (|)
            headers = [(m.group(), m.start()) for m in re.finditer(r"([^|\s]+(?: [^|\s]+)*)", line)]
            next_line = m_next.group(1) if m_next else ""
            values = [(m.group(), m.start()) for m in re.finditer(r"([^|\s]+(?: [^|\s]+)*)", next_line)]
            
            is_table = len(headers) > 1 and len(values) >= 1
            
            if is_table:
                for i, (h_text, h_pos) in enumerate(headers):
                    if label.lower() in h_text.lower():
                        # If pipe delimited, we can just use the index directly!
                        if "|" in line and "|" in next_line:
                            pipe_headers = [h.strip() for h in line.split("|")]
                            pipe_values = [v.strip() for v in next_line.split("|")]
                            col_idx = -1
                            for c_i, ph in enumerate(pipe_headers):
                                if label.lower() in ph.lower():
                                    col_idx = c_i
                                    break
                            if col_idx != -1 and col_idx < len(pipe_values):
                                val = pipe_values[col_idx]
                                if len(val) > 1 and val.upper() not in [l.upper() for l in labels]: return "PIPE MATCH: " + val
                        
                        # Otherwise use visual spacing threshold
                        valid_values = [v for v in values if abs(v[1] - h_pos) <= 20]
                        if valid_values:
                            best_val = min(valid_values, key=lambda v: abs(v[1] - h_pos))
                            val = best_val[0]
                            if len(val) > 1 and val.upper() not in [l.upper() for l in labels]: return "SPATIAL MATCH: " + val
                        break

    return default

sample_text = """
Full Name | Date of Birth | Nationality
MOSAAD HELMY IBRAHIM ELAFANY HELMY IBRAHIM | 18/02/1978 | Egyptian
"""
print("Full Name:", repr(_field(sample_text, "Full Name")))
print("Date of Birth:", repr(_field(sample_text, "Date of Birth")))
print("Nationality:", repr(_field(sample_text, "Nationality")))
