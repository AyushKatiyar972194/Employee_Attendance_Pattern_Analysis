"""Unit tests for Predictive Risk Intelligence, Policy Simulation, and Financial ROI."""
from pathlib import Path
import pandas as pd
import pytest

from src.config import DB_PATH
from src.data_loader import load_attendance_data
from src.predictive import (
    extract_employee_risk_features,
    compute_attendance_risk_scores,
)
from src.simulation import (
    simulate_grace_period_policy,
    calculate_financial_loss,
    generate_executive_audit_markdown,
)


@pytest.fixture(scope="module")
def sample_df():
    df = load_attendance_data(DB_PATH)
    assert not df.empty
    return df


def test_extract_employee_risk_features(sample_df):
    features = extract_employee_risk_features(sample_df)
    assert not features.empty
    assert len(features) == 120  # All 120 employees evaluated
    required_cols = [
        "employee_id",
        "employee_code",
        "department_name",
        "total_shifts",
        "late_rate",
        "delay_volatility",
        "weekend_leave_pct",
        "missing_checkouts",
    ]
    assert set(required_cols).issubset(features.columns)


def test_compute_attendance_risk_scores(sample_df):
    scores = compute_attendance_risk_scores(sample_df)
    assert not scores.empty
    assert len(scores) == 120

    # Scores must be bounded 0 to 100
    assert (scores["risk_score"] >= 0).all()
    assert (scores["risk_score"] <= 100).all()

    # Verify risk tiers exist
    tiers = set(scores["risk_tier"].unique())
    assert {"Low Risk (Healthy)", "Moderate Risk (Watchlist)", "High Risk (Action Needed)"}.intersection(tiers)

    # Verify explainable drivers are present
    assert scores["primary_drivers"].str.len().gt(0).all()


def test_simulate_grace_period_policy(sample_df):
    # Test 15-minute grace period policy
    sim_15 = simulate_grace_period_policy(sample_df, target_grace_minutes=15)
    assert sim_15["baseline_grace"] == 10
    assert sim_15["target_grace"] == 15
    assert sim_15["simulated_punctuality_pct"] >= sim_15["baseline_punctuality_pct"]
    assert sim_15["reclassified_on_time"] > 0
    assert not sim_15["department_comparison"].empty

    # Test extreme 0-minute grace period policy (strict 09:00 cutoff)
    sim_0 = simulate_grace_period_policy(sample_df, target_grace_minutes=0)
    assert sim_0["simulated_punctuality_pct"] <= sim_15["baseline_punctuality_pct"]


def test_calculate_financial_loss(sample_df):
    fin = calculate_financial_loss(sample_df, hourly_wage=650.0, contractor_multiplier=1.5)
    assert fin["total_records"] == len(sample_df)
    assert fin["late_hours_lost"] > 0
    assert fin["late_cost"] > 0
    assert fin["absence_cost"] > 0
    assert fin["total_financial_loss"] == round(fin["late_cost"] + fin["absence_cost"], 2)
    assert fin["projected_10pct_recovery"] > 0


def test_generate_executive_audit_markdown(sample_df):
    memo = generate_executive_audit_markdown(sample_df)
    assert isinstance(memo, str)
    assert "NORTHSTAR TECHNOLOGIES — EXECUTIVE AUDIT MEMORANDUM" in memo
    assert "Financial & Productivity Exposure" in memo
    assert "Prescriptive Policy Recommendations" in memo
