@echo off
:: V-LKG One-Click Launcher
:: Double-click this file to start the app

title V-LKG Leadership Knowledge Graph
cd /d D:\v_lkg_reproduction

:: Kill any existing python processes (clean start)
taskkill /F /IM python.exe >nul 2>&1

:: Start Streamlit
echo Starting V-LKG App...
start /B python -m streamlit run app.py --server.headless true

:: Wait for server to start
timeout /t 6 >nul

:: Open browser
start http://localhost:8501

:: Show status
echo.
echo ==========================================
echo    V-LKG App is running!
echo ==========================================
echo.
echo   Local:  http://localhost:8501
echo.
echo   Press any key to stop...
pause >nul

:: Stop server
taskkill /F /IM python.exe >nul 2>&1
