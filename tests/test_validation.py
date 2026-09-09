"""Acceptance tests for the supplier alias + validation utilities.

Run: python3 tests/test_validation.py

Pure-pandas tests — no Streamlit runtime, no app.py import. Mirrors the
AppTest pattern from pitfalls #86 but is even simpler: just call the
utility functions with fixture data and assert on the result.

These tests are BACKWARD-COMPATIBLE: they only assert behavior, not
internal implementation. Adding new tests is safe; renaming or removing
tests requires updating the phased plan.
"""
# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportCallIssue=false, reportArgumentType=false
from __future__ import annotations

import sys
from pathlib import Path

# Make ../utils importable without installing the package
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import pandas as pd

from utils.supplier_aliases import canonical_supplier, normalize_series, all_known_suppliers  # noqa: E402
from utils.validation import (  # noqa: E402
    detect_header_row,
    normalize_columns,
    coerce_types,
    validate_dataframe,
    safe_read_excel,
    REQUIRED_COLUMNS,
)


passed = 0
failed = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        print(f"  ✓ {name}")
        passed += 1
    else:
        print(f"  ✗ {name}  {detail}")
        failed += 1


# =====================================================================
# supplier_aliases
# =====================================================================
print("\n[1] supplier_aliases.canonical_supplier")
check(
    "NISSEN CHEMITEC → NISSEN",
    canonical_supplier("NISSEN CHEMITEC") == "NISSEN",
)
check(
    "NISSEN → NISSEN (idempotent)",
    canonical_supplier("NISSEN") == "NISSEN",
)
check(
    "APT (Thailand) → APT",
    canonical_supplier("APT (Thailand)") == "APT",
)
check(
    "lowercase nissen chemitec → NISSEN",
    canonical_supplier("  nissen chemitec  ") == "NISSEN",
)
check(
    "unknown supplier returns stripped original",
    canonical_supplier("NEW_UNKNOWN_SUPPLIER") == "NEW_UNKNOWN_SUPPLIER",
)
check(
    "None → empty string",
    canonical_supplier(None) == "",
)


print("\n[2] supplier_aliases.normalize_series")
s = pd.Series(["NISSEN CHEMITEC", "APT (Thailand)", "KSV", "nonsense"])
result = normalize_series(s)
check(
    "vectorized mapping returns canonical codes",
    list(result) == ["NISSEN", "APT", "KSV", "nonsense"],
    f"got {list(result)}",
)


print("\n[3] supplier_aliases.all_known_suppliers")
known = all_known_suppliers()
check(
    "contains KSV",
    "KSV" in known,
)
check(
    "contains AKUSAN",
    "AKUSAN" in known,
)
check(
    "no duplicates",
    len(known) == len(set(known)),
    f"got {known}",
)


# =====================================================================
# validation.normalize_columns
# =====================================================================
print("\n[4] validation.normalize_columns")
df = pd.DataFrame({" Date ": [1], "Supplier ": ["X"], "Qty": [5]})
norm = normalize_columns(df)
check(
    "strips whitespace from column names",
    list(norm.columns) == ["Date", "Supplier", "Qty"],
    f"got {list(norm.columns)}",
)


# =====================================================================
# validation.coerce_types
# =====================================================================
print("\n[5] validation.coerce_types")
df = pd.DataFrame([{
    "Date": "2026-09-01",
    "Supplier": "KSV",
    "Group Part": "PLASTIC",
    "Problem Mode": "PART MISTAKE",
    "Part Name": "COVER",
    "Part No": "X-1",
    "Qty": "12",
    "Comment": "  scratch  ",
}])
c = coerce_types(df)
check(
    "Qty coerced to numeric",
    c["Qty"].iloc[0] == 12,
    f"got {c['Qty'].iloc[0]!r} (dtype={c['Qty'].dtype})",
)
check(
    "Date parsed to datetime",
    pd.api.types.is_datetime64_any_dtype(c["Date"]),
    f"got dtype={c['Date'].dtype}",
)
check(
    "Comment stripped",
    c["Comment"].iloc[0] == "scratch",
    f"got {c['Comment'].iloc[0]!r}",
)


# =====================================================================
# validation.validate_dataframe
# =====================================================================
print("\n[6] validation.validate_dataframe — happy path")
df = pd.DataFrame([
    {"Date": "2026-09-01", "Supplier": "KSV", "Group Part": "PLASTIC",
     "Problem Mode": "PART MISTAKE", "Part Name": "COVER", "Part No": "X-1",
     "Qty": 12, "Comment": "ok"},
    {"Date": "2026-09-02", "Supplier": "NISSEN", "Group Part": "PIPING",
     "Problem Mode": "LEAK", "Part Name": "PIPE", "Part No": "P-2",
     "Qty": 5, "Comment": ""},
])
valid, errors, invalid = validate_dataframe(df)
check("valid_df has 2 rows", len(valid) == 2, f"got {len(valid)}")
check("no errors", len(errors) == 0, f"got {errors}")
check("invalid_df empty", len(invalid) == 0)


print("\n[7] validation.validate_dataframe — bad rows detected")
df = pd.DataFrame([
    {"Date": "2026-09-01", "Supplier": "KSV", "Group Part": "PLASTIC",
     "Problem Mode": "PART MISTAKE", "Part Name": "COVER", "Part No": "X-1",
     "Qty": 12, "Comment": "ok"},
    {"Date": "garbage", "Supplier": "KSV", "Group Part": "PLASTIC",
     "Problem Mode": "PART MISTAKE", "Part Name": "COVER", "Part No": "X-2",
     "Qty": 3, "Comment": ""},
    {"Date": "2026-09-02", "Supplier": "BTD", "Group Part": "PLASTIC",
     "Problem Mode": "PART MISTAKE", "Part Name": "COVER", "Part No": "",
     "Qty": 5, "Comment": ""},
    {"Date": "2026-09-03", "Supplier": "BTD", "Group Part": "PLASTIC",
     "Problem Mode": "PART MISTAKE", "Part Name": "COVER", "Part No": "Y-1",
     "Qty": 0, "Comment": ""},
])
valid, errors, invalid = validate_dataframe(df)
check("valid_df has 1 row", len(valid) == 1, f"got {len(valid)}")
check("3 errors reported", len(errors) == 3, f"got {len(errors)}")
check(
    "errors cover Date / Part No / Qty",
    all(any("Date" in e or "Part No" in e or "Qty" in e
            for e in err["errors"]) for err in errors),
)


print("\n[8] validation.validate_dataframe — missing required columns")
df = pd.DataFrame([{"Foo": 1, "Bar": 2}])
valid, errors, invalid = validate_dataframe(df)
check("returns empty valid_df", len(valid) == 0)
check("returns 1 schema error", len(errors) == 1, f"got {len(errors)}")
check("error mentions missing columns", "Missing required columns" in errors[0]["errors"][0])


print("\n[9] validation.validate_dataframe — empty df")
valid, errors, invalid = validate_dataframe(pd.DataFrame())
check("empty input returns empty valid", len(valid) == 0)
check("empty input returns no errors", len(errors) == 0)


# =====================================================================
# validation.detect_header_row + safe_read_excel
# =====================================================================
print("\n[10] validation.detect_header_row — live file (header on row 1)")
live = REPO / "QA_Defects_Data.xlsx"
if live.exists():
    detected = detect_header_row(live)
    check("live file header detected at row 0", detected == 0,
          f"got {detected}")
    df_live = safe_read_excel(live)
    check("safe_read_excel returns 8 columns", df_live.shape[1] == 8,
          f"got shape {df_live.shape}")
    check("expected Date column present", "Date" in df_live.columns)
    check("expected Part No column present", "Part No" in df_live.columns)


print("\n[11] validation.detect_header_row — legacy template (header on row 4)")
legacy = REPO / "QA_Defects_Template.xlsx"
if legacy.exists():
    detected = detect_header_row(legacy, sheet_name="Defects Data")
    check("legacy template header detected at row 3", detected == 3,
          f"got {detected}")
    df_legacy = safe_read_excel(legacy, sheet_name="Defects Data")
    check("legacy template reads 8 named columns", df_legacy.shape[1] == 8,
          f"got shape {df_legacy.shape}, cols={list(df_legacy.columns)}")
    check("Date column named (not Unnamed)", "Date" in df_legacy.columns,
          f"got {list(df_legacy.columns)}")


print("\n[12] validation.detect_header_row — 14-day template (header on row 1)")
t14 = REPO / "QA_Defects_Template_14days.xlsx"
if t14.exists():
    detected = detect_header_row(t14, sheet_name="Defects Data")
    check("14-day template header on row 0", detected == 0,
          f"got {detected}")


# =====================================================================
# End-to-end: load_data behavior contract (without importing app.py)
# =====================================================================
print("\n[13] End-to-end — legacy template loads correctly via safe_read_excel")
if legacy.exists():
    df = safe_read_excel(legacy, sheet_name="Defects Data")
    valid, errors, invalid = validate_dataframe(df)
    # Legacy template has 5 sample data rows; all should be valid
    check("valid sample rows preserved", len(valid) == 5,
          f"got {len(valid)} valid")
    check("no validation errors", len(errors) == 0, f"got {errors}")


# =====================================================================
print(f"\n{'=' * 60}")
print(f"PASSED: {passed}   FAILED: {failed}")
print(f"{'=' * 60}")
sys.exit(0 if failed == 0 else 1)
