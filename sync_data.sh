#!/bin/bash
# ============================================================
# QA Defects Dashboard — Data Sync Script
# ============================================================
# Usage: ./sync_data.sh
#
# What it does:
#   1. Locates QA_Defects_Data.xlsx in repo
#   2. Validates Excel structure (no missing required columns)
#   3. Commits + pushes to GitHub
#   4. Streamlit Cloud auto-rebuilds (1-2 min)
# ============================================================

set -e  # Exit on any error

REPO_DIR="$HOME/Desktop/Kanom/QA_Defects_Dashboard"
EXCEL_FILE="$REPO_DIR/data/QA_Defects_Data.xlsx"

# Colors for terminal output
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo "${YELLOW}⚡ 3K BATTERY — QA Defects Dashboard Sync${NC}"
echo "================================================"
echo ""

# Step 1: Check repo exists
if [ ! -d "$REPO_DIR" ]; then
    echo "${RED}� Repo not found: $REPO_DIR${NC}"
    echo "   Make sure you've cloned the GitHub repo to this location."
    exit 1
fi

cd "$REPO_DIR"

# Step 2: Check Excel file exists
if [ ! -f "$EXCEL_FILE" ]; then
    echo "${RED}❌ Excel file not found: $EXCEL_FILE${NC}"
    echo "   Make sure QA_Defects_Data.xlsx is in the data/ folder."
    exit 1
fi

# Step 3: Validate Excel structure
echo "🔍 Validating Excel structure..."
python3 -c "
import pandas as pd
import sys
try:
    df = pd.read_excel('$EXCEL_FILE')
    required = ['Date', 'Supplier', 'Group Part', 'Problem Mode', 'Part No', 'Qty']
    missing = [c for c in required if c not in df.columns]
    if missing:
        print(f'Missing columns: {missing}')
        sys.exit(1)
    print(f'✅ Valid — {len(df)} records, {df[\"Supplier\"].nunique()} suppliers')
except Exception as e:
    print(f'❌ Error: {e}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo "${RED}� Excel validation failed. Aborting sync.${NC}"
    exit 1
fi

# Step 4: Git commit + push
echo ""
echo "📤 Committing to Git..."
git add data/QA_Defects_Data.xlsx

# Check if there are changes to commit
if git diff --cached --quiet; then
    echo "${YELLOW}ℹ️  No changes detected. Nothing to sync.${NC}"
    exit 0
fi

# Get timestamp for commit message
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
RECORD_COUNT=$(python3 -c "import pandas as pd; print(len(pd.read_excel('$EXCEL_FILE')))")

git commit -m "DATA sync: ${RECORD_COUNT} records — ${TIMESTAMP}"

echo ""
echo "🚀 Pushing to GitHub..."
if git push origin main; then
    echo ""
    echo "${GREEN}✅ Sync successful!${NC}"
    echo ""
    echo "📊 Dashboard will update in 1-2 minutes at:"
    echo "   https://defects-test.streamlit.app"
    echo ""
else
    echo ""
    echo "${RED}❌ Push failed. Check your GitHub authentication.${NC}"
    exit 1
fi
