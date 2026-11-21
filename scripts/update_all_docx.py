import os
import docx

def update_docx_file(file_path):
    doc = docx.Document(file_path)
    updated = False
    
    def replace_in_text(text):
        nonlocal updated
        orig = text
        text = text.replace("Alpna Lodhi", "Dinesh Sereno")
        text = text.replace("alpna lodhi", "Dinesh Sereno")
        text = text.replace("ALPNA LODHI", "DINESH SERENO")
        text = text.replace("Alpna", "Dinesh Sereno")
        text = text.replace("EAPA-01", "P070")
        text = text.replace("EAPA_01", "P070")
        text = text.replace("MCA 2nd Year Data Analyst - ABES_OND26_MCA Batch [To confirm]", "ABES_OND26_MCA 2nd Year_Data Analytics_Batch 01")
        text = text.replace("ABES_OND26_MCA; batch number [To confirm]", "ABES_OND26_MCA 2nd Year_Data Analytics_Batch 01")
        text = text.replace("Batch number for ABES_OND26_MCA.", "Batch: ABES_OND26_MCA 2nd Year_Data Analytics_Batch 01")
        text = text.replace("ABES_OND26_MCA Batch [To confirm]", "ABES_OND26_MCA 2nd Year_Data Analytics_Batch 01")
        text = text.replace("ABES_OND26_MCA", "ABES_OND26_MCA 2nd Year_Data Analytics_Batch 01")
        if text != orig:
            updated = True
        return text

    for p in doc.paragraphs:
        if any(k in p.text for k in ["Alpna", "Lodhi", "EAPA-01", "EAPA_01", "ABES_OND26", "[To confirm]"]):
            p.text = replace_in_text(p.text)
            
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    if any(k in p.text for k in ["Alpna", "Lodhi", "EAPA-01", "EAPA_01", "ABES_OND26", "[To confirm]"]):
                        p.text = replace_in_text(p.text)
                        
    if updated:
        doc.save(file_path)
        print(f"Updated: {file_path}")
    else:
        print(f"No changes: {file_path}")

target_folders = ['HCL_Docs', 'docs']
for folder in target_folders:
    if os.path.exists(folder):
        for f in os.listdir(folder):
            if f.endswith('.docx') and not f.startswith('~$'):
                p = os.path.join(folder, f)
                update_docx_file(p)
