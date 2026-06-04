@echo off
title V-LKG - Leadership Knowledge Graph
cd /d D:\v_lkg_reproduction

echo ========================================
echo    V-LKG - Leadership Knowledge Graph
echo ========================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [1/4] Starting Docker Desktop...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    echo Waiting for Docker to start...
    :wait_docker
    docker info >nul 2>&1
    if %errorlevel% neq 0 (
        timeout /t 3 >nul
        goto wait_docker
    )
)

REM Start Neo4j container
echo [2/4] Checking Neo4j...
docker ps | findstr neo4j >nul
if %errorlevel% neq 0 (
    echo [2/4] Creating Neo4j container...
    docker run -d --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:5.26.0-community >nul 2>&1
)
docker start neo4j >nul 2>&1

REM Wait for Neo4j to be ready
echo [3/4] Waiting for Neo4j to be ready...
:wait_neo4j
curl -s http://localhost:7474 >nul 2>&1
if %errorlevel% neq 0 (
    timeout /t 2 >nul
    goto wait_neo4j
)

REM Run Streamlit app
echo [4/4] Starting V-LKG App...
echo.
echo ========================================
echo    App opening at: http://localhost:8501
echo    Press Ctrl+C to stop
echo ========================================
echo.
python -m streamlit run app.py
