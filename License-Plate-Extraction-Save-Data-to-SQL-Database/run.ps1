# Quick Start Script - License Plate Extraction (PowerShell)
# Run this to quickly start the program after installation

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "License Plate Extraction" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Navigate to project directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Check if virtual environment exists
if (-not (Test-Path "venv_license")) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run install_windows.ps1 first." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv_license\Scripts\Activate.ps1
Write-Host ""

# Check if database exists
if (-not (Test-Path "licensePlatesDatabase.db")) {
    Write-Host "WARNING: Database not found. Initializing..." -ForegroundColor Yellow
    python sqldb.py
    Write-Host ""
}

# Display menu
Write-Host "Choose an option:" -ForegroundColor Cyan
Write-Host "1. Run on sample image (carImage1.png)" -ForegroundColor White
Write-Host "2. Run on sample video (carLicence1.mp4)" -ForegroundColor White
Write-Host "3. Run with webcam" -ForegroundColor White
Write-Host "4. View database" -ForegroundColor White
Write-Host "5. Custom input" -ForegroundColor White
Write-Host "6. Exit" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter your choice (1-6)"

switch ($choice) {
    "1" {
        Write-Host "`nRunning on sample image..." -ForegroundColor Yellow
        python main.py --source data/carImage1.png
    }
    "2" {
        Write-Host "`nRunning on sample video..." -ForegroundColor Yellow
        python main.py --source data/carLicence1.mp4
    }
    "3" {
        Write-Host "`nRunning with webcam..." -ForegroundColor Yellow
        python main.py --source 0
    }
    "4" {
        Write-Host "`nOpening database viewer in browser..." -ForegroundColor Yellow
        Start-Process "https://inloop.github.io/sqlite-viewer/"
        Write-Host ""
        Write-Host "Upload the file: $scriptPath\licensePlatesDatabase.db" -ForegroundColor Gray
    }
    "5" {
        $customSource = Read-Host "Enter path to image/video"
        Write-Host "`nRunning on custom input..." -ForegroundColor Yellow
        python main.py --source $customSource
    }
    "6" {
        Write-Host "`nExiting..." -ForegroundColor Green
        exit 0
    }
    default {
        Write-Host "`nInvalid choice. Running default..." -ForegroundColor Yellow
        python main.py
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Program finished!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Read-Host "Press Enter to exit"
