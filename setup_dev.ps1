<#
.SYNOPSIS
    Setup development environment for HandBrake MCP server.
.DESCRIPTION
    This script sets up a Python virtual environment and installs the required dependencies.
    It also installs the package in development mode.
#>

# Stop on first error
$ErrorActionPreference = "Stop"

# Check if Python is installed
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "Python is not installed or not in PATH. Please install Python 3.8 or later and try again."
    exit 1
}

Write-Host "Setting up development environment for HandBrake MCP server..." -ForegroundColor Green

# Create and activate virtual environment
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    python -m venv venv
}

# Activate the virtual environment
$activateScript = ".\venv\Scripts\Activate.ps1"
if (-not (Test-Path $activateScript)) {
    $activateScript = "./venv/bin/Activate.ps1"
}

Write-Host "Activating virtual environment..." -ForegroundColor Cyan
. $activateScript

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Cyan
python -m pip install --upgrade pip

# Install development dependencies
Write-Host "Installing development dependencies..." -ForegroundColor Cyan
pip install -r requirements-dev.txt

# Install package in development mode
Write-Host "Installing package in development mode..." -ForegroundColor Cyan
pip install -e .

Write-Host "`nDevelopment environment setup complete!`n" -ForegroundColor Green
Write-Host "To activate the virtual environment, run:" -ForegroundColor Yellow
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "`nTo start the development server, run:" -ForegroundColor Yellow
Write-Host "  uvicorn handbrake_mcp.main:app --reload" -ForegroundColor White
Write-Host "`nTo run tests, use:" -ForegroundColor Yellow
Write-Host "  pytest tests/" -ForegroundColor White
