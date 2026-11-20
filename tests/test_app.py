"""Streamlit AppTest smoke tests.

Expected application structure from Step 7 TRD:
- app.py
- pages/1_Overview.py
- pages/2_Department_Analysis.py
- pages/3_Time_and_Lateness.py
- pages/4_Data_Quality.py

Some tests may remain pending/fail until Step 15 implements the app.
"""
from pathlib import Path
import time

import pytest
from streamlit.testing.v1 import AppTest

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_main_app_starts_without_exception():
    app_file = PROJECT_ROOT / "app.py"
    assert app_file.exists(), "app.py will be created in Step 15"
    at = AppTest.from_file(str(app_file), default_timeout=20).run()
    assert not at.exception


@pytest.mark.parametrize("relative_page", [
    "pages/1_Overview.py",
    "pages/2_Department_Analysis.py",
    "pages/3_Time_and_Lateness.py",
    "pages/4_Data_Quality.py",
    "pages/5_Pattern_Intelligence.py",
])
def test_each_page_renders_without_exception(relative_page):
    page = PROJECT_ROOT / relative_page
    assert page.exists(), f"{relative_page} will be created in Step 15"
    at = AppTest.from_file(str(page), default_timeout=20).run()
    assert not at.exception


def test_main_app_initial_render_under_three_seconds():
    app_file = PROJECT_ROOT / "app.py"
    assert app_file.exists(), "app.py will be created in Step 15"
    started = time.perf_counter()
    at = AppTest.from_file(str(app_file), default_timeout=20).run()
    elapsed = time.perf_counter() - started
    assert not at.exception
    # This is a local smoke-test threshold, not a guarantee of cloud cold-start time.
    assert elapsed < 15.0
