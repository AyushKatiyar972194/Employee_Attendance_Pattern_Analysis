"""Automated test suite verifying enterprise error handling and crash resilience."""
import pytest
import pandas as pd
import numpy as np
from pathlib import Path

from src.data_loader import filter_data, load_attendance_data
from src.metrics import (
    attendance_rate,
    department_attendance_rates,
    late_arrival_metrics,
    average_duration_metrics,
    daily_status_counts,
    daily_attendance_trend,
)
from src.charts import (
    department_rates_chart,
    late_by_department_chart,
    daily_attendance_trend_chart,
    checkin_delay_chart,
    elapsed_duration_chart,
    high_absence_chart,
    status_donut_chart,
    department_weekday_heatmap,
    department_quadrant_chart,
    arrival_distribution_chart,
    punctuality_donut_chart,
)
from src.validation import validate_attendance_data
from src.database import get_table_counts, get_observation_dates
from src.ui import safe_page_render


def test_filter_data_handles_none_and_empty():
    """Verify filter_data does not raise on None or empty DataFrame."""
    res_none = filter_data(None)
    assert isinstance(res_none, pd.DataFrame)
    assert res_none.empty

    res_empty = filter_data(pd.DataFrame())
    assert isinstance(res_empty, pd.DataFrame)
    assert res_empty.empty


def test_filter_data_handles_inverted_dates():
    """Verify filter_data safely filters when start_date > end_date (returns empty)."""
    df = pd.DataFrame({
        "attendance_date": pd.to_datetime(["2026-10-01", "2026-10-15"]),
        "department_name": ["Engineering", "HR"],
        "status_code": ["PRESENT", "PRESENT"],
    })
    filtered = filter_data(df, start_date="2026-10-20", end_date="2026-10-01")
    assert isinstance(filtered, pd.DataFrame)
    assert filtered.empty


def test_department_rates_with_only_approved_leave_no_idxmax_crash():
    """Verify department_attendance_rates when all records are APPROVED_LEAVE."""
    df_leave = pd.DataFrame({
        "department_name": ["Engineering", "Sales"],
        "is_working_day": [1, 1],
        "status_code": ["APPROVED_LEAVE", "APPROVED_LEAVE"],
        "counts_as_present": [0, 0],
    })
    dept_rates = department_attendance_rates(df_leave)
    assert isinstance(dept_rates, pd.DataFrame)
    # attendance_rate should be empty or NaN, must not crash when querying
    valid = dept_rates.dropna(subset=["attendance_rate"]) if not dept_rates.empty else pd.DataFrame()
    assert valid.empty


def test_late_arrival_metrics_with_only_absent_records():
    """Verify late arrival metrics when there are zero PRESENT shifts."""
    df_absent = pd.DataFrame({
        "department_name": ["Finance", "Customer Support"],
        "status_code": ["ABSENT", "ABSENT"],
        "check_in_time": [None, None],
        "scheduled_start_time": ["09:00", "09:00"],
    })
    metrics = late_arrival_metrics(df_absent)
    assert metrics["late_count"] == 0
    assert metrics["total_present"] == 0
    assert np.isnan(metrics["late_rate"])
    assert metrics["late_by_department"].empty


def test_charts_gracefully_handle_empty_and_nan():
    """Verify that all chart builders return valid Figure without exceptions on empty/NaN data."""
    # 1. Department rates with empty / all-NaN
    fig1 = department_rates_chart(pd.DataFrame())
    assert fig1 is not None

    fig1_nan = department_rates_chart(pd.DataFrame({
        "department_name": ["Engineering"],
        "attendance_rate": [float("nan")]
    }))
    assert fig1_nan is not None

    # 2. Late by department
    fig2 = late_by_department_chart(pd.DataFrame())
    assert fig2 is not None

    fig2_nan = late_by_department_chart(pd.DataFrame({
        "department_name": ["Engineering"],
        "late_rate": [float("nan")],
        "late_count": [0],
        "total_present": [0],
    }))
    assert fig2_nan is not None

    # 3. Trend chart
    fig3 = daily_attendance_trend_chart(pd.DataFrame())
    assert fig3 is not None

    # 4. Checkin delay
    fig4 = checkin_delay_chart(pd.DataFrame())
    assert fig4 is not None

    # 5. Elapsed duration
    fig5 = elapsed_duration_chart(pd.Series(dtype=float))
    assert fig5 is not None

    # 6. High absence
    fig6 = high_absence_chart(pd.DataFrame())
    assert fig6 is not None

    # 7. Status Donut
    fig7 = status_donut_chart(pd.DataFrame())
    assert fig7 is not None

    # 8. Department x Weekday Heatmap
    fig8 = department_weekday_heatmap(pd.DataFrame())
    assert fig8 is not None

    # 9. Department Quadrant Matrix
    fig9 = department_quadrant_chart(pd.DataFrame())
    assert fig9 is not None

    # 10. Arrival Distribution
    fig10 = arrival_distribution_chart(pd.DataFrame())
    assert fig10 is not None

    # 11. Punctuality Donut
    fig11 = punctuality_donut_chart({})
    assert fig11 is not None


def test_donut_charts_render_with_actual_data():
    """Verify that status and punctuality donut charts render traces with actual data."""
    mock_df = pd.DataFrame({
        "status_code": ["PRESENT", "PRESENT", "APPROVED_LEAVE", "ABSENT"]
    })
    fig_status = status_donut_chart(mock_df, attendance_rate=75.0)
    assert len(fig_status.data) == 1
    assert tuple(fig_status.data[0].values) == (2, 1, 1)

    mock_late = {
        "punctual_count": 80,
        "late_count": 20,
        "total_present": 100,
    }
    fig_punc = punctuality_donut_chart(mock_late)
    assert len(fig_punc.data) == 1
    assert tuple(fig_punc.data[0].values) == (80, 20)


def test_department_rates_chart_accepts_both_org_rate_and_org_avg():
    """Verify department_rates_chart accepts both org_rate and org_avg without TypeError."""
    mock_dept_rates = pd.DataFrame({
        "department_name": ["Engineering", "HR"],
        "attendance_rate": [95.0, 98.0],
        "present_count": [95, 98],
        "eligible_count": [100, 100],
    })
    fig1 = department_rates_chart(mock_dept_rates, org_rate=96.5)
    assert fig1 is not None

    fig2 = department_rates_chart(mock_dept_rates, org_avg=96.5)
    assert fig2 is not None


def test_validate_attendance_data_handles_empty_or_none():
    """Verify validation engine handles empty or None input gracefully."""
    rep_none = validate_attendance_data(None)
    assert rep_none["total_rows"] == 0
    assert rep_none["missing_count"] == 0
    assert rep_none["dimensions"]["Completeness"] == "Passed"

    rep_empty = validate_attendance_data(pd.DataFrame())
    assert rep_empty["total_rows"] == 0


def test_database_helpers_handle_nonexistent_paths():
    """Verify database helpers return safe fallbacks instead of crashing when path is invalid."""
    fake_path = Path("non_existent_directory_xyz") / "fake.db"
    counts = get_table_counts(fake_path)
    assert isinstance(counts, dict)
    assert all(v == 0 for v in counts.values())

    dates = get_observation_dates(fake_path)
    assert isinstance(dates, list)
    assert len(dates) == 0


def test_safe_page_render_catches_unhandled_exception():
    """Verify safe_page_render catches exceptions without raising."""
    def broken_page():
        raise RuntimeError("Simulated runtime failure")

    # Must catch and not raise
    safe_page_render(broken_page)
