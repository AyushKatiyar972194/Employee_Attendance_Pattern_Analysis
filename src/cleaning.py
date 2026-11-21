"""Data cleaning for P070 attendance data.

clean_attendance_data(df) returns a cleaned copy:
  - Removes rows with invalid status codes
  - Removes exact duplicate (employee_id, attendance_date) rows (keeps first)
  - Preserves missing check-out times as NaN (never fabricates)
  - Ensures consistent datetime types
"""
from __future__ import annotations

import pandas as pd

from src.config import VALID_STATUSES


def clean_attendance_data(df: pd.DataFrame) -> pd.DataFrame:
    """Return a cleaned copy of the attendance DataFrame.

    Rules:
    1. Keep only rows with valid status codes.
    2. Drop exact duplicate (employee_id, attendance_date) rows, keeping first.
    3. Preserve missing check_out_time as NaN — never fabricate a checkout.
    4. Ensure attendance_date is datetime.
    """
    cleaned = df.copy()

    # 1. Filter to valid statuses
    cleaned = cleaned[cleaned["status_code"].isin(VALID_STATUSES)]

    # 2. Drop duplicate employee/date combos (keep first occurrence)
    if {"employee_id", "attendance_date"}.issubset(cleaned.columns):
        cleaned = cleaned.drop_duplicates(
            subset=["employee_id", "attendance_date"], keep="first"
        )

    # 3. Ensure attendance_date is datetime
    if "attendance_date" in cleaned.columns:
        cleaned["attendance_date"] = pd.to_datetime(cleaned["attendance_date"])

    # 4. Reset index for clean downstream use
    cleaned = cleaned.reset_index(drop=True)

    return cleaned
