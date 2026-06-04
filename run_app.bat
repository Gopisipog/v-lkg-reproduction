@echo off
echo Starting V-LKG Application...
echo.

REM Start Docker Desktop if not running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo Starting Docker Desktop...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    echo Waiting for Docker to start...
    :wait_docker
    docker info >nul 2>&1
    if %errorlevel% neq 0 (
        timeout /t 2 >nul
        goto wait_docker
    )
)

REM Start Neo4j if not running
docker ps | findstr neo4j >nul
if %errorlevel% neq 0 (
    echo Starting Neo4j container...
    docker start neo4j
)

REM Wait for Neo4j to be ready
echo Waiting for Neo4j to be ready...
:wait_neo4j
curl -s http://localhost:7474 >nul 2>&1
if %errorlevel% neq 0 (
    timeout /t 2 >nul
    goto wait_neo4j
)
echo Neo4j is ready!

REM Run Streamlit app
echo.
echo Starting Streamlit app...
echo.
cd /d "%~dp0"
python -m streamlit run app.py
