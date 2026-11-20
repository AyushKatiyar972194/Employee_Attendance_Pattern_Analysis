"""Predictive Machine Learning & Attendance Risk Intelligence.

Calculates composite Attendance Risk Scores (0-100) using multi-factor
behavioral feature engineering:
- Lateness frequency & arrival delay volatility
- Monday/Friday weekend-adjacent leave clustering
- Missing punch-out frequency
- Unplanned absence streaks
"""
from __future__ import annotations

import pandas as pd
import numpy as np


def extract_employee_risk_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extract granular behavioral attendance features per employee.

    Features engineered:
    - total_shifts: total shifts assigned
    - present_shifts: shifts with status PRESENT
    - late_shifts: shifts where is_late == 1
    - late_rate: percentage of attended shifts that were late
    - avg_delay_mins: average arrival delay minutes
    - delay_std_mins: standard deviation / volatility of arrival delay
    - weekend_adjacent_leave_pct: percentage of leaves on Monday or Friday
    - missing_checkout_count: shifts with missing check-outs
    - missing_checkout_rate: percentage of present shifts missing checkout
    - absence_count: shifts with status ABSENT
    - absence_rate: percentage of shifts absent
    """
    if df is None or df.empty:
        return pd.DataFrame()

    data = df.copy()

    records = []
    grouped = data.groupby(["employee_id", "employee_code", "department_name"])

    for (emp_id, emp_code, dept), group in grouped:
        total_shifts = len(group)
        if total_shifts == 0:
            continue

        p_mask = group["status_code"] == "PRESENT"
        present_count = int(p_mask.sum())
        absent_count = int((group["status_code"] == "ABSENT").sum())
        leave_count = int((group["status_code"] == "APPROVED_LEAVE").sum())

        # Lateness features
        late_count = int((group["is_late"] == 1).sum()) if "is_late" in group.columns else 0
        late_rate = (late_count / present_count * 100.0) if present_count > 0 else 0.0

        # Delay volatility
        delays = group.loc[p_mask & group["arrival_delay_minutes"].notna(), "arrival_delay_minutes"]
        avg_delay = float(delays.mean()) if not delays.empty else 0.0
        std_delay = float(delays.std()) if len(delays) > 1 else 0.0

        # Weekend-adjacent leave ratio (Monday / Friday clustering)
        if "weekday_name" in group.columns:
            leave_rows = group[group["status_code"] == "APPROVED_LEAVE"]
            if not leave_rows.empty:
                wf_leaves = leave_rows["weekday_name"].isin(["Monday", "Friday"]).sum()
                weekend_leave_pct = float(wf_leaves / len(leave_rows) * 100.0)
            else:
                weekend_leave_pct = 0.0
        else:
            weekend_leave_pct = 0.0

        # Missing check-outs
        if "check_out_time" in group.columns:
            missing_co = int((p_mask & group["check_out_time"].isna()).sum())
        else:
            missing_co = 0
        missing_co_rate = (missing_co / present_count * 100.0) if present_count > 0 else 0.0

        # Absence rate
        absence_rate = (absent_count / total_shifts * 100.0)

        records.append({
            "employee_id": emp_id,
            "employee_code": emp_code,
            "department_name": dept,
            "total_shifts": total_shifts,
            "present_count": present_count,
            "absent_count": absent_count,
            "leave_count": leave_count,
            "late_count": late_count,
            "late_rate": round(late_rate, 1),
            "avg_delay_mins": round(avg_delay, 1),
            "delay_volatility": round(std_delay, 1),
            "weekend_leave_pct": round(weekend_leave_pct, 1),
            "missing_checkouts": missing_co,
            "missing_checkout_rate": round(missing_co_rate, 1),
            "absence_rate": round(absence_rate, 1),
        })

    return pd.DataFrame(records)


def compute_attendance_risk_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Compute normalized 0-100 Attendance Risk Scores & explainable drivers.

    Risk Model Weighting:
    - 40% Tardiness & Delay Volatility: recurring late arrivals & unpredictable arrival timing
    - 25% Unplanned Absenteeism: pure non-attendance without approved leave
    - 20% Pattern Opportunism: clustering leaves on Mondays & Fridays
    - 15% Administrative Non-Compliance: repeated missing clock-outs
    """
    features = extract_employee_risk_features(df)
    if features.empty:
        return pd.DataFrame()

    scores = []
    for _, row in features.iterrows():
        # Component 1: Lateness & Volatility (max 40 pts)
        # Cap late_rate at 50% for 30 pts, volatility at 30m for 10 pts
        c_late = min(row["late_rate"] / 50.0, 1.0) * 30.0
        c_vol = min(row["delay_volatility"] / 30.0, 1.0) * 10.0
        score_tardiness = c_late + c_vol

        # Component 2: Unplanned Absenteeism (max 25 pts)
        # Cap absence rate at 20% for 25 pts
        score_absence = min(row["absence_rate"] / 20.0, 1.0) * 25.0

        # Component 3: Weekend Clustering (max 20 pts)
        # Random distribution of leaves across 5 weekdays would be 40%.
        # Anything above 50% indicates pattern opportunism.
        if row["weekend_leave_pct"] > 40.0:
            score_clustering = min((row["weekend_leave_pct"] - 40.0) / 60.0, 1.0) * 20.0
        else:
            score_clustering = 0.0

        # Component 4: Missing check-outs (max 15 pts)
        score_admin = min(row["missing_checkout_rate"] / 25.0, 1.0) * 15.0

        total_risk = round(score_tardiness + score_absence + score_clustering + score_admin, 1)
        total_risk = min(max(total_risk, 0.0), 100.0)

        # Risk Tier
        if total_risk >= 65.0:
            tier = "High Risk (Action Needed)"
            badge_color = "#DC2626"
        elif total_risk >= 35.0:
            tier = "Moderate Risk (Watchlist)"
            badge_color = "#D97706"
        else:
            tier = "Low Risk (Healthy)"
            badge_color = "#059669"

        # Explainable primary drivers in plain English
        drivers = []
        if row["late_count"] >= 3:
            drivers.append(f"⏱️ Late on {row['late_count']} shifts ({row['late_rate']:.0f}% of days)")
        if row["delay_volatility"] >= 15.0:
            drivers.append(f"📊 Unpredictable arrival times (varies by ±{row['delay_volatility']:.0f} mins)")
        if row["weekend_leave_pct"] >= 65.0:
            drivers.append(f"📅 Leaves clustered near weekends ({row['weekend_leave_pct']:.0f}% taken on Mon/Fri)")
        if row["missing_checkouts"] >= 2:
            drivers.append(f"⚠️ Forgot to clock out ({row['missing_checkouts']} times)")
        if row["absence_rate"] >= 10.0:
            drivers.append(f"🚨 Unplanned absences ({row['absence_rate']:.0f}% of scheduled shifts)")

        if not drivers:
            drivers.append("✅ Dependable, consistent, and on time")

        scores.append({
            "employee_id": row["employee_id"],
            "employee_code": row["employee_code"],
            "department_name": row["department_name"],
            "risk_score": total_risk,
            "risk_tier": tier,
            "badge_color": badge_color,
            "late_count": row["late_count"],
            "late_rate": row["late_rate"],
            "delay_volatility": row["delay_volatility"],
            "weekend_leave_pct": row["weekend_leave_pct"],
            "missing_checkouts": row["missing_checkouts"],
            "absence_rate": row["absence_rate"],
            "primary_drivers": " • ".join(drivers),
            "driver_list": drivers,
        })

    result = pd.DataFrame(scores).sort_values("risk_score", ascending=False).reset_index(drop=True)
    return result
