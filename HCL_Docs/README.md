# Workforce Attendance Pattern Analysis Platform

**Northstar Technologies · Enterprise Operations Intelligence System**

---

## Executive Summary

The **Workforce Attendance Pattern Analysis Platform** is an enterprise data analytics application designed to evaluate employee attendance patterns, cross-department punctuality benchmarks, shift duration variance, and pipeline data validation metrics.

## Key Modules

- **Executive Overview** — Active attendance fulfillment rates, daily status breakdowns, and historical reporting trends.
- **Department Benchmarks** — Cross-departmental attendance comparisons, fulfillment differentials, and weekday pattern trends.
- **Time & Lateness Intelligence** — Shift check-in punctuality, grace tolerance violations, arrival variances, and recorded shift durations.
- **Data Quality & Audit** — Automated data hygiene diagnostics, schema reconciliation, missing field detection, and statistical anomaly flags.
- **Universal Filters** — Department, date range, and status filters across all analytical views.
- **Data Export** — Filtered and master dataset exports with UTF-8 BOM encoding for seamless Excel compatibility.

## Technology Architecture

| Component | Standard / Framework |
|---|---|
| Application Engine | Python 3.12 |
| Interface Platform | Streamlit (Custom Enterprise Theme) |
| Relational Storage | SQLite (Relational Foreign Key Enforced) |
| Data Processing | pandas, NumPy |
| Statistical Computations | SciPy, statsmodels |
| Data Visualisation | Plotly (Corporate Layouts & Palettes) |
| Automated Test Suite | pytest |

## Relational Schema

Five-table relational database architecture with an integrated 34-column analytics view:

| Table / Entity | Records | Description |
|---|---|---|
| `departments` | 8 | Engineering, HR, Finance, Sales, Support, Product, QA, Operations |
| `employees` | 120 | Active staff directory across 8 operating units |
| `attendance_statuses` | 4 | PRESENT, ABSENT, APPROVED_LEAVE, HOLIDAY |
| `work_calendar` | 248 | Departmental work schedule & multi-shift grace period rules |
| `attendance_records` | 2,400 | Full October 2026 multi-date attendance logs (20 working days) |
| `vw_attendance_analysis` | 2,400 | Denormalized 34-column relational view |

## Local Installation & Setup

```powershell
# Open terminal in project root
cd D:\Employee_Attendance_Pattern_Analysis

# Create virtual environment
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1

# Install requirements
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip check
```

## Running the Application

```powershell
streamlit run app.py
```
Open `http://localhost:8501` in your browser.

## Test Verification

```powershell
python -m pytest -v
```
All 25 automated tests pass:
- 11 data layer and schema integrity tests (`tests/test_data.py`)
- 8 metric calculation & statistical test cases (`tests/test_analysis.py`)
- 6 Streamlit page rendering and load-time tests (`tests/test_app.py`)
