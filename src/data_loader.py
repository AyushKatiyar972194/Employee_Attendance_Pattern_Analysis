"""Load and filter attendance data from the SQLite database.

Primary function: load_attendance_data(db_path) → pandas DataFrame
from vw_attendance_analysis with all 34 columns.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config import VIEW_NAME


def load_attendance_data(db_path: str | Path) -> pd.DataFrame:
    """Load all rows from vw_attendance_analysis into a DataFrame.

    Preserves missing values (NaN/None) for nullable fields
    such as check_in_time, check_out_time, record_note, etc.
    Includes defensive fallback if SQLite is locked or unavailable.
    """
    import sqlite3
    import logging
    from pathlib import Path

    df = None
    try:
        p = Path(db_path)
        if p.exists():
            conn = sqlite3.connect(str(p), timeout=10)
            conn.execute("PRAGMA foreign_keys = ON")
            df = pd.read_sql_query(f"SELECT * FROM {VIEW_NAME}", conn)
            conn.close()
    except Exception as exc:
        logging.warning("SQLite load failed (%s). Attempting CSV fallback.", exc)

    # Fallback to pre-computed CSV view if database connection fails
    if df is None or df.empty:
        csv_fallback = Path("data") / "vw_attendance_analysis.csv"
        if csv_fallback.exists():
            try:
                df = pd.read_csv(csv_fallback)
            except Exception as exc:
                logging.error("CSV fallback load failed: %s", exc)
                df = pd.DataFrame()
        else:
            df = pd.DataFrame()

    # Ensure attendance_date is proper datetime for filtering
    if not df.empty and "attendance_date" in df.columns:
        df["attendance_date"] = pd.to_datetime(df["attendance_date"], errors="coerce")

    return df


def get_available_observation_dates(db_path: str | Path) -> list[str]:
    """Return the distinct observation dates present in attendance_records."""
    import sqlite3
    import logging
    try:
        conn = sqlite3.connect(str(db_path), timeout=5)
        rows = conn.execute(
            "SELECT DISTINCT attendance_date FROM attendance_records "
            "ORDER BY attendance_date"
        ).fetchall()
        conn.close()
        return [r[0] for r in rows]
    except Exception as exc:
        logging.warning("Failed to fetch observation dates from DB: %s", exc)
        return []


def filter_data(
    df: pd.DataFrame,
    department: str = "All",
    start_date=None,
    end_date=None,
    status: str = "All",
) -> pd.DataFrame:
    """Apply shared sidebar filters to the attendance DataFrame safely."""
    if df is None or df.empty:
        return pd.DataFrame(columns=df.columns if df is not None else [])

    filtered = df.copy()

    if department and department != "All" and "department_name" in filtered.columns:
        filtered = filtered[filtered["department_name"] == department]

    if start_date is not None and "attendance_date" in filtered.columns:
        try:
            s_dt = pd.to_datetime(start_date)
            filtered = filtered[filtered["attendance_date"] >= s_dt]
        except (ValueError, TypeError):
            pass

    if end_date is not None and "attendance_date" in filtered.columns:
        try:
            e_dt = pd.to_datetime(end_date)
            filtered = filtered[filtered["attendance_date"] <= e_dt]
        except (ValueError, TypeError):
            pass

    if status and status != "All" and "status_code" in filtered.columns:
        filtered = filtered[filtered["status_code"] == status]

    return filtered


def ingest_punch_records(current_df: pd.DataFrame, new_batch: pd.DataFrame) -> pd.DataFrame:
    """Validate, format, and append a batch of new attendance punch records into the master DataFrame."""
    if current_df is None or current_df.empty or new_batch is None or new_batch.empty:
        return current_df if current_df is not None else pd.DataFrame()

    batch = new_batch.copy()

    # 1. Lookup employee and department attributes from existing dataset
    emp_cols = ["employee_code", "employee_id", "department_id", "department_name", "location"]
    available_emp_cols = [c for c in emp_cols if c in current_df.columns]
    emp_lookup = current_df[available_emp_cols].drop_duplicates("employee_code")

    merged = batch.merge(emp_lookup, on="employee_code", how="left")

    # 2. Assign unique sequential attendance_ids
    max_id = int(current_df["attendance_id"].max()) if "attendance_id" in current_df.columns and not current_df["attendance_id"].dropna().empty else 2400
    merged["attendance_id"] = range(max_id + 1, max_id + 1 + len(merged))

    # 3. Format calendar dates and timestamps
    merged["attendance_date"] = pd.to_datetime(merged["attendance_date"], errors="coerce")
    merged["attendance_year"] = merged["attendance_date"].dt.year
    merged["attendance_month"] = merged["attendance_date"].dt.month
    merged["attendance_year_month"] = merged["attendance_date"].dt.strftime("%Y-%m")
    merged["weekday_number"] = merged["attendance_date"].dt.weekday
    merged["weekday_name"] = merged["attendance_date"].dt.strftime("%A")
    merged["is_working_day"] = 1
    merged["day_type"] = "REGULAR_WORKDAY"
    merged["scheduled_start_time"] = "09:00:00"
    merged["scheduled_end_time"] = "17:00:00"
    merged["grace_minutes"] = 10

    # 4. Status mapping flags
    merged["counts_as_present"] = (merged["status_code"] == "PRESENT").astype(int)
    merged["counts_as_absence"] = (merged["status_code"] == "ABSENT").astype(int)
    merged["is_leave"] = (merged["status_code"] == "APPROVED_LEAVE").astype(int)

    # 5. Concatenate and return complete updated DataFrame
    combined = pd.concat([current_df, merged], ignore_index=True)
    return combined


COLUMN_ALIASES = {
    "employee_code": [
        "employee_code", "emp_code", "employee_id", "empid", "emp_id",
        "employee", "emp", "code", "badge_id", "user_id", "staff_id", "worker_id"
    ],
    "attendance_date": [
        "attendance_date", "date", "shift_date", "punch_date", "day_date",
        "work_date", "log_date", "record_date", "day", "attendance_dt"
    ],
    "status_code": [
        "status_code", "status", "attendance_status", "punch_status",
        "state", "presence", "attendance"
    ],
    "check_in_time": [
        "check_in_time", "check_in", "checkin", "in_time", "intime",
        "clock_in", "clockin", "punch_in", "punchin", "in", "time_in",
        "arrival_time", "start_time", "arrival", "in_punch"
    ],
    "check_out_time": [
        "check_out_time", "check_out", "checkout", "out_time", "outtime",
        "clock_out", "clockout", "punch_out", "punchout", "out", "time_out",
        "departure_time", "end_time", "departure", "out_punch"
    ],
}


def _clean_time_string(val: any) -> str | None:
    """Standardize arbitrary time representation into HH:MM or None."""
    import re

    if val is None or pd.isna(val):
        return None
    s = str(val).strip()
    if s in ("", "-", "—", "nan", "None", "null", "nat", "NAT", "NaT"):
        return None
    if " " in s:
        parts = s.split()
        if len(parts) >= 2 and parts[-1].upper() in ("AM", "PM"):
            s = f"{parts[-2]} {parts[-1]}"
        elif len(parts) >= 2 and ":" in parts[-1]:
            s = parts[-1]

    for fmt in ("%H:%M:%S", "%H:%M", "%I:%M %p", "%I:%M:%S %p", "%I:%M%p"):
        try:
            return pd.to_datetime(s, format=fmt).strftime("%H:%M")
        except (ValueError, TypeError):
            continue

    m = re.search(r"(\d{1,2}):(\d{2})", s)
    if m:
        hh = int(m.group(1))
        mm = int(m.group(2))
        if 0 <= hh < 24 and 0 <= mm < 60:
            return f"{hh:02d}:{mm:02d}"
    return None


def _clean_date_string(val: any) -> str | None:
    """Standardize arbitrary date strings (ISO, DD-MM-YYYY, DD Mon YYYY) into YYYY-MM-DD."""
    import re

    if val is None or pd.isna(val):
        return None
    s = str(val).strip()
    if re.match(r"^\d{4}[-/]\d{1,2}[-/]\d{1,2}", s):
        p = pd.to_datetime(s, errors="coerce")
        return p.strftime("%Y-%m-%d") if pd.notna(p) else None
    if re.match(r"^\d{1,2}[-/]\d{1,2}[-/]\d{4}", s):
        p = pd.to_datetime(s, dayfirst=True, errors="coerce")
        return p.strftime("%Y-%m-%d") if pd.notna(p) else None
    p = pd.to_datetime(s, errors="coerce")
    return p.strftime("%Y-%m-%d") if pd.notna(p) else None


def normalize_uploaded_batch(raw_df: pd.DataFrame) -> tuple[pd.DataFrame, list[str], list[str]]:
    """Intelligently map, clean, and validate an uploaded attendance DataFrame.

    Handles:
    - Case-insensitive & alias column matching (e.g. 'Date' -> 'attendance_date', 'In-Time' -> 'check_in_time')
    - Auto-inferring 'status_code' if omitted (PRESENT if check-in punch exists, else ABSENT)
    - Auto-filling missing 'check_out_time' as None (flagged as missing punch / pending departure)
    - Normalizing employee IDs (e.g., numeric 1 -> EMP0001)
    - Robust date parsing (YYYY-MM-DD, DD-MM-YYYY, DD Mon YYYY)
    - Standardizing timestamps to 24-hr HH:MM format

    Returns:
        tuple: (normalized_df, applied_mappings, error_messages)
    """
    if raw_df is None or raw_df.empty:
        return pd.DataFrame(), [], ["Uploaded file contains no data or could not be read."]

    df = raw_df.copy()
    mappings_applied: list[str] = []
    errors: list[str] = []

    # 1. Alias matching
    col_map: dict[str, str] = {}
    normalized_cols = {col: str(col).lower().strip().replace(" ", "_").replace("-", "_") for col in df.columns}

    for target, aliases in COLUMN_ALIASES.items():
        matched_orig = None
        for orig, norm in normalized_cols.items():
            if norm in aliases:
                matched_orig = orig
                break
        if matched_orig:
            col_map[matched_orig] = target
            if matched_orig != target:
                mappings_applied.append(f"Mapped column '{matched_orig}' ➔ '{target}'")

    # Heuristic for employee_code if not matched by name
    if "employee_code" not in col_map.values():
        for col in df.columns:
            sample = df[col].dropna().astype(str).head(10)
            if any(s.upper().startswith("EMP") for s in sample):
                col_map[col] = "employee_code"
                mappings_applied.append(f"Detected employee code column '{col}' ➔ 'employee_code'")
                break

    df = df.rename(columns=col_map)

    # 2. Required columns check (employee_code and date are mandatory; others can be inferred/defaulted)
    if "employee_code" not in df.columns:
        errors.append("Missing employee identifier. Please include a column named 'employee_code', 'Emp ID', or 'Employee'.")
    if "attendance_date" not in df.columns:
        errors.append("Missing attendance date. Please include a column named 'attendance_date', 'Date', or 'Shift Date'.")

    if errors:
        return df, mappings_applied, errors

    # 3. Clean and normalize times
    if "check_in_time" not in df.columns:
        df["check_in_time"] = None
        mappings_applied.append("Notice: 'check_in_time' column omitted; punches defaulted to None")
    else:
        df["check_in_time"] = df["check_in_time"].apply(_clean_time_string)

    if "check_out_time" not in df.columns:
        df["check_out_time"] = None
        mappings_applied.append("Notice: 'check_out_time' column omitted; shifts flagged as missing clock-out")
    else:
        df["check_out_time"] = df["check_out_time"].apply(_clean_time_string)

    # 4. Status code resolution
    if "status_code" not in df.columns:
        df["status_code"] = df["check_in_time"].apply(lambda t: "PRESENT" if pd.notna(t) and t else "ABSENT")
        mappings_applied.append("Auto-inferred 'status_code' (PRESENT if check-in punch exists, else ABSENT)")
    else:
        def clean_status(val: any, cin: any) -> str:
            if pd.isna(val) or not str(val).strip():
                return "PRESENT" if pd.notna(cin) and cin else "ABSENT"
            s = str(val).strip().upper()
            if s in ("PRESENT", "P", "1", "TRUE", "ATTENDED"):
                return "PRESENT"
            if s in ("ABSENT", "A", "0", "FALSE", "UNEXCUSED"):
                return "ABSENT"
            if s in ("APPROVED_LEAVE", "LEAVE", "L", "ON_LEAVE", "PL", "SL", "CL", "SICK_LEAVE", "CASUAL_LEAVE"):
                return "APPROVED_LEAVE"
            if s in ("HOLIDAY", "H", "OFF", "WEEKEND", "WO"):
                return "HOLIDAY"
            return "PRESENT" if pd.notna(cin) and cin else "ABSENT"

        df["status_code"] = [clean_status(s, cin) for s, cin in zip(df["status_code"], df["check_in_time"])]

    # 5. Clean employee codes (format integers to EMP####)
    def clean_emp(val: any) -> str:
        if pd.isna(val):
            return ""
        s = str(val).strip().upper()
        if s.isdigit():
            return f"EMP{int(s):04d}"
        if s.startswith("EMP") and s[3:].isdigit():
            return f"EMP{int(s[3:]):04d}"
        return s

    df["employee_code"] = df["employee_code"].apply(clean_emp)

    # 6. Clean attendance dates
    df["attendance_date"] = df["attendance_date"].apply(_clean_date_string)
    unparseable_dates = int(df["attendance_date"].isna().sum())
    if unparseable_dates > 0:
        errors.append(f"{unparseable_dates} rows contain unparseable or invalid dates.")

    result_cols = ["employee_code", "attendance_date", "status_code", "check_in_time", "check_out_time"]
    return df[result_cols], mappings_applied, errors


def commit_punch_records_to_db(db_path: str | Path, new_batch: pd.DataFrame, mode: str = "append") -> int:
    """Insert batch punch records into SQLite app.db (handling work_calendar dates and constraints).

    Parameters:
      - mode='append': Keeps existing attendance_records and appends new batch with sequential IDs.
      - mode='replace': Wipes existing attendance_records and loads only new_batch as the active audit records.

    Inserts necessary work_calendar entries for unrecorded dates and ensures all foreign key
    and check constraints (5-character times, valid status codes, SYNTHETIC_IMPORT label) are met.
    Returns the count of newly committed records.
    """
    import sqlite3

    if new_batch is None or new_batch.empty:
        return 0

    p = Path(db_path)
    if not p.exists():
        return 0

    conn = sqlite3.connect(str(p), timeout=10)
    conn.execute("PRAGMA foreign_keys = ON")

    try:
        # Ensure canonical backup tables exist before any destructive replace
        conn.execute("CREATE TABLE IF NOT EXISTS canonical_attendance_records AS SELECT * FROM attendance_records")
        conn.execute("CREATE TABLE IF NOT EXISTS canonical_work_calendar AS SELECT * FROM work_calendar")
        conn.execute("CREATE TABLE IF NOT EXISTS canonical_employees AS SELECT * FROM employees")

        # 1. Lookup employee and department IDs
        emp_df = pd.read_sql_query("SELECT employee_code, employee_id, department_id FROM employees", conn)

        # Auto-register any new employees into Operations department (dept 8) so they never fail foreign keys
        missing_emps = set(new_batch["employee_code"].dropna()) - set(emp_df["employee_code"])
        if missing_emps:
            max_emp_id = conn.execute("SELECT COALESCE(MAX(employee_id), 120) FROM employees").fetchone()[0]
            now_str = "2026-11-01 00:00:00"
            for idx, code in enumerate(sorted(missing_emps)):
                conn.execute(
                    "INSERT INTO employees (employee_id, employee_code, department_id, hire_date, employment_status, is_active, created_at) "
                    "VALUES (?, ?, 8, '2026-01-01', 'ACTIVE', 1, ?)",
                    (max_emp_id + 1 + idx, code, now_str),
                )
            emp_df = pd.read_sql_query("SELECT employee_code, employee_id, department_id FROM employees", conn)

        merged = new_batch.merge(emp_df, on="employee_code", how="inner")
        if merged.empty:
            conn.close()
            return 0

        # If replacing, clear current attendance records first
        if mode == "replace":
            conn.execute("DELETE FROM attendance_records")
            max_id = 0
        else:
            max_id = conn.execute("SELECT COALESCE(MAX(attendance_id), 2400) FROM attendance_records").fetchone()[0]

        # 2. Insert any missing calendar dates into work_calendar
        for _, row in merged[["attendance_date", "department_id"]].drop_duplicates().iterrows():
            conn.execute(
                """
                INSERT OR IGNORE INTO work_calendar (
                    calendar_date, department_id, is_working_day, scheduled_start_time,
                    scheduled_end_time, grace_minutes, day_type, calendar_note
                ) VALUES (?, ?, 1, '09:00', '17:00', 10, 'WORKING', 'Standard Workday')
                """,
                (str(row["attendance_date"]), int(row["department_id"])),
            )

        # 3. Format and insert attendance records
        records = []
        for i, row in merged.iterrows():
            cur_id = max_id + 1 + i
            raw_cin = row.get("check_in_time")
            raw_cout = row.get("check_out_time")
            cin = str(raw_cin)[:5] if pd.notna(raw_cin) and str(raw_cin).strip() and str(raw_cin).strip() not in ("None", "nan") else None
            cout = str(raw_cout)[:5] if pd.notna(raw_cout) and str(raw_cout).strip() and str(raw_cout).strip() not in ("None", "nan") else None

            # If status is ABSENT or APPROVED_LEAVE, check times must be None
            if str(row["status_code"]) in ("ABSENT", "APPROVED_LEAVE", "HOLIDAY"):
                cin = None
                cout = None

            records.append((
                cur_id,
                int(row["employee_id"]),
                int(row["department_id"]),
                str(row["attendance_date"]),
                str(row["status_code"]),
                cin,
                cout,
                "SYNTHETIC_IMPORT",
                "Batch Ingest (Replace)" if mode == "replace" else "Batch Ingest (Append)",
                f"{row['attendance_date']} 09:00:00",
            ))

        conn.executemany(
            """
            INSERT INTO attendance_records (
                attendance_id, employee_id, department_id, attendance_date,
                status_code, check_in_time, check_out_time, source_label, record_note, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            records,
        )
        conn.commit()
        return len(records)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def reset_database_to_canonical(db_path: str | Path) -> None:
    """Restore attendance_records and work_calendar back to canonical baseline (2,400 records, October 2026)."""
    import sqlite3

    p = Path(db_path)
    if not p.exists():
        return

    conn = sqlite3.connect(str(p), timeout=10)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        has_backup = conn.execute(
            "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='canonical_attendance_records'"
        ).fetchone()[0] > 0

        if has_backup:
            conn.execute("DELETE FROM attendance_records")
            conn.execute("DELETE FROM work_calendar WHERE calendar_date NOT IN (SELECT calendar_date FROM canonical_work_calendar)")
            conn.execute("INSERT OR IGNORE INTO work_calendar SELECT * FROM canonical_work_calendar")
            conn.execute("INSERT INTO attendance_records SELECT * FROM canonical_attendance_records")

            has_emp_backup = conn.execute(
                "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='canonical_employees'"
            ).fetchone()[0] > 0
            if has_emp_backup:
                conn.execute("DELETE FROM employees WHERE employee_id NOT IN (SELECT employee_id FROM canonical_employees)")
            else:
                conn.execute("DELETE FROM employees WHERE employee_id > 120")
            conn.commit()
        else:
            conn.execute("DELETE FROM attendance_records WHERE attendance_id > 2400")
            conn.execute("DELETE FROM work_calendar WHERE calendar_date > '2026-10-31'")
            conn.execute("DELETE FROM employees WHERE employee_id > 120")
            conn.commit()
    finally:
        conn.close()
