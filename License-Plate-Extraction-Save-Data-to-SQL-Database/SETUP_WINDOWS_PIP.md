# License Plate Extraction - Windows Setup Guide (pip)

This guide provides step-by-step instructions for setting up the License Plate Extraction project on Windows using **pip** (without conda).

## 📋 Prerequisites

- Python 3.11 (recommended) or Python 3.9-3.12
- pip (comes with Python)
- Git for Windows
- Visual Studio Build Tools (for some packages)

## 🚀 Installation Steps

### Step 1: Check Python Version

```powershell
python --version
# Should show Python 3.11.x or similar
```

If you don't have Python 3.11, download from: https://www.python.org/downloads/

### Step 2: Create Virtual Environment (Using venv)

```powershell
# Navigate to the license project directory
cd "c:\Users\DELL\Desktop\AvanishCodes\Hacknova-CodeBreakers\license\License-Plate-Extraction-Save-Data-to-SQL-Database"

# Create virtual environment
python -m venv venv_license

# Activate virtual environment (PowerShell)
.\venv_license\Scripts\Activate.ps1

# If you get execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Alternative for Command Prompt:**
```cmd
venv_license\Scripts\activate.bat
```

### Step 3: Upgrade pip

```powershell
python -m pip install --upgrade pip setuptools wheel
```

### Step 4: Clone YOLOv10 Repository

```powershell
# Make sure you're in the license project directory
git clone https://github.com/THU-MIG/yolov10.git
```

### Step 5: Install Project Requirements

```powershell
# Install project dependencies
pip install -r requirements.txt
```

### Step 6: Install YOLOv10

```powershell
# Navigate to yolov10 directory
cd yolov10

# Install YOLOv10 in editable mode
pip install -e .

# Return to project root
cd ..
```

### Step 7: Fix NumPy Version (Important!)

There's a known compatibility issue with NumPy. Fix it:

```powershell
pip uninstall numpy -y
pip install numpy==1.26.4
```

### Step 8: Install Additional Dependencies

Some packages may need additional installation:

```powershell
# Install PyTorch (CPU version for Windows)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# If you have NVIDIA GPU, use this instead:
# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install other required packages
pip install opencv-python
pip install ultralytics
pip install paddlepaddle
pip install paddleocr
pip install db-sqlite3
pip install pillow
```

### Step 9: Initialize Database

```powershell
# Create and initialize the SQLite database
python sqldb.py
```

Expected output:
```
Database created successfully
Table created successfully
```

### Step 10: Run the License Plate Extraction

```powershell
# Run the main program
python main.py
```

## 🎯 Quick Start (One-Time Setup)

Copy and paste this entire block into PowerShell:

```powershell
# Navigate to project directory
cd "c:\Users\DELL\Desktop\AvanishCodes\Hacknova-CodeBreakers\license\License-Plate-Extraction-Save-Data-to-SQL-Database"

# Create and activate virtual environment
python -m venv venv_license
.\venv_license\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip setuptools wheel

# Clone YOLOv10 if not already cloned
if (-not (Test-Path "yolov10")) {
    git clone https://github.com/THU-MIG/yolov10.git
}

# Install requirements
pip install -r requirements.txt

# Install YOLOv10
cd yolov10
pip install -e .
cd ..

# Fix numpy version
pip uninstall numpy -y
pip install numpy==1.26.4

# Install PyTorch (CPU)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install additional packages
pip install opencv-python ultralytics paddlepaddle paddleocr db-sqlite3 pillow

# Initialize database
python sqldb.py

# Run the program
python main.py
```

## 📁 Project Structure

```
License-Plate-Extraction-Save-Data-to-SQL-Database/
├── venv_license/              # Virtual environment (created by you)
├── yolov10/                   # YOLOv10 repository (cloned)
├── data/                      # Input images/videos
│   ├── carImage1.png
│   ├── carImage2.png
│   └── *.mp4 files
├── weights/
│   └── best.pt               # YOLOv10 trained weights
├── json/
│   └── LicensePlateData.json # Extracted data
├── main.py                    # Main program
├── sqldb.py                   # Database initialization
├── requirements.txt           # Dependencies
├── licensePlatesDatabase.db   # SQLite database (created)
└── README.md
```

## 🔧 Troubleshooting

### Issue 1: Virtual Environment Activation Error

**Error**: `execution policy error`

**Solution**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue 2: NumPy Compatibility Error

**Error**: `A module that was compiled using NumPy 1.x cannot be run in NumPy 2.x`

**Solution**:
```powershell
pip uninstall numpy -y
pip install numpy==1.26.4
```

### Issue 3: PyTorch Not Found

**Solution**:
```powershell
# For CPU
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# For GPU (CUDA 11.8)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Issue 4: PaddleOCR Installation Failed

**Solution**:
```powershell
# Install Visual C++ Build Tools first
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Then retry:
pip install paddlepaddle paddleocr
```

### Issue 5: Git Clone Failed

**Solution**:
```powershell
# Install Git for Windows from: https://git-scm.com/download/win

# Or download YOLOv10 manually from:
# https://github.com/THU-MIG/yolov10/archive/refs/heads/main.zip
```

## 🎮 Usage

### Run on Single Image

```python
python main.py --source data/carImage1.png
```

### Run on Video

```python
python main.py --source data/carLicence1.mp4
```

### Run with Webcam

```python
python main.py --source 0
```

## 📊 View Database

### Option 1: Online SQLite Viewer
Visit: https://inloop.github.io/sqlite-viewer/
- Upload `licensePlatesDatabase.db`
- View and query data

### Option 2: Python Script

```python
import sqlite3

conn = sqlite3.connect('licensePlatesDatabase.db')
cursor = conn.cursor()

# Query all license plates
cursor.execute("SELECT * FROM license_plates")
results = cursor.fetchall()

for row in results:
    print(row)

conn.close()
```

### Option 3: DB Browser for SQLite

Download from: https://sqlitebrowser.org/
- Open `licensePlatesDatabase.db`
- Browse data graphically

## 🔄 Daily Usage (After Setup)

```powershell
# Navigate to project
cd "c:\Users\DELL\Desktop\AvanishCodes\Hacknova-CodeBreakers\license\License-Plate-Extraction-Save-Data-to-SQL-Database"

# Activate environment
.\venv_license\Scripts\Activate.ps1

# Run the program
python main.py
```

## 📦 Required Packages List

```
torch>=2.0.0
torchvision
torchaudio
opencv-python>=4.8.0
ultralytics>=8.0.0
paddlepaddle
paddleocr>=2.6.0
db-sqlite3
Pillow>=10.0.0
numpy==1.26.4
huggingface-hub
```

## 🎯 Features

- **YOLOv10**: State-of-the-art object detection for license plates
- **PaddleOCR**: Accurate text recognition from license plates
- **SQLite Database**: Store extracted license plate data
- **Multiple Input Support**: Images, videos, webcam
- **JSON Export**: Save data to JSON format
- **Real-time Processing**: Process video streams

## 🌟 Comparison: conda vs pip

| Feature | conda (Original) | pip (This Guide) |
|---------|------------------|------------------|
| Environment | conda env | venv |
| Activation | `conda activate` | `.\venv_license\Scripts\Activate.ps1` |
| Installation | `conda install` | `pip install` |
| Deactivation | `conda deactivate` | `deactivate` |
| Package Manager | conda | pip |
| Python Version | Managed by conda | Use system Python |

## 📝 Additional Notes

1. **Virtual Environment**: Always activate `venv_license` before running the project
2. **GPU Support**: If you have NVIDIA GPU, install CUDA-enabled PyTorch
3. **Model Weights**: Ensure `weights/best.pt` exists (YOLOv10 trained model)
4. **Data Location**: Place images/videos in `data/` folder
5. **Database**: SQLite database is created automatically

## 🚀 Next Steps

1. ✅ Complete installation following this guide
2. ✅ Test with sample images in `data/` folder
3. ✅ View results in SQLite database
4. 🔄 Train custom model on your license plates (optional)
5. 🔄 Integrate with your ID card extraction project

## 🔗 Useful Links

- [YOLOv10 GitHub](https://github.com/THU-MIG/yolov10)
- [PaddleOCR Documentation](https://github.com/PaddlePaddle/PaddleOCR)
- [SQLite Viewer](https://inloop.github.io/sqlite-viewer/)
- [PyTorch Installation](https://pytorch.org/get-started/locally/)

---

**Status**: Ready to install and use with pip on Windows!

**Python Version**: 3.11 (recommended)

**Virtual Environment**: venv (pip-based)
