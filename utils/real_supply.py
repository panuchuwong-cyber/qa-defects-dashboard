"""Real supply chain metrics derived from defect log + supplier master.

Replaces mock_supply.py — all numbers come from QA_Defects_Data.xlsx and
supplier_master.csv, no random data.

Derived metrics (proxy until delivery tracking is wired up):
- OTIF: 1 - defect_qty / monthly_received_qty  per supplier → aggregate
- SCAR: top defect groups by qty (>= 50 or >= 3 cases) become action items

When real delivery tracking is added (columns: delivery_date, qty_ordered,
qty_received, scar_status), swap these functions to read from those.
"""
# pyright: reportMissingImports=false
from __future__ import annotations

from datetime import timedelta
from pathlib import Path

import pandas as pd


SCAR_QTY_THRESHOLD = 50    # defect qty that opens a SCAR
SCAR_CASE_THRESHOLD = 3    # defect cases that open a SCAR


def _load_supplier_master() -> pd.DataFrame:
    """Load supplier master CSV shipped with the repo."""
    csv_path = Path(__file__).parent.parent / "supplier_master.csv"
    if not csv_path.exists():
        return pd.DataFrame(columns=["Supplier Code", "Monthly Received Qty"])
    return pd.read_csv(csv_path)


def get_supplier_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate supplier quality score from defect data.

    Score = PPM (parts per million) — lower is better.
    PPM uses Monthly Received Qty from supplier_master as denominator
    (real, not assumed).

    Returns DataFrame sorted by defect qty desc (worst first).
    """
    if df is None or df.empty:
        return pd.DataFrame()

    master = _load_supplier_master()
    monthly = dict(zip(master["Supplier Code"], master["Monthly Received Qty"]))

    agg = (df.groupby("Supplier")
             .agg(Qty=("Qty", "sum"),
                  Cases=("Qty", "count"),
                  UniqueParts=("Part No", "nunique"))
             .reset_index())

    # PPM with real monthly received qty; fall back to 0 if supplier not in master
    agg["MonthlyReceived"] = agg["Supplier"].map(monthly).fillna(0).astype(int)
    agg["PPM"] = agg.apply(
        lambda r: round((r["Qty"] / r["MonthlyReceived"]) * 1_000_000, 1)
                  if r["MonthlyReceived"] > 0 else 0.0,
        axis=1,
    )

    def status(ppm):
        if ppm > 5_000:
            return "critical"
        if ppm > 2_000:
            return "warning"
        return "good"

    agg["Status"] = agg["PPM"].apply(status)
    agg = agg.sort_values("Qty", ascending=False).reset_index(drop=True)
    agg.insert(0, "Rank", range(1, len(agg) + 1))
    return agg


def real_otif(df: pd.DataFrame, window_days: int = 14) -> dict:
    """Calculate proxy OTIF from defect log + supplier master.

    OTIF proxy per supplier = max(0, 1 - defect_qty / monthly_received)
    Aggregated as qty-weighted average across suppliers with deliveries.

    Returns dict with otif_pct, on_time_pct, in_full_pct, supplier_count.
    """
    if df is None or df.empty:
        return _empty_otif(window_days)

    master = _load_supplier_master()
    if master.empty:
        return _empty_otif(window_days)

    # Filter to last N days
    cutoff = pd.Timestamp.now().normalize() - pd.Timedelta(days=window_days)
    recent = df[df["Date"] >= cutoff].copy()
    if recent.empty:
        recent = df.copy()  # fallback to all data if window too narrow

    defect_qty = recent.groupby("Supplier")["Qty"].sum().reset_index()
    defect_qty.columns = ["Supplier", "DefectQty"]

    # Merge with monthly received (assume monthly = 30-day window)
    merged = master.merge(defect_qty, left_on="Supplier Code",
                          right_on="Supplier", how="left")
    merged["DefectQty"] = merged["DefectQty"].fillna(0).astype(int)
    merged["DefectRate"] = merged["DefectQty"] / merged["Monthly Received Qty"]

    # On-time proxy: 1 - defect_rate (no defect = on-time)
    merged["OnTimeProxy"] = (1 - merged["DefectRate"]).clip(lower=0, upper=1)

    # In-full proxy: same logic — short shipments show up as defects
    merged["InFullProxy"] = (1 - merged["DefectRate"]).clip(lower=0, upper=1)

    # Qty-weighted aggregation
    total_received = merged["Monthly Received Qty"].sum()
    if total_received == 0:
        return _empty_otif(window_days)

    otif_pct = round((merged["OnTimeProxy"] * merged["Monthly Received Qty"]).sum()
                     / total_received * 100, 1)
    on_time_pct = otif_pct
    in_full_pct = otif_pct

    return {
        "otif_pct": otif_pct,
        "on_time_pct": on_time_pct,
        "in_full_pct": in_full_pct,
        "total_orders": int(total_received),
        "late_orders": int(merged["DefectQty"].sum()),
        "short_orders": 0,
        "supplier_count": int((merged["DefectQty"] > 0).sum()),
        "window_days": window_days,
        "is_proxy": True,
    }


def real_scars(df: pd.DataFrame) -> list:
    """Derive open SCARs from top defect groups.

    A SCAR opens when a Supplier + Problem Mode combo exceeds either:
    - SCAR_QTY_THRESHOLD defect qty, OR
    - SCAR_CASE_THRESHOLD cases

    SCAR ID format: SCAR-{YEAR}-{SEQ:03d}  (sequential within year)
    """
    if df is None or df.empty:
        return []

    today = pd.Timestamp.now().normalize()
    year = today.year

    grouped = (df.groupby(["Supplier", "Problem Mode"])
                 .agg(Cases=("Qty", "count"),
                      Qty=("Qty", "sum"),
                      FirstSeen=("Date", "min"),
                      LastSeen=("Date", "max"),
                      Parts=("Part No", "nunique"))
                 .reset_index())

    # Filter: open SCAR candidates
    candidates = grouped[
        (grouped["Qty"] >= SCAR_QTY_THRESHOLD) |
        (grouped["Cases"] >= SCAR_CASE_THRESHOLD)
    ].sort_values("Qty", ascending=False).reset_index(drop=True)

    scars = []
    for i, row in candidates.iterrows():
        # Priority: qty >= 200 → high, >= 100 → medium, else low
        if row["Qty"] >= 200:
            priority = "high"
        elif row["Qty"] >= 100:
            priority = "medium"
        else:
            priority = "low"

        # Status: if LastSeen within 3 days → in_progress, else awaiting
        days_since = (today - row["LastSeen"]).days
        status = "in_progress" if days_since <= 3 else "awaiting_response"

        # Due date: 7 days from first seen (proxy for response SLA)
        due = row["FirstSeen"] + timedelta(days=7)

        scars.append({
            "id": f"SCAR-{year}-{i+1:03d}",
            "supplier": row["Supplier"],
            "defect": row["Problem Mode"],
            "priority": priority,
            "qty_affected": int(row["Qty"]),
            "cases": int(row["Cases"]),
            "open_date": row["FirstSeen"].strftime("%Y-%m-%d"),
            "due_date": due.strftime("%Y-%m-%d"),
            "status": status,
        })

    return scars


def _empty_otif(window_days: int) -> dict:
    return {
        "otif_pct": 0.0,
        "on_time_pct": 0.0,
        "in_full_pct": 0.0,
        "total_orders": 0,
        "late_orders": 0,
        "short_orders": 0,
        "supplier_count": 0,
        "window_days": window_days,
        "is_proxy": True,
    }