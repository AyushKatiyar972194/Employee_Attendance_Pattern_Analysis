# Employee Attendance Pattern Analysis (EAPA-01)
## Master Project Documentation: Purpose, Architecture, Methodology & Operational Impact

---

## 1. Executive Summary & Project Identity

| Attribute | Specification |
| :--- | :--- |
| **Project Code** | `EAPA-01` |
| **Project Title** | Enterprise Workforce Attendance & Punctuality Intelligence Platform |
| **Author / Candidate** | **Ayush Katiyar** (Roll No: `2500320140036`) |
| **Institution & Batch** | ABES Engineering College · MCA 2nd Year Data Analytics (HCLTech Career Shaper) |
| **Faculty Mentor** | Alpna Lodhi |
| **Live Cloud Application** | [employeeattendancepatternanalysis.streamlit.app](https://employeeattendancepatternanalysis-xweeu4ylh8pneqxoxkikwk.streamlit.app/) |
| **GitHub Repository** | [github.com/AyushKatiyar972194/Employee_Attendance_Pattern_Analysis](https://github.com/AyushKatiyar972194/Employee_Attendance_Pattern_Analysis) |
| **Client / Context** | Northstar Technologies (Noida Regional Operations & Distributed Engineering Hub) |
| **Observation Window** | October 1, 2026 – October 31, 2026 (22 Working Days, 2 Weekend Periods, 0 Official Holidays) |
| **Workforce Scale** | 120 Full-Time Employees across 8 Functional Operating Departments |
| **Master Dataset Scale** | 2,400 Raw Shift Records expanded into 34 Dimensional Analytical Features |
| **Technology Stack** | Python 3.12, Streamlit 1.40+, SQLite 3, Pandas, NumPy, Plotly Express, Scikit-Learn |
| **Test Verification** | 58 Automated Pytest Unit & Integration Tests (100% Pass Rate) |

```
                       ┌──────────────────────────────────────────────┐
                       │           Northstar Technologies             │
                       │   Workforce Attendance Intelligence Platform │
                       └──────────────────────┬───────────────────────┘
                                              │
              ┌───────────────────────────────┴───────────────────────────────┐
              ▼                                                               ▼
   ┌───────────────────────┐                                       ┌───────────────────────┐
   │   Biometric Loggers   │                                       │   Multi-Hub Roster    │
   │   (Punches / Times)   │                                       │   (120 Staff / 8 Dept)│
   └──────────┬────────────┘                                       └───────────┬───────────┘
              │                                                                │
              └───────────────────────────────┬────────────────────────────────┘
                                              │
                                              ▼
                             ┌─────────────────────────────────┐
                             │    Data Ingestion & Cleaning    │
                             │  • Smart Alias Column Matcher   │
                             │  • Missing Punch Imputation     │
                             │  • SQLite Star-Schema Database  │
                             └────────────────┬────────────────┘
                                              │
                                              ▼
                             ┌─────────────────────────────────┐
                             │       Analytics Core Engine     │
                             │  • Punctuality Sensitivity      │
                             │  • Anomaly Isolation Forest     │
                             │  • Risk Propensity Predictor    │
                             └────────────────┬────────────────┘
                                              │
         ┌────────────────────────────────────┼────────────────────────────────────┐
         ▼                                    ▼                                    ▼
┌──────────────────┐               ┌───────────────────────┐              ┌──────────────────┐
│ Executive Portal │               │ Operational Forensics │              │ Policy Simulation│
│ (KPIs / Grades)  │               │ (1-on-1 Action Plans) │              │ ($42k Recovery)  │
└──────────────────┘               └───────────────────────┘              └──────────────────┘
```

---

## 2. The Business Problem ("Why")

Prior to this initiative, Northstar Technologies monitored attendance through basic high-level biometric headcounts. This created an **optical illusion of operational discipline**:

1. **The Punctuality Paradox:**
   * Headline attendance was recorded at **95.9%** (2,302 attended shifts out of 2,400 scheduled shifts).
   * However, **17.0% of all attended shifts (391 shifts)** breached the scheduled 09:00 AM cutoff plus the 10-minute grace period.
   * Operations managers believed workforce availability was pristine, while daily morning standups were consistently disrupted.
2. **The "Customer Support" Commute Anomaly:**
   * Customer Support demonstrated near-perfect shift attendance (**96.2%**), yet suffered from a staggering **23.8% late arrival rate**.
   * Commute transit bottleneck forensics revealed that support staff morning punches clustered sharply between **09:11 AM and 09:14 AM**—missing the rigid 10-minute cutoff by merely 1 to 4 minutes due to Noida Metro interchange congestion.
3. **Ghost Hours & Missing Clock-Outs:**
   * **14 shifts** had valid morning check-ins but missing check-out timestamps.
   * Unresolved, these punches created administrative deadlocks in payroll calculation, overtime reconciliation, and statutory compliance.
4. **Direct Financial Impact:**
   * Punctuality slippage accounted for **169.4 lost productive hours** in October 2026 alone.
   * At standard fully burdened enterprise labor cost tiers ($35.00/hour blended rate), unmanaged morning delays represented a **$71,148 annualized payroll drag**.

---

## 3. System Architecture & Engineering ("How")

### 3.1 Relational Schema (`data/app.db`)
The persistence tier utilizes SQLite configured with strict relational integrity (`PRAGMA foreign_keys = ON`), foreign-key cascades, and a multi-table analytical architecture:

* `departments`: Department master metadata (ID, Department Name, Operating Cost Center, Base Office Location).
* `employees`: Employee roster metadata (ID, Employee Code, Department FK, Hire Date, Employment Status).
* `attendance_statuses`: Canonical status definitions (`PRESENT`, `ABSENT`, `APPROVED_LEAVE`, `HOLIDAY`).
* `work_calendar`: Department-specific calendar matrix including scheduled start/end times (`09:00` / `17:00`), working day indicators, and grace thresholds (10 minutes).
* `attendance_records`: Core transaction log capturing punch timestamps (`check_in_time`, `check_out_time`), status codes, audit source labels, and timestamps.
* `vw_attendance_analysis`: 34-column pre-joined database view joining employees, departments, calendar rules, and punch records to enable high-throughput analytical querying without runtime join overhead.

### 3.2 The Smart Resilient Ingestion Engine
Real-world enterprise biometric machines and external branches rarely output standardized database column names. The batch ingestion pipeline in [`src/data_loader.py`](file:///d:/Employee_Attendance_Pattern_Analysis/src/data_loader.py) contains `normalize_uploaded_batch()`:
* **Fuzzy Alias Resolution:** Automatically maps variations such as `Employee Code` / `Emp ID` ➔ `employee_code`, `Date` / `Shift Date` ➔ `attendance_date`, `Clock In` / `In Time` ➔ `check_in_time`, and `Clock Out` / `Out Time` ➔ `check_out_time`.
* **Heuristic Punch Inference:** If an uploaded batch omits the `status_code` column (common in punch-card CSVs), the engine inspects timestamps—automatically assigning `PRESENT` if a check-in punch exists, and `ABSENT` if null.
* **Date & Timestamp Standardization:** Harmonizes multi-format dates (`YYYY-MM-DD`, `DD-MM-YYYY`, `DD Mon YYYY`) and 12-hour AM/PM times into standard 24-hour `HH:MM` values.
* **Zero Foreign-Key Failures:** Automatically provisions new employee profiles in the workforce registry if uncatalogued employee IDs are ingested.
* **Dual Ingestion Modes:** Supports non-destructive incremental appending (`mode="append"`) and full audit replacement (`mode="replace"`), backed by automated canonical snapshot tables (`canonical_attendance_records`, `canonical_work_calendar`) allowing 1-click restoration of baseline production data.

---

## 4. Mathematical Formulations & Statistical Engine

### 4.1 Core Attendance Formulation
$$\text{Attendance Rate} = \left( \frac{\sum [\text{status\_code} = \text{'PRESENT'}]}{\text{Total Scheduled Shifts}} \right) \times 100$$

### 4.2 Lateness & Grace Period Delta
For each attended shift, arrival delay is computed relative to scheduled start ($T_{\text{sched}} = \text{09:00}$):
$$\Delta_{\text{arrival}} = T_{\text{actual\_in}} - T_{\text{sched}}$$

A shift is flagged as late if and only if:
$$\text{is\_late} = \begin{cases} 
1, & \text{if } \text{status\_code} = \text{'PRESENT'} \text{ and } \Delta_{\text{arrival}} > \text{Grace Minutes} \\
0, & \text{otherwise}
\end{cases}$$

### 4.3 Punctuality Sensitivity Model
To solve the Customer Support paradox without punitive managerial escalation, the engine models grace threshold adjustments:
$$\text{Simulated Punctuality}(\tau) = \frac{\sum [\text{status\_code} = \text{'PRESENT'} \land \Delta_{\text{arrival}} \le \tau]}{\sum [\text{status\_code} = \text{'PRESENT'}]} \times 100$$
* **Finding:** Increasing grace from **10 to 15 minutes** reclassifies **232 late shifts** as on-time, elevating company-wide punctuality from **83.0% to 93.1% (+10.1% gain)** and eliminating **59.3% of all tardiness infractions**.

### 4.4 Unsupervised Anomaly Detection & Risk Scoring
* **Isolation Forest (`src/anomaly_detector.py`):** Unsupervised outlier identification across continuous features (arrival delays, shift elapsed durations, departure deltas). Detects irregular punch behavior (e.g., short 4-hour shifts or delayed morning arrivals).
* **Predictive Attendance Watchlist (`src/predictive.py`):** Evaluates multi-factor employee risk scores based on:
  $$S_{\text{risk}} = 0.40 \times R_{\text{absence}} + 0.35 \times R_{\text{lateness}} + 0.15 \times \bar{\Delta}_{\text{late\_mins}} + 0.10 \times N_{\text{missing\_punches}}$$
  Employees are segmented into risk tiers (`Critical`, `Moderate`, `Low`) to trigger targeted supervisor support before absenteeism escalates into turnover.

---

## 5. Application Walkthrough & User Capabilities

The platform operates as a responsive multipage analytical web application (`http://localhost:8501`):

### Home: Executive Command Center (`app.py`)
* **Executive Flash Briefing:** Plain-English, 20-second summary translating raw database rows into board-level business health insights.
* **Dynamic KPI Scorecard:** Real-time headcount, attendance rate, total late shifts, unrecorded clock-outs, and annualized cost impact.
* **Department Performance Grades:** Letter grades (`⭐ Grade A+ Benchmark` for Finance & Operations; `🔴 Grade C Commute Bottleneck` for Customer Support).
* **Policy Sensitivity Simulator:** Visual interactive curve demonstrating the mathematical impact of shifting grace periods from 5 to 30 minutes.
* **Employee 360° Profile Dossier:** Comprehensive employee shift ledger download and an actionable **Ready-to-Use 1-on-1 Conversation Script for Supervisors** (Opening Appreciation, Data Review, Schedule Action).

### Page 1: Overview & Workforce Trends (`pages/1_Overview.py`)
* Company-wide daily attendance trends, weekly cadence analysis, and attendance volume distributions.
* Interactive global filters (Department, Date Range, Status) with immediate reactive KPI card updates.

### Page 2: Department Drill-Down (`pages/2_Department_Analysis.py`)
* Benchmarking all 8 departments across attendance and punctuality dimensions.
* Attendance fulfillment vs. punctuality quadrant matrix identifying benchmark, stable, and commute-impacted groups.
* Heatmap matrix tracking day-by-day departmental performance.

### Page 3: Time & Punctuality Forensics (`pages/3_Time_and_Lateness.py`)
* Timestamp arrival distribution curves mapping morning arrivals in 5-minute bins.
* Elapsed shift duration analysis highlighting under-hour and extended-hour shifts.
* Exportable table of all 391 late arrival incidents.

### Page 4: Data Quality & Ingestion Portal (`pages/4_Data_Quality.py`)
* Automated data integrity audit (missing values, schema consistency, time-range validity).
* Flagged missing clock-out remediation portal with instant CSV ledger export.
* Enterprise CSV Batch Ingestion Tool: smart auto-mapping, live preview, append vs. replace mode, and one-click canonical database reset.

### Page 5: Pattern Intelligence & Policy Lab (`pages/5_Pattern_Intelligence.py`)
* ML-driven employee risk watchlist identifying staff requiring proactive retention or commute counseling.
* Interactive Grace Period Policy Simulator with department-by-department impact breakdown.
* Financial Cost Calculator estimating recoverable payroll hours and monetary savings.

---

## 6. Verification, Testing & Error Resilience

The platform features automated quality assurance:
* **Test Suite:** 58 automated unit and integration tests in `tests/`:
  * `test_analysis.py`: Mathematical metrics, rate calculations, sensitivity curves, and aggregation logic.
  * `test_app.py`: Streamlit component rendering, session state initialization, and visual styling.
  * `test_data.py`: Database loading, row counts, constraints, normalization, and canonical resets.
  * `test_error_resilience.py`: Defensive error-handling boundaries and graceful fallbacks.
  * `test_pipeline_quality.py`: End-to-end data pipeline validation.
  * `test_predictive.py`: Anomaly detection algorithms and risk-scoring models.
* **Zero Deprecation Warnings:** 100% updated to modern Streamlit specifications (`width="stretch"` / `width="content"` replacing deprecated `use_container_width`).
* **Session Isolation Fixture:** [`tests/conftest.py`](file:///d:/Employee_Attendance_Pattern_Analysis/tests/conftest.py) automatically restores the database to the canonical baseline before and after tests, preventing state pollution.

---

## 7. How to Run, Test, and Operate

### 7.1 Launching the Live Application
```powershell
streamlit run app.py --server.port 8501 --server.headless true
```
Access the application at: `http://localhost:8501`

### 7.2 Executing the Automated Test Suite
```powershell
python -m pytest -v
```
Expected outcome: **58 passed in < 15 seconds**.

### 7.3 Ingesting New Batch Data
1. Navigate to **Page 4: Data Quality & Records**.
2. Upload any attendance CSV file (standard headers or arbitrary names like `Emp ID`, `Date`, `In Time`, `Out Time`).
3. Inspect the **Smart Column Mapping** preview.
4. Choose **Append** (add to existing) or **Replace All** (set as active audit cycle).
5. Click **Commit to Active Database**—all metrics, charts, and grades across all 6 pages recompute dynamically.
6. Click **Restore Canonical Baseline** at any time to return to the original October 2026 dataset.
