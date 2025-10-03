# Smart Campus Access Control System

![Hackathon Project](https://img.shields.io/badge/Hackathon-Project-blue)
![License](https://img.shields.io/badge/License-MIT-green)

An intelligent campus access control system using Computer Vision (ANPR, OCR, Face Recognition) and real-time monitoring dashboards.

## 🚀 Features

- **Automatic Number Plate Recognition (ANPR)**: Detect and recognize vehicle license plates
- **ID Card OCR**: Extract student information from ID cards
- **Face Recognition**: Identify students using facial recognition
- **Live Dashboard**: Real-time monitoring of access logs and alerts
- **Reports & Analytics**: Generate comprehensive access reports
- **Security Alerts**: Instant notifications for unauthorized access attempts

## 🏗️ Project Structure

```
Hacknova-CodeBreakers/
├── frontend/              # Next.js dashboard application
│   ├── app/              # App router pages
│   ├── components/       # React components
│   └── public/           # Static assets
│
├── backend/              # FastAPI backend server
│   ├── app/
│   │   ├── routers/     # API endpoints
│   │   ├── models/      # Database models
│   │   ├── services/    # Business logic
│   │   ├── schemas/     # Pydantic schemas
│   │   └── core/        # Configuration & utilities
│   └── main.py          # FastAPI application entry
│
├── cv_pipeline/          # Computer Vision pipelines
│   ├── anpr/            # Vehicle number plate recognition
│   ├── ocr/             # ID card OCR
│   ├── face_recognition/# Face detection & matching
│   ├── models/          # Trained ML models
│   └── utils/           # Image processing utilities
│
├── data/                 # Datasets and sample data
│   ├── students.csv     # Student records
│   ├── vehicles.csv     # Vehicle registrations
│   ├── id_cards/        # Sample ID card images
│   └── temp/            # Temporary processing files
│
├── scripts/              # Utility scripts
│   ├── seed_database.py        # Database seeding
│   ├── generate_embeddings.py  # Generate face embeddings
│   ├── test_cv_pipeline.py     # Test CV components
│   └── dataset_utils.py        # Dataset management
│
├── docs/                 # Documentation
│   ├── SETUP.md         # Setup instructions
│   └── ARCHITECTURE.md  # System architecture
│
└── logs/                 # Application logs

```

## 🛠️ Tech Stack

### Frontend
- **Next.js 15** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first styling
- **Recharts** - Data visualization

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL/Supabase** - Database
- **SQLAlchemy** - ORM
- **JWT** - Authentication

### CV Pipeline
- **OpenCV** - Image processing
- **YOLOv8** - Object detection (ANPR)
- **DeepFace/FaceNet** - Face recognition
- **EasyOCR/Tesseract** - Text extraction

## 📦 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/AvanishVadke/Hacknova-CodeBreakers.git
cd Hacknova-CodeBreakers
```

### 2. Setup Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration
python main.py
```

### 3. Setup Frontend
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

### 4. Initialize Database
```bash
cd scripts
python seed_database.py
```

## 🚦 Access the Application

- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📚 Documentation

- [**Setup Guide**](docs/SETUP.md) - Complete installation instructions
- [**Architecture**](docs/ARCHITECTURE.md) - System design and architecture

## 🎯 Key Features

### 1. Vehicle Access Control
- Automatic license plate detection
- Vehicle registration management
- Entry/exit logging

### 2. Face Recognition
- Real-time face detection
- Face matching with database
- Student identification

### 3. ID Card Scanning
- OCR-based information extraction
- Automatic student verification
- Digital record creation

### 4. Dashboard
- Live access monitoring
- Analytics and reports
- Alert management
- Student/vehicle CRUD

## 🤝 Team Collaboration

### For Frontend Developers
- Work in `frontend/` directory
- Create components in `components/`
- Follow TypeScript best practices

### For Backend Developers
- Work in `backend/` directory
- Add routes in `app/routers/`
- Define models in `app/models/`

### For CV/ML Engineers
- Work in `cv_pipeline/` directory
- Implement detection in respective modules
- Test with `scripts/test_cv_pipeline.py`

## 📊 Database Schema

- **Students**: moodle_id, name, email, department, face_embedding
- **Vehicles**: plate_number, owner_moodle_id, make, model
- **Access Logs**: timestamp, entry_type, recognition_confidence, access_granted
- **Users**: username, email, role (for admin access)

## 🔒 Security Features

- JWT-based authentication
- Password hashing (bcrypt)
- CORS protection
- Input validation with Pydantic
- Secure file uploads

## 🐛 Troubleshooting

See [SETUP.md](docs/SETUP.md#troubleshooting) for common issues and solutions.

## 🚀 Future Enhancements

- [ ] Real-time video stream processing
- [ ] Mobile app integration
- [ ] Advanced analytics dashboard
- [ ] Multi-camera support
- [ ] Cloud deployment ready

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

Built with ❤️ for Hacknova by **Team CodeBreakers**

---

For detailed setup instructions, see [docs/SETUP.md](docs/SETUP.md)
Automated Smart Campus Access Control using vehicle number plate recognition, ID card OCR, and face verification. Grants or denies access in real-time, logs entries, handles multiple riders, and provides a live Next.js dashboard with alerts and reports. Built with FastAPI, Supabase, OpenCV, and YOLOv8.
