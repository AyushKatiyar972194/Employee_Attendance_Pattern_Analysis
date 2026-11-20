"""Read-only SQLite access for EAPA-01.

Provides a safe connection helper with foreign keys enabled
and read-only pragmas for the synthetic dataset.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path


def get_connection(db_path: str | Path) -> sqlite3.Connection:
    """Return a read-only SQLite connection with foreign keys enabled."""
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.row_factory = sqlite3.Row
    return conn


def get_table_counts(db_path: str | Path) -> dict[str, int]:
    """Return row counts for all base tables safely."""
    tables = ["departments", "employees", "attendance_statuses",
              "work_calendar", "attendance_records"]
    counts = {table: 0 for table in tables}
    try:
        conn = get_connection(db_path)
        for table in tables:
            try:
                row = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
                if row:
                    counts[table] = int(row[0])
            except Exception:
                counts[table] = 0
        conn.close()
    except Exception:
        pass
    return counts


def get_observation_dates(db_path: str | Path) -> list[str]:
    """Return sorted distinct observation dates from attendance_records safely."""
    try:
        conn = get_connection(db_path)
        rows = conn.execute(
            "SELECT DISTINCT attendance_date FROM attendance_records "
            "ORDER BY attendance_date"
        ).fetchall()
        conn.close()
        return [r[0] for r in rows]
    except Exception:
        return []
