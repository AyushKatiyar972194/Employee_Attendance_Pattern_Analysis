import openpyxl

wb = openpyxl.load_workbook('HCL_Docs/04_Ayush_Employee_Attendance_Traceability_Matrix.xlsx')
ws = wb['Read Me']
for r in range(1, ws.max_row + 1):
    for c in range(1, ws.max_column + 1):
        v = ws.cell(row=r, column=c).value
        if v and isinstance(v, str):
            if "Alpna Lodhi" in v:
                print(f"Row {r} Col {c}: {v}")
                ws.cell(row=r, column=c).value = v.replace("Alpna Lodhi", "Dinesh Sereno")
            if "EAPA-01" in v:
                print(f"Row {r} Col {c}: {v}")
                ws.cell(row=r, column=c).value = v.replace("EAPA-01", "P070")

wb.save('HCL_Docs/04_Ayush_Employee_Attendance_Traceability_Matrix.xlsx')
print("Updated Traceability Matrix Read Me sheet.")
