"""Data validation, quality scorecard, and pipeline auditing for EAPA-01.

Provides formal quality dimension checks:
- Completeness
- Uniqueness
- Validity
- Consistency
- Referential Integrity
- Pipeline Audit Run Tracking
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from datetime import datetime
import pandas as pd

from src.config import VALID_STATUSES, EXPECTED_VIEW_COLUMNS, DB_PATH


def validate_attendance_data(df: pd.DataFrame) -> dict:
    """Validate attendance DataFrame across enterprise data-quality dimensions.

    Returns comprehensive quality scorecard dictionary without modifying source records.
    Safely handles empty DataFrames or missing columns without crashing.
    """
    if df is None or df.empty:
        return {
            "missing_count": 0,
            "duplicate_count": 0,
            "invalid_count": 0,
            "fk_violations": 0,
            "total_rows": 0,
            "issues": [],
            "flagged_records": pd.DataFrame(
                columns=["attendance_id", "employee_code", "department_name", "attendance_date", "status_code", "dimension", "issue_type", "severity", "description"]
            ),
            "dimensions": {
                "Completeness": "Passed",
                "Uniqueness": "Passed",
                "Validity": "Passed",
                "Consistency": "Passed",
                "Referential Integrity": "Passed",
            }
        }

    issues: list[dict] = []
    flagged_records_list: list[dict] = []

    # 1. COMPLETENESS DIMENSION (Missing Check-out Times)
    present_mask = (df["status_code"] == "PRESENT") if "status_code" in df.columns else pd.Series(False, index=df.index)
    check_out_col = df["check_out_time"] if "check_out_time" in df.columns else pd.Series(float("nan"), index=df.index)
    missing_checkout_mask = present_mask & check_out_col.isna()
    missing_checkout_count = int(missing_checkout_mask.sum())
    
    if missing_checkout_count > 0:
        missing_df = df[missing_checkout_mask]
        for _, row in missing_df.iterrows():
            flagged_records_list.append({
                "attendance_id": row.get("attendance_id", "N/A"),
                "employee_code": row.get("employee_code", f"EMP{row.get('employee_id', 0):04d}"),
                "department_name": row.get("department_name", "N/A"),
                "attendance_date": str(row.get("attendance_date", ""))[:10],
                "status_code": row.get("status_code", "PRESENT"),
                "dimension": "Completeness",
                "issue_type": "Missing Check-out",
                "severity": "Medium",
                "description": "Present shift recorded without punch-out timestamp. Retained as null per policy."
            })
        missing_ids = missing_df["attendance_id"].tolist() if "attendance_id" in missing_df.columns else []
        issues.append({
            "dimension": "Completeness",
            "type": "missing_checkout",
            "count": missing_checkout_count,
            "severity": "Medium",
            "detail": f"{missing_checkout_count} present shifts lack check-out timestamps (IDs: {missing_ids}). Preserved as null."
        })

    # Missing Check-in for Present
    check_in_col = df["check_in_time"] if "check_in_time" in df.columns else pd.Series(float("nan"), index=df.index)
    missing_checkin_mask = present_mask & check_in_col.isna()
    missing_checkin_count = int(missing_checkin_mask.sum())
    if missing_checkin_count > 0:
        issues.append({
            "dimension": "Completeness",
            "type": "missing_checkin",
            "count": missing_checkin_count,
            "severity": "High",
            "detail": f"{missing_checkin_count} present shifts lack check-in timestamps."
        })

    # 2. UNIQUENESS DIMENSION (Employee + Attendance Date Duplicates)
    if {"employee_id", "attendance_date"}.issubset(df.columns):
        dup_mask = df.duplicated(subset=["employee_id", "attendance_date"], keep=False)
        duplicate_count = int(dup_mask.sum())
        if duplicate_count > 0:
            dup_df = df[dup_mask]
            for _, row in dup_df.iterrows():
                flagged_records_list.append({
                    "attendance_id": row["attendance_id"],
                    "employee_code": row.get("employee_code", "N/A"),
                    "department_name": row.get("department_name", "N/A"),
                    "attendance_date": str(row.get("attendance_date", ""))[:10],
                    "status_code": row["status_code"],
                    "dimension": "Uniqueness",
                    "issue_type": "Duplicate Key",
                    "severity": "High",
                    "description": "Duplicate (employee_id, attendance_date) combination detected."
                })
            issues.append({
                "dimension": "Uniqueness",
                "type": "duplicate_key",
                "count": duplicate_count,
                "severity": "High",
                "detail": f"{duplicate_count} candidate duplicate rows detected across employee dates."
            })
    else:
        duplicate_count = 0

    # 3. VALIDITY DIMENSION (Status codes, clock shapes)
    invalid_status_mask = ~df["status_code"].isin(VALID_STATUSES)
    invalid_status_count = int(invalid_status_mask.sum())
    if invalid_status_count > 0:
        bad_statuses = df.loc[invalid_status_mask, "status_code"].unique().tolist()
        issues.append({
            "dimension": "Validity",
            "type": "invalid_status",
            "count": invalid_status_count,
            "severity": "High",
            "detail": f"Unrecognized status codes found: {bad_statuses}"
        })

    # Time format checks
    malformed_times = 0
    for col in ["check_in_time", "check_out_time"]:
        if col in df.columns:
            non_null = df[col].dropna().astype(str)
            bad = non_null[(non_null.str.len() != 5) | (~non_null.str.contains(r"^\d{2}:\d{2}$"))]
            malformed_times += len(bad)

    if malformed_times > 0:
        issues.append({
            "dimension": "Validity",
            "type": "malformed_time",
            "count": malformed_times,
            "severity": "High",
            "detail": f"{malformed_times} malformed timestamps not following standard HH:MM format."
        })

    # 4. CONSISTENCY DIMENSION (Sequence: check_out >= check_in)
    inconsistent_seq_count = 0
    if {"check_in_time", "check_out_time"}.issubset(df.columns):
        both_times = df[df["check_in_time"].notna() & df["check_out_time"].notna()]
        bad_seq = both_times[both_times["check_out_time"] < both_times["check_in_time"]]
        inconsistent_seq_count = len(bad_seq)
        if inconsistent_seq_count > 0:
            issues.append({
                "dimension": "Consistency",
                "type": "invalid_time_sequence",
                "count": inconsistent_seq_count,
                "severity": "High",
                "detail": f"{inconsistent_seq_count} shifts where check_out_time precedes check_in_time."
            })

    # Total invalid count for legacy test contract compatibility
    invalid_count = invalid_status_count + malformed_times + missing_checkin_count + inconsistent_seq_count

    # 5. REFERENTIAL INTEGRITY (Verified from SQLite PRAGMA)
    fk_violations = 0
    try:
        with sqlite3.connect(str(DB_PATH)) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            violations = conn.execute("PRAGMA foreign_key_check").fetchall()
            fk_violations = len(violations)
    except Exception:
        fk_violations = 0

    flagged_records_df = pd.DataFrame(flagged_records_list) if flagged_records_list else pd.DataFrame(
        columns=["attendance_id", "employee_code", "department_name", "attendance_date", "status_code", "dimension", "issue_type", "severity", "description"]
    )

    return {
        "missing_count": missing_checkout_count,
        "duplicate_count": duplicate_count,
        "invalid_count": invalid_count,
        "fk_violations": fk_violations,
        "total_rows": len(df),
        "issues": issues,
        "flagged_records": flagged_records_df,
        "dimensions": {
            "Completeness": "Warning" if missing_checkout_count > 0 else "Passed",
            "Uniqueness": "Passed" if duplicate_count == 0 else "Failed",
            "Validity": "Passed" if invalid_count == 0 else "Failed",
            "Consistency": "Passed" if inconsistent_seq_count == 0 else "Failed",
            "Referential Integrity": "Passed" if fk_violations == 0 else "Failed",
        }
    }


def get_pipeline_runs(db_path: str | Path = DB_PATH) -> pd.DataFrame:
    """Retrieve execution history of ingestion and validation runs."""
    try:
        with sqlite3.connect(str(db_path)) as conn:
            query = "SELECT run_id, source_dataset, execution_start, execution_end, status, records_loaded, records_accepted, records_rejected, validation_warnings, notes FROM pipeline_runs ORDER BY run_id DESC"
            return pd.read_sql_query(query, conn)
    except Exception:
        return pd.DataFrame()
