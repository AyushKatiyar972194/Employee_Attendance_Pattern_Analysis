"""Analysis and KPI tests using small deterministic data.

Expected Step 15 module contract:
- src.metrics.attendance_rate(df) -> percentage
- src.metrics.daily_status_counts(df) -> DataFrame
- src.metrics.department_attendance_rates(df) -> DataFrame
- src.metrics.late_arrival_metrics(df) -> dict
- src.metrics.elapsed_duration_minutes(df) -> Series
- src.statistics.weekday_attendance_summary(df) -> DataFrame
- src.statistics.flag_high_absence_dates(df) -> DataFrame

Input DataFrames use the joined-view field names from Step 8.
"""
import pandas as pd
import pytest


@pytest.fixture
def tiny_attendance():
    return pd.DataFrame([
        # 3 expected employee-days: 2 present, 1 absent; one approved leave is not in this tiny denominator.
        {"attendance_id": 1, "employee_id": 1, "department_id": 1, "attendance_date": "2026-10-01",
         "status_code": "PRESENT", "counts_as_present": 1, "counts_as_absence": 0,
         "is_working_day": 1, "scheduled_start_time": "09:00", "grace_minutes": 10,
         "check_in_time": "09:05", "check_out_time": "18:00", "department_name": "Engineering",
         "weekday_name": "Thursday"},
        {"attendance_id": 2, "employee_id": 2, "department_id": 1, "attendance_date": "2026-10-01",
         "status_code": "PRESENT", "counts_as_present": 1, "counts_as_absence": 0,
         "is_working_day": 1, "scheduled_start_time": "09:00", "grace_minutes": 10,
         "check_in_time": "09:15", "check_out_time": "18:15", "department_name": "Engineering",
         "weekday_name": "Thursday"},
        {"attendance_id": 3, "employee_id": 3, "department_id": 1, "attendance_date": "2026-10-01",
         "status_code": "ABSENT", "counts_as_present": 0, "counts_as_absence": 1,
         "is_working_day": 1, "scheduled_start_time": "09:00", "grace_minutes": 10,
         "check_in_time": None, "check_out_time": None, "department_name": "Engineering",
         "weekday_name": "Thursday"},
    ])


def test_attendance_rate_known_result(tiny_attendance):
    from src.metrics import attendance_rate

    assert attendance_rate(tiny_attendance) == pytest.approx(66.6667, rel=1e-4)


def test_daily_status_counts_known_result(tiny_attendance):
    from src.metrics import daily_status_counts

    result = daily_status_counts(tiny_attendance)
    row = result.iloc[0]
    assert row["PRESENT"] == 2
    assert row["ABSENT"] == 1


def test_department_attendance_rate_known_result(tiny_attendance):
    from src.metrics import department_attendance_rates

    result = department_attendance_rates(tiny_attendance)
    rate = result.loc[result["department_name"] == "Engineering", "attendance_rate"].iloc[0]
    assert rate == pytest.approx(66.6667, rel=1e-4)


def test_late_arrival_grace_period_boundary(tiny_attendance):
    from src.metrics import late_arrival_metrics

    result = late_arrival_metrics(tiny_attendance)
    # 09:05 is within grace; 09:15 is later than 09:10 and is late.
    assert result["late_count"] == 1


def test_elapsed_duration_is_minutes_and_excludes_missing_pairs(tiny_attendance):
    from src.metrics import elapsed_duration_minutes

    result = elapsed_duration_minutes(tiny_attendance)
    assert list(result.dropna()) == [535.0, 540.0]


def test_weekday_summary_groups_by_weekday(tiny_attendance):
    from src.statistics import weekday_attendance_summary

    result = weekday_attendance_summary(tiny_attendance)
    assert "weekday_name" in result.columns
    assert "attendance_rate" in result.columns
    assert "Thursday" in result["weekday_name"].values


def test_high_absence_flags_return_reviewable_dates(tiny_attendance):
    from src.statistics import flag_high_absence_dates

    result = flag_high_absence_dates(tiny_attendance)
    assert isinstance(result, pd.DataFrame)
    assert {"attendance_date", "absence_rate", "is_flagged"}.issubset(result.columns)


def test_empty_input_returns_safe_empty_or_zero_result():
    from src.metrics import attendance_rate, daily_status_counts

    empty = pd.DataFrame(columns=[
        "attendance_id", "attendance_date", "status_code", "counts_as_present",
        "counts_as_absence", "is_working_day", "employee_id", "department_id"
    ])
    rate = attendance_rate(empty)
    assert rate == 0 or pd.isna(rate)
    counts = daily_status_counts(empty)
    assert isinstance(counts, pd.DataFrame)


# ==============================================================================
# ENTERPRISE & P0 RECONCILIATION TESTS
# ==============================================================================

def test_grace_period_exact_boundary_reconciliation():
    """Verify that arrival at exactly 09:10 (09:00 + 10m grace) is PUNCTUAL, not late."""
    from src.metrics import late_arrival_metrics
    df = pd.DataFrame([
        {
            "attendance_id": 101, "employee_id": 1, "status_code": "PRESENT",
            "scheduled_start_time": "09:00", "grace_minutes": 10,
            "check_in_time": "09:10", "department_name": "Engineering"
        },
        {
            "attendance_id": 102, "employee_id": 2, "status_code": "PRESENT",
            "scheduled_start_time": "09:00", "grace_minutes": 10,
            "check_in_time": "09:11", "department_name": "Engineering"
        }
    ])
    metrics = late_arrival_metrics(df)
    # 09:10 is punctual, 09:11 is late
    assert metrics["late_count"] == 1
    assert metrics["punctual_count"] == 1
    assert metrics["late_rate"] == 50.0


def test_average_duration_denominator_and_missing_checkout_exclusion():
    """Verify that average duration calculation excludes null checkouts from denominator."""
    from src.metrics import average_duration_metrics
    df = pd.DataFrame([
        {"status_code": "PRESENT", "check_in_time": "09:00", "check_out_time": "17:00", "elapsed_duration_minutes": 480},
        {"status_code": "PRESENT", "check_in_time": "09:00", "check_out_time": "18:00", "elapsed_duration_minutes": 540},
        {"status_code": "PRESENT", "check_in_time": "09:00", "check_out_time": None, "elapsed_duration_minutes": None}, # Missing checkout
        {"status_code": "ABSENT", "check_in_time": None, "check_out_time": None, "elapsed_duration_minutes": None},
    ])
    metrics = average_duration_metrics(df)
    assert metrics["valid_sample_size"] == 2
    assert metrics["missing_checkouts_count"] == 1
    assert metrics["average_duration_minutes"] == 510.0  # (480 + 540) / 2


def test_department_rate_weighting_vs_simple_average():
    """Verify that department attendance rate is weighted, not an arithmetic mean of percentages."""
    from src.metrics import attendance_rate
    # Dept A: 10/10 (100%), Dept B: 1/10 (10%)
    # Simple average of dept rates would be 55%.
    # Weighted average is (10 + 1) / 20 = 55%.
    # Now Dept A: 100/100 (100%), Dept B: 1/2 (50%)
    # Simple avg is 75%, weighted is 101/102 = 99.0196%
    records = []
    for i in range(100):
        records.append({"is_working_day": 1, "status_code": "PRESENT", "counts_as_present": 1, "department_name": "DeptA"})
    records.append({"is_working_day": 1, "status_code": "PRESENT", "counts_as_present": 1, "department_name": "DeptB"})
    records.append({"is_working_day": 1, "status_code": "ABSENT", "counts_as_present": 0, "department_name": "DeptB"})
    df = pd.DataFrame(records)
    
    overall_rate = attendance_rate(df)
    assert overall_rate == pytest.approx(101 / 102 * 100.0, rel=1e-4)


def test_daily_attendance_trend_calculation():
    """Verify day-by-day attendance rate trend output."""
    from src.metrics import daily_attendance_trend
    df = pd.DataFrame([
        {"attendance_date": "2026-10-01", "is_working_day": 1, "status_code": "PRESENT", "counts_as_present": 1},
        {"attendance_date": "2026-10-01", "is_working_day": 1, "status_code": "ABSENT", "counts_as_present": 0},
        {"attendance_date": "2026-10-05", "is_working_day": 1, "status_code": "PRESENT", "counts_as_present": 1},
    ])
    trend = daily_attendance_trend(df)
    assert len(trend) == 2
    assert trend.loc[trend["attendance_date"] == pd.to_datetime("2026-10-01"), "attendance_rate"].iloc[0] == 50.0
    assert trend.loc[trend["attendance_date"] == pd.to_datetime("2026-10-05"), "attendance_rate"].iloc[0] == 100.0


def test_database_actual_reconciliation():
    """Verify live app.db values against known ground truth for the 2,400-record dataset."""
    import sqlite3
    from src.config import DB_PATH
    from src.metrics import attendance_rate, late_arrival_metrics, average_duration_metrics
    from src.data_loader import load_attendance_data

    df = load_attendance_data(DB_PATH)
    assert len(df) == 2400
    
    # 1. Overall attendance rate
    rate = attendance_rate(df)
    assert rate == pytest.approx(95.8696, rel=1e-4)
    
    # 2. Lateness
    late_info = late_arrival_metrics(df)
    assert late_info["late_count"] == 353
    assert late_info["punctual_count"] == 1852
    assert late_info["total_present"] == 2205
    assert late_info["late_rate"] == pytest.approx(16.0091, rel=1e-4)
    
    # 3. Average duration
    dur_info = average_duration_metrics(df)
    assert dur_info["valid_sample_size"] == 2154
    assert dur_info["missing_checkouts_count"] == 51
    assert dur_info["average_duration_minutes"] == pytest.approx(505.1908, rel=1e-3)


def test_employee_punctuality_rankings_calculation():
    """Verify employee punctuality rankings, risk categorization, and sorting logic."""
    from src.metrics import employee_punctuality_rankings

    mock_df = pd.DataFrame([
        # EMP1: 2 shifts, 2 late -> 100% late rate -> Chronic
        {"employee_code": "EMP01", "department_name": "Engineering", "status_code": "PRESENT",
         "is_late": 1, "arrival_delay_minutes": 25.0, "elapsed_duration_minutes": 500.0},
        {"employee_code": "EMP01", "department_name": "Engineering", "status_code": "PRESENT",
         "is_late": 1, "arrival_delay_minutes": 15.0, "elapsed_duration_minutes": 510.0},
        # EMP2: 5 shifts, 1 late -> 20% late rate -> Moderate
        {"employee_code": "EMP02", "department_name": "Operations", "status_code": "PRESENT",
         "is_late": 1, "arrival_delay_minutes": 12.0, "elapsed_duration_minutes": 520.0},
        {"employee_code": "EMP02", "department_name": "Operations", "status_code": "PRESENT",
         "is_late": 0, "arrival_delay_minutes": 0.0, "elapsed_duration_minutes": 510.0},
        {"employee_code": "EMP02", "department_name": "Operations", "status_code": "PRESENT",
         "is_late": 0, "arrival_delay_minutes": 0.0, "elapsed_duration_minutes": 510.0},
        {"employee_code": "EMP02", "department_name": "Operations", "status_code": "PRESENT",
         "is_late": 0, "arrival_delay_minutes": 0.0, "elapsed_duration_minutes": 510.0},
        {"employee_code": "EMP02", "department_name": "Operations", "status_code": "PRESENT",
         "is_late": 0, "arrival_delay_minutes": 0.0, "elapsed_duration_minutes": 510.0},
        # EMP3: 2 shifts, 0 late -> 100% Punctual Champion
        {"employee_code": "EMP03", "department_name": "Finance", "status_code": "PRESENT",
         "is_late": 0, "arrival_delay_minutes": 0.0, "elapsed_duration_minutes": 490.0},
        {"employee_code": "EMP03", "department_name": "Finance", "status_code": "PRESENT",
         "is_late": 0, "arrival_delay_minutes": 0.0, "elapsed_duration_minutes": 500.0},
    ])

    rankings = employee_punctuality_rankings(mock_df)
    assert len(rankings) == 3
    # Check EMP01 top ranked because of highest late_count (2)
    assert rankings.iloc[0]["employee_code"] == "EMP01"
    assert rankings.iloc[0]["late_rate"] == 100.0
    assert rankings.iloc[0]["risk_category"] == "🔴 Chronic Lateness Risk"
    assert rankings.iloc[0]["avg_delay_minutes"] == 20.0

    # EMP02
    emp02 = rankings[rankings["employee_code"] == "EMP02"].iloc[0]
    assert emp02["late_count"] == 1
    assert emp02["late_rate"] == 20.0
    assert emp02["risk_category"] == "🟡 Moderate Lateness"

    # EMP03
    emp03 = rankings[rankings["employee_code"] == "EMP03"].iloc[0]
    assert emp03["late_count"] == 0
    assert emp03["late_rate"] == 0.0
    assert emp03["risk_category"] == "⭐ 100% Punctual Champion"


def test_employee_punctuality_rankings_empty_and_edge_cases():
    """Verify handling of empty df, missing columns, or no present shifts."""
    from src.metrics import employee_punctuality_rankings

    # Empty DataFrame
    empty_res = employee_punctuality_rankings(pd.DataFrame())
    assert isinstance(empty_res, pd.DataFrame)
    assert "employee_code" in empty_res.columns

    # Only Absent shifts
    absent_df = pd.DataFrame([
        {"employee_code": "EMP99", "status_code": "ABSENT"}
    ])
    absent_res = employee_punctuality_rankings(absent_df)
    assert absent_res.empty
