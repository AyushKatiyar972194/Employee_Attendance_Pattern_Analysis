import os
import shutil
import zipfile
import win32com.client

ppt_path = os.path.abspath('EAPA-01_Presentation.pptx')
doc_path = os.path.abspath('HCL_Docs/EAPA-01_Project_Document.docx')
out_dir = os.path.abspath('LMS_Submission_Package')
renders_dir = os.path.abspath('SS/slide_renders')
os.makedirs(out_dir, exist_ok=True)
os.makedirs(renders_dir, exist_ok=True)

# 1. Copy PPTX to LMS package
lms_pptx = os.path.join(out_dir, '2_Project_Presentation.pptx')
shutil.copy2(ppt_path, lms_pptx)
print(f"Copied PPTX -> {lms_pptx}")

# 2. PowerPoint COM: Export slides to PNG and Presentation to PDF
try:
    ppt_app = win32com.client.Dispatch('PowerPoint.Application')
    pres = ppt_app.Presentations.Open(ppt_path, WithWindow=False)
    
    # Export slide PNGs
    for i, slide in enumerate(pres.Slides, 1):
        png_path = os.path.join(renders_dir, f'slide_{i:02d}.png')
        slide.Export(png_path, 'PNG', 1920, 1080)
    print(f"Exported all {len(pres.Slides)} slides to PNG in {renders_dir}")
    
    # Export PDF
    lms_pdf = os.path.join(out_dir, '2_Project_Presentation.pdf')
    pres.SaveAs(lms_pdf, 32) # 32 = ppSaveAsPDF
    pres.Close()
    ppt_app.Quit()
    print(f"Exported PPTX to PDF -> {lms_pdf}")
except Exception as e:
    print(f"PowerPoint COM error: {e}")

# 3. Word COM: Export EAPA-01_Project_Document.docx to 1_Project_Document.pdf
try:
    word_app = win32com.client.Dispatch('Word.Application')
    word_app.Visible = False
    doc = word_app.Documents.Open(doc_path)
    lms_doc_pdf = os.path.join(out_dir, '1_Project_Document.pdf')
    doc.SaveAs(lms_doc_pdf, FileFormat=17) # 17 = wdFormatPDF
    doc.Close()
    word_app.Quit()
    print(f"Exported DOCX to PDF -> {lms_doc_pdf}")
except Exception as e:
    print(f"Word COM error: {e}")

# 4. Rebuild LMS ZIP archive
zip_path = os.path.join(out_dir, '6_Employee_Attendance_Pattern_Analysis_EAPA-01.zip')
if os.path.exists(zip_path):
    os.remove(zip_path)

include_dirs = ['pages', 'src', 'tests', 'data', 'docs', 'HCL_Docs', 'scripts', 'SS', '.streamlit']
include_files = [
    'app.py', 'requirements.txt', 'README.md', 'PROJECT_MASTER_DOCUMENTATION.md',
    'INTERVIEW_PREP_GUIDE.md', 'EAPA-01_Presentation.pptx', 'ABES_logo.jpg'
]

exclude_exts = {'.pyc', '.tmp', '.log'}
exclude_dirs = {'.venv', 'venv', '__pycache__', '.pytest_cache', '.git', 'LMS_Submission_Package', '.qodo'}

file_count = 0
total_uncompressed = 0

with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for fname in include_files:
        if os.path.exists(fname):
            zf.write(fname, arcname=fname)
            file_count += 1
            total_uncompressed += os.path.getsize(fname)
            
    for dname in include_dirs:
        for root, dirs, files in os.walk(dname):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext in exclude_exts:
                    continue
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, '.')
                zf.write(full_path, arcname=rel_path)
                file_count += 1
                total_uncompressed += os.path.getsize(full_path)

zip_size_mb = os.path.getsize(zip_path) / (1024 * 1024)
print(f"Recreated {zip_path}: {file_count} files, {zip_size_mb:.2f} MB")
print("ALL EXPORTS COMPLETED SUCCESSFULLY!")
