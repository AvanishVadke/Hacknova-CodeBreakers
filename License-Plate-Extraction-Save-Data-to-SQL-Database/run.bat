@echo off
REM Quick Start Script - License Plate Extraction
REM Run this to quickly start the program after installation

echo ========================================
echo License Plate Extraction
echo ========================================
echo.

REM Navigate to project directory
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist venv_license\ (
    echo ERROR: Virtual environment not found!
    echo Please run install_windows.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv_license\Scripts\activate.bat
echo.

REM Check if database exists
if not exist licensePlatesDatabase.db (
    echo WARNING: Database not found. Initializing...
    python sqldb.py
    echo.
)

REM Display menu
echo Choose an option:
echo 1. Run on sample image (carImage1.png)
echo 2. Run on sample video (carLicence1.mp4)
echo 3. Run with webcam
echo 4. View database
echo 5. Custom input
echo 6. Exit
echo.

set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" (
    echo.
    echo Running on sample image...
    python main.py --source data/carImage1.png
) else if "%choice%"=="2" (
    echo.
    echo Running on sample video...
    python main.py --source data/carLicence1.mp4
) else if "%choice%"=="3" (
    echo.
    echo Running with webcam...
    python main.py --source 0
) else if "%choice%"=="4" (
    echo.
    echo Opening database viewer in browser...
    start https://inloop.github.io/sqlite-viewer/
    echo.
    echo Upload the file: %CD%\licensePlatesDatabase.db
) else if "%choice%"=="5" (
    set /p custom_source="Enter path to image/video: "
    echo.
    echo Running on custom input...
    python main.py --source !custom_source!
) else if "%choice%"=="6" (
    echo.
    echo Exiting...
    exit /b 0
) else (
    echo.
    echo Invalid choice. Running default...
    python main.py
)

echo.
echo ========================================
echo Program finished!
echo ========================================
pause
