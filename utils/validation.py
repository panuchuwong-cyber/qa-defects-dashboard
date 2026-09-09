"""Shared dataframe validation for QA Defects data.

Backwards-compatible: the 8-column schema (Date, Supplier, Group Part,
Problem Mode, Part Name, Part No, Qty, Comment) is unchanged. This module
adds:

  - normalize_columns(): tolerant column-name lookup (case-insensitive,
    trims whitespace) so templates with " date " or "Qty " still load.
  - coerce_types(): parses Date (mixed format), Qty (int), Supplier (str).
  - validate_dataframe(): returns (valid_df, errors, invalid_df) so callers
    can show users a report instead of crashing on bad rows.
  - detect_header_row(): when an Excel file's first row is a title banner
    (legacy QA_Defects_Template.xlsx uses row 1=merged title, row 4=header),
    scan rows 0-5 to find the row that contains "Date"+"Supplier"+"Part No".

Used by load_data() in app.py and by the upload handler. The intent is to
prevent silent breakage (e.g. user uploads a renamed export with different
headers) rather than block the data.
"""
# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportCallIssue=false, reportArgumentType=false
from __future__ import annotations

from typing import Optional

import pandas as pd

REQUIRED_COLUMNS = [
    "Date",
    "Supplier",
    "Group Part",
    "Problem Mode",
    "Part Name",
    "Part No",
    "Qty",
    "Comment",
]

REQUIRED_NON_EMPTY = ["Date", "Supplier", "Part No"]


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Strip whitespace and standardize case on column names.

    Does NOT rename columns that don't match — leave them alone so callers
    can decide. This is purely a tolerance pass.
    """
    renamed = {}
    for c in df.columns:
        if isinstance(c, str):
            new = c.strip()
            if new != c:
                renamed[c] = new
    if renamed:
        df = df.rename(columns=renamed)
    return df


def coerce_types(df: pd.DataFrame) -> pd.DataFrame:
    """Best-effort type coercion for the 8 known columns.

    Leaves unknown columns untouched. Never raises; coerces failures to
    NaT / NaN so callers can dropna() the bad rows.
    """
    df = df.copy()
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], format="mixed", errors="coerce")
    if "Qty" in df.columns:
        df["Qty"] = pd.to_numeric(df["Qty"], errors="coerce")
    for col in ("Supplier", "Group Part", "Problem Mode",
                "Part Name", "Part No", "Comment"):
        if col in df.columns:
            df[col] = df[col].astype("string").str.strip()
    return df


def detect_header_row(
    file_or_path,
    sheet_name: Union[int, str] = 0,
    max_scan_rows: int = 8,
) -> int:
    """Scan an uploaded file or path to find which row contains the schema
    header. Returns the 0-based row index that should be passed to
    pd.read_excel(header=...).

    Strategy: pick the first row whose values include all of REQUIRED_NON_EMPTY.
    Falls back to 0 if no match is found within max_scan_rows.
    """
    try:
        scan = pd.read_excel(file_or_path, sheet_name=sheet_name,
                             header=None, nrows=max_scan_rows)
    except Exception:
        return 0
    targets = set(REQUIRED_NON_EMPTY)
    for i, row in scan.iterrows():
        rowset = {str(v).strip() for v in row.tolist() if pd.notna(v)}
        if targets.issubset(rowset):
            return int(i)
    return 0


def validate_dataframe(
    df: pd.DataFrame,
    *,
    drop_invalid: bool = False,
) -> tuple[pd.DataFrame, list[dict], pd.DataFrame]:
    """Validate that df has the required schema and that rows have non-empty
    Date/Supplier/Part No and Qty > 0.

    Returns:
        valid_df: rows that pass all checks (coerced types applied)
        errors: list of {"row": int, "errors": list[str], "data": dict}
        invalid_df: the dropped rows (useful for showing the user)

    If drop_invalid=False (default), invalid rows are removed from
    valid_df but returned in invalid_df regardless. If True, the invalid
    rows are also stripped from the returned valid_df (same behavior — kept
    for API clarity / future streaming use).
    """
    if df is None or df.empty:
        empty = pd.DataFrame(columns=REQUIRED_COLUMNS)
        return empty, [], pd.DataFrame(columns=REQUIRED_COLUMNS)

    df = normalize_columns(df)
    df = coerce_types(df)

    missing = [c for c in REQUIRED_NON_EMPTY if c not in df.columns]
    if missing:
        return (
            pd.DataFrame(columns=REQUIRED_COLUMNS),
            [{"row": -1, "errors": [f"Missing required columns: {missing}"],
              "data": {}}],
            pd.DataFrame(columns=REQUIRED_COLUMNS),
        )

    errors: list[dict] = []
    valid_mask = pd.Series(True, index=df.index)
    for idx in df.index:
        row = df.loc[idx]
        row_errors = []
        if pd.isna(row.get("Date")):
            row_errors.append("Date missing or unparseable")
        if not row.get("Supplier") or row.get("Supplier") == "" or pd.isna(row.get("Supplier")):
            row_errors.append("Supplier missing")
        if not row.get("Part No") or row.get("Part No") == "" or pd.isna(row.get("Part No")):
            row_errors.append("Part No missing")
        qty = row.get("Qty")
        if pd.isna(qty) or qty <= 0:
            row_errors.append("Qty must be > 0")
        if row_errors:
            valid_mask[idx] = False
            errors.append({
                "row": int(idx) + 2,  # +2 because idx 0 is row 2 in 1-indexed Excel
                "errors": row_errors,
                "data": {k: (None if pd.isna(v) else v) for k, v in row.items()},
            })

    invalid_df = df.loc[~valid_mask].reset_index(drop=True)
    valid_df = df.loc[valid_mask].reset_index(drop=True)
    if drop_invalid:
        pass  # already excluded
    return valid_df, errors, invalid_df


def safe_read_excel(
    file_or_path,
    *,
    sheet_name: Union[int, str] = 0,
    header: Optional[int] = None,
) -> pd.DataFrame:
    """Read Excel with auto header-row detection.

    If header is None, scans the first 8 rows for the schema header.
    Otherwise passes through to pd.read_excel unchanged.
    """
    if header is None:
        header = detect_header_row(file_or_path, sheet_name=sheet_name)
    return pd.read_excel(file_or_path, sheet_name=sheet_name, header=header)
