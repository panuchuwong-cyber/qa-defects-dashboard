"""Mock supply chain data for supplier score, OTIF, SCAR.

These functions generate simulated data when real columns aren't in Excel.
Real OTIF/SCAR requires: delivery_date, qty_ordered, qty_received, scar_status.
"""
# pyright: reportMissingImports=false
from __future__ import annotations
from datetime import datetime, timedelta

import pandas as pd


def get_supplier_scores(df: pd.DataFrame, window_days: int = 14) -> pd.DataFrame:
    """Calculate supplier composite quality score from defect data.

    Score formula (higher = worse supplier):
        score = (0.45 * case_norm) + (0.35 * qty_norm) + (0.20 * freq_norm)

    Each dimension is normalized by max across all suppliers in the window:
        - qty_norm:   total defect Q'TY
        - case_norm:  count of rows where Comment contains CASE or REJECT
        - freq_norm:  fraction of days in window that had at least one defect

    Weights rationale:
        - 0.45 case:  one CASE may reject an entire lot (severity-weighted)
        - 0.35 qty:   small-issue aggregation volume
        - 0.20 freq:  captures chronicity (defects every day = worse than one bad batch)

    Status thresholds (on score_pct, 0-100 scale):
        - critical:  >= 70
        - warning:   40-69
        - good:      < 40

    Returns DataFrame sorted by score desc (worst first):
        Rank / Supplier / Qty / Case / Days / Freq / Score / ScorePct / Status
    """
    if df is None or df.empty:
        return pd.DataFrame(
            columns=["Rank", "Supplier", "Qty", "Case", "Days",
                     "Freq", "Score", "ScorePct", "Status"]
        )

    # Ensure Date is datetime
    work = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(work["Date"]):
        work["Date"] = pd.to_datetime(work["Date"], format="mixed", errors="coerce")
    work = work.dropna(subset=["Date"]).reset_index(drop=True)
    if work.empty:
        return pd.DataFrame(
            columns=["Rank", "Supplier", "Qty", "Case", "Days",
                     "Freq", "Score", "ScorePct", "Status"]
        )

    # Slice to window
    max_date = work["Date"].max()
    cutoff = max_date - pd.Timedelta(days=window_days - 1)
    recent = work[work["Date"] >= cutoff].copy()

    if recent.empty:
        return pd.DataFrame(
            columns=["Rank", "Supplier", "Qty", "Case", "Days",
                     "Freq", "Score", "ScorePct", "Status"]
        )

    # Severity weight (higher = worse): CRITICAL=1.0, MAJOR=0.5, MINOR=0.1
    SEVERITY_WEIGHT = {"CRITICAL": 1.0, "MAJOR": 0.5, "MINOR": 0.1}

    if "Severity" in recent.columns:
        # Use Severity column for weighted severity score
        recent["severity_w"] = (
            recent["Severity"].astype(str).str.strip().str.upper()
            .map(SEVERITY_WEIGHT).fillna(0.0)
        )
        # Case = count of CRITICAL + MAJOR rows (proxy for severity cases)
        recent["is_case"] = (recent["severity_w"] >= 0.5).astype(int)
    else:
        # Fallback: detect CASE/REJECT from Comment
        recent["is_case"] = (
            recent["Comment"].astype(str)
            .str.contains("CASE|REJECT", case=False, na=False)
            .astype(int)
        )

    # Aggregate per supplier
    agg = (recent.groupby("Supplier")
                  .agg(Qty=("Qty", "sum"),
                       Case=("is_case", "sum"),
                       Days=("Date", lambda x: x.dt.date.nunique()))
                  .reset_index())

    agg["Freq"] = (agg["Days"] / window_days).round(3)

    # Normalize each dimension by max across all suppliers
    for col in ["Qty", "Case", "Freq"]:
        max_val = agg[col].max()
        agg[f"{col.lower()}_norm"] = (
            (agg[col] / max_val).round(3) if max_val > 0 else 0.0
        )

    # Composite score (0-1) → scale to 0-100 for readability
    agg["Score"] = (
        0.45 * agg["case_norm"]
        + 0.35 * agg["qty_norm"]
        + 0.20 * agg["freq_norm"]
    ).round(4)
    agg["ScorePct"] = (agg["Score"] * 100).round(1)

    # Status based on ScorePct
    def status(pct: float) -> str:
        if pct >= 70:
            return "critical"
        if pct >= 40:
            return "warning"
        return "good"

    agg["Status"] = agg["ScorePct"].apply(status)

    # Sort worst first, add rank
    agg = agg.sort_values("Score", ascending=False).reset_index(drop=True)
    agg.insert(0, "Rank", range(1, len(agg) + 1))

    # Final column order
    return agg[["Rank", "Supplier", "Qty", "Case", "Days", "Freq",
                "Score", "ScorePct", "Status"]]


def mock_otif(window_days: int = 14) -> dict:
    """Generate mock OTIF data.

    Returns dict: {otif_pct, on_time_pct, in_full_pct, total_orders, late_orders}
    """
    import random
    random.seed(42)  # Stable mock data

    total = 487
    late = 19
    short = 8
    otif_pct = round((total - late - short) / total * 100, 1)
    on_time = round((total - late) / total * 100, 1)
    in_full = round((total - short) / total * 100, 1)

    return {
        "otif_pct": otif_pct,
        "on_time_pct": on_time,
        "in_full_pct": in_full,
        "total_orders": total,
        "late_orders": late,
        "short_orders": short,
        "window_days": window_days,
    }


def mock_scars() -> list:
    """Generate mock SCAR (Supplier Corrective Action Request) list."""
    today = datetime.now()
    return [
        {
            "id": "SCAR-2026-089",
            "supplier": "BTD",
            "defect": "LEAK",
            "priority": "high",
            "qty_affected": 187,
            "open_date": (today - timedelta(days=2)).strftime("%Y-%m-%d"),
            "due_date": (today + timedelta(days=5)).strftime("%Y-%m-%d"),
            "status": "in_progress",
        },
        {
            "id": "SCAR-2026-087",
            "supplier": "AKUSAN",
            "defect": "DIMENSION NG",
            "priority": "medium",
            "qty_affected": 51,
            "open_date": (today - timedelta(days=5)).strftime("%Y-%m-%d"),
            "due_date": (today + timedelta(days=9)).strftime("%Y-%m-%d"),
            "status": "awaiting_response",
        },
        {
            "id": "SCAR-2026-085",
            "supplier": "KSV",
            "defect": "APPEARANCE NG",
            "priority": "low",
            "qty_affected": 23,
            "open_date": (today - timedelta(days=8)).strftime("%Y-%m-%d"),
            "due_date": (today + timedelta(days=14)).strftime("%Y-%m-%d"),
            "status": "in_progress",
        },
    ]
