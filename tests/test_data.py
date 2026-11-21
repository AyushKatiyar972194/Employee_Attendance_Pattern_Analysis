"""Technical data-layer tests for P070.

Expected Step 15 module contract:
- src.data_loader.load_attendance_data(db_path) -> pandas.DataFrame
- src.validation.validate_attendance_data(df) -> dict with issue counts/details
- src.cleaning.clean_attendance_data(df) -> pandas.DataFrame

These tests intentionally define the expected contract and may fail until Step 15
implements the corresponding modules.
"""
from pathlib import Path
import sqlite3

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "data" / "app.db"


def test_database_file_exists():
    assert DB_PATH.exists(), "Expected synthetic SQLite database at data/app.db"


def test_data_loads_from_sqlite():
    from src.data_loader import load_attendance_data

    df = load_attendance_data(DB_PATH)
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert {"attendance_id", "employee_code", "department_name", "attendance_date",
            "status_code", "check_in_time", "check_out_time"}.issubset(df.columns)


def test_base_table_row_counts_match_generated_dataset():
    with sqlite3.connect(DB_PATH) as conn:
        expected = {
            "departments": 8,
            "employees": 120,
            "attendance_statuses": 4,
            "work_calendar": 248,
            "attendance_records": 2400,
        }
        for table, count in expected.items():
            actual = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            assert actual == count, f"{table}: expected {count}, got {actual}"


def test_joined_view_has_30_to_40_columns():
    with sqlite3.connect(DB_PATH) as conn:
        columns = conn.execute("PRAGMA table_info(vw_attendance_analysis)").fetchall()
    assert 30 <= len(columns) <= 40
    assert len(columns) == 34


def test_primary_keys_are_unique_and_non_null():
    with sqlite3.connect(DB_PATH) as conn:
        checks = [
            ("departments", "department_id"),
            ("employees", "employee_id"),
            ("attendance_statuses", "status_code"),
            ("attendance_records", "attendance_id"),
        ]
        for table, key in checks:
            total = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            distinct = conn.execute(f"SELECT COUNT(DISTINCT {key}) FROM {table}").fetchone()[0]
            nulls = conn.execute(f"SELECT COUNT(*) FROM {table} WHERE {key} IS NULL").fetchone()[0]
            assert total == distinct
            assert nulls == 0


def test_composite_calendar_primary_key_is_unique():
    with sqlite3.connect(DB_PATH) as conn:
        duplicates = conn.execute("""
            SELECT COUNT(*) FROM (
              SELECT calendar_date, department_id, COUNT(*) c
              FROM work_calendar GROUP BY calendar_date, department_id HAVING c > 1
            )
        """).fetchone()[0]
    assert duplicates == 0


def test_foreign_keys_are_valid():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        violations = conn.execute("PRAGMA foreign_key_check").fetchall()
    assert violations == []


def test_attendance_allowed_values_and_time_ranges():
    with sqlite3.connect(DB_PATH) as conn:
        invalid_status = conn.execute("""
            SELECT COUNT(*) FROM attendance_records
            WHERE status_code NOT IN ('PRESENT','ABSENT','APPROVED_LEAVE','HOLIDAY')
        """).fetchone()[0]
        invalid_grace = conn.execute("""
            SELECT COUNT(*) FROM work_calendar WHERE grace_minutes NOT BETWEEN 0 AND 120
        """).fetchone()[0]
        malformed_times = conn.execute("""
            SELECT COUNT(*) FROM attendance_records
            WHERE (check_in_time IS NOT NULL AND
                   (length(check_in_time) != 5 OR substr(check_in_time,3,1) != ':'))
               OR (check_out_time IS NOT NULL AND
                   (length(check_out_time) != 5 OR substr(check_out_time,3,1) != ':'))
        """).fetchone()[0]
    assert invalid_status == 0
    assert invalid_grace == 0
    assert malformed_times == 0


def test_duplicate_employee_date_rows_do_not_exist():
    with sqlite3.connect(DB_PATH) as conn:
        duplicates = conn.execute("""
            SELECT COUNT(*) FROM (
              SELECT employee_id, attendance_date, COUNT(*) c
              FROM attendance_records GROUP BY employee_id, attendance_date HAVING c > 1
            )
        """).fetchone()[0]
    assert duplicates == 0


def test_cleaning_preserves_valid_rows_and_flags_missing_checkout():
    from src.data_loader import load_attendance_data
    from src.cleaning import clean_attendance_data

    raw = load_attendance_data(DB_PATH)
    cleaned = clean_attendance_data(raw)
    assert len(cleaned) <= len(raw)
    assert "check_out_time" in cleaned.columns
    # Missing check-outs should not be fabricated as a real clock time.
    missing_checkout = cleaned.loc[
        (cleaned["status_code"] == "PRESENT") & cleaned["check_out_time"].isna()
    ]
    assert len(missing_checkout) >= 1


def test_validation_reports_documented_quality_issues():
    from src.data_loader import load_attendance_data
    from src.validation import validate_attendance_data

    df = load_attendance_data(DB_PATH)
    report = validate_attendance_data(df)
    assert isinstance(report, dict)
    # Contract: report should expose at least missing, duplicate and invalid counts.
    assert {"missing_count", "duplicate_count", "invalid_count"}.issubset(report.keys())
    assert report["missing_count"] >= 1
    assert report["duplicate_count"] == 0


def test_ingest_punch_records_appends_and_updates_metrics():
    """Verify that ingest_punch_records properly formats, maps foreign keys, and appends rows."""
    from src.data_loader import load_attendance_data, ingest_punch_records
    import pandas as pd

    df = load_attendance_data(DB_PATH)
    initial_len = len(df)
    batch = pd.DataFrame([
        {"employee_code": "EMP0001", "attendance_date": "2026-11-02", "status_code": "PRESENT", "check_in_time": "08:55:00", "check_out_time": "17:30:00"},
        {"employee_code": "EMP0066", "attendance_date": "2026-11-02", "status_code": "PRESENT", "check_in_time": "09:22:00", "check_out_time": "18:00:00"},
    ])

    updated = ingest_punch_records(df, batch)
    assert len(updated) == initial_len + 2
    assert updated.iloc[-1]["employee_code"] == "EMP0066"
    assert updated.iloc[-1]["department_name"] == "Customer Support"
    assert updated.iloc[-1]["attendance_id"] > df["attendance_id"].max()


def test_commit_punch_records_to_db_and_reset():
    """Verify that commit_punch_records_to_db persists to SQLite and reset restores canonical 2,400 rows."""
    from src.data_loader import (
        load_attendance_data,
        commit_punch_records_to_db,
        reset_database_to_canonical,
    )
    import pandas as pd

    batch = pd.DataFrame([
        {"employee_code": "EMP0001", "attendance_date": "2026-11-02", "status_code": "PRESENT", "check_in_time": "08:55", "check_out_time": "17:30"},
        {"employee_code": "EMP0002", "attendance_date": "2026-11-02", "status_code": "PRESENT", "check_in_time": "09:05", "check_out_time": "17:40"},
    ])

    reset_database_to_canonical(DB_PATH)
    try:
        inserted = commit_punch_records_to_db(DB_PATH, batch, mode="append")
        assert inserted == 2
        df_new = load_attendance_data(DB_PATH)
        assert len(df_new) == 2402

        # Test replace mode
        inserted_replace = commit_punch_records_to_db(DB_PATH, batch, mode="replace")
        assert inserted_replace == 2
        df_replaced = load_attendance_data(DB_PATH)
        assert len(df_replaced) == 2
    finally:
        reset_database_to_canonical(DB_PATH)
        df_canonical = load_attendance_data(DB_PATH)
        assert len(df_canonical) == 2400


def test_normalize_uploaded_batch_canonical_format():
    """Verify that a canonical CSV passes normalization without issues."""
    from src.data_loader import normalize_uploaded_batch
    import pandas as pd

    df = pd.DataFrame([
        {"employee_code": "EMP0001", "attendance_date": "2026-11-02", "status_code": "PRESENT", "check_in_time": "08:55", "check_out_time": "17:30"},
        {"employee_code": "EMP0002", "attendance_date": "2026-11-02", "status_code": "ABSENT", "check_in_time": None, "check_out_time": None},
    ])
    cleaned, mappings, errors = normalize_uploaded_batch(df)
    assert errors == []
    assert len(cleaned) == 2
    assert list(cleaned.columns) == ["employee_code", "attendance_date", "status_code", "check_in_time", "check_out_time"]
    assert cleaned.iloc[0]["status_code"] == "PRESENT"
    assert cleaned.iloc[1]["status_code"] == "ABSENT"


def test_normalize_uploaded_batch_with_aliases_and_omissions():
    """Verify that alternative headers (e.g. Employee Code, Date, In Time, Out Time) are mapped and status is inferred."""
    from src.data_loader import normalize_uploaded_batch
    import pandas as pd

    df = pd.DataFrame([
        {"Employee Code": "EMP0001", "Date": "02-11-2026", "In Time": "08:55 AM", "Out Time": "5:30 PM"},
        {"Employee Code": "EMP0002", "Date": "02-11-2026", "In Time": None, "Out Time": None},
    ])
    cleaned, mappings, errors = normalize_uploaded_batch(df)
    assert errors == []
    assert len(cleaned) == 2
    assert cleaned.iloc[0]["employee_code"] == "EMP0001"
    assert cleaned.iloc[0]["attendance_date"] == "2026-11-02"
    assert cleaned.iloc[0]["status_code"] == "PRESENT"
    assert cleaned.iloc[0]["check_in_time"] == "08:55"
    assert cleaned.iloc[0]["check_out_time"] == "17:30"
    assert cleaned.iloc[1]["status_code"] == "ABSENT"
    assert any("Mapped column 'Employee Code'" in m for m in mappings)
    assert any("status_code" in m.lower() and "inferred" in m.lower() for m in mappings)


def test_normalize_uploaded_batch_missing_required_columns_error():
    """Verify that an arbitrary unrelated CSV returns informative errors."""
    from src.data_loader import normalize_uploaded_batch
    import pandas as pd

    unrelated_df = pd.DataFrame([
        {"Product": "Laptop", "Price": 1200, "Quantity": 5},
    ])
    cleaned, mappings, errors = normalize_uploaded_batch(unrelated_df)
    assert len(errors) >= 2
    assert any("employee" in e.lower() for e in errors)
    assert any("date" in e.lower() for e in errors)

