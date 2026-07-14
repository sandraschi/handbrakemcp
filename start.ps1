Param([switch]$Headless)
$SkipFrontend = $Headless

# --- SOTA Headless Standard ---
if ($Headless -and ($Host.UI.RawUI.WindowTitle -notmatch 'Hidden')) {
    Start-Process pwsh -ArgumentList '-NoProfile', '-File', $PSCommandPath, '-Headless' -WindowStyle Hidden
    exit
}
$WindowStyle = if ($Headless) { 'Hidden' } else { 'Normal' }
# ------------------------------

$env:FASTMCP_LOG_LEVEL = 'WARNING'
$BackendPort = 10875
$WebPort = 10874

Write-Host 'Starting handbrake-mcp...' -ForegroundColor Cyan
Set-Location $PSScriptRoot

# Kill port zombies
Get-NetTCPConnection -LocalPort $BackendPort, $WebPort -ErrorAction SilentlyContinue |
    ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }

# Start backend in HTTP mode
Write-Host 'Starting backend (HTTP mode)...' -ForegroundColor Green
$backendJob = Start-Job -Name "backend" -ScriptBlock {
    param($Root, $Port)
    Set-Location $Root
    uv run python -m handbrake_mcp.server --http --port $Port --log-level info
} -ArgumentList $PSScriptRoot, $BackendPort

# Wait for backend readiness
Write-Host 'Waiting for backend...' -ForegroundColor Gray
for ($i = 0; $i -lt 30; $i++) {
    try {
        $resp = Invoke-WebRequest -Uri "http://127.0.0.1:$BackendPort/health" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
        if ($resp.StatusCode -eq 200) { Write-Host 'Backend online.' -ForegroundColor Green; break }
    } catch { Start-Sleep -Seconds 1 }
}

# Start frontend
if (-not $SkipFrontend) {
    Set-Location web_sota
    Write-Host 'Starting frontend...' -ForegroundColor Green
    Start-Process pwsh -ArgumentList '-NoProfile', '-Command', "npm run dev -- --port $WebPort --host; pause" -WindowStyle $WindowStyle
    Start-Sleep 3
    Start-Process "http://127.0.0.1:$WebPort"
}

Set-Location $PSScriptRoot

# Keep-alive
while ($true) {
    if ($backendJob.State -eq "Completed" -or $backendJob.State -eq "Failed") {
        Receive-Job $backendJob; break
    }
    Start-Sleep 2
}
