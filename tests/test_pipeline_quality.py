"""Comprehensive automated test suite for P070 data quality, pipelines, and schema integrity."""
import sqlite3
import pandas as pd
import pytest
from pathlib import Path

from src.config import DB_PATH
from src.data_loader import load_attendance_data, filter_data
from src.validation import validate_attendance_data, get_pipeline_runs
from src.cleaning import clean_attendance_data
from src.export import export_filtered_data


def test_database_connection_and_table_structure():
    """Verify that all 5 base tables exist and have expected minimum rows."""
    with sqlite3.connect(DB_PATH) as conn:
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        table_names = [t[0] for t in tables]
        assert {"departments", "employees", "attendance_statuses", "work_calendar", "attendance_records"}.issubset(table_names)


def test_pipeline_runs_logging():
    """Verify that pipeline runs table logs execution history."""
    runs = get_pipeline_runs()
    assert isinstance(runs, pd.DataFrame)
    assert not runs.empty
    assert {"run_id", "source_dataset", "status", "records_loaded", "records_accepted"}.issubset(runs.columns)
    assert runs.iloc[0]["status"] == "SUCCESS"


def test_data_quality_scorecard_dimensions():
    """Verify that validate_attendance_data returns complete dimensional audits."""
    raw = load_attendance_data(DB_PATH)
    report = validate_attendance_data(raw)
    
    assert "dimensions" in report
    dims = report["dimensions"]
    assert dims["Completeness"] == "Warning"  # Due to 7 missing checkouts
    assert dims["Uniqueness"] == "Passed"
    assert dims["Validity"] == "Passed"
    assert dims["Consistency"] == "Passed"
    assert dims["Referential Integrity"] == "Passed"
    
    flagged = report["flagged_records"]
    assert len(flagged) == 51


def test_filter_consistency_across_dimensions():
    """Verify that filtering by department and status subsets rows reliably."""
    raw = load_attendance_data(DB_PATH)
    filtered = filter_data(raw, department="Engineering", status="PRESENT")
    
    assert not filtered.empty
    assert (filtered["department_name"] == "Engineering").all()
    assert (filtered["status_code"] == "PRESENT").all()
    assert len(filtered) == 269  # 269 present shifts in Engineering


def test_csv_export_byte_stream():
    """Verify CSV byte stream generation with UTF-8 BOM encoding."""
    raw = load_attendance_data(DB_PATH).head(10)
    csv_bytes = export_filtered_data(raw)
    assert isinstance(csv_bytes, bytes)
    assert csv_bytes.startswith(b"\xef\xbb\xbf")  # UTF-8 BOM check
    assert b"attendance_id" in csv_bytes
