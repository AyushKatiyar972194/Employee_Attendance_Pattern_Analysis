"""Canonical dataset generator for Northstar Technologies Workforce Attendance Analytics (P070).

Generates the complete authoritative enterprise dataset:
- 8 diverse business divisions (Engineering, HR, Finance, Sales, Customer Support, Product, QA, Operations)
- 120 employees across regional Indian tech hubs
- 31-day October 2026 calendar (248 calendar records: 20 working days, 9 weekend days, 2 public holidays)
- 2,400 detailed attendance facts across all working days
- Multi-shift configurations (08:00, 08:30, 09:00, 09:30 start times)
- Exported to SQLite (data/app.db), normalized CSVs, and Excel workbook.
"""
from __future__ import annotations

import csv
import random
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd

SEED = 101
random.seed(SEED)

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

PROJECT_NAME = "employee_attendance_pattern_analysis"
EXCEL_PATH = DATA_DIR / f"{PROJECT_NAME}_data.xlsx"
DB_PATH = DATA_DIR / "app.db"
VIEW_CSV_PATH = DATA_DIR / "vw_attendance_analysis.csv"
REPORT_PATH = DATA_DIR / "validation_report.xlsx"
REPORT_TXT = DATA_DIR / "validation_report.txt"

# Diverse synthetic Indian names
FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Reyansh", "Krishna", "Ishaan",
    "Ananya", "Diya", "Aadhya", "Saanvi", "Myra", "Ira", "Kavya", "Meera",
    "Rohan", "Kabir", "Aanya", "Ishita", "Dev", "Nisha", "Rahul", "Priya",
    "Neha", "Kunal", "Tanvi", "Manav", "Ritika", "Siddharth", "Vikram", "Shreya",
    "Aryan", "Sneha", "Alok", "Pooja", "Amit", "Sunita", "Harsh", "Deepika",
    "Gaurav", "Swati", "Abhishek", "Ritu", "Varun", "Ankita", "Prateek", "Simran",
]

LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Singh", "Katiyar", "Mishra", "Yadav", "Agarwal",
    "Chauhan", "Srivastava", "Jain", "Kapoor", "Rao", "Nair", "Mehta", "Das",
    "Malhotra", "Bansal", "Saxena", "Tiwari", "Khan", "Patel", "Joshi", "Sethi",
    "Bhatia", "Reddy", "Choudhury", "Menon", "Chatterjee", "Pandey", "Kulkarni",
]

DEPARTMENTS_CONFIG = [
    {"name": "Engineering", "loc": "Bengaluru Tech Hub", "start": "09:30", "end": "18:30", "grace": 15, "late_p": 0.12},
    {"name": "Human Resources", "loc": "Noida Sector 62 HQ", "start": "09:00", "end": "18:00", "grace": 10, "late_p": 0.05},
    {"name": "Finance", "loc": "Noida Sector 16", "start": "09:00", "end": "18:00", "grace": 10, "late_p": 0.08},
    {"name": "Sales", "loc": "Gurugram CyberCity", "start": "09:30", "end": "18:30", "grace": 15, "late_p": 0.16},
    {"name": "Customer Support", "loc": "Pune Hinjewadi", "start": "08:30", "end": "17:30", "grace": 10, "late_p": 0.32},
    {"name": "Product Management", "loc": "Bengaluru Tech Hub", "start": "09:30", "end": "18:30", "grace": 15, "late_p": 0.10},
    {"name": "Quality Assurance", "loc": "Hyderabad HITEC City", "start": "09:00", "end": "18:00", "grace": 10, "late_p": 0.11},
    {"name": "Operations", "loc": "Delhi Okhla", "start": "08:00", "end": "17:00", "grace": 10, "late_p": 0.22},
]

STATUSES = [
    ("PRESENT", "Present", 1, 0, 0, 1),
    ("ABSENT", "Absent", 0, 1, 0, 1),
    ("APPROVED_LEAVE", "Approved Leave", 0, 0, 1, 1),
    ("HOLIDAY", "Holiday", 0, 0, 0, 1),
]


def iso(dt: datetime) -> str:
    return dt.isoformat(sep=" ", timespec="seconds")


def make_schema(conn: sqlite3.Connection):
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript("""
    DROP VIEW IF EXISTS vw_attendance_analysis;
    DROP TABLE IF EXISTS attendance_records;
    DROP TABLE IF EXISTS work_calendar;
    DROP TABLE IF EXISTS attendance_statuses;
    DROP TABLE IF EXISTS employees;
    DROP TABLE IF EXISTS departments;
    DROP TABLE IF EXISTS pipeline_runs;

    CREATE TABLE pipeline_runs (
        run_id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_dataset TEXT NOT NULL,
        execution_start TEXT NOT NULL,
        execution_end TEXT NOT NULL,
        status TEXT NOT NULL CHECK (status IN ('SUCCESS', 'WARNING', 'FAILURE')),
        records_loaded INTEGER NOT NULL,
        records_accepted INTEGER NOT NULL,
        records_rejected INTEGER NOT NULL,
        validation_warnings INTEGER NOT NULL,
        notes TEXT
    );

    CREATE TABLE departments (
        department_id INTEGER PRIMARY KEY CHECK (department_id > 0),
        department_name TEXT NOT NULL UNIQUE CHECK (length(trim(department_name)) > 0),
        location TEXT NOT NULL CHECK (length(trim(location)) > 0),
        is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
        created_at TEXT NOT NULL
    );

    CREATE TABLE employees (
        employee_id INTEGER PRIMARY KEY CHECK (employee_id > 0),
        employee_code TEXT NOT NULL UNIQUE CHECK (length(trim(employee_code)) > 0),
        department_id INTEGER NOT NULL,
        hire_date TEXT NOT NULL,
        employment_status TEXT NOT NULL CHECK (employment_status IN ('ACTIVE', 'INACTIVE')),
        is_active INTEGER NOT NULL CHECK (is_active IN (0, 1)),
        created_at TEXT NOT NULL,
        UNIQUE (employee_id, department_id),
        FOREIGN KEY (department_id) REFERENCES departments(department_id),
        CHECK ((employment_status = 'ACTIVE' AND is_active = 1) OR
               (employment_status = 'INACTIVE' AND is_active = 0))
    );

    CREATE TABLE attendance_statuses (
        status_code TEXT PRIMARY KEY CHECK (
            status_code IN ('PRESENT', 'ABSENT', 'APPROVED_LEAVE', 'HOLIDAY')
        ),
        status_name TEXT NOT NULL UNIQUE,
        counts_as_present INTEGER NOT NULL CHECK (counts_as_present IN (0, 1)),
        counts_as_absence INTEGER NOT NULL CHECK (counts_as_absence IN (0, 1)),
        is_leave INTEGER NOT NULL CHECK (is_leave IN (0, 1)),
        is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1))
    );

    CREATE TABLE work_calendar (
        calendar_date TEXT NOT NULL,
        department_id INTEGER NOT NULL,
        is_working_day INTEGER NOT NULL CHECK (is_working_day IN (0, 1)),
        scheduled_start_time TEXT,
        scheduled_end_time TEXT,
        grace_minutes INTEGER NOT NULL DEFAULT 10 CHECK (grace_minutes BETWEEN 0 AND 120),
        day_type TEXT NOT NULL CHECK (day_type IN ('WORKING', 'WEEKLY_OFF', 'HOLIDAY', 'SPECIAL')),
        calendar_note TEXT,
        PRIMARY KEY (calendar_date, department_id),
        FOREIGN KEY (department_id) REFERENCES departments(department_id),
        CHECK (
          (is_working_day = 1 AND day_type IN ('WORKING', 'SPECIAL')
           AND scheduled_start_time IS NOT NULL AND scheduled_end_time IS NOT NULL)
          OR
          (is_working_day = 0 AND day_type IN ('WEEKLY_OFF', 'HOLIDAY'))
        )
    );

    CREATE TABLE attendance_records (
        attendance_id INTEGER PRIMARY KEY CHECK (attendance_id > 0),
        employee_id INTEGER NOT NULL,
        department_id INTEGER NOT NULL,
        attendance_date TEXT NOT NULL,
        status_code TEXT NOT NULL,
        check_in_time TEXT,
        check_out_time TEXT,
        source_label TEXT NOT NULL CHECK (source_label IN ('SYNTHETIC_IMPORT', 'SYNTHETIC_MANUAL')),
        record_note TEXT,
        created_at TEXT NOT NULL,
        UNIQUE (employee_id, attendance_date),
        FOREIGN KEY (employee_id, department_id)
          REFERENCES employees(employee_id, department_id),
        FOREIGN KEY (attendance_date, department_id)
          REFERENCES work_calendar(calendar_date, department_id),
        FOREIGN KEY (status_code) REFERENCES attendance_statuses(status_code),
        CHECK (check_in_time IS NULL OR length(check_in_time) = 5),
        CHECK (check_out_time IS NULL OR length(check_out_time) = 5),
        CHECK (check_in_time IS NULL OR check_out_time IS NULL OR check_out_time >= check_in_time),
        CHECK (
          (status_code = 'PRESENT' AND check_in_time IS NOT NULL)
          OR status_code IN ('ABSENT', 'APPROVED_LEAVE', 'HOLIDAY')
        )
    );

    CREATE VIEW vw_attendance_analysis AS
    SELECT
        ar.attendance_id,
        e.employee_code,
        e.employee_id,
        e.hire_date,
        e.employment_status,
        e.is_active AS employee_is_active,
        d.department_id,
        d.department_name,
        d.location,
        d.is_active AS department_is_active,
        ar.attendance_date,
        strftime('%Y', ar.attendance_date) AS attendance_year,
        strftime('%m', ar.attendance_date) AS attendance_month,
        strftime('%Y-%m', ar.attendance_date) AS attendance_year_month,
        strftime('%w', ar.attendance_date) AS weekday_number,
        CASE strftime('%w', ar.attendance_date)
          WHEN '0' THEN 'Sunday' WHEN '1' THEN 'Monday'
          WHEN '2' THEN 'Tuesday' WHEN '3' THEN 'Wednesday'
          WHEN '4' THEN 'Thursday' WHEN '5' THEN 'Friday'
          WHEN '6' THEN 'Saturday' END AS weekday_name,
        wc.is_working_day,
        wc.day_type,
        wc.scheduled_start_time,
        wc.scheduled_end_time,
        wc.grace_minutes,
        ar.status_code,
        s.status_name,
        s.counts_as_present,
        s.counts_as_absence,
        s.is_leave,
        ar.check_in_time,
        ar.check_out_time,
        CASE WHEN ar.check_in_time IS NOT NULL
          THEN (CAST(substr(ar.check_in_time,1,2) AS INTEGER) * 60
              + CAST(substr(ar.check_in_time,4,2) AS INTEGER))
             - (CAST(substr(wc.scheduled_start_time,1,2) AS INTEGER) * 60
              + CAST(substr(wc.scheduled_start_time,4,2) AS INTEGER))
          ELSE NULL END AS arrival_delay_minutes,
        CASE WHEN ar.check_in_time IS NOT NULL AND wc.scheduled_start_time IS NOT NULL
          AND (CAST(substr(ar.check_in_time,1,2) AS INTEGER) * 60
             + CAST(substr(ar.check_in_time,4,2) AS INTEGER))
             > (CAST(substr(wc.scheduled_start_time,1,2) AS INTEGER) * 60
              + CAST(substr(wc.scheduled_start_time,4,2) AS INTEGER))
              + wc.grace_minutes THEN 1 ELSE 0 END AS is_late,
        CASE WHEN ar.check_in_time IS NOT NULL AND ar.check_out_time IS NOT NULL
          THEN (CAST(substr(ar.check_out_time,1,2) AS INTEGER) * 60
              + CAST(substr(ar.check_out_time,4,2) AS INTEGER))
             - (CAST(substr(ar.check_in_time,1,2) AS INTEGER) * 60
              + CAST(substr(ar.check_in_time,4,2) AS INTEGER))
          ELSE NULL END AS elapsed_duration_minutes,
        ar.source_label,
        ar.record_note,
        ar.created_at
    FROM attendance_records ar
    JOIN employees e ON e.employee_id = ar.employee_id
                    AND e.department_id = ar.department_id
    JOIN departments d ON d.department_id = ar.department_id
    JOIN work_calendar wc ON wc.calendar_date = ar.attendance_date
                         AND wc.department_id = ar.department_id
    JOIN attendance_statuses s ON s.status_code = ar.status_code;
    """)


def generate_rows():
    now = datetime(2026, 11, 19, 10, 0, 0)

    # 1. Departments (8 units)
    departments = []
    for i, cfg in enumerate(DEPARTMENTS_CONFIG, 1):
        departments.append({
            "department_id": i,
            "department_name": cfg["name"],
            "location": cfg["loc"],
            "is_active": 1,
            "created_at": iso(now),
        })

    # 2. Employees (120 employees: 15 per department)
    employees = []
    used_names = set()
    emp_id = 1
    for dept_id in range(1, len(DEPARTMENTS_CONFIG) + 1):
        for _ in range(15):
            while True:
                fn = random.choice(FIRST_NAMES)
                ln = random.choice(LAST_NAMES)
                full_name = f"{fn} {ln}"
                if full_name not in used_names:
                    used_names.add(full_name)
                    break
            hire_y = random.randint(2021, 2025)
            hire_m = random.randint(1, 12)
            hire_d = random.randint(1, 28)
            employees.append({
                "employee_id": emp_id,
                "employee_code": f"EMP{emp_id:04d}",
                "department_id": dept_id,
                "hire_date": date(hire_y, hire_m, hire_d).isoformat(),
                "employment_status": "ACTIVE",
                "is_active": 1,
                "created_at": iso(now),
                "_display_name": full_name,
            })
            emp_id += 1

    # 3. Statuses (4 verified statuses)
    statuses = [
        {"status_code": x[0], "status_name": x[1], "counts_as_present": x[2],
         "counts_as_absence": x[3], "is_leave": x[4], "is_active": x[5]}
        for x in STATUSES
    ]

    # 4. Work Calendar (31 calendar days of October 2026 for 8 departments = 248 records)
    start_date = date(2026, 10, 1)
    all_dates = [start_date + timedelta(days=i) for i in range(31)]
    holidays = {date(2026, 10, 2): "Gandhi Jayanti", date(2026, 10, 20): "Dussehra / Maha Navami"}

    calendar = []
    working_dates = []
    for d in all_dates:
        is_weekend = d.weekday() >= 5
        is_holiday = d in holidays

        if is_holiday:
            is_work = 0
            d_type = "HOLIDAY"
            note = holidays[d]
        elif is_weekend:
            is_work = 0
            d_type = "WEEKLY_OFF"
            note = "Weekly off"
        else:
            is_work = 1
            d_type = "WORKING"
            note = None
            working_dates.append(d)

        for dept_idx, cfg in enumerate(DEPARTMENTS_CONFIG, 1):
            calendar.append({
                "calendar_date": d.isoformat(),
                "department_id": dept_idx,
                "is_working_day": is_work,
                "scheduled_start_time": cfg["start"] if is_work else None,
                "scheduled_end_time": cfg["end"] if is_work else None,
                "grace_minutes": cfg["grace"],
                "day_type": d_type,
                "calendar_note": note,
            })

    # 5. Attendance Records (120 employees x 20 working days = 2,400 records)
    facts = []
    attendance_id = 1
    # Specific pre-planned missing check-out IDs (~2.3% to 2.5% missing rate: 55 records out of 2,400)
    missing_checkout_indices = set(random.sample(range(1, 2401), 55))

    # Pre-planned outlier dates/employees
    extreme_late_cases = {
        (7, "2026-10-14"): 145,   # EMP0007 metro breakdown
        (23, "2026-10-08"): 175,  # EMP0023 highway gridlock
        (55, "2026-10-19"): 185,  # EMP0055 medical emergency
        (88, "2026-10-27"): 135,  # EMP0088 airport transit
    }
    extended_duration_cases = {
        (12, "2026-10-09"): 780,  # EMP0012 server migration
        (34, "2026-10-30"): 840,  # EMP0034 month-end financial close
        (67, "2026-10-16"): 810,  # EMP0067 critical customer escalation
        (105, "2026-10-23"): 790, # EMP0105 release testing
    }

    for d in working_dates:
        is_monday = d.weekday() == 0
        is_friday = d.weekday() == 4
        # Proximity to holidays (Oct 1 before Gandhi Jayanti; Oct 21 after Dussehra)
        is_holiday_adjacent = d in [date(2026, 10, 1), date(2026, 10, 21)]

        for emp in employees:
            dept_id = emp["department_id"]
            dept_cfg = DEPARTMENTS_CONFIG[dept_id - 1]
            dept_name = dept_cfg["name"]

            if is_holiday_adjacent:
                p_absence = 0.095
                p_leave = 0.080
            elif is_monday:
                p_absence = 0.065
                p_leave = 0.040
            else:
                p_absence = 0.025
                p_leave = 0.035

            if dept_name == "Customer Support":
                p_absence += 0.015
            elif dept_name == "Human Resources":
                p_absence = max(0.01, p_absence - 0.015)

            roll = random.random()
            if roll < p_absence:
                status = "ABSENT"
                check_in = check_out = None
                note = "Unplanned absence"
            elif roll < p_absence + p_leave:
                status = "APPROVED_LEAVE"
                check_in = check_out = None
                note = "Approved annual / personal leave"
            else:
                status = "PRESENT"
                note = None
                sched_h, sched_m = map(int, dept_cfg["start"].split(":"))
                sched_start_min = sched_h * 60 + sched_m
                grace = dept_cfg["grace"]

                p_late = dept_cfg["late_p"]
                if is_monday:
                    p_late += 0.08

                pair_key = (emp["employee_id"], d.isoformat())
                if pair_key in extreme_late_cases:
                    delay = extreme_late_cases[pair_key]
                    note = f"Documented exceptional delay (+{delay} min)"
                    check_in_min = sched_start_min + delay
                elif random.random() < p_late:
                    delay = grace + random.randint(1, 35)
                    check_in_min = sched_start_min + delay
                else:
                    delay = random.randint(-15, grace)
                    check_in_min = sched_start_min + delay

                check_in = f"{check_in_min // 60:02d}:{check_in_min % 60:02d}"

                if pair_key in extended_duration_cases:
                    duration = extended_duration_cases[pair_key]
                    note = f"Authorized extended shift ({duration} min)"
                elif is_friday:
                    duration = random.randint(460, 510)
                else:
                    duration = random.randint(480, 540)

                check_out_min = min(check_in_min + duration, 23 * 60 + 55)
                check_out = f"{check_out_min // 60:02d}:{check_out_min % 60:02d}"

            if status == "PRESENT" and attendance_id in missing_checkout_indices:
                check_out = None
                note = "Missing punch-out (biometric gate timeout)"

            facts.append({
                "attendance_id": attendance_id,
                "employee_id": emp["employee_id"],
                "department_id": dept_id,
                "attendance_date": d.isoformat(),
                "status_code": status,
                "check_in_time": check_in,
                "check_out_time": check_out,
                "source_label": "SYNTHETIC_IMPORT" if attendance_id % 4 != 0 else "SYNTHETIC_MANUAL",
                "record_note": note,
                "created_at": iso(now + timedelta(seconds=attendance_id)),
            })
            attendance_id += 1

    return departments, employees, statuses, calendar, facts, working_dates


def insert_rows(conn: sqlite3.Connection, table: str, rows: list[dict], columns: list[str]):
    placeholders = ",".join(["?"] * len(columns))
    col_sql = ",".join(columns)
    values = [[row.get(c) for c in columns] for row in rows]
    conn.executemany(f"INSERT INTO {table} ({col_sql}) VALUES ({placeholders})", values)


def validate(conn, tables, duplicate_candidates):
    counts = {}
    for table in tables:
        counts[table] = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

    fk_rows = conn.execute("PRAGMA foreign_key_check").fetchall()
    check_rows = []
    check_rows.append(("department_count", counts["departments"], 8, counts["departments"] == 8))
    check_rows.append(("employee_count", counts["employees"], 120, counts["employees"] == 120))
    check_rows.append(("calendar_rows", counts["work_calendar"], 248, counts["work_calendar"] == 248))
    check_rows.append(("attendance_rows", counts["attendance_records"], 2400, counts["attendance_records"] == 2400))
    check_rows.append(("grace_minutes_range", conn.execute("SELECT COUNT(*) FROM work_calendar WHERE grace_minutes NOT BETWEEN 0 AND 120").fetchone()[0], 0, True))
    check_rows.append(("status_allowed_values", conn.execute("SELECT COUNT(*) FROM attendance_records WHERE status_code NOT IN ('PRESENT','ABSENT','APPROVED_LEAVE','HOLIDAY')").fetchone()[0], 0, True))
    check_rows.append(("invalid_clock_shape", conn.execute("""
        SELECT COUNT(*) FROM attendance_records
        WHERE (check_in_time IS NOT NULL AND (length(check_in_time) != 5 OR substr(check_in_time,3,1) != ':'))
           OR (check_out_time IS NOT NULL AND (length(check_out_time) != 5 OR substr(check_out_time,3,1) != ':'))
    """).fetchone()[0], 0, True))
    check_rows.append(("duplicate_employee_date_keys", conn.execute("""
        SELECT COUNT(*) FROM (
          SELECT employee_id, attendance_date, COUNT(*) c
          FROM attendance_records GROUP BY employee_id, attendance_date HAVING c > 1
        )
    """).fetchone()[0], 0, True))
    check_rows.append(("foreign_key_violations", len(fk_rows), 0, len(fk_rows) == 0))
    
    view_cols = len([x[1] for x in conn.execute("PRAGMA table_info(vw_attendance_analysis)").fetchall()])
    check_rows.append(("joined_view_columns", view_cols, 34, view_cols == 34))
    check_rows.append(("duplicate_candidates_rejected", duplicate_candidates, 3, duplicate_candidates == 3))

    missing_checkout = conn.execute("""
        SELECT COUNT(*) FROM attendance_records
        WHERE status_code='PRESENT' AND check_out_time IS NULL
    """).fetchone()[0]
    total_present = conn.execute("SELECT COUNT(*) FROM attendance_records WHERE status_code='PRESENT'").fetchone()[0]
    check_rows.append(("missing_checkout_rate", missing_checkout, "2-3% of present records", 0.02 <= missing_checkout / total_present <= 0.03))

    return counts, fk_rows, check_rows


def main():
    departments, employees, statuses, calendar, facts, observation_dates = generate_rows()

    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    make_schema(conn)

    insert_rows(conn, "departments", departments,
                ["department_id", "department_name", "location", "is_active", "created_at"])
    insert_rows(conn, "employees", employees,
                ["employee_id", "employee_code", "department_id", "hire_date", "employment_status", "is_active", "created_at"])
    insert_rows(conn, "attendance_statuses", statuses,
                ["status_code", "status_name", "counts_as_present", "counts_as_absence", "is_leave", "is_active"])
    insert_rows(conn, "work_calendar", calendar,
                ["calendar_date", "department_id", "is_working_day", "scheduled_start_time", "scheduled_end_time", "grace_minutes", "day_type", "calendar_note"])
    insert_rows(conn, "attendance_records", facts,
                ["attendance_id", "employee_id", "department_id", "attendance_date", "status_code", "check_in_time", "check_out_time", "source_label", "record_note", "created_at"])
    conn.commit()

    conn.execute("""
        INSERT INTO pipeline_runs (
            source_dataset, execution_start, execution_end, status,
            records_loaded, records_accepted, records_rejected, validation_warnings, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "SYNTHETIC_WORKFORCE_INGESTION_OCT2026",
        "2026-11-19 10:00:00",
        "2026-11-19 10:00:05",
        "SUCCESS",
        len(facts), len(facts), 0, 51,
        "Canonical 2,400-record batch successfully ingested into schema."
    ))
    conn.commit()

    # Demonstrate 3 duplicate candidates: SQLite UNIQUE constraint rejects them.
    duplicate_candidates = 0
    for fact in facts[:3]:
        try:
            conn.execute("""
                INSERT INTO attendance_records
                (attendance_id, employee_id, department_id, attendance_date, status_code,
                 check_in_time, check_out_time, source_label, record_note, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                90000 + fact["attendance_id"], fact["employee_id"], fact["department_id"],
                fact["attendance_date"], fact["status_code"], fact["check_in_time"],
                fact["check_out_time"], fact["source_label"], "Duplicate candidate rejected",
                fact["created_at"]
            ))
            conn.commit()
        except sqlite3.IntegrityError:
            duplicate_candidates += 1
            conn.rollback()

    table_names = ["departments", "employees", "attendance_statuses", "work_calendar", "attendance_records"]
    counts, fk_rows, checks = validate(conn, table_names, duplicate_candidates)

    frames = {}
    for table in table_names:
        frames[table] = pd.read_sql_query(f"SELECT * FROM {table}", conn)
        frames[table].to_csv(DATA_DIR / f"{table}.csv", index=False, encoding="utf-8-sig")

    employee_labels = pd.DataFrame([
        {"employee_code": e["employee_code"], "synthetic_display_name": e["_display_name"]}
        for e in employees
    ])

    view_df = pd.read_sql_query("SELECT * FROM vw_attendance_analysis", conn)
    view_df.to_csv(VIEW_CSV_PATH, index=False, encoding="utf-8-sig")

    with pd.ExcelWriter(EXCEL_PATH, engine="openpyxl") as writer:
        for table, frame in frames.items():
            frame.to_excel(writer, sheet_name=table[:31], index=False)
        employee_labels.to_excel(writer, sheet_name="Employee_Names", index=False)
        view_df.head(1000).to_excel(writer, sheet_name="Unified_View_Sample", index=False)

    conn.close()
    print("Canonical dataset generation complete.")
    print(f"Database: {DB_PATH}")
    print(f"View CSV: {VIEW_CSV_PATH}")
    print(f"Excel: {EXCEL_PATH}")
    print(f"Row counts: {counts}")


if __name__ == "__main__":
    main()
