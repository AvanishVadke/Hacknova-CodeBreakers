# License Plate Extraction with YOLOv10 and PaddleOCR & Save Data to SQL Database

## 🚀 Quick Start (Windows - pip)

### Automated Installation (Recommended)

```powershell
# Run the automated installation script
.\install_windows.ps1
```

### Manual Installation

```bash
# Create virtual environment
python -m venv venv_license

# Activate (PowerShell)
.\venv_license\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip

# Clone YOLOv10
git clone https://github.com/THU-MIG/yolov10.git

# Install dependencies
pip install -r requirements.txt

# Install YOLOv10
cd yolov10
pip install -e .
cd ..

# Fix NumPy compatibility
pip uninstall numpy -y
pip install numpy==1.26.4

# Install PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Initialize database
python sqldb.py

# Run the program
python main.py
```

## 📚 Full Documentation

See **[SETUP_WINDOWS_PIP.md](SETUP_WINDOWS_PIP.md)** for detailed setup instructions.

---

## Original Setup (conda)

### How to run:

```bash
git clone https://github.com/THU-MIG/yolov10.git
```

```bash
conda create -n cvproj python=3.11 -y
```

```bash
conda activate cvproj
```

```bash
pip install -r requirements.txt
```

```bash
cd yolov10
```

```bash
pip install -e .
```

```bash
cd ..
```

```bash
python sqldb.py
```

```bash
python main.py
```

## Error Fixed

```bash
pip uninstall numpy
```

```bash
pip install numpy==1.26.4
```


### sqlite viewer:

https://inloop.github.io/sqlite-viewer/


