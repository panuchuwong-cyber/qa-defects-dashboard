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
- **2026-09-09**: Added Found + Severity columns (schema v2, 10 columns). Severity-based scoring replaces CASE/REJECT keyword detection. New sidebar filters for Found Stage + Severity. Data Entry form updated with Found Stage + Severity dropdowns. Template regenerated with data validation dropdowns.
- **2026-09-03**: Sidebar nav converted from radio to gradient buttons; brand updated to 3K Battery; added "Auto-sync from GitHub" subtitle
- **2026-08-31**: Original v1 deploy with TEST branding, password gate, 3 pages

## Data Schema (v2 — 10 columns)

QA_Defects_Data.xlsx uses this schema. **All 10 columns required** for new records.

| Column | Type | Required | Description |
|---|---|---|---|
| Date | date (YYYY-MM-DD) | YES | Date defect was found/reported |
| Found | string | YES | Inspection stage — see below |
| Supplier | string | YES | Supplier code (must match supplier_master.csv) |
| Group Part | string | YES | Material group (dropdown in template) |
| Problem Mode | string | YES | Defect type (dropdown in template) |
| Part Name | string | YES | Human-readable part name |
| Part No | string | YES | Part number / drawing number |
| Qty | int > 0 | YES | Defective quantity (pieces) |
| Severity | string | YES | CRITICAL / MAJOR / MINOR — see below |
| Comment | string | optional | Free text describing the defect (Thai or English) |

### Found Stage (Inspection Point)

- **IN LINE** = detected during production (in-line QC)
- **FINAL** = detected at final inspection before shipping
- **INCOMING** = detected at goods receiving (from supplier)
- **OQA** = detected at outgoing quality audit
- **CUSTOMER** = detected at customer site (field failure)

### Severity Guide

- **CRITICAL** (weight 1.0): lot reject / safety issue / line stop / customer return
- **MAJOR** (weight 0.5): dimension out of spec / wrong part shipped / function failure
- **MINOR** (weight 0.1): appearance (scratch, color, surface defect) / cosmetic

### Scoring Impact

Worst Supplier Score formula: `Score = (0.45 × Case_norm) + (0.35 × Qty_norm) + (0.20 × Frequency_norm)` × 100

Where **Case = count of rows with Severity >= MAJOR** (i.e., CRITICAL or MAJOR).
MINOR defects count toward Qty but not toward Case.

### Backfill for Old Data

When loading older xlsx files without these columns, dashboard will:
- Treat missing Found/Severity as empty (no filter applied)
- Fall back to CASE/REJECT keyword detection for Case count
- Show warning if Severity column missing

