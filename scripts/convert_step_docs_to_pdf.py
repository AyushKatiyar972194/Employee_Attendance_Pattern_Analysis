"""Convert all step documents from Step 1 through the final step to PDF.

Handles:
- Word (.docx) files using Word COM
- Excel (.xlsx) files using Excel COM
- Markdown (.md) files using ReportLab
- Merges all converted step PDFs into 5_All_Project_Step_Documents_Compiled.pdf
"""
import os
import sys
import win32com.client
from pathlib import Path
from pypdf import PdfWriter, PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable


def convert_docx_to_pdf(word_app, docx_path, pdf_path):
    abs_docx = os.path.abspath(docx_path)
    abs_pdf = os.path.abspath(pdf_path)
    try:
        doc = word_app.Documents.Open(abs_docx)
        doc.SaveAs(abs_pdf, FileFormat=17) # 17 = wdFormatPDF
        doc.Close()
        print(f"  [DOCX -> PDF] {os.path.basename(docx_path)} -> {os.path.basename(pdf_path)}")
        return True
    except Exception as e:
        print(f"  [DOCX Error] {docx_path}: {e}")
        return False


def convert_xlsx_to_pdf(excel_app, xlsx_path, pdf_path):
    abs_xlsx = os.path.abspath(xlsx_path)
    abs_pdf = os.path.abspath(pdf_path)
    try:
        wb = excel_app.Workbooks.Open(abs_xlsx)
        wb.ExportAsFixedFormat(0, abs_pdf) # 0 = xlTypePDF
        wb.Close(False)
        print(f"  [XLSX -> PDF] {os.path.basename(xlsx_path)} -> {os.path.basename(pdf_path)}")
        return True
    except Exception as e:
        print(f"  [XLSX Error] {xlsx_path}: {e}")
        return False


def convert_markdown_to_pdf(md_path, pdf_path, doc_title):
    abs_md = os.path.abspath(md_path)
    abs_pdf = os.path.abspath(pdf_path)
    if not os.path.exists(abs_md):
        return False

    with open(abs_md, "r", encoding="utf-8", errors="ignore") as f:
        md_text = f.read()

    doc = SimpleDocTemplate(abs_pdf, pagesize=letter, leftMargin=54, rightMargin=54, topMargin=54, bottomMargin=54)
    styles = getSampleStyleSheet()

    h1 = ParagraphStyle("H1", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=colors.HexColor("#0F172A"), spaceAfter=8)
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=13, leading=16, textColor=colors.HexColor("#1E3A8A"), spaceBefore=10, spaceAfter=6)
    body = ParagraphStyle("Body", parent=styles["Normal"], fontName="Helvetica", fontSize=9, leading=13, textColor=colors.HexColor("#334155"), spaceAfter=5)
    code = ParagraphStyle("Code", parent=styles["Normal"], fontName="Courier", fontSize=7.5, leading=10, textColor=colors.HexColor("#0F172A"))

    story = [
        Paragraph(doc_title, h1),
        Paragraph("HCLTech Career Shaper / Northstar Technologies · Capstone Project P070", styles["Italic"]),
        HRFlowable(width="100%", thickness=1, color=colors.HexColor("#2563EB"), spaceBefore=4, spaceAfter=10),
    ]

    for line in md_text.splitlines():
        line_s = line.strip()
        if not line_s:
            story.append(Spacer(1, 4))
        elif line_s.startswith("# "):
            story.append(Paragraph(line_s[2:], h1))
        elif line_s.startswith("## "):
            story.append(Paragraph(line_s[3:], h2))
        elif line_s.startswith("### "):
            story.append(Paragraph(line_s[4:], ParagraphStyle("H3", parent=h2, fontSize=11, leading=14)))
        elif line_s.startswith("- ") or line_s.startswith("* "):
            clean_item = line_s[2:].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(f"• {clean_item}", body))
        elif line_s.startswith("```"):
            continue
        elif line_s.startswith("|"):
            # Render table rows simply
            cells = [c.strip() for c in line_s.split("|")[1:-1]]
            if cells and not all(c.startswith("-") for c in cells):
                story.append(Paragraph(" | ".join(cells), code))
        else:
            clean_text = line_s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(clean_text, body))

    try:
        doc.build(story)
        print(f"  [MD -> PDF] {os.path.basename(md_path)} -> {os.path.basename(pdf_path)}")
        return True
    except Exception as e:
        print(f"  [MD Error] {md_path}: {e}")
        return False


def main():
    root = os.path.abspath(".")
    hcl_dir = os.path.join(root, "HCL_Docs")
    docs_dir = os.path.join(root, "docs")
    out_dir = os.path.join(root, "LMS_Submission_Package", "5_Project_Step_Documents_Individual")
    compiled_pdf = os.path.join(root, "LMS_Submission_Package", "5_All_Project_Step_Documents_Compiled.pdf")
    os.makedirs(out_dir, exist_ok=True)

    print("Initializing Office COM applications...")
    word_app = win32com.client.Dispatch("Word.Application")
    word_app.Visible = False
    excel_app = win32com.client.Dispatch("Excel.Application")
    excel_app.Visible = False

    step_files = [
        ("Step_01_Problem_Understanding.pdf", os.path.join(hcl_dir, "01_Ayush_Employee_Attendance_Pattern_Understanding.docx"), "docx"),
        ("Step_02_HMW_Statements.pdf", os.path.join(hcl_dir, "02_Ayush_Employee_Attendance_HMW_Statements.docx"), "docx"),
        ("Step_03_Needs_Analysis.pdf", os.path.join(hcl_dir, "03_Ayush_Employee_Attendance_Needs_Analysis.docx"), "docx"),
        ("Step_04_Traceability_Matrix.pdf", os.path.join(hcl_dir, "04_Ayush_Employee_Attendance_Traceability_Matrix.xlsx"), "xlsx"),
        ("Step_05_BRD.pdf", os.path.join(hcl_dir, "05_Ayush_Employee_Attendance_BRD.docx"), "docx"),
        ("Step_07_TRD.pdf", os.path.join(hcl_dir, "07_Ayush_Employee_Attendance_TRD.docx"), "docx"),
        ("Step_08_Database_Design.pdf", os.path.join(hcl_dir, "08_Database_Design.xlsx"), "xlsx"),
        ("Step_09_ER_Diagram.pdf", os.path.join(hcl_dir, "09_ER_Diagram.docx"), "docx"),
        ("Step_11_User_Stories.pdf", os.path.join(hcl_dir, "11_User_Stories.docx"), "docx"),
        ("Step_12_UI_Framework.pdf", os.path.join(hcl_dir, "12_UI_Framework.docx"), "docx"),
        ("Step_13_Test_Cases.pdf", os.path.join(hcl_dir, "13_Test_Cases.docx"), "docx"),
        ("Step_14_Build_Plan.pdf", os.path.join(hcl_dir, "14_BUILD_PLAN.docx"), "docx"),
        ("Step_15_EDA_Enterprise_Analysis.pdf", os.path.join(docs_dir, "EDA_ENTERPRISE_ANALYSIS_REPORT.md"), "md_eda"),
        ("Step_16_Project_Master_Documentation.pdf", os.path.join(root, "PROJECT_MASTER_DOCUMENTATION.md"), "md_master"),
    ]

    generated_pdfs = []

    try:
        for out_name, src_path, ftype in step_files:
            target_pdf = os.path.join(out_dir, out_name)
            if not os.path.exists(src_path):
                print(f"  [WARN] Source file missing: {src_path}")
                continue

            if ftype == "docx":
                ok = convert_docx_to_pdf(word_app, src_path, target_pdf)
            elif ftype == "xlsx":
                ok = convert_xlsx_to_pdf(excel_app, src_path, target_pdf)
            elif ftype == "md_eda":
                ok = convert_markdown_to_pdf(src_path, target_pdf, "Step 15: EDA Enterprise Analysis & Forensic Report")
            elif ftype == "md_master":
                ok = convert_markdown_to_pdf(src_path, target_pdf, "Step 16: Project Master Documentation (Full Architecture)")
            else:
                ok = False

            if ok and os.path.exists(target_pdf):
                generated_pdfs.append(target_pdf)
    finally:
        try:
            word_app.Quit()
        except Exception:
            pass
        try:
            excel_app.Quit()
        except Exception:
            pass

    print(f"\nSuccessfully generated {len(generated_pdfs)} individual step PDFs.")

    # Merge into 5_All_Project_Step_Documents_Compiled.pdf
    print("Compiling all step PDFs into a single master PDF...")
    merger = PdfWriter()
    for pdf_path in generated_pdfs:
        try:
            reader = PdfReader(pdf_path)
            for page in reader.pages:
                merger.add_page(page)
        except Exception as e:
            print(f"  [Merge Error] {pdf_path}: {e}")

    with open(compiled_pdf, "wb") as f_out:
        merger.write(f_out)
    print("Compiled Master Step PDF built at:", compiled_pdf)


if __name__ == "__main__":
    main()
