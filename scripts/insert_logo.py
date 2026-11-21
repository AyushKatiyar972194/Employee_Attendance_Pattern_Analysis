import os
import docx
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

# 1. Update Word Document
doc_path = os.path.abspath('HCL_Docs/EAPA-01_Project_Document.docx')
logo_path = os.path.abspath('HCL_Docs/ABES_logo.jpg')

if os.path.exists(doc_path) and os.path.exists(logo_path):
    doc = docx.Document(doc_path)
    updated = False
    for i, p in enumerate(doc.paragraphs):
        if '[insert abes logo here]' in p.text.lower() or '[insert abes logo]' in p.text.lower():
            print(f"Found placeholder in paragraph {i}: '{p.text}'")
            p.text = ""  # Clear the text
            run = p.add_run()
            run.add_picture(logo_path, width=Inches(1.8))
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            updated = True
            print("Successfully inserted ABES logo into EAPA-01_Project_Document.docx!")
            break
            
    if updated:
        doc.save(doc_path)
        print("Saved updated EAPA-01_Project_Document.docx")
    else:
        print("Placeholder not found in EAPA-01_Project_Document.docx")
else:
    print(f"Doc or logo not found: doc={os.path.exists(doc_path)}, logo={os.path.exists(logo_path)}")
