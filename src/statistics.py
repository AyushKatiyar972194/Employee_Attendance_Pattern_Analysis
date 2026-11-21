"""Statistical analysis functions for P070.

Weekday attendance summary and high-absence date flagging
using Q3 + 1.5 × IQR threshold.
"""
from __future__ import annotations

import pandas as pd
import numpy as np


def weekday_attendance_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Summarise attendance rate by weekday.

    Returns DataFrame with columns: weekday_name, attendance_rate,
    present_count, eligible_count.
    Uses observed dates only.
    """
    if df.empty:
        return pd.DataFrame(
            columns=["weekday_name", "attendance_rate",
                      "present_count", "eligible_count"]
        )

    # Eligible: working day, not HOLIDAY, not APPROVED_LEAVE
    eligible = df[
        (df["is_working_day"] == 1)
        & (df["status_code"] != "HOLIDAY")
        & (df["status_code"] != "APPROVED_LEAVE")
    ].copy()

    if eligible.empty:
        return pd.DataFrame(
            columns=["weekday_name", "attendance_rate",
                      "present_count", "eligible_count"]
        )

    grouped = eligible.groupby("weekday_name").agg(
        present_count=("counts_as_present", "sum"),
        eligible_count=("counts_as_present", "count"),
    ).reset_index()

    grouped["attendance_rate"] = np.where(
        grouped["eligible_count"] > 0,
        (grouped["present_count"] / grouped["eligible_count"]) * 100,
        float("nan"),
    )

    # Order weekdays
    weekday_order = [
        "Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
        "Saturday", "Sunday",
    ]
    grouped["weekday_name"] = pd.Categorical(
        grouped["weekday_name"], categories=weekday_order, ordered=True,
    )
    grouped = grouped.sort_values("weekday_name").reset_index(drop=True)

    return grouped


def weekly_attendance_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Summarise attendance fulfillment and punctuality by calendar week.

    Returns DataFrame with columns:
      - week_number: int
      - week_label: str (e.g. 'Week 41 (Oct 05 - Oct 09)')
      - date_range: str
      - present_count: int
      - eligible_count: int
      - attendance_rate: float (%)
      - late_count: int
      - late_rate: float (%)
    """
    if df.empty or "attendance_date" not in df.columns:
        return pd.DataFrame(columns=[
            "week_number", "week_label", "date_range", "present_count",
            "eligible_count", "attendance_rate", "late_count", "late_rate",
        ])

    data = df.copy()
    data["dt"] = pd.to_datetime(data["attendance_date"], errors="coerce")
    data = data.dropna(subset=["dt"])

    if data.empty:
        return pd.DataFrame(columns=[
            "week_number", "week_label", "date_range", "present_count",
            "eligible_count", "attendance_rate", "late_count", "late_rate",
        ])

    data["week_number"] = data["dt"].dt.isocalendar().week

    # Eligible for attendance rate: working day, not HOLIDAY, not APPROVED_LEAVE
    eligible = data[
        (data["is_working_day"] == 1)
        & (data["status_code"] != "HOLIDAY")
        & (data["status_code"] != "APPROVED_LEAVE")
    ]

    rows = []
    for week_num, grp in data.groupby("week_number"):
        dates = grp["dt"]
        d_min = dates.min().strftime("%b %d")
        d_max = dates.max().strftime("%b %d")
        date_range = d_min if d_min == d_max else f"{d_min} – {d_max}"
        week_label = f"Week {week_num} ({date_range})"

        elig_grp = eligible[eligible["week_number"] == week_num]
        pres_count = int(elig_grp["counts_as_present"].sum()) if not elig_grp.empty and "counts_as_present" in elig_grp.columns else 0
        elig_count = int(elig_grp["counts_as_present"].count()) if not elig_grp.empty and "counts_as_present" in elig_grp.columns else 0
        att_rate = (pres_count / elig_count * 100.0) if elig_count > 0 else float("nan")

        present_shifts = grp[grp["status_code"] == "PRESENT"]
        late_count = int(present_shifts["is_late"].sum()) if not present_shifts.empty and "is_late" in present_shifts.columns else 0
        late_rate = (late_count / len(present_shifts) * 100.0) if not present_shifts.empty else float("nan")

        rows.append({
            "week_number": int(week_num),
            "week_label": week_label,
            "date_range": date_range,
            "present_count": pres_count,
            "eligible_count": elig_count,
            "attendance_rate": round(att_rate, 2) if pd.notna(att_rate) else 0.0,
            "late_count": late_count,
            "late_rate": round(late_rate, 2) if pd.notna(late_rate) else 0.0,
        })

    return pd.DataFrame(rows).sort_values("week_number").reset_index(drop=True)


def flag_high_absence_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Flag dates with unusually high absence using IQR method.

    Threshold: Q3 + 1.5 × IQR on per-date absence rates.
    Uses observed dates only.

    Returns DataFrame with columns: attendance_date, absence_count,
    eligible_count, absence_rate, is_flagged, threshold.

    If fewer than 4 dates exist, all dates are unflagged (sample too small).
    """
    if df.empty:
        return pd.DataFrame(
            columns=["attendance_date", "absence_count", "eligible_count",
                      "absence_rate", "is_flagged", "threshold"]
        )

    # Eligible: working day, not HOLIDAY, not APPROVED_LEAVE
    eligible = df[
        (df["is_working_day"] == 1)
        & (df["status_code"] != "HOLIDAY")
        & (df["status_code"] != "APPROVED_LEAVE")
    ].copy()

    if eligible.empty:
        return pd.DataFrame(
            columns=["attendance_date", "absence_count", "eligible_count",
                      "absence_rate", "is_flagged", "threshold"]
        )

    daily = eligible.groupby("attendance_date").agg(
        absence_count=("counts_as_absence", "sum"),
        eligible_count=("counts_as_absence", "count"),
    ).reset_index()

    daily["absence_rate"] = np.where(
        daily["eligible_count"] > 0,
        (daily["absence_count"] / daily["eligible_count"]) * 100,
        float("nan"),
    )

    # IQR-based threshold
    rates = daily["absence_rate"].dropna()
    if len(rates) < 4:
        daily["is_flagged"] = False
        daily["threshold"] = float("nan")
    else:
        q1 = rates.quantile(0.25)
        q3 = rates.quantile(0.75)
        iqr = q3 - q1
        threshold = q3 + 1.5 * iqr
        daily["threshold"] = threshold
        daily["is_flagged"] = daily["absence_rate"] > threshold

    daily["attendance_date"] = pd.to_datetime(daily["attendance_date"])
    return daily
