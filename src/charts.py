"""Reusable Plotly chart builders for Enterprise Attendance Analytics.

Polished executive theme, responsive layouts, clear typography, and accurate outlier representations.
"""
from __future__ import annotations

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

PLOT_LAYOUT_DEFAULTS = dict(
    font=dict(family="Plus Jakarta Sans, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif", color="#1E293B", size=12),
    plot_bgcolor="#FFFFFF",
    paper_bgcolor="#FFFFFF",
    margin=dict(l=40, r=40, t=50, b=40),
)


def _empty_figure(message: str = "No data available") -> go.Figure:
    """Return a clean blank figure with an informational annotation."""
    fig = go.Figure()
    fig.add_annotation(
        text=message, xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=14, color="#94A3B8"),
    )
    fig.update_layout(
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        height=320,
        **PLOT_LAYOUT_DEFAULTS,
    )
    return fig


# ---------------------------------------------------------------------------
# 1. Daily status stacked bar
# ---------------------------------------------------------------------------

def daily_status_chart(daily_counts: pd.DataFrame) -> go.Figure:
    """Stacked bar chart of daily status counts."""
    if daily_counts.empty or "attendance_date" not in daily_counts.columns:
        return _empty_figure("No daily status data available")

    try:
        df = daily_counts.copy()
        df["attendance_date"] = pd.to_datetime(df["attendance_date"], errors="coerce")
        df = df.dropna(subset=["attendance_date"]).sort_values("attendance_date")
        if df.empty:
            return _empty_figure("No daily status data available")

        status_cols = [c for c in df.columns if c != "attendance_date"]
        color_map = {
            "PRESENT": "#059669",
            "ABSENT": "#E11D48",
            "APPROVED_LEAVE": "#D97706",
            "HOLIDAY": "#6366F1",
        }

        fig = go.Figure()
        for col in status_cols:
            if col in df.columns:
                fig.add_trace(go.Bar(
                    x=df["attendance_date"].dt.strftime("%b %d"),
                    y=df[col],
                    name=col.replace("_", " ").title(),
                    marker_color=color_map.get(col, "#94A3B8"),
                    marker_line_width=0,
                    hovertemplate="<b>Date:</b> %{x}<br><b>Status:</b> " + col.replace("_", " ").title() + "<br><b>Count:</b> %{y}<extra></extra>"
                ))

        fig.update_layout(
            barmode="stack",
            height=380,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(title="", showgrid=False, linecolor="#CBD5E1"),
            yaxis=dict(title="Employees", gridcolor="#F1F5F9", linecolor="#CBD5E1"),
            **PLOT_LAYOUT_DEFAULTS,
        )
        return fig
    except Exception:
        return _empty_figure("Unable to render daily status chart")


# ---------------------------------------------------------------------------
# 2. Daily Attendance Rate Trend
# ---------------------------------------------------------------------------

def daily_attendance_trend_chart(daily_trend: pd.DataFrame, org_avg: float | None = None) -> go.Figure:
    """Line and marker chart showing day-by-day attendance rate across observation dates."""
    if daily_trend.empty:
        return _empty_figure("No observation dates available")

    df = daily_trend.copy()
    df["formatted_date"] = df["attendance_date"].dt.strftime("%b %d")

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["formatted_date"],
        y=df["attendance_rate"],
        mode="lines+markers+text",
        name="Daily Attendance Rate",
        line=dict(color="#2563EB", width=3),
        marker=dict(size=8, color="#1D4ED8"),
        text=df["attendance_rate"].round(1).astype(str) + "%",
        textposition="top center",
        hovertemplate="<b>Date:</b> %{x}<br><b>Attendance Rate:</b> %{y:.1f}%<extra></extra>"
    ))

    if org_avg is not None and not np.isnan(org_avg):
        fig.add_hline(
            y=org_avg, line_dash="dash", line_color="#10B981", line_width=1.5,
            annotation_text=f"Org Weighted Mean: {org_avg:.1f}%",
            annotation_position="bottom right"
        )

    fig.update_layout(
        height=350,
        showlegend=False,
        xaxis=dict(title="", linecolor="#CBD5E1"),
        yaxis=dict(title="Attendance Rate (%)", range=[80, 105], gridcolor="#F1F5F9", linecolor="#CBD5E1"),
        **PLOT_LAYOUT_DEFAULTS,
    )
    return fig


# ---------------------------------------------------------------------------
# 3. Department attendance rates horizontal bar
# ---------------------------------------------------------------------------

def department_rates_chart(
    dept_rates: pd.DataFrame,
    org_rate: float | None = None,
    org_avg: float | None = None,
) -> go.Figure:
    """Horizontal bar chart of attendance rates by department with org reference line."""
    if org_rate is None and org_avg is not None:
        org_rate = org_avg

    if dept_rates.empty or "attendance_rate" not in dept_rates.columns or dept_rates["attendance_rate"].dropna().empty:
        return _empty_figure("No department records available")

    try:
        df = dept_rates.dropna(subset=["attendance_rate"]).sort_values("attendance_rate", ascending=True)
        if df.empty:
            return _empty_figure("No department records available")

        fig = px.bar(
            df,
            x="attendance_rate",
            y="department_name",
            orientation="h",
            labels={"attendance_rate": "Fulfillment Rate (%)", "department_name": ""},
            color="attendance_rate",
            color_continuous_scale=["#93C5FD", "#2563EB", "#1D4ED8"],
        )
        
        if org_rate is not None and not np.isnan(org_rate):
            fig.add_vline(
                x=org_rate, line_dash="dash", line_color="#10B981", line_width=2,
                annotation_text=f"Org Avg: {org_rate:.1f}%",
                annotation_position="top right",
            )

        fig.update_layout(
            height=360,
            showlegend=False,
            coloraxis_showscale=False,
            xaxis=dict(range=[80, 102], gridcolor="#F1F5F9", linecolor="#CBD5E1"),
            yaxis=dict(linecolor="#CBD5E1"),
            **PLOT_LAYOUT_DEFAULTS,
        )
        fig.update_traces(
            text=df["attendance_rate"].round(1).astype(str) + "%",
            textposition="outside",
            textfont=dict(size=12, color="#0F172A"),
            marker_line_width=0,
            hovertemplate="<b>%{y}</b><br>Attendance Rate: %{x:.1f}%<extra></extra>"
        )
        return fig
    except Exception:
        return _empty_figure("Unable to render department chart")


# ---------------------------------------------------------------------------
# 4. Weekday attendance pattern
# ---------------------------------------------------------------------------

def weekday_pattern_chart(weekday_summary: pd.DataFrame) -> go.Figure:
    """Bar chart of attendance rate by weekday."""
    if (
        weekday_summary.empty
        or "weekday_name" not in weekday_summary.columns
        or "attendance_rate" not in weekday_summary.columns
        or weekday_summary["attendance_rate"].dropna().empty
    ):
        return _empty_figure("No weekday pattern data available")

    try:
        fig = px.bar(
            weekday_summary,
            x="weekday_name",
            y="attendance_rate",
            labels={"attendance_rate": "Fulfillment Rate (%)", "weekday_name": ""},
            color="attendance_rate",
            color_continuous_scale=["#99F6E4", "#0D9488", "#115E59"],
        )
        fig.update_layout(
            height=360,
            showlegend=False,
            coloraxis_showscale=False,
            yaxis=dict(range=[80, 102], gridcolor="#F1F5F9", linecolor="#CBD5E1"),
            xaxis=dict(linecolor="#CBD5E1"),
            **PLOT_LAYOUT_DEFAULTS,
        )
        fig.update_traces(
            text=weekday_summary["attendance_rate"].round(1).astype(str) + "%",
            textposition="outside",
            textfont=dict(size=12, color="#0F172A"),
            marker_line_width=0,
            hovertemplate="<b>%{x}</b><br>Rate: %{y:.2f}%<extra></extra>"
        )
        return fig
    except Exception:
        return _empty_figure("Unable to render weekday pattern chart")


# ---------------------------------------------------------------------------
# 5. Late arrivals by department
# ---------------------------------------------------------------------------

def late_by_department_chart(late_dept: pd.DataFrame) -> go.Figure:
    """Bar chart of late arrival rate by department."""
    if late_dept.empty or "late_rate" not in late_dept.columns or late_dept["late_rate"].dropna().empty:
        return _empty_figure("No late arrival records available")

    try:
        df = late_dept.dropna(subset=["late_rate"]).sort_values("late_rate", ascending=True)
        if df.empty:
            return _empty_figure("No late arrival records available")

        fig = px.bar(
            df,
            x="late_rate",
            y="department_name",
            orientation="h",
            labels={"late_rate": "Late Arrival Rate (%)", "department_name": ""},
            color="late_rate",
            color_continuous_scale=["#FECDD3", "#F43F5E", "#BE123C"],
        )
        fig.update_layout(
            height=360,
            showlegend=False,
            coloraxis_showscale=False,
            xaxis=dict(gridcolor="#F1F5F9", linecolor="#CBD5E1"),
            yaxis=dict(linecolor="#CBD5E1"),
            **PLOT_LAYOUT_DEFAULTS,
        )
        fig.update_traces(
            text=df["late_rate"].round(1).astype(str) + "%",
            textposition="outside",
            textfont=dict(size=12, color="#0F172A"),
            marker_line_width=0,
            hovertemplate="<b>%{y}</b><br>Late Incidents: " + df["late_count"].astype(str) + " / " + df["total_present"].astype(str) + " (%{x:.1f}%)<extra></extra>"
        )
        return fig
    except Exception:
        return _empty_figure("Unable to render late arrivals chart")


# ---------------------------------------------------------------------------
# 6. Elapsed duration distribution
# ---------------------------------------------------------------------------

def elapsed_duration_chart(durations: pd.Series) -> go.Figure:
    """Histogram of elapsed recorded durations in minutes."""
    valid = durations.dropna()
    if valid.empty:
        return _empty_figure("No duration data available (missing timestamps)")

    fig = px.histogram(
        x=valid,
        nbins=30,
        labels={"x": "Duration (minutes)", "y": "Shift Count"},
        color_discrete_sequence=["#2563EB"],
    )
    fig.update_layout(
        height=350,
        xaxis=dict(title="Recorded Elapsed Duration (minutes)", gridcolor="#F1F5F9", linecolor="#CBD5E1"),
        yaxis=dict(title="Logged Shifts", gridcolor="#F1F5F9", linecolor="#CBD5E1"),
        showlegend=False,
        **PLOT_LAYOUT_DEFAULTS,
    )
    return fig


# ---------------------------------------------------------------------------
# 7. Check-in delay scatter / strip
# ---------------------------------------------------------------------------

def checkin_delay_chart(df: pd.DataFrame) -> go.Figure:
    """Strip plot of arrival delay (minutes relative to scheduled start)."""
    if df.empty or "status_code" not in df.columns or "arrival_delay_minutes" not in df.columns:
        return _empty_figure("No check-in delay data available")

    try:
        present = df[df["status_code"] == "PRESENT"].copy()
        if present.empty or "arrival_delay_minutes" not in present.columns:
            return _empty_figure("No check-in delay data available")

        present["arrival_delay_minutes"] = pd.to_numeric(
            present["arrival_delay_minutes"], errors="coerce"
        )
        valid = present.dropna(subset=["arrival_delay_minutes"])
        if valid.empty:
            return _empty_figure("No check-in delay data available")

        dept_col = "department_name" if "department_name" in valid.columns else None

        fig = px.strip(
            valid,
            x=dept_col,
            y="arrival_delay_minutes",
            color=dept_col,
            labels={
                "arrival_delay_minutes": "Arrival Variance (minutes)",
                "department_name": "",
            },
            color_discrete_sequence=["#2563EB", "#0D9488", "#D97706", "#E11D48", "#8B5CF6"],
        )
        fig.add_hline(
            y=0, line_dash="solid", line_color="#94A3B8", line_width=1,
            annotation_text="Scheduled Start (09:00)", annotation_position="top left",
        )
        fig.add_hline(
            y=10, line_dash="dash", line_color="#EF4444", line_width=1.5,
            annotation_text="Grace Buffer Limit (+10m)", annotation_position="bottom left",
        )
        fig.update_layout(
            height=360,
            showlegend=False,
            yaxis=dict(gridcolor="#F1F5F9", linecolor="#CBD5E1"),
            xaxis=dict(linecolor="#CBD5E1"),
            **PLOT_LAYOUT_DEFAULTS,
        )
        fig.update_traces(
            hovertemplate="<b>Department:</b> %{x}<br><b>Delay:</b> %{y} min<extra></extra>"
        )
        return fig
    except Exception:
        return _empty_figure("Unable to render check-in delay chart")


# ---------------------------------------------------------------------------
# 8. High-absence flagged dates
# ---------------------------------------------------------------------------

def high_absence_chart(flagged_df: pd.DataFrame) -> go.Figure:
    """Bar chart of daily absence rates with flagged outliers highlighted."""
    if flagged_df.empty or "attendance_date" not in flagged_df.columns or "absence_rate" not in flagged_df.columns:
        return _empty_figure("No absence records available")

    try:
        df = flagged_df.copy()
        df["attendance_date"] = pd.to_datetime(df["attendance_date"], errors="coerce")
        df = df.dropna(subset=["attendance_date"]).sort_values("attendance_date")
        if df.empty:
            return _empty_figure("No absence records available")

        is_flagged = df["is_flagged"] if "is_flagged" in df.columns else [False] * len(df)
        colors = ["#EF4444" if f else "#64748B" for f in is_flagged]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df["attendance_date"].dt.strftime("%b %d"),
            y=df["absence_rate"],
            marker_color=colors,
            name="Absence Rate",
            marker_line_width=0,
            hovertemplate="<b>Date:</b> %{x}<br><b>Absence Rate:</b> %{y:.2f}%<extra></extra>"
        ))

        if "threshold" in df.columns:
            threshold = df["threshold"].dropna()
            if not threshold.empty:
                t_val = threshold.iloc[0]
                fig.add_hline(
                    y=t_val, line_dash="dash", line_color="#EF4444", line_width=1.5,
                    annotation_text=f"IQR Anomaly Threshold (Q3+1.5*IQR): {t_val:.1f}%",
                    annotation_position="top right",
                )

        fig.update_layout(
            height=350,
            xaxis=dict(title="", showgrid=False, linecolor="#CBD5E1"),
            yaxis=dict(title="Absence Rate (%)", gridcolor="#F1F5F9", linecolor="#CBD5E1"),
            showlegend=False,
            **PLOT_LAYOUT_DEFAULTS,
        )
        return fig
    except Exception:
        return _empty_figure("Unable to render absence chart")


# ---------------------------------------------------------------------------
# 9. Weekly Attendance Trend
# ---------------------------------------------------------------------------

def weekly_attendance_trend_chart(weekly_df: pd.DataFrame) -> go.Figure:
    """Bar & line chart showing weekly attendance fulfillment and lateness rate."""
    if weekly_df.empty or "week_label" not in weekly_df.columns:
        return _empty_figure("No weekly trend data available")

    try:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=weekly_df["week_label"],
            y=weekly_df["attendance_rate"],
            name="Attendance Rate (%)",
            marker_color="#2563EB",
            marker_line_width=0,
            text=weekly_df["attendance_rate"].round(1).astype(str) + "%",
            textposition="inside",
            textfont=dict(color="#FFFFFF", size=12),
            hovertemplate="<b>%{x}</b><br>Attendance: %{y:.1f}%<extra></extra>",
        ))
        if "late_rate" in weekly_df.columns:
            fig.add_trace(go.Scatter(
                x=weekly_df["week_label"],
                y=weekly_df["late_rate"],
                name="Late Rate (%)",
                mode="lines+markers+text",
                line=dict(color="#F59E0B", width=2.5),
                marker=dict(size=8, color="#D97706"),
                text=weekly_df["late_rate"].round(1).astype(str) + "%",
                textposition="top center",
                hovertemplate="<b>%{x}</b><br>Late Rate: %{y:.1f}%<extra></extra>",
            ))

        fig.update_layout(
            height=340,
            yaxis=dict(title="Rate (%)", range=[0, 110], gridcolor="#F1F5F9", linecolor="#CBD5E1"),
            xaxis=dict(title="", linecolor="#CBD5E1"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            **PLOT_LAYOUT_DEFAULTS,
        )
        return fig
    except Exception:
        return _empty_figure("Unable to render weekly trend chart")


# ---------------------------------------------------------------------------
# 10. Status Proportion Donut Chart
# ---------------------------------------------------------------------------

def status_donut_chart(df: pd.DataFrame, attendance_rate: float | None = None) -> go.Figure:
    """Modern donut chart of attendance status proportion with center KPI."""
    if df.empty or "status_code" not in df.columns:
        return _empty_figure("No status breakdown data available")

    try:
        counts = df["status_code"].value_counts()
        labels = [c.replace("_", " ").title() for c in counts.index]
        values = counts.values.tolist()

        color_map = {
            "PRESENT": "#10B981",         # Emerald Green
            "APPROVED_LEAVE": "#F59E0B",   # Amber / Orange
            "ABSENT": "#EF4444",           # Red
            "HOLIDAY": "#6366F1",          # Indigo
        }
        colors = [color_map.get(k, "#94A3B8") for k in counts.index]

        center_text = f"<b>{attendance_rate:.1f}%</b><br><span style='font-size:11px;color:#64748B;'>Attendance</span>" if attendance_rate is not None and not np.isnan(attendance_rate) else ""

        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.62,
            marker=dict(colors=colors, line=dict(color="#FFFFFF", width=2)),
            textinfo="percent",
            textfont=dict(size=12, color="#FFFFFF", family="Plus Jakarta Sans"),
            hovertemplate="<b>%{label}</b><br>Count: %{value:,}<br>Proportion: %{percent}<extra></extra>",
        )])

        layout_kwargs = {**PLOT_LAYOUT_DEFAULTS, "margin": dict(l=20, r=20, t=20, b=20)}
        fig.update_layout(
            height=280,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
            annotations=[dict(text=center_text, x=0.5, y=0.5, font_size=18, showarrow=False)],
            **layout_kwargs,
        )
        return fig
    except Exception:
        return _empty_figure("Unable to render status donut chart")


# ---------------------------------------------------------------------------
# 11. Department x Weekday Attendance Heatmap
# ---------------------------------------------------------------------------

def department_weekday_heatmap(df: pd.DataFrame) -> go.Figure:
    """Annotated heatmap showing attendance fulfillment rate across departments and weekdays."""
    if df.empty or "department_name" not in df.columns or "weekday_name" not in df.columns:
        return _empty_figure("No department weekday data available")

    try:
        eligible = df[
            (df.get("is_working_day", 1) == 1)
            & (df["status_code"] != "HOLIDAY")
            & (df["status_code"] != "APPROVED_LEAVE")
        ]
        if eligible.empty:
            return _empty_figure("No eligible working shifts available")

        weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

        pivot = eligible.pivot_table(
            index="department_name",
            columns="weekday_name",
            values="counts_as_present",
            aggfunc=lambda x: round((x.sum() / len(x)) * 100, 1),
        )

        valid_cols = [c for c in weekdays if c in pivot.columns]
        if not valid_cols:
            return _empty_figure("No weekday columns available")

        pivot = pivot[valid_cols]

        fig = px.imshow(
            pivot,
            labels=dict(x="Weekday", y="Department", color="Fulfillment %"),
            x=pivot.columns,
            y=pivot.index,
            color_continuous_scale=[
                (0.0, "#FEF3C7"),  # Amber light for ~90%
                (0.5, "#A7F3D0"),  # Light emerald
                (1.0, "#059669"),  # Deep green for 100%
            ],
            text_auto=True,
            aspect="auto",
        )

        fig.update_layout(
            height=360,
            xaxis=dict(title="", side="top", linecolor="#CBD5E1"),
            yaxis=dict(title="", linecolor="#CBD5E1"),
            coloraxis_colorbar=dict(title="Rate (%)", thickness=14, len=0.8),
            **PLOT_LAYOUT_DEFAULTS,
        )
        fig.update_traces(
            texttemplate="%{z:.1f}%",
            hovertemplate="<b>Department:</b> %{y}<br><b>Day:</b> %{x}<br><b>Attendance Rate:</b> %{z:.1f}%<extra></extra>",
        )
        return fig
    except Exception:
        return _empty_figure("Unable to render heatmap")


# ---------------------------------------------------------------------------
# 12. Department Quadrant Matrix (Attendance vs. Punctuality)
# ---------------------------------------------------------------------------

def department_quadrant_chart(df: pd.DataFrame) -> go.Figure:
    """2x2 Quadrant scatter chart comparing Department Attendance Fulfillment vs Punctuality Rate."""
    if df.empty or "department_name" not in df.columns:
        return _empty_figure("No department records available")

    try:
        from src.metrics import department_attendance_rates

        dept_rates = department_attendance_rates(df)
        if dept_rates.empty:
            return _empty_figure("No department rates available")

        present = df[df["status_code"] == "PRESENT"]
        dept_lates = present.groupby("department_name").agg(
            late_count=("is_late", "sum"),
            total_present=("is_late", "count"),
            headcount=("employee_id", "nunique"),
        ).reset_index()

        dept_lates["punctuality_rate"] = np.where(
            dept_lates["total_present"] > 0,
            ((dept_lates["total_present"] - dept_lates["late_count"]) / dept_lates["total_present"]) * 100.0,
            0.0,
        )

        merged = pd.merge(dept_rates, dept_lates, on="department_name").dropna(subset=["attendance_rate", "punctuality_rate"])
        if merged.empty:
            return _empty_figure("No department metric data available")

        mean_att = float(merged["attendance_rate"].mean())
        mean_punc = float(merged["punctuality_rate"].mean())

        fig = px.scatter(
            merged,
            x="attendance_rate",
            y="punctuality_rate",
            text="department_name",
            size="headcount",
            color="department_name",
            size_max=32,
            labels={
                "attendance_rate": "Attendance Fulfillment Rate (%)",
                "punctuality_rate": "Punctuality Rate (% On-Time)",
            },
            color_discrete_sequence=["#2563EB", "#0D9488", "#D97706", "#DC2626", "#8B5CF6", "#EC4899", "#10B981", "#6366F1"],
        )

        fig.add_vline(x=mean_att, line_dash="dash", line_color="#94A3B8", annotation_text=f"Avg Att ({mean_att:.1f}%)", annotation_position="top left")
        fig.add_hline(y=mean_punc, line_dash="dash", line_color="#94A3B8", annotation_text=f"Avg Punc ({mean_punc:.1f}%)", annotation_position="bottom right")

        min_x = min(merged["attendance_rate"].min() - 1, 90)
        max_x = max(merged["attendance_rate"].max() + 1, 99)
        min_y = min(merged["punctuality_rate"].min() - 3, 60)
        max_y = max(merged["punctuality_rate"].max() + 3, 98)

        fig.add_annotation(x=max_x - 0.5, y=max_y - 1, text="🌟 High Attendance & Punctual", showarrow=False, font=dict(color="#059669", size=10, weight="bold"))
        fig.add_annotation(x=max_x - 0.5, y=min_y + 2, text="🕒 High Attendance, Frequent Late", showarrow=False, font=dict(color="#D97706", size=10, weight="bold"))

        fig.update_traces(
            textposition="top center",
            hovertemplate="<b>%{text}</b><br>Attendance: %{x:.1f}%<br>Punctuality: %{y:.1f}%<extra></extra>",
        )

        fig.update_layout(
            height=400,
            showlegend=False,
            xaxis=dict(range=[min_x, max_x], gridcolor="#F1F5F9", linecolor="#CBD5E1"),
            yaxis=dict(range=[min_y, max_y], gridcolor="#F1F5F9", linecolor="#CBD5E1"),
            **PLOT_LAYOUT_DEFAULTS,
        )
        return fig
    except Exception:
        return _empty_figure("Unable to render quadrant chart")


# ---------------------------------------------------------------------------
# 13. Arrival Time Distribution (On-Time vs Late Bell Curve)
# ---------------------------------------------------------------------------

def arrival_distribution_chart(df: pd.DataFrame) -> go.Figure:
    """Histogram of arrival delays relative to scheduled 09:00 start with on-time vs late color coding."""
    if df.empty or "arrival_delay_minutes" not in df.columns:
        return _empty_figure("No arrival delay data available")

    try:
        present = df[df["status_code"] == "PRESENT"].copy()
        present["arrival_delay_minutes"] = pd.to_numeric(present["arrival_delay_minutes"], errors="coerce")
        valid = present.dropna(subset=["arrival_delay_minutes"])
        if valid.empty:
            return _empty_figure("No arrival delay records found")

        ontime = valid[valid["arrival_delay_minutes"] <= 10]["arrival_delay_minutes"]
        late = valid[valid["arrival_delay_minutes"] > 10]["arrival_delay_minutes"]

        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=ontime,
            name="On-Time (≤ 10m Grace)",
            marker_color="#10B981",
            xbins=dict(start=-30, end=10, size=2),
            hovertemplate="<b>Delay:</b> %{x} min<br><b>Shifts:</b> %{y}<extra></extra>",
        ))
        fig.add_trace(go.Histogram(
            x=late,
            name="Late Arrival (> 10m Grace)",
            marker_color="#EF4444",
            xbins=dict(start=10, end=60, size=2),
            hovertemplate="<b>Delay:</b> %{x} min (Late)<br><b>Shifts:</b> %{y}<extra></extra>",
        ))

        fig.add_vline(
            x=10, line_dash="dash", line_color="#DC2626", line_width=2,
            annotation_text="Grace Cutoff (+10 min)", annotation_position="top right",
        )
        fig.add_vline(
            x=0, line_dash="solid", line_color="#64748B", line_width=1.5,
            annotation_text="Scheduled Start (09:00)", annotation_position="top left",
        )

        fig.update_layout(
            barmode="overlay",
            height=340,
            xaxis=dict(title="Arrival Variance in Minutes (0 = 09:00 AM)", gridcolor="#F1F5F9", linecolor="#CBD5E1"),
            yaxis=dict(title="Number of Shifts", gridcolor="#F1F5F9", linecolor="#CBD5E1"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            **PLOT_LAYOUT_DEFAULTS,
        )
        return fig
    except Exception:
        return _empty_figure("Unable to render arrival distribution chart")


# ---------------------------------------------------------------------------
# 14. Punctuality Donut Chart
# ---------------------------------------------------------------------------

def punctuality_donut_chart(late_metrics: dict) -> go.Figure:
    """Donut chart showing On-Time vs Late Check-in proportion with center percentage."""
    if not late_metrics or late_metrics.get("total_present", 0) == 0:
        return _empty_figure("No punctuality data available")

    try:
        punc_count = late_metrics.get("punctual_count", 0)
        late_count = late_metrics.get("late_count", 0)
        total = punc_count + late_count
        punc_rate = (punc_count / total * 100.0) if total > 0 else 0.0

        fig = go.Figure(data=[go.Pie(
            labels=["On-Time (≤ 10m Grace)", "Late (> 10m Grace)"],
            values=[punc_count, late_count],
            hole=0.62,
            marker=dict(colors=["#10B981", "#F59E0B"], line=dict(color="#FFFFFF", width=2)),
            textinfo="percent",
            textfont=dict(size=12, color="#FFFFFF", family="Plus Jakarta Sans"),
            hovertemplate="<b>%{label}</b><br>Shifts: %{value:,}<br>Rate: %{percent}<extra></extra>",
        )])

        center_text = f"<b>{punc_rate:.1f}%</b><br><span style='font-size:11px;color:#64748B;'>On-Time</span>"

        layout_kwargs = {**PLOT_LAYOUT_DEFAULTS, "margin": dict(l=20, r=20, t=20, b=20)}
        fig.update_layout(
            height=280,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
            annotations=[dict(text=center_text, x=0.5, y=0.5, font_size=18, showarrow=False)],
            **layout_kwargs,
        )
        return fig
    except Exception:
        return _empty_figure("Unable to render punctuality donut")


# ---------------------------------------------------------------------------
# 12. Predictive Attendance Risk Tier Donut & Scatter
# ---------------------------------------------------------------------------

def risk_tier_donut_chart(risk_df: pd.DataFrame) -> go.Figure:
    """Donut chart showing proportion of employees in each risk tier."""
    if risk_df is None or risk_df.empty or "risk_tier" not in risk_df.columns:
        return _empty_figure("No risk score data available")

    try:
        tier_counts = risk_df["risk_tier"].value_counts()
        colors = {
            "Low Risk (Healthy)": "#10B981",
            "Moderate Risk (Watchlist)": "#F59E0B",
            "High Risk (Action Needed)": "#EF4444",
        }
        ordered_tiers = [t for t in ["Low Risk (Healthy)", "Moderate Risk (Watchlist)", "High Risk (Action Needed)"] if t in tier_counts.index]
        tier_vals = [tier_counts[t] for t in ordered_tiers]
        tier_colors = [colors[t] for t in ordered_tiers]

        high_risk_count = tier_counts.get("High Risk (Action Needed)", 0)
        center_text = f"<b>{high_risk_count}</b><br><span style='font-size:11px;color:#EF4444;'>High Risk</span>"

        fig = go.Figure(data=[go.Pie(
            labels=ordered_tiers,
            values=tier_vals,
            hole=0.62,
            marker=dict(colors=tier_colors, line=dict(color="#FFFFFF", width=2)),
            textinfo="percent",
            textfont=dict(size=12, color="#FFFFFF", family="Plus Jakarta Sans"),
            hovertemplate="<b>%{label}</b><br>Staff: %{value}<br>Proportion: %{percent}<extra></extra>",
        )])

        layout_kwargs = {**PLOT_LAYOUT_DEFAULTS, "margin": dict(l=20, r=20, t=20, b=20)}
        fig.update_layout(
            height=280,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
            annotations=[dict(text=center_text, x=0.5, y=0.5, font_size=18, showarrow=False)],
            **layout_kwargs,
        )
        return fig
    except Exception:
        return _empty_figure("Unable to render risk tier donut")


def risk_scatter_chart(risk_df: pd.DataFrame) -> go.Figure:
    """Scatter plot of Delay Volatility vs Late Arrival Rate with risk-encoded points."""
    if risk_df is None or risk_df.empty:
        return _empty_figure("No risk data available")

    try:
        color_discrete_map = {
            "Low Risk (Healthy)": "#10B981",
            "Moderate Risk (Watchlist)": "#F59E0B",
            "High Risk (Action Needed)": "#EF4444",
        }

        fig = px.scatter(
            risk_df,
            x="delay_volatility",
            y="late_rate",
            color="risk_tier",
            size="risk_score",
            hover_name="employee_code",
            hover_data={
                "department_name": True,
                "risk_score": True,
                "late_count": True,
                "weekend_leave_pct": True,
                "delay_volatility": ":.1f",
                "late_rate": ":.1f",
                "risk_tier": False,
            },
            color_discrete_map=color_discrete_map,
            labels={
                "delay_volatility": "Arrival Delay Volatility (Std Dev Minutes)",
                "late_rate": "Late Arrival Rate (%)",
                "risk_tier": "Risk Tier",
            },
        )

        fig.update_traces(marker=dict(line=dict(width=1, color="#FFFFFF")))
        fig.update_layout(
            height=380,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(gridcolor="#F1F5F9", linecolor="#CBD5E1", title="Arrival Delay Volatility (± Minutes)"),
            yaxis=dict(gridcolor="#F1F5F9", linecolor="#CBD5E1", title="Late Arrival Rate (% of shifts)"),
            **PLOT_LAYOUT_DEFAULTS,
        )
        return fig
    except Exception:
        return _empty_figure("Unable to render risk scatter")


# ---------------------------------------------------------------------------
# 13. Policy Sensitivity Curve & Financial Loss Waterfall
# ---------------------------------------------------------------------------

def grace_period_sensitivity_chart(df: pd.DataFrame) -> go.Figure:
    """Sensitivity curve showing simulated punctuality across 0 to 30 min grace thresholds."""
    if df is None or df.empty or "arrival_delay_minutes" not in df.columns:
        return _empty_figure("No delay data available")

    try:
        present = df[(df["status_code"] == "PRESENT") & df["arrival_delay_minutes"].notna()]
        total_p = len(present)
        if total_p == 0:
            return _empty_figure("No present records available")

        thresholds = list(range(0, 31, 2))
        rates = []
        for t in thresholds:
            on_time = (present["arrival_delay_minutes"] <= t).sum()
            rates.append(round(on_time / total_p * 100.0, 1))

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=thresholds,
            y=rates,
            mode="lines+markers",
            line=dict(color="#2563EB", width=3, shape="spline"),
            marker=dict(size=7, color="#1D4ED8", line=dict(width=1.5, color="#FFFFFF")),
            name="Simulated Punctuality Rate",
            hovertemplate="Grace Threshold: <b>%{x} mins</b><br>Punctuality: <b>%{y}%</b><extra></extra>",
        ))

        # Add vertical marker at current baseline (10 mins)
        fig.add_vline(x=10, line_dash="dash", line_color="#EF4444", annotation_text="Baseline (10m)", annotation_position="top left")
        # Add vertical marker at recommended threshold (15 mins)
        fig.add_vline(x=15, line_dash="dot", line_color="#10B981", annotation_text="Recommended (15m)", annotation_position="top right")

        fig.update_layout(
            height=340,
            xaxis=dict(title="Allowed Grace Period Threshold (Minutes past 09:00 AM)", dtick=2, gridcolor="#F1F5F9", linecolor="#CBD5E1"),
            yaxis=dict(title="Simulated On-Time Rate (%)", gridcolor="#F1F5F9", linecolor="#CBD5E1", range=[70, 100]),
            **PLOT_LAYOUT_DEFAULTS,
        )
        return fig
    except Exception:
        return _empty_figure("Unable to render policy curve")


def financial_loss_breakdown_chart(fin: dict) -> go.Figure:
    """Bar chart illustrating financial productivity loss breakdown."""
    if not fin:
        return _empty_figure("No financial data available")

    try:
        categories = ["Late Arrival Leakage", "Unplanned Absence Exposure", "Total Productivity Loss"]
        values = [fin.get("late_cost", 0), fin.get("absence_cost", 0), fin.get("total_financial_loss", 0)]
        colors = ["#F59E0B", "#EF4444", "#1E293B"]

        fig = go.Figure(go.Bar(
            x=categories,
            y=values,
            marker_color=colors,
            text=[f"₹{v:,.0f}" for v in values],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Loss: ₹%{y:,.2f}<extra></extra>",
        ))

        fig.update_layout(
            height=320,
            yaxis=dict(title="Financial Exposure (₹ INR)", gridcolor="#F1F5F9", linecolor="#CBD5E1"),
            xaxis=dict(showgrid=False, linecolor="#CBD5E1"),
            **PLOT_LAYOUT_DEFAULTS,
        )
        return fig
    except Exception:
        return _empty_figure("Unable to render financial loss chart")
