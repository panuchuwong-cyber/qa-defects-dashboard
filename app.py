"""
QA Defects Web Dashboard - Streamlit version
Run: streamlit run app.py
"""

import streamlit as st
import pandas as pd
from pathlib import Path

CHARTJS_CDN = "https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"

# --- Password Gate ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.markdown("""
        <style>
        .login-box {
            max-width: 400px;
            margin: 80px auto;
            padding: 40px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            text-align: center;
        }
        </style>
        <div class="login-box">
            <h1 style="color:#1668E3;">🔒 QA Defects Dashboard</h1>
            <p style="color:#666;">TEST Co. — Restricted Access</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            password = st.text_input("Password", type="password", label_visibility="collapsed", placeholder="Enter password")
            if st.button("🔓 Login", use_container_width=True):
                try:
                    correct_password = st.secrets["password"]
                except Exception:
                    correct_password = "TEST@2026"
                if password == correct_password:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ Wrong password")
        st.stop()

check_password()

# Page config
st.set_page_config(
    page_title="QA Defects Dashboard - TEST Co.",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS to mimic Daikin style
st.markdown("""
<style>
.main-header {
    background: linear-gradient(135deg, #1668E3 0%, #0d4ba8 100%);
    color: white;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 20px;
}
.main-header h1 {
    color: white;
    margin: 0;
    font-size: 28px;
    font-weight: 700;
}
.kpi-card {
    background: white;
    padding: 20px;
    border-radius: 8px;
    border-left: 5px solid #1668E3;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}
.kpi-value {
    font-size: 36px;
    font-weight: 800;
    color: #1668E3;
}
.section-header {
    background: #1668E3;
    color: white;
    padding: 10px 16px;
    border-radius: 5px;
    font-weight: 700;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)

# Data loader with cache
@st.cache_data
def load_data():
    csv_path = Path(__file__).parent / "QA_Defects_Data.csv"
    df = pd.read_csv(csv_path)
    df["Date_parsed"] = pd.to_datetime(df["Date"], format="%d/%m/%y")
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Please ensure QA_Defects_Data.csv is in the same directory as app.py")
    st.stop()

# Sidebar filters
with st.sidebar:
    st.markdown("### 🎯 Menu")
    menu = st.radio(
        "Navigation",
        ["📊 BIG PROBLEM", "📈 TOTAL PPM", "⭐ EVALUATION", "📅 MONITORING", "🔍 SEARCHING", "✅ SELECTION"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("### 🔧 Filters")

    fy_options = ["All", "FY2026", "FY2025"]
    fy = st.selectbox("SELECT FY", fy_options)

    supplier_options = ["All"] + sorted(df["Supplier Name"].unique().tolist())
    supplier = st.selectbox("SUPPLIER NAME", supplier_options)

    group_options = sorted(df["Group"].unique().tolist())
    selected_groups = st.multiselect("SUPPLIER GROUP", group_options)

    if st.button("🔄 CLEAR FILTER", use_container_width=True):
        st.rerun()

    st.markdown("---")
    st.caption(f"Last updated: {pd.Timestamp.now().strftime('%d/%m/%Y %H:%M:%S')}")
    st.caption("Data: QA Defects (14 days)")

# Apply filters
filtered = df.copy()
if supplier != "All":
    filtered = filtered[filtered["Supplier Name"] == supplier]
if selected_groups:
    filtered = filtered[filtered["Group"].isin(selected_groups)]

# Header
date_min = df["Date_parsed"].min().strftime("%d/%m/%Y")
date_max = df["Date_parsed"].max().strftime("%d/%m/%Y")
header_col1, header_col2, header_col3 = st.columns([1, 4, 2])
with header_col1:
    st.markdown("## 🏭 TEST")
with header_col2:
    st.markdown(f"""
    <div class="main-header">
        <h1>14 DAYS DEFECT MONITORING</h1>
    </div>
    """, unsafe_allow_html=True)
with header_col3:
    st.markdown(f"<div style='text-align: right; padding-top: 16px;'><b>📅 {date_min} - {date_max}</b></div>", unsafe_allow_html=True)

# KPIs
total_qty = int(filtered["Quantity"].sum())
total_case = len(filtered)
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div style="color:#555; font-size:14px; font-weight:600;">QTY (Defect Quantity)</div>
        <div class="kpi-value">{total_qty:,} <span style="font-size:16px; color:#888;">PCS</span></div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div style="color:#555; font-size:14px; font-weight:600;">CASE (Defect Cases)</div>
        <div class="kpi-value" style="color:#fd7e14;">{total_case} <span style="font-size:16px; color:#888;">CASE</span></div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Charts row
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-header">📊 QTY GRAPH</div>', unsafe_allow_html=True)
    daily_qty = filtered.groupby("Date")["Quantity"].sum().reset_index()
    daily_qty.columns = ["Date", "QTY"]
    qty_labels = daily_qty["Date"].tolist()
    qty_values = daily_qty["QTY"].tolist()

    qty_chart_html = f"""
    <canvas id="qtyChart" height="280"></canvas>
    <script src="{CHARTJS_CDN}"></script>
    <script>
    new Chart(document.getElementById('qtyChart'), {{
        type: 'bar',
        data: {{
            labels: {qty_labels},
            datasets: [{{
                label: 'QTY',
                data: {qty_values},
                backgroundColor: '#1668E3',
                borderRadius: 4,
            }}]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{ legend: {{ display: false }} }},
            scales: {{ y: {{ beginAtZero: true }} }}
        }}
    }});
    </script>
    """
    st.components.v1.html(qty_chart_html, height=300)

with col2:
    st.markdown('<div class="section-header">📈 CASE GRAPH</div>', unsafe_allow_html=True)
    daily_case = filtered.groupby("Date").size().reset_index()
    daily_case.columns = ["Date", "CASE"]
    case_labels = daily_case["Date"].tolist()
    case_values = daily_case["CASE"].tolist()

    case_chart_html = f"""
    <canvas id="caseChart" height="280"></canvas>
    <script src="{CHARTJS_CDN}"></script>
    <script>
    new Chart(document.getElementById('caseChart'), {{
        type: 'line',
        data: {{
            labels: {case_labels},
            datasets: [{{
                label: 'CASE',
                data: {case_values},
                borderColor: '#fd7e14',
                backgroundColor: 'rgba(253,126,20,0.15)',
                fill: true,
                tension: 0.3,
                pointBackgroundColor: '#fd7e14',
                pointRadius: 5,
            }}]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{ legend: {{ display: false }} }},
            scales: {{ y: {{ beginAtZero: true, ticks: {{ stepSize: 1 }} }} }}
        }}
    }});
    </script>
    """
    st.components.v1.html(case_chart_html, height=300)

# Tables row
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-header">⚠️ PROBLEM MODE</div>', unsafe_allow_html=True)
    pm_summary = filtered.groupby("Problem Mode").agg(
        QTY=("Quantity", "sum"),
        CASE=("Problem Mode", "count")
    ).reset_index().sort_values("QTY", ascending=False)

    # Color coding
    def color_coding(case):
        if case == 0:
            return "🟢"
        elif case <= 2:
            return "🟡"
        else:
            return "🔴"

    pm_summary["Status"] = pm_summary["CASE"].apply(color_coding)
    pm_summary["QTY"] = pm_summary["QTY"].apply(lambda x: f"{x:.2f}")
    st.dataframe(
        pm_summary[["Status", "Problem Mode", "QTY", "CASE"]],
        use_container_width=True, hide_index=True,
        column_config={"Status": st.column_config.TextColumn("", width="small")}
    )

with col2:
    st.markdown('<div class="section-header">🏆 TOP 5 SUPPLIERS</div>', unsafe_allow_html=True)
    sup_summary = filtered.groupby("Supplier Name").agg(
        QTY=("Quantity", "sum"),
        CASE=("Supplier Name", "count")
    ).reset_index().sort_values("QTY", ascending=False).head(5)
    sup_summary["QTY"] = sup_summary["QTY"].apply(lambda x: f"{x:.2f}")
    st.dataframe(sup_summary, use_container_width=True, hide_index=True)

# Detail table
st.markdown('<div class="section-header">📋 DETAIL OF SUPPLIER PROBLEM</div>', unsafe_allow_html=True)
detail = filtered[["Date", "Found", "Supplier Name", "Group", "Problem Mode", "Part Name", "Part No", "Quantity"]].copy()
detail["Quantity"] = detail["Quantity"].apply(lambda x: f"{x:.2f}")
st.dataframe(detail, use_container_width=True, hide_index=True, height=400)

# Footer
st.markdown("---")
st.caption("🌐 QA Defects Dashboard | Built with Streamlit | Plan A - Web App Preview")
