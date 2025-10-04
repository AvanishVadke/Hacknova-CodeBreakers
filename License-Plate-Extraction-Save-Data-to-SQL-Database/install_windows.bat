@echo off
REM License Plate Extraction - Automated Installation Script for Windows
REM Run this in Command Prompt

echo ========================================
echo License Plate Extraction Setup (pip)
echo ========================================
echo.

REM Check Python version
echo Checking Python version...
python --version
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.11 from python.org
    pause
    exit /b 1
)

REM Navigate to project directory
cd /d "%~dp0"
echo Working directory: %CD%

REM Step 1: Create virtual environment
echo.
echo [Step 1/10] Creating virtual environment...
if exist venv_license\ (
    echo Virtual environment already exists.
) else (
    python -m venv venv_license
    echo Virtual environment created successfully!
)

REM Step 2: Activate virtual environment
echo.
echo [Step 2/10] Activating virtual environment...
call venv_license\Scripts\activate.bat
echo Virtual environment activated!

REM Step 3: Upgrade pip
echo.
echo [Step 3/10] Upgrading pip, setuptools, and wheel...
python -m pip install --upgrade pip setuptools wheel --quiet
echo pip upgraded successfully!

REM Step 4: Clone YOLOv10
echo.
echo [Step 4/10] Cloning YOLOv10 repository...
if exist yolov10\ (
    echo YOLOv10 already cloned.
) else (
    git clone https://github.com/THU-MIG/yolov10.git
    if errorlevel 1 (
        echo ERROR: Failed to clone YOLOv10. Please check your internet connection.
        pause
        exit /b 1
    )
    echo YOLOv10 cloned successfully!
)

REM Step 5: Install project requirements
echo.
echo [Step 5/10] Installing project requirements...
pip install -r requirements.txt --quiet
echo Project requirements installed!

REM Step 6: Install YOLOv10
echo.
echo [Step 6/10] Installing YOLOv10...
cd yolov10
pip install -e . --quiet
cd ..
echo YOLOv10 installed successfully!

REM Step 7: Fix NumPy version
echo.
echo [Step 7/10] Fixing NumPy version...
pip uninstall numpy -y --quiet
pip install numpy==1.26.4 --quiet
echo NumPy 1.26.4 installed!

REM Step 8: Install PyTorch
echo.
echo [Step 8/10] Installing PyTorch (CPU version)...
echo This may take a few minutes...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu --quiet
echo PyTorch installed successfully!

REM Step 9: Install additional packages
echo.
echo [Step 9/10] Installing additional packages...
pip install opencv-python ultralytics paddlepaddle paddleocr db-sqlite3 Pillow --quiet
echo Additional packages installed!

REM Step 10: Initialize database
echo.
echo [Step 10/10] Initializing SQLite database...
python sqldb.py
if errorlevel 1 (
    echo ERROR: Database initialization failed. Check sqldb.py
) else (
    echo Database initialized successfully!
)

REM Verification
echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Installed packages:
pip list | findstr /i "torch numpy paddle ultralytics opencv"

echo.
echo Next Steps:
echo 1. Activate environment: venv_license\Scripts\activate.bat
echo 2. Run the program: python main.py
echo 3. View database: https://inloop.github.io/sqlite-viewer/
echo.
echo Database location: %CD%\licensePlatesDatabase.db
echo.

REM Prompt to run
set /p runnow="Do you want to run the program now? (y/n): "
if /i "%runnow%"=="y" (
    echo.
    echo Starting License Plate Extraction...
    python main.py
) else (
    echo.
    echo Setup complete! Run 'python main.py' when ready.
)

pause
