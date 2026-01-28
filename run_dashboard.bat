@echo off
REM Premier League xG Analytics - Dashboard Launcher

echo ========================================
echo Premier League xG Analytics
echo Starting Dashboard...
echo ========================================
echo.

REM Check if virtual environment is activated
if not defined VIRTUAL_ENV (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
    echo.
)

echo Starting Streamlit dashboard...
echo Dashboard will open at: http://localhost:8501
echo.
echo Press Ctrl+C to stop the dashboard
echo.

streamlit run dashboard/app.py
