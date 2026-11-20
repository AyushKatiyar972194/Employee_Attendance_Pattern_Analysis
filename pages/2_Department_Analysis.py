"""Page 2 — Department Benchmarks.

Weighted departmental metrics, organization benchmarks, weekday heatmaps,
2x2 performance matrix, and interactive employee directory drill-down.
"""
from __future__ import annotations

import streamlit as st
import pandas as pd

from src.config import DB_PATH
from src.data_loader import load_attendance_data, filter_data
from src.cleaning import clean_attendance_data
from src.metrics import (
    department_attendance_rates,
    attendance_rate,
    late_arrival_metrics,
)
from src.charts import (
    department_rates_chart,
    department_quadrant_chart,
    department_weekday_heatmap,
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
    page_title="Department Benchmarks — Northstar Analytics",
    page_icon="🏢",
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
        title="Department Attendance Comparison",
        subtitle="Compare attendance rates across all departments, see weekday trends, and explore team rosters",
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

    # --- KPI Cards & Dynamic Banner ---
    dept_rates = department_attendance_rates(filtered)
    org_rate = attendance_rate(filtered)

    valid_rates = (
        dept_rates.dropna(subset=["attendance_rate"])
        if not dept_rates.empty and "attendance_rate" in dept_rates.columns
        else pd.DataFrame()
    )

    if not valid_rates.empty:
        best = valid_rates.loc[valid_rates["attendance_rate"].idxmax()]
        worst = valid_rates.loc[valid_rates["attendance_rate"].idxmin()]
        step_sub = f"{best['department_name']} leads at {best['attendance_rate']:.1f}%, while {worst['department_name']} records {worst['attendance_rate']:.1f}%."
        takeaway_sub = f"<strong>{best['department_name']}</strong> sets the benchmark at <strong>{best['attendance_rate']:.1f}%</strong> fulfillment, while <strong>{worst['department_name']}</strong> records <strong>{worst['attendance_rate']:.1f}%</strong>."
    else:
        step_sub = "Compare attendance rates across all monitored operational departments."
        takeaway_sub = "Compare departmental fulfillment across active workforce filters."

    render_step_flow_banner(
        step_num=2,
        total_steps=5,
        title="DEPARTMENT DRILL-DOWN",
        subtitle=step_sub,
        color_theme="teal",
    )

    st.markdown(
        f"""
        <div style="background: #F0FDFA; border: 1px solid #99F6E4; border-radius: 0.75rem; padding: 0.75rem 1.15rem; margin-bottom: 1.1rem; font-size: 0.85rem; color: #0F766E; line-height: 1.5;">
            💡 <strong>10-Second Executive Takeaway:</strong> {takeaway_sub}
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    if not valid_rates.empty:
        best = valid_rates.loc[valid_rates["attendance_rate"].idxmax()]
        worst = valid_rates.loc[valid_rates["attendance_rate"].idxmin()]
        with c1:
            render_kpi_card(
                f"Highest · {best['department_name']}",
                f"{best['attendance_rate']:.1f}%",
                f"Present: {int(best['present_count'])} of {int(best['eligible_count'])} eligible days",
            )
        with c2:
            render_kpi_card(
                f"Lowest · {worst['department_name']}",
                f"{worst['attendance_rate']:.1f}%",
                f"Present: {int(worst['present_count'])} of {int(worst['eligible_count'])} eligible days",
            )
    else:
        with c1:
            render_kpi_card("Highest Attendance", "N/A", "No records found")
        with c2:
            render_kpi_card("Lowest Attendance", "N/A", "No records found")

    with c3:
        render_kpi_card(
            "Company Average",
            "N/A" if pd.isna(org_rate) else f"{org_rate:.1f}%",
            "Across all eligible working days",
        )

    st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

    # --- Clean 2-Tab Navigation ---
    tab_benchmarks, tab_roster = st.tabs([
        "📊 Department Benchmarks & Performance Matrix",
        "👥 Department Roster & Employee Drill-Down",
    ])

    # =========================================================================
    # TAB 1: BENCHMARKS & MATRIX
    # =========================================================================
    with tab_benchmarks:
        r1_col1, r1_col2 = st.columns(2)
        with r1_col1:
            st.markdown("#### 🏢 Attendance Rate by Department")
            if not valid_rates.empty:
                fig_dept = department_rates_chart(dept_rates, org_rate=org_rate)
                st.plotly_chart(fig_dept, width="stretch")
            else:
                st.info("No comparative department records found.")

        with r1_col2:
            st.markdown("#### 🎯 2x2 Performance Matrix (Attendance vs. Punctuality)")
            fig_quad = department_quadrant_chart(filtered)
            st.plotly_chart(fig_quad, width="stretch")

        late_metrics_f = late_arrival_metrics(filtered)
        late_by_dept_f = late_metrics_f.get("late_by_department", pd.DataFrame())
        matrix_note = ""
        if not late_by_dept_f.empty and "late_rate" in late_by_dept_f.columns:
            w_late = late_by_dept_f.dropna(subset=["late_rate"]).sort_values("late_rate", ascending=False).iloc[0]
            w_dept = w_late["department_name"]
            w_late_r = float(w_late["late_rate"])
            w_punc_r = round(100.0 - w_late_r, 1)
            matrix_note = f"Notice that <strong>{w_dept}</strong> has the lowest punctuality with <strong>{w_punc_r:.1f}% on-time</strong> ({w_late_r:.1f}% late arrivals)."

        if matrix_note:
            st.markdown(
                f"""
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 0.65rem; padding: 0.65rem 1rem; margin-top: 0.5rem; margin-bottom: 1rem; font-size: 0.84rem; color: #334155;">
                    💡 <strong>Matrix Takeaway:</strong> {matrix_note}
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("#### 📅 Department Weekday Attendance Heatmap")
        fig_heat = department_weekday_heatmap(filtered)
        st.plotly_chart(fig_heat, width="stretch")

        st.markdown("#### 📋 Department Performance Summary Table")
        if not dept_rates.empty:
            dept_summary_df = dept_rates.copy()
            dept_summary_df["attendance_rate"] = dept_summary_df["attendance_rate"].map(lambda x: f"{x:.1f}%" if pd.notnull(x) else "N/A")
            if "punctuality_rate" in dept_summary_df.columns:
                dept_summary_df["punctuality_rate"] = dept_summary_df["punctuality_rate"].map(lambda x: f"{x:.1f}%" if pd.notnull(x) else "N/A")

            st.dataframe(
                dept_summary_df,
                column_config={
                    "department_name": st.column_config.TextColumn("Department", width="medium"),
                    "present_count": st.column_config.NumberColumn("Present Shifts", format="%d"),
                    "eligible_count": st.column_config.NumberColumn("Eligible Days", format="%d"),
                    "attendance_rate": st.column_config.TextColumn("Attendance Rate", width="small"),
                },
                width="stretch",
                hide_index=True,
            )

            csv_matrix = export_filtered_data(dept_summary_df)
            st.download_button(
                label="⬇ Export Department Performance Matrix (CSV)",
                data=csv_matrix,
                file_name="department_performance_matrix.csv",
                mime="text/csv",
            )

    # =========================================================================
    # TAB 2: DEPARTMENT ROSTER & DRILL-DOWN
    # =========================================================================
    with tab_roster:
        st.markdown("### 👥 Department Employee Directory & Shift Drill-Down")
        dept_options = ["All"] + sorted(filtered["department_name"].unique().tolist()) if "department_name" in filtered.columns else ["All"]
        selected_dept = st.selectbox("Select Department to Inspect:", options=dept_options, key="drilldown_dept_tab")

        drill_df = filtered if selected_dept == "All" or "department_name" not in filtered.columns else filtered[filtered["department_name"] == selected_dept]
        emp_in_dept = drill_df["employee_code"].nunique() if "employee_code" in drill_df.columns else 0

        d1, d2, d3 = st.columns(3)
        with d1:
            st.metric("Headcount Monitored", f"{emp_in_dept} Employees")
        with d2:
            st.metric("Total Shift Logs", f"{len(drill_df)} Records")
        with d3:
            dept_p_rate = attendance_rate(drill_df)
            st.metric("Attendance Rate", f"{dept_p_rate:.1f}%")

        display_cols = [
            "attendance_id", "employee_code", "department_name", "attendance_date",
            "weekday_name", "status_code", "check_in_time", "check_out_time", "arrival_delay_minutes", "is_late"
        ]
        st.dataframe(drill_df[[c for c in display_cols if c in drill_df.columns]], width="stretch", height=340)

    render_step_navigation_footer(
        prev_page="pages/1_Overview.py",
        prev_label="⬅️ Step 1: Overview",
        next_page="pages/3_Time_and_Lateness.py",
        next_label="Step 3: Punctuality & Lateness ➔",
        next_hint="Customer Support shows 96.2% overall attendance, but why is their fulfillment flagged as low? Let's check arrival check-in times to see if lateness is the real issue.",
    )


safe_page_render(render_page)
