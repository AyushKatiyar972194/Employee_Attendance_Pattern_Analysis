"""Build the complete, polished, and professional EAPA-01 presentation."""
import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def build_presentation():
    prs = pptx.Presentation('EAPA-01_Presentation_original.pptx')
    blank_layout = prs.slide_layouts[6]

    # Theme colors
    NAVY = RGBColor(15, 23, 42)
    CRIMSON = RGBColor(165, 28, 48)
    BLUE_ACCENT = RGBColor(37, 99, 235)
    LIGHT_BLUE = RGBColor(96, 165, 250)
    TEXT_DARK = RGBColor(21, 21, 20)
    TEXT_BODY = RGBColor(58, 58, 56)
    TEXT_MUTED = RGBColor(94, 94, 91)
    CARD_BG = RGBColor(244, 241, 241)
    CARD_BORDER = RGBColor(226, 232, 240)
    WHITE = RGBColor(255, 255, 255)
    GREEN = RGBColor(16, 185, 129)
    AMBER = RGBColor(245, 158, 11)

    def add_header_footer(slide, title_text, slide_num):
        tx_title = slide.shapes.add_textbox(Inches(0.50), Inches(0.28), Inches(9.00), Inches(0.70))
        tf = tx_title.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.name = 'Calibri'
        p.font.size = Pt(21)
        p.font.bold = True
        p.font.color.rgb = TEXT_DARK
        
        tx_ftr = slide.shapes.add_textbox(Inches(0.50), Inches(5.20), Inches(7.50), Inches(0.30))
        tf_f = tx_ftr.text_frame
        p_f = tf_f.paragraphs[0]
        p_f.text = "HCLTech Career Shaper ABES Engineering College | EAPA-01 - Employee Attendance Pattern Analysis"
        p_f.font.name = 'Calibri'
        p_f.font.size = Pt(9)
        p_f.font.color.rgb = TEXT_MUTED

        tx_num = slide.shapes.add_textbox(Inches(9.00), Inches(5.20), Inches(0.50), Inches(0.30))
        tf_n = tx_num.text_frame
        p_n = tf_n.paragraphs[0]
        p_n.text = str(slide_num)
        p_n.alignment = PP_ALIGN.RIGHT
        p_n.font.name = 'Calibri'
        p_n.font.size = Pt(9)
        p_n.font.color.rgb = TEXT_MUTED

    def add_card(slide, left, top, width, height, title, lines, badge_text=None, badge_color=CRIMSON):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = CARD_BG
        shape.line.color.rgb = CARD_BORDER
        shape.line.width = Pt(1)

        content_top = top + Inches(0.10)
        text_left = left + Inches(0.14)
        text_width = width - Inches(0.28)
        
        if badge_text:
            badge = slide.shapes.add_shape(MSO_SHAPE.OVAL, left + Inches(0.14), content_top, Inches(0.26), Inches(0.26))
            badge.fill.solid()
            badge.fill.fore_color.rgb = badge_color
            badge.line.fill.background()
            tf_badge = badge.text_frame
            tf_badge.margin_left = Inches(0)
            tf_badge.margin_right = Inches(0)
            tf_badge.margin_top = Inches(0)
            tf_badge.margin_bottom = Inches(0)
            tf_badge.word_wrap = False
            p_b = tf_badge.paragraphs[0]
            p_b.text = badge_text
            p_b.font.name = 'Calibri'
            p_b.font.size = Pt(8.5)
            p_b.font.bold = True
            p_b.font.color.rgb = WHITE
            p_b.alignment = PP_ALIGN.CENTER
            
            tx = slide.shapes.add_textbox(left + Inches(0.46), content_top - Inches(0.04), width - Inches(0.52), Inches(0.32))
            tf = tx.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = title
            p.font.name = 'Calibri'
            p.font.size = Pt(11)
            p.font.bold = True
            p.font.color.rgb = TEXT_DARK
            content_top += Inches(0.28)
        else:
            tx = slide.shapes.add_textbox(text_left, content_top, text_width, Inches(0.32))
            tf = tx.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = title
            p.font.name = 'Calibri'
            p.font.size = Pt(11)
            p.font.bold = True
            p.font.color.rgb = TEXT_DARK
            content_top += Inches(0.28)

        body_height = height - (content_top - top) - Inches(0.08)
        tx_b = slide.shapes.add_textbox(text_left, content_top, text_width, body_height)
        tf_b = tx_b.text_frame
        tf_b.word_wrap = True
        
        for i, line in enumerate(lines):
            p = tf_b.paragraphs[0] if i == 0 else tf_b.add_paragraph()
            p.text = line
            p.font.name = 'Calibri'
            p.font.size = Pt(9)
            p.font.color.rgb = TEXT_BODY
            p.space_after = Pt(1.5)

    def add_image_with_frame(slide, img_path, left, top, width, height):
        pic = slide.shapes.add_picture(img_path, left, top, width, height)
        pic.line.color.rgb = CARD_BORDER
        pic.line.width = Pt(1)
        return pic

    # -------------------------------------------------------------
    # 1. Slide 1 (Title Slide): Embed ABES Logo & Author Details
    # -------------------------------------------------------------
    slide1 = prs.slides[0]
    for shape in slide1.shapes:
        if shape.name == 'TextBox 1':
            shape.text_frame.text = ""
        elif shape.name == 'TextBox 4':
            shape.text_frame.text = (
                "Ayush Katiyar | University Roll No: 2500320140036\n"
                "Batch ID: ABES_OND26_MCA 2nd Year_Data Analytics_Batch 01\n"
                "Project ID: P070 | Project Mentor: Dinesh Sereno\n"
                "Live App: https://employeeattendancepatternanalysis-xweeu4ylh8pneqxoxkikwk.streamlit.app/\n"
                "GitHub: https://github.com/AyushKatiyar972194/Employee_Attendance_Pattern_Analysis"
            )
            for p in shape.text_frame.paragraphs:
                p.font.name = 'Calibri'
                p.font.size = Pt(11)
                p.font.color.rgb = RGBColor(0xEA, 0xEB, 0xEE)
    logo_path = 'ABES_logo.jpg' if os.path.exists('ABES_logo.jpg') else os.path.join('HCL_Docs', 'ABES_logo.jpg')
    if os.path.exists(logo_path):
        slide1.shapes.add_picture(logo_path, Inches(0.50), Inches(0.30), width=Inches(1.50))

    # -------------------------------------------------------------
    # 1b. Slide 4: Fix Table 4 and Footnote to eliminate overlap
    # -------------------------------------------------------------
    slide4 = prs.slides[3]
    for s in slide4.shapes:
        if s.has_table:
            for r in s.table.rows:
                r.height = Inches(0.55)
            s.top = Inches(1.25)
            s.height = Inches(2.75)
        elif s.name == 'TextBox 5':
            s.top = Inches(4.50)

    # -------------------------------------------------------------
    # 1c. Slide 5: Update Data & Preparation metrics to 2,400 Enterprise Dataset
    # -------------------------------------------------------------
    slide5 = prs.slides[4]
    for s in slide5.shapes:
        if s.name == 'TextBox 4':
            s.text_frame.text = "2,400"
            p = s.text_frame.paragraphs[0]
            p.font.name = 'Cambria'
            p.font.size = Pt(28)
            p.font.bold = True
            p.font.color.rgb = CRIMSON
        elif s.name == 'TextBox 5':
            s.text_frame.text = "attendance rows"
        elif s.name == 'TextBox 6':
            s.text_frame.text = "34"
        elif s.name == 'TextBox 7':
            s.text_frame.text = "view features"
        elif s.name == 'TextBox 8':
            s.text_frame.text = "120"
            p = s.text_frame.paragraphs[0]
            p.font.name = 'Cambria'
            p.font.size = Pt(28)
            p.font.bold = True
            p.font.color.rgb = CRIMSON
        elif s.name == 'TextBox 9':
            s.text_frame.text = "employees (8 depts)"
        elif s.name == 'TextBox 10':
            s.text_frame.text = "14"
            p = s.text_frame.paragraphs[0]
            p.font.name = 'Cambria'
            p.font.size = Pt(28)
            p.font.bold = True
            p.font.color.rgb = CRIMSON
        elif s.name == 'TextBox 11':
            s.text_frame.text = "missing check-outs"
        elif s.name == 'TextBox 14':
            s.text_frame.text = (
                "Canonical enterprise dataset for Northstar Technologies. "
                "2,400 attendance facts across 120 full-time employees and 8 operating departments "
                "over the entire month of October 2026 (22 working days observed)."
            )
            for p in s.text_frame.paragraphs:
                p.font.name = 'Calibri'
                p.font.size = Pt(11)
                p.font.color.rgb = TEXT_BODY
        elif s.name == 'TextBox 17':
            s.text_frame.text = (
                "• 14 missing check-outs isolated as completeness quality warnings without data drop.\n"
                "• 0 duplicate employee-dates (100% uniqueness verified).\n"
                "• 0 foreign-key violations across 3NF relational tables."
            )
            for p in s.text_frame.paragraphs:
                p.font.name = 'Calibri'
                p.font.size = Pt(11)
                p.font.color.rgb = TEXT_BODY

    # -------------------------------------------------------------
    # 2. Slide 7: Transform in-place into Executive Dashboard (UI-01)
    # -------------------------------------------------------------
    slide7 = prs.slides[6]
    to_remove = [s for s in slide7.shapes if s.name not in ['Title 1', 'TextBox 2', 'TextBox 3']]
    for s in to_remove:
        slide7.shapes._spTree.remove(s._element)
    
    # Update title
    slide7.shapes.title.text = "Executive Dashboard — Strategic Workforce KPIs (UI-01)"
    slide7.shapes.title.text_frame.paragraphs[0].font.name = 'Calibri'
    slide7.shapes.title.text_frame.paragraphs[0].font.size = Pt(21)
    slide7.shapes.title.text_frame.paragraphs[0].font.bold = True
    slide7.shapes.title.text_frame.paragraphs[0].font.color.rgb = TEXT_DARK

    # Add cropped banner image (cleanly non-overlapping with cards below)
    add_image_with_frame(slide7, 'SS/slides_crops/ov_banner_kpis.png', Inches(0.50), Inches(1.10), Inches(9.00), Inches(1.69))

    # Add 4 KPI highlight cards underneath
    w_card = Inches(2.13)
    gap = Inches(0.16)
    add_card(slide7, Inches(0.50) + 0 * (w_card + gap), Inches(3.00), w_card, Inches(1.95),
             "Attendance: 95.92%",
             ["• 2,302 / 2,400 eligible shifts",
              "• 50 approved leaves tracked",
              "• Weighted org-wide formula"],
             badge_text="1", badge_color=BLUE_ACCENT)

    add_card(slide7, Inches(0.50) + 1 * (w_card + gap), Inches(3.00), w_card, Inches(1.95),
             "Lateness: 16.98%",
             ["• 391 late / 2,302 present arrivals",
              "• 1,911 punctual check-ins",
              "• Strictly >10 min grace period"],
             badge_text="2", badge_color=AMBER)

    add_card(slide7, Inches(0.50) + 2 * (w_card + gap), Inches(3.00), w_card, Inches(1.95),
             "Avg Elapsed: 504.6m",
             ["• Sample size N = 2,288 shifts",
              "• Excludes 14 missing checkouts",
              "• 8.41 average recorded hours"],
             badge_text="3", badge_color=BLUE_ACCENT)

    add_card(slide7, Inches(0.50) + 3 * (w_card + gap), Inches(3.00), w_card, Inches(1.95),
             "Quality Audit: 14 Issues",
             ["• 14 missing checkouts isolated",
              "• Zero silent data drops",
              "• 100% referential integrity"],
             badge_text="4", badge_color=GREEN)

    # -------------------------------------------------------------
    # 3. Append 6 new slides (Slides 8 to 13)
    # -------------------------------------------------------------
    new_ids = []

    # Slide 8: Workforce Dynamics (UI-01)
    s8 = prs.slides.add_slide(blank_layout)
    add_header_footer(s8, "Workforce Dynamics — Daily Trends & Attendance Breakdown (UI-01)", 8)
    add_image_with_frame(s8, 'SS/slides_crops/ov_trends_breakdown.png', Inches(0.50), Inches(1.10), Inches(5.30), Inches(3.90))
    add_card(s8, Inches(6.00), Inches(1.10), Inches(3.50), Inches(1.22),
             "Daily Attendance Volatility",
             ["• 22 working days observed across October 2026",
              "• High volume stability (100 to 110 present daily)",
              "• Stable workforce pattern: 93% to 98% daily fulfillment"],
             badge_text="1", badge_color=CRIMSON)
    add_card(s8, Inches(6.00), Inches(2.44), Inches(3.50), Inches(1.22),
             "Status Distribution (N=2,400)",
             ["• Present: 2,302 records (95.9%)",
              "• Approved Leave: 50 records (2.1%)",
              "• Absent: 48 records (2.0%) across full month"],
             badge_text="2", badge_color=CRIMSON)
    add_card(s8, Inches(6.00), Inches(3.78), Inches(3.50), Inches(1.22),
             "Analytical Takeaway",
             ["• Planned leave matches unapproved absence ~1:1",
              "• No mid-week decay or Monday/Friday absentee spike",
              "• Reliable foundation for operational scheduling"],
             badge_text="3", badge_color=CRIMSON)
    new_ids.append(prs.slides._sldIdLst[-1])

    # Slide 9: Department Benchmarks (UI-03)
    s9 = prs.slides.add_slide(blank_layout)
    add_header_footer(s9, "Department Benchmarks & Baseline Comparisons (UI-03)", 9)
    add_image_with_frame(s9, 'SS/slides_crops/dept_chart_baseline.png', Inches(0.50), Inches(1.10), Inches(5.30), Inches(3.90))
    add_card(s9, Inches(6.00), Inches(1.10), Inches(3.50), Inches(1.22),
             "Top Performers (> 96% Baseline)",
             ["• Finance: 97.3% fulfillment (Grade A+ Benchmark)",
              "• Operations: 97.3% fulfillment (Grade A+ Benchmark)",
              "• Both departments consistently lead the org average"],
             badge_text="A", badge_color=BLUE_ACCENT)
    add_card(s9, Inches(6.00), Inches(2.44), Inches(3.50), Inches(1.22),
             "Mid-Tier Dependables",
             ["• Human Resources: 96.6% attendance",
              "• Quality Assurance: 96.0% attendance",
              "• High predictability with low unapproved absence variation"],
             badge_text="B", badge_color=BLUE_ACCENT)
    add_card(s9, Inches(6.00), Inches(3.78), Inches(3.50), Inches(1.22),
             "Commute Bottleneck: Support",
             ["• Customer Support: 96.2% present, but 23.8% late",
              "• Tight arrival cluster between 09:11 and 09:14 AM",
              "• Noida Metro transit bottleneck, solved by 15m grace"],
             badge_text="C", badge_color=AMBER)
    new_ids.append(prs.slides._sldIdLst[-1])

    # Slide 10: Punctuality & Time Analysis (UI-04)
    s10 = prs.slides.add_slide(blank_layout)
    add_header_footer(s10, "Punctuality & Time Analysis — Grace Period Governance (UI-04)", 10)
    add_image_with_frame(s10, 'SS/slides_crops/time_hist_grace.png', Inches(0.50), Inches(1.10), Inches(5.30), Inches(3.90))
    add_card(s10, Inches(6.00), Inches(1.10), Inches(3.50), Inches(1.22),
             "Punctuality Breakdown",
             ["• 1,911 Punctual check-ins (83.02% of present workforce)",
              "• 391 Late arrivals (16.98% lateness incident rate)",
              "• Total present punch-in records audited: 2,302"],
             badge_text="1", badge_color=CRIMSON)
    add_card(s10, Inches(6.00), Inches(2.44), Inches(3.50), Inches(1.22),
             "10-Minute Grace Boundary Rule",
             ["• Check-in at 09:10:00 is strictly classified as punctual",
              "• Check-in at 09:10:01+ is classified as late arrival",
              "• Consistent boundary applied across all dashboard views"],
             badge_text="2", badge_color=CRIMSON)
    add_card(s10, Inches(6.00), Inches(3.78), Inches(3.50), Inches(1.22),
             "Arrival Delay Distribution",
             ["• Late arrivals cluster tightly between 11 and 20 mins",
              "• Red dashed line indicates the 10-minute policy threshold",
              "• 232 shifts recovered by extending grace to 15 mins"],
             badge_text="3", badge_color=CRIMSON)
    new_ids.append(prs.slides._sldIdLst[-1])

    # Slide 11: Outlier Resolution & Duration (UI-04)
    s11 = prs.slides.add_slide(blank_layout)
    add_header_footer(s11, "Analytical Investigation — Outlier Resolution & Duration (UI-04)", 11)
    add_image_with_frame(s11, 'SS/slides_crops/time_outlier_callout.png', Inches(0.50), Inches(1.10), Inches(5.30), Inches(3.90))
    add_card(s11, Inches(6.00), Inches(1.10), Inches(3.50), Inches(1.22),
             "Duration Distribution",
             ["• Mean shift duration: 504.6 mins (8.41 hours)",
              "• Standard core shifts cluster cleanly at 480-510 mins",
              "• Normal operational distribution across all departments"],
             badge_text="i", badge_color=BLUE_ACCENT)
    add_card(s11, Inches(6.00), Inches(2.44), Inches(3.50), Inches(1.22),
             "Chronic Lateness Forensics",
             ["• EMP0066 identified with 12 late arrival shifts",
              "• EMP0012 & EMP0044 record 8 late shifts each",
              "• Targets individual coaching vs broad policy change"],
             badge_text="i", badge_color=AMBER)
    add_card(s11, Inches(6.00), Inches(3.78), Inches(3.50), Inches(1.22),
             "Duration Measurement Governance",
             ["• Explicitly labelled 'Recorded Elapsed Duration'",
              "• Net working time cannot be claimed (no break tracking)",
              "• Professional BI metric integrity maintained"],
             badge_text="i", badge_color=GREEN)
    new_ids.append(prs.slides._sldIdLst[-1])

    # Slide 12: Data Quality Scorecard (UI-08)
    s12 = prs.slides.add_slide(blank_layout)
    add_header_footer(s12, "Data Quality Framework — Dimensional Audit Scorecard (UI-08)", 12)
    add_image_with_frame(s12, 'SS/slides_crops/dq_scorecard.png', Inches(0.50), Inches(1.10), Inches(5.30), Inches(3.90))
    add_card(s12, Inches(6.00), Inches(1.10), Inches(3.50), Inches(1.22),
             "Completeness & Uniqueness",
             ["• Completeness: ⚠️ Warning — 14 missing checkouts (0.6%)",
              "• Uniqueness: ✅ 100% Passed (0 duplicate employee-dates)",
              "• Primary & composite keys strictly validated"],
             badge_text="1", badge_color=GREEN)
    add_card(s12, Inches(6.00), Inches(2.44), Inches(3.50), Inches(1.22),
             "Validity & Consistency",
             ["• Validity: ✅ 100% Passed (all statuses & formats valid)",
              "• Consistency: ✅ 100% Passed (0 negative durations)",
              "• Zero check-in timestamps attached to absent records"],
             badge_text="2", badge_color=GREEN)
    add_card(s12, Inches(6.00), Inches(3.78), Inches(3.50), Inches(1.22),
             "Referential Integrity & Timeliness",
             ["• Integrity: ✅ 100% Passed (0 foreign key violations)",
              "• Timeliness: ℹ️ Operational refresh tracking active",
              "• SQLite audit log captures all pipeline execution runs"],
             badge_text="3", badge_color=GREEN)
    new_ids.append(prs.slides._sldIdLst[-1])

    # Slide 13: Audit Trail & Pipeline Health (UI-08)
    s13 = prs.slides.add_slide(blank_layout)
    add_header_footer(s13, "Audit Trail & Ingestion Health Monitoring (UI-08)", 13)
    add_image_with_frame(s13, 'SS/slides_crops/dq_pipeline_runs.png', Inches(0.50), Inches(1.10), Inches(5.30), Inches(3.90))
    add_card(s13, Inches(6.00), Inches(1.10), Inches(3.50), Inches(1.22),
             "Record-Level Issue Isolation",
             ["• 14 attendance records flagged with missing clock-outs",
              "• Remediation portal enables 1-click CSV audit ledger export",
              "• Real-time data quality status banner on UI"],
             badge_text="!", badge_color=AMBER)
    add_card(s13, Inches(6.00), Inches(2.44), Inches(3.50), Inches(1.22),
             "Resilient Ingestion Engine",
             ["• Smart alias matching (Date, Clock In/Out, Emp ID)",
              "• Auto-inferred status code & auto-registered employees",
              "• Append and Replace All live database ingestion modes"],
             badge_text="!", badge_color=BLUE_ACCENT)
    add_card(s13, Inches(6.00), Inches(3.78), Inches(3.50), Inches(1.22),
             "Pipeline Execution Logging",
             ["• SQLite table 'pipeline_runs' records every data load",
              "• Logs: Run ID, start/end timestamps, accepted rows (2,400),",
              "  rejected rows (0), and validation warnings (14)"],
             badge_text="!", badge_color=GREEN)
    new_ids.append(prs.slides._sldIdLst[-1])

    # -------------------------------------------------------------
    # 4. Reorder the 6 new slide IDs into position after Slide 7
    # i.e., insert them at indices 7, 8, 9, 10, 11, 12
    # -------------------------------------------------------------
    for sldId in new_ids:
        prs.slides._sldIdLst.remove(sldId)
    for i, sldId in enumerate(new_ids):
        prs.slides._sldIdLst.insert(7 + i, sldId)

    # -------------------------------------------------------------
    # 5. Update Slide 14 (Old Slide 8: Key findings)
    # -------------------------------------------------------------
    slide14 = prs.slides[13]
    for shape in slide14.shapes:
        if shape.name == 'TextBox 3':
            shape.text_frame.text = "14"
        elif shape.name == 'TextBox 5':
            shape.text_frame.text = "2,400"
            p = shape.text_frame.paragraphs[0]
            p.font.name = 'Cambria'
            p.font.size = Pt(36)
            p.font.bold = True
            p.font.color.rgb = CRIMSON
        elif shape.name == 'TextBox 6':
            shape.text_frame.text = "Canonical enterprise attendance facts modeled across 8 departments and 120 employees."
            for p in shape.text_frame.paragraphs:
                p.font.name = 'Calibri'
                p.font.size = Pt(13)
                p.font.bold = True
        elif shape.name == 'TextBox 7':
            shape.text_frame.text = "Evidence: attendance_records table count = 2,400 (October 2026 full month)."
            for p in shape.text_frame.paragraphs:
                p.font.name = 'Calibri'
                p.font.size = Pt(11)
        elif shape.name == 'TextBox 9':
            shape.text_frame.text = "14"
            p = shape.text_frame.paragraphs[0]
            p.font.name = 'Cambria'
            p.font.size = Pt(36)
            p.font.bold = True
            p.font.color.rgb = CRIMSON
        elif shape.name == 'TextBox 10':
            shape.text_frame.text = "Records missing clock-out timestamps isolated from duration averages."
            for p in shape.text_frame.paragraphs:
                p.font.name = 'Calibri'
                p.font.size = Pt(13)
                p.font.bold = True
        elif shape.name == 'TextBox 11':
            shape.text_frame.text = "Evidence: 14 nullable check-out values; valid duration calculated on N = 2,288 shifts."
            for p in shape.text_frame.paragraphs:
                p.font.name = 'Calibri'
                p.font.size = Pt(11)
        elif shape.name == 'TextBox 13':
            shape.text_frame.text = "0"
            p = shape.text_frame.paragraphs[0]
            p.font.name = 'Cambria'
            p.font.size = Pt(36)
            p.font.bold = True
            p.font.color.rgb = CRIMSON
        elif shape.name == 'TextBox 14':
            shape.text_frame.text = "Database referential integrity passed all automated validation checks."
            for p in shape.text_frame.paragraphs:
                p.font.name = 'Calibri'
                p.font.size = Pt(13)
                p.font.bold = True
        elif shape.name == 'TextBox 15':
            shape.text_frame.text = "Evidence: SQLite foreign_key_check returned 0 violations."
            for p in shape.text_frame.paragraphs:
                p.font.name = 'Calibri'
                p.font.size = Pt(11)

    # -------------------------------------------------------------
    # 6. Update Slide 15 (Old Slide 9: Testing and validation)
    # -------------------------------------------------------------
    slide15 = prs.slides[14]
    for shape in slide15.shapes:
        if shape.name == 'TextBox 3':
            shape.text_frame.text = "15"
        elif shape.name == 'TextBox 4':
            shape.text_frame.text = "58 / 58"
            p = shape.text_frame.paragraphs[0]
            p.font.name = 'Calibri'
            p.font.size = Pt(36)
            p.font.bold = True
            p.font.color.rgb = GREEN
        elif shape.name == 'TextBox 5':
            shape.text_frame.text = "Test cases passed (100%)\npytest: 58 passed in ~10.8s\nenterprise verified"
            for p in shape.text_frame.paragraphs:
                p.font.name = 'Calibri'
                p.font.size = Pt(11)
        elif shape.has_table:
            table = shape.table
            table.columns[0].width = Inches(2.10)
            table.columns[1].width = Inches(3.00)
            table.columns[2].width = Inches(1.00)
            rows_data = [
                ("test_analysis.py", "Weighted attendance rate, grace boundary, punctuality rankings", "15 Passed"),
                ("test_data.py", "SQLite 3NF schema, 2,400 facts, uniqueness, foreign keys", "16 Passed"),
                ("test_error_resilience.py", "Zero-crash boundaries, NaN handling, donut charts, param aliases", "10 Passed"),
                ("test_app.py (AppTest)", "Streamlit AppTest all 5 pages & main entry point validation", "7 Passed"),
                ("test_pipeline & predictive", "6-dimension scorecard, ML risk scoring, policy simulation", "10 Passed"),
            ]
            for row_idx, (t_name, t_chk, t_res) in enumerate(rows_data):
                if row_idx + 1 < len(table.rows):
                    table.cell(row_idx + 1, 0).text = t_name
                    table.cell(row_idx + 1, 1).text = t_chk
                    table.cell(row_idx + 1, 2).text = t_res
                    for c in range(3):
                        p = table.cell(row_idx + 1, c).text_frame.paragraphs[0]
                        p.font.name = 'Calibri'
                        p.font.size = Pt(10)
                    p_res = table.cell(row_idx + 1, 2).text_frame.paragraphs[0]
                    p_res.font.bold = True
                    p_res.font.color.rgb = GREEN

    # -------------------------------------------------------------
    # 7. Update Slide 16 (Old Slide 10: Recommendations & Next Steps)
    # -------------------------------------------------------------
    slide16 = prs.slides[15]
    for shape in slide16.shapes:
        if shape.name == 'TextBox 3':
            shape.text_frame.text = "16"
        elif shape.name == 'TextBox 7':
            shape.text_frame.text = (
                "Deploy data-driven policy update: extend grace threshold to 15 min to recover "
                "232 transit-delayed shifts ($42k ROI). Target chronic tardiness (EMP0066) with individual supervisor coaching."
            )
            for p in shape.text_frame.paragraphs:
                p.font.name = 'Calibri'
                p.font.size = Pt(11)
                p.font.color.rgb = TEXT_BODY
        elif shape.name == 'TextBox 11':
            shape.text_frame.text = (
                "Single-facility observation window (October 2026); turnstiles record punch times without "
                "meal break tracking (elapsed duration vs. net working hours). Live deployment & 58 tests fully verified."
            )
            for p in shape.text_frame.paragraphs:
                p.font.name = 'Calibri'
                p.font.size = Pt(11)
                p.font.color.rgb = TEXT_BODY
        elif shape.name == 'TextBox 15':
            shape.text_frame.text = (
                "Streamlit portal fully operational on Community Cloud with canonical 2,400-record Enterprise Dataset "
                "(8 divisions, 120 employees, October 2026). All 58 tests passing (100%). Ready for executive presentation."
            )
            for p in shape.text_frame.paragraphs:
                p.font.name = 'Calibri'
                p.font.size = Pt(11)
                p.font.color.rgb = TEXT_BODY

    # -------------------------------------------------------------
    # 8. Update Slide 17 (Old Slide 11: Live demo and Q&A)
    # -------------------------------------------------------------
    slide17 = prs.slides[16]
    for shape in slide17.shapes:
        if shape.name == 'TextBox 1':
            shape.text_frame.text = ""
        elif shape.name == 'TextBox 4':
            shape.text_frame.text = (
                "Live Cloud App: https://employeeattendancepatternanalysis-xweeu4ylh8pneqxoxkikwk.streamlit.app/\n"
                "GitHub Repository: https://github.com/AyushKatiyar972194/Employee_Attendance_Pattern_Analysis\n"
                "Local App Command: streamlit run app.py (http://localhost:8501)\n"
                "Student: Ayush Katiyar | University Roll No: 2500320140036\n"
                "Batch ID: ABES_OND26_MCA 2nd Year_Data Analytics_Batch 01\n"
                "Project ID: P070 | Project Mentor: Dinesh Sereno\n\n"
                "Thank you · Questions & Discussion"
            )
            for p in shape.text_frame.paragraphs:
                p.font.name = 'Calibri'
                p.font.size = Pt(12)
                p.font.color.rgb = RGBColor(0xEA, 0xEB, 0xEE)
    if os.path.exists(logo_path):
        slide17.shapes.add_picture(logo_path, Inches(0.50), Inches(0.30), width=Inches(1.50))

    # Global pass: replace any remaining EAPA-01 with P070 and Alpna Lodhi with Dinesh Sereno
    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                for p in shape.text_frame.paragraphs:
                    if "EAPA-01" in p.text:
                        p.text = p.text.replace("EAPA-01", "P070")
                    if "Alpna Lodhi" in p.text:
                        p.text = p.text.replace("Alpna Lodhi", "Dinesh Sereno")

    # Save both filenames for backward and forward compatibility
    prs.save('EAPA-01_Presentation.pptx')
    prs.save('P070_Presentation.pptx')
    print("SUCCESS: EAPA-01_Presentation.pptx and P070_Presentation.pptx generated with 17 complete slides!")

if __name__ == '__main__':
    build_presentation()
