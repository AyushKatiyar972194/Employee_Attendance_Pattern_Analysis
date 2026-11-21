import os
import docx
import pptx

search_terms = ['eapa-01', 'alpna', 'lodhi', 'abes_ond26', '[to confirm]']
results = {term: [] for term in search_terms}

exclude_dirs = {'.venv', 'venv', '.git', '__pycache__', '.pytest_cache'}

for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in exclude_dirs]
    for file in files:
        path = os.path.join(root, file)
        ext = os.path.splitext(file)[1].lower()
        if ext in ['.py', '.md', '.txt', '.json', '.html', '.csv', '.yaml', '.yml', '.sql']:
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().lower()
                    for term in search_terms:
                        if term in content:
                            results[term].append(path)
            except Exception:
                pass
        elif ext == '.docx':
            try:
                doc = docx.Document(path)
                full_text = ' '.join(p.text for p in doc.paragraphs) + ' ' + ' '.join(c.text for t in doc.tables for r in t.rows for c in r.cells)
                full_text_lower = full_text.lower()
                for term in search_terms:
                    if term in full_text_lower:
                        results[term].append(path)
            except Exception:
                pass
        elif ext == '.pptx':
            try:
                prs = pptx.Presentation(path)
                full_text = ' '.join(sh.text_frame.text for sl in prs.slides for sh in sl.shapes if sh.has_text_frame)
                full_text_lower = full_text.lower()
                for term in search_terms:
                    if term in full_text_lower:
                        results[term].append(path)
            except Exception:
                pass

for term, paths in results.items():
    print(f'=== Matches for "{term}" ({len(paths)}) ===')
    for p in sorted(set(paths)):
        print(f'  {p}')
