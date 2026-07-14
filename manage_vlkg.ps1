param(
    [ValidateSet("start","stop","restart","status","logs")]
    [string]$Action = "status"
)

$AppDir = Split-Path -Parent $PSCommandPath
$Port   = 9999
$LogDir = Join-Path $AppDir "logs"
$PidFile= Join-Path $LogDir "streamlit.pid"
$LogFile= Join-Path $LogDir "streamlit.log"
$ErrFile= Join-Path $LogDir "streamlit.err"

if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir -Force | Out-Null }

function Get-AppPid {
    if (Test-Path $PidFile) {
        $appPid = Get-Content $PidFile -Raw | ForEach-Object { $_.Trim() }
        if ($appPid -and (Get-Process -Id $appPid -ErrorAction SilentlyContinue)) { return $appPid }
        Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
    }
    return $null
}

function Write-Status {
    $appPid = Get-AppPid
    if ($appPid) {
        $proc = Get-Process -Id $appPid
        $resp = $null
        try { $resp = Invoke-WebRequest -Uri "http://localhost:$Port" -TimeoutSec 5 -UseBasicParsing; $ok = $resp.StatusCode -eq 200 }
        catch { $ok = $false }
        $elapsed = [math]::Round(((Get-Date) - $proc.StartTime).TotalMinutes)
        Write-Host "V-LKG App: RUNNING (PID $appPid, running for ${elapsed} min)" -ForegroundColor Green
        if ($ok) { Write-Host "Health:     OK (HTTP $($resp.StatusCode))" -ForegroundColor Green } else { Write-Host "Health:     WARN (not responding yet)" -ForegroundColor Yellow }
    } else {
        Write-Host "V-LKG App: STOPPED" -ForegroundColor Red
    }
}

switch ($Action) {
    "start" {
        $appPid = Get-AppPid
        if ($appPid) { Write-Host "Already running (PID $appPid). Use restart or stop first." -ForegroundColor Yellow; exit 1 }
        Write-Host "Starting V-LKG on port $Port ..." -ForegroundColor Cyan
        $logHeader = "="*60 + "`nV-LKG App started at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n" + "="*60
        $logHeader | Out-File $LogFile -Encoding utf8
        $logHeader | Out-File $ErrFile -Encoding utf8
        $proc = Start-Process -FilePath "python" -ArgumentList "-m streamlit run $AppDir\app.py --server.port $Port --server.headless True" -WorkingDirectory $AppDir -NoNewWindow -RedirectStandardOutput $LogFile -RedirectStandardError $ErrFile -PassThru
        $proc.Id | Out-File $PidFile -Encoding ascii
        Write-Host "Started (PID $($proc.Id)). Logs: $LogFile" -ForegroundColor Green
        Write-Host "Waiting for health check..."
        $ok = $false
        for ($i=0; $i -lt 30; $i++) {
            Start-Sleep 2
            try { Invoke-WebRequest -Uri "http://localhost:$Port" -TimeoutSec 3 -UseBasicParsing | Out-Null; $ok = $true; break }
            catch { }
        }
        if ($ok) { Write-Host "App is ready at http://localhost:$Port" -ForegroundColor Green }
        else { Write-Host "App started but not yet responding. Check logs: $LogFile" -ForegroundColor Yellow }
    }
    "stop" {
        $appPid = Get-AppPid
        if (-not $appPid) { Write-Host "Not running." -ForegroundColor Yellow; exit 0 }
        taskkill /F /PID $appPid 2>$null
        Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
        Write-Host "Stopped (PID $appPid)." -ForegroundColor Green
    }
    "restart" {
        & $PSCommandPath stop
        Start-Sleep 2
        & $PSCommandPath start
    }
    "status" { Write-Status }
    "logs" {
        if (Test-Path $LogFile) { Get-Content $LogFile -Tail 50 }
        else { Write-Host "No logs yet." -ForegroundColor Yellow }
    }
}
