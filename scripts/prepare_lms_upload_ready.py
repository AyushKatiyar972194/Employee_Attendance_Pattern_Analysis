import os
import shutil
import win32com.client

root = os.path.abspath('.')
hcl_dir = os.path.join(root, 'HCL_Docs')
data_dir = os.path.join(root, 'data')
lms_src_dir = os.path.join(root, 'LMS_Submission_Package')
step_docs_dir = os.path.join(lms_src_dir, '5_Project_Step_Documents_Individual')

target_dir = os.path.join(root, 'LMS_Upload_Ready_Package')
os.makedirs(target_dir, exist_ok=True)

prefix = '2500320140036_AyushKatiyar_'

# 1. Convert validation_report.xlsx to PDF for Step 10
val_xlsx = os.path.join(data_dir, 'validation_report.xlsx')
val_pdf = os.path.join(step_docs_dir, 'Step_10_Data_Validation_Report.pdf')

excel_app = win32com.client.Dispatch('Excel.Application')
excel_app.Visible = False
try:
    wb = excel_app.Workbooks.Open(val_xlsx)
    wb.ExportAsFixedFormat(0, val_pdf) # 0 = xlTypePDF
    wb.Close(False)
    print("Converted validation_report.xlsx -> Step_10_Data_Validation_Report.pdf")
except Exception as e:
    print(f"Error converting validation_report: {e}")
finally:
    excel_app.Quit()

# Mapping of file item name to source path
files_to_copy = [
    # Item 1: Project Report
    (f"{prefix}Project_Report.pdf", os.path.join(lms_src_dir, '1_Project_Document.pdf')),
    # Item 2: Presentation
    (f"{prefix}Presentation.pdf", os.path.join(lms_src_dir, '2_Project_Presentation.pdf')),
    # Item 3: GitHub and Streamlit Details
    (f"{prefix}GitHub_and_Streamlit_Details.pdf", os.path.join(lms_src_dir, '3_GitHub_Repository_Report.pdf')),
    # Item 4: Complete Source Code
    (f"{prefix}Source_Code.pdf", os.path.join(lms_src_dir, '4_Complete_Source_Code.pdf')),
    # Item 5: Database Schema (XLSX)
    (f"{prefix}Database_Schema.xlsx", os.path.join(hcl_dir, '08_Database_Design.xlsx')),
    # Item 6: Project Database (XLSX)
    (f"{prefix}Project_Database.xlsx", os.path.join(data_dir, 'employee_attendance_pattern_analysis_data.xlsx')),
    # Item 7: 01 Project Understanding
    (f"{prefix}01_Project_Understanding.pdf", os.path.join(step_docs_dir, 'Step_01_Problem_Understanding.pdf')),
    # Item 8: 02 HMW
    (f"{prefix}02_HMW.pdf", os.path.join(step_docs_dir, 'Step_02_HMW_Statements.pdf')),
    # Item 9: 03 Needs Analysis
    (f"{prefix}03_Needs_Analysis.pdf", os.path.join(step_docs_dir, 'Step_03_Needs_Analysis.pdf')),
    # Item 10: 04 Traceability Matrix (XLSX)
    (f"{prefix}04_Traceability_Matrix.xlsx", os.path.join(hcl_dir, '04_Ayush_Employee_Attendance_Traceability_Matrix.xlsx')),
    # Item 11: 05 BRD
    (f"{prefix}05_BRD.pdf", os.path.join(step_docs_dir, 'Step_05_BRD.pdf')),
    # Item 12: 07 TRD
    (f"{prefix}07_TRD.pdf", os.path.join(step_docs_dir, 'Step_07_TRD.pdf')),
    # Item 13: 08 Database Design (XLSX)
    (f"{prefix}08_Database_Design.xlsx", os.path.join(hcl_dir, '08_Database_Design.xlsx')),
    # Item 14: 09 ER Diagram
    (f"{prefix}09_ER_Diagram.pdf", os.path.join(step_docs_dir, 'Step_09_ER_Diagram.pdf')),
    # Item 15: 10 Data Validation Report
    (f"{prefix}10_Data_Validation_Report.pdf", val_pdf),
    # Item 16: 11 User Stories
    (f"{prefix}11_User_Stories.pdf", os.path.join(step_docs_dir, 'Step_11_User_Stories.pdf')),
    # Item 17: 12 UI Framework
    (f"{prefix}12_UI_Framework.pdf", os.path.join(step_docs_dir, 'Step_12_UI_Framework.pdf')),
    # Item 18: 13 Test Cases
    (f"{prefix}13_Test_Cases.pdf", os.path.join(step_docs_dir, 'Step_13_Test_Cases.pdf')),
    # Item 19: Project ZIP file
    (f"{prefix}Employee_Attendance_Pattern_Analysis.zip", os.path.join(lms_src_dir, '6_Employee_Attendance_Pattern_Analysis_P070.zip')),
]

copied_count = 0
total_bytes = 0

print("\n--- Preparing LMS Upload-Ready Files ---")
for target_name, src_path in files_to_copy:
    if os.path.exists(src_path):
        target_path = os.path.join(target_dir, target_name)
        shutil.copy2(src_path, target_path)
        sz_kb = os.path.getsize(target_path) / 1024
        total_bytes += os.path.getsize(target_path)
        copied_count += 1
        print(f"[{copied_count:02d}] Copied: {target_name} ({sz_kb:,.1f} KB)")
    else:
        print(f"[MISSING] {src_path}")

total_mb = total_bytes / (1024 * 1024)
print(f"\n==========================================")
print(f"Total Prepared Files: {copied_count} (Limit: max 20 files)")
print(f"Total Submission Size: {total_mb:.2f} MB (Limit: max 100 MB)")
print(f"Target Directory: {target_dir}")
print(f"==========================================")
