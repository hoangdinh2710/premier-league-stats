#!/bin/bash
# Premier League xG Analytics - Dashboard Launcher

echo "========================================"
echo "Premier League xG Analytics"
echo "Starting Dashboard..."
echo "========================================"
echo ""

# Check if virtual environment exists and activate it
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
    echo ""
fi

echo "Starting Streamlit dashboard..."
echo "Dashboard will open at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the dashboard"
echo ""

streamlit run dashboard/app.py
