"""Modern enterprise UI styling components for Employee Attendance Analytics.

100% native CSS and HTML embedding (zero iframes). Clean reset filters and KPI components.
"""
from __future__ import annotations

from html import escape
import streamlit as st


def inject_custom_css() -> None:
    """Inject polished enterprise design CSS globally."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }

        /* Top header bar refinement */
        header[data-testid="stHeader"] {
            background-color: rgba(248, 250, 252, 0.9);
            backdrop-filter: blur(8px);
        }

        /* Sidebar styling - Professional Dark Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #0F172A !important;
            border-right: 1px solid #1E293B !important;
        }

        /* Sidebar headers and general labels */
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] h4,
        section[data-testid="stSidebar"] p {
            color: #E2E8F0 !important;
        }

        section[data-testid="stSidebar"] hr {
            border-color: #334155 !important;
        }

        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] label p,
        section[data-testid="stSidebar"] label span {
            color: #94A3B8 !important;
            font-weight: 600 !important;
            font-size: 0.82rem !important;
            letter-spacing: 0.03em !important;
            text-transform: uppercase !important;
        }

        /* Form inputs, selectboxes, datepickers in sidebar MUST have dark text */
        section[data-testid="stSidebar"] [data-baseweb="select"] *,
        section[data-testid="stSidebar"] [data-baseweb="input"] *,
        section[data-testid="stSidebar"] [data-testid="stDateInput"] input,
        section[data-testid="stSidebar"] [data-testid="stDateInput"] div,
        section[data-testid="stSidebar"] [data-testid="stDateInput"] span,
        section[data-testid="stSidebar"] .stDateInput input,
        section[data-testid="stSidebar"] input {
            color: #0F172A !important;
            -webkit-text-fill-color: #0F172A !important;
            font-weight: 600 !important;
        }

        /* White input background for all sidebar inputs */
        section[data-testid="stSidebar"] [data-baseweb="input"],
        section[data-testid="stSidebar"] [data-baseweb="select"] > div,
        section[data-testid="stSidebar"] input {
            background-color: #FFFFFF !important;
            border-radius: 0.5rem !important;
        }

        /* Dropdown popover list items */
        div[data-baseweb="popover"],
        div[data-baseweb="popover"] *,
        div[data-baseweb="calendar"],
        div[data-baseweb="calendar"] * {
            color: #0F172A !important;
            -webkit-text-fill-color: #0F172A !important;
        }

        div[data-baseweb="popover"] ul[role="listbox"] li {
            color: #0F172A !important;
            background-color: #FFFFFF !important;
        }

        div[data-baseweb="popover"] ul[role="listbox"] li:hover,
        div[data-baseweb="popover"] ul[role="listbox"] li[aria-selected="true"] {
            background-color: #EFF6FF !important;
            color: #1D4ED8 !important;
        }

        /* Flex alignment for Streamlit columns to equalize card heights */
        div[data-testid="stHorizontalBlock"] {
            align-items: stretch !important;
        }
        div[data-testid="column"] {
            display: flex !important;
            flex-direction: column !important;
        }
        div[data-testid="column"] > div {
            flex: 1 1 auto !important;
            display: flex !important;
            flex-direction: column !important;
        }
        div[data-testid="column"] > div > div {
            flex: 1 1 auto !important;
            display: flex !important;
            flex-direction: column !important;
        }

        /* Native metric cards elevation */
        div[data-testid="stMetric"] {
            background: #FFFFFF !important;
            padding: 1.25rem 1.4rem !important;
            border-radius: 1rem !important;
            border: 1px solid #E2E8F0 !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04), 0 2px 4px -2px rgba(0, 0, 0, 0.04) !important;
            transition: all 0.2s ease !important;
            height: 100% !important;
        }
        div[data-testid="stMetric"]:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08) !important;
            border-color: #CBD5E1 !important;
        }

        /* Button styling - Download & General */
        .stDownloadButton > button {
            background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
            color: white !important;
            border: none !important;
            font-weight: 600 !important;
            border-radius: 0.75rem !important;
            padding: 0.6rem 1.4rem !important;
            box-shadow: 0 4px 10px rgba(37, 99, 235, 0.25) !important;
            transition: all 0.2s ease !important;
        }
        .stDownloadButton > button:hover {
            background: linear-gradient(135deg, #1D4ED8 0%, #1E40AF 100%) !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 14px rgba(37, 99, 235, 0.35) !important;
        }

        /* Sidebar Reset Button - Matches dark sidebar palette */
        section[data-testid="stSidebar"] div.stButton > button,
        section[data-testid="stSidebar"] .st-key-btn_reset_filters > button,
        section[data-testid="stSidebar"] .st-key-btn_reset_filters button[kind="primary"],
        section[data-testid="stSidebar"] .st-key-btn_reset_filters button[data-testid="stBaseButton-primary"] {
            background-color: #1E293B !important;
            color: #94A3B8 !important;
            -webkit-text-fill-color: #94A3B8 !important;
            border: 1px solid #334155 !important;
            border-radius: 0.5rem !important;
            font-size: 0.76rem !important;
            font-weight: 700 !important;
            padding: 0.25rem 0.65rem !important;
            transition: all 0.2s ease !important;
            box-shadow: none !important;
        }
        section[data-testid="stSidebar"] div.stButton > button *,
        section[data-testid="stSidebar"] .st-key-btn_reset_filters > button *,
        section[data-testid="stSidebar"] .st-key-btn_reset_filters > button p,
        section[data-testid="stSidebar"] .st-key-btn_reset_filters > button span {
            color: #94A3B8 !important;
            -webkit-text-fill-color: #94A3B8 !important;
        }
        section[data-testid="stSidebar"] div.stButton > button:hover,
        section[data-testid="stSidebar"] .st-key-btn_reset_filters > button:hover,
        section[data-testid="stSidebar"] .st-key-btn_reset_filters button:hover {
            background-color: #334155 !important;
            border-color: #60A5FA !important;
            color: #E2E8F0 !important;
            -webkit-text-fill-color: #E2E8F0 !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 2px 6px rgba(96, 165, 250, 0.15) !important;
        }
        section[data-testid="stSidebar"] div.stButton > button:focus,
        section[data-testid="stSidebar"] .st-key-btn_reset_filters > button:focus {
            color: #E2E8F0 !important;
            -webkit-text-fill-color: #E2E8F0 !important;
            outline: 1px solid #60A5FA !important;
            outline-offset: 2px !important;
        }

        /* Custom Banner Container (Native, no iframe, no scrollbars) */
        .enterprise-header-banner {
            background: linear-gradient(135deg, #0F172A 0%, #1E1B4B 50%, #1E3A8A 100%);
            border-radius: 1rem;
            padding: 1.5rem 2rem;
            color: #FFFFFF;
            margin-bottom: 1.5rem;
            box-shadow: 0 10px 15px -3px rgba(15, 23, 42, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.1);
            position: relative;
            overflow: hidden;
        }
        .enterprise-header-banner .badge {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #93C5FD;
            margin-bottom: 0.4rem;
        }
        .enterprise-header-banner .pulse-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background-color: #34D399;
            box-shadow: 0 0 8px #34D399;
        }
        .enterprise-header-banner h1 {
            font-size: 1.75rem;
            font-weight: 800;
            letter-spacing: -0.02em;
            color: #FFFFFF !important;
            margin: 0.25rem 0 0.4rem 0 !important;
            line-height: 1.25;
        }
        .enterprise-header-banner p {
            font-size: 0.92rem;
            color: #CBD5E1 !important;
            margin: 0 !important;
            line-height: 1.5;
        }

        /* Native KPI Cards - Strictly Equalized Fixed Height */
        .enterprise-kpi-card {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 1rem;
            padding: 1.15rem 1.25rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04);
            transition: all 0.2s ease;
            height: 150px !important;
            max-height: 150px !important;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-sizing: border-box;
            overflow: hidden;
        }
        .enterprise-kpi-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
            border-color: #93C5FD;
        }
        .enterprise-kpi-card .kpi-label {
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #64748B;
            line-height: 1.25;
            height: 2.5em;
            overflow: hidden;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
        }
        .enterprise-kpi-card .kpi-value {
            font-size: 1.75rem;
            font-weight: 800;
            color: #0F172A;
            line-height: 1.15;
            letter-spacing: -0.02em;
            margin: 0.15rem 0;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        .enterprise-kpi-card .kpi-help {
            font-size: 0.74rem;
            font-weight: 500;
            color: #94A3B8;
            line-height: 1.35;
            height: 2.7em;
            overflow: hidden;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
        }

        /* Native Insight Box */
        .enterprise-insight-box {
            border-radius: 0.85rem;
            padding: 1rem 1.25rem;
            margin: 0.75rem 0;
            border-left: 4px solid;
            display: flex;
            align-items: flex-start;
            gap: 0.85rem;
        }
        .enterprise-insight-box.info {
            background-color: #EFF6FF;
            border-color: #3B82F6;
            color: #1E3A8A;
        }
        .enterprise-insight-box.warning {
            background-color: #FFFBEB;
            border-color: #F59E0B;
            color: #78350F;
        }
        .enterprise-insight-box.success {
            background-color: #ECFDF5;
            border-color: #10B981;
            color: #064E3B;
        }
        .enterprise-insight-box .insight-title {
            font-size: 0.9rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
        }
        .enterprise-insight-box .insight-msg {
            font-size: 0.84rem;
            line-height: 1.5;
            color: #334155;
            margin: 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_tailwind_header(title: str, subtitle: str = "") -> None:
    """Render an executive dashboard header banner cleanly without any iframe."""
    safe_title = escape(str(title))
    safe_subtitle = escape(str(subtitle))
    st.markdown(
        f"""
        <div class="enterprise-header-banner">
            <div class="badge">
                <span class="pulse-dot"></span>
                <span>Enterprise Workforce Intelligence · Operations System</span>
            </div>
            <h1>{safe_title}</h1>
            <p>{safe_subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(label: str, value: str, help_text: str = "") -> None:
    """Render a native executive KPI card (no iframe, no scrollbars, equalized)."""
    safe_label = escape(str(label))
    safe_value = escape(str(value))
    safe_help = escape(str(help_text))
    st.markdown(
        f"""
        <div class="enterprise-kpi-card">
            <div class="kpi-label">{safe_label}</div>
            <div class="kpi-value">{safe_value}</div>
            <div class="kpi-help" title="{safe_help}">{safe_help}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_insight_box(title: str, message: str, tone: str = "info") -> None:
    """Render a native executive insight callout."""
    icons = {"info": "💡", "warning": "⚠️", "success": "✅"}
    icon = icons.get(tone, "💡")
    safe_title = escape(str(title))
    safe_message = escape(str(message))
    st.markdown(
        f"""
        <div class="enterprise-insight-box {tone}">
            <div style="font-size: 1.2rem; line-height: 1;">{icon}</div>
            <div>
                <div class="insight-title">{safe_title}</div>
                <div class="insight-msg">{safe_message}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def initialise_shared_filters() -> None:
    """Initialise shared filter state once; pages can read the same keys."""
    st.session_state.setdefault("filter_department", "All")
    st.session_state.setdefault("filter_start_date", None)
    st.session_state.setdefault("filter_end_date", None)
    st.session_state.setdefault("filter_status", "All")


def render_sidebar_filters(departments: list[str], min_date=None, max_date=None) -> dict:
    """Render professional enterprise sidebar controls with Reset option."""
    initialise_shared_filters()
    with st.sidebar:
        st.markdown(
            """
            <div style="padding: 0.5rem 0 1rem 0;">
                <div style="font-size: 1.15rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.02em;">
                    ⚡ Northstar Analytics
                </div>
                <div style="font-size: 0.75rem; color: #94A3B8; font-weight: 500;">
                    Workforce Intelligence Portal
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("---")

        col_hdr, col_reset = st.columns([6, 4])
        with col_hdr:
            st.markdown(
                "<span style='font-size:0.75rem; font-weight:700; text-transform:uppercase; color:#60A5FA; letter-spacing:0.05em;'>Filters</span>",
                unsafe_allow_html=True,
            )
        with col_reset:
            if st.button("🔄 Reset", key="btn_reset_filters", type="primary", help="Reset all filters to defaults"):
                st.session_state["filter_department"] = "All"
                st.session_state["filter_start_date"] = min_date
                st.session_state["filter_end_date"] = max_date
                st.session_state["filter_status"] = "All"
                st.session_state["filter_date_range"] = (min_date, max_date) if min_date and max_date else None
                st.rerun()

        options = ["All"] + sorted(set(departments))
        if st.session_state["filter_department"] not in options:
            st.session_state["filter_department"] = "All"
        st.selectbox("Select Department", options, key="filter_department")
        
        st.date_input(
            "Reporting Period",
            value=(
                st.session_state["filter_start_date"] or min_date,
                st.session_state["filter_end_date"] or max_date,
            ) if min_date and max_date else None,
            key="filter_date_range",
        )
        st.selectbox("Attendance Status", ["All", "PRESENT", "ABSENT", "APPROVED_LEAVE"], key="filter_status")

    # Safe extraction of date range from Streamlit date_input
    selected_range = st.session_state.get("filter_date_range")
    if isinstance(selected_range, (tuple, list)):
        if len(selected_range) == 2:
            st.session_state["filter_start_date"] = selected_range[0]
            st.session_state["filter_end_date"] = selected_range[1]
        elif len(selected_range) == 1:
            st.session_state["filter_start_date"] = selected_range[0]
            st.session_state["filter_end_date"] = selected_range[0]
    elif selected_range is not None:
        st.session_state["filter_start_date"] = selected_range
        st.session_state["filter_end_date"] = selected_range

    # Guard against inverted date selections
    s_date = st.session_state.get("filter_start_date")
    e_date = st.session_state.get("filter_end_date")
    if s_date and e_date:
        try:
            if s_date > e_date:
                st.session_state["filter_start_date"], st.session_state["filter_end_date"] = e_date, s_date
        except TypeError:
            pass

    return {
        "department": st.session_state.get("filter_department", "All"),
        "start_date": st.session_state.get("filter_start_date"),
        "end_date": st.session_state.get("filter_end_date"),
        "status": st.session_state.get("filter_status", "All"),
    }


def render_home_sidebar() -> None:
    """Render a clean, dedicated portal sidebar header for app.py."""
    with st.sidebar:
        st.markdown(
            """
            <div style="padding: 0.5rem 0 0.75rem 0;">
                <div style="font-size: 1.15rem; font-weight: 800; color: #FFFFFF; letter-spacing: -0.02em;">
                    ⚡ Northstar Analytics
                </div>
                <div style="font-size: 0.75rem; color: #94A3B8; font-weight: 500;">
                    Operations Intelligence Portal
                </div>
                <div style="margin-top: 0.85rem; padding: 0.65rem 0.75rem; background: rgba(30, 41, 59, 0.85); border: 1px solid #334155; border-radius: 0.65rem; font-size: 0.75rem;">
                    <div style="font-weight: 700; color: #F8FAFC;">👨‍💻 Ayush Katiyar</div>
                    <div style="font-size: 0.70rem; color: #94A3B8; margin-bottom: 0.4rem;">Roll No: 2500320140036 · ABES EC</div>
                    <a href="https://github.com/AyushKatiyar972194/Employee_Attendance_Pattern_Analysis" target="_blank" style="color: #60A5FA; text-decoration: none; font-weight: 600; font-size: 0.72rem;">
                        📂 GitHub Repository ↗
                    </a>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_step_flow_banner(
    step_num: int,
    total_steps: int = 5,
    title: str = "",
    subtitle: str = "",
    color_theme: str = "blue",
) -> None:
    """Render a standardized, beautiful step banner across all 5 analytical modules."""
    themes = {
        "blue": {"border": "#2563EB", "bg": "#EFF6FF", "title": "#1E40AF", "text": "#1E3A8A", "badge_bg": "#DBEAFE", "badge_text": "#1D4ED8"},
        "teal": {"border": "#0D9488", "bg": "#F0FDFA", "title": "#0F766E", "text": "#115E59", "badge_bg": "#CCFBF1", "badge_text": "#0F766E"},
        "rose": {"border": "#E11D48", "bg": "#FFF1F2", "title": "#BE123C", "text": "#9F1239", "badge_bg": "#FFE4E6", "badge_text": "#BE123C"},
        "purple": {"border": "#8B5CF6", "bg": "#F5F3FF", "title": "#6D28D9", "text": "#5B21B6", "badge_bg": "#EDE9FE", "badge_text": "#6D28D9"},
        "fuchsia": {"border": "#C026D3", "bg": "#FDF4FF", "title": "#A21CAF", "text": "#86198F", "badge_bg": "#FAE8FF", "badge_text": "#A21CAF"},
    }
    t = themes.get(color_theme, themes["blue"])
    safe_title = escape(str(title))
    safe_sub = escape(str(subtitle))

    st.markdown(
        f"""
        <div style="background: {t['bg']}; border-left: 4px solid {t['border']}; border-radius: 0.5rem; padding: 0.7rem 1rem; margin-bottom: 1.15rem; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem;">
            <div>
                <span style="font-weight: 800; color: {t['title']}; font-size: 0.82rem; letter-spacing: 0.05em;">STEP {step_num} OF {total_steps} · {safe_title}</span>
                <span style="color: {t['border']}; margin: 0 0.5rem; opacity: 0.4;">|</span>
                <span style="color: {t['text']}; font-size: 0.85rem;">{safe_sub}</span>
            </div>
            <span style="font-size: 0.78rem; font-weight: 700; color: {t['badge_text']}; background: {t['badge_bg']}; padding: 0.2rem 0.65rem; border-radius: 9999px;">Step {step_num} of {total_steps}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_step_navigation_footer(
    prev_page: str | None = None,
    prev_label: str | None = None,
    next_page: str | None = None,
    next_label: str | None = None,
    next_hint: str | None = None,
) -> None:
    """Render a standardized forward/backward breadcrumb navigation bar at the bottom of each module."""
    st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)

    if next_hint:
        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%); border: 1px solid #CBD5E1; border-radius: 0.85rem; padding: 1rem 1.25rem; margin-top: 1rem; margin-bottom: 0.85rem; display: flex; align-items: center; justify-content: space-between; gap: 1rem; flex-wrap: wrap;">
                <div>
                    <div style="font-weight: 700; color: #1E293B; font-size: 0.95rem;">👉 Recommended Next Step in Analysis</div>
                    <div style="color: #475569; font-size: 0.86rem; margin-top: 0.25rem; line-height: 1.5;">
                        {escape(str(next_hint))}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    col1, col2, col3 = st.columns([4, 3, 4])
    with col1:
        if prev_page:
            st.page_link(prev_page, label=prev_label or "⬅️ Previous Step")
        else:
            st.page_link("app.py", label="💼 Executive Home")

    with col2:
        st.page_link("app.py", label="💼 Home Portal")

    with col3:
        if next_page:
            st.page_link(next_page, label=next_label or "Next Step ➔")


def safe_page_render(render_fn):
    """Global execution error boundary for Streamlit pages.
    
    Catches any unforeseen runtime exception, prevents full app crash,
    logs the event, and renders an enterprise-grade recovery interface.
    """
    import logging
    try:
        render_fn()
    except Exception as err:
        logging.exception("Caught unexpected exception in safe_page_render: %s", err)
        st.markdown(
            """
            <div style="background-color: #FEF2F2; border: 1px solid #F87171; border-radius: 0.75rem; padding: 1.25rem; margin: 1.5rem 0;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 1.25rem;">⚠️</span>
                    <span style="font-weight: 700; color: #991B1B; font-size: 1rem;">Service Error Handler Activated</span>
                </div>
                <div style="color: #7F1D1D; font-size: 0.88rem; margin-top: 0.5rem; line-height: 1.5;">
                    The analytics engine encountered an unexpected condition while processing this view. The application has isolated the error to protect overall session stability.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        with st.expander("🛠 Diagnostic Details & Fast Recovery", expanded=True):
            st.error(f"**Exception:** `{type(err).__name__}: {str(err)}`")
            st.info("Tip: Try clicking **Reset Application State** below or adjust sidebar filters to valid parameters.")
            col_rec1, col_rec2 = st.columns([3, 7])
            with col_rec1:
                if st.button("🔄 Reset Application State", key=f"btn_error_recover_{id(err)}", type="primary"):
                    for k in list(st.session_state.keys()):
                        del st.session_state[k]
                    st.rerun()
