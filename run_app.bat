@echo off
title V-LKG Leadership Knowledge Graph
color 0A
echo ==========================================
echo    V-LKG Leadership Knowledge Graph
echo ==========================================
echo.
echo Starting Streamlit app...
echo.

cd /d D:\v_lkg_reproduction

:: Check if streamlit is already running
tasklist /FI "IMAGENAME eq python.exe" 2>NUL | find /I /N "python.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo Streamlit is already running!
    echo.
    echo Opening browser...
    start http://localhost:8501
    timeout /t 3 >nul
    exit
)

:: Start Streamlit in background
echo Starting server...
start /B python -m streamlit run app.py --server.headless true

:: Wait for server to start
echo Waiting for server to start...
timeout /t 8 >nul

:: Check if server is running
:check
tasklist /FI "IMAGENAME eq python.exe" 2>NUL | find /I /N "python.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo.
    echo ==========================================
    echo    ✅ App is running!
    echo ==========================================
    echo.
    echo Opening browser...
    start http://localhost:8501
    echo.
    echo Press any key to stop the server...
    pause >nul
    taskkill /F /IM python.exe >nul 2>&1
    echo Server stopped.
) else (
    echo ❌ Failed to start server
    pause
)
