import os
import docx

hcl_dir = 'HCL_Docs'
docs_dir = 'docs'

for folder in [hcl_dir, docs_dir]:
    for f in os.listdir(folder):
        if f.endswith('.docx'):
            p = os.path.join(folder, f)
            try:
                doc = docx.Document(p)
                matches = []
                for idx, para in enumerate(doc.paragraphs):
                    low = para.text.lower()
                    if any(k in low for k in ['alpna', 'lodhi', 'eapa-01', 'eapa_01', 'abes_ond26', '[to confirm]']):
                        matches.append(f"P{idx}: {para.text.strip()}")
                for t_idx, table in enumerate(doc.tables):
                    for r_idx, row in enumerate(table.rows):
                        for c_idx, cell in enumerate(row.cells):
                            low = cell.text.lower()
                            if any(k in low for k in ['alpna', 'lodhi', 'eapa-01', 'eapa_01', 'abes_ond26', '[to confirm]']):
                                matches.append(f"T{t_idx} R{r_idx}C{c_idx}: {cell.text.strip()}")
                if matches:
                    print(f"\n=== {p} ({len(matches)} matches) ===")
                    for m in set(matches):
                        print(f"  {m}")
            except Exception as e:
                print(f"Error {p}: {e}")
