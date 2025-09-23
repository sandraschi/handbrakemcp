# PowerShell script to activate DXT virtual environment

param(
    [switch]$Create,
    [switch]$Install,
    [switch]$Help
)

if ($Help) {
    Write-Host "DXT Virtual Environment Management Script" -ForegroundColor Green
    Write-Host ""
    Write-Host "Usage: .\activate-venv.ps1 [options]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Create    Create the virtual environment (if it doesn't exist)"
    Write-Host "  -Install   Install dependencies from requirements-dxt.txt"
    Write-Host "  -Help      Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\activate-venv.ps1 -Create -Install  # Create venv and install deps"
    Write-Host "  .\activate-venv.ps1                   # Activate existing venv"
    return
}

$venvPath = ".\venv"
$requirementsPath = ".\requirements-dxt.txt"

if ($Create) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    if (Test-Path $venvPath) {
        Write-Host "Virtual environment already exists. Removing..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force $venvPath
    }

    python -m venv $venvPath
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
    Write-Host "Virtual environment created successfully" -ForegroundColor Green
}

if ($Install) {
    if (-not (Test-Path $venvPath)) {
        Write-Host "Virtual environment does not exist. Creating..." -ForegroundColor Yellow
        python -m venv $venvPath
    }

    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    & "$venvPath\Scripts\python.exe" -m pip install --upgrade pip
    & "$venvPath\Scripts\python.exe" -m pip install -r $requirementsPath
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
    Write-Host "Dependencies installed successfully" -ForegroundColor Green
}

# Activate the virtual environment
if (Test-Path $venvPath) {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & "$venvPath\Scripts\Activate.ps1"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to activate virtual environment" -ForegroundColor Red
        exit 1
    }
    Write-Host "Virtual environment activated" -ForegroundColor Green
    Write-Host "You can now run: python dxt/scripts/build.py" -ForegroundColor Cyan
} else {
    Write-Host "Virtual environment does not exist. Run with -Create flag first." -ForegroundColor Red
}
