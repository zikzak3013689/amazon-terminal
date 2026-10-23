@echo off
TITLE Amazon India Research Terminal - Cloud Edition
COLOR 0B

echo ===============================================================================
echo       AMAZON INDIA PRODUCT RESEARCH TERMINAL - CLOUD EDITION
echo ===============================================================================
echo.
echo Starting Streamlit server and generating secure public HTTPS Cloud link...
echo.

:: Start Streamlit in the background if not already running
start /B python -m streamlit run app.py --server.headless=true --server.port=8501 >nul 2>&1

:: Start Cloudflare Tunnel to expose the terminal to any device globally
echo ===============================================================================
echo Generating your private Cloud HTTPS link...
echo (Open the link below on your phone, iPad, or any laptop from anywhere in the world!)
echo ===============================================================================
echo.

.\cloudflared.exe tunnel --url http://localhost:8501
pause
