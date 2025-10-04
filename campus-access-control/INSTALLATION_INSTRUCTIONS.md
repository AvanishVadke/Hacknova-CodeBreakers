# 🚀 Installation Instructions - Enhanced Access Control

## 📋 Prerequisites

### System Requirements
- **Operating System:** Windows 10/11, Linux (Ubuntu 20.04+), or macOS
- **Python:** 3.11 or 3.10 (Recommended: 3.11)
- **RAM:** 8GB minimum (16GB recommended for smooth operation)
- **Storage:** 5GB free disk space
- **GPU (Optional):** NVIDIA GPU with CUDA 12.1+ for faster processing
- **Internet:** Required for initial setup and database connection

---

## 📦 Step 1: Extract Package

1. Extract the ZIP file to your desired location:
   ```
   C:\Projects\Enhanced_Access_Control\
   ```
   or
   ```
   ~/projects/enhanced_access_control/
   ```

2. Verify folder structure:
   ```
   Enhanced_Access_Control/
   ├── Enhanced_Access_Control.ipynb
   ├── requirements_notebook.txt
   ├── .env.example
   ├── models/
   │   └── best.pt
   └── data/
       └── training_data/
           └── (60 ID card images)
   ```

---

## 🐍 Step 2: Python Setup

### Windows

1. **Check Python version:**
   ```powershell
   python --version
   ```
   Should show: `Python 3.11.x` or `Python 3.10.x`

2. **If Python not installed:**
   - Download from: https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"
   - Restart terminal after installation

3. **Create virtual environment:**
   ```powershell
   cd C:\Projects\Enhanced_Access_Control
   python -m venv venv
   ```

4. **Activate virtual environment:**
   ```powershell
   .\venv\Scripts\activate
   ```
   You should see `(venv)` in your terminal prompt.

### Linux/Mac

1. **Check Python version:**
   ```bash
   python3 --version
   ```

2. **Create virtual environment:**
   ```bash
   cd ~/projects/enhanced_access_control
   python3 -m venv venv
   ```

3. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

---

## 📚 Step 3: Install Dependencies

### Option A: Install from requirements.txt (Recommended)

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all dependencies
pip install -r requirements_notebook.txt
```

**⏱️ Time:** 10-15 minutes (depending on internet speed)

**📊 Download Size:** ~2.5 GB (includes PyTorch, TensorFlow, OpenCV, etc.)

### Option B: Install Step-by-Step (If Option A fails)

```bash
# Core packages
pip install opencv-python opencv-contrib-python
pip install numpy pandas matplotlib

# Deep Learning
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install ultralytics

# OCR and Face Recognition
pip install easyocr
pip install deepface tf-keras tensorflow

# Database
pip install psycopg2-binary python-dotenv

# Jupyter
pip install jupyter ipywidgets ipython

# Utilities
pip install tqdm Pillow scipy requests pyyaml
```

### Verify Installation

```python
# Create test_install.py
import torch
import cv2
import easyocr
from ultralytics import YOLO
from deepface import DeepFace
import psycopg2

print("✅ All packages imported successfully!")
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
```

Run:
```bash
python test_install.py
```

---

## 🗄️ Step 4: Database Setup (Supabase)

### Create Supabase Account

1. **Go to:** https://supabase.com
2. **Sign up** with GitHub or email
3. **Create new project:**
   - Project name: `campus-access-control`
   - Database password: (create a strong password)
   - Region: (choose closest to you)
   - Plan: Free tier (sufficient for testing)

4. **Wait** for project to initialize (~2 minutes)

### Get Database Credentials

1. Go to **Settings** → **Database**
2. Scroll to **Connection String** section
3. Select **Connection Pooling** → **Transaction Mode**
4. Copy the connection details:
   ```
   Host: aws-1-us-east-2.pooler.supabase.com
   Port: 5432
   Database: postgres
   User: postgres.your-project-ref
   Password: [your database password]
   ```

### Configure .env File

1. **Copy template:**
   ```bash
   cp .env.example .env
   ```

2. **Edit .env file:**
   ```properties
   SUPABASE_USER=postgres.your_project_ref
   SUPABASE_PASSWORD=your_database_password
   SUPABASE_HOST=aws-1-us-east-2.pooler.supabase.com
   SUPABASE_PORT=5432
   SUPABASE_DBNAME=postgres
   ```

3. **Save the file**

### Test Database Connection

```python
# Create test_db.py
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

try:
    conn = psycopg2.connect(
        host=os.getenv('SUPABASE_HOST'),
        port=os.getenv('SUPABASE_PORT'),
        dbname=os.getenv('SUPABASE_DBNAME'),
        user=os.getenv('SUPABASE_USER'),
        password=os.getenv('SUPABASE_PASSWORD')
    )
    print("✅ Database connection successful!")
    conn.close()
except Exception as e:
    print(f"❌ Database connection failed: {e}")
```

Run:
```bash
python test_db.py
```

---

## 📓 Step 5: Launch Jupyter Notebook

### Start Jupyter Server

```bash
# Make sure virtual environment is activated
jupyter notebook
```

This will:
1. Start Jupyter server
2. Open browser automatically at `http://localhost:8888`

### Open the Notebook

1. In Jupyter file browser, click: `Enhanced_Access_Control.ipynb`
2. Notebook will open in new tab

---

## ▶️ Step 6: Run the Notebook

### Execute Cells in Order

**Cell 1: Install Packages** (if not done via requirements.txt)
- Click the cell
- Press `Shift + Enter` or click "Run"
- Wait for completion (skip if already installed)

**Cell 2: Import Libraries**
```python
import os
import json
import cv2
# ... etc
```
- Should complete in 2-5 seconds
- Look for: `✅ Libraries imported successfully`

**Cell 3: Configure Paths**
```python
BASE_DIR = os.getcwd()
# ... etc
```
- Should show your folder paths
- Look for: `✅ Supabase: aws-1-us-east-2.pooler.supabase.com`

**Cell 4: Initialize Database**
```python
db = SupabaseManager()
```
- Creates database tables
- Look for: `✅ Connected to Supabase database`
- Look for: `✅ All tables created successfully`

**Cell 5: Load Models**
```python
yolo_model = YOLO(MODEL_PATH)
ocr_reader = easyocr.Reader(['en'], gpu=True)
```
- Takes 30-60 seconds
- First time: EasyOCR downloads models (~200 MB)
- Look for: `✅ YOLO model loaded successfully`
- Look for: `✅ EasyOCR initialized successfully`

**Cell 6: ID Card Processor**
- Defines the main processor class
- Should complete instantly

**Cell 7: Interactive Scanner**
- Shows dropdown with ID card images
- Click "Process ID Card" button to test
- Or click "Process All Images" for batch processing

**Cell 8: Face Recognition System**
- Initializes face recognition
- Look for: `✅ Loaded X face templates`

**Cell 9: Build Face Database**
```python
face_system.build_face_database()
```
- ⚠️ Run this ONCE only
- Extracts faces from all ID cards
- Takes 2-5 minutes for 60 images
- Creates `face_database/` folder with face images

**Cell 10: Live Face Recognition**
```python
face_system.start_live_camera()
```
- Opens camera window
- Press SPACE to capture and verify
- Press Q to quit

**Cell 11: View Logs**
- Shows recent access logs from database
- Displays in pandas DataFrame

---

## ✅ Step 7: Verify Everything Works

### Test 1: Process Single ID Card
1. Go to Cell 7 (Interactive Scanner)
2. Select an ID card from dropdown (e.g., `avanish.jpg`)
3. Click "🔍 Process ID Card"
4. Should see:
   - Original and detected images
   - Moodle ID extracted
   - Name extracted
   - Department extracted
   - "✅ Data saved to Supabase database"

### Test 2: Check Database
1. Run Cell 11 (View Logs)
2. Should see recent entries in `id_card_logs` table
3. Verify data is correct

### Test 3: Build Face Database
1. Run Cell 9 once
2. Check `face_database/` folder
3. Should contain extracted face images (e.g., `22102003.jpg`)

### Test 4: Live Camera (Optional)
1. Run Cell 10
2. Camera window opens
3. Position face in green box
4. Press SPACE
5. Should match against database

---

## 🐛 Common Issues & Solutions

### Issue 1: Module Not Found
```
ModuleNotFoundError: No module named 'cv2'
```
**Solution:**
```bash
pip install opencv-python
```

### Issue 2: CUDA Not Available
```
CUDA available: False
```
**Solution:**
- This is OK! System will use CPU (slower but works)
- For GPU support: Install CUDA Toolkit 12.1 from NVIDIA

### Issue 3: Database Connection Failed
```
psycopg2.OperationalError: connection failed
```
**Solution:**
1. Check `.env` file has correct credentials
2. Verify Supabase project is active (not paused)
3. Check internet connection
4. In Supabase dashboard: Settings → API → Disable "Email confirmations"

### Issue 4: Model File Not Found
```
FileNotFoundError: models/best.pt
```
**Solution:**
1. Verify `models/best.pt` exists
2. Check you're running notebook from correct directory
3. File size should be ~6 MB

### Issue 5: EasyOCR Slow First Time
```
Downloading detection model...
```
**Solution:**
- This is normal on first run
- EasyOCR downloads models (~200 MB)
- Subsequent runs will be fast
- Wait 5-10 minutes for download to complete

### Issue 6: Jupyter Kernel Dies
```
Kernel died, restarting...
```
**Solution:**
- System may be out of RAM
- Close other applications
- Restart notebook server
- Run cells one at a time

---

## 🎯 Quick Start Guide (TL;DR)

```bash
# 1. Extract package
cd Enhanced_Access_Control/

# 2. Create virtual environment
python -m venv venv

# 3. Activate (Windows)
.\venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements_notebook.txt

# 5. Configure database
cp .env.example .env
# Edit .env with your Supabase credentials

# 6. Start Jupyter
jupyter notebook

# 7. Open Enhanced_Access_Control.ipynb

# 8. Run all cells in order (Cell → Run All)
```

---

## 📊 System Performance

### Expected Processing Times

| Task | CPU | GPU (CUDA) |
|------|-----|------------|
| Single ID card | 3-5 sec | 1-2 sec |
| Batch (60 cards) | 3-5 min | 1-2 min |
| Face extraction | 2-3 sec | 1 sec |
| Face recognition | 4-6 sec | 2-3 sec |
| Live camera FPS | 10-15 | 25-30 |

### Storage Requirements

| Item | Size |
|------|------|
| Python packages | ~2.5 GB |
| YOLO model | ~6 MB |
| EasyOCR models | ~200 MB |
| Training data | ~15 MB |
| Face database | ~5 MB |
| Output files | Varies |
| **Total** | **~2.7 GB** |

---

## 🎓 Learning Resources

- **OpenCV Tutorial:** https://docs.opencv.org/
- **EasyOCR Documentation:** https://github.com/JaidedAI/EasyOCR
- **Ultralytics YOLO:** https://docs.ultralytics.com/
- **DeepFace Guide:** https://github.com/serengil/deepface
- **Supabase Docs:** https://supabase.com/docs

---

## 📞 Support & Contact

### Before Asking for Help:
1. ✅ Check this installation guide
2. ✅ Read `DEPLOYMENT_PACKAGE_GUIDE.md`
3. ✅ Review common issues section
4. ✅ Verify all files are present
5. ✅ Check system requirements

### Still Need Help?
- Email: avanishvadke@example.com
- GitHub: https://github.com/AvanishVadke/Hacknova-CodeBreakers

---

## ✅ Installation Complete!

If you've reached this point and all tests pass:
🎉 **Congratulations!** Your system is ready to use.

**Next Steps:**
1. Process your own ID cards
2. Build face database
3. Test live camera recognition
4. Integrate with your access control system

**Enjoy!** 🚀

---

**Last Updated:** October 4, 2025  
**Version:** 1.0
