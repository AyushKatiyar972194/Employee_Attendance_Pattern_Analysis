files = [
    'README.md',
    'PROJECT_MASTER_DOCUMENTATION.md',
    'INTERVIEW_PREP_GUIDE.md',
    'HCL_Docs/BUILD_PLAN.md',
    'docs/EDA_ENTERPRISE_ANALYSIS_REPORT.md'
]

for f in files:
    with open(f, 'r', encoding='utf-8', errors='ignore') as fp:
        lines = fp.readlines()
    print(f"\n=== {f} ===")
    for idx, line in enumerate(lines, 1):
        low = line.lower()
        if any(k in low for k in ['alpna', 'lodhi', 'mentor', 'batch', 'eapa-01', 'eapa_01']):
            print(f"  Line {idx}: {line.strip()[:100]}")
