# Setup Instructions

Complete setup guide for the Smart Campus Access Control System.

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Frontend Setup](#frontend-setup)
3. [Backend Setup](#backend-setup)
4. [CV Pipeline Setup](#cv-pipeline-setup)
5. [Database Setup](#database-setup)
6. [Environment Variables](#environment-variables)
7. [Troubleshooting](#troubleshooting)

## System Requirements

### Hardware
- CPU: Quad-core processor (Intel i5 or AMD Ryzen 5 equivalent)
- RAM: 8GB minimum (16GB recommended)
- Storage: 10GB free space
- GPU: Optional (NVIDIA GPU for faster CV processing)

### Software
- **Node.js**: 18.x or higher
- **Python**: 3.9, 3.10, or 3.11
- **PostgreSQL**: 14+ (or Supabase account)
- **Git**: Latest version
- **VS Code**: Recommended IDE

## Frontend Setup

### 1. Install Node.js
Download from [nodejs.org](https://nodejs.org/)

Verify installation:
```bash
node --version
npm --version
```

### 2. Install Dependencies
```bash
cd frontend
npm install
```

### 3. Configure Environment
```bash
cp .env.example .env.local
```

Edit `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Smart Campus Access Control
```

### 4. Run Development Server
```bash
npm run dev
```

Access at: http://localhost:3000

## Backend Setup

### 1. Create Virtual Environment
```bash
cd backend

# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
```

Edit `.env`:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/campus_db
SECRET_KEY=your-secret-key-here
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
```

Generate secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 4. Run Server
```bash
python main.py
# Or
uvicorn main:app --reload --port 8000
```

Access API docs: http://localhost:8000/docs

## CV Pipeline Setup

### 1. Install Dependencies
```bash
cd cv_pipeline
pip install -r requirements.txt
```

### 2. Install Tesseract OCR
**Windows:**
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Install and add to PATH

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

**Mac:**
```bash
brew install tesseract
```

### 3. Download Pre-trained Models

#### YOLOv8 for ANPR
```bash
# Install ultralytics
pip install ultralytics

# Download model
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

#### Face Recognition Models
```bash
# DeepFace will download models automatically on first use
python -c "from deepface import DeepFace; DeepFace.build_model('Facenet')"
```

### 4. Test CV Pipeline
```bash
cd scripts
python test_cv_pipeline.py
```

## Database Setup

### Option 1: PostgreSQL (Local)

#### Install PostgreSQL
**Windows:**
- Download from: https://www.postgresql.org/download/windows/

**Linux:**
```bash
sudo apt-get install postgresql postgresql-contrib
```

**Mac:**
```bash
brew install postgresql
```

#### Create Database
```bash
# Start PostgreSQL service
# Windows: Use Services
# Linux: sudo systemctl start postgresql
# Mac: brew services start postgresql

# Create database
psql -U postgres
CREATE DATABASE campus_access_db;
CREATE USER campus_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE campus_access_db TO campus_user;
\q
```

#### Run Migrations
```bash
cd backend
alembic upgrade head
```

### Option 2: Supabase (Cloud)

1. Create account at [supabase.com](https://supabase.com)
2. Create new project
3. Copy Project URL and API Key
4. Update `.env` with Supabase credentials

### Initialize Database
```bash
cd scripts
python seed_database.py
```

## Environment Variables

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
NEXT_PUBLIC_APP_NAME=Smart Campus Access Control
```

### Backend (.env)
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/campus_db

# Supabase (if using)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_role_key

# JWT
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# File Upload
MAX_UPLOAD_SIZE=10485760
UPLOAD_DIR=uploads

# CV Pipeline
FACE_RECOGNITION_THRESHOLD=0.6
ANPR_CONFIDENCE_THRESHOLD=0.75

# Environment
ENVIRONMENT=development
DEBUG=True
```

## Generate Initial Data

### 1. Generate Face Embeddings
```bash
cd scripts
python generate_embeddings.py
```

### 2. Add Sample Data
```bash
python dataset_utils.py
```

## Verify Installation

### Backend Health Check
```bash
curl http://localhost:8000/health
```

### Frontend Check
Open browser: http://localhost:3000

### Database Connection
```bash
cd backend
python -c "from app.core.database import engine; print('Database connected!' if engine else 'Failed')"
```

## Troubleshooting

### Port Already in Use
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Python Module Not Found
```bash
pip install -r requirements.txt --upgrade
```

### Database Connection Error
- Check PostgreSQL service is running
- Verify credentials in .env
- Check DATABASE_URL format

### CORS Errors
- Add frontend URL to ALLOWED_ORIGINS in backend/.env
- Restart backend server

### OpenCV Import Error
```bash
pip uninstall opencv-python opencv-contrib-python
pip install opencv-contrib-python
```

### Tesseract Not Found
- Ensure Tesseract is installed
- Add to system PATH
- Or set in code:
```python
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

## Next Steps

1. Review API documentation: http://localhost:8000/docs
2. Read [Architecture Guide](ARCHITECTURE.md)
3. Check [API Documentation](API.md)
4. Start developing your features!

## Support

For issues and questions:
- Create an issue on GitHub
- Contact team members
- Check documentation in `docs/`

---

Happy Coding! 🚀
