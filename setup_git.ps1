<#
.SYNOPSIS
    Initialize Git repository, make initial commit, and push to GitHub.
.DESCRIPTION
    This script initializes a new Git repository, adds all files, makes an initial commit,
    and pushes to a new GitHub repository.
.PARAMETER RepositoryName
    The name of the GitHub repository (default: handbrakemcp)
.PARAMETER Description
    A short description of the repository
.PARAMETER Private
    Whether the repository should be private (default: $true)
#>
param(
    [string]$RepositoryName = "handbrakemcp",
    [string]$Description = "A FastMCP 2.10-compliant server for video transcoding using HandBrakeCLI",
    [bool]$Private = $true
)

# Stop on first error
$ErrorActionPreference = "Stop"

# Check if Git is installed
try {
    $gitVersion = git --version
    Write-Host "Using Git version: $gitVersion" -ForegroundColor Green
} catch {
    Write-Error "Git is not installed or not in PATH. Please install Git and try again."
    exit 1
}

# Check if GitHub CLI is installed
try {
    $ghVersion = gh --version
    Write-Host "Using GitHub CLI version: $($ghVersion[0])" -ForegroundColor Green
} catch {
    Write-Error "GitHub CLI (gh) is not installed or not in PATH. Please install it from https://cli.github.com/"
    exit 1
}

# Check if already a Git repository
if (Test-Path .git) {
    Write-Host "This directory is already a Git repository." -ForegroundColor Yellow
    exit 0
}

# Initialize Git repository
Write-Host "Initializing Git repository..." -ForegroundColor Cyan
git init

# Create .gitignore if it doesn't exist
if (-not (Test-Path .gitignore)) {
    @"
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/
.venv/

# Environment variables
.env

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# Logs
logs/
*.log

# Local development
*.local

# DXT
*.dxt

# HandBrake
*.log
"@ | Out-File -FilePath .gitignore -Encoding utf8
}

# Add all files to Git
Write-Host "Adding files to Git..." -ForegroundColor Cyan
git add .

# Make initial commit
$commitMessage = "Initial commit: $Description"
Write-Host "Creating initial commit..." -ForegroundColor Cyan
git commit -m $commitMessage

# Create GitHub repository
Write-Host "Creating GitHub repository..." -ForegroundColor Cyan
$privateFlag = if ($Private) { "--private" } else { "--public" }
$createRepoCmd = "gh repo create $RepositoryName --source=. --remote=origin --description=""$Description"" $privateFlag --push"
Invoke-Expression $createRepoCmd

# Set up git branch
git branch -M main

git push -u origin main

Write-Host "" -ForegroundColor Green
Write-Host "✅ Successfully initialized Git repository and pushed to GitHub!" -ForegroundColor Green
Write-Host "" -ForegroundColor Green
Write-Host "Repository URL: https://github.com/$(gh repo view --json nameWithOwner -q '.nameWithOwner')" -ForegroundColor Cyan
Write-Host "" -ForegroundColor Green
