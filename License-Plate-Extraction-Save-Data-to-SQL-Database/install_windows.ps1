# License Plate Extraction - Automated Installation Script for Windows
# Run this in PowerShell

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "License Plate Extraction Setup (pip)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
Write-Host "Found: $pythonVersion" -ForegroundColor Green

# Navigate to project directory
$projectDir = "c:\Users\DELL\Desktop\AvanishCodes\Hacknova-CodeBreakers\license\License-Plate-Extraction-Save-Data-to-SQL-Database"
Set-Location $projectDir
Write-Host "Working directory: $projectDir" -ForegroundColor Green

# Step 1: Create virtual environment
Write-Host "`n[Step 1/10] Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv_license") {
    Write-Host "Virtual environment already exists." -ForegroundColor Gray
} else {
    python -m venv venv_license
    Write-Host "Virtual environment created successfully!" -ForegroundColor Green
}

# Step 2: Activate virtual environment
Write-Host "`n[Step 2/10] Activating virtual environment..." -ForegroundColor Yellow
& .\venv_license\Scripts\Activate.ps1
Write-Host "Virtual environment activated!" -ForegroundColor Green

# Step 3: Upgrade pip
Write-Host "`n[Step 3/10] Upgrading pip, setuptools, and wheel..." -ForegroundColor Yellow
python -m pip install --upgrade pip setuptools wheel --quiet
Write-Host "pip upgraded successfully!" -ForegroundColor Green

# Step 4: Clone YOLOv10
Write-Host "`n[Step 4/10] Cloning YOLOv10 repository..." -ForegroundColor Yellow
if (Test-Path "yolov10") {
    Write-Host "YOLOv10 already cloned." -ForegroundColor Gray
} else {
    git clone https://github.com/THU-MIG/yolov10.git
    if ($LASTEXITCODE -eq 0) {
        Write-Host "YOLOv10 cloned successfully!" -ForegroundColor Green
    } else {
        Write-Host "Failed to clone YOLOv10. Please check your internet connection." -ForegroundColor Red
        exit 1
    }
}

# Step 5: Install project requirements
Write-Host "`n[Step 5/10] Installing project requirements..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
Write-Host "Project requirements installed!" -ForegroundColor Green

# Step 6: Install YOLOv10
Write-Host "`n[Step 6/10] Installing YOLOv10..." -ForegroundColor Yellow
Set-Location yolov10
pip install -e . --quiet
Set-Location ..
Write-Host "YOLOv10 installed successfully!" -ForegroundColor Green

# Step 7: Fix NumPy version
Write-Host "`n[Step 7/10] Fixing NumPy version..." -ForegroundColor Yellow
pip uninstall numpy -y --quiet
pip install numpy==1.26.4 --quiet
Write-Host "NumPy 1.26.4 installed!" -ForegroundColor Green

# Step 8: Install PyTorch
Write-Host "`n[Step 8/10] Installing PyTorch (CPU version)..." -ForegroundColor Yellow
Write-Host "This may take a few minutes..." -ForegroundColor Gray
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu --quiet
Write-Host "PyTorch installed successfully!" -ForegroundColor Green

# Step 9: Install additional packages
Write-Host "`n[Step 9/10] Installing additional packages..." -ForegroundColor Yellow
pip install opencv-python ultralytics paddlepaddle paddleocr db-sqlite3 Pillow --quiet
Write-Host "Additional packages installed!" -ForegroundColor Green

# Step 10: Initialize database
Write-Host "`n[Step 10/10] Initializing SQLite database..." -ForegroundColor Yellow
python sqldb.py
if ($LASTEXITCODE -eq 0) {
    Write-Host "Database initialized successfully!" -ForegroundColor Green
} else {
    Write-Host "Database initialization failed. Check sqldb.py" -ForegroundColor Red
}

# Verification
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Installed packages:" -ForegroundColor Yellow
pip list | Select-String -Pattern "torch|numpy|paddle|ultralytics|opencv"

Write-Host "`n📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Activate environment: .\venv_license\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "2. Run the program: python main.py" -ForegroundColor White
Write-Host "3. View database: https://inloop.github.io/sqlite-viewer/" -ForegroundColor White
Write-Host ""
Write-Host "📁 Database location: $projectDir\licensePlatesDatabase.db" -ForegroundColor Gray
Write-Host ""

# Prompt to run
$runNow = Read-Host "Do you want to run the program now? (y/n)"
if ($runNow -eq 'y' -or $runNow -eq 'Y') {
    Write-Host "`nStarting License Plate Extraction..." -ForegroundColor Yellow
    python main.py
} else {
    Write-Host "`nSetup complete! Run 'python main.py' when ready." -ForegroundColor Green
}
