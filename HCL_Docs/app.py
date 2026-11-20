"""Employee Attendance Pattern Analysis — Operations Intelligence Portal.

Engineered for Northstar Technologies Workforce Analytics.
"""
from __future__ import annotations

import streamlit as st

from src.config import DB_PATH, OBSERVATION_DATES
from src.data_loader import load_attendance_data
from src.ui import (
    render_tailwind_header,
    render_kpi_card,
    initialise_shared_filters,
    inject_custom_css,
    safe_page_render,
)

# --- Page config ---
st.set_page_config(
    page_title="Workforce Attendance Analytics — Northstar Technologies",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_custom_css()


def render_main():
    # --- Load data once into session state ---
    if "attendance_df" not in st.session_state:
        st.session_state["attendance_df"] = load_attendance_data(DB_PATH)

    # --- Initialise shared filters ---
    initialise_shared_filters()

    # --- Executive Header ---
    render_tailwind_header(
        title="Workforce Attendance Analytics Dashboard",
        subtitle="Enterprise Operations, Departmental Punctuality & Attendance Intelligence",
    )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # --- Executive Overview Banner ---
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%); border: 1px solid #E2E8F0; padding: 1.5rem; border-radius: 1rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.03); margin-bottom: 1.5rem;">
            <h3 style="margin: 0 0 0.5rem 0; color: #0F172A; font-weight: 700; font-size: 1.25rem;">Executive Summary & Platform Purpose</h3>
            <p style="margin: 0 0 0.75rem 0; color: #475569; font-size: 0.95rem; line-height: 1.6;">
                Welcome to the <strong>Northstar Technologies Attendance Intelligence Platform</strong>. Designed for workforce operations, human resource oversight, and department leadership, this platform delivers verified reporting on employee attendance fulfillment, cross-department punctuality benchmarks, shift duration variance, and rigorous data quality validation.
            </p>
            <p style="margin: 0; color: #64748B; font-size: 0.85rem; line-height: 1.5;">
                <strong>Fictional Organization Profile:</strong> Northstar Technologies is an enterprise technology provider operating across 5 functional departments (Engineering, Human Resources, Finance, Sales, and Customer Support) with an active headcount of 50 staff members.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- Key Metric Highlights ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_kpi_card("Total Headcount", "50", "Active full-time workforce")
    with col2:
        render_kpi_card("Operating Units", "5", "Cross-functional business units")
    with col3:
        render_kpi_card("Verified Logs", "300", "Logged attendance records")
    with col4:
        render_kpi_card("Audit Cycle", f"{len(OBSERVATION_DATES)} Dates", "Observation audit window")

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    # --- Navigation Hub Grid ---
    st.markdown("### 🧭 Platform Modules")

    n1, n2 = st.columns(2)
    with n1:
        st.markdown(
            """
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 0.85rem; padding: 1.25rem; margin-bottom: 1rem; border-left: 4px solid #2563EB; min-height: 120px; display: flex; flex-direction: column; justify-content: space-between;">
                <div style="font-weight: 700; font-size: 1.05rem; color: #0F172A;">📊 1. Overview & Daily Trends</div>
                <div style="color: #64748B; font-size: 0.88rem; margin-top: 0.35rem; line-height: 1.5;">
                    Reconciled organization-wide attendance fulfillment rate (95.8%), daily status breakdown (Present, Approved Leave, Absent), and day-by-day fulfillment trend lines.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 0.85rem; padding: 1.25rem; margin-bottom: 1rem; border-left: 4px solid #0D9488; min-height: 120px; display: flex; flex-direction: column; justify-content: space-between;">
                <div style="font-weight: 700; font-size: 1.05rem; color: #0F172A;">🏢 2. Department Analysis</div>
                <div style="color: #64748B; font-size: 0.88rem; margin-top: 0.35rem; line-height: 1.5;">
                    Weighted comparative evaluation across Engineering, HR, Finance, Sales, and Support alongside weekday patterns and employee record drill-downs.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with n2:
        st.markdown(
            """
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 0.85rem; padding: 1.25rem; margin-bottom: 1rem; border-left: 4px solid #E11D48; min-height: 120px; display: flex; flex-direction: column; justify-content: space-between;">
                <div style="font-weight: 700; font-size: 1.05rem; color: #0F172A;">⏰ 3. Time & Lateness Insights</div>
                <div style="color: #64748B; font-size: 0.88rem; margin-top: 0.35rem; line-height: 1.5;">
                    Shift punctuality analysis applying strict grace period thresholds, arrival delay distributions, and average recorded elapsed shift durations.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 0.85rem; padding: 1.25rem; margin-bottom: 1rem; border-left: 4px solid #8B5CF6; min-height: 120px; display: flex; flex-direction: column; justify-content: space-between;">
                <div style="font-weight: 700; font-size: 1.05rem; color: #0F172A;">🔍 4. Data Quality & Audit</div>
                <div style="color: #64748B; font-size: 0.88rem; margin-top: 0.35rem; line-height: 1.5;">
                    Data quality scorecard across 5 dimensions, pipeline run monitoring, flagged record inspection, and statistical IQR anomaly detection.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.caption(
        "Northstar Technologies Workforce Intelligence Suite · Production Analytics"
    )


safe_page_render(render_main)
