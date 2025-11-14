@echo off
REM Windows batch script to start the dashboard
REM This script activates the virtual environment and starts Streamlit

echo ========================================
echo Starting AI Cost Optimizer Dashboard...
echo ========================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo.
    echo Please run the setup first:
    echo   python setup.py
    echo.
    echo This will automatically:
    echo   - Create virtual environment
    echo   - Install all dependencies
    echo   - Set up configuration files
    echo.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo [WARNING] .env file not found!
    echo.
    echo Please create .env file with your AWS credentials:
    echo   1. Copy .env.example to .env
    echo   2. Edit .env and add your AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
    echo.
    echo Or run setup.py which will create it automatically.
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Check if dependencies are installed
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo [WARNING] Dependencies not installed!
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies!
        pause
        exit /b 1
    )
)

REM Set environment variable to skip Streamlit email prompt
set STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

REM Start Streamlit dashboard
echo.
echo ========================================
echo Starting Streamlit dashboard...
echo ========================================
echo.
echo The dashboard will be available at: http://localhost:8501
echo.
echo Press Ctrl+C to stop the server.
echo.
streamlit run src/dashboard.py

pause

