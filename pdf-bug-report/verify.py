import fitz
import os
import sys
sys.stdout.reconfigure(encoding="utf-8")

pdf = r"E:\2-TECHNO AQUARE\sakr-no-post-error.pdf"
doc = fitz.open(pdf)
print("=== PDF SUMMARY ===")
print(f"Pages       : {doc.page_count}")
print(f"Page size   : {doc[0].rect}")
print(f"Title       : {doc.metadata.get('title')}")
print(f"Author      : {doc.metadata.get('author')}")
print(f"Subject     : {doc.metadata.get('subject')}")
print(f"Images      : {sum(len(p.get_images(full=True)) for p in doc)}")
print(f"Link annots : {sum(len(p.get_links()) for p in doc)}")
print(f"File size   : {os.path.getsize(pdf):,} bytes")
