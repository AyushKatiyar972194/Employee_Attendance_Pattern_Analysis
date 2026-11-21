import docx

for f in ['HCL_Docs/EAPA-01_Project_Document.docx', 'HCL_Docs/P070_Project_Document.docx']:
    doc = docx.Document(f)
    for p in doc.paragraphs:
        if "ABES_OND26_MCA 2nd Year_Data Analytics_Batch 01 2nd Year_Data Analytics_Batch 01" in p.text:
            p.text = p.text.replace("ABES_OND26_MCA 2nd Year_Data Analytics_Batch 01 2nd Year_Data Analytics_Batch 01", "ABES_OND26_MCA 2nd Year_Data Analytics_Batch 01")
    for t in doc.tables:
        for r in t.rows:
            for c in r.cells:
                for p in c.paragraphs:
                    if "ABES_OND26_MCA 2nd Year_Data Analytics_Batch 01 2nd Year_Data Analytics_Batch 01" in p.text:
                        p.text = p.text.replace("ABES_OND26_MCA 2nd Year_Data Analytics_Batch 01 2nd Year_Data Analytics_Batch 01", "ABES_OND26_MCA 2nd Year_Data Analytics_Batch 01")
    doc.save(f)
    print(f"Cleaned batch name in {f}")
