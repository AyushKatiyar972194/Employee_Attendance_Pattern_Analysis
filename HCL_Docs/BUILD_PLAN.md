# BUILD PLAN — Employee Attendance Pattern Analysis

**Project ID:** P070  
**Owner / Learner:** Ayush Katiyar (University Roll No: 2500320140036 · ABES Engineering College)  
**Batch ID:** ABES_OND26_MCA 2nd Year_Data Analytics_Batch 01  
**Project Mentor:** Dinesh Sereno  
**Version:** Step 14 baseline; execute one task at a time in Step 15.  
**Status:** Plan only; no BUILD tasks are claimed completed.

## How to use this file with an AI coding assistant

1. Read this entire plan and the linked documents before editing.
2. Start only the BUILD task explicitly requested by the user (for example, `BUILD-01`).
3. For that task, read its goal, files, linked IDs, exact prompt, checks and required tests.
4. Implement only that task, preserve existing files/data/IDs, run the listed checks, report results and stop.
5. If a test is impossible before a later task, label it **pending**; never claim it passed.
6. Do not start the next BUILD task until the user authorises it.
7. Treat documents as the baseline, but flag contradictions and propose the smallest evidence-based fix before changing a definition.

## 1. Project summary (10 lines)

1. Project P070 is an MCA Data Analysis application for a fictional organisation, Northstar Technologies, Noida.
2. It examines employee attendance patterns using synthetic data only.
3. The database is SQLite at data/app.db and contains five related tables.
4. The sample includes 50 employees, five departments and 300 attendance facts.
5. The attendance facts cover six observation dates in October 2026; the calendar covers 30 dates.
6. The application uses Python 3.12, pandas, NumPy, SciPy/statsmodels, Streamlit and Plotly.
7. Its four Streamlit pages cover Overview, Department Analysis, Time and Lateness, and Data Quality.
8. Nine UI specifications are grouped into those four pages, with shared native Streamlit filters.
9. It calculates descriptive KPIs, late arrivals, elapsed recorded duration, trends and data-quality indicators.
10. It is an academic reporting prototype, not payroll, real-time tracking or employee discipline software.

### Source documents and existing deliverables

> Relative links assume the project folder remains alongside the earlier numbered deliverables in the same parent directory. If moving this repository to GitHub, copy the needed reference documents into `docs/references/` and update these links; do not pretend parent-folder documents are already committed.

- [01 Project Understanding](../01_Ayush_Employee_Attendance_Pattern_Understanding.docx)
- [02 HMW Statements](../02_Ayush_Employee_Attendance_HMW_Statements.docx)
- [03 Needs Analysis](../03_Ayush_Employee_Attendance_Needs_Analysis.docx)
- [04 RTM](../04_Ayush_Employee_Attendance_Traceability_Matrix.xlsx)
- [05 BRD](../05_Ayush_Employee_Attendance_BRD.docx)
- [07 TRD](../07_Ayush_Employee_Attendance_TRD.docx)
- [08 Database Design](../08_Database_Design.xlsx)
- [09 ER Diagram](docs/09_ER_Diagram.docx)
- [09 ER Diagram PNG](docs/09_ER_Diagram.png)
- [10 Dataset Generation Package](../10_Employee_Attendance_Dataset_Package.zip)
- [10 Dataset README](data/README_dataset.txt)
- [11 User Stories](docs/11_User_Stories.docx)
- [12 UI Framework](docs/12_UI_Framework.docx)
- [13 Test Cases](docs/13_Test_Cases.docx)
- [13 Technical tests](tests/test_data.py)
- [13 Analysis tests](tests/test_analysis.py)
- [13 App tests](tests/test_app.py)

**Document sequence:** Step 6 was removed by the user. No PRD exists; do not invent one.

## 2. Final folder structure

```text
employee-attendance-pattern-analysis/
├── app.py
├── BUILD_PLAN.md
├── README.md
├── requirements.txt
├── .gitignore
├── .streamlit/
│   └── config.toml
├── pages/
│   ├── 1_Overview.py
│   ├── 2_Department_Analysis.py
│   ├── 3_Time_and_Lateness.py
│   └── 4_Data_Quality.py
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── data_loader.py
│   ├── validation.py
│   ├── cleaning.py
│   ├── metrics.py
│   ├── statistics.py
│   ├── charts.py
│   ├── export.py
│   ├── ui.py                    # already exists
│   └── generate_data.py         # already exists
├── data/
│   ├── app.db                   # existing synthetic seed DB
│   ├── *.csv                    # existing generated data
│   ├── *.xlsx                   # existing validation/dataset workbooks
│   └── README_dataset.txt
├── tests/
│   ├── __init__.py
│   ├── test_data.py             # already exists
│   ├── test_analysis.py         # already exists
│   └── test_app.py              # already exists
└── docs/
    ├── 09_ER_Diagram.docx
    ├── 09_ER_Diagram.png
    ├── 11_User_Stories.docx
    ├── 12_UI_Framework.docx
    ├── 13_Test_Cases.docx
    ├── 14_BUILD_PLAN.docx
    └── references/             # optional copy of prior source docs for GitHub
```

### Non-negotiable business and technical rules

- Use synthetic data only; no real employee details, payroll, biometrics, predictive or disciplinary claims.
- Do not infer absence from a calendar date lacking attendance facts; there are six observed fact dates.
- Keep approved leave distinct from absence; make the denominator treatment explicit and consistent with the BRD.
- Late arrival: check-in strictly after scheduled start plus grace minutes (default 10 in synthetic data).
- Duration: elapsed check-out minus check-in, **not** net work time. Missing check-out remains missing.
- Shared filters must affect all relevant KPIs, charts, tables and exports.
- Use four Streamlit page files for nine UI specifications; extra UI screens become sections/tabs, not unapproved extra pages.
- Use Tailwind only within `st.iframe` for noninteractive decorative components; keep filters and downloads native.
- SQLite seed DB is read-mostly on Community Cloud; do not promise durable writes.
- Preserve BR-12 baseline priority `Could`; its workday denominator logic is an implementation dependency (US-05 `Must*`) requiring mentor confirmation.
- Existing Step 13 tests are specifications and may contain incorrect schema assumptions; fix tests transparently only against authoritative schema and documented rules.

## 3. Ordered build tasks

### BUILD-01 — Project setup and dependencies

**Goal:** Project setup and dependencies.  
**Files:** `requirements.txt, .gitignore, README.md (stub), src/__init__.py, tests/__init__.py, .streamlit/config.toml`  
**User stories + feature IDs:** US-01–US-15; FR-01–FR-12  

**Exact prompt for the AI (copy verbatim after selecting this task):**

> You are implementing BUILD-01 of P070 Employee Attendance Pattern Analysis. Read BUILD_PLAN.md and the relevant source documents linked in Section 1 first. Do not begin any other BUILD task. Create Python 3.12 project setup, preserve existing synthetic data and existing UI/test source. Add compatible pinned requirements for Streamlit, pandas, NumPy, SciPy, statsmodels, Plotly, pytest and openpyxl. Preserve the existing Streamlit theme, make imports work from project root, add safe .gitignore, and document reproducible installation. Do not create application logic or change test expectations yet. Preserve existing IDs, the synthetic SQLite dataset, and unrelated working code. Explain any conflicts before changing definitions. Provide only the files changed, key implementation decisions, the exact checks run and their actual results, and remaining blockers. Stop after this task.

**How to check it:** `python -m pip install -r requirements.txt; python -m pip check; python -m compileall src tests`  
**Tests that must pass / be verified:** Environment resolves, compileall succeeds; no functional tests expected to pass yet.

### BUILD-02 — Database access and deterministic loading

**Goal:** Database access and deterministic loading.  
**Files:** `src/database.py, src/data_loader.py`  
**User stories + feature IDs:** US-01, US-14; FR-01, FR-10  

**Exact prompt for the AI (copy verbatim after selecting this task):**

> You are implementing BUILD-02 of P070 Employee Attendance Pattern Analysis. Read BUILD_PLAN.md and the relevant source documents linked in Section 1 first. Do not begin any other BUILD task. Implement read-only SQLite access to data/app.db and load_attendance_data(db_path) returning a pandas DataFrame from vw_attendance_analysis. Keep schema field names unchanged, preserve missing values, use safe SQL and enable foreign keys per connection. Verify 300 rows and 34 view columns. Add an explicit available-observation-date helper. Do not create attendance facts for missing dates. Preserve existing IDs, the synthetic SQLite dataset, and unrelated working code. Explain any conflicts before changing definitions. Provide only the files changed, key implementation decisions, the exact checks run and their actual results, and remaining blockers. Stop after this task.

**How to check it:** `python -m pytest -q tests/test_data.py -k "database_file or data_loads or row_counts or joined_view or primary_keys or composite_calendar or foreign_keys"`  
**Tests that must pass / be verified:** TC-T-01–TC-T-05; data-loading and schema pytest checks.

### BUILD-03 — Validation and cleaning

**Goal:** Validation and cleaning.  
**Files:** `src/validation.py, src/cleaning.py`  
**User stories + feature IDs:** US-12, US-14; FR-08, FR-10  

**Exact prompt for the AI (copy verbatim after selecting this task):**

> You are implementing BUILD-03 of P070 Employee Attendance Pattern Analysis. Read BUILD_PLAN.md and the relevant source documents linked in Section 1 first. Do not begin any other BUILD task. Implement validate_attendance_data(df) with missing_count, duplicate_count, invalid_count and useful issue breakdowns; implement clean_attendance_data(df). Check key/date/status/time consistency; preserve missing check-outs as missing, do not fabricate check-outs or absences. Keep valid source rows; document invalid-row treatment. Make validation independent of UI. Preserve existing IDs, the synthetic SQLite dataset, and unrelated working code. Explain any conflicts before changing definitions. Provide only the files changed, key implementation decisions, the exact checks run and their actual results, and remaining blockers. Stop after this task.

**How to check it:** `python -m pytest -q tests/test_data.py`  
**Tests that must pass / be verified:** TC-T-06, TC-T-07; data suite including missing check-outs and duplicate checks.

### BUILD-04 — Attendance and coverage KPI functions

**Goal:** Attendance and coverage KPI functions.  
**Files:** `src/metrics.py`  
**User stories + feature IDs:** US-01, US-02, US-03, US-05, US-06; FR-01, FR-02, FR-03, FR-12  

**Exact prompt for the AI (copy verbatim after selecting this task):**

> You are implementing BUILD-04 of P070 Employee Attendance Pattern Analysis. Read BUILD_PLAN.md and the relevant source documents linked in Section 1 first. Do not begin any other BUILD task. Implement attendance_rate, daily_status_counts, department_attendance_rates, record/date coverage helpers, and expected employee-working-day logic. Use observed eligible employee-days and the calendar; do not infer absences from unobserved dates. Respect approved leave rules in BRD and document whether it is excluded from denominator. Return NA/None for zero denominators (align any existing test expecting zero with documented rule). Keep outputs deterministic and testable. Preserve existing IDs, the synthetic SQLite dataset, and unrelated working code. Explain any conflicts before changing definitions. Provide only the files changed, key implementation decisions, the exact checks run and their actual results, and remaining blockers. Stop after this task.

**How to check it:** `python -m pytest -q tests/test_analysis.py -k "attendance_rate or daily_status or department or empty"`  
**Tests that must pass / be verified:** TC-T-08–TC-T-10, TC-T-15; TC-F-01–TC-F-06, TC-F-25 when UI exists.

### BUILD-05 — Lateness, duration and filtering

**Goal:** Lateness, duration and filtering.  
**Files:** `src/metrics.py, src/data_loader.py`  
**User stories + feature IDs:** US-04, US-08, US-09, US-10; FR-05, FR-06, FR-11  

**Exact prompt for the AI (copy verbatim after selecting this task):**

> You are implementing BUILD-05 of P070 Employee Attendance Pattern Analysis. Read BUILD_PLAN.md and the relevant source documents linked in Section 1 first. Do not begin any other BUILD task. Add late_arrival_metrics, elapsed_duration_minutes, late grouping by department/month, and reusable date/department filter function. Lateness is strictly after scheduled start + grace. Duration is elapsed check-out minus check-in, not net paid work. Invalid or missing time pairs yield missing durations. Check month boundaries and empty selections. Preserve existing IDs, the synthetic SQLite dataset, and unrelated working code. Explain any conflicts before changing definitions. Provide only the files changed, key implementation decisions, the exact checks run and their actual results, and remaining blockers. Stop after this task.

**How to check it:** `python -m pytest -q tests/test_analysis.py -k "late or elapsed"`  
**Tests that must pass / be verified:** TC-T-11, TC-T-12, TC-T-19; TC-F-08–TC-F-10, TC-F-23–TC-F-24 after UI.

### BUILD-06 — Statistics and high-absence insights

**Goal:** Statistics and high-absence insights.  
**Files:** `src/statistics.py`  
**User stories + feature IDs:** US-07, US-11; FR-04, FR-07  

**Exact prompt for the AI (copy verbatim after selecting this task):**

> You are implementing BUILD-06 of P070 Employee Attendance Pattern Analysis. Read BUILD_PLAN.md and the relevant source documents linked in Section 1 first. Do not begin any other BUILD task. Implement weekday_attendance_summary and flag_high_absence_dates using a clearly documented Q3 + 1.5×IQR threshold. Handle small/empty samples without misleading significance claims. Expose count, denominator and flag status. Use observed dates only. No forecasting or employee-level disciplinary scoring. Preserve existing IDs, the synthetic SQLite dataset, and unrelated working code. Explain any conflicts before changing definitions. Provide only the files changed, key implementation decisions, the exact checks run and their actual results, and remaining blockers. Stop after this task.

**How to check it:** `python -m pytest -q tests/test_analysis.py -k "weekday or high_absence"`  
**Tests that must pass / be verified:** TC-T-13, TC-T-14; TC-F-07, TC-F-11, TC-F-22 after UI.

### BUILD-07 — Reusable Plotly charts and CSV export

**Goal:** Reusable Plotly charts and CSV export.  
**Files:** `src/charts.py, src/export.py`  
**User stories + feature IDs:** US-03, US-06, US-07, US-09, US-10, US-14; FR-02–FR-06, FR-10  

**Exact prompt for the AI (copy verbatim after selecting this task):**

> You are implementing BUILD-07 of P070 Employee Attendance Pattern Analysis. Read BUILD_PLAN.md and the relevant source documents linked in Section 1 first. Do not begin any other BUILD task. Create pure chart builders for daily status, department rates, weekday patterns, late breakdown and elapsed duration. Provide a filtered DataFrame-to-CSV helper with UTF-8 headers. Charts must show explicit empty states, axis labels, units and no invented data. Never embed personal or external data. Preserve existing IDs, the synthetic SQLite dataset, and unrelated working code. Explain any conflicts before changing definitions. Provide only the files changed, key implementation decisions, the exact checks run and their actual results, and remaining blockers. Stop after this task.

**How to check it:** `python -m pytest -q tests/test_app.py -k "nonexistent"; python -m compileall src`  
**Tests that must pass / be verified:** TC-T-20 requires adding a concrete export test during BUILD-15; TC-F-03, TC-F-19, TC-F-20 after pages.

### BUILD-08 — Shared UI components and app shell

**Goal:** Shared UI components and app shell.  
**Files:** `src/ui.py, app.py, .streamlit/config.toml`  
**User stories + feature IDs:** US-04, US-13, US-15; FR-09, FR-11  

**Exact prompt for the AI (copy verbatim after selecting this task):**

> You are implementing BUILD-08 of P070 Employee Attendance Pattern Analysis. Read BUILD_PLAN.md and the relevant source documents linked in Section 1 first. Do not begin any other BUILD task. Reuse and refine the existing src/ui.py helpers; keep Streamlit controls native and Tailwind CDN inside isolated st.iframe for decorative header/KPI cards. Build app.py as multipage entry point and shared sidebar filter state. Map nine UI specifications onto the four TRD page files. Do not remove the supplied theme. Provide clear metric definitions and synthetic-data notice. Preserve existing IDs, the synthetic SQLite dataset, and unrelated working code. Explain any conflicts before changing definitions. Provide only the files changed, key implementation decisions, the exact checks run and their actual results, and remaining blockers. Stop after this task.

**How to check it:** `streamlit run app.py; python -m pytest -q tests/test_app.py -k "main_app_starts"`  
**Tests that must pass / be verified:** TC-T-16; TC-F-14, TC-F-16, TC-F-21 after all pages.

### BUILD-09 — Overview page

**Goal:** Overview page.  
**Files:** `pages/1_Overview.py`  
**User stories + feature IDs:** US-01, US-02, US-03, US-04, US-05; FR-01, FR-02, FR-11, FR-12  

**Exact prompt for the AI (copy verbatim after selecting this task):**

> You are implementing BUILD-09 of P070 Employee Attendance Pattern Analysis. Read BUILD_PLAN.md and the relevant source documents linked in Section 1 first. Do not begin any other BUILD task. Implement Overview with record coverage, attendance KPI, present/absent/leave counts, daily status chart and shared filters. Show observed date coverage prominently; for zero denominator display unavailable, not a false 0% or infinity. Use src metrics and charts, no duplicate formulas. Preserve existing IDs, the synthetic SQLite dataset, and unrelated working code. Explain any conflicts before changing definitions. Provide only the files changed, key implementation decisions, the exact checks run and their actual results, and remaining blockers. Stop after this task.

**How to check it:** `streamlit run app.py; python -m pytest -q tests/test_app.py -k "Overview"`  
**Tests that must pass / be verified:** TC-F-01–TC-F-05, TC-F-17, TC-F-25; page part of TC-T-17.

### BUILD-10 — Department comparison page

**Goal:** Department comparison page.  
**Files:** `pages/2_Department_Analysis.py`  
**User stories + feature IDs:** US-04, US-06, US-07; FR-03, FR-04, FR-11  

**Exact prompt for the AI (copy verbatim after selecting this task):**

> You are implementing BUILD-10 of P070 Employee Attendance Pattern Analysis. Read BUILD_PLAN.md and the relevant source documents linked in Section 1 first. Do not begin any other BUILD task. Build department attendance comparison, rates and weekday view with shared date/department filters. Explain denominators and exclude unobserved calendar dates from absence counts. Add no-match state. Keep responsive Plotly labels and data table. Preserve existing IDs, the synthetic SQLite dataset, and unrelated working code. Explain any conflicts before changing definitions. Provide only the files changed, key implementation decisions, the exact checks run and their actual results, and remaining blockers. Stop after this task.

**How to check it:** `streamlit run app.py; python -m pytest -q tests/test_app.py -k "Department"`  
**Tests that must pass / be verified:** TC-F-04, TC-F-06, TC-F-07, TC-F-18; page part of TC-T-17.

### BUILD-11 — Time and lateness page

**Goal:** Time and lateness page.  
**Files:** `pages/3_Time_and_Lateness.py`  
**User stories + feature IDs:** US-08, US-09, US-10; FR-05, FR-06  

**Exact prompt for the AI (copy verbatim after selecting this task):**

> You are implementing BUILD-11 of P070 Employee Attendance Pattern Analysis. Read BUILD_PLAN.md and the relevant source documents linked in Section 1 first. Do not begin any other BUILD task. Build late arrivals KPI, department/month breakdown, check-in delay and recorded elapsed duration charts. Apply scheduled start + grace and make missing checkout handling visible. Do not describe elapsed duration as net work hours. Preserve existing IDs, the synthetic SQLite dataset, and unrelated working code. Explain any conflicts before changing definitions. Provide only the files changed, key implementation decisions, the exact checks run and their actual results, and remaining blockers. Stop after this task.

**How to check it:** `streamlit run app.py; python -m pytest -q tests/test_app.py -k "Time_and_Lateness"`  
**Tests that must pass / be verified:** TC-F-08–TC-F-10, TC-F-23, TC-F-24; page part of TC-T-17.

### BUILD-12 — Insights, EDA and supporting views

**Goal:** Insights, EDA and supporting views.  
**Files:** `pages/1_Overview.py, pages/2_Department_Analysis.py, pages/3_Time_and_Lateness.py, src/charts.py`  
**User stories + feature IDs:** US-07, US-11, US-13; FR-04, FR-07, FR-09  

**Exact prompt for the AI (copy verbatim after selecting this task):**

> You are implementing BUILD-12 of P070 Employee Attendance Pattern Analysis. Read BUILD_PLAN.md and the relevant source documents linked in Section 1 first. Do not begin any other BUILD task. Integrate UI-05 EDA, UI-06 Insights and UI-09 About/Definitions as clearly labelled sections/expanders/tabs within the four approved TRD pages, not extra page files. Show high-absence flags with method and sample-size caveats, and no-outlier empty state. Add glossary for attendance and lateness definitions. Preserve existing IDs, the synthetic SQLite dataset, and unrelated working code. Explain any conflicts before changing definitions. Provide only the files changed, key implementation decisions, the exact checks run and their actual results, and remaining blockers. Stop after this task.

**How to check it:** `streamlit run app.py; manually inspect all relevant sections`  
**Tests that must pass / be verified:** TC-F-07, TC-F-11, TC-F-14, TC-F-22.

### BUILD-13 — Data-quality page

**Goal:** Data-quality page.  
**Files:** `pages/4_Data_Quality.py`  
**User stories + feature IDs:** US-12, US-14; FR-08, FR-10  

**Exact prompt for the AI (copy verbatim after selecting this task):**

> You are implementing BUILD-13 of P070 Employee Attendance Pattern Analysis. Read BUILD_PLAN.md and the relevant source documents linked in Section 1 first. Do not begin any other BUILD task. Build validation overview, missing/invalid/duplicate counts, schema checks, issue preview and explanatory notes. Present actual synthetic dataset findings (including missing check-outs) without changing source DB. Surface known observation-date coverage limitation. Preserve existing IDs, the synthetic SQLite dataset, and unrelated working code. Explain any conflicts before changing definitions. Provide only the files changed, key implementation decisions, the exact checks run and their actual results, and remaining blockers. Stop after this task.

**How to check it:** `streamlit run app.py; python -m pytest -q tests/test_app.py -k "Data_Quality"`  
**Tests that must pass / be verified:** TC-F-12, TC-F-13, TC-F-15; page part of TC-T-17.

### BUILD-14 — Data preview, downloads and navigation completion

**Goal:** Data preview, downloads and navigation completion.  
**Files:** `pages/1_Overview.py, pages/4_Data_Quality.py, src/export.py, src/ui.py`  
**User stories + feature IDs:** US-04, US-14, US-15; FR-10, FR-11  

**Exact prompt for the AI (copy verbatim after selecting this task):**

> You are implementing BUILD-14 of P070 Employee Attendance Pattern Analysis. Read BUILD_PLAN.md and the relevant source documents linked in Section 1 first. Do not begin any other BUILD task. Implement UI-07 data preview/download as a section of Data Quality or Overview; CSV download must match selected filters. Complete shared filter persistence, consistent empty states and navigation across four page files. Avoid separate UI-07 page unless TRD is formally amended. Preserve existing IDs, the synthetic SQLite dataset, and unrelated working code. Explain any conflicts before changing definitions. Provide only the files changed, key implementation decisions, the exact checks run and their actual results, and remaining blockers. Stop after this task.

**How to check it:** `streamlit run app.py; manually verify CSV row counts and filter persistence`  
**Tests that must pass / be verified:** TC-F-16–TC-F-21, TC-F-20; TC-T-19, TC-T-20.

### BUILD-15 — Automated tests, corrections and performance

**Goal:** Automated tests, corrections and performance.  
**Files:** `tests/test_data.py, tests/test_analysis.py, tests/test_app.py, src/*.py, app.py, pages/*.py`  
**User stories + feature IDs:** US-01–US-15; FR-01–FR-12  

**Exact prompt for the AI (copy verbatim after selecting this task):**

> You are implementing BUILD-15 of P070 Employee Attendance Pattern Analysis. Read BUILD_PLAN.md and the relevant source documents linked in Section 1 first. Do not begin any other BUILD task. Run all tests and fix implementation defects. First audit test assumptions against real schema: work_calendar uses (calendar_date, department_id); the joined view has 34 fields; attendance data has 6 observed dates. Replace placeholder test logic with actual meaningful assertions for filters and CSV; add deterministic outlier boundary tests. Keep tests honest: never delete, skip or weaken a test solely to get green. Investigate the <3 s warm local render threshold separately from cloud cold start. Preserve existing IDs, the synthetic SQLite dataset, and unrelated working code. Explain any conflicts before changing definitions. Provide only the files changed, key implementation decisions, the exact checks run and their actual results, and remaining blockers. Stop after this task.

**How to check it:** `python -m pytest -q; python -m pip check; python -m compileall .`  
**Tests that must pass / be verified:** All TC-T-01–TC-T-20 pass; execute and record all TC-F-01–TC-F-25 manually/automated; no unresolved Must failure.

### BUILD-16 — README, reproducibility and documentation

**Goal:** README, reproducibility and documentation.  
**Files:** `README.md, docs/13_Test_Cases.docx (results note), BUILD_PLAN.md`  
**User stories + feature IDs:** US-13, US-14, US-15; FR-09, FR-10, FR-11  

**Exact prompt for the AI (copy verbatim after selecting this task):**

> You are implementing BUILD-16 of P070 Employee Attendance Pattern Analysis. Read BUILD_PLAN.md and the relevant source documents linked in Section 1 first. Do not begin any other BUILD task. Write README with purpose, synthetic-data notice, architecture, 5-table schema, setup, run, test, page guide, KPI definitions, six observation dates, limitations, screenshots only if actually captured, and deployment instructions. Record tested versions and actual test results. Do not assert live URL or passed tests without evidence. Preserve existing IDs, the synthetic SQLite dataset, and unrelated working code. Explain any conflicts before changing definitions. Provide only the files changed, key implementation decisions, the exact checks run and their actual results, and remaining blockers. Stop after this task.

**How to check it:** `Review README commands in clean venv; verify relative links`  
**Tests that must pass / be verified:** TC-F-14, TC-F-15; documentation acceptance checklist.

### BUILD-17 — GitHub and Streamlit Community Cloud deployment

**Goal:** GitHub and Streamlit Community Cloud deployment.  
**Files:** `README.md, requirements.txt, .streamlit/config.toml, data/app.db, .gitignore`  
**User stories + feature IDs:** US-01–US-15; FR-01–FR-12  

**Exact prompt for the AI (copy verbatim after selecting this task):**

> You are implementing BUILD-17 of P070 Employee Attendance Pattern Analysis. Read BUILD_PLAN.md and the relevant source documents linked in Section 1 first. Do not begin any other BUILD task. After local DoD, push repository to GitHub, deploy app.py via Streamlit Community Cloud, check dependencies, file paths and seed SQLite read-only behavior. Verify no secrets or real employee data. Open deployed URL and smoke-test all pages, filters, charts and downloads; document actual URL only after successful deployment. Preserve existing IDs, the synthetic SQLite dataset, and unrelated working code. Explain any conflicts before changing definitions. Provide only the files changed, key implementation decisions, the exact checks run and their actual results, and remaining blockers. Stop after this task.

**How to check it:** `python -m pytest -q; streamlit run app.py; manually test deployed URL`  
**Tests that must pass / be verified:** All TC-F and TC-T pass locally; cloud smoke checks pass; live URL recorded.

## 4. Definition of Done

- [ ] All seven baseline **Must** BRs (BR-01, BR-02, BR-03, BR-05, BR-08, BR-10, BR-11) are implemented and demonstrated.
- [ ] BR-12 workday/holiday denominator dependency is implemented and its priority discrepancy is documented for mentor review.
- [ ] All 15 user stories have acceptance evidence; Should-level stories are delivered as in-scope or explicitly signed off as deferred.
- [ ] All TC-T-01 through TC-T-20 are implemented and pass in a clean local environment.
- [ ] All TC-F-01 through TC-F-25 are executed and pass, or any deviations are explicitly approved and documented.
- [ ] No divide-by-zero, fake absence, fabricated checkout, broken navigation or failed download.
- [ ] App starts and all four pages render; local warm AppTest render is under 3 s on the documented test machine.
- [ ] README explains setup, run, test, data limits, metrics and screenshots (if captured).
- [ ] GitHub repository contains no secrets or real personal data.
- [ ] Streamlit Community Cloud URL is actually live and verified for pages, filters and downloads.
- [ ] RTM status and test evidence are updated to reflect actual results, not assumptions.

## 5. Commands (from repository root)

```bash
# Create and activate virtual environment (Windows PowerShell)
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
# On macOS/Linux instead: python3.12 -m venv .venv && source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip check

# Run application
streamlit run app.py

# Run all automated tests
python -m pytest -q

# Run a single file or verbose suite
python -m pytest -q tests/test_data.py
python -m pytest -v
```

**Note:** `requirements.txt` and `app.py` are planned outputs of BUILD-01 and BUILD-08 respectively; commands that depend on them cannot work before those tasks. Verify compatible package versions rather than blindly trusting earlier suggested pins.

## 6. Viva notes: 10 likely questions

1. **What problem does the project solve?** It replaces repeated manual attendance summaries with consistent, filterable descriptive analysis.
2. **Why synthetic data?** It supports repeatable academic demonstrations without exposing employee information.
3. **Why SQLite?** It is lightweight, local, reproducible and adequate for a read-mostly demonstration dataset.
4. **What is the database grain?** One attendance fact per employee per observed attendance date; calendar is per department/date.
5. **How is attendance rate calculated?** Present eligible employee-days divided by the documented expected eligible employee-days, multiplied by 100.
6. **Why is the calendar not enough to infer absence?** A calendar marks possible workdays, but missing attendance facts can mean unobserved data, not absence.
7. **How is lateness determined?** A check-in strictly later than scheduled start plus the grace period is late.
8. **Is check-out minus check-in net work time?** No. It is elapsed recorded duration and does not subtract unrecorded breaks.
9. **What is the role of pytest and AppTest?** pytest checks data and formulas; AppTest checks that Streamlit pages execute without exceptions.
10. **What is the purpose of the RTM?** It links operational questions, business requirements, user stories, UI and tests so coverage is auditable.

## 7. Known risks, corrections and handoff rules

1. **Test/data contract drift:** the existing tests are not proof of working features. The Step 15 implementer must reconcile expected columns, helper signatures, denominator treatment and view schema before claiming green.
2. **Performance variability:** local AppTest <3 s is a smoke-test target; Cloud cold starts and network-dependent Tailwind assets can be slower.
3. **Six observation dates:** the month-long work calendar must not be presented as 30 days of measured attendance.
4. **GitHub references:** prior documents stored outside the repository will not resolve after publishing unless copied into `docs/references/`.
5. **Feature column in RTM:** the existing RTM may leave `Feature` blank. Do not invent a completed mapping; populate FR IDs when formally updating RTM in Step 15, retaining BR/US/UI/TC mappings.
6. **Status reporting:** after each BUILD task, report changed files, commands, pass/fail/pending test results and the next task ID, then wait for approval.

**Next step:** Step 15 starts with **BUILD-01** only after the user requests it.
