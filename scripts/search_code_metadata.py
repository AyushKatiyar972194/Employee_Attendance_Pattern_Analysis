import os

search_terms = ['eapa', 'alpna', 'lodhi', 'sereno', 'p070', 'batch 01', 'batch 1']
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

for term, paths in results.items():
    print(f'=== Matches for "{term}" ({len(paths)}) ===')
    for p in sorted(set(paths)):
        print(f'  {p}')
