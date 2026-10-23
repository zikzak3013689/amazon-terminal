@echo off
TITLE Amazon India Product Research Terminal
COLOR 0B

echo ===============================================================================
echo       AMAZON INDIA PRODUCT RESEARCH & OPPORTUNITY INTELLIGENCE TERMINAL
echo ===============================================================================
echo.
echo Market: Amazon India (amazon.in) ^| Currency: INR (INR)
echo Starting local terminal environment...
echo.

:: Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not added to your system PATH.
    echo Please install Python 3.12+ from python.org and check "Add Python to PATH".
    pause
    exit /b
)

:: Verify dependencies
echo [1/2] Verifying Python dependencies...
python -m pip install -r requirements.txt --quiet --disable-pip-version-check

echo [2/2] Launching Streamlit Research Terminal...
echo.
echo The terminal interface will open automatically in your default browser.
echo Press Ctrl+C in this command window to stop the terminal.
echo ===============================================================================

python -m streamlit run app.py --server.port 8501 --server.headless false

pause
