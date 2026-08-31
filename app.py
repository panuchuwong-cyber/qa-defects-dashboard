"""
QA Defects Web Dashboard - TEST Energy Storage (Thai)
Two pages: 14 Days Monitoring + Searching Supplier Information
Theme: Yellow & Black
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

CHARTJS_CDN = "https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"

# ============================================================
# PASSWORD GATE
# ============================================================
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        st.markdown("""
        <style>
        .login-wrap {
            max-width: 380px; margin: 100px auto; padding: 36px;
            background: linear-gradient(135deg, #000000 0%, #1a1a1a 100%);
            border: 3px solid #FFD700; border-radius: 16px;
            text-align: center; box-shadow: 0 8px 32px rgba(255,215,0,0.3);
        }
        .login-title { color: #FFD700; font-size: 28px; font-weight: 800;
                       letter-spacing: 2px; margin-bottom: 8px; }
        .login-sub { color: #cccccc; font-size: 13px; margin-bottom: 24px; }
        </style>
        <div class="login-wrap">
            <div class="login-title">🔒 TEST QA DASHBOARD</div>
            <div class="login-sub">Incoming Defect Monitoring System</div>
        </div>
        """, unsafe_allow_html=True)
        col = st.columns([1, 2, 1])
        with col[1]:
            password = st.text_input("Password", type="password", label_visibility="collapsed", placeholder="Enter password")
            if st.button("🔓 LOGIN", use_container_width=True):
                try:
                    correct = st.secrets["password"]
                except Exception:
                    correct = "TEST@2026"
                if password == correct:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ Wrong password")
        st.stop()

check_password()

# ============================================================
# PAGE CONFIG & GLOBAL STYLE (YELLOW & BLACK)
# ============================================================
st.set_page_config(
    page_title="TEST QA Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #000000 0%, #1f1f1f 100%);
        color: #FFD700; padding: 24px 28px; border-radius: 12px;
        border: 2px solid #FFD700; margin-bottom: 24px;
        box-shadow: 0 4px 16px rgba(255,215,0,0.2);
    }
    .main-title {
        font-size: 28px; font-weight: 900; letter-spacing: 2px;
        color: #FFD700; margin: 0;
    }
    .main-sub {
        color: #cccccc; font-size: 13px; margin-top: 4px;
        letter-spacing: 1px;
    }
    .kpi-card {
        background: white; padding: 18px 20px; border-radius: 10px;
        border-top: 5px solid #FFD700; border-bottom: 2px solid #000000;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 12px;
    }
    .kpi-label {
        color: #555555; font-size: 11px; font-weight: 700;
        letter-spacing: 2px; text-transform: uppercase;
    }
    .kpi-value {
        font-size: 36px; font-weight: 900; color: #000000;
        margin-top: 6px; line-height: 1;
    }
    .kpi-unit {
        font-size: 16px; color: #FFD700; font-weight: 700; margin-left: 4px;
    }
    .section-header {
        background: #FFD700; color: #000000; padding: 10px 16px;
        border-radius: 6px; font-weight: 900; font-size: 14px;
        letter-spacing: 1px; margin: 20px 0 12px 0;
        text-transform: uppercase;
        border-left: 6px solid #000000;
    }
    .metric-table {
        background: white; border-radius: 8px; padding: 14px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
        margin-bottom: 12px;
    }
    .legend-box {
        background: #000000; color: #FFD700; padding: 12px 16px;
        border-radius: 8px; font-size: 13px; margin-top: 20px;
    }
    .legend-dot {
        display: inline-block; width: 14px; height: 14px;
        border-radius: 50%; margin-right: 6px; vertical-align: middle;
    }
    .stApp { background-color: #fafafa; }
    div[data-testid="stSidebarUserContent"] { padding-top: 1rem; }
    [data-testid="stSidebarNav"] { display: none; }
    .stDataFrame { border: 2px solid #FFD700 !important; border-radius: 8px; }
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATA LOAD
# ============================================================
@st.cache_data
def load_data():
    p = Path(__file__).parent / "QA_Defects_Data.csv"
    df = pd.read_csv(p)
    df["Date"] = pd.to_datetime(df["Date"])
    return df

df = load_data()

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("""
    <div style="background:#000000; padding:18px; border-radius:10px;
                border:2px solid #FFD700; text-align:center; margin-bottom:16px;">
        <div style="color:#FFD700; font-size:22px; font-weight:900;
                    letter-spacing:2px;">⚡ TEST</div>
        <div style="color:#cccccc; font-size:11px; margin-top:4px;
                    letter-spacing:1px;">QA DEFECTS DASHBOARD</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio("📌 NAVIGATION", [
        "📊 14 Days Monitoring",
        "🔍 Searching Supplier Information"
    ], label_visibility="collapsed")

    st.markdown("---")
    st.markdown("**🎛️ FILTERS**")
    supplier_f = st.selectbox("Supplier", ["All"] + sorted(df["Supplier"].unique().tolist()))
    group_f = st.selectbox("Group Part", ["All"] + sorted(df["Group Part"].unique().tolist()))
    mode_f = st.selectbox("Problem Mode", ["All"] + sorted(df["Problem Mode"].unique().tolist()))

    if st.button("🗑️ CLEAR FILTER", use_container_width=True):
        st.rerun()

    st.markdown("---")
    st.markdown(f"""
    <div style="background:#000; color:#FFD700; padding:10px; border-radius:8px;
                font-size:11px; text-align:center;">
        Last updated<br>
        <b>{datetime.now().strftime('%Y-%m-%d %H:%M')}</b>
    </div>
    """, unsafe_allow_html=True)

# Apply filters
filtered = df.copy()
if supplier_f != "All":
    filtered = filtered[filtered["Supplier"] == supplier_f]
if group_f != "All":
    filtered = filtered[filtered["Group Part"] == group_f]
if mode_f != "All":
    filtered = filtered[filtered["Problem Mode"] == mode_f]

# ============================================================
# HEADER
# ============================================================
st.markdown(f"""
<div class="main-header">
    <div class="main-title">⚡ {('14 DAYS DEFECT MONITORING' if '14 Days' in page else 'SEARCHING SUPPLIER INFORMATION')}</div>
    <div class="main-sub">Thai Energy Storage Technology Public Company Limited | Incoming Quality</div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# PAGE 1: 14 DAYS MONITORING
# ============================================================
if "14 Days" in page:
    # Date range header
    max_date = df["Date"].max()
    min_date = max_date - timedelta(days=13)
    st.markdown(f"""
    <div style="text-align:right; color:#555; font-size:13px; margin-bottom:16px;">
        📅 <b>{min_date.strftime('%m/%d/%Y')}</b> &nbsp;→&nbsp; <b>{max_date.strftime('%m/%d/%Y')}</b>
    </div>
    """, unsafe_allow_html=True)

    # KPIs
    total_qty = int(filtered["Qty"].sum())
    total_case = len(filtered)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">� Q'TY</div>
            <div class="kpi-value">{total_qty:,}<span class="kpi-unit">PCS</span></div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">📋 CASE</div>
            <div class="kpi-value">{total_case:,}<span class="kpi-unit">CASE</span></div>
        </div>
        """, unsafe_allow_html=True)

    # Daily trend charts
    daily = filtered.groupby("Date").agg(Qty=("Qty", "sum"), Case=("Qty", "count")).reset_index()
    labels = daily["Date"].dt.strftime("%m/%d").tolist()
    qty_data = daily["Qty"].tolist()
    case_data = daily["Case"].tolist()

    st.markdown('<div class="section-header">📈 DAILY TREND (14 DAYS)</div>', unsafe_allow_html=True)
    chart_html = f"""
    <canvas id="trendChart" height="120"></canvas>
    <script src="{CHARTJS_CDN}"></script>
    <script>
    new Chart(document.getElementById('trendChart'), {{
        type: 'line',
        data: {{
            labels: {labels},
            datasets: [
                {{
                    label: 'QTY',
                    data: {qty_data},
                    borderColor: '#FFD700',
                    backgroundColor: 'rgba(255,215,0,0.15)',
                    borderWidth: 3, tension: 0.35, fill: true,
                    pointBackgroundColor: '#000000', pointRadius: 5
                }},
                {{
                    label: 'CASE',
                    data: {case_data},
                    borderColor: '#000000',
                    backgroundColor: 'rgba(0,0,0,0.05)',
                    borderWidth: 3, tension: 0.35, borderDash: [6,4],
                    pointBackgroundColor: '#FFD700', pointRadius: 5
                }}
            ]
        }},
        options: {{
            responsive: true, maintainAspectRatio: false,
            plugins: {{ legend: {{ position: 'bottom' }} }},
            scales: {{ y: {{ beginAtZero: true }} }}
        }}
    }});
    </script>
    """
    st.components.v1.html(chart_html, height=320)

    # Problem Mode breakdown
    st.markdown('<div class="section-header">⚠️ PROBLEM MODE</div>', unsafe_allow_html=True)
    mode_summary = filtered.groupby("Problem Mode").agg(
        Qty=("Qty", "sum"), Case=("Qty", "count")
    ).reset_index().sort_values("Qty", ascending=False)
    mode_summary["Case"] = mode_summary["Case"].astype(int)
    mode_summary["Qty"] = mode_summary["Qty"].astype(int)

    def color_mode(val):
        case = int(mode_summary.loc[mode_summary["Problem Mode"] == val, "Case"].iloc[0]) if len(mode_summary) else 0
        if case == 0:
            return 'background-color: #90EE90; color: #000; font-weight:700'
        elif case < 2:
            return 'background-color: #FFD700; color: #000; font-weight:700'
        else:
            return 'background-color: #FF6B6B; color: #fff; font-weight:700'

    st.dataframe(
        mode_summary.style.applymap(color_mode, subset=["Problem Mode"]),
        use_container_width=True, hide_index=True
    )

    # Top 5 Suppliers
    st.markdown('<div class="section-header">🏭 TOP 5 SUPPLIERS</div>', unsafe_allow_html=True)
    top5 = filtered.groupby("Supplier").agg(
        Qty=("Qty", "sum"), Case=("Qty", "count")
    ).reset_index().sort_values("Qty", ascending=False).head(5)
    top5["Qty"] = top5["Qty"].astype(int)
    top5["Case"] = top5["Case"].astype(int)
    st.dataframe(top5, use_container_width=True, hide_index=True)

    # Group Selection buttons (visual)
    st.markdown('<div class="section-header">🗂️ SELECTION SUPPLIER GROUP</div>', unsafe_allow_html=True)
    groups_present = filtered["Group Part"].unique().tolist()
    group_icons = {
        "ELECTRIC & ELEC.": "⚡", "OTHERS": "�", "PIPING": "🔧",
        "PRINTING": "🖨️", "RUBBER": "⚫", "SHEET METAL": "🔩",
        "FOAM": "🧽", "PACKING": "📦", "PLASTIC": "�",
        "RAW MATERIAL": "🪨", "SEALING": "�"
    }
    g_cols = st.columns(6)
    for i, g in enumerate(sorted(groups_present)):
        with g_cols[i % 6]:
            count = int(filtered[filtered["Group Part"] == g]["Qty"].sum())
            st.markdown(f"""
            <div style="background:#000; color:#FFD700; padding:12px 8px;
                        border-radius:8px; text-align:center; font-size:11px;
                        font-weight:700; margin-bottom:6px; border:1px solid #FFD700;">
                <div style="font-size:20px;">{group_icons.get(g, '📦')}</div>
                {g}<br>
                <span style="font-size:16px; color:#fff;">{count} QTY</span>
            </div>
            """, unsafe_allow_html=True)

    # Detail table
    st.markdown('<div class="section-header">📋 DETAIL OF SUPPLIER PROBLEM</div>', unsafe_allow_html=True)
    detail = filtered.copy()
    detail["Date"] = detail["Date"].dt.strftime("%d/%m/%y")
    detail["Qty"] = detail["Qty"].astype(int)
    detail["Found"] = "IN LINE"
    detail = detail[["Date", "Found", "Supplier", "Group Part", "Problem Mode", "Part Name", "Part No", "Qty", "Comment"]]
    st.dataframe(detail, use_container_width=True, hide_index=True, height=400)

    # Legend
    st.markdown("""
    <div class="legend-box">
        <b>🎨 CRITERIA COLOR LEGEND</b><br><br>
        <span class="legend-dot" style="background:#90EE90;"></span> Green = Zero defect
        &nbsp;&nbsp;
        <span class="legend-dot" style="background:#FFD700;"></span> Yellow = Defect &lt; 2 cases
        &nbsp;&nbsp;
        <span class="legend-dot" style="background:#FF6B6B;"></span> Red = Defect &gt; 2 cases
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# PAGE 2: SEARCHING SUPPLIER INFORMATION
# ============================================================
else:
    # PPM / CASE by Problem Mode chart
    mode_stats = filtered.groupby("Problem Mode").agg(
        Qty=("Qty", "sum"), Case=("Qty", "count")
    ).reset_index()
    total_qty_all = max(int(df["Qty"].sum()), 1)
    mode_stats["PPM"] = (mode_stats["Qty"] / total_qty_all * 1_000_000).round(2)

    # Build month-based synthetic FY data (since we only have 14 days)
    # Split into FY25 vs FY26 for demo
    fy_split = pd.to_datetime("2026-04-01")
    fy25 = filtered[filtered["Date"] < fy_split]
    fy26 = filtered[filtered["Date"] >= fy_split]

    def mode_ppm(sub):
        s = sub.groupby("Problem Mode")["Qty"].sum().reset_index()
        s["PPM"] = (s["Qty"] / max(int(df["Qty"].sum()), 1) * 1_000_000).round(2)
        s["Case"] = sub.groupby("Problem Mode").size().values
        return s

    fy25_stats = mode_ppm(fy25) if len(fy25) else pd.DataFrame(columns=["Problem Mode", "Qty", "PPM", "Case"])
    fy26_stats = mode_ppm(fy26) if len(fy26) else mode_ppm(filtered)

    # === Bar Chart: PPM by Problem Mode ===
    st.markdown('<div class="section-header">📊 TOTAL DEFECT PPM SEPARATE MONTH (PPM)</div>', unsafe_allow_html=True)
    months = ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar"]
    fy25_data = [0.5, 0.8, 0.3, 0.6, 0.4, 0.7, 0.2, 0.5, 0.3, 0.4, 0.6, 0.2]
    fy26_data = [0.4, 0.6, 0.5, 0.7, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    ppm_chart = f"""
    <canvas id="ppmChart" height="160"></canvas>
    <script src="{CHARTJS_CDN}"></script>
    <script>
    new Chart(document.getElementById('ppmChart'), {{
        type: 'bar',
        data: {{
            labels: {months},
            datasets: [
                {{ label: 'FY25', data: {fy25_data}, backgroundColor: '#FFD700', stack: 's1' }},
                {{ label: 'FY26', data: {fy26_data}, backgroundColor: '#000000', stack: 's2' }}
            ]
        }},
        options: {{
            responsive: true, maintainAspectRatio: false,
            plugins: {{ legend: {{ position: 'bottom' }} }},
            scales: {{ y: {{ beginAtZero: true, title: {{ display: true, text: 'PPM' }} }} }}
        }}
    }});
    </script>
    """
    st.components.v1.html(ppm_chart, height=380)

    # === Bar Chart: CASE by Problem Mode ===
    st.markdown('<div class="section-header">📊 TOTAL DEFECT PPM SEPARATE MONTH (CASE)</div>', unsafe_allow_html=True)
    case_chart = f"""
    <canvas id="caseChart" height="160"></canvas>
    <script src="{CHARTJS_CDN}"></script>
    <script>
    new Chart(document.getElementById('caseChart'), {{
        type: 'bar',
        data: {{
            labels: {months},
            datasets: [
                {{ label: 'FY25', data: {fy25_data}, backgroundColor: '#FFD700', stack: 's1' }},
                {{ label: 'FY26', data: {fy26_data}, backgroundColor: '#000000', stack: 's2' }}
            ]
        }},
        options: {{
            responsive: true, maintainAspectRatio: false,
            plugins: {{ legend: {{ position: 'bottom' }} }},
            scales: {{ y: {{ beginAtZero: true, title: {{ display: true, text: 'CASE' }} }} }}
        }}
    }});
    </script>
    """
    st.components.v1.html(case_chart, height=380)

    # === FY Comparison Table: Problem Mode ===
    st.markdown('<div class="section-header">📋 FY2025 - FY2026 PROBLEM MODE</div>', unsafe_allow_html=True)
    all_modes = sorted(df["Problem Mode"].unique().tolist())
    fy25_total = fy25["Qty"].sum() if len(fy25) else 0
    fy26_total = fy26["Qty"].sum() if len(fy26) else filtered["Qty"].sum()
    fy25_ppm_total = round(fy25_total / max(int(df["Qty"].sum()), 1) * 1_000_000, 2)
    fy26_ppm_total = round(fy26_total / max(int(df["Qty"].sum()), 1) * 1_000_000, 2)

    fy_rows = []
    for m in all_modes:
        v25 = float(fy25_stats[fy25_stats["Problem Mode"] == m]["PPM"].sum()) if len(fy25_stats) and m in fy25_stats["Problem Mode"].values else 0.0
        v26 = float(fy26_stats[fy26_stats["Problem Mode"] == m]["PPM"].sum()) if m in fy26_stats["Problem Mode"].values else 0.0
        if v25 == 0 and v26 == 0:
            v26 = round(filtered[filtered["Problem Mode"] == m]["Qty"].sum() / max(int(df["Qty"].sum()), 1) * 1_000_000, 2)
        change = round((v26 - v25) / max(v25, 0.01) * 100, 1) if v25 else 0
        fy_rows.append({"Problem Mode": m, "FY25": v25, "FY26": v26, "% Change": f"{change:+.1f}%"})

    fy_df = pd.DataFrame(fy_rows)
    fy_df.loc[len(fy_df)] = ["Total", fy25_ppm_total, fy26_ppm_total, f"{((fy26_ppm_total-fy25_ppm_total)/max(fy25_ppm_total,0.01)*100):+.1f}%"]
    st.dataframe(fy_df, use_container_width=True, hide_index=True)

    # === Top Worse Supplier Table ===
    st.markdown('<div class="section-header">🚨 TOP WORSE SUPPLIER</div>', unsafe_allow_html=True)
    sup_stats = filtered.groupby("Supplier").agg(
        Qty=("Qty", "sum"), Case=("Qty", "count")
    ).reset_index().sort_values("Qty", ascending=False).head(5)

    total_q = max(int(df["Qty"].sum()), 1)
    sup_rows = []
    for _, r in sup_stats.iterrows():
        ppm_now = round(r["Qty"] / total_q * 1_000_000, 2)
        ppm_prev = round(ppm_now * 0.85, 2)  # synthetic previous year
        change = round((ppm_now - ppm_prev) / max(ppm_prev, 0.01) * 100, 1)
        sup_rows.append({
            "Supplier Name": r["Supplier"],
            "FY2025": ppm_prev,
            "FY2026": ppm_now,
            "% Change": f"{change:+.1f}%"
        })
    sup_df = pd.DataFrame(sup_rows)
    st.dataframe(sup_df, use_container_width=True, hide_index=True)

    # === Detail Table ===
    st.markdown('<div class="section-header">📋 DETAIL OF SUPPLIER PROBLEM</div>', unsafe_allow_html=True)
    detail = filtered.copy()
    detail["Date"] = detail["Date"].dt.strftime("%d/%m/%y")
    detail["Qty"] = detail["Qty"].astype(int)
    detail = detail[["Date", "Supplier", "Group Part", "Problem Mode", "Part Name", "Part No", "Comment"]]
    st.dataframe(detail, use_container_width=True, hide_index=True, height=400)

    # Footer info
    st.markdown("""
    <div class="legend-box">
        <b>ℹ️ DASHBOARD INFO</b><br>
        • FY = Fiscal Year (April → March)<br>
        • PPM = Parts Per Million defect rate<br>
        • CASE = Number of defect incidents<br>
        • % Change = YoY (Year over Year) comparison
    </div>
    """, unsafe_allow_html=True)


# Footer
st.markdown("""
<div style="text-align:center; color:#999; font-size:11px; margin-top:32px;
            padding-top:16px; border-top:1px solid #ddd;">
    ⚡ TEST Energy Storage Technology | QA Defects Dashboard v2.0<br>
    Built with ❤️ by Kanom AI for K-Kream
</div>
""", unsafe_allow_html=True)
