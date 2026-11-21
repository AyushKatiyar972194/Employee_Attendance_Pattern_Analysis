import docx

files = [
    'HCL_Docs/01_Ayush_Employee_Attendance_Pattern_Understanding.docx',
    'HCL_Docs/02_Ayush_Employee_Attendance_HMW_Statements.docx',
    'HCL_Docs/03_Ayush_Employee_Attendance_Needs_Analysis.docx',
    'HCL_Docs/05_Ayush_Employee_Attendance_BRD.docx',
    'HCL_Docs/07_Ayush_Employee_Attendance_TRD.docx',
]

for f in files:
    doc = docx.Document(f)
    print(f"\n=== {f} Table 0 ===")
    t = doc.tables[0]
    for r_idx, row in enumerate(t.rows):
        cells = [c.text.strip().replace('\n', ' ') for c in row.cells]
        print(f"  Row {r_idx}: {cells}")
