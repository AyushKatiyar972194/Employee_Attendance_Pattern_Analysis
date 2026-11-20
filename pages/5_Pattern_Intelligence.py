"""Page 5 — Smart Patterns, Policy Playground & Cost Calculator.

Understand employee attendance habits, test new office timing rules,
and see the financial cost and potential money saved.
"""
from __future__ import annotations

import streamlit as st
import pandas as pd

from src.config import DB_PATH
from src.data_loader import load_attendance_data, filter_data
from src.cleaning import clean_attendance_data
from src.predictive import compute_attendance_risk_scores
from src.simulation import (
    simulate_grace_period_policy,
    calculate_financial_loss,
    generate_executive_audit_markdown,
)
from src.charts import (
    risk_tier_donut_chart,
    risk_scatter_chart,
    grace_period_sensitivity_chart,
    financial_loss_breakdown_chart,
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
    page_title="Smart Patterns & Policy — Northstar Analytics",
    page_icon="🔮",
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
    if df_raw is None or df_raw.empty:
        st.warning("No attendance data could be loaded. Please ensure dataset is available.")
        return

    df = clean_attendance_data(df_raw)

    departments = sorted(df["department_name"].dropna().unique().tolist()) if "department_name" in df.columns else []
    min_date = df["attendance_date"].min() if "attendance_date" in df.columns else None
    max_date = df["attendance_date"].max() if "attendance_date" in df.columns else None
    filters = render_sidebar_filters(departments, min_date, max_date)

    filtered = filter_data(
        df,
        department=filters["department"],
        start_date=filters["start_date"],
        end_date=filters["end_date"],
        status=filters["status"],
    )

    # --- Header ---
    render_tailwind_header(
        title="Smart Patterns, Policy Playground & ROI",
        subtitle="Understand employee attendance habits, test new office timing rules, and see the financial impact",
    )

    active_df = filtered if not filtered.empty else df
    risk_df = compute_attendance_risk_scores(active_df)
    tier_counts = risk_df["risk_tier"].value_counts() if not risk_df.empty else pd.Series()
    low_count = tier_counts.get("Low Risk (Healthy)", 0)
    low_pct = (low_count / len(risk_df) * 100.0) if not risk_df.empty else 0.0

    sim_data = simulate_grace_period_policy(active_df, target_grace_minutes=15)
    loss_data = calculate_financial_loss(active_df)
    punc_sim = sim_data.get("simulated_punctuality_pct", 0.0)
    reclass_c = sim_data.get("reclassified_on_time", 0)
    recov_val = loss_data.get("projected_10pct_recovery", 0.0)

    render_step_flow_banner(
        step_num=5,
        total_steps=5,
        title="SMART PATTERNS & POLICY SIMULATOR",
        subtitle=f"{low_pct:.1f}% of staff are in the healthy low-risk tier; test policy grace adjustments and savings.",
        color_theme="fuchsia",
    )

    st.markdown(
        f"""
        <div style="background: #FDF4FF; border: 1px solid #F5D0FE; border-radius: 0.75rem; padding: 0.75rem 1.15rem; margin-bottom: 1.1rem; font-size: 0.85rem; color: #86198F; line-height: 1.5;">
            💡 <strong>10-Second Executive Takeaway:</strong> Our predictive risk model identifies that <strong>{low_pct:.1f}% of monitored staff are stable and low-risk</strong>. Modeling a 15-minute grace period reclassifies {reclass_c:,} transit delays, improving on-time arrivals to {punc_sim:.1f}%, while targeted scheduling interventions can recover an estimated <strong>₹{recov_val:,.0f} annually</strong> in lost productive hours.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- 3-Tab Structure (Easy, Plain English) ---
    tab_habits, tab_simulator, tab_roi = st.tabs([
        "🔮 1. Employee Attendance Habits & Early Warnings",
        "⚙️ 2. 'What-If?' Policy Playground (Test New Rules)",
        "💰 3. Money Lost & Savings Calculator",
    ])

    # =========================================================================
    # TAB 1: ATTENDANCE HABITS & EARLY WARNINGS
    # =========================================================================
    with tab_habits:
        st.markdown("#### 👥 Who Might Need Extra Support With Attendance?")
        st.markdown(
            "<span style='color: #475569; font-size: 0.88rem;'>"
            "Instead of just counting late arrivals, this tool looks at the full picture to understand <strong>who is struggling and why</strong>:<br/>"
            "• <strong>🟢 Reliable (Low Risk):</strong> Always on-time, predictable schedule.<br/>"
            "• <strong>🟡 Watchlist (Moderate Risk):</strong> Occasionally late, or tends to take leave right before/after weekends.<br/>"
            "• <strong>🔴 Needs Action (High Risk):</strong> Frequent late arrivals, unpredictable timings, or repeated missing clock-outs."
            "</span>",
            unsafe_allow_html=True,
        )

        risk_df = compute_attendance_risk_scores(filtered if not filtered.empty else df)

        if not risk_df.empty:
            tier_counts = risk_df["risk_tier"].value_counts()
            high_count = tier_counts.get("High Risk (Action Needed)", 0)
            mod_count = tier_counts.get("Moderate Risk (Watchlist)", 0)
            low_count = tier_counts.get("Low Risk (Healthy)", 0)
            avg_risk = float(risk_df["risk_score"].mean())

            k1, k2, k3, k4 = st.columns(4)
            with k1:
                render_kpi_card(
                    "Needs Support (High)",
                    f"{high_count} Employees",
                    f"{high_count / len(risk_df) * 100:.1f}% of staff · Recommended for 1-on-1 check-in",
                )
            with k2:
                render_kpi_card(
                    "Watchlist (Moderate)",
                    f"{mod_count} Employees",
                    f"{mod_count / len(risk_df) * 100:.1f}% · Generally fine, occasional slips",
                )
            with k3:
                render_kpi_card(
                    "Reliable & On-Time",
                    f"{low_count} Employees",
                    f"{low_count / len(risk_df) * 100:.1f}% · High consistency & dependable",
                )
            with k4:
                render_kpi_card(
                    "Company Habit Score",
                    f"{avg_risk:.1f} / 100",
                    "Lower is healthier (Company target: <30.0)",
                )

            st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

            col_dnut, col_scat = st.columns([4, 6])
            with col_dnut:
                st.markdown("##### 🍩 Employee Proportion by Category")
                fig_d = risk_tier_donut_chart(risk_df)
                st.plotly_chart(fig_d, width="stretch")

            with col_scat:
                st.markdown("##### 📊 Arrival Timing Unpredictability vs Lateness")
                st.caption("Points in the top-right corner are employees with both high lateness and unpredictable arrival times:")
                fig_s = risk_scatter_chart(risk_df)
                st.plotly_chart(fig_s, width="stretch")

            st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

            # Interactive Watchlist Table
            st.markdown("#### 📋 Detailed Employee Attendance Watchlist")
            st.info(
                "💡 **How to use this:** Filter by category below to see exactly *why* an employee was flagged. "
                "This helps managers offer practical solutions (like flexible shift timing) instead of issuing unfair penalties."
            )

            filter_tier = st.selectbox(
                "Filter List by Employee Category:",
                options=["All Categories", "High Risk (Action Needed)", "Moderate Risk (Watchlist)", "Low Risk (Healthy)"],
                key="filter_risk_tier",
            )

            display_risk = risk_df.copy()
            if filter_tier != "All Categories":
                display_risk = display_risk[display_risk["risk_tier"] == filter_tier]

            show_cols = [
                "employee_code",
                "department_name",
                "risk_score",
                "risk_tier",
                "late_count",
                "late_rate",
                "delay_volatility",
                "weekend_leave_pct",
                "missing_checkouts",
                "primary_drivers",
            ]
            renamed_cols = {
                "employee_code": "Employee",
                "department_name": "Department",
                "risk_score": "Risk (0-100)",
                "risk_tier": "Category",
                "late_count": "Late Shifts",
                "late_rate": "Late %",
                "delay_volatility": "Time Variation (±mins)",
                "weekend_leave_pct": "Mon/Fri Leaves %",
                "missing_checkouts": "Missing Clock-Outs",
                "primary_drivers": "Plain-English Reasons Why Flagged",
            }

            st.dataframe(
                display_risk[show_cols].rename(columns=renamed_cols),
                width="stretch",
                height=280,
                hide_index=True,
            )

            col_exp, _ = st.columns([4, 6])
            with col_exp:
                csv_risk = export_filtered_data(display_risk[show_cols])
                st.download_button(
                    label="⬇ Download Employee Watchlist (CSV)",
                    data=csv_risk,
                    file_name="employee_attendance_watchlist.csv",
                    mime="text/csv",
                    key="btn_dl_risk_ledger",
                )
        else:
            st.info("No records available to analyze habits.")

    # =========================================================================
    # TAB 2: POLICY PLAYGROUND
    # =========================================================================
    with tab_simulator:
        st.markdown("#### 🕹️ Test Changing the Office Grace Period")
        st.markdown(
            "<span style='color: #475569; font-size: 0.88rem;'>"
            "Right now, employees are marked late if they arrive after <strong>09:10 AM</strong> (a 10-minute grace window). "
            "Use the slider below to test what happens if you allow <strong>15 minutes, 20 minutes</strong>, or zero grace time:"
            "</span>",
            unsafe_allow_html=True,
        )

        sim_grace = st.slider(
            "Allowed Grace Window (Minutes past 09:00 AM start):",
            min_value=0,
            max_value=30,
            value=15,
            step=1,
            key="slider_sim_grace",
            help="10 minutes is current policy. Try sliding to 15 minutes to see traffic impact.",
        )

        sim_res = simulate_grace_period_policy(filtered if not filtered.empty else df, target_grace_minutes=sim_grace)

        p1, p2, p3, p4 = st.columns(4)
        with p1:
            render_kpi_card(
                "New On-Time Rate",
                f"{sim_res['simulated_punctuality_pct']:.1f}%",
                f"Previous baseline: {sim_res['baseline_punctuality_pct']:.1f}%",
            )
        with p2:
            delta_str = f"+{sim_res['punctuality_delta_pct']:.1f}%" if sim_res["punctuality_delta_pct"] >= 0 else f"{sim_res['punctuality_delta_pct']:.1f}%"
            render_kpi_card(
                "Punctuality Boost",
                delta_str,
                "Net change in overall company punctuality",
            )
        with p3:
            render_kpi_card(
                "Minor Delays Forgiven",
                f"{sim_res['reclassified_on_time']:,} Shifts",
                f"Infractions saved by allowing {sim_grace} mins",
            )
        with p4:
            render_kpi_card(
                "Remaining Chronic Late",
                f"{sim_res['simulated_late_count']:,} Shifts",
                "True delays still arriving after the grace window",
            )

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        col_curve, col_dept_sim = st.columns([6, 4])
        with col_curve:
            st.markdown(f"##### 📈 What Happens as You Give More Grace Time (0 to 30 mins)")
            fig_curve = grace_period_sensitivity_chart(filtered if not filtered.empty else df)
            st.plotly_chart(fig_curve, width="stretch")

        with col_dept_sim:
            st.markdown(f"##### 🏢 Department-by-Department Improvement")
            st.caption(f"Comparing current 10m rule vs. your simulated {sim_grace}m rule:")
            st.dataframe(sim_res["department_comparison"], width="stretch", height=280, hide_index=True)

        sim_15_tab = simulate_grace_period_policy(filtered if not filtered.empty else df, target_grace_minutes=15)
        sweet_base_punc = sim_15_tab.get("baseline_punctuality_pct", 0.0)
        sweet_sim_punc = sim_15_tab.get("simulated_punctuality_pct", 0.0)
        sweet_forgiven = sim_15_tab.get("reclassified_on_time", 0)

        st.markdown(
            f"""
            <div style="background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 0.75rem; padding: 0.95rem 1.25rem; margin-top: 0.75rem;">
                <div style="font-weight: 700; color: #1E40AF; font-size: 0.95rem;">💡 Key Takeaway: The "15-Minute Sweet Spot"</div>
                <div style="color: #1E3A8A; font-size: 0.86rem; margin-top: 0.3rem; line-height: 1.5;">
                    Giving just <strong>5 extra minutes</strong> (moving cutoff from 09:10 to 09:15 AM) forgives <strong>{sweet_forgiven:,} minor traffic delays</strong>, 
                    jumping company punctuality from <strong>{sweet_base_punc:.1f}% to {sweet_sim_punc:.1f}%</strong>! 
                    This stops managers from penalizing employees who were stuck in momentary traffic, while still catching the few who are truly 20-30 minutes late.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # =========================================================================
    # TAB 3: MONEY LOST & SAVINGS CALCULATOR
    # =========================================================================
    with tab_roi:
        st.markdown("#### 💵 How Much Does Lateness & Absence Cost the Company?")
        st.markdown(
            "<span style='color: #475569; font-size: 0.88rem;'>"
            "When employees arrive late or miss work without notice, the company loses productive hours and often pays extra overtime. "
            "Use the sliders below to estimate the real monetary cost in Indian Rupees (₹):"
            "</span>",
            unsafe_allow_html=True,
        )

        col_w1, col_w2 = st.columns(2)
        with col_w1:
            wage_slider = st.slider(
                "Estimated Average Hourly Wage (₹ / hour):",
                min_value=300,
                max_value=2000,
                value=650,
                step=50,
                key="slider_hourly_wage",
                help="₹650/hr represents approx. ₹11.5 Lakhs annual salary baseline.",
            )
        with col_w2:
            multiplier_slider = st.slider(
                "Extra Cost to Cover an Unplanned Absence (Overtime Multiplier):",
                min_value=1.0,
                max_value=2.5,
                value=1.5,
                step=0.1,
                key="slider_contractor_mult",
                help="1.5x means covering a missed shift costs 1.5 times normal pay (overtime/peer coverage).",
            )

        fin_data = calculate_financial_loss(
            filtered if not filtered.empty else df,
            hourly_wage=wage_slider,
            contractor_multiplier=multiplier_slider,
        )

        f1, f2, f3, f4 = st.columns(4)
        with f1:
            render_kpi_card(
                "Lost to Late Arrivals",
                f"₹{fin_data['late_cost']:,.0f}",
                f"From {fin_data['late_hours_lost']:.1f} cumulative delay hours",
            )
        with f2:
            render_kpi_card(
                "Lost to Absenteeism",
                f"₹{fin_data['absence_cost']:,.0f}",
                f"From {fin_data['absent_shifts_count']} missed shifts ({fin_data['absence_hours_lost']:.0f} hrs)",
            )
        with f3:
            render_kpi_card(
                "Total Money Leakage",
                f"₹{fin_data['total_financial_loss']:,.0f}",
                "Direct estimated productivity leakage",
            )
        with f4:
            render_kpi_card(
                "Money Saved (10% Gain)",
                f"₹{fin_data['projected_10pct_recovery']:,.0f}",
                "Estimated annual savings from better timing policies",
            )

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

        col_fin_c, col_fin_m = st.columns([5, 5])
        with col_fin_c:
            st.markdown("##### 📊 Where is the Money Going?")
            fig_fin = financial_loss_breakdown_chart(fin_data)
            st.plotly_chart(fig_fin, width="stretch")

        with col_fin_m:
            st.markdown("##### 📄 Executive Summary Briefing (Ready for Management)")
            memo_text = generate_executive_audit_markdown(filtered if not filtered.empty else df)
            st.text_area(
                "Summary Text (Copy or Download):",
                value=memo_text,
                height=260,
                key="txt_exec_memo",
            )
            st.download_button(
                label="⬇ Download Executive Summary (.md)",
                data=memo_text,
                file_name="Executive_Attendance_Summary.md",
                mime="text/markdown",
                key="btn_dl_memo",
            )

    render_step_navigation_footer(
        prev_page="pages/4_Data_Quality.py",
        prev_label="⬅️ Step 4: Data Quality & Records",
        next_page=None,
        next_label=None,
        next_hint=None,
    )


safe_page_render(render_page)
