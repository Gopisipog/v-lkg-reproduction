@echo off
title V-LKG Launcher - Setup & Run
cd /d "%~dp0"

echo =============================================
echo    V-LKG - Leadership Knowledge Graph
echo    Local Setup & Launcher
echo =============================================
echo.

REM ── Step 1: Check Python ────────────────────────────────────────────
echo [1/6] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo     Python not found! Downloading Python 3.11...
    echo     Downloading from python.org...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile '%TEMP%\python_installer.exe'"
    echo     Installing Python (check "Add Python to PATH")...
    start /wait "" "%TEMP%\python_installer.exe" /quiet InstallAllUsers=1 PrependPath=1
    echo     Python installed. Restart this script to continue.
    pause
    exit /b
)
echo     Python found: 
python --version

REM ── Step 2: Ensure pip is up to date ────────────────────────────────
echo [2/6] Upgrading pip...
python -m pip install --upgrade pip --quiet

REM ── Step 3: Pull latest code from GitHub ────────────────────────────
echo [3/6] Checking for latest code...
if exist ".git" (
    echo     Updating existing repository...
    git pull --ff-only --quiet
    if %errorlevel% neq 0 (
        echo     Warning: Could not update. Using local files.
    )
) else (
    echo     Downloading V-LKG from GitHub...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/Gopisipog/v-lkg-reproduction/archive/refs/heads/main.zip' -OutFile '%TEMP%\vlkg.zip'"
    powershell -Command "Expand-Archive -Path '%TEMP%\vlkg.zip' -DestinationPath '%TEMP%' -Force"
    xcopy /E /Y /Q "%TEMP%\v-lkg-reproduction-main\*" "%~dp0" >nul 2>&1
    echo     Downloaded successfully.
)

REM ── Step 4: Create virtual environment ──────────────────────────────
echo [4/6] Setting up virtual environment...
if not exist "venv" (
    python -m venv venv
    echo     Virtual environment created.
)
call venv\Scripts\activate.bat

REM ── Step 5: Install dependencies ────────────────────────────────────
echo [5/6] Installing dependencies (this may take 5-10 minutes first time)...
echo     Installing PyTorch, Whisper, sentence-transformers...
pip install -r requirements.txt --quiet 2>&1 | findstr /V "already satisfied"
echo     Dependencies installed.

REM ── Step 6: Create .env if missing ──────────────────────────────────
if not exist ".env" (
    echo [6/6] Creating .env file...
    echo.
    echo =============================================
    echo    CONFIGURATION
    echo =============================================
    set /p NEO4J_URI="Enter Neo4j URI (default: bolt://localhost:7687): "
    if "%NEO4J_URI%"=="" set NEO4J_URI=bolt://localhost:7687
    set /p NEO4J_USER="Enter Neo4j Username (default: neo4j): "
    if "%NEO4J_USER%"=="" set NEO4J_USER=neo4j
    set /p NEO4J_PASSWORD="Enter Neo4j Password (default: password): "
    if "%NEO4J_PASSWORD%"=="" set NEO4J_PASSWORD=password
    set /p OPENAI_API_KEY="Enter OpenAI API Key: "
    set /p DEEPSEEK_API_KEY="Enter DeepSeek API Key: "
    
    (
        echo OPENAI_API_KEY=%OPENAI_API_KEY%
        echo DEEPSEEK_API_KEY=%DEEPSEEK_API_KEY%
        echo NEO4J_URI=%NEO4J_URI%
        echo NEO4J_USER=%NEO4J_USER%
        echo NEO4J_PASSWORD=%NEO4J_PASSWORD%
    ) > .env
    echo     .env file created.
    echo.
) else (
    echo [6/6] .env file found - skipping configuration.
)

REM ── Launch App ──────────────────────────────────────────────────────
echo.
echo =============================================
echo    Launching V-LKG App...
echo    Local URL: http://localhost:8501
echo    Network URL: http://%COMPUTERNAME%:8501
echo.
echo    Press Ctrl+C to stop
echo =============================================
echo.
python -m streamlit run app.py
pause
