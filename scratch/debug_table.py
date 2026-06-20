import docx

doc = docx.Document('all_json_files_processed/AB ESLAM ASHOUR SEDKY ELALAMY.docx')
for i, table in enumerate(doc.tables):
    text_content = " ".join([c.text.strip() for r in table.rows for c in r.cells])
    if "CONTACT DETAILS" in text_content:
        print(f"--- Table {i} ---")
        for r_idx, row in enumerate(table.rows):
            cells = []
            for c in row.cells:
                text = c.text.strip().replace('\n', ' ')
                if not cells or cells[-1] != text:
                    cells.append(text)
            print(f"Row {r_idx}: {cells}")
