#!/bin/bash
# Premier League xG Analytics - Quick Extraction Script
# This script extracts all data except shots (which takes longer)

echo "========================================"
echo "Premier League xG Analytics"
echo "Quick Data Extraction"
echo "========================================"
echo ""

# Check if virtual environment exists and activate it
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
    echo ""
fi

echo "[1/3] Extracting team data..."
python -m extract.extract_league
echo ""

echo "[2/3] Extracting player data..."
python -m extract.extract_players
echo ""

echo "[3/3] Extracting match data..."
python -m extract.extract_matches
echo ""

echo "========================================"
echo "Extraction complete!"
echo "========================================"
echo ""
echo "To extract shot data (takes 5-10 min):"
echo "  python -m extract.extract_shots"
echo ""
echo "To start the dashboard:"
echo "  streamlit run dashboard/app.py"
echo ""
