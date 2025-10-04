# License Plate Extraction - Installation Summary

## 📦 What Has Been Created

### 1. **SETUP_WINDOWS_PIP.md** - Comprehensive Setup Guide
- Complete step-by-step installation instructions
- Troubleshooting section
- Usage examples
- Database viewing options
- Comparison with conda approach

### 2. **install_windows.ps1** - Automated PowerShell Installer
- One-click installation for PowerShell users
- Automatic dependency installation
- Error handling and verification
- Progress indicators

### 3. **install_windows.bat** - Automated Batch Installer
- One-click installation for Command Prompt users
- Same functionality as PowerShell version
- Compatible with older Windows systems

### 4. **run.ps1** - Quick Start Script (PowerShell)
- Menu-driven interface
- Multiple input options (image/video/webcam)
- Database viewer integration
- Virtual environment auto-activation

### 5. **run.bat** - Quick Start Script (Batch)
- Same features as PowerShell version
- Command Prompt compatible

### 6. **Updated requirements.txt**
- Complete dependency list
- Version specifications
- Organized by category

### 7. **Updated README.md**
- pip-based instructions added
- Quick start section
- Link to full documentation

## 🚀 Installation Methods

### Method 1: Automated Installation (Recommended)

**PowerShell:**
```powershell
cd "c:\Users\DELL\Desktop\AvanishCodes\Hacknova-CodeBreakers\license\License-Plate-Extraction-Save-Data-to-SQL-Database"
.\install_windows.ps1
```

**Command Prompt:**
```cmd
cd "c:\Users\DELL\Desktop\AvanishCodes\Hacknova-CodeBreakers\license\License-Plate-Extraction-Save-Data-to-SQL-Database"
install_windows.bat
```

### Method 2: Manual Installation

Follow the detailed instructions in **SETUP_WINDOWS_PIP.md**

### Method 3: Quick Command Block

Copy and paste the entire setup block from **SETUP_WINDOWS_PIP.md**

## 📋 Installation Steps (Summary)

1. ✅ Create virtual environment (`venv_license`)
2. ✅ Activate virtual environment
3. ✅ Upgrade pip
4. ✅ Clone YOLOv10 repository
5. ✅ Install project requirements
6. ✅ Install YOLOv10 package
7. ✅ Fix NumPy compatibility (1.26.4)
8. ✅ Install PyTorch (CPU or GPU)
9. ✅ Install additional packages
10. ✅ Initialize SQLite database

## 🎯 Daily Usage

### Quick Start

**PowerShell:**
```powershell
.\run.ps1
```

**Command Prompt:**
```cmd
run.bat
```

### Manual Run

```bash
# Activate environment
venv_license\Scripts\activate.bat  # CMD
# OR
.\venv_license\Scripts\Activate.ps1  # PowerShell

# Run program
python main.py
```

## 📦 Installed Packages

| Package | Purpose |
|---------|---------|
| **torch** | PyTorch deep learning framework |
| **torchvision** | Computer vision models and utilities |
| **opencv-python** | Computer vision operations |
| **ultralytics** | YOLO implementation |
| **paddlepaddle** | PaddlePaddle framework |
| **paddleocr** | OCR text recognition |
| **db-sqlite3** | SQLite database operations |
| **numpy** | Numerical computations (v1.26.4) |
| **Pillow** | Image processing |

## 🗂️ Project Structure

```
License-Plate-Extraction-Save-Data-to-SQL-Database/
├── 📁 venv_license/              # Virtual environment (you create)
├── 📁 yolov10/                   # YOLOv10 repo (auto-cloned)
├── 📁 data/                      # Input images/videos
│   ├── carImage1.png
│   ├── carImage2.png
│   └── carLicence*.mp4
├── 📁 weights/
│   └── best.pt                   # YOLOv10 trained model
├── 📁 json/
│   └── LicensePlateData.json     # Extracted data
├── 📄 main.py                    # Main program
├── 📄 sqldb.py                   # Database initialization
├── 📄 requirements.txt           # Dependencies list
├── 📄 licensePlatesDatabase.db   # SQLite database (created)
├── 📄 SETUP_WINDOWS_PIP.md       # 📖 Full setup guide
├── 📄 install_windows.ps1        # 🚀 Auto installer (PowerShell)
├── 📄 install_windows.bat        # 🚀 Auto installer (Batch)
├── 📄 run.ps1                    # ▶️ Quick start (PowerShell)
├── 📄 run.bat                    # ▶️ Quick start (Batch)
└── 📄 README.md                  # Project overview
```

## 🎮 Usage Examples

### Run on Image
```bash
python main.py --source data/carImage1.png
```

### Run on Video
```bash
python main.py --source data/carLicence1.mp4
```

### Run with Webcam
```bash
python main.py --source 0
```

### View Database
1. Visit: https://inloop.github.io/sqlite-viewer/
2. Upload: `licensePlatesDatabase.db`
3. Browse and query data

## 🔧 Troubleshooting Quick Reference

| Issue | Solution |
|-------|----------|
| **Execution Policy Error** | `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| **NumPy Compatibility** | `pip uninstall numpy -y && pip install numpy==1.26.4` |
| **PyTorch Not Found** | Install with pip from PyTorch website |
| **PaddleOCR Failed** | Install Visual C++ Build Tools |
| **Git Not Found** | Install Git for Windows |

## 🌟 Key Differences: conda vs pip

| Aspect | conda (Original) | pip (Our Setup) |
|--------|------------------|-----------------|
| Environment | `conda create -n cvproj` | `python -m venv venv_license` |
| Activation | `conda activate cvproj` | `.\venv_license\Scripts\Activate.ps1` |
| Package Manager | conda | pip |
| Python Version | Managed by conda | Use system Python |
| Environment Location | conda/envs/ | Project directory |
| Portability | conda-specific | Standard Python |

## ✅ Verification Checklist

After installation, verify:

- [ ] Virtual environment created (`venv_license/` exists)
- [ ] YOLOv10 cloned (`yolov10/` exists)
- [ ] NumPy version is 1.26.4 (`pip show numpy`)
- [ ] PyTorch installed (`python -c "import torch; print(torch.__version__)"`)
- [ ] Database exists (`licensePlatesDatabase.db`)
- [ ] Can run program (`python main.py --help`)

## 📊 Expected Output

When running `python main.py`:

1. **YOLOv10 loads** (~2-5 seconds)
2. **Detects license plates** in image/video
3. **OCR extracts text** from detected plates
4. **Saves to database** and JSON
5. **Displays results** in console
6. **Shows annotated images** (if GUI available)

## 🔗 Useful Commands

```bash
# Check installed packages
pip list

# Check NumPy version
pip show numpy

# Check PyTorch
python -c "import torch; print(torch.__version__)"

# Check PaddleOCR
python -c "import paddleocr; print('PaddleOCR OK')"

# View database schema
python -c "import sqlite3; conn=sqlite3.connect('licensePlatesDatabase.db'); print(conn.execute('SELECT sql FROM sqlite_master').fetchall()); conn.close()"

# Deactivate environment
deactivate
```

## 🎯 Next Steps

1. ✅ Run automated installer
2. ✅ Test with sample images in `data/`
3. ✅ View extracted data in database
4. 🔄 Add your own images/videos to `data/`
5. 🔄 Customize detection parameters
6. 🔄 Train custom model (optional)
7. 🔄 Integrate with ID card extraction project

## 📚 Documentation Links

- **Full Setup Guide**: [SETUP_WINDOWS_PIP.md](SETUP_WINDOWS_PIP.md)
- **YOLOv10**: https://github.com/THU-MIG/yolov10
- **PaddleOCR**: https://github.com/PaddlePaddle/PaddleOCR
- **SQLite Viewer**: https://inloop.github.io/sqlite-viewer/

## 💡 Tips

1. **First Time Setup**: Use automated installer for easiest setup
2. **Daily Use**: Use `run.ps1` or `run.bat` for quick access
3. **GPU Users**: Install CUDA-enabled PyTorch for faster processing
4. **Debugging**: Check console output for errors
5. **Database**: Use online SQLite viewer for easy data access

## 🎉 Success Indicators

✅ Installation complete when:
- All packages installed without errors
- Database file created successfully
- Program runs without import errors
- Can process sample images
- Data saved to database

## 📞 Support

If you encounter issues:
1. Check **SETUP_WINDOWS_PIP.md** troubleshooting section
2. Verify all dependencies installed: `pip list`
3. Check Python version: `python --version` (should be 3.9-3.12)
4. Ensure virtual environment activated
5. Check error messages in console

---

**Status**: ✅ Ready to install and use!

**Environment**: Windows with pip (no conda required)

**Python Version**: 3.11 recommended (3.9-3.12 supported)

**Installation Time**: ~10-15 minutes (depending on internet speed)
