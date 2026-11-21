"""CSV export helper for P070.

Provides filtered DataFrame-to-CSV conversion with UTF-8 headers.
"""
from __future__ import annotations

import io

import pandas as pd


def dataframe_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Convert a DataFrame to UTF-8 CSV bytes for Streamlit download.

    Includes column headers. Returns bytes suitable for
    st.download_button(data=...).
    """
    buffer = io.BytesIO()
    df.to_csv(buffer, index=False, encoding="utf-8-sig")
    return buffer.getvalue()


def export_filtered_data(
    df: pd.DataFrame,
    columns: list[str] | None = None,
) -> bytes:
    """Export a (possibly filtered) DataFrame as CSV bytes.

    Parameters
    ----------
    df : The DataFrame to export (already filtered by caller).
    columns : Optional subset of columns to include.

    Returns
    -------
    UTF-8 CSV bytes with BOM for Excel compatibility.
    """
    if columns:
        export_df = df[[c for c in columns if c in df.columns]]
    else:
        export_df = df

    return dataframe_to_csv_bytes(export_df)
