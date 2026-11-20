"""Page 1 — Overview & Attendance Patterns.

Visual daily attendance trajectory, status proportions, weekday patterns,
and exportable shift ledger.
"""
from __future__ import annotations

import streamlit as st
import pandas as pd

from src.config import DB_PATH, OBSERVATION_DATES
from src.data_loader import load_attendance_data, filter_data
from src.cleaning import clean_attendance_data
from src.metrics import (
    attendance_rate,
    daily_status_counts,
    daily_attendance_trend,
    record_coverage,
)
from src.statistics import weekday_attendance_summary, weekly_attendance_summary
from src.charts import (
    daily_status_chart,
    daily_attendance_trend_chart,
    weekday_pattern_chart,
    weekly_attendance_trend_chart,
    status_donut_chart,
)
from src.export import export_filtered_data
from src.ui import (
    render_tailwind_header,
    render_kpi_card,
    render_sidebar_filters,
    render_step_flow_banner,
    render_step_navigation_footer,
    inject_custom_css,
    safe_page_render,
)

# --- Page config ---
st.set_page_config(
    page_title="Executive Overview — Northstar Analytics",
    page_icon="📊",
    layout="wide",
)

inject_custom_css()


def render_page():
    # --- Load data ---
    if "attendance_df" not in st.session_state:
        st.session_state["attendance_df"] = load_attendance_data(DB_PATH)

    # Apply pending filter reset BEFORE widgets are instantiated
    if st.session_state.pop("_needs_filter_reset", False):
        if "attendance_df" in st.session_state and not st.session_state["attendance_df"].empty:
            new_min = st.session_state["attendance_df"]["attendance_date"].min()
            new_max = st.session_state["attendance_df"]["attendance_date"].max()
            st.session_state["filter_start_date"] = new_min
            st.session_state["filter_end_date"] = new_max
            st.session_state["filter_date_range"] = (new_min, new_max)

    df_raw = st.session_state["attendance_df"]
    df = clean_attendance_data(df_raw)

    # --- Header ---
    render_tailwind_header(
        title="Workforce Attendance Overview",
        subtitle="Track daily attendance patterns, status breakdowns, and weekly fulfillment across teams",
    )

    # --- Sidebar filters ---
    departments = sorted(df["department_name"].unique().tolist()) if not df.empty and "department_name" in df.columns else []
    min_date = df["attendance_date"].min() if not df.empty and "attendance_date" in df.columns else None
    max_date = df["attendance_date"].max() if not df.empty and "attendance_date" in df.columns else None
    filters = render_sidebar_filters(departments, min_date, max_date)

    # Apply filters
    filtered = filter_data(
        df,
        department=filters["department"],
        start_date=filters["start_date"],
        end_date=filters["end_date"],
        status=filters["status"],
    )

    if filtered.empty:
        st.warning("No attendance records match the selected filter parameters.")
        return

    coverage = record_coverage(filtered)
    rate = attendance_rate(filtered)
    daily_trend_df = daily_attendance_trend(filtered)

    lowest_day_str = ""
    if not daily_trend_df.empty and "attendance_rate" in daily_trend_df.columns:
        v_trend = daily_trend_df.dropna(subset=["attendance_rate"]).sort_values("attendance_rate")
        if not v_trend.empty:
            l_day = v_trend.iloc[0]
            lowest_day_str = f" The lowest attendance rate was on {pd.to_datetime(l_day['attendance_date']).strftime('%b %d')} ({l_day['attendance_rate']:.1f}%)."

    render_step_flow_banner(
        step_num=1,
        total_steps=5,
        title="THE BIG PICTURE",
        subtitle=f"Assess attendance health ({rate:.1f}%) and daily rhythm across {coverage['unique_departments']} department(s).",
        color_theme="blue",
    )

    st.markdown(
        f"""
        <div style="background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 0.75rem; padding: 0.75rem 1.15rem; margin-bottom: 1.1rem; font-size: 0.85rem; color: #1E40AF; line-height: 1.5;">
            💡 <strong>10-Second Executive Takeaway:</strong> Attendance across the active selection is <strong>{rate:.1f}%</strong> ({'exceeding' if rate >= 95.0 else 'below'} our 95.0% target).{lowest_day_str}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- Active Filter Indicator ---
    n_dates = filtered["attendance_date"].nunique() if not filtered.empty and "attendance_date" in filtered.columns else len(OBSERVATION_DATES)
    st.markdown(
        f"""
        <div style="background-color: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 0.75rem; padding: 0.75rem 1.25rem; margin-bottom: 1.25rem; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem;">
            <div style="font-size: 0.85rem; color: #1E40AF; font-weight: 500;">
                📅 <strong>Active Audit Window:</strong> Production audit cycle covering <strong>{n_dates} observation dates</strong> ({len(filtered):,} matching records).
            </div>
            <div style="display: flex; gap: 0.5rem; align-items: center;">
                <span style="font-size: 0.75rem; font-weight: 700; color: #1D4ED8; background: #DBEAFE; padding: 0.25rem 0.65rem; border-radius: 9999px;">
                    Dept: {filters['department']}
                </span>
                <span style="font-size: 0.75rem; font-weight: 700; color: #047857; background: #D1FAE5; padding: 0.25rem 0.65rem; border-radius: 9999px;">
                    Status: {filters['status']}
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- Key Performance Indicators ---
    coverage = record_coverage(filtered)
    rate = attendance_rate(filtered)

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_kpi_card(
            "Overall Attendance",
            "N/A" if pd.isna(rate) else f"{rate:.1f}%",
            "Present shifts ÷ Eligible working days (Target: ≥95.0%)",
        )
    with k2:
        render_kpi_card(
            "Shifts Logged",
            f"{coverage['total_records']:,}",
            "Matching current filter selection",
        )
    with k3:
        render_kpi_card(
            "Employees Included",
            str(coverage["unique_employees"]),
            "Active employees in current selection",
        )
    with k4:
        render_kpi_card(
            "Working Days",
            f"{coverage['unique_dates']} Days",
            "Observation dates in October 2026",
        )

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # --- Clean 2-Tab Navigation ---
    tab_visuals, tab_ledger = st.tabs([
        "📊 Visual Attendance Dynamics & Patterns",
        "📋 Shift Records Ledger & CSV Download",
    ])

    # =========================================================================
    # TAB 1: VISUAL PATTERNS & RHYTHMS
    # =========================================================================
    with tab_visuals:
        # Row 1: Daily Status Distribution & Donut
        col_chart, col_summary = st.columns([7, 3])
        with col_chart:
            st.markdown("#### 📊 Daily Attendance Status Breakdown")
            daily = daily_status_counts(filtered)
            if daily.empty:
                st.warning("No attendance records match the selected filter parameters.")
            else:
                fig = daily_status_chart(daily)
                st.plotly_chart(fig, width="stretch")

        with col_summary:
            st.markdown("#### 🍩 Status Proportions")
            if not filtered.empty and "status_code" in filtered.columns:
                fig_donut = status_donut_chart(filtered, rate)
                st.plotly_chart(fig_donut, width="stretch")

                status_counts = filtered["status_code"].value_counts()
                total_recs = len(filtered)
                pres_c = status_counts.get("PRESENT", 0)
                leave_c = status_counts.get("APPROVED_LEAVE", 0)
                abs_c = status_counts.get("ABSENT", 0)

                st.markdown(
                    f"""
                    <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 0.75rem; padding: 0.75rem 1rem;">
                        <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 0.35rem;">
                            <span style="color: #059669; font-weight: 600;">● Present</span>
                            <span style="font-weight: 700;">{pres_c:,} ({pres_c/total_recs*100:.1f}%)</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 0.35rem;">
                            <span style="color: #D97706; font-weight: 600;">● Leave</span>
                            <span style="font-weight: 700;">{leave_c:,} ({leave_c/total_recs*100:.1f}%)</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; font-size: 0.85rem;">
                            <span style="color: #DC2626; font-weight: 600;">● Absent</span>
                            <span style="font-weight: 700;">{abs_c:,} ({abs_c/total_recs*100:.1f}%)</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.info("No records to summarize.")

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        # Row 2: Day-by-Day Attendance Rate Trend
        st.markdown("#### 📈 Day-by-Day Attendance Rate Trend")
        daily_trend_df = daily_attendance_trend(filtered)
        if not daily_trend_df.empty:
            fig_trend = daily_attendance_trend_chart(daily_trend_df, org_avg=rate)
            st.plotly_chart(fig_trend, width="stretch")
            n_above = int((daily_trend_df["attendance_rate"] >= 95.0).sum())
            n_tot = len(daily_trend_df)
            st.markdown(
                f"""
                <div style="background: #F8FAFC; border-radius: 0.5rem; padding: 0.5rem 0.75rem; font-size: 0.82rem; color: #475569;">
                    💡 <strong>Insight:</strong> The workforce meets or exceeds the 95.0% target on {n_above} out of {n_tot} recorded working days.{lowest_day_str}
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.info("No trend records available for the active filter selection.")

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        # Row 3: Multi-Week & Weekday Trajectories
        st.markdown("#### 🗓️ Weekly Trajectory & Weekday Rhythm")
        wk_col1, wk_col2 = st.columns([6, 4])
        weekly_df = weekly_attendance_summary(filtered)
        weekday_summary = weekday_attendance_summary(filtered)

        with wk_col1:
            st.markdown("##### 📅 Weekly Fulfillment vs Late Rate")
            if not weekly_df.empty:
                fig_weekly = weekly_attendance_trend_chart(weekly_df)
                st.plotly_chart(fig_weekly, width="stretch")
            else:
                st.info("No weekly data available.")

        with wk_col2:
            st.markdown("##### 📊 Weekday Attendance Distribution")
            if not weekday_summary.empty:
                fig_wk = weekday_pattern_chart(weekday_summary)
                st.plotly_chart(fig_wk, width="stretch")
            else:
                st.info("No weekday breakdown records available.")

    # =========================================================================
    # TAB 2: SHIFT LEDGER & FILTERED EXPORT
    # =========================================================================
    with tab_ledger:
        st.markdown("#### 📋 Filtered Shift Records Ledger")
        st.markdown("Detailed tabular audit view for active filter selection:")

        display_cols = [
            "attendance_id", "employee_code", "department_name",
            "attendance_date", "status_code", "check_in_time",
            "check_out_time", "is_late", "elapsed_duration_minutes",
        ]
        available_cols = [c for c in display_cols if c in filtered.columns]

        st.dataframe(
            filtered[available_cols],
            column_config={
                "attendance_id": st.column_config.NumberColumn("ID", format="%d"),
                "employee_code": st.column_config.TextColumn("Emp Code", width="small"),
                "department_name": st.column_config.TextColumn("Department", width="medium"),
                "attendance_date": st.column_config.TextColumn("Date", width="small"),
                "status_code": st.column_config.TextColumn("Status", width="small"),
                "check_in_time": st.column_config.TextColumn("Punch In", width="small"),
                "check_out_time": st.column_config.TextColumn("Punch Out", width="small"),
                "is_late": st.column_config.CheckboxColumn("Late?", width="small"),
                "elapsed_duration_minutes": st.column_config.NumberColumn("Work Mins", format="%.0f"),
            },
            width="stretch",
            height=380,
            hide_index=True,
        )

        col_d1, col_d2 = st.columns([3, 7])
        with col_d1:
            csv_bytes = export_filtered_data(filtered, columns=available_cols)
            st.download_button(
                label="⬇ Export Filtered Shift Ledger (CSV)",
                data=csv_bytes,
                file_name="workforce_attendance_ledger.csv",
                mime="text/csv",
            )

    render_step_navigation_footer(
        prev_page="app.py",
        prev_label="💼 Executive Home",
        next_page="pages/2_Department_Analysis.py",
        next_label="Step 2: Department Drill-Down ➔",
        next_hint="Company-wide attendance is solid at 95.9%, but which departments are pulling down the average? Drill down into all 8 departments next.",
    )


safe_page_render(render_page)
