#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Build MCPB package for HandBrake MCP Server

.DESCRIPTION
    This script builds an MCPB (MCP Bundle) package for the HandBrake MCP Server.
    It validates prerequisites, builds the package, and optionally signs it.

.PARAMETER NoSign
    Skip package signing (for development builds)

.PARAMETER OutputDir
    Custom output directory for the built package (default: dist)

.PARAMETER Version
    Override version number for the build

.EXAMPLE
    # Build without signing (development)
    .\scripts\build-mcpb-package.ps1 -NoSign

    # Build with signing (production)
    .\scripts\build-mcpb-package.ps1

    # Build with custom output directory
    .\scripts\build-mcpb-package.ps1 -OutputDir "C:\builds"
#>

param(
    [switch]$NoSign,
    [string]$OutputDir = "dist",
    [string]$Version
)

# Configuration
$MCPB_PACKAGE_NAME = "handbrake-mcp"
$REQUIRED_NODE_VERSION = "18"
$REQUIRED_PYTHON_VERSION = "3.8"

# Colors for output
$Green = "Green"
$Yellow = "Yellow"
$Red = "Red"
$Cyan = "Cyan"
$White = "White"

function Write-ColoredOutput {
    param(
        [string]$Message,
        [string]$Color = $White,
        [switch]$NoNewline
    )

    if ($NoNewline) {
        Write-Host $Message -ForegroundColor $Color -NoNewline
    } else {
        Write-Host $Message -ForegroundColor $Color
    }
}

function Write-Step {
    param([string]$Message)

    Write-ColoredOutput "==> $Message" $Cyan
}

function Write-Success {
    param([string]$Message)

    Write-ColoredOutput "✅ $Message" $Green
}

function Write-Warning {
    param([string]$Message)

    Write-ColoredOutput "⚠️  $Message" $Yellow
}

function Write-Error {
    param([string]$Message)

    Write-ColoredOutput "❌ $Message" $Red
}

function Test-Prerequisites {
    Write-Step "Checking prerequisites..."

    # Check Node.js
    try {
        $nodeVersion = & node --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            $nodeVersionNumber = $nodeVersion -replace '^v', ''
            Write-Success "Node.js: $nodeVersion"
        } else {
            Write-Error "Node.js not found. Please install Node.js $REQUIRED_NODE_VERSION or later."
            exit 1
        }
    } catch {
        Write-Error "Node.js not found. Please install Node.js $REQUIRED_NODE_VERSION or later."
        exit 1
    }

    # Check Python
    try {
        $pythonVersion = & python --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            $pythonVersionNumber = ($pythonVersion -split ' ')[1]
            Write-Success "Python: $pythonVersion"
        } else {
            Write-Error "Python not found. Please install Python $REQUIRED_PYTHON_VERSION or later."
            exit 1
        }
    } catch {
        Write-Error "Python not found. Please install Python $REQUIRED_PYTHON_VERSION or later."
        exit 1
    }

    # Check MCPB CLI
    try {
        $mcpbVersion = & mcpb --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "MCPB CLI: $mcpbVersion"
        } else {
            Write-Error "MCPB CLI not found. Installing..."
            & npm install -g @anthropic-ai/mcpb
            if ($LASTEXITCODE -ne 0) {
                Write-Error "Failed to install MCPB CLI"
                exit 1
            }
            Write-Success "MCPB CLI installed successfully"
        }
    } catch {
        Write-Error "MCPB CLI not found. Installing..."
        & npm install -g @anthropic-ai/mcpb
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to install MCPB CLI"
            exit 1
        }
        Write-Success "MCPB CLI installed successfully"
    }

    # Check for manifest.json
    if (!(Test-Path "mcpb/manifest.json")) {
        Write-Error "mcpb/manifest.json not found"
        exit 1
    }
    Write-Success "mcpb/manifest.json found"

    # Check for mcpb.json
    if (!(Test-Path "mcpb/mcpb.json")) {
        Write-Error "mcpb/mcpb.json not found"
        exit 1
    }
    Write-Success "mcpb/mcpb.json found"

    Write-Success "All prerequisites satisfied"
}

function Validate-Manifest {
    Write-Step "Validating mcpb/manifest.json..."

    try {
        & mcpb validate mcpb/manifest.json
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Manifest validation passed"
        } else {
            Write-Error "Manifest validation failed"
            exit 1
        }
    } catch {
        Write-Error "Failed to validate manifest: $_"
        exit 1
    }
}

function Install-Dependencies {
    Write-Step "Installing Python dependencies..."

    try {
        # Check if requirements.txt exists
        if (!(Test-Path "requirements.txt")) {
            Write-Error "requirements.txt not found"
            exit 1
        }

        # Install dependencies
        & python -m pip install --upgrade pip
        & python -m pip install -r requirements.txt

        if ($LASTEXITCODE -eq 0) {
            Write-Success "Python dependencies installed"
        } else {
            Write-Error "Failed to install Python dependencies"
            exit 1
        }
    } catch {
        Write-Error "Failed to install dependencies: $_"
        exit 1
    }
}

function Build-Package {
    Write-Step "Building MCPB package..."

    # Create output directory
    if (!(Test-Path $OutputDir)) {
        New-Item -ItemType Directory -Path $OutputDir | Out-Null
    }

    # Set version if provided
    $buildArgs = @()
    if ($Version) {
        $buildArgs += "--version", $Version
    }

    try {
        # Build the package
        $packageName = "handbrake-mcp.mcpb"
        $packagePath = Join-Path $OutputDir $packageName
        & mcpb pack . $packagePath @buildArgs

        if ($LASTEXITCODE -eq 0) {
            Write-Success "MCPB package built successfully"
        } else {
            Write-Error "Failed to build MCPB package"
            exit 1
        }
    } catch {
        Write-Error "Failed to build package: $_"
        exit 1
    }
}

function Sign-Package {
    param([string]$PackagePath)

    if ($NoSign) {
        Write-Warning "Skipping package signing (--NoSign specified)"
        return
    }

    Write-Step "Signing MCPB package..."

    # Check if signing key exists (you would set this up separately)
    $signingKey = $env:MCPB_SIGNING_KEY
    if (!$signingKey) {
        Write-Warning "No signing key found. Set MCPB_SIGNING_KEY environment variable for signing."
        Write-Warning "Building unsigned package (suitable for development/testing)"
        return
    }

    try {
        # Create temporary key file
        $keyFile = [System.IO.Path]::GetTempFileName()
        $signingKey | Out-File -FilePath $keyFile -Encoding ASCII

        & mcpb sign --key $keyFile $PackagePath

        # Clean up
        Remove-Item $keyFile -Force

        if ($LASTEXITCODE -eq 0) {
            Write-Success "Package signed successfully"
        } else {
            Write-Warning "Failed to sign package. Package built but not signed."
        }
    } catch {
        Write-Warning "Failed to sign package: $_. Package built but not signed."
    }
}

function Verify-Package {
    param([string]$PackagePath)

    Write-Step "Verifying MCPB package..."

    try {
        $packageInfo = Get-Item $PackagePath
        $packageSize = [math]::Round($packageInfo.Length / 1MB, 2)

        Write-Success "Package: $($packageInfo.Name)"
        Write-Success "Size: $packageSize MB"
        Write-Success "Location: $($packageInfo.FullName)"

        # Verify package integrity
        & mcpb verify $PackagePath
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Package verification passed"
        } else {
            Write-Warning "Package verification failed"
        }

    } catch {
        Write-Error "Failed to verify package: $_"
        exit 1
    }
}

function Show-Usage {
    Write-ColoredOutput @"
HandBrake MCP MCPB Package Builder

USAGE:
    .\scripts\build-mcpb-package.ps1 [OPTIONS]

OPTIONS:
    -NoSign           Skip package signing (development builds)
    -OutputDir <dir>  Custom output directory (default: dist)
    -Version <ver>    Override version number
    -Help             Show this help message

EXAMPLES:
    .\scripts\build-mcpb-package.ps1 -NoSign
    .\scripts\build-mcpb-package.ps1 -OutputDir "C:\builds"
    .\scripts\build-mcpb-package.ps1 -Version "1.0.0"

"@ $White
}

# Main script execution
function Main {
    # Show banner
    Write-ColoredOutput @"

╔══════════════════════════════════════════════════════════════╗
║                 HandBrake MCP - MCPB Builder                 ║
║                   Professional Video Transcoding             ║
╚══════════════════════════════════════════════════════════════╝

"@ $Cyan

    # Parse arguments
    if ($args -contains "-Help" -or $args -contains "--help" -or $args -contains "-h") {
        Show-Usage
        exit 0
    }

    # Check prerequisites
    Test-Prerequisites

    # Validate manifest
    Validate-Manifest

    # Install dependencies
    Install-Dependencies

    # Build package
    Build-Package

    # Find the built package
    $packagePath = Get-ChildItem -Path $OutputDir -Filter "*.mcpb" | Select-Object -First 1
    if (!$packagePath) {
        Write-Error "Built package not found in $OutputDir"
        exit 1
    }

    # Sign package (if requested)
    Sign-Package -PackagePath $packagePath.FullName

    # Verify package
    Verify-Package -PackagePath $packagePath.FullName

    # Show success message
    Write-ColoredOutput @"

╔══════════════════════════════════════════════════════════════╗
║                      BUILD COMPLETE!                        ║
╚══════════════════════════════════════════════════════════════╝

Package: $($packagePath.Name)
Location: $($packagePath.FullName)
Size: $([math]::Round($packagePath.Length / 1MB, 2)) MB

🎯 Ready for distribution!

Next steps:
1. Test installation: Drag package to Claude Desktop
2. Verify configuration prompts work
3. Test video transcoding tools
4. Share with users or publish to registry

📦 Happy transcoding!

"@ $Green
}

# Run main function
Main
