import docx

doc = docx.Document('HCL_Docs/EAPA-01_Project_Document.docx')
print('=== Paragraphs in EAPA-01_Project_Document.docx ===')
for i, p in enumerate(doc.paragraphs):
    txt_lower = p.text.lower()
    if any(k in txt_lower for k in ['eapa', 'alpna', 'lodhi', 'mentor', 'batch', '2500320140036', 'p070']):
        print(f'P{i}: {p.text}')

for t_idx, table in enumerate(doc.tables):
    for r_idx, row in enumerate(table.rows):
        for c_idx, cell in enumerate(row.cells):
            txt_lower = cell.text.lower()
            if any(k in txt_lower for k in ['eapa', 'alpna', 'lodhi', 'mentor', 'batch', '2500320140036', 'p070']):
                print(f'T{t_idx} R{r_idx}C{c_idx}: {cell.text.strip()}')
