# 3K Battery Co., Ltd. - QA Defects Dashboard

Dashboard สำหรับ **ฝ่าย Incoming Quality** ของ 3K Battery Co., Ltd.
ติดตามและวิเคราะห์ปัญหา defect จาก supplier แบบ real-time

## Features

**3 หน้าหลัก:**
1. **14 Days Defect Monitoring** - Daily defect quantity และ case overview พร้อม trend badges
2. **Searching Supplier Information** - PPM analysis เปรียบเทียบ FY25 vs FY26
3. **Data Entry** - Upload Excel หรือ Manual form + 1-click sync to GitHub

**Key Capabilities:**
- KPI cards พร้อม trend ▲▼ vs 7 วันก่อนหน้า (real calculation, ไม่ใช่ static label)
- Sidebar nav buttons แบบ gradient สีเหลือง/ดำ/ส้ม
- Live data indicator (pulsing green dot)
- Auto-sync ผ่าน GitHub Contents API (ไม่ต้องผ่าน Telegram)
- ใช้ได้ทั้งบน mobile และ desktop

## Tech Stack
- Streamlit (Python web framework)
- Chart.js (charts via CDN, ไม่ต้องติดตั้ง Plotly)
- Pandas (data processing)
- openpyxl (Excel read/write)
- GitHub Contents API (data sync)

## Theme
Yellow & Black (⚡ 3K Battery brand) — primary: #FFD700, secondary: #000

## Files
- `app.py` - Main application (single file, 3 pages via sidebar)
- `QA_Defects_Data.xlsx` - Primary data source (synced from GitHub)
- `QA_Defects_Data.csv` - Backup data source
- `QA_Defects_Template.xlsx` - Template for supplier upload
- `requirements.txt` - Python dependencies
- `assets/3k_logo.jpg` - Company logo

## Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

Default password: stored in `.streamlit/secrets.toml` (local) or Streamlit Cloud Secrets

## Deploy
Push to GitHub main branch → Streamlit Cloud auto-rebuilds (after manual reboot)

## Live URL
https://panuchuwong-cyber-test-defects.streamlit.app

## Changelog
- **2026-09-03**: Sidebar nav converted from radio to gradient buttons; brand updated to 3K Battery; added "Auto-sync from GitHub" subtitle
- **2026-08-31**: Original v1 deploy with TEST branding, password gate, 3 pages

