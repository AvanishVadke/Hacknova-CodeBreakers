# System Architecture

## Overview

The Smart Campus Access Control System is a full-stack application combining Computer Vision, Backend APIs, and a Real-time Dashboard.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                            │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  Next.js App (TypeScript + Tailwind)                  │ │
│  │  - Dashboard (Real-time updates)                      │ │
│  │  - Reports & Analytics                                │ │
│  │  - Alerts Management                                  │ │
│  │  - Student/Vehicle Management                         │ │
│  └───────────────────────────────────────────────────────┘ │
└───────────────────────┬─────────────────────────────────────┘
                        │ REST API / WebSocket
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI)                      │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  API Layer (Routers)                                  │ │
│  │  - Authentication (JWT)                               │ │
│  │  - Students CRUD                                      │ │
│  │  - Vehicles CRUD                                      │ │
│  │  - Access Logs                                        │ │
│  │  - Alerts                                             │ │
│  └───────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  Service Layer                                        │ │
│  │  - Business Logic                                     │ │
│  │  - CV Pipeline Integration                            │ │
│  └───────────────────────────────────────────────────────┘ │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  Data Layer (SQLAlchemy ORM)                          │ │
│  └───────────────────────────────────────────────────────┘ │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              DATABASE (PostgreSQL/Supabase)                 │
│  - students (face_embeddings)                               │
│  - vehicles (plate_numbers)                                 │
│  - access_logs (entry records)                              │
│  - users (admin accounts)                                   │
└─────────────────────────────────────────────────────────────┘

                        ▲
                        │
┌─────────────────────────────────────────────────────────────┐
│                     CV PIPELINE                             │
│  ┌───────────────┐  ┌────────────────┐  ┌───────────────┐ │
│  │  ANPR Module  │  │  OCR Module    │  │ Face Recog    │ │
│  │  - YOLOv8     │  │  - Tesseract   │  │ - DeepFace    │ │
│  │  - Plate OCR  │  │  - EasyOCR     │  │ - FaceNet     │ │
│  └───────────────┘  └────────────────┘  └───────────────┘ │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │  Utilities & Models                                   │ │
│  │  - Image preprocessing                                │ │
│  │  - Pre-trained models                                 │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Frontend (Next.js)

**Technology Stack:**
- Next.js 15 (App Router)
- TypeScript
- Tailwind CSS
- React Server Components

**Key Features:**
- **Dashboard**: Real-time access monitoring
- **Reports**: Generate PDF/CSV reports
- **Alerts**: Security notifications
- **Management**: CRUD for students/vehicles

**Data Flow:**
1. User interacts with UI
2. React components fetch data via API calls
3. Server components handle initial data loading
4. Client components manage real-time updates

### 2. Backend (FastAPI)

**Technology Stack:**
- FastAPI (Python)
- SQLAlchemy ORM
- Pydantic for validation
- JWT authentication

**Architecture Layers:**

#### a) Router Layer (`app/routers/`)
- Define API endpoints
- Request/response handling
- Input validation

#### b) Service Layer (`app/services/`)
- Business logic implementation
- CV pipeline integration
- Data processing

#### c) Model Layer (`app/models/`)
- Database schema definition
- Relationships between entities

#### d) Core Layer (`app/core/`)
- Configuration management
- Database connection
- Security utilities

**Authentication Flow:**
```
User Login → Validate Credentials → Generate JWT → Return Token
Protected Route → Verify JWT → Allow/Deny Access
```

### 3. CV Pipeline

**Modules:**

#### a) ANPR (Automatic Number Plate Recognition)
```
Vehicle Image → YOLOv8 Detection → Plate Localization → 
OCR (Tesseract) → Plate Number Extraction
```

**Components:**
- Plate detection using YOLOv8
- Image preprocessing (grayscale, thresholding)
- Character recognition
- Post-processing (format validation)

#### b) ID Card OCR
```
ID Card Image → Preprocessing → Text Detection → 
OCR → Information Extraction → Validation
```

**Extracted Fields:**
- Moodle ID
- Student Name
- Department
- Photo (for face embedding)

#### c) Face Recognition
```
Image → Face Detection (MTCNN) → Face Alignment → 
Embedding Generation (FaceNet) → Database Matching → 
Identity Verification
```

**Process:**
1. **Detection**: Locate faces in image
2. **Alignment**: Normalize face orientation
3. **Embedding**: Generate 128/512-d vector
4. **Matching**: Compare with database embeddings
5. **Verification**: Threshold-based decision

### 4. Database Schema

#### Students Table
```sql
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    moodle_id VARCHAR UNIQUE NOT NULL,
    name VARCHAR NOT NULL,
    email VARCHAR UNIQUE,
    department VARCHAR,
    phone VARCHAR,
    face_embedding JSON,  -- Array of face embeddings
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### Vehicles Table
```sql
CREATE TABLE vehicles (
    id SERIAL PRIMARY KEY,
    plate_number VARCHAR UNIQUE NOT NULL,
    owner_moodle_id VARCHAR REFERENCES students(moodle_id),
    make VARCHAR,
    model VARCHAR,
    color VARCHAR,
    vehicle_type VARCHAR,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

#### Access Logs Table
```sql
CREATE TABLE access_logs (
    id SERIAL PRIMARY KEY,
    student_moodle_id VARCHAR REFERENCES students(moodle_id),
    vehicle_plate VARCHAR REFERENCES vehicles(plate_number),
    entry_type VARCHAR,  -- 'vehicle', 'face', 'id_card'
    recognition_confidence FLOAT,
    access_granted BOOLEAN,
    is_alert BOOLEAN,
    alert_reason VARCHAR,
    location VARCHAR,
    image_path VARCHAR,
    additional_data JSON,
    timestamp TIMESTAMP
);
```

## Data Flow

### Access Control Flow

1. **Image Capture**
   - Camera captures image/video
   - Image sent to CV pipeline

2. **Recognition**
   - CV module processes image
   - Extracts identifying information
   - Returns confidence score

3. **Verification**
   - Backend queries database
   - Matches against registered records
   - Determines access permission

4. **Logging**
   - Creates access log entry
   - Triggers alerts if necessary
   - Updates dashboard in real-time

5. **Response**
   - Grants/denies access
   - Displays result on UI
   - Notifies security personnel

### Complete Access Flow Diagram

```
┌─────────────┐
│   Camera    │
└──────┬──────┘
       │ Capture Image
       ▼
┌─────────────┐
│ CV Pipeline │
│ (ANPR/Face/ │
│    OCR)     │
└──────┬──────┘
       │ Extract Info
       ▼
┌─────────────┐
│   Backend   │
│   Verify    │
└──────┬──────┘
       │ Database Query
       ▼
┌─────────────┐
│  Database   │
│   Match     │
└──────┬──────┘
       │ Result
       ▼
┌─────────────┐
│ Access Log  │
│   Create    │
└──────┬──────┘
       │
       ├──────► Dashboard Update (Real-time)
       ├──────► Alert (if unauthorized)
       └──────► Grant/Deny Access
```

## Security Considerations

### Authentication
- JWT tokens with expiration
- Password hashing (bcrypt)
- Role-based access control

### Data Protection
- HTTPS for all communications
- Encrypted database connections
- Sensitive data encryption

### Privacy
- Face embeddings stored (not raw images)
- GDPR compliance considerations
- Access log retention policies

## Scalability

### Horizontal Scaling
- Stateless backend (multiple instances)
- Load balancer for API requests
- Database connection pooling

### Performance Optimization
- Image processing queue
- Caching frequently accessed data
- Database indexing on queries
- Async processing for CV tasks

### Monitoring
- Application logs
- Performance metrics
- Error tracking
- Real-time alerts

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Production Environment                  │
│                                                           │
│  ┌─────────────┐                                         │
│  │   Vercel    │ ← Frontend (Next.js)                   │
│  └─────────────┘                                         │
│                                                           │
│  ┌─────────────┐                                         │
│  │   Railway/  │ ← Backend (FastAPI)                    │
│  │   Render    │                                         │
│  └─────────────┘                                         │
│                                                           │
│  ┌─────────────┐                                         │
│  │  Supabase   │ ← Database (PostgreSQL)                │
│  └─────────────┘                                         │
│                                                           │
│  ┌─────────────┐                                         │
│  │   AWS S3    │ ← File Storage (Images, Models)        │
│  └─────────────┘                                         │
└─────────────────────────────────────────────────────────┘
```

## Technology Choices

### Why Next.js?
- Server-side rendering
- API routes
- Excellent developer experience
- Production-ready optimizations

### Why FastAPI?
- High performance (async support)
- Automatic API documentation
- Type hints and validation
- Easy to learn and use

### Why PostgreSQL?
- Robust and reliable
- JSON support for embeddings
- Strong consistency
- Great ecosystem

### Why OpenCV?
- Industry standard
- Comprehensive functionality
- Active community
- Good documentation

---

For implementation details, see individual module documentation.
