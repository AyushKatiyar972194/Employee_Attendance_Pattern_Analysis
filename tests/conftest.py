"""Pytest configuration and global fixtures for EAPA-01."""
import pytest
from pathlib import Path
from src.config import DB_PATH
from src.data_loader import reset_database_to_canonical


@pytest.fixture(autouse=True, scope="session")
def ensure_canonical_db():
    """Ensure database is restored to canonical 2,400-record baseline before and after tests."""
    reset_database_to_canonical(DB_PATH)
    yield
    reset_database_to_canonical(DB_PATH)
