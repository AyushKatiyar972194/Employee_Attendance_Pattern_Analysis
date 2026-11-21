import openpyxl

files = [
    'HCL_Docs/04_Ayush_Employee_Attendance_Traceability_Matrix.xlsx',
    'HCL_Docs/08_Database_Design.xlsx',
    'data/employee_attendance_pattern_analysis_data.xlsx',
    'data/validation_report.xlsx'
]

for f in files:
    wb = openpyxl.load_workbook(f)
    print(f"\n=== {f} ===")
    for sname in wb.sheetnames:
        sheet = wb[sname]
        for row in sheet.iter_rows(values_only=True):
            for cell in row:
                if cell and isinstance(cell, str):
                    low = cell.lower()
                    if any(k in low for k in ['alpna', 'lodhi', 'eapa', 'mentor', 'batch', 'dinesh', 'p070']):
                        print(f"  [{sname}] {cell.strip()[:80]}")
