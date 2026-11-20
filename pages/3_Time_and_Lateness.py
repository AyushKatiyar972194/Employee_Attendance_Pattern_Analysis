"""Page 3 — Time & Lateness Intelligence.

Punctuality benchmarks, grace threshold handling, arrival delay curves,
employee-level chronic lateness rankings, and shift duration analytics.
"""
from __future__ import annotations

import streamlit as st
import pandas as pd
import numpy as np

from src.config import DB_PATH
from src.data_loader import load_attendance_data, filter_data
from src.cleaning import clean_attendance_data
from src.metrics import (
    late_arrival_metrics,
    average_duration_metrics,
    employee_punctuality_rankings,
)
from src.charts import (
    late_by_department_chart,
    elapsed_duration_chart,
    arrival_distribution_chart,
    punctuality_donut_chart,
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
    page_title="Punctuality & Time Analysis — Northstar Analytics",
    page_icon="⏰",
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
        title="Punctuality & Shift Hours",
        subtitle="Identify who arrives on time or late, compare department delays, and inspect working hours",
    )

    # --- Sidebar filters ---
    departments = sorted(df["department_name"].unique().tolist()) if not df.empty and "department_name" in df.columns else []
    min_date = df["attendance_date"].min() if not df.empty and "attendance_date" in df.columns else None
    max_date = df["attendance_date"].max() if not df.empty and "attendance_date" in df.columns else None
    filters = render_sidebar_filters(departments, min_date, max_date)

    filtered = filter_data(
        df,
        department=filters["department"],
        start_date=filters["start_date"],
        end_date=filters["end_date"],
        status=filters["status"],
    )

    if filtered.empty:
        st.warning("No records match the current filter parameters.")
        return

    # --- Late Arrivals & Duration KPI Row ---
    late_metrics = late_arrival_metrics(filtered)
    dur_metrics = average_duration_metrics(filtered)
    emp_ranks = employee_punctuality_rankings(filtered)

    punc_r = 100.0 - late_metrics.get("late_rate", 0.0) if not np.isnan(late_metrics.get("late_rate", 0.0)) else 100.0
    tot_p = late_metrics.get("total_present", 0)
    punc_c = late_metrics.get("punctual_count", 0)
    late_c = late_metrics.get("late_count", 0)
    champs_c = len(emp_ranks[emp_ranks["late_count"] == 0]) if not emp_ranks.empty else 0

    late_by_dept = late_metrics.get("late_by_department", pd.DataFrame())
    top_dept_str = ""
    if not late_by_dept.empty and "late_count" in late_by_dept.columns:
        valid_ld = late_by_dept.dropna(subset=["late_count"]).sort_values("late_count", ascending=False)
        if not valid_ld.empty:
            d1 = valid_ld.iloc[0]
            top_dept_str = f" {d1['department_name']} accounts for the largest share ({d1['late_count']} late shifts)."

    render_step_flow_banner(
        step_num=3,
        total_steps=5,
        title="ROOT CAUSE & PUNCTUALITY",
        subtitle=f"Workforce punctuality is {punc_r:.1f}% ({punc_c:,} on-time shifts, {late_c:,} late shifts).{top_dept_str}",
        color_theme="rose",
    )

    st.markdown(
        f"""
        <div style="background: #FFF1F2; border: 1px solid #FECDD3; border-radius: 0.75rem; padding: 0.75rem 1.15rem; margin-bottom: 1.1rem; font-size: 0.85rem; color: #BE123C; line-height: 1.5;">
            💡 <strong>10-Second Executive Takeaway:</strong> Across {tot_p:,} attended shifts, <strong>{punc_r:.1f}% are on-time</strong> ({punc_c:,} shifts) while {late_c:,} arrived past the grace cutoff.{top_dept_str} {champs_c} staff members achieved a 100% on-time record.
        </div>
        """,
        unsafe_allow_html=True,
    )

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_kpi_card(
            "Late Arrivals",
            str(late_metrics["late_count"]),
            "Arrived after 09:10 AM grace buffer",
        )
    with k2:
        render_kpi_card(
            "Lateness Rate",
            "N/A" if pd.isna(late_metrics["late_rate"]) else f"{late_metrics['late_rate']:.1f}%",
            f"Across {late_metrics['total_present']} attended shifts",
        )
    with k3:
        render_kpi_card(
            "On-Time Check-ins",
            str(late_metrics["punctual_count"]),
            "Arrived at or before 09:10 AM",
        )
    with k4:
        avg_dur_val = dur_metrics["average_duration_minutes"]
        hrs_str = f"{avg_dur_val/60:.1f} hrs" if pd.notna(avg_dur_val) else "N/A"
        render_kpi_card(
            "Avg Shift Length",
            hrs_str,
            f"{avg_dur_val:.0f} min per shift (N={dur_metrics['valid_sample_size']})",
        )

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # --- Clean 2-Tab Navigation ---
    tab_patterns, tab_leaderboard = st.tabs([
        "⏰ Punctuality Breakdown & Arrival Curves",
        "🏆 Employee Punctuality Leaderboard & Shift Search",
    ])

    # =========================================================================
    # TAB 1: PUNCTUALITY BREAKDOWN & ARRIVAL CURVES
    # =========================================================================
    with tab_patterns:
        r1_col1, r1_col2 = st.columns([4, 6])
        with r1_col1:
            st.markdown("#### 🍩 On-Time vs. Late Proportion")
            fig_punc_donut = punctuality_donut_chart(late_metrics)
            st.plotly_chart(fig_punc_donut, width="stretch")
            st.markdown(
                f"""
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 0.65rem; padding: 0.65rem 0.85rem; font-size: 0.82rem; color: #475569;">
                    ● <strong>On-Time:</strong> {late_metrics['punctual_count']:,} shifts ({late_metrics.get('punctuality_rate', 0):.1f}%)<br>
                    ● <strong>Late Arrival:</strong> {late_metrics['late_count']:,} shifts ({late_metrics.get('late_rate', 0):.1f}%)
                </div>
                """,
                unsafe_allow_html=True,
            )

        with r1_col2:
            st.markdown("#### 🔔 Check-In Arrival Delay Distribution")
            fig_arr = arrival_distribution_chart(filtered)
            st.plotly_chart(fig_arr, width="stretch")
            st.markdown(
                """
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 0.65rem; padding: 0.65rem 0.85rem; font-size: 0.82rem; color: #475569;">
                    💡 <strong>Insight:</strong> The distribution peaks around 08:55 AM. Green bars reflect check-ins within the 10-minute grace period (up to 09:10 AM); red bars represent late check-ins.
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        r2_col1, r2_col2 = st.columns(2)
        with r2_col1:
            st.markdown("#### 🏢 Late Arrivals by Department")
            fig_dept_late = late_by_department_chart(filtered)
            st.plotly_chart(fig_dept_late, width="stretch")
            dept_disp_text = ""
            if not late_by_dept.empty and "late_count" in late_by_dept.columns:
                sorted_ld = late_by_dept.dropna(subset=["late_count"]).sort_values("late_count", ascending=False)
                if len(sorted_ld) >= 2:
                    dept_disp_text = f"💡 <strong>Department Disparity:</strong> {sorted_ld.iloc[0]['department_name']} accounts for the largest share of late arrivals ({sorted_ld.iloc[0]['late_count']} shifts), followed by {sorted_ld.iloc[1]['department_name']} ({sorted_ld.iloc[1]['late_count']} shifts)."
                elif len(sorted_ld) == 1:
                    dept_disp_text = f"💡 <strong>Department Disparity:</strong> {sorted_ld.iloc[0]['department_name']} recorded {sorted_ld.iloc[0]['late_count']} late shifts."
            if dept_disp_text:
                st.markdown(
                    f"""
                    <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 0.65rem; padding: 0.65rem 0.85rem; font-size: 0.82rem; color: #475569;">
                        {dept_disp_text}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with r2_col2:
            st.markdown("#### ⏱️ Shift Working Duration Distribution")
            durations = filtered[filtered["status_code"] == "PRESENT"]["elapsed_duration_minutes"].dropna()
            fig_dur = elapsed_duration_chart(durations)
            st.plotly_chart(fig_dur, width="stretch")
            st.markdown(
                """
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 0.65rem; padding: 0.65rem 0.85rem; font-size: 0.82rem; color: #475569;">
                    💡 <strong>Duration Check:</strong> Valid shifts center tightly around 8.5 to 9.2 hours. Shifts with missing check-outs (51 records) are quarantined to maintain duration integrity.
                </div>
                """,
                unsafe_allow_html=True,
            )

    # =========================================================================
    # TAB 2: EMPLOYEE LEADERBOARDS & HISTORY SEARCH
    # =========================================================================
    with tab_leaderboard:
        st.markdown("### 🏆 Employee Punctuality & Chronic Lateness Leaderboard")

        emp_ranks = employee_punctuality_rankings(filtered)

        if not emp_ranks.empty:
            top_late = emp_ranks.iloc[0]
            champions = emp_ranks[emp_ranks["late_count"] == 0]
            chronic_risks = emp_ranks[emp_ranks["late_rate"] >= 30.0]

            hl1, hl2, hl3 = st.columns(3)
            with hl1:
                st.markdown(
                    f"""
                    <div style="background-color: #FEF2F2; border: 1px solid #F87171; border-radius: 0.75rem; padding: 0.9rem 1.1rem;">
                        <div style="font-size: 0.75rem; font-weight: 700; color: #DC2626; text-transform: uppercase;">🚨 Top Chronic Late</div>
                        <div style="font-size: 1.3rem; font-weight: 800; color: #991B1B; margin-top: 2px;">{top_late['employee_code']}</div>
                        <div style="font-size: 0.8rem; color: #B91C1C; margin-top: 2px;">{int(top_late['late_count'])} late shifts ({top_late['late_rate']:.1f}%) · {top_late['department_name']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with hl2:
                st.markdown(
                    f"""
                    <div style="background-color: #ECFDF5; border: 1px solid #6EE7B7; border-radius: 0.75rem; padding: 0.9rem 1.1rem;">
                        <div style="font-size: 0.75rem; font-weight: 700; color: #059669; text-transform: uppercase;">🌟 On-Time Champions</div>
                        <div style="font-size: 1.3rem; font-weight: 800; color: #065F46; margin-top: 2px;">{len(champions)} Staff</div>
                        <div style="font-size: 0.8rem; color: #047857; margin-top: 2px;">100% on-time record across all shifts</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with hl3:
                st.markdown(
                    f"""
                    <div style="background-color: #FFFBEB; border: 1px solid #FCD34D; border-radius: 0.75rem; padding: 0.9rem 1.1rem;">
                        <div style="font-size: 0.75rem; font-weight: 700; color: #D97706; text-transform: uppercase;">⚠️ High Lateness Risk</div>
                        <div style="font-size: 1.3rem; font-weight: 800; color: #92400E; margin-top: 2px;">{len(chronic_risks)} Staff</div>
                        <div style="font-size: 0.8rem; color: #B45309; margin-top: 2px;">≥30% of shifts arrived late</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

            lead_col1, lead_col2 = st.columns(2)
            with lead_col1:
                st.markdown("##### 🚨 Top Chronic Late Arrivals")
                late_cols = [c for c in ["employee_code", "department_name", "total_attended_shifts", "total_shifts", "late_count", "late_rate", "avg_delay_minutes"] if c in emp_ranks.columns]
                st.dataframe(
                    emp_ranks.head(10)[late_cols],
                    column_config={
                        "employee_code": st.column_config.TextColumn("Emp Code", width="small"),
                        "department_name": st.column_config.TextColumn("Department", width="medium"),
                        "total_attended_shifts": st.column_config.NumberColumn("Attended", format="%d"),
                        "total_shifts": st.column_config.NumberColumn("Attended", format="%d"),
                        "late_count": st.column_config.NumberColumn("Late Shifts", format="%d"),
                        "late_rate": st.column_config.NumberColumn("Late %", format="%.1f%%"),
                        "avg_delay_minutes": st.column_config.NumberColumn("Avg Delay", format="%.1f min"),
                    },
                    width="stretch",
                    height=280,
                    hide_index=True,
                )

            with lead_col2:
                st.markdown("##### 🌟 On-Time Champions (100% Punctual)")
                if not champions.empty:
                    champ_cols = [c for c in ["employee_code", "department_name", "total_attended_shifts", "total_shifts", "punctual_count", "avg_delay_minutes"] if c in champions.columns]
                    st.dataframe(
                        champions.head(10)[champ_cols],
                        column_config={
                            "employee_code": st.column_config.TextColumn("Emp Code", width="small"),
                            "department_name": st.column_config.TextColumn("Department", width="medium"),
                            "total_attended_shifts": st.column_config.NumberColumn("Attended", format="%d"),
                            "total_shifts": st.column_config.NumberColumn("Attended", format="%d"),
                            "punctual_count": st.column_config.NumberColumn("On-Time Shifts", format="%d"),
                            "avg_delay_minutes": st.column_config.NumberColumn("Avg Delay", format="%.1f min"),
                        },
                        width="stretch",
                        height=280,
                        hide_index=True,
                    )
                else:
                    st.info("No 100% punctual staff in this filter subset.")

            st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

            # Individual Employee Timeline Search
            st.markdown("#### 🔍 Individual Employee Shift History")
            emp_list = sorted(filtered["employee_code"].unique().tolist()) if "employee_code" in filtered.columns else []
            if emp_list:
                selected_emp = st.selectbox("Select Employee Code:", options=emp_list, key="select_emp_timeline")
                emp_shifts = filtered[filtered["employee_code"] == selected_emp].sort_values("attendance_date")

                timeline_cols = [
                    "attendance_date", "weekday_name", "scheduled_start_time", "check_in_time",
                    "arrival_delay_minutes", "is_late", "check_out_time", "elapsed_duration_minutes", "status_code"
                ]
                st.dataframe(emp_shifts[[c for c in timeline_cols if c in emp_shifts.columns]], width="stretch", height=240, hide_index=True)

            # Export Late Records Button
            late_df = late_metrics.get("late_records", pd.DataFrame())
            if not late_df.empty:
                cols_show = ["attendance_id", "employee_code", "department_name", "attendance_date", "check_in_time", "arrival_delay_minutes", "check_out_time", "elapsed_duration_minutes"]
                csv_bytes = export_filtered_data(late_df, columns=cols_show)
                st.download_button(
                    label="⬇ Export Late Arrival Records (CSV)",
                    data=csv_bytes,
                    file_name="workforce_late_arrival_records.csv",
                    mime="text/csv",
                )
        else:
            st.info("No employee records match the active filter.")

    render_step_navigation_footer(
        prev_page="pages/2_Department_Analysis.py",
        prev_label="⬅️ Step 2: Departments",
        next_page="pages/4_Data_Quality.py",
        next_label="Step 4: Data Quality & Records ➔",
        next_hint="Before implementing shift changes or warning notices, audit data health: 51 shifts had forgotten clock-outs that need regularization.",
    )


safe_page_render(render_page)
