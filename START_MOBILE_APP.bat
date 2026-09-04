@echo off
title V-LKG Mobile Multi-App Platform
echo ===================================================
echo   Launching V-LKG Mobile Multi-App Platform
echo ===================================================
echo.

echo Starting V-LKG Server on http://localhost:8080 ...
start "V-LKG Mobile Server" cmd /k "cd /d %~dp0 && python -m uvicorn mobile_api.server:app --host 0.0.0.0 --port 8080 --reload"

echo Opening browser at http://localhost:8080 ...
timeout /t 2 /nobreak >nul
start http://localhost:8080

echo.
echo ===================================================
echo   V-LKG Mobile is running!
echo   Mobile App: http://localhost:8080
echo   API Docs:   http://localhost:8080/docs
echo ===================================================
pause
