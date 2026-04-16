# Webapp Start - Standardized SOTA v13.1
$WebPort = 10874
$BackendPort = 10875
$ProjectRoot = Split-Path -Parent $PSScriptRoot

# 1. Kill any process squatting on the ports
Write-Host "Checking for port squatters on $WebPort and $BackendPort..." -ForegroundColor Yellow
$pids = Get-NetTCPConnection -LocalPort $WebPort, $BackendPort -ErrorAction SilentlyContinue | Where-Object { $_.OwningProcess -gt 4 } | Select-Object -ExpandProperty OwningProcess -Unique
foreach ($p in $pids) {
    Write-Host "Found squatter (PID: $p). Terminating..." -ForegroundColor Red
    try { Stop-Process -Id $p -Force -ErrorAction Stop } catch { Write-Host "Warning: Could not terminate PID $p." -ForegroundColor Gray }
}

# 2. Setup
Set-Location $PSScriptRoot
if (-not (Test-Path "node_modules")) { 
    Write-Host "node_modules missing. Installing dependencies..." -ForegroundColor Gray
    npm install 
}

# 3. Start the Python backend (Background)
Write-Host "Starting Python backend on http://127.0.0.1:$BackendPort ..." -ForegroundColor Cyan
$backendCmd = "`$env:PYTHONPATH = '$ProjectRoot\src'; Set-Location '$ProjectRoot'; uv run python -m handbrake_mcp.server --http --port $BackendPort --log-level info"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WindowStyle Normal

# 4. Wait for Backend to be ready
Write-Host "Waiting for backend telemetry sync..." -ForegroundColor Gray
$backendUrl = "http://127.0.0.1:$BackendPort/health"
for ($i = 0; $i -lt 30; $i++) {
    try {
        $resp = Invoke-WebRequest -Uri $backendUrl -TimeoutSec 1 -UseBasicParsing -ErrorAction Stop
        if ($resp.StatusCode -eq 200) { 
            Write-Host "Backend Online." -ForegroundColor Emerald
            break 
        }
    } catch {
        Write-Host "." -NoNewline -ForegroundColor Gray
        Start-Sleep -Seconds 1
    }
}

# 5. Start Vite frontend
Write-Host "`nStarting Vite frontend on port $WebPort ..." -ForegroundColor Green
$frontendUrl = "http://127.0.0.1:$WebPort/"
$pollAndOpen = "for (`$i = 0; `$i -lt 60; `$i++) { try { `$null = Invoke-WebRequest -Uri '$frontendUrl' -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop; Start-Process '$frontendUrl'; exit } catch { Start-Sleep -Seconds 1 } }"
Start-Process powershell -ArgumentList "-NoProfile", "-WindowStyle", "Hidden", "-Command", $pollAndOpen

Write-Host "Browser will open automatically when Vite is ready." -ForegroundColor Gray
npm run dev -- --port $WebPort --host

