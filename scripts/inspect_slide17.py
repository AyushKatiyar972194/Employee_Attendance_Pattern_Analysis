import pptx

prs = pptx.Presentation('EAPA-01_Presentation.pptx')
s17 = prs.slides[16]
for idx, sh in enumerate(s17.shapes):
    if sh.has_text_frame:
        print(f"Shape {idx} (name={sh.name}):\n{sh.text_frame.text}\n")
