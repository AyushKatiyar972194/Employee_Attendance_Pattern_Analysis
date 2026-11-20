"""Centralised Metric Calculation Layer & Business Metric Catalogue for EAPA-01.

This module provides authoritative, mathematically reconciled functions for all
KPIs across Northstar Technologies Workforce Analytics dashboards.

All functions:
- Accept filtered DataFrames or raw tables
- Safely handle empty datasets (return float('nan') or 0 where appropriate)
- Strictly avoid division by zero
- Maintain 100% deterministic, testable calculations
- Reconcile identically across all pages and reports
"""
from __future__ import annotations

import pandas as pd
import numpy as np


# ==============================================================================
# METRIC CATALOGUE METADATA
# ==============================================================================

METRIC_CATALOGUE = [
    {
        "metric_id": "KPI-01",
        "metric_name": "Organisation Attendance Rate",
        "business_definition": "Percentage of eligible working days fulfilled by employee attendance.",
        "formula": "(Total Present Records ÷ Total Eligible Working-Day Records) × 100",
        "source": "vw_attendance_analysis (counts_as_present, is_working_day, status_code)",
        "denominator": "Records where is_working_day = 1, status != 'HOLIDAY', status != 'APPROVED_LEAVE'",
        "exclusions": "Approved leave and public holidays are excluded from denominator per BRD.",
        "interpretation": "Weighted workforce fulfillment rate across all active business units."
    },
    {
        "metric_id": "KPI-02",
        "metric_name": "Department Attendance Rate",
        "business_definition": "Department-specific percentage of eligible working days attended.",
        "formula": "(Department Present Records ÷ Department Eligible Working-Day Records) × 100",
        "source": "vw_attendance_analysis (counts_as_present, department_name)",
        "denominator": "Department records where is_working_day = 1, excluding leave/holidays",
        "exclusions": "Approved leave and public holidays excluded.",
        "interpretation": "Benchmarking departmental workforce participation."
    },
    {
        "metric_id": "KPI-03",
        "metric_name": "Lateness Incident Rate",
        "business_definition": "Proportion of attended shifts that exceeded scheduled start time plus grace buffer.",
        "formula": "(Late Arrival Count ÷ Total Present Shifts) × 100",
        "source": "vw_attendance_analysis (is_late, status_code)",
        "denominator": "Total records where status_code = 'PRESENT'",
        "exclusions": "Absent days and approved leave days (only active check-ins evaluated).",
        "interpretation": "Indicator of arrival punctuality compliance across shifts."
    },
    {
        "metric_id": "KPI-04",
        "metric_name": "Average Recorded Elapsed Duration",
        "business_definition": "Mean gross elapsed duration in minutes between check-in and check-out timestamps.",
        "formula": "Sum(Check-out Minutes − Check-in Minutes) ÷ Count(Valid Timestamp Pairs)",
        "source": "vw_attendance_analysis (check_in_time, check_out_time, elapsed_duration_minutes)",
        "denominator": "Present shifts with valid, non-null check-in and check-out timestamps.",
        "exclusions": "Shifts with missing check-outs (7 records in dataset) and non-present records.",
        "interpretation": "Gross recorded time span on site. Note: Does not subtract unpaid meal or rest breaks."
    },
    {
        "metric_id": "KPI-05",
        "metric_name": "Statistical High-Absence Anomaly Flag",
        "business_definition": "Date-level absence anomaly identified via Tukey Interquartile Range method.",
        "formula": "Daily Absence Rate > Q3 + (1.5 × IQR)",
        "source": "vw_attendance_analysis (attendance_date, counts_as_absence)",
        "denominator": "Eligible daily employee shifts on that observation date.",
        "exclusions": "Dates with fewer than 4 observation samples evaluate to unflagged.",
        "interpretation": "Identifies outlier absence spikes for operational audit review."
    }
]


# ==============================================================================
# 1. ATTENDANCE RATE & STATUS CALCULATIONS
# ==============================================================================

def attendance_rate(df: pd.DataFrame) -> float:
    """Overall attendance rate as a weighted percentage.

    Formula:
      (sum of counts_as_present) / (number of eligible employee-days) * 100

    Rules:
      - Eligible employee-days: is_working_day == 1 and status_code not in ('HOLIDAY', 'APPROVED_LEAVE')
      - Returns NaN if eligible count is 0 (prevents divide-by-zero or misleading 0%).
    """
    if df.empty:
        return float("nan")

    # Working days excluding holidays
    eligible = df[
        (df["is_working_day"] == 1) & (df["status_code"] != "HOLIDAY")
    ]
    # Approved leave excluded from denominator
    eligible_denominator = eligible[eligible["status_code"] != "APPROVED_LEAVE"]
    denominator = len(eligible_denominator)

    if denominator == 0:
        return float("nan")

    present_count = int(eligible_denominator["counts_as_present"].sum())
    return (present_count / denominator) * 100.0


def daily_status_counts(df: pd.DataFrame) -> pd.DataFrame:
    """Pivot attendance records to obtain daily counts per status category.

    Returns DataFrame indexed by attendance_date with columns:
    PRESENT, ABSENT, APPROVED_LEAVE, HOLIDAY (missing categories fill with 0).
    """
    if df.empty:
        return pd.DataFrame()

    pivot = (
        df.groupby(["attendance_date", "status_code"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )
    pivot["attendance_date"] = pd.to_datetime(pivot["attendance_date"])
    for col in ["PRESENT", "ABSENT", "APPROVED_LEAVE", "HOLIDAY"]:
        if col not in pivot.columns:
            pivot[col] = 0
    return pivot.sort_values("attendance_date").reset_index(drop=True)


def daily_attendance_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate daily attendance rates for trend tracking across observation dates."""
    if df.empty:
        return pd.DataFrame(columns=["attendance_date", "present_count", "eligible_count", "attendance_rate"])

    eligible = df[
        (df["is_working_day"] == 1)
        & (df["status_code"] != "HOLIDAY")
        & (df["status_code"] != "APPROVED_LEAVE")
    ]
    if eligible.empty:
        return pd.DataFrame(columns=["attendance_date", "present_count", "eligible_count", "attendance_rate"])

    daily = eligible.groupby("attendance_date").agg(
        present_count=("counts_as_present", "sum"),
        eligible_count=("counts_as_present", "count"),
    ).reset_index()

    daily["attendance_rate"] = np.where(
        daily["eligible_count"] > 0,
        (daily["present_count"] / daily["eligible_count"]) * 100.0,
        float("nan"),
    )
    daily["attendance_date"] = pd.to_datetime(daily["attendance_date"])
    return daily.sort_values("attendance_date").reset_index(drop=True)


def department_attendance_rates(df: pd.DataFrame) -> pd.DataFrame:
    """Weighted attendance rate grouped by department.

    Returns DataFrame: department_name, attendance_rate, present_count, eligible_count.
    """
    if df.empty:
        return pd.DataFrame(
            columns=["department_name", "attendance_rate", "present_count", "eligible_count"]
        )

    eligible = df[
        (df["is_working_day"] == 1)
        & (df["status_code"] != "HOLIDAY")
        & (df["status_code"] != "APPROVED_LEAVE")
    ]

    grouped = eligible.groupby("department_name").agg(
        present_count=("counts_as_present", "sum"),
        eligible_count=("counts_as_present", "count"),
    ).reset_index()

    grouped["attendance_rate"] = np.where(
        grouped["eligible_count"] > 0,
        (grouped["present_count"] / grouped["eligible_count"]) * 100.0,
        float("nan"),
    )
    return grouped


def record_coverage(df: pd.DataFrame) -> dict:
    """High-level summary of records, unique staff, dates, and departments."""
    if df.empty:
        return {
            "total_records": 0,
            "unique_employees": 0,
            "unique_dates": 0,
            "unique_departments": 0,
        }
    return {
        "total_records": len(df),
        "unique_employees": int(df["employee_id"].nunique()) if "employee_id" in df.columns else 0,
        "unique_dates": int(df["attendance_date"].nunique()) if "attendance_date" in df.columns else 0,
        "unique_departments": int(df["department_name"].nunique()) if "department_name" in df.columns else 0,
    }


# ==============================================================================
# 2. PUNCTUALITY & DURATION METRICS
# ==============================================================================

def _time_to_minutes(t_val) -> float:
    """Convert 'HH:MM' string to minutes from midnight."""
    if pd.isna(t_val) or not isinstance(t_val, str) or len(t_val) != 5:
        return float("nan")
    try:
        parts = t_val.split(":")
        return int(parts[0]) * 60 + int(parts[1])
    except (ValueError, IndexError):
        return float("nan")


def late_arrival_metrics(df: pd.DataFrame) -> dict:
    """Calculate shift punctuality and late arrival incident metrics.

    Business Rule:
      Late arrival strictly means check_in_time > scheduled_start_time + grace_minutes.
      If check_in_time == scheduled_start_time + grace_minutes, it is considered PUNCTUAL.

    Returns dict:
      - late_count: int
      - punctual_count: int
      - total_present: int
      - late_rate: float (%)
      - late_by_department: DataFrame
      - late_by_month: DataFrame
      - late_records: DataFrame of specific late shifts
    """
    if df.empty:
        return {
            "late_count": 0,
            "punctual_count": 0,
            "total_present": 0,
            "late_rate": float("nan"),
            "late_by_department": pd.DataFrame(),
            "late_by_month": pd.DataFrame(),
            "late_records": pd.DataFrame(),
        }

    present = df[df["status_code"] == "PRESENT"].copy()
    total_present = len(present)

    if total_present == 0:
        return {
            "late_count": 0,
            "punctual_count": 0,
            "total_present": 0,
            "late_rate": float("nan"),
            "late_by_department": pd.DataFrame(),
            "late_by_month": pd.DataFrame(),
            "late_records": pd.DataFrame(),
        }

    # Verify or compute is_late explicitly to adhere to the strict grace boundary rule
    ci_min = present["check_in_time"].apply(_time_to_minutes)
    ss_min = present["scheduled_start_time"].apply(_time_to_minutes)
    grace = pd.to_numeric(present.get("grace_minutes", 10), errors="coerce").fillna(10)
    
    # Strictly greater than scheduled start + grace
    present["is_late_reconciled"] = ((ci_min > (ss_min + grace)) & ci_min.notna()).astype(int)

    late_count = int(present["is_late_reconciled"].sum())
    punctual_count = total_present - late_count
    late_rate = (late_count / total_present) * 100.0

    # Department breakdown
    late_by_dept = (
        present.groupby("department_name")
        .agg(
            late_count=("is_late_reconciled", "sum"),
            total_present=("is_late_reconciled", "count"),
        )
        .reset_index()
    )
    late_by_dept["late_rate"] = np.where(
        late_by_dept["total_present"] > 0,
        (late_by_dept["late_count"] / late_by_dept["total_present"]) * 100.0,
        float("nan"),
    )

    # Monthly breakdown if attendance_date column exists
    if "attendance_date" in present.columns:
        present["month"] = pd.to_datetime(present["attendance_date"]).dt.to_period("M").astype(str)
        late_by_month = (
            present.groupby("month")
            .agg(
                late_count=("is_late_reconciled", "sum"),
                total_present=("is_late_reconciled", "count"),
            )
            .reset_index()
        )
        late_by_month["late_rate"] = np.where(
            late_by_month["total_present"] > 0,
            (late_by_month["late_count"] / late_by_month["total_present"]) * 100.0,
            float("nan"),
        )
    else:
        late_by_month = pd.DataFrame()

    late_records = present[present["is_late_reconciled"] == 1].copy()

    return {
        "late_count": late_count,
        "punctual_count": punctual_count,
        "total_present": total_present,
        "late_rate": late_rate,
        "late_by_department": late_by_dept,
        "late_by_month": late_by_month,
        "late_records": late_records,
    }


def elapsed_duration_minutes(df: pd.DataFrame) -> pd.Series:
    """Return elapsed duration in minutes for each attended shift.

    Formula: Check-out timestamp in minutes − Check-in timestamp in minutes.
    Preserves missing check-out records as NaN (never fabricated or imputed).
    Excludes invalid negative durations if any exist.
    """
    if df.empty:
        return pd.Series(dtype=float)

    if "elapsed_duration_minutes" in df.columns:
        dur = pd.to_numeric(df["elapsed_duration_minutes"], errors="coerce")
        # Ensure any corrupt negative elapsed durations are invalidated to NaN
        return dur.mask(dur < 0)

    # Compute directly from timestamps
    ci_min = df["check_in_time"].apply(_time_to_minutes)
    co_min = df["check_out_time"].apply(_time_to_minutes)
    dur = co_min - ci_min
    return dur.mask(dur < 0)


def average_duration_metrics(df: pd.DataFrame) -> dict:
    """Calculates average recorded duration and documents valid sample sizes."""
    present = df[df["status_code"] == "PRESENT"]
    durations = elapsed_duration_minutes(present).dropna()
    
    sample_size = len(durations)
    missing_checkouts = int(present["check_out_time"].isna().sum()) if not present.empty else 0
    mean_val = float(durations.mean()) if sample_size > 0 else float("nan")
    min_val = float(durations.min()) if sample_size > 0 else float("nan")
    max_val = float(durations.max()) if sample_size > 0 else float("nan")

    return {
        "average_duration_minutes": mean_val,
        "min_duration_minutes": min_val,
        "max_duration_minutes": max_val,
        "valid_sample_size": sample_size,
        "missing_checkouts_count": missing_checkouts,
        "total_present_records": len(present),
    }


def employee_punctuality_rankings(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate employee-level punctuality and chronic lateness rankings.
    
    Identifies habitual late arrivals, punctuality champions, average delays,
    and classifies staff into actionable operational risk categories.
    """
    if df is None or df.empty or "employee_code" not in df.columns:
        return pd.DataFrame(columns=[
            "employee_code", "department_name", "total_shifts", "total_attended_shifts", "late_count",
            "punctual_count", "late_rate", "punctuality_rate", "avg_delay_minutes",
            "max_delay_minutes", "avg_duration_minutes", "risk_category"
        ])

    rows = []
    for emp_code, grp in df.groupby("employee_code"):
        dept_name = grp["department_name"].iloc[0] if "department_name" in grp.columns else "Unknown"
        present_shifts = grp[grp["status_code"] == "PRESENT"]
        total_p = len(present_shifts)
        
        if total_p == 0:
            continue

        late_c = int(present_shifts["is_late"].sum()) if "is_late" in present_shifts.columns else 0
        punctual_c = total_p - late_c
        late_r = (late_c / total_p * 100.0)
        punc_r = 100.0 - late_r

        delays = present_shifts["arrival_delay_minutes"].dropna()
        avg_delay = float(delays.mean()) if not delays.empty else 0.0
        max_delay = float(delays.max()) if not delays.empty else 0.0

        durations = present_shifts["elapsed_duration_minutes"].dropna()
        avg_dur = float(durations.mean()) if not durations.empty else 0.0

        if late_r >= 30.0:
            risk = "🔴 Chronic Lateness Risk"
        elif late_r >= 15.0:
            risk = "🟡 Moderate Lateness"
        elif late_c > 0:
            risk = "🟢 Minor Lateness (<15%)"
        else:
            risk = "⭐ 100% Punctual Champion"

        rows.append({
            "employee_code": emp_code,
            "department_name": dept_name,
            "total_shifts": total_p,
            "total_attended_shifts": total_p,
            "late_count": late_c,
            "punctual_count": punctual_c,
            "late_rate": round(late_r, 1),
            "punctuality_rate": round(punc_r, 1),
            "avg_delay_minutes": round(avg_delay, 1),
            "max_delay_minutes": round(max_delay, 1),
            "avg_duration_minutes": round(avg_dur, 1),
            "risk_category": risk,
        })

    rankings_df = pd.DataFrame(rows)
    if not rankings_df.empty:
        rankings_df = rankings_df.sort_values(
            by=["late_count", "late_rate", "avg_delay_minutes"],
            ascending=[False, False, False]
        )
    return rankings_df
