"""Mock supply chain data for supplier score, OTIF, SCAR.

These functions generate simulated data when real columns aren't in Excel.
Real OTIF/SCAR requires: delivery_date, qty_ordered, qty_received, scar_status.
"""
# pyright: reportMissingImports=false
from __future__ import annotations
from datetime import datetime, timedelta

import pandas as pd


def get_supplier_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate supplier quality score from defect data.

    Score = PPM (parts per million) — lower is better.
    Returns DataFrame sorted by defect qty desc (worst first).
    """
    if df is None or df.empty:
        return pd.DataFrame()

    # Aggregate by supplier
    agg = (df.groupby("Supplier")
             .agg(Qty=("Qty", "sum"),
                  Cases=("Qty", "count"),
                  UniqueParts=("Part No", "nunique"))
             .reset_index())

    # PPM (proxy): assume total units received = Qty * 100 (mock)
    agg["TotalUnits"] = (agg["Qty"] * 100).astype(int)
    agg["PPM"] = ((agg["Qty"] / agg["TotalUnits"]) * 1_000_000).round(1)

    # Status based on PPM
    def status(ppm):
        if ppm > 30_000:
            return "critical"
        if ppm > 15_000:
            return "warning"
        return "good"

    agg["Status"] = agg["PPM"].apply(status)

    # Sort by defect qty (worst first)
    agg = agg.sort_values("Qty", ascending=False).reset_index(drop=True)
    agg.insert(0, "Rank", range(1, len(agg) + 1))

    return agg


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
