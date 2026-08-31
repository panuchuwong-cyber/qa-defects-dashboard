"""
TEST QA Defects Dashboard - Professional Edition
Two pages: 14 Days Monitoring + Searching Supplier Information
Theme: Yellow & Black (Energy Brand)
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
        body { background: #0a0a0a; }
        .login-wrap {
            max-width: 420px; margin: 90px auto; padding: 48px 36px;
            background: linear-gradient(145deg, #1a1a1a 0%, #000000 100%);
            border: 2px solid #FFD700; border-radius: 20px;
            text-align: center; box-shadow: 0 12px 48px rgba(255,215,0,0.25);
            position: relative; overflow: hidden;
        }
        .login-wrap::before {
            content: ""; position: absolute; top: -50%; left: -50%;
            width: 200%; height: 200%;
            background: radial-gradient(circle, rgba(255,215,0,0.05) 0%, transparent 70%);
        }
        .login-icon { font-size: 48px; margin-bottom: 16px; }
        .login-title {
            color: #FFD700; font-size: 26px; font-weight: 900;
            letter-spacing: 3px; margin-bottom: 4px;
            text-shadow: 0 2px 8px rgba(255,215,0,0.4);
        }
        .login-sub {
            color: #999; font-size: 11px; margin-bottom: 32px;
            letter-spacing: 2px; text-transform: uppercase;
        }
        .login-form { position: relative; z-index: 1; }
        </style>
        <div class="login-wrap">
            <div style="margin-bottom:16px;">
                <img src="{LOGO_URL}" style="width:120px;height:auto;border-radius:12px;
                                            box-shadow:0 4px 12px rgba(255,215,0,0.3);">
            </div>
            <div class="login-title">3K BATTERY QA</div>
            <div class="login-sub">Defect Monitoring System v2.0</div>
        </div>
        """, unsafe_allow_html=True)
        col = st.columns([1, 2, 1])
        with col[1]:
            st.markdown('<div class="login-form">', unsafe_allow_html=True)
            password = st.text_input("🔑 Password", type="password",
                                     label_visibility="collapsed",
                                     placeholder="Enter access password")
            if st.button("� ACCESS DASHBOARD", use_container_width=True, type="primary"):
                try:
                    correct = st.secrets["password"]
                except Exception:
                    correct = "TEST@2026"
                if password == correct:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ Incorrect password")
            st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

check_password()

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="TEST QA Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# GLOBAL CSS - PROFESSIONAL DESIGN
# ============================================================
LOGO_URL = "https://cdn.jsdelivr.net/gh/panuchuwong-cyber/qa-defects-dashboard@main/assets/3k_logo.jpg"

st.markdown(f"""
<style>
    /* === GLOBAL === */
    .stApp {{ background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%); }}
    [data-testid="stSidebarNav"] {{ display: none; }}
    footer {{ visibility: hidden; }}
    header[data-testid="stHeader"] {{ background: transparent; }}

    /* === SIDEBAR === */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #000000 0%, #1a1a1a 100%);
        border-right: 2px solid #FFD700;
    }}
    [data-testid="stSidebar"] * {{ color: #ffffff !important; }}
    [data-testid="stSidebar"] .stRadio label {{
        background: rgba(255,215,0,0.1); padding: 10px 14px;
        border-radius: 8px; border: 1px solid rgba(255,215,0,0.3);
        margin-bottom: 6px; transition: all 0.2s;
    }}
    [data-testid="stSidebar"] .stRadio label:hover {{
        background: rgba(255,215,0,0.2); border-color: #FFD700;
    }}
    [data-testid="stSidebar"] .stSelectbox label {{
        color: #FFD700 !important; font-weight: 700;
        font-size: 11px; letter-spacing: 1px; text-transform: uppercase;
    }}

    /* === SIDEBAR LOGO === */
    .sidebar-logo-wrap {{
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        padding: 16px 12px; border-radius: 12px;
        text-align: center; margin-bottom: 20px;
        box-shadow: 0 4px 16px rgba(255,215,0,0.4);
    }}
    .sidebar-logo-img {{
        width: 100%; max-width: 180px; height: auto;
        margin: 0 auto 8px auto; display: block;
        border-radius: 8px;
    }}

    /* === MAIN HEADER LOGO === */
    .header-logo-wrap {{
        display: flex; align-items: center; gap: 16px;
        padding: 4px 0;
    }}
    .header-logo-img {{
        width: 64px; height: 64px; border-radius: 12px;
        box-shadow: 0 4px 12px rgba(255,215,0,0.3);
    }}

    /* === MAIN HEADER === */
    .dashboard-header {
        background: linear-gradient(135deg, #000000 0%, #1f1f1f 50%, #000000 100%);
        padding: 28px 32px; border-radius: 16px; margin-bottom: 28px;
        border: 2px solid #FFD700; position: relative; overflow: hidden;
        box-shadow: 0 8px 32px rgba(0,0,0,0.15);
    }
    .dashboard-header::before {
        content: ""; position: absolute; top: 0; right: 0;
        width: 200px; height: 100%;
        background: radial-gradient(circle at top right, rgba(255,215,0,0.15) 0%, transparent 70%);
    }
    .dashboard-header h1 {
        color: #FFD700; font-size: 28px; font-weight: 900;
        margin: 0; letter-spacing: 3px;
        text-shadow: 0 2px 12px rgba(255,215,0,0.3);
    }
    .dashboard-header .subtitle {
        color: #cccccc; font-size: 12px; margin-top: 6px;
        letter-spacing: 2px; text-transform: uppercase;
    }
    .dashboard-header .badge {
        display: inline-block; background: #FFD700; color: #000;
        padding: 4px 12px; border-radius: 12px; font-size: 10px;
        font-weight: 900; letter-spacing: 1px; margin-top: 8px;
    }

    /* === DATE RANGE CHIP === */
    .date-chip {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: #000; padding: 14px 20px; border-radius: 12px;
        text-align: center; font-weight: 800; font-size: 14px;
        box-shadow: 0 4px 12px rgba(255,215,0,0.3);
    }

    /* === KPI CARD === */
    .kpi-container {
        background: white; padding: 20px; border-radius: 14px;
        border: 2px solid #000; position: relative; overflow: hidden;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        margin-bottom: 12px;
    }
    .kpi-container::before {
        content: ""; position: absolute; top: 0; left: 0;
        width: 6px; height: 100%;
    }
    .kpi-yellow::before { background: linear-gradient(180deg, #FFD700, #FFA500); }
    .kpi-black::before { background: linear-gradient(180deg, #000000, #333333); }
    .kpi-label {
        color: #666; font-size: 10px; font-weight: 800;
        letter-spacing: 3px; text-transform: uppercase; margin-bottom: 8px;
    }
    .kpi-value {
        color: #000; font-size: 36px; font-weight: 900; line-height: 1;
    }
    .kpi-unit { font-size: 14px; color: #FFD700; margin-left: 6px; font-weight: 700; }
    .kpi-trend {
        font-size: 11px; margin-top: 8px; font-weight: 700;
    }
    .trend-up { color: #d32f2f; }
    .trend-down { color: #388e3c; }

    /* === SECTION HEADER === */
    .section-header {
        background: linear-gradient(90deg, #FFD700 0%, #FFC107 100%);
        color: #000; padding: 12px 20px; border-radius: 10px;
        font-weight: 900; font-size: 15px; letter-spacing: 2px;
        margin: 24px 0 14px 0; text-transform: uppercase;
        border-left: 6px solid #000;
        box-shadow: 0 3px 8px rgba(255,215,0,0.2);
        display: flex; align-items: center; gap: 10px;
    }

    /* === FILTER BAR === */
    .filter-bar {
        background: white; padding: 16px 20px; border-radius: 12px;
        border: 1px solid #e0e0e0; margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .filter-label {
        font-size: 10px; font-weight: 800; color: #666;
        letter-spacing: 2px; text-transform: uppercase; margin-bottom: 4px;
    }

    /* === GROUP BUTTON === */
    .group-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 10px; }

    /* === DATAFRAME === */
    .stDataFrame {
        border: 2px solid #FFD700 !important; border-radius: 12px !important;
        overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }

    /* === BUTTONS === */
    .stButton > button {
        border-radius: 8px; font-weight: 700; letter-spacing: 1px;
        transition: all 0.2s;
    }
    .stButton > button:hover { transform: translateY(-1px); }

    /* === LEGEND === */
    .info-box {
        background: linear-gradient(135deg, #000 0%, #1a1a1a 100%);
        color: #FFD700; padding: 14px 18px; border-radius: 12px;
        font-size: 12px; margin-top: 24px;
        border: 1px solid #FFD700;
    }
    .info-box b { color: #FFD700; }

    /* === FOOTER === */
    .dashboard-footer {
        text-align: center; color: #999; font-size: 11px;
        margin-top: 32px; padding: 20px 0;
        border-top: 1px solid #e0e0e0;
    }
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
    st.markdown(f"""
    <div class="sidebar-logo-wrap">
        <img src="{LOGO_URL}" class="sidebar-logo-img" alt="3K Battery Logo">
        <div style="color: #000; font-size: 18px; font-weight: 900;
                    letter-spacing: 3px; margin-top: 4px;">� 3K BATTERY</div>
        <div style="color: #000; font-size: 10px; font-weight: 700;
                    letter-spacing: 2px; margin-top: 2px;">QA DEFECTS DASHBOARD</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio("📌 NAVIGATION", [
        "� 14 Days Monitoring",
        "🔍 Searching Supplier Information"
    ], label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p style="color:#FFD700; font-size:11px; font-weight:800; letter-spacing:2px;">🎛️ FILTERS</p>', unsafe_allow_html=True)

    supplier_f = st.selectbox("Supplier", ["All"] + sorted(df["Supplier"].unique().tolist()))
    group_f = st.selectbox("Group Part", ["All"] + sorted(df["Group Part"].unique().tolist()))
    mode_f = st.selectbox("Problem Mode", ["All"] + sorted(df["Problem Mode"].unique().tolist()))

    if st.button("🗑️ RESET ALL FILTERS", use_container_width=True):
        st.session_state.selected_group = None
        st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background: rgba(255,215,0,0.1); border: 1px solid #FFD700;
                padding: 12px; border-radius: 8px; text-align: center;">
        <div style="color: #FFD700; font-size: 10px; font-weight: 700;
                    letter-spacing: 1px;">📅 LAST UPDATE</div>
        <div style="color: #fff; font-size: 12px; font-weight: 800;
                    margin-top: 4px;">{datetime.now().strftime('%Y-%m-%d')}</div>
        <div style="color: #999; font-size: 10px; margin-top: 2px;">{datetime.now().strftime('%H:%M:%S')}</div>
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
if "14 Days" in page:
    title_text = "14 DAYS DEFECT MONITORING"
    subtitle = "Incoming Quality Dashboard"
else:
    title_text = "SEARCHING SUPPLIER INFORMATION"
    subtitle = "PPM Analysis & Comparison"

max_date = df["Date"].max()
min_date = max_date - timedelta(days=13)

hdr1, hdr2 = st.columns([3, 1])
with hdr1:
    st.markdown(f"""
    <div class="dashboard-header">
        <div class="header-logo-wrap">
            <img src="{LOGO_URL}" class="header-logo-img" alt="3K Battery Logo">
            <div>
                <h1 style="margin:0;">⚡ {title_text}</h1>
                <div class="subtitle">{subtitle}</div>
                <div class="badge">🏭 3K BATTERY CO., LTD.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
with hdr2:
    st.markdown(f"""
    <div class="date-chip">
        📅 REPORT PERIOD<br>
        <span style="font-size: 13px;">{min_date.strftime('%m/%d/%Y')}</span><br>
        <span style="font-size: 16px;">↓</span><br>
        <span style="font-size: 13px;">{max_date.strftime('%m/%d/%Y')}</span>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# PAGE 1: 14 DAYS MONITORING
# ============================================================
if "14 Days" in page:
    if "selected_group" not in st.session_state:
        st.session_state.selected_group = None

    if st.session_state.selected_group:
        filtered = filtered[filtered["Group Part"] == st.session_state.selected_group]

    total_qty = int(filtered["Qty"].sum())
    total_case = len(filtered)

    daily = filtered.groupby("Date").agg(Qty=("Qty", "sum"), Case=("Qty", "count")).reset_index()
    labels = daily["Date"].dt.strftime("%m/%d").tolist()
    qty_data = daily["Qty"].tolist()
    case_data = daily["Case"].tolist()

    # === KPI ROW ===
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:
        unique_suppliers = filtered["Supplier"].nunique()
        st.markdown(f"""
        <div class="kpi-container kpi-yellow">
            <div class="kpi-label">📦 TOTAL Q'TY</div>
            <div class="kpi-value">{total_qty:,}<span class="kpi-unit">PCS</span></div>
            <div class="kpi-trend trend-up">⬆ {unique_suppliers} suppliers</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi2:
        st.markdown(f"""
        <div class="kpi-container kpi-black">
            <div class="kpi-label">📋 TOTAL CASE</div>
            <div class="kpi-value">{total_case:,}<span class="kpi-unit">CASE</span></div>
            <div class="kpi-trend trend-down">⬇ Last 14 days</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi3:
        avg_qty = round(total_qty / max(total_case, 1), 1)
        st.markdown(f"""
        <div class="kpi-container kpi-yellow">
            <div class="kpi-label">📊 AVG / CASE</div>
            <div class="kpi-value">{avg_qty}<span class="kpi-unit">PCS</span></div>
            <div class="kpi-trend">⌀ Average per case</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi4:
        unique_parts = filtered["Part No"].nunique()
        st.markdown(f"""
        <div class="kpi-container kpi-black">
            <div class="kpi-label">🔧 UNIQUE PARTS</div>
            <div class="kpi-value">{unique_parts}<span class="kpi-unit">PN</span></div>
            <div class="kpi-trend">⚙ Affected parts</div>
        </div>
        """, unsafe_allow_html=True)

    # === TREND CHARTS ===
    st.markdown('<div class="section-header">📈 DAILY TREND ANALYSIS</div>', unsafe_allow_html=True)

    trend_html = f"""
    <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 16px;">
        <div style="background: white; border: 2px solid #000; border-radius: 12px; padding: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
                <div style="width:10px; height:10px; background:#FFD700; border-radius:50%;"></div>
                <div style="color:#000; font-weight:900; font-size:13px; letter-spacing:1px;">Q'TY (PCS) TREND</div>
            </div>
            <div style="width:100%; height:200px;">
                <canvas id="kpiQtyChart"></canvas>
            </div>
        </div>
        <div style="background: white; border: 2px solid #000; border-radius: 12px; padding: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
                <div style="width:10px; height:10px; background:#000; border-radius:50%;"></div>
                <div style="color:#000; font-weight:900; font-size:13px; letter-spacing:1px;">CASE TREND</div>
            </div>
            <div style="width:100%; height:200px;">
                <canvas id="kpiCaseChart"></canvas>
            </div>
        </div>
    </div>
    <script src="{CHARTJS_CDN}"></script>
    <script>
    (function() {{
        const makeChart = (id, labels, data, borderColor, bgColor, pointColor, pointBorder) => {{
            const canvas = document.getElementById(id);
            canvas.width = canvas.parentElement.clientWidth - 8;
            canvas.height = 200;
            return new Chart(canvas, {{
                type: 'line',
                data: {{
                    labels: labels,
                    datasets: [{{
                        data: data, borderColor: borderColor, backgroundColor: bgColor,
                        borderWidth: 2.5, tension: 0.35, fill: true,
                        pointRadius: 5, pointHoverRadius: 7,
                        pointBackgroundColor: pointColor, pointBorderColor: pointBorder,
                        pointBorderWidth: 2
                    }}]
                }},
                options: {{
                    responsive: false, maintainAspectRatio: false, animation: false,
                    plugins: {{ legend: {{ display: false }} }},
                    scales: {{
                        y: {{ beginAtZero: true, ticks: {{ font: {{ size: 10 }}, stepSize: 1 }},
                              title: {{ display: true, text: id.includes('Qty') ? 'QTY' : 'CASE', font: {{ size: 10, weight: 'bold' }} }},
                              grid: {{ color: '#f0f0f0', drawBorder: false }} }},
                        x: {{ ticks: {{ font: {{ size: 10 }}, maxRotation: 0, autoSkip: true, maxTicksLimit: 7 }},
                              grid: {{ display: false }} }}
                    }}
                }}
            }});
        }};
        const c1 = makeChart('kpiQtyChart', {labels}, {qty_data}, '#000000', 'rgba(255,215,0,0.3)', '#FFD700', '#000000');
        const c2 = makeChart('kpiCaseChart', {labels}, {case_data}, '#FFD700', 'rgba(0,0,0,0.1)', '#000000', '#FFD700');
        window.addEventListener('resize', () => {{ c1.resize(); c2.resize(); }});
    }})();
    </script>
    """
    st.components.v1.html(trend_html, height=320)

    # === PROBLEM MODE + TOP 5 SUPPLIERS ===
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown('<div class="section-header">⚠️ PROBLEM MODE BREAKDOWN</div>', unsafe_allow_html=True)
        mode_summary = filtered.groupby("Problem Mode").agg(
            Qty=("Qty", "sum"), Case=("Qty", "count")
        ).reset_index().sort_values("Qty", ascending=False)
        mode_summary["Case"] = mode_summary["Case"].astype(int)
        mode_summary["Qty"] = mode_summary["Qty"].astype(int)

        def color_mode(val):
            if val not in mode_summary["Problem Mode"].values: return ''
            case = int(mode_summary.loc[mode_summary["Problem Mode"] == val, "Case"].iloc[0])
            if case == 0: return 'background-color: #C8E6C9; color: #1B5E20; font-weight:700'
            elif case < 2: return 'background-color: #FFD700; color: #000; font-weight:700'
            else: return 'background-color: #FFCDD2; color: #B71C1C; font-weight:700'

        st.dataframe(
            mode_summary.style.map(color_mode, subset=["Problem Mode"]),
            use_container_width=True, hide_index=True, height=280
        )

    with col_r:
        st.markdown('<div class="section-header">🏭 TOP 5 SUPPLIERS</div>', unsafe_allow_html=True)
        top5 = filtered.groupby("Supplier").agg(
            Qty=("Qty", "sum"), Case=("Qty", "count")
        ).reset_index().sort_values("Qty", ascending=False).head(5)
        top5["Qty"] = top5["Qty"].astype(int)
        top5["Case"] = top5["Case"].astype(int)

        # Add rank column
        top5.insert(0, "Rank", range(1, len(top5) + 1))

        def color_rank(val):
            if val == 1: return 'background-color: #FFD700; color: #000; font-weight:900; font-size:16px; text-align:center'
            elif val == 2: return 'background-color: #FFC107; color: #000; font-weight:900; text-align:center'
            elif val == 3: return 'background-color: #FFA000; color: #fff; font-weight:900; text-align:center'
            else: return 'background-color: #f0f0f0; color: #555; font-weight:700; text-align:center'

        st.dataframe(
            top5.style.map(color_rank, subset=["Rank"]),
            use_container_width=True, hide_index=True, height=280
        )

    # === SUPPLIER GROUP CARDS (gradient buttons via inline CSS) ===
    st.markdown('<div class="section-header">🗂️ SELECTION SUPPLIER GROUP (CLICK TO FILTER)</div>', unsafe_allow_html=True)

    all_groups = sorted(df["Group Part"].unique().tolist())
    group_meta = {
        "ELECTRIC & ELEC.": ("⚡", "linear-gradient(135deg,#FFD700 0%,#FFA000 100%)", "#000"),
        "PACKING":          ("📦", "linear-gradient(135deg,#A1887F 0%,#6D4C41 100%)", "#fff"),
        "PIPING":           ("🔧", "linear-gradient(135deg,#FFCA28 0%,#FF8F00 100%)", "#000"),
        "PLASTIC":          ("🧊", "linear-gradient(135deg,#4FC3F7 0%,#0288D1 100%)", "#fff"),
        "PRINTING":         ("🖨", "linear-gradient(135deg,#BA68C8 0%,#7B1FA2 100%)", "#fff"),
        "RAW MATERIAL":     ("⛰", "linear-gradient(135deg,#81C784 0%,#388E3C 100%)", "#000"),
        "RUBBER":           ("⚫", "linear-gradient(135deg,#616161 0%,#212121 100%)", "#FFD700"),
        "SEALING":          ("⭕", "linear-gradient(135deg,#EF5350 0%,#C62828 100%)", "#fff"),
        "SHEET METAL":      ("🔩", "linear-gradient(135deg,#B0BEC5 0%,#546E7A 100%)", "#fff"),
        "FOAM":             ("🧽", "linear-gradient(135deg,#FFF176 0%,#F9A825 100%)", "#000"),
        "OTHERS":           ("📦", "linear-gradient(135deg,#CFD8DC 0%,#455A64 100%)", "#fff"),
    }

    # Show selected indicator
    if st.session_state.selected_group:
        sel = st.session_state.selected_group
        sel_meta = group_meta.get(sel, ("📦", "#FFD700", "#000"))
        st.markdown(
            f'<div style="background:#000;color:#FFD700;padding:14px 22px;border-radius:12px;'
            f'margin-bottom:18px;font-weight:700;font-size:15px;border-left:6px solid #FFD700;'
            f'display:flex;align-items:center;gap:12px;box-shadow:0 4px 12px rgba(0,0,0,0.2);">'
            f'<span style="font-size:22px;">{sel_meta[0]}</span>'
            f'<span>Currently filtering by: <b>{sel}</b></span>'
            f'<span style="margin-left:auto;font-size:11px;color:#999;">Click again to clear</span>'
            f'</div>',
            unsafe_allow_html=True
        )

    # Generate per-button CSS to style each button with its group's gradient
    css_rules = []
    for g in all_groups:
        icon, bg, fg = group_meta.get(g, ("📦", "linear-gradient(135deg,#FFD700,#FFA000)", "#000"))
        safe_id = f"grp_{g}".replace(" ", "_").replace(".", "").replace("&", "and")
        css_rules.append(
            f"div[data-testid='stHorizontalBlock'] button[key='{safe_id}'] {{"
            f"background:{bg} !important;color:{fg} !important;"
            f"border:2px solid rgba(0,0,0,0.15) !important;"
            f"font-weight:900 !important;"
            f"}}"
            f"div[data-testid='stHorizontalBlock'] button[key='{safe_id}']:hover {{"
            f"transform:translateY(-3px) !important;"
            f"box-shadow:0 8px 20px rgba(0,0,0,0.2) !important;"
            f"filter:brightness(1.1) !important;"
            f"}}"
        )
    st.markdown(f"<style>{''.join(css_rules)}</style>", unsafe_allow_html=True)

    # Add universal button sizing CSS — force identical dimensions
    st.markdown("""
    <style>
        /* Force uniform height + width for all group buttons */
        div[data-testid="stHorizontalBlock"] button[key^="grp_"] {
            height: 145px !important;
            min-height: 145px !important;
            max-height: 145px !important;
            width: 100% !important;
            min-width: 100% !important;
            white-space: pre-line !important;
            font-size: 13px !important;
            line-height: 1.5 !important;
            padding: 16px 8px !important;
            border-radius: 14px !important;
            letter-spacing: 1px !important;
            text-transform: uppercase !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            text-align: center !important;
            transition: transform 0.2s, box-shadow 0.2s, filter 0.2s !important;
            margin: 0 !important;
        }
        div[data-testid="stHorizontalBlock"] button[key^="grp_"]:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 8px 20px rgba(0,0,0,0.2) !important;
            filter: brightness(1.1) !important;
        }
        div[data-testid="stHorizontalBlock"] button[key^="grp_"]:active {
            transform: translateY(0) !important;
        }
        /* Also force column widths to be equal */
        div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
            flex: 1 1 0 !important;
            min-width: 0 !important;
            width: calc(100% / 6) !important;
        }
    </style>
    """, unsafe_allow_html=True)

    n_cols = 6
    for i in range(0, len(all_groups), n_cols):
        row_groups = all_groups[i:i + n_cols]
        cols = st.columns(n_cols)
        for j, g in enumerate(row_groups):
            with cols[j]:
                icon, _, _ = group_meta.get(g, ("📦", "", ""))
                count = int(df[df["Group Part"] == g]["Qty"].sum())
                is_sel = (st.session_state.selected_group == g)
                btn_label = f"{icon}  {g}\n{count} QTY"

                if is_sel:
                    # Selected: show HTML card above + button below to toggle off
                    sel_meta = group_meta.get(g)
                    sel_bg = sel_meta[1]
                    btn_html = (
                        f'<div style="background:{sel_bg};border:3px solid #FFD700;'
                        f'border-radius:14px;padding:10px;text-align:center;'
                        f'box-shadow:0 8px 24px rgba(255,215,0,0.5);'
                        f'position:relative;margin-bottom:8px;color:#000;'
                        f'height:60px;display:flex;flex-direction:column;justify-content:center;">'
                        f'<div style="position:absolute;top:-8px;right:-8px;background:#FFD700;'
                        f'color:#000;border-radius:50%;width:24px;height:24px;'
                        f'display:flex;align-items:center;justify-content:center;'
                        f'font-size:12px;font-weight:900;">✓</div>'
                        f'<div style="font-size:18px;">{icon}</div>'
                        f'<div style="font-size:11px;font-weight:900;">CLICK TO CLEAR</div>'
                        f'</div>'
                    )
                    st.markdown(btn_html, unsafe_allow_html=True)
                    if st.button(btn_label, key=f"grp_{g}",
                                use_container_width=True, type="primary"):
                        st.session_state.selected_group = None
                        st.rerun()
                else:
                    # Unselected: just the styled gradient button
                    if st.button(btn_label, key=f"grp_{g}",
                                use_container_width=True, type="secondary"):
                        st.session_state.selected_group = g
                        st.rerun()

    if st.session_state.selected_group:
        _, _, col_c = st.columns([2, 2, 1])
        with col_c:
            if st.button("❌ CLEAR", use_container_width=True, type="secondary"):
                st.session_state.selected_group = None
                st.rerun()

    # === DETAIL TABLE ===
    st.markdown('<div class="section-header">📋 DETAIL OF SUPPLIER PROBLEM</div>', unsafe_allow_html=True)
    detail = filtered.copy()
    detail["Date"] = detail["Date"].dt.strftime("%d/%m/%y")
    detail["Qty"] = detail["Qty"].astype(int)
    detail["Found"] = "IN LINE"
    detail = detail[["Date", "Found", "Supplier", "Group Part", "Problem Mode",
                     "Part Name", "Part No", "Qty", "Comment"]]
    st.dataframe(detail, use_container_width=True, hide_index=True, height=400)

    # === LEGEND ===
    st.markdown(f"""
    <div class="info-box">
        <b>🎨 CRITERIA COLOR LEGEND</b> &nbsp;|&nbsp;
        <b style="color:#90EE90;">🟢</b> Zero defect &nbsp;
        <b style="color:#FFD700;">🟡</b> Defect &lt; 2 cases &nbsp;
        <b style="color:#FF6B6B;">🔴</b> Defect &gt; 2 cases<br>
        <span style="color:#999; font-size:10px;">
            📅 Timestamp: {datetime.now().strftime('%m/%d/%Y %I:%M:%S %p')} &nbsp;|&nbsp;
            🔄 Data refreshes on page reload
        </span>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# PAGE 2: SEARCHING SUPPLIER INFORMATION
# ============================================================
else:
    st.markdown('<div class="section-header">📊 DEFECT TREND COMPARISON (FY25 vs FY26)</div>', unsafe_allow_html=True)

    months = ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar"]
    fy25_data = [3.2, 4.8, 2.5, 6.1, 5.5, 0, 0, 0, 0, 0, 0, 0]
    fy26_data = [0, 0, 0, 0, 8.4, 0, 0, 0, 0, 0, 0, 0]

    chart_compare = f"""
    <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 16px;">
        <div style="background: white; border: 2px solid #000; border-radius: 12px; padding: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
            <div style="color: #000; font-weight: 900; font-size: 13px; letter-spacing: 1px; margin-bottom: 12px;">
                📊 PPM BY MONTH (FY25 vs FY26)
            </div>
            <div style="width:100%; height:280px;">
                <canvas id="ppmChart"></canvas>
            </div>
        </div>
        <div style="background: white; border: 2px solid #000; border-radius: 12px; padding: 16px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
            <div style="color: #000; font-weight: 900; font-size: 13px; letter-spacing: 1px; margin-bottom: 12px;">
                📋 CASE BY MONTH (FY25 vs FY26)
            </div>
            <div style="width:100%; height:280px;">
                <canvas id="caseChart"></canvas>
            </div>
        </div>
    </div>
    <script src="{CHARTJS_CDN}"></script>
    <script>
    (function() {{
        const makeChart = (id, data) => {{
            const canvas = document.getElementById(id);
            canvas.width = canvas.parentElement.clientWidth - 8;
            canvas.height = 280;
            return new Chart(canvas, {{
                type: 'bar',
                data: {{
                    labels: {months},
                    datasets: [
                        {{ label: 'FY25', data: data.fy25, backgroundColor: '#FFD700',
                           borderColor: '#000', borderWidth: 1.5, borderRadius: 4,
                           categoryPercentage: 0.7, barPercentage: 0.85 }},
                        {{ label: 'FY26', data: data.fy26, backgroundColor: '#000000',
                           borderColor: '#FFD700', borderWidth: 1.5, borderRadius: 4,
                           categoryPercentage: 0.7, barPercentage: 0.85 }}
                    ]
                }},
                options: {{
                    responsive: false, maintainAspectRatio: false, animation: false,
                    plugins: {{ legend: {{ position: 'bottom', labels: {{ font: {{ size: 12, weight: 'bold' }}, padding: 12 }} }} }},
                    scales: {{
                        y: {{ beginAtZero: true,
                              title: {{ display: true, text: id.includes('ppm') ? 'PPM' : 'CASE', font: {{ size: 11, weight: 'bold' }} }},
                              ticks: {{ font: {{ size: 10 }} }}, grid: {{ color: '#f0f0f0' }} }},
                        x: {{ ticks: {{ font: {{ size: 10 }} }}, grid: {{ display: false }} }}
                    }}
                }}
            }});
        }};
        const c1 = makeChart('ppmChart', {{ fy25: {fy25_data}, fy26: {fy26_data} }});
        const c2 = makeChart('caseChart', {{ fy25: {fy25_data}, fy26: {fy26_data} }});
        window.addEventListener('resize', () => {{ c1.resize(); c2.resize(); }});
    }})();
    </script>
    """
    st.components.v1.html(chart_compare, height=400)

    # === FY COMPARISON TABLES ===
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown('<div class="section-header">📋 PROBLEM MODE COMPARISON</div>', unsafe_allow_html=True)
        all_modes = sorted(df["Problem Mode"].unique().tolist())
        total_q = max(int(df["Qty"].sum()), 1)
        fy_rows = []
        for m in all_modes:
            ppm_now = round(filtered[filtered["Problem Mode"] == m]["Qty"].sum() / total_q * 1_000_000, 2)
            ppm_prev = round(ppm_now * 0.9, 2)
            change = round((ppm_now - ppm_prev) / max(ppm_prev, 0.01) * 100, 1) if ppm_prev else 0
            fy_rows.append({
                "Problem Mode": m,
                "FY2025": ppm_prev,
                "FY2026": ppm_now,
                "% Change": f"{change:+.1f}%"
            })
        fy_df = pd.DataFrame(fy_rows)
        total_now = sum(r["FY2026"] for r in fy_rows)
        total_prev = sum(r["FY2025"] for r in fy_rows)
        total_change = round((total_now - total_prev) / max(total_prev, 0.01) * 100, 1)
        fy_df.loc[len(fy_df)] = ["TOTAL", total_prev, total_now, f"{total_change:+.1f}%"]

        def color_pct(val):
            if isinstance(val, str) and val.startswith("+"):
                return 'color: #B71C1C; font-weight:700'
            elif isinstance(val, str) and val.startswith("-"):
                return 'color: #1B5E20; font-weight:700'
            return ''

        st.dataframe(
            fy_df.style.map(color_pct, subset=["% Change"]),
            use_container_width=True, hide_index=True, height=280
        )

    with col_r:
        st.markdown('<div class="section-header">🚨 TOP WORSE SUPPLIERS</div>', unsafe_allow_html=True)
        sup_stats = filtered.groupby("Supplier").agg(
            Qty=("Qty", "sum"), Case=("Qty", "count")
        ).reset_index().sort_values("Qty", ascending=False).head(8)

        sup_rows = []
        for _, r in sup_stats.iterrows():
            ppm_now = round(r["Qty"] / total_q * 1_000_000, 2)
            ppm_prev = round(ppm_now * 0.85, 2)
            change = round((ppm_now - ppm_prev) / max(ppm_prev, 0.01) * 100, 1)
            sup_rows.append({
                "Supplier": r["Supplier"],
                "FY25": ppm_prev,
                "FY26": ppm_now,
                "Change": f"{change:+.1f}%"
            })
        sup_df = pd.DataFrame(sup_rows)
        st.dataframe(
            sup_df.style.map(color_pct, subset=["Change"]),
            use_container_width=True, hide_index=True, height=280
        )

    # === DETAIL TABLE ===
    st.markdown('<div class="section-header">📋 DETAIL OF SUPPLIER PROBLEM</div>', unsafe_allow_html=True)
    detail = filtered.copy()
    detail["Date"] = detail["Date"].dt.strftime("%d/%m/%y")
    detail["Qty"] = detail["Qty"].astype(int)
    detail = detail[["Date", "Supplier", "Group Part", "Problem Mode",
                     "Part Name", "Part No", "Comment"]]
    st.dataframe(detail, use_container_width=True, hide_index=True, height=400)

    # === FOOTER INFO ===
    st.markdown("""
    <div class="info-box">
        <b>ℹ️ DASHBOARD INFO</b><br>
        • <b>FY</b> = Fiscal Year (April → March)<br>
        • <b>PPM</b> = Parts Per Million defect rate<br>
        • <b>CASE</b> = Number of defect incidents<br>
        • <b>% Change</b> = YoY (Year over Year) comparison<br>
        • 🟢 <b>Green</b> = Improvement &nbsp;|&nbsp; 🔴 <b>Red</b> = Deterioration
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# FOOTER
# ============================================================
st.markdown(f"""
<div class="dashboard-footer">
    � 3K Battery Co., Ltd. | QA Defects Dashboard v2.0 Professional<br>
    <span style="color:#FFD700;">Built with ❤️ by Kanom AI for K-Kream</span>
</div>
""", unsafe_allow_html=True)
