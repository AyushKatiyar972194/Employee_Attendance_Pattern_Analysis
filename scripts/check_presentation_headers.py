import pptx

prs = pptx.Presentation('EAPA-01_Presentation.pptx')
for idx, slide in enumerate(prs.slides, 1):
    for sh in slide.shapes:
        if sh.has_text_frame:
            for p in sh.text_frame.paragraphs:
                txt = p.text
                if any(k in txt for k in ['EAPA', 'Alpna', 'Lodhi']):
                    print(f"Slide {idx} ({sh.name}): {txt}")
