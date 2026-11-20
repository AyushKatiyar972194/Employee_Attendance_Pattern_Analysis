"""Reusable Tailwind-styled UI helpers for the Employee Attendance app.

The iframe content is developer-authored constant HTML. Dynamic text is HTML-escaped
before insertion. Tailwind's CDN requires an internet connection in the browser.
"""
from __future__ import annotations

from html import escape
import streamlit as st


def render_tailwind_header(title: str, subtitle: str = "") -> None:
    """Render a branded header using a small, isolated Tailwind CDN iframe."""
    safe_title = escape(str(title))
    safe_subtitle = escape(str(subtitle))
    html = f"""
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <script src="https://cdn.tailwindcss.com"></script>
      </head>
      <body class="m-0 bg-slate-50 font-sans">
        <header class="rounded-2xl bg-gradient-to-r from-slate-900 via-blue-900 to-cyan-800 px-5 py-5 text-white shadow">
          <div class="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-200">
            Northstar Technologies · Synthetic Workforce Analytics
          </div>
          <h1 class="mt-2 text-2xl font-bold tracking-tight">{safe_title}</h1>
          <p class="mt-1 text-sm text-slate-200">{safe_subtitle}</p>
        </header>
      </body>
    </html>
    """
    st.iframe(srcdoc=html, height=142, scrolling=False)


def render_kpi_card(label: str, value: str, help_text: str = "") -> None:
    """Render one compact KPI card in an isolated Tailwind iframe."""
    safe_label = escape(str(label))
    safe_value = escape(str(value))
    safe_help = escape(str(help_text))
    html = f"""
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <script src="https://cdn.tailwindcss.com"></script>
      </head>
      <body class="m-0 bg-transparent font-sans">
        <section class="rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-sm">
          <p class="text-xs font-semibold uppercase tracking-wide text-slate-500">{safe_label}</p>
          <p class="mt-2 text-2xl font-bold tracking-tight text-slate-900">{safe_value}</p>
          <p class="mt-1 text-xs text-slate-500">{safe_help}</p>
        </section>
      </body>
    </html>
    """
    st.iframe(srcdoc=html, height=116, scrolling=False)


def render_insight_box(title: str, message: str, tone: str = "info") -> None:
    """Render a simple insight panel. tone is restricted to known styles."""
    styles = {
        "info": ("border-blue-200 bg-blue-50", "text-blue-900"),
        "warning": ("border-amber-200 bg-amber-50", "text-amber-900"),
        "success": ("border-emerald-200 bg-emerald-50", "text-emerald-900"),
    }
    panel, text_color = styles.get(tone, styles["info"])
    safe_title = escape(str(title))
    safe_message = escape(str(message))
    html = f"""
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <script src="https://cdn.tailwindcss.com"></script>
      </head>
      <body class="m-0 bg-transparent font-sans">
        <section class="rounded-xl border {panel} p-4">
          <h3 class="text-sm font-bold {text_color}">{safe_title}</h3>
          <p class="mt-1 text-sm {text_color}">{safe_message}</p>
        </section>
      </body>
    </html>
    """
    st.iframe(srcdoc=html, height=116, scrolling=False)


def initialise_shared_filters() -> None:
    """Initialise shared filter state once; pages can read the same keys."""
    st.session_state.setdefault("filter_department", "All")
    st.session_state.setdefault("filter_start_date", None)
    st.session_state.setdefault("filter_end_date", None)
    st.session_state.setdefault("filter_status", "All")


def render_sidebar_filters(departments: list[str], min_date=None, max_date=None) -> dict:
    """Render shared filters and return the selected values.

    Call this function on each data page after initialise_shared_filters().
    """
    initialise_shared_filters()
    with st.sidebar:
        st.subheader("Shared filters")
        options = ["All"] + sorted(set(departments))
        if st.session_state["filter_department"] not in options:
            st.session_state["filter_department"] = "All"
        st.selectbox("Department", options, key="filter_department")
        st.date_input(
            "Date range",
            value=(
                st.session_state["filter_start_date"] or min_date,
                st.session_state["filter_end_date"] or max_date,
            ) if min_date and max_date else None,
            key="filter_date_range",
        )
        st.selectbox("Attendance status", ["All", "PRESENT", "ABSENT", "APPROVED_LEAVE"], key="filter_status")
    selected_range = st.session_state.get("filter_date_range")
    if isinstance(selected_range, (tuple, list)) and len(selected_range) == 2:
        st.session_state["filter_start_date"], st.session_state["filter_end_date"] = selected_range
    return {
        "department": st.session_state["filter_department"],
        "start_date": st.session_state.get("filter_start_date"),
        "end_date": st.session_state.get("filter_end_date"),
        "status": st.session_state["filter_status"],
    }
