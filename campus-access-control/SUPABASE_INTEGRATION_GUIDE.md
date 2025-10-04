# 🗄️ Supabase Integration Guide

## ✅ Installation Complete

Dependencies installed:
- ✅ `python-dotenv 1.1.1` - Environment variable management
- ✅ `psycopg2-binary 2.9.10` - PostgreSQL database connector

---

## 📋 Quick Start (3 Steps)

### Step 1: Get Supabase Credentials

1. Go to your Supabase project: **https://supabase.com/dashboard**
2. Click on **Settings** → **Database**
3. Scroll to **Connection String** section
4. Copy the **URI** connection string:
   ```
   postgres://postgres.xxxxx:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
   ```

### Step 2: Create `.env` File

1. **Copy the template:**
   ```bash
   copy .env.example .env
   ```

2. **Edit `.env`** and fill in your credentials:
   ```env
   # Supabase Database Connection (PostgreSQL)
   SUPABASE_USER=postgres.xxxxx
   SUPABASE_PASSWORD=your_password_here
   SUPABASE_HOST=aws-0-us-east-1.pooler.supabase.com
   SUPABASE_PORT=6543
   SUPABASE_DBNAME=postgres
   
   # Supabase REST API (optional)
   SUPABASE_URL=https://xxxxx.supabase.co
   SUPABASE_ANON_KEY=your_anon_key
   SUPABASE_SERVICE_KEY=your_service_key
   ```

### Step 3: Test Connection

```bash
python database/supabase_manager.py
```

Expected output:
```
🔌 Connecting to Supabase database...
✅ Connected to Supabase successfully!

📦 Creating database tables...
✅ Tables created successfully!

🧪 Testing database operations...
✅ Inserted test student: 20230001
✅ Logged test ID card access
✅ Inserted test vehicle: KA 02 HN 1828
✅ Logged test vehicle access

✅ All tests passed!
```

---

## 🗃️ Database Schema

### Tables Created Automatically:

#### 1. `students` - Student Information
```sql
- id (SERIAL PRIMARY KEY)
- moodle_id (VARCHAR(20) UNIQUE) -- 8-digit ID
- name (VARCHAR(100))
- department (VARCHAR(100))
- photo_path (VARCHAR(500))
- card_image_path (VARCHAR(500))
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

#### 2. `vehicles` - Vehicle Registration
```sql
- id (SERIAL PRIMARY KEY)
- license_plate (VARCHAR(50) UNIQUE) -- e.g., KA 02 HN 1828
- owner_moodle_id (VARCHAR(20) FK → students)
- vehicle_type (VARCHAR(50))
- color (VARCHAR(50))
- model (VARCHAR(100))
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

#### 3. `id_card_logs` - ID Card Access Logs
```sql
- id (SERIAL PRIMARY KEY)
- moodle_id (VARCHAR(20) FK → students)
- name (VARCHAR(100))
- department (VARCHAR(100))
- confidence (FLOAT)
- access_time (TIMESTAMP)
- camera_id (VARCHAR(50))
- frame_path (VARCHAR(500))
- status (VARCHAR(20)) -- allowed/denied
```

#### 4. `vehicle_logs` - Vehicle Access Logs
```sql
- id (SERIAL PRIMARY KEY)
- license_plate (VARCHAR(50) FK → vehicles)
- confidence (FLOAT)
- access_time (TIMESTAMP)
- camera_id (VARCHAR(50))
- frame_path (VARCHAR(500))
- status (VARCHAR(20)) -- allowed/denied
```

#### 5. `access_statistics` - Daily Statistics
```sql
- date (DATE PRIMARY KEY)
- id_card_entries (INTEGER)
- vehicle_entries (INTEGER)
- total_entries (INTEGER)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

---

## 🚀 Usage Examples

### 1. Import Batch Results to Database

Import all 58 students from batch processing:

```bash
python -c "from database.supabase_manager import SupabaseManager; db = SupabaseManager(); db.connect(); db.create_tables(); count = db.bulk_import_students_from_json('outputs/id_card_data/batch_results_improved.json'); print(f'✅ Imported {count} students')"
```

### 2. Standalone Script - Process ID Card with Database Logging

```python
from database.supabase_manager import SupabaseManager
from offline_id_card_recognizer import OfflineIDCardRecognizer
import cv2

# Initialize
db = SupabaseManager()
db.connect()
db.create_tables()

recognizer = OfflineIDCardRecognizer()

# Process image
frame = cv2.imread('path/to/id_card.jpg')
card_bbox = recognizer.detect_id_card_opencv(frame)

if card_bbox:
    x, y, w, h = card_bbox
    card_region = frame[y:y+h, x:x+w]
    
    # Extract text
    preprocessed = recognizer.preprocess_for_ocr(card_region)
    ocr_results = recognizer.extract_text_with_ocr(preprocessed)
    card_data = recognizer.parse_id_card_text(ocr_results)
    
    # Save to database
    if card_data.get('moodle_id'):
        db.insert_student(
            moodle_id=card_data['moodle_id'],
            name=card_data.get('name'),
            department=card_data.get('department')
        )
        
        db.log_id_card_access(
            moodle_id=card_data['moodle_id'],
            name=card_data.get('name'),
            department=card_data.get('department'),
            confidence=0.85,
            camera_id='entrance_1',
            status='allowed'
        )
        
        print(f"✅ Logged access for {card_data['name']}")

db.disconnect()
```

### 3. Standalone Script - Process License Plate with Database Logging

```python
from database.supabase_manager import SupabaseManager
from test_indian_plates import IndianLicensePlateRecognizer
import cv2

# Initialize
db = SupabaseManager()
db.connect()
db.create_tables()

recognizer = IndianLicensePlateRecognizer()

# Process image
frame = cv2.imread('path/to/vehicle.jpg')
results = recognizer.model(frame, conf=0.25, verbose=False)

for result in results:
    for box in result.boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = float(box.conf[0])
        
        plate_text = recognizer.extract_plate_text(frame, x1, y1, x2, y2)
        
        if plate_text:
            # Save to database
            db.insert_vehicle(license_plate=plate_text)
            
            db.log_vehicle_access(
                license_plate=plate_text,
                confidence=conf,
                camera_id='gate_1',
                status='allowed'
            )
            
            print(f"✅ Logged access for {plate_text}")

db.disconnect()
```

### 4. Get Today's Statistics

```python
from database.supabase_manager import SupabaseManager

db = SupabaseManager()
db.connect()

# Get statistics
stats = db.get_today_statistics()
print(f"📊 Today: {stats['total_entries']} entries")
print(f"   🆔 ID Cards: {stats['id_card_entries']}")
print(f"   🚗 Vehicles: {stats['vehicle_entries']}")

# Get recent logs
id_logs = db.get_recent_id_card_logs(limit=10)
for log in id_logs:
    print(f"✅ {log['moodle_id']} - {log['name']} @ {log['access_time']}")

vehicle_logs = db.get_recent_vehicle_logs(limit=10)
for log in vehicle_logs:
    print(f"🚗 {log['license_plate']} @ {log['access_time']}")

db.disconnect()
```

---

## 🔧 Integration Points

### Files That Need Database Integration:

#### ✅ **Already Created:**
- `database/supabase_manager.py` - Core database manager
- `.env.example` - Credential template

#### 🔄 **To Be Modified:**

1. **`batch_process_id_cards.py`** - Batch Processing
   - Add `SupabaseManager` instance
   - Call `insert_student()` for each successful extraction
   - Keep JSON backup for offline mode

2. **`live_camera_visual.py`** - Live Camera Feed
   - Add `SupabaseManager` instance
   - Call `log_id_card_access()` when card detected
   - Include confidence, camera_id, frame_path

3. **`test_indian_plates.py`** - License Plate Recognition
   - Add `SupabaseManager` instance
   - Call `insert_vehicle()` for new plates
   - Call `log_vehicle_access()` for each detection

4. **`access_control_system.py`** - Unified System
   - Already exists, can be enhanced with database
   - Add logging for combined ID + vehicle access

---

## 📊 Viewing Data in Supabase Dashboard

1. Go to **https://supabase.com/dashboard**
2. Select your project
3. Click **Table Editor** in sidebar
4. View tables:
   - `students` - All registered students
   - `vehicles` - All registered vehicles
   - `id_card_logs` - Every ID card scan
   - `vehicle_logs` - Every plate detection
   - `access_statistics` - Daily summaries

---

## 🔒 Security Best Practices

### ✅ Done:
- ✅ `.env.example` created (safe to commit)
- ✅ Passwords stored in `.env` (never commit)
- ✅ Connection pooling enabled
- ✅ Prepared statements prevent SQL injection

### 🛡️ To Do:
1. **Add `.env` to `.gitignore`:**
   ```bash
   echo ".env" >> .gitignore
   ```

2. **Use read-only credentials** for query-only operations

3. **Enable Row Level Security (RLS)** in Supabase:
   - Go to Database → Policies
   - Create policies for each table

---

## 📈 Performance Optimization

### Indexes Created:
```sql
CREATE INDEX idx_students_moodle_id ON students(moodle_id);
CREATE INDEX idx_vehicles_plate ON vehicles(license_plate);
CREATE INDEX idx_id_card_logs_time ON id_card_logs(access_time);
CREATE INDEX idx_vehicle_logs_time ON vehicle_logs(access_time);
```

### Connection Pooling:
- Supabase uses PgBouncer (port 6543)
- Max 15 concurrent connections in free tier
- Use `db.disconnect()` after batch operations

---

## 🐛 Troubleshooting

### Issue 1: Connection Timeout
**Error:** `connection timeout`

**Solution:**
- Check if IP is whitelisted in Supabase
- Go to Settings → Database → Connection Pooling
- Add your IP or use `0.0.0.0/0` (not recommended for production)

### Issue 2: Too Many Connections
**Error:** `FATAL: remaining connection slots are reserved`

**Solution:**
- Use connection pooling port (6543) instead of direct (5432)
- Close connections: `db.disconnect()`
- Increase connection limit in Supabase settings

### Issue 3: Import Errors
**Error:** `No module named 'psycopg2'`

**Solution:**
```bash
pip install psycopg2-binary
```

### Issue 4: Environment Variables Not Loading
**Error:** `SUPABASE_HOST environment variable not set`

**Solution:**
- Create `.env` file in `campus-access-control` directory
- Fill in credentials from Supabase dashboard
- Restart Python script

---

## 📚 Next Steps

### Immediate:
1. ✅ Install dependencies (DONE)
2. ⏳ Create `.env` file with credentials
3. ⏳ Test connection: `python database/supabase_manager.py`
4. ⏳ Import 58 students: bulk_import script

### Short-term:
5. 🔄 Modify `batch_process_id_cards.py` for DB logging
6. 🔄 Modify `live_camera_visual.py` for real-time logging
7. 🔄 Modify `test_indian_plates.py` for vehicle logging

### Long-term:
8. 🎯 Create Flask/Streamlit dashboard
9. 🎯 Add user authentication
10. 🎯 Generate daily/weekly reports
11. 🎯 Add SMS/email notifications
12. 🎯 Implement visitor management

---

## 📞 Support

**Documentation:**
- Supabase Docs: https://supabase.com/docs
- psycopg2 Docs: https://www.psycopg.org/docs/

**Supabase Dashboard:**
- https://supabase.com/dashboard

**Database Manager Code:**
- `database/supabase_manager.py` - Full source code with comments

---

## ✅ Integration Checklist

- [x] Install python-dotenv
- [x] Install psycopg2-binary
- [x] Create database/supabase_manager.py
- [x] Create .env.example template
- [ ] Create .env with credentials
- [ ] Test connection
- [ ] Create tables
- [ ] Import 58 students
- [ ] Integrate with batch processor
- [ ] Integrate with live camera
- [ ] Integrate with plate recognizer
- [ ] Add .env to .gitignore
- [ ] Test end-to-end workflow

---

**Status:** 🟡 Ready for Credentials & Testing

**Next Action:** Create `.env` file with your Supabase credentials
