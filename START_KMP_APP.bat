@echo off
title V-LKG Mobile - Compose Multiplatform
echo ===================================================
echo   Launching V-LKG Mobile (Compose Multiplatform)
echo ===================================================
echo.
cd /d "%~dp0"
set "JAVA_HOME=%~dp0.jdk\jdk-17.0.20.1+1"
set "PATH=%JAVA_HOME%\bin;%PATH%"

echo Starting Compose Multiplatform interactive window...
call gradlew.bat :composeApp:run
pause