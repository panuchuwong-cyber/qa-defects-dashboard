"""
TEST QA Defects Dashboard - Professional Edition
Two pages: 14 Days Monitoring + Searching Supplier Information
Theme: Yellow & Black (Energy Brand)
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import io
from datetime import datetime, timedelta

CHARTJS_CDN = "https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"
LOGO_URL = "https://cdn.jsdelivr.net/gh/panuchuwong-cyber/qa-defects-dashboard@main/assets/3k_logo.jpg"

# ============================================================
# PASSWORD GATE
# ============================================================
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if not st.session_state.authenticated:
        logo_html = """
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

        /* === PASSWORD INPUT === */
        .login-form input[type="password"],
        .login-form input[type="text"] {
            background: #0a0a0a !important;
            border: 2px solid #FFD700 !important;
            border-radius: 10px !important;
            color: #FFD700 !important;
            font-size: 15px !important;
            font-weight: 600 !important;
            letter-spacing: 2px !important;
            padding: 12px 16px !important;
            text-align: center !important;
            transition: all 0.3s ease !important;
        }
        .login-form input[type="password"]:focus,
        .login-form input[type="text"]:focus {
            border-color: #FFC107 !important;
            box-shadow: 0 0 0 3px rgba(255,215,0,0.25) !important;
            outline: none !important;
        }
        .login-form input::placeholder {
            color: #666 !important;
            letter-spacing: 1px !important;
        }

        /* === ACCESS BUTTON — YELLOW & BLACK THEME === */
        div[data-testid="stButton"] button[kind="primary"] {
            background: linear-gradient(135deg, #FFD700 0%, #FFC107 50%, #FFD700 100%) !important;
            background-size: 200% 100% !important;
            color: #000000 !important;
            font-weight: 900 !important;
            font-size: 15px !important;
            letter-spacing: 2px !important;
            text-transform: uppercase !important;
            border: 2px solid #000000 !important;
            border-radius: 10px !important;
            padding: 14px 24px !important;
            margin-top: 14px !important;
            box-shadow: 0 6px 20px rgba(255,215,0,0.35),
                        inset 0 1px 0 rgba(255,255,255,0.3) !important;
            animation: btnShimmer 3s linear infinite !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            position: relative !important;
            overflow: hidden !important;
        }
        div[data-testid="stButton"] button[kind="primary"]:hover {
            background: #000000 !important;
            color: #FFD700 !important;
            border-color: #FFD700 !important;
            box-shadow: 0 8px 28px rgba(255,215,0,0.55),
                        inset 0 0 0 2px rgba(255,215,0,0.2) !important;
            transform: translateY(-2px) !important;
        }
        div[data-testid="stButton"] button[kind="primary"]:active {
            transform: translateY(0) !important;
            box-shadow: 0 4px 12px rgba(255,215,0,0.4) !important;
        }
        @keyframes btnShimmer {
            0%   { background-position: 0% 50%; }
            100% { background-position: 200% 50%; }
        }
        </style>
        <div class="login-wrap">
            <div style="margin-bottom:20px;">
                <img src="__LOGO_URL__" width="140"
                     style="border-radius:14px;box-shadow:0 6px 20px rgba(255,215,0,0.4);">
            </div>
            <div class="login-title">3K BATTERY QA</div>
            <div class="login-sub">Defect Monitoring System v2.0</div>
        </div>
        """.replace("__LOGO_URL__", LOGO_URL)
        st.markdown(logo_html, unsafe_allow_html=True)
        col = st.columns([1, 2, 1])
        with col[1]:
            st.markdown('<div class="login-form">', unsafe_allow_html=True)
            password = st.text_input("🔑 Password", type="password",
                                     label_visibility="collapsed",
                                     placeholder="Enter access password")
            if st.button("⚡ ACCESS DASHBOARD", use_container_width=True, type="primary"):
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

st.markdown("""
<style>
    /* === GLOBAL === */
    .stApp { background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%); }
    [data-testid="stSidebarNav"] { display: none; }
    footer { visibility: hidden; }
    header[data-testid="stHeader"] { background: transparent; }

    /* === SIDEBAR === */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0a0a 0%, #1a1a1a 50%, #0a0a0a 100%);
        border-right: 2px solid #FFD700;
        box-shadow: 4px 0 20px rgba(0,0,0,0.3);
    }
    [data-testid="stSidebar"] * { color: #ffffff !important; }
    [data-testid="stSidebar"] .stRadio label {
        background: rgba(255,215,0,0.08); padding: 12px 16px;
        border-radius: 10px; border: 1px solid rgba(255,215,0,0.25);
        margin-bottom: 8px; transition: all 0.3s; font-weight: 700;
        letter-spacing: 1px;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(255,215,0,0.2); border-color: #FFD700;
        transform: translateX(4px);
    }
    [data-testid="stSidebar"] .stSelectbox label {
        color: #FFD700 !important; font-weight: 800;
        font-size: 11px; letter-spacing: 2px; text-transform: uppercase;
        margin-bottom: 6px;
    }
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,215,0,0.3) !important;
        border-radius: 8px !important;
        color: #fff !important;
    }
    [data-testid="stSidebar"] button {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%) !important;
        color: #000 !important;
        border: none !important; font-weight: 800 !important;
        letter-spacing: 1px !important;
        border-radius: 8px !important;
    }

    /* === SIDEBAR LOGO === */
    .sidebar-logo-wrap {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        padding: 20px 12px; border-radius: 14px;
        text-align: center; margin-bottom: 24px;
        border: 2px solid #FFD700;
        box-shadow: 0 6px 24px rgba(255,215,0,0.25);
        position: relative;
        overflow: hidden;
    }
    .sidebar-logo-wrap::before {
        content: ""; position: absolute; top: -50%; left: -50%;
        width: 200%; height: 200%;
        background: radial-gradient(circle, rgba(255,215,0,0.08) 0%, transparent 60%);
    }
    .sidebar-logo-img {
        width: 100%; max-width: 200px; height: auto;
        margin: 0 auto 10px auto; display: block;
        border-radius: 10px;
        position: relative; z-index: 1;
    }
    .sidebar-divider {
        height: 1px; background: linear-gradient(90deg,
            transparent 0%, rgba(255,215,0,0.5) 50%, transparent 100%);
        margin: 16px 0;
    }

    /* === MAIN HEADER LOGO === */
    .header-logo-wrap {
        display: flex; align-items: center; gap: 18px;
        padding: 4px 0; position: relative; z-index: 1;
    }
    .header-logo-img {
        width: 72px; height: 72px; border-radius: 14px;
        box-shadow: 0 4px 16px rgba(255,215,0,0.4);
        background: #FFD700;
    }

    /* === MAIN HEADER === */
    .dashboard-header {
        background:
            linear-gradient(135deg, #000000 0%, #1f1f1f 50%, #000000 100%),
            radial-gradient(circle at top right, rgba(255,215,0,0.15) 0%, transparent 50%);
        padding: 28px 36px; border-radius: 18px; margin-bottom: 28px;
        border: 2px solid #FFD700; position: relative; overflow: hidden;
        box-shadow: 0 12px 40px rgba(0,0,0,0.2);
    }
    .dashboard-header::before {
        content: ""; position: absolute; top: -100%; right: -10%;
        width: 400px; height: 400px;
        background: radial-gradient(circle, rgba(255,215,0,0.15) 0%, transparent 60%);
        animation: pulse 4s ease-in-out infinite;
    }
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.6; }
        50% { transform: scale(1.2); opacity: 0.9; }
    }
    .dashboard-header h1 {
        color: #FFD700; font-size: 30px; font-weight: 900;
        margin: 0; letter-spacing: 3px;
        text-shadow: 0 2px 16px rgba(255,215,0,0.4);
        position: relative; z-index: 1;
    }
    .dashboard-header .subtitle {
        color: #cccccc; font-size: 12px; margin-top: 6px;
        letter-spacing: 2px; text-transform: uppercase;
        position: relative; z-index: 1;
    }
    .dashboard-header .badge {
        display: inline-block; background: #FFD700; color: #000;
        padding: 5px 14px; border-radius: 14px; font-size: 10px;
        font-weight: 900; letter-spacing: 1.5px; margin-top: 10px;
        box-shadow: 0 4px 12px rgba(255,215,0,0.3);
        position: relative; z-index: 1;
    }

    /* === DATE RANGE CHIP === */
    .date-chip {
        background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
        color: #000; padding: 14px 20px; border-radius: 12px;
        text-align: center; font-weight: 800; font-size: 14px;
        box-shadow: 0 4px 12px rgba(255,215,0,0.3);
    }

    /* === INFO STACK (sidebar cards) === */
    .info-stack {
        margin-top: 14px;
        margin-bottom: 18px;
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
    }
    .info-card {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        border: 1.5px solid #FFD700;
        border-radius: 10px;
        padding: 12px 6px;
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    .info-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 16px rgba(255,215,0,0.25);
    }
    .info-card-icon {
        font-size: 22px;
        margin-bottom: 6px;
        display: block;
    }
    .info-card-value {
        color: #FFD700;
        font-size: 20px;
        font-weight: 900;
        line-height: 1.1;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    .info-card-label {
        color: #ffffff;
        font-size: 9px;
        font-weight: 700;
        letter-spacing: 1.2px;
        text-transform: uppercase;
        margin-top: 4px;
        opacity: 0.9;
    }
    .live-indicator {
        margin-top: 6px;
        margin-bottom: 20px;
        background: linear-gradient(90deg, #1a1a1a 0%, #2d2d2d 100%);
        border: 1.5px solid #FFD700;
        color: #FFD700;
        padding: 12px 14px;
        border-radius: 10px;
        font-size: 11px;
        font-weight: 800;
        text-align: center;
        letter-spacing: 2px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
    }
    .live-dot {
        width: 9px; height: 9px;
        background: #FFD700;
        border-radius: 50%;
        animation: pulse 1.5s ease-in-out infinite;
        box-shadow: 0 0 8px #FFD700;
    }

    /* === KPI CARD === */
    .kpi-container {
        background: white; padding: 24px 22px; border-radius: 16px;
        border: 2px solid #1a1a1a; position: relative; overflow: hidden;
        box-shadow: 0 4px 16px rgba(0,0,0,0.06);
        margin-bottom: 14px;
        transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1),
                    box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        cursor: default;
        height: 100%;
        min-height: 160px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .kpi-container:hover {
        transform: translateY(-6px);
        box-shadow: 0 16px 40px rgba(0,0,0,0.15);
    }
    /* Top accent bar - thin and clean */
    .kpi-container::before {
        content: ""; position: absolute; top: 0; left: 0;
        width: 100%; height: 3px;
    }
    .kpi-yellow::before {
        background: linear-gradient(90deg, #FFD700 0%, #FFA500 100%);
    }
    .kpi-black::before {
        background: linear-gradient(90deg, #000000 0%, #333333 100%);
    }
    .kpi-icon {
        position: absolute; top: 18px; right: 18px;
        font-size: 28px; opacity: 0.12;
        transition: opacity 0.3s;
    }
    .kpi-container:hover .kpi-icon { opacity: 0.25; }
    .kpi-label {
        color: #555; font-size: 10px; font-weight: 800;
        letter-spacing: 3px; text-transform: uppercase;
        margin-bottom: 10px; margin-top: 4px;
    }
    .kpi-value {
        color: #000; font-size: 32px; font-weight: 900;
        line-height: 1; margin: 4px 0 8px 0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        white-space: nowrap;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .kpi-unit {
        font-size: 13px; color: #FFD700; margin-left: 6px;
        font-weight: 700;
        background: #000; padding: 2px 8px; border-radius: 10px;
        text-shadow: none;
    }
    .kpi-trend {
        font-size: 11px; font-weight: 700;
        padding: 6px 14px; border-radius: 14px;
        display: inline-flex; align-items: center; gap: 4px;
        align-self: flex-start;
        margin-top: 14px;
    }
    .trend-up {
        color: #B71C1C; background: rgba(255,107,107,0.12);
        border: 1px solid rgba(255,107,107,0.2);
    }
    .trend-down {
        color: #1B5E20; background: rgba(76,175,80,0.12);
        border: 1px solid rgba(76,175,80,0.2);
    }
    .trend-neutral {
        color: #555; background: rgba(0,0,0,0.05);
        border: 1px solid rgba(0,0,0,0.1);
    }

    /* === SECTION HEADER === */
    .section-header {
        background: linear-gradient(90deg, #FFD700 0%, #FFC107 50%, #FFD700 100%);
        background-size: 200% 100%;
        color: #000; padding: 14px 22px; border-radius: 12px;
        font-weight: 900; font-size: 16px; letter-spacing: 2px;
        margin: 28px 0 16px 0; text-transform: uppercase;
        border-left: 6px solid #000;
        box-shadow: 0 6px 16px rgba(255,215,0,0.25);
        display: flex; align-items: center; gap: 12px;
        animation: shimmer 3s linear infinite;
    }
    @keyframes shimmer {
        0% { background-position: 0% 50%; }
        100% { background-position: 200% 50%; }
    }
    .section-header .section-icon {
        font-size: 22px;
        background: #000; color: #FFD700;
        width: 36px; height: 36px;
        border-radius: 50%; display: flex;
        align-items: center; justify-content: center;
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
@st.cache_data(ttl=30)
def load_data():
    """Read from .xlsx file - cache expires every 30s so updates appear quickly."""
    xlsx_path = Path(__file__).parent / "QA_Defects_Data.xlsx"
    csv_path  = Path(__file__).parent / "QA_Defects_Data.csv"

    # Try .xlsx first (current source of truth)
    if xlsx_path.exists():
        df = pd.read_excel(xlsx_path)
    elif csv_path.exists():
        df = pd.read_csv(csv_path)
    else:
        return pd.DataFrame(columns=["Date","Supplier","Group Part","Problem Mode","Part Name","Part No","Qty","Comment"])

    # Normalize Date column - handle mixed formats ('2026-08-31' and '2026-08-31 00:00:00')
    df["Date"] = pd.to_datetime(df["Date"], format="mixed", errors="coerce")
    # Drop rows where Date couldn't be parsed
    df = df.dropna(subset=["Date"]).reset_index(drop=True)
    return df

df = load_data()

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    # === LOGO SECTION (centered with proper spacing) ===
    # Open container with generous padding
    st.markdown(
        '<div style="padding: 24px 12px 16px 12px; text-align: center;">',
        unsafe_allow_html=True
    )

    # Logo image — centered, no decorations
    try:
        st.image(LOGO_URL, width=180)
    except Exception:
        st.markdown(
            f'<img src="{LOGO_URL}" width="180" '
            f'style="border-radius:12px;display:block;margin:0 auto;">',
            unsafe_allow_html=True
        )

    # Brand text — clean, centered, proper line-height
    st.markdown(
        '<div style="color:#FFD700; font-size:20px; font-weight:900; '
        'letter-spacing:3px; margin-top:18px; line-height:1.2;">'
        '⚡ 3K BATTERY</div>'
        '<div style="color:#999; font-size:10px; font-weight:600; '
        'letter-spacing:2.5px; margin-top:8px; line-height:1.2;">'
        'QA DEFECTS DASHBOARD</div>'
        '</div>',
        unsafe_allow_html=True
    )

    # Divider
    st.markdown(
        '<div style="height:1px; margin:24px 8px; '
        'background:linear-gradient(90deg, transparent 0%, '
        'rgba(255,215,0,0.4) 50%, transparent 100%);"></div>',
        unsafe_allow_html=True
    )

    # === NAVIGATION ===
    page = st.radio(
        "NAVIGATION",
        ["📊 14 Days Monitoring", "🔍 Searching Supplier Information", "📝 Data Entry"],
        label_visibility="collapsed"
    )

    # Divider
    st.markdown(
        '<div style="height:1px; margin:20px 8px; '
        'background:linear-gradient(90deg, transparent 0%, '
        'rgba(255,215,0,0.3) 50%, transparent 100%);"></div>',
        unsafe_allow_html=True
    )

    # === FILTERS ===
    st.markdown(
        '<div style="color:#FFD700; font-size:11px; font-weight:800; '
        'letter-spacing:2.5px; margin:0 4px 12px 4px; '
        'text-transform:uppercase;">🎛️ FILTERS</div>',
        unsafe_allow_html=True
    )

    supplier_f = st.selectbox(
        "Supplier", ["All"] + sorted(df["Supplier"].unique().tolist())
    )
    group_f = st.selectbox(
        "Group Part", ["All"] + sorted(df["Group Part"].unique().tolist())
    )
    mode_f = st.selectbox(
        "Problem Mode", ["All"] + sorted(df["Problem Mode"].unique().tolist())
    )

    # Divider
    st.markdown(
        '<div style="height:1px; margin:20px 8px; '
        'background:linear-gradient(90deg, transparent 0%, '
        'rgba(255,215,0,0.3) 50%, transparent 100%);"></div>',
        unsafe_allow_html=True
    )

    # Reset button
    if st.button("🗑️ RESET ALL FILTERS", use_container_width=True):
        st.session_state.selected_group = None
        st.rerun()

    # Footer info at bottom
    st.markdown(
        '<div style="position:relative; margin-top:24px; padding:14px 12px; '
        'background:rgba(255,215,0,0.08); border:1px solid rgba(255,215,0,0.3); '
        'border-radius:10px; text-align:center;">'
        '<div style="color:#FFD700; font-size:9px; font-weight:700; '
        'letter-spacing:2px;">📅 LAST UPDATE</div>'
        f'<div style="color:#fff; font-size:11px; font-weight:800; '
        f'margin-top:4px;">{datetime.now().strftime("%Y-%m-%d")}</div>'
        f'<div style="color:#666; font-size:9px; margin-top:2px;">'
        f'{datetime.now().strftime("%H:%M:%S")}</div>'
        '</div>',
        unsafe_allow_html=True
    )

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
elif "Searching" in page:
    title_text = "SEARCHING SUPPLIER INFORMATION"
    subtitle = "PPM Analysis & Comparison"
else:  # Data Entry
    title_text = "DATA ENTRY"
    subtitle = "Quick Defect Logging System"

max_date = df["Date"].max()
min_date = max_date - timedelta(days=13)

hdr1, hdr2 = st.columns([3, 1])
with hdr1:
    st.markdown(
        f"""
        <div class="dashboard-header">
            <h1>⚡ {title_text}</h1>
            <div class="subtitle">{subtitle}</div>
            <div class="badge">🏭 3K BATTERY CO., LTD.</div>
        </div>
        """,
        unsafe_allow_html=True
    )
with hdr2:
    # Calculate quick stats for sidebar info
    n_suppliers = filtered["Supplier"].nunique() if "Supplier" in filtered.columns else 0
    n_groups    = filtered["Group Part"].nunique() if "Group Part" in filtered.columns else 0
    n_modes     = filtered["Problem Mode"].nunique() if "Problem Mode" in filtered.columns else 0

    st.markdown(f"""
    <div class="date-chip">
        📅 REPORT PERIOD<br>
        <span style="font-size: 13px;">{min_date.strftime('%m/%d/%Y')}</span><br>
        <span style="font-size: 16px;">↓</span><br>
        <span style="font-size: 13px;">{max_date.strftime('%m/%d/%Y')}</span>
    </div>

    <div class="info-stack">
        <div class="info-card">
            <span class="info-card-icon">🏭</span>
            <div class="info-card-value">{n_suppliers}</div>
            <div class="info-card-label">Suppliers</div>
        </div>
        <div class="info-card">
            <span class="info-card-icon">📦</span>
            <div class="info-card-value">{n_groups}</div>
            <div class="info-card-label">Groups</div>
        </div>
        <div class="info-card">
            <span class="info-card-icon">⚠️</span>
            <div class="info-card-value">{n_modes}</div>
            <div class="info-card-label">Modes</div>
        </div>
    </div>

    <div class="live-indicator">
        <span class="live-dot"></span>
        <span>LIVE DATA</span>
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

    # === TREND CALCULATION (Last 7 days vs Previous 7 days) ===
    if not filtered.empty:
        max_date = filtered["Date"].max()
        cutoff = max_date - pd.Timedelta(days=6)
        prev_cutoff = max_date - pd.Timedelta(days=13)
        recent_7 = filtered[filtered["Date"] >= cutoff]
        prev_7 = filtered[(filtered["Date"] >= prev_cutoff) & (filtered["Date"] < cutoff)]

        recent_qty = int(recent_7["Qty"].sum())
        prev_qty = int(prev_7["Qty"].sum())
        recent_case = len(recent_7)
        prev_case = len(prev_7)

        # For QTY: lower is better → up arrow = bad (red), down arrow = good (green)
        if prev_qty > 0:
            qty_pct = round(((recent_qty - prev_qty) / prev_qty) * 100, 1)
        else:
            qty_pct = 0.0 if recent_qty == 0 else 100.0

        # For CASE: lower is better
        if prev_case > 0:
            case_pct = round(((recent_case - prev_case) / prev_case) * 100, 1)
        else:
            case_pct = 0.0 if recent_case == 0 else 100.0

        # For AVG/CASE: lower is better
        recent_avg = recent_qty / max(recent_case, 1)
        prev_avg = prev_qty / max(prev_case, 1)
        if prev_avg > 0:
            avg_pct = round(((recent_avg - prev_avg) / prev_avg) * 100, 1)
        else:
            avg_pct = 0.0

        # For UNIQUE PARTS: lower is better
        recent_parts = recent_7["Part No"].nunique()
        prev_parts = prev_7["Part No"].nunique()
        if prev_parts > 0:
            parts_pct = round(((recent_parts - prev_parts) / prev_parts) * 100, 1)
        else:
            parts_pct = 0.0 if recent_parts == 0 else 100.0
    else:
        qty_pct = case_pct = avg_pct = parts_pct = 0.0

    def trend_arrow(value):
        # For QA defects: lower is better
        # value > 0 = bad (up arrow red), value < 0 = good (down arrow green)
        if value > 0:
            return "up"
        elif value < 0:
            return "down"
        else:
            return "neutral"

    qty_arrow = trend_arrow(qty_pct)
    case_arrow = trend_arrow(case_pct)
    avg_arrow = trend_arrow(avg_pct)
    parts_arrow = trend_arrow(parts_pct)

    daily = filtered.groupby("Date").agg(Qty=("Qty", "sum"), Case=("Qty", "count")).reset_index()
    labels = daily["Date"].dt.strftime("%m/%d").tolist()
    qty_data = daily["Qty"].tolist()
    case_data = daily["Case"].tolist()

    # === KPI ROW ===
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    with kpi1:
        unique_suppliers = filtered["Supplier"].nunique()
        arrow_icon = {"up": "▲", "down": "▼", "neutral": "—"}[qty_arrow]
        st.markdown(f"""
        <div class="kpi-container kpi-yellow">
            <div class="kpi-icon">📦</div>
            <div class="kpi-label">📦 TOTAL Q'TY</div>
            <div class="kpi-value">{total_qty:,}<span class="kpi-unit">PCS</span></div>
            <div class="kpi-trend trend-{qty_arrow}">{arrow_icon} {abs(qty_pct):.1f}% vs prev 7d</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi2:
        arrow_icon = {"up": "▲", "down": "▼", "neutral": "—"}[case_arrow]
        st.markdown(f"""
        <div class="kpi-container kpi-black">
            <div class="kpi-icon">📋</div>
            <div class="kpi-label">📋 TOTAL CASE</div>
            <div class="kpi-value">{total_case:,}<span class="kpi-unit">CASE</span></div>
            <div class="kpi-trend trend-{case_arrow}">{arrow_icon} {abs(case_pct):.1f}% vs prev 7d</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi3:
        avg_qty = round(total_qty / max(total_case, 1), 1)
        arrow_icon = {"up": "▲", "down": "▼", "neutral": "—"}[avg_arrow]
        st.markdown(f"""
        <div class="kpi-container kpi-yellow">
            <div class="kpi-icon">📊</div>
            <div class="kpi-label">📊 AVG / CASE</div>
            <div class="kpi-value">{avg_qty}<span class="kpi-unit">PCS</span></div>
            <div class="kpi-trend trend-{avg_arrow}">{arrow_icon} {abs(avg_pct):.1f}% vs prev 7d</div>
        </div>
        """, unsafe_allow_html=True)

    with kpi4:
        unique_parts = filtered["Part No"].nunique()
        arrow_icon = {"up": "▲", "down": "▼", "neutral": "—"}[parts_arrow]
        st.markdown(f"""
        <div class="kpi-container kpi-black">
            <div class="kpi-icon">⚙</div>
            <div class="kpi-label">⚙ UNIQUE PARTS</div>
            <div class="kpi-value">{unique_parts}<span class="kpi-unit">PART</span></div>
            <div class="kpi-trend trend-{parts_arrow}">{arrow_icon} {abs(parts_pct):.1f}% vs prev 7d</div>
        </div>
        """, unsafe_allow_html=True)

    # === TREND CHARTS ===
    st.markdown(
        '<div class="section-header">'
        '<div class="section-icon">📈</div>'
        'DAILY TREND ANALYSIS'
        '</div>',
        unsafe_allow_html=True
    )

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
# PAGE 3: DATA ENTRY (Quick Logging System)
# ============================================================
elif "Data Entry" in page:
    st.markdown(
        '<div class="section-header">'
        '<div class="section-icon">📝</div>'
        'QUICK DEFECT LOGGING'
        '</div>',
        unsafe_allow_html=True
    )

    # Initialize session state for new entries
    if "new_entries" not in st.session_state:
        st.session_state.new_entries = []

    if "form_reset_counter" not in st.session_state:
        st.session_state.form_reset_counter = 0

    if "uploaded_data" not in st.session_state:
        st.session_state.uploaded_data = None

    # === MODE SELECTOR ===
    entry_mode = st.radio(
        "📋 Choose how you want to add data:",
        ["📤 Upload Excel File", "✏️ Manual Form"],
        horizontal=True,
        key="entry_mode_selector"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ============================================================
    # MODE 1: UPLOAD EXCEL FILE
    # ============================================================
    if entry_mode == "📤 Upload Excel File":
        st.markdown(
            '<div style="background: linear-gradient(135deg, #FFD700 0%, #FFC107 100%);'
            'color: #000; padding: 20px; border-radius: 12px; margin-bottom: 16px;'
            'border: 2px solid #000; box-shadow: 0 4px 16px rgba(255,215,0,0.3);">'
            '<b style="font-size: 15px;">📤 UPLOAD EXCEL — Fastest way to add multiple records</b><br>'
            '<span style="color: #333; font-size: 12px;">'
            'Drag & drop your edited Excel file (.xlsx) → preview → sync to dashboard'
            '</span></div>',
            unsafe_allow_html=True
        )

        uploaded_file = st.file_uploader(
            "📁 Choose Excel file (.xlsx)",
            type=["xlsx"],
            help="Upload the QA_Defects_Template.xlsx file after editing",
            key="excel_uploader"
        )

        if uploaded_file is not None:
            try:
                # Try to read Excel (try multiple sheet names)
                df_uploaded = None
                sheet_used = None
                for sheet_name in ["Defects Data", "Sheet1", 0]:
                    try:
                        df_uploaded = pd.read_excel(uploaded_file, sheet_name=sheet_name, header=3)
                        sheet_used = sheet_name
                        break
                    except Exception:
                        continue

                if df_uploaded is None or df_uploaded.empty:
                    st.error("❌ Could not read Excel file. Make sure it has data.")
                else:
                    # Validate required columns
                    required_cols = ["Date", "Supplier", "Group Part", "Problem Mode", "Part No", "Qty"]
                    missing_cols = [c for c in required_cols if c not in df_uploaded.columns]
                    extra_cols = [c for c in df_uploaded.columns if c not in required_cols + ["Part Name", "Comment"]]

                    # === VALIDATION REPORT ===
                    valid_records = []
                    invalid_records = []

                    for idx, row in df_uploaded.iterrows():
                        record = {}
                        record["Date"] = str(row.get("Date", ""))
                        record["Supplier"] = str(row.get("Supplier", ""))
                        record["Group Part"] = str(row.get("Group Part", ""))
                        record["Problem Mode"] = str(row.get("Problem Mode", ""))
                        record["Part Name"] = str(row.get("Part Name", "") or "—")
                        record["Part No"] = str(row.get("Part No", ""))
                        try:
                            record["Qty"] = int(row.get("Qty", 0))
                        except (ValueError, TypeError):
                            record["Qty"] = 0
                        record["Comment"] = str(row.get("Comment", "") or "—")

                        # Check if row is empty
                        if all(v in ["", "nan", "—", None, 0] for v in [record["Date"], record["Supplier"], record["Part No"]]):
                            continue

                        # Validate required fields
                        row_errors = []
                        if not record["Date"] or record["Date"] == "nan":
                            row_errors.append("Date missing")
                        if not record["Supplier"] or record["Supplier"] == "nan":
                            row_errors.append("Supplier missing")
                        if not record["Part No"] or record["Part No"] == "nan":
                            row_errors.append("Part No missing")
                        if record["Qty"] <= 0:
                            row_errors.append("Qty must be > 0")

                        if row_errors:
                            invalid_records.append({"row": idx + 5, "data": record, "errors": row_errors})
                        else:
                            valid_records.append(record)

                    # Show validation results
                    col_v1, col_v2, col_v3 = st.columns(3)
                    with col_v1:
                        st.markdown(
                            f'<div style="background:#000; color:#FFD700; padding:14px; '
                            f'border-radius:10px; text-align:center;">'
                            f'<div style="font-size:11px; opacity:0.8;">TOTAL ROWS</div>'
                            f'<div style="font-size:28px; font-weight:900;">{len(df_uploaded)}</div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                    with col_v2:
                        st.markdown(
                            f'<div style="background:#4CAF50; color:white; padding:14px; '
                            f'border-radius:10px; text-align:center;">'
                            f'<div style="font-size:11px; opacity:0.9;">VALID ✓</div>'
                            f'<div style="font-size:28px; font-weight:900;">{len(valid_records)}</div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                    with col_v3:
                        st.markdown(
                            f'<div style="background:#F44336; color:white; padding:14px; '
                            f'border-radius:10px; text-align:center;">'
                            f'<div style="font-size:11px; opacity:0.9;">INVALID ✗</div>'
                            f'<div style="font-size:28px; font-weight:900;">{len(invalid_records)}</div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )

                    # Show column warnings
                    if missing_cols:
                        st.warning(f"⚠️ Missing columns: {', '.join(missing_cols)}")
                    if extra_cols:
                        st.info(f"�️ Extra columns ignored: {', '.join(extra_cols)}")

                    # Preview table
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("##### 📋 Preview (Valid Records)")

                    if valid_records:
                        preview_df = pd.DataFrame(valid_records)
                        st.dataframe(
                            preview_df[["Date", "Supplier", "Group Part", "Problem Mode", "Part No", "Qty"]],
                            use_container_width=True, hide_index=True,
                            height=300
                        )
                        st.session_state.uploaded_data = valid_records

                        # === SEND TO KANOM ===
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.markdown(
                            '<div style="background: #000; color: #FFD700; padding: 16px 20px; '
                            'border-radius: 12px; margin-bottom: 16px; '
                            'border: 2px solid #FFD700;">'
                            '<b style="font-size: 14px;">📤 READY TO SYNC!</b><br>'
                            '<span style="color: #ccc; font-size: 12px;">'
                            f'{len(valid_records)} valid records detected. Download CSV and send to Kanom via Telegram. '
                            'Dashboard will refresh in 1-2 minutes.'
                            '</span></div>',
                            unsafe_allow_html=True
                        )

                        # CSV download + Telegram sync
                        csv_data = preview_df.to_csv(index=False).encode('utf-8')
                        col_dl1, col_dl2 = st.columns(2)
                        with col_dl1:
                            st.download_button(
                                "📥 DOWNLOAD CSV",
                                csv_data,
                                f"defects_upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                "text/csv",
                                use_container_width=True,
                                type="primary"
                            )
                        with col_dl2:
                            # Copy to clipboard text area
                            st.text_area(
                                "📋 Or copy CSV text:",
                                preview_df.to_csv(index=False),
                                height=80,
                                help="Copy and paste to Telegram"
                            )

                        # === TELEGRAM DIRECT SYNC ===
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.markdown(
                            '<div style="background: linear-gradient(135deg, #FFD700 0%, #FFC107 100%);'
                            'color: #000; padding: 16px; border-radius: 10px; margin-bottom: 12px;'
                            'border: 2px solid #000;">'
                            '<b style="font-size: 14px;">⚡ FASTEST: Send directly to Kanom</b><br>'
                            '<span style="color: #333; font-size: 12px;">'
                            'Click button below → message sent to Kanom via Telegram → dashboard refreshes in 1 min'
                            '</span></div>',
                            unsafe_allow_html=True
                        )

                        if st.button(
                            "📤 SYNC TO GITHUB (1-CLICK)",
                            use_container_width=True,
                            type="primary",
                            key="sync_github_btn",
                            help="Push data directly to GitHub repo - dashboard refreshes in 1 min"
                        ):
                            try:
                                # Use GitHub Contents API to push xlsx directly
                                # Note: requires github_token in secrets, fallback to instructions
                                try:
                                    gh_token = st.secrets["github_token"]
                                    gh_repo  = st.secrets.get("github_repo", "panuchuwong-cyber/qa-defects-dashboard")
                                    gh_branch = st.secrets.get("github_branch", "main")
                                except (KeyError, FileNotFoundError, AttributeError):
                                    gh_token = None
                                    gh_repo  = None

                                if gh_token:
                                    import requests
                                    import base64
                                    from openpyxl import load_workbook

                                    # Merge uploaded records with existing data, then push
                                    existing_path = Path("QA_Defects_Data.xlsx")
                                    if existing_path.exists():
                                        existing_wb = load_workbook(existing_path)
                                        existing_ws = existing_wb.active
                                        # Read existing records (skip header)
                                        existing_records = []
                                        headers = [c.value for c in existing_ws[1]]
                                        for row in existing_ws.iter_rows(min_row=2, values_only=True):
                                            existing_records.append(dict(zip(headers, row)))
                                    else:
                                        existing_records = []
                                        headers = ["Date","Supplier","Group Part","Problem Mode","Part Name","Part No","Qty","Comment"]

                                    # Merge with deduplication (key = Date + Supplier + Part No)
                                    new_records_df = pd.DataFrame(valid_records)
                                    existing_df = pd.DataFrame(existing_records)

                                    if not existing_df.empty:
                                        # Combine, then drop duplicates keeping the NEW record
                                        merged_df = pd.concat([new_records_df, existing_df], ignore_index=True)
                                        merged_df = merged_df.drop_duplicates(
                                            subset=["Date", "Supplier", "Part No"],
                                            keep="first"  # first = the new uploaded record
                                        ).reset_index(drop=True)
                                    else:
                                        merged_df = new_records_df.reset_index(drop=True)

                                    added = len(new_records_df)
                                    total = len(merged_df)

                                    # Save to bytes for upload
                                    from openpyxl import Workbook
                                    wb_out = Workbook()
                                    ws_out = wb_out.active
                                    ws_out.append(headers)
                                    for _, row in merged_df.iterrows():
                                        ws_out.append([row.get(h, "") for h in headers])
                                    buf = io.BytesIO()
                                    wb_out.save(buf)
                                    content_b64 = base64.b64encode(buf.getvalue()).decode()

                                    # Read existing file SHA from GitHub
                                    api_base = f"https://api.github.com/repos/{gh_repo}/contents/QA_Defects_Data.xlsx"
                                    headers_auth = {
                                        "Authorization": f"Bearer {gh_token}",
                                        "Accept": "application/vnd.github+json"
                                    }
                                    existing_resp = requests.get(api_base, headers=headers_auth, params={"ref": gh_branch}, timeout=10)
                                    sha = existing_resp.json().get("sha") if existing_resp.status_code == 200 else None

                                    # Push merged xlsx
                                    payload = {
                                        "message": f"DATA: sync {added} new records (dedup, total {total})",
                                        "content": content_b64,
                                        "branch": gh_branch,
                                    }
                                    if sha:
                                        payload["sha"] = sha

                                    push_resp = requests.put(api_base, headers=headers_auth, json=payload, timeout=15)

                                    if push_resp.status_code in (200, 201):
                                        st.success(
                                            f"✅ **Pushed to GitHub successfully!**\n\n"
                                            f"📊 {len(valid_records)} records committed.\n"
                                            f"🔄 Dashboard will rebuild and refresh in 1-2 minutes.\n\n"
                                            f"💡 **No Telegram needed** — pure Git workflow!"
                                        )
                                        st.balloons()
                                    else:
                                        err = push_resp.json().get("message", push_resp.text)
                                        st.error(f"❌ GitHub push failed: {err}")
                                else:
                                    st.info(
                                        "ℹ️ **GitHub API not configured**\n\n"
                                        "**To enable 1-click sync, add these to Streamlit Cloud secrets:**\n"
                                        "```toml\n"
                                        "github_token = \"ghp_xxxxxxxxxxxxxxxxxxxx\"\n"
                                        "github_repo  = \"panuchuwong-cyber/qa-defects-dashboard\"\n"
                                        "github_branch = \"main\"\n"
                                        "```\n\n"
                                        "Get a token at: https://github.com/settings/tokens (scope: `repo`)\n\n"
                                        "📥 **OR use the DOWNLOAD CSV button below** → paste text here."
                                    )

                            except Exception as e:
                                st.error(f"❌ Sync error: {str(e)}\n\n📥 Use download button as fallback.")

                    # Show invalid records
                    if invalid_records:
                        st.markdown("<br>", unsafe_allow_html=True)
                        with st.expander(f"⚠️ {len(invalid_records)} Invalid Records (click to view)"):
                            for inv in invalid_records:
                                st.error(
                                    f"**Row {inv['row']}:** {', '.join(inv['errors'])}\n\n"
                                    f"`{inv['data']}`"
                                )

            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")
                st.info("� Make sure you're uploading the QA_Defects_Template.xlsx file")

        # Footer for upload mode
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            '<div style="background: #FFF8DC; padding: 16px; border-radius: 10px; '
            'border: 1px solid #FFD700; font-size: 12px; color: #333;">'
            '<b>💡 TIP:</b> Use the QA_Defects_Template.xlsx for consistent format. '
            'The template has dropdowns for Group Part and Problem Mode to prevent typos.'
            '</div>',
            unsafe_allow_html=True
        )

    # ============================================================
    # MODE 2: MANUAL FORM (existing logic)
    # ============================================================
    else:
        # === INFO BOX ===
        st.markdown("""
        <div style="background: linear-gradient(135deg, #000 0%, #1a1a1a 100%);
                    color: #FFD700; padding: 16px 20px; border-radius: 12px;
                    border: 1px solid #FFD700; margin-bottom: 20px;
                    box-shadow: 0 4px 16px rgba(0,0,0,0.15);">
            <b style="font-size: 14px;">💡 HOW IT WORKS</b><br>
            <span style="color: #ccc; font-size: 12px;">
                1. Fill the form below<br>
                2. Click <b>"✅ ADD RECORD"</b> — data appears in table below<br>
                3. Copy the table data and send to Kanom via Telegram<br>
                4. Kanom will save to GitHub → Dashboard refreshes for everyone
            </span>
        </div>
        """, unsafe_allow_html=True)

        # === FORM ===
        col_form, col_preview = st.columns([3, 2])

        with col_form:
            st.markdown(
                '<div style="background:white; padding:24px; border-radius:14px; '
                'border:2px solid #000; box-shadow:0 4px 16px rgba(0,0,0,0.08);">'
                '<div style="color:#000; font-weight:900; font-size:14px; '
                'letter-spacing:2px; margin-bottom:16px; '
                'border-bottom:3px solid #FFD700; padding-bottom:8px;">'
                '📋 NEW DEFECT RECORD</div>',
                unsafe_allow_html=True
            )

            # Form fields with key based on reset counter to force clear after save
            rc = st.session_state.form_reset_counter
            c1, c2 = st.columns(2)
            with c1:
                entry_date = st.date_input(
                    "📅 Date",
                    value=datetime.now().date(),
                    key=f"date_{rc}"
                )
                entry_supplier = st.selectbox(
                    "🏭 Supplier",
                    ["-- Select Supplier --"] + sorted(df["Supplier"].unique().tolist()) + ["� Add new..."],
                    key=f"supplier_{rc}"
                )
                if entry_supplier == "➕ Add new...":
                    entry_supplier = st.text_input(
                        "✏️ New supplier name", key=f"new_supplier_{rc}"
                    )
                entry_group = st.selectbox(
                    "📦 Group Part",
                    ["-- Select Group --",
                     "ELECTRIC & ELEC.", "PACKING", "PIPING", "PLASTIC",
                     "PRINTING", "RAW MATERIAL", "RUBBER", "SHEET METAL",
                     "FOAM", "SEALING", "OTHERS"],
                    key=f"group_{rc}"
                )
                entry_mode = st.selectbox(
                    "⚠️ Problem Mode",
                    ["-- Select Mode --",
                     "APPEARANCE NG", "PART MISTAKE", "DIMENSION NG",
                     "FUNCTION NG", "LEAK"],
                    key=f"mode_{rc}"
                )

            with c2:
                entry_part_name = st.text_input(
                    "⚙️ Part Name",
                    placeholder="e.g., ELBOW PIPE 1/2",
                    key=f"partname_{rc}"
                )
                entry_part_no = st.text_input(
                    "🔧 Part No.",
                    placeholder="e.g., 1P095004-1 K",
                    key=f"partno_{rc}"
                )
                entry_qty = st.number_input(
                    "📦 Quantity (PCS)",
                    min_value=1,
                    value=1,
                    step=1,
                    key=f"qty_{rc}"
                )
                entry_comment = st.text_area(
                    "💬 Comment",
                    placeholder="Describe the defect...",
                    height=80,
                    key=f"comment_{rc}"
                )

            # Action buttons
            st.markdown("<br>", unsafe_allow_html=True)
            btn_c1, btn_c2 = st.columns(2)
            with btn_c1:
                add_clicked = st.button(
                    "✅ ADD RECORD",
                    use_container_width=True,
                    type="primary"
                )
            with btn_c2:
                clear_clicked = st.button(
                    "🗑️ CLEAR FORM",
                    use_container_width=True,
                    type="secondary"
                )

            st.markdown('</div>', unsafe_allow_html=True)

            # Handle ADD
            if add_clicked:
                # Validate required fields
                errors = []
                if entry_supplier in ["-- Select Supplier --", None, ""]:
                    errors.append("Supplier")
                if entry_group in ["-- Select Group --", None, ""]:
                    errors.append("Group Part")
                if entry_mode in ["-- Select Mode --", None, ""]:
                    errors.append("Problem Mode")
                if not entry_part_no.strip():
                    errors.append("Part No.")

                if errors:
                    st.error(f"❌ Please fill required fields: {', '.join(errors)}")
                else:
                    new_record = {
                        "Date": entry_date.strftime("%Y-%m-%d"),
                        "Supplier": entry_supplier,
                        "Group Part": entry_group,
                        "Problem Mode": entry_mode,
                        "Part Name": entry_part_name.strip() or "—",
                        "Part No": entry_part_no.strip(),
                        "Qty": int(entry_qty),
                        "Comment": entry_comment.strip() or "—"
                    }
                    st.session_state.new_entries.append(new_record)
                    st.session_state.form_reset_counter += 1
                    st.success(f"✅ Record #{len(st.session_state.new_entries)} added!")
                    st.rerun()

            # Handle CLEAR form
            if clear_clicked:
                st.session_state.form_reset_counter += 1
                st.rerun()

        # === PREVIEW / PENDING RECORDS ===
        with col_preview:
            st.markdown(
                '<div style="background:white; padding:20px; border-radius:14px; '
                'border:2px solid #FFD700; box-shadow:0 4px 16px rgba(255,215,0,0.2);">'
                '<div style="color:#000; font-weight:900; font-size:14px; '
                'letter-spacing:2px; margin-bottom:12px; '
                'border-bottom:3px solid #000; padding-bottom:8px;">'
                f'📦 PENDING ({len(st.session_state.new_entries)} records)</div>',
                unsafe_allow_html=True
            )

            if st.session_state.new_entries:
                pending_df = pd.DataFrame(st.session_state.new_entries)
                st.dataframe(
                    pending_df[["Date", "Supplier", "Group Part", "Qty"]],
                    use_container_width=True, hide_index=True,
                    height=300
                )

                # Total summary
                total_pending_qty = pending_df["Qty"].sum()
                st.markdown(
                    f'<div style="background:#FFD700; color:#000; padding:10px; '
                    f'border-radius:8px; margin-top:8px; text-align:center; '
                    f'font-weight:900;">'
                    f'TOTAL: {total_pending_qty} PCS / {len(pending_df)} CASE'
                    f'</div>',
                    unsafe_allow_html=True
                )

                # Export buttons
                st.markdown("<br>", unsafe_allow_html=True)
                csv_data = pending_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 DOWNLOAD CSV",
                    csv_data,
                    "defects_pending.csv",
                    "text/csv",
                    use_container_width=True,
                    type="secondary"
                )

                if st.button("🗑️ CLEAR ALL PENDING", use_container_width=True):
                    st.session_state.new_entries = []
                    st.rerun()
            else:
                st.markdown(
                    '<div style="color:#999; font-size:13px; text-align:center; '
                    'padding:30px 10px;">'
                    '📋 No pending records yet.<br>'
                    'Add records using the form →'
                    '</div>',
                    unsafe_allow_html=True
                )

            st.markdown('</div>', unsafe_allow_html=True)

        # === SEND TO KANOM INSTRUCTIONS ===
        if st.session_state.new_entries:
            st.markdown(
                '<div class="section-header">'
                '<div class="section-icon">📤</div>'
                'SEND TO KANOM TO PUBLISH'
                '</div>',
                unsafe_allow_html=True
            )

            st.markdown("""
            <div style="background: #FFF8DC; padding: 20px; border-radius: 12px;
                        border: 2px solid #FFD700; margin-bottom: 16px;">
                <b style="color: #000; font-size: 14px;">📌 3 WAYS TO SEND:</b>
                <ol style="color: #333; font-size: 13px; line-height: 1.8; margin-top: 8px;">
                    <li><b>Screenshot</b> the table below → send via Telegram</li>
                    <li><b>Copy-paste</b> the CSV text below → paste in Telegram chat</li>
                    <li><b>Download</b> CSV file → send file via Telegram</li>
                </ol>
                <div style="background: #000; color: #FFD700; padding: 10px 14px;
                            border-radius: 8px; margin-top: 12px; font-size: 12px;">
                    ⏱️ <b>Kanom will publish within 30 seconds!</b><br>
                    📊 Dashboard refreshes → everyone sees new data
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Show CSV text for easy copy
            csv_text = pending_df.to_csv(index=False)
            st.text_area(
                "📋 Copy this CSV:",
                csv_text,
                height=200,
                help="Copy this text and paste in Telegram to Kanom"
            )


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
