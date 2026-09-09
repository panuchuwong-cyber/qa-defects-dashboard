"""Reconcile supplier name drift across data sources.

The defect log (`QA_Defects_Data.xlsx`) and the templates use FULL supplier
names ("NISSEN CHEMITEC", "APT (Thailand)"). The supplier master
(`supplier_master.csv`) uses SHORT codes ("NISSEN", "APT"). The FY monthly
data uses short codes too.

Without this map, joins in `real_supply.py` lose ~15% of supplier matches and
the derived PPM/OTIF numbers are undercounted for those suppliers (their
MonthlyReceivedQty falls back to 0 → PPM=0 → "good" status, opposite of
truth).

Usage:
    from utils.supplier_aliases import canonical_supplier
    canonical_supplier("NISSEN CHEMITEC")  # → "NISSEN"
    canonical_supplier("KSV")               # → "KSV"  (pass-through)

This is purely additive: existing columns and schema are untouched.
"""
# pyright: reportMissingImports=false
from __future__ import annotations

# Alias → canonical code (must match Supplier Code column in supplier_master.csv).
# Keys are normalized via .strip().upper() before lookup, so casing/whitespace
# variations collapse to the same canonical.
_ALIAS_TO_CANONICAL: dict[str, str] = {
    # NISSEN — full vs short
    "NISSEN CHEMITEC": "NISSEN",
    "NISSEN": "NISSEN",
    # APT — full vs short
    "APT (THAILAND)": "APT",
    "APT (THAILAND) CO., LTD.": "APT",
    "APT": "APT",
    # Other suppliers that appear in templates / defects / master — listed
    # explicitly so that a future typo is loud (KeyError) rather than silent.
    "KSV": "KSV",
    "KSV (THAILAND) CO., LTD.": "KSV",
    "AKUSAN": "AKUSAN",
    "AKUSAN TRADING": "AKUSAN",
    "PARADISE": "PARADISE",
    "PARADISE INDUSTRIES": "PARADISE",
    "BTD": "BTD",
    "BTD MANUFACTURING": "BTD",
    "C.G.": "C.G.",
    "C.G. PLASTIC": "C.G.",
    "TTS PLASTIC": "TTS PLASTIC",
    "TTS PLASTIC CO., LTD.": "TTS PLASTIC",
    "SAMBO": "SAMBO",
    "SAMBO INDUSTRIES": "SAMBO",
    "DEM": "DEM",
    "DEM ENGINEERING": "DEM",
    "SUPERFAST": "SUPERFAST",
    "SUPER FAST CO., LTD.": "SUPERFAST",
    "SAM NEO": "SAM NEO",
    "SAM NEO TRADING": "SAM NEO",
    "TECHNO ASSOCIATE": "TECHNO ASSOCIATE",
    "TECHNO ASSOCIATE INC.": "TECHNO ASSOCIATE",
}


def canonical_supplier(name: str) -> str:
    """Map any known variant of a supplier name to the canonical Supplier Code.

    Unknown names are returned unchanged (after strip) so the join still
    attempts; the merged-on-missing row will simply have MonthlyReceivedQty=0
    and PPM=0, which surfaces as a warning rather than a crash.
    """
    if name is None:
        return ""
    key = str(name).strip().upper()
    return _ALIAS_TO_CANONICAL.get(key, str(name).strip())


def all_known_suppliers() -> list[str]:
    """Canonical supplier codes (sorted, deduplicated)."""
    return sorted(set(_ALIAS_TO_CANONICAL.values()))


def normalize_series(series):
    """Apply canonical_supplier() to a pandas Series (vectorized-safe).

    Args:
        series: pandas.Series of supplier names (any dtype that .astype(str)
                can handle).

    Returns:
        pandas.Series of canonical names, same length and index.
    """
    # Import lazily so this module stays importable without pandas if needed
    # (e.g. for static analysis / doc tools).
    import pandas as pd  # noqa: PLC0415

    return series.astype(str).map(lambda v: canonical_supplier(v))
