"""Project-wide configuration constants for EAPA-01."""
from __future__ import annotations

from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "app.db"

# Attendance statuses
VALID_STATUSES = ("PRESENT", "ABSENT", "APPROVED_LEAVE", "HOLIDAY")

# Default grace period in minutes
DEFAULT_GRACE_MINUTES = 10

# Observation dates in October 2026 (20 working days)
OBSERVATION_DATES = [
    "2026-10-01", "2026-10-05", "2026-10-06", "2026-10-07", "2026-10-08", "2026-10-09",
    "2026-10-12", "2026-10-13", "2026-10-14", "2026-10-15", "2026-10-16",
    "2026-10-19", "2026-10-21", "2026-10-22", "2026-10-23",
    "2026-10-26", "2026-10-27", "2026-10-28", "2026-10-29", "2026-10-30",
]

# View name in SQLite
VIEW_NAME = "vw_attendance_analysis"
EXPECTED_VIEW_COLUMNS = 34
EXPECTED_ROW_COUNT = 2400
