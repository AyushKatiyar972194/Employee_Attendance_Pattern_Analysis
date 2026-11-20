"""Build the enhanced, professional EAPA-01 Presentation with cropped screenshots."""
import os
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    # Load original presentation to preserve exact slide layouts and design assets
    prs = pptx.Presentation('EAPA-01_Presentation_original.pptx')
    blank_layout = prs.slide_layouts[6]
    
    # Palette definitions
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
        # Title
        tx_title = slide.shapes.add_textbox(Inches(0.50), Inches(0.30), Inches(9.00), Inches(0.75))
        tf = tx_title.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.name = 'Calibri'
        p.font.size = Pt(22)
        p.font.bold = True
        p.font.color.rgb = TEXT_DARK
        
        # Footer text
        tx_ftr = slide.shapes.add_textbox(Inches(0.50), Inches(5.20), Inches(7.50), Inches(0.30))
        tf_f = tx_ftr.text_frame
        p_f = tf_f.paragraphs[0]
        p_f.text = "HCLTech Career Shaper ABES Engineering College | EAPA-01 - Employee Attendance Pattern Analysis"
        p_f.font.name = 'Calibri'
        p_f.font.size = Pt(9)
        p_f.font.color.rgb = TEXT_MUTED

        # Slide number
        tx_num = slide.shapes.add_textbox(Inches(9.00), Inches(5.20), Inches(0.50), Inches(0.30))
        tf_n = tx_num.text_frame
        p_n = tf_n.paragraphs[0]
        p_n.text = str(slide_num)
        p_n.alignment = PP_ALIGN.RIGHT
        p_n.font.name = 'Calibri'
        p_n.font.size = Pt(9)
        p_n.font.color.rgb = TEXT_MUTED

    def add_card(slide, left, top, width, height, title, lines, badge_text=None, badge_color=CRIMSON):
        # Card background
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = CARD_BG
        shape.line.color.rgb = CARD_BORDER
        shape.line.width = Pt(1)

        # Badge / icon
        content_top = top + Inches(0.12)
        text_left = left + Inches(0.15)
        text_width = width - Inches(0.30)
        
        if badge_text:
            badge = slide.shapes.add_shape(MSO_SHAPE.OVAL, left + Inches(0.15), content_top, Inches(0.28), Inches(0.28))
            badge.fill.solid()
            badge.fill.fore_color.rgb = badge_color
            badge.line.fill.background()
            p_b = badge.text_frame.paragraphs[0]
            p_b.text = badge_text
            p_b.font.name = 'Calibri'
            p_b.font.size = Pt(9)
            p_b.font.bold = True
            p_b.font.color.rgb = WHITE
            p_b.alignment = PP_ALIGN.CENTER
            
            # Title next to badge
            tx = slide.shapes.add_textbox(left + Inches(0.48), content_top - Inches(0.04), width - Inches(0.55), Inches(0.35))
            tf = tx.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = title
            p.font.name = 'Calibri'
            p.font.size = Pt(11.5)
            p.font.bold = True
            p.font.color.rgb = TEXT_DARK
            content_top += Inches(0.32)
        else:
            # Title alone
            tx = slide.shapes.add_textbox(text_left, content_top, text_width, Inches(0.35))
            tf = tx.text_frame
            tf.word_wrap = True
            p = tf.paragraphs[0]
            p.text = title
            p.font.name = 'Calibri'
            p.font.size = Pt(11.5)
            p.font.bold = True
            p.font.color.rgb = TEXT_DARK
            content_top += Inches(0.30)

        # Body lines
        body_height = height - (content_top - top) - Inches(0.10)
        tx_b = slide.shapes.add_textbox(text_left, content_top, text_width, body_height)
        tf_b = tx_b.text_frame
        tf_b.word_wrap = True
        
        for i, line in enumerate(lines):
            p = tf_b.paragraphs[0] if i == 0 else tf_b.add_paragraph()
            p.text = line
            p.font.name = 'Calibri'
            p.font.size = Pt(9.5)
            p.font.color.rgb = TEXT_BODY
            p.space_after = Pt(2)

    # -------------------------------------------------------------
    # 1. Update Slide 1 (Title Slide): Insert ABES logo
    # -------------------------------------------------------------
    slide1 = prs.slides[0]
    for shape in slide1.shapes:
        if shape.name == 'TextBox 1':
            shape.text_frame.text = ""  # Clear "[ABES logo]" placeholder
    if os.path.exists('ABES_logo.jpg'):
        slide1.shapes.add_picture('ABES_logo.jpg', Inches(0.50), Inches(0.30), width=Inches(1.50))

    # We will build a new presentation or reconstruct slides to ensure perfect ordering
    # Let's inspect the original slides 1-6, 8-11
    # We can create a fresh presentation that takes original slides 1-6, adds our 7 new slides, and adds updated 8-11
    print("Base assets verified. Building new cohesive presentation...")

if __name__ == '__main__':
    create_presentation()
