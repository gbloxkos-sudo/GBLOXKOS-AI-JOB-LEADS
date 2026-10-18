<#>
.SYNOPSIS
    Build Windows standalone executable for Job Lead Finder

.DESCRIPTION
    Creates a portable .exe using PyInstaller with embedded Python.
    Run this on Windows (or via Wine/CI) to produce JobLeadFinder.exe

.NOTES
    Requires: Python 3.11+, PyInstaller, project dependencies
    Output: dist/JobLeadFinder/JobLeadFinder.exe (portable folder)
            dist/JobLeadFinder.exe (single-file, slower startup)
#>

param(
    [string]$ProjectRoot = "$PSScriptRoot\..\job-lead-finder-0.14.16",
    [string]$OutDir = "$PSScriptRoot\dist-win",
    [switch]$SingleFile
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "=== Building GBLOXKOS AI JOB LEADS for Windows ===" -ForegroundColor Cyan

# 1. Clean
if (Test-Path $OutDir) { Remove-Item $OutDir -Recurse -Force }
New-Item -ItemType Directory -Path $OutDir | Out-Null

# 2. Create venv
Write-Host "[1/5] Creating virtual environment..." -ForegroundColor Yellow
python -m venv "$OutDir\venv"
& "$OutDir\venv\Scripts\Activate.ps1"
python -m pip install --upgrade pip setuptools wheel

# 3. Install deps
Write-Host "[2/5] Installing dependencies..." -ForegroundColor Yellow
cd $ProjectRoot
pip install -e ".[web]"
pip install pyinstaller

# 4. Build with PyInstaller
Write-Host "[3/5] Building executable..." -ForegroundColor Yellow
$specArgs = @(
    "--clean", "--noconfirm"
    "--name", "GBLOXKOS-AI-JOB-LEADS"
    "--add-data", "src/app/templates;app/templates"
    "--add-data", "src/app;app"
    "--hidden-import", "app.ui_server"
    "--hidden-import", "app.job_finder"
    "--hidden-import", "app.ollama_provider"
    "--hidden-import", "app.gemini_provider"
    "--hidden-import", "app.mcp_providers"
    "--hidden-import", "app.background_scheduler"
    "--hidden-import", "app.job_tracker"
    "--hidden-import", "app.config_manager"
    "--hidden-import", "app.email_sender"
    "--hidden-import", "app.desktop"
    "--hidden-import", "fastapi"
    "--hidden-import", "uvicorn"
    "--hidden-import", "pydantic"
    "--hidden-import", "httpx"
    "--hidden-import", "apscheduler"
    "--hidden-import", "python_dotenv"
    "--hidden-import", "bs4"
    "--hidden-import", "pypdf"
    "--hidden-import", "docx"
    "--hidden-import", "defusedxml"
    "--collect-all", "app"
)

if ($SingleFile) {
    $specArgs += "--onefile"
}

pyinstaller @specArgs "src/app/desktop.py"

# 5. Copy to output
Write-Host "[4/5] Preparing distribution..." -ForegroundColor Yellow
if ($SingleFile) {
    Copy-Item "$ProjectRoot\dist\GBLOXKOS-AI-JOB-LEADS.exe" "$OutDir\GBLOXKOS-AI-JOB-LEADS.exe" -Force
    Write-Host "Single-file exe: $OutDir\GBLOXKOS-AI-JOB-LEADS.exe" -ForegroundColor Green
} else {
    Copy-Item "$ProjectRoot\dist\GBLOXKOS-AI-JOB-LEADS" "$OutDir\GBLOXKOS-AI-JOB-LEADS" -Recurse -Force
    # Create a launch script
    @"
@echo off
set JOBLEAD_DATA_DIR=%LOCALAPPDATA%\gbloxkos-ai-job-leads
set OLLAMA_MODEL=qwen2.5:3b
set OLLAMA_BASE_URL=http://localhost:11434
set USE_OLLAMA=true
set PREFER_LOCAL_AI=true
cd /d "%~dp0"
GBLOXKOS-AI-JOB-LEADS.exe %*
"@
    | Set-Content "$OutDir\GBLOXKOS-AI-JOB-LEADS\GBLOXKOS-AI-JOB-LEADS.bat" -Encoding ASCII
    Write-Host "Portable folder: $OutDir\GBLOXKOS-AI-JOB-LEADS\" -ForegroundColor Green
    Write-Host "Run with: GBLOXKOS-AI-JOB-LEADS.bat" -ForegroundColor Green
}

# 6. Create README
Write-Host "[5/5] Writing README..." -ForegroundColor Yellow
@"
# GBLOXKOS AI JOB LEADS - Windows Portable

## Quick Start
1. Install Ollama: https://ollama.ai/download/windows
2. Pull model: `ollama pull qwen2.5:3b`
3. Run `GBLOXKOS-AI-JOB-LEADS.bat` (folder) or `GBLOXKOS-AI-JOB-LEADS.exe` (single-file)

## No API Keys Required
- Job search: RemoteOK, Remotive, WeWorkRemotely (public APIs)
- AI ranking: Local Ollama (qwen2.5:3b)
- Email: Your Gmail/Outlook App Password (free) or .eml draft

## Data Location
%LOCALAPPDATA%\gbloxkos-ai-job-leads\

## Environment Variables (optional)
JOBLEAD_DATA_DIR    - Custom data directory
OLLAMA_MODEL        - Override model (default: qwen2.5:3b)
OLLAMA_BASE_URL     - Override Ollama URL (default: http://localhost:11434)
SMTP_PROVIDER       - gmail|outlook|yahoo|icloud|custom
EMAIL_ADDRESS       - Your email
EMAIL_PASSWORD      - App Password (not login password)
"@
| Set-Content "$OutDir\README.txt" -Encoding UTF8

Write-Host "=== Windows build complete ===" -ForegroundColor Cyan