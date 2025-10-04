# 🗄️ Supabase Database Integration

Complete guide for integrating Supabase PostgreSQL database with the campus access control system.

---

## 📦 Installation Status

✅ **Dependencies Installed:**
- `python-dotenv 1.1.1` - Environment variable management
- `psycopg2-binary 2.9.10` - PostgreSQL database connector

---

## 🚀 Quick Start (3 Commands)

### 1. Get Supabase Credentials
Go to: **https://supabase.com/dashboard** → Your Project → Settings → Database

Copy your connection string:
```
postgres://postgres.xxxxx:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
```

### 2. Create `.env` File
```bash
copy .env.example .env
```

Edit `.env` with your credentials:
```env
SUPABASE_USER=postgres.xxxxx
SUPABASE_PASSWORD=your_password_here
SUPABASE_HOST=aws-0-us-east-1.pooler.supabase.com
SUPABASE_PORT=6543
SUPABASE_DBNAME=postgres
```

### 3. Run Setup Script
```bash
python setup_supabase.py
```

The script will:
- ✅ Test connection
- ✅ Create all tables
- ✅ Import 58 students from batch results
- ✅ Show statistics

---

## 📁 Files Created

### Core Database Files:
```
campus-access-control/
├── database/
│   ├── __init__.py
│   └── supabase_manager.py         # 450+ lines - Complete DB manager
│
├── .env.example                     # Credential template (safe to commit)
├── .env                             # Your credentials (NEVER commit)
├── setup_supabase.py                # Interactive setup utility
├── SUPABASE_INTEGRATION_GUIDE.md   # Detailed documentation
└── DATABASE_README.md               # This file
```

### Database Manager Features:
- ✅ Connection management with error handling
- ✅ 5 tables: students, vehicles, id_card_logs, vehicle_logs, access_statistics
- ✅ CRUD operations for all tables
- ✅ Bulk import from JSON
- ✅ Statistics tracking
- ✅ Recent logs retrieval
- ✅ Foreign keys and indexes for performance
- ✅ ON CONFLICT handling for upserts

---

## 🗃️ Database Schema

### Tables:

#### 1. **students** - Student Registry
```sql
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    moodle_id VARCHAR(20) UNIQUE NOT NULL,  -- e.g., 20230001
    name VARCHAR(100),
    department VARCHAR(100),
    photo_path VARCHAR(500),
    card_image_path VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_students_moodle_id ON students(moodle_id);
```

#### 2. **vehicles** - Vehicle Registry
```sql
CREATE TABLE vehicles (
    id SERIAL PRIMARY KEY,
    license_plate VARCHAR(50) UNIQUE NOT NULL,  -- e.g., KA 02 HN 1828
    owner_moodle_id VARCHAR(20) REFERENCES students(moodle_id),
    vehicle_type VARCHAR(50),
    color VARCHAR(50),
    model VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_vehicles_plate ON vehicles(license_plate);
```

#### 3. **id_card_logs** - ID Card Access History
```sql
CREATE TABLE id_card_logs (
    id SERIAL PRIMARY KEY,
    moodle_id VARCHAR(20) REFERENCES students(moodle_id),
    name VARCHAR(100),
    department VARCHAR(100),
    confidence FLOAT,
    access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    camera_id VARCHAR(50),
    frame_path VARCHAR(500),
    status VARCHAR(20) DEFAULT 'allowed'
);
CREATE INDEX idx_id_card_logs_time ON id_card_logs(access_time);
```

#### 4. **vehicle_logs** - Vehicle Access History
```sql
CREATE TABLE vehicle_logs (
    id SERIAL PRIMARY KEY,
    license_plate VARCHAR(50) REFERENCES vehicles(license_plate),
    confidence FLOAT,
    access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    camera_id VARCHAR(50),
    frame_path VARCHAR(500),
    status VARCHAR(20) DEFAULT 'allowed'
);
CREATE INDEX idx_vehicle_logs_time ON vehicle_logs(access_time);
```

#### 5. **access_statistics** - Daily Summary
```sql
CREATE TABLE access_statistics (
    date DATE PRIMARY KEY,
    id_card_entries INTEGER DEFAULT 0,
    vehicle_entries INTEGER DEFAULT 0,
    total_entries INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 💻 Usage Examples

### Example 1: Import Batch Results

Import all 58 students from batch processing:

```bash
python setup_supabase.py
# Select option 2: Import Batch Results
```

Or programmatically:
```python
from database.supabase_manager import SupabaseManager

db = SupabaseManager()
db.connect()
db.create_tables()

count = db.bulk_import_students_from_json(
    'outputs/id_card_data/batch_results_improved.json'
)
print(f"✅ Imported {count} students")

db.disconnect()
```

### Example 2: Log ID Card Access

```python
from database.supabase_manager import SupabaseManager

db = SupabaseManager()
db.connect()

# Insert/update student
db.insert_student(
    moodle_id='20210001',
    name='John Doe',
    department='COMPUTER ENGINEERING'
)

# Log access
db.log_id_card_access(
    moodle_id='20210001',
    name='John Doe',
    department='COMPUTER ENGINEERING',
    confidence=0.95,
    camera_id='entrance_1',
    frame_path='/path/to/frame.jpg',
    status='allowed'
)

print("✅ Access logged")
db.disconnect()
```

### Example 3: Log Vehicle Access

```python
from database.supabase_manager import SupabaseManager

db = SupabaseManager()
db.connect()

# Register vehicle
db.insert_vehicle(
    license_plate='KA 02 HN 1828',
    owner_moodle_id='20210001',
    vehicle_type='Car',
    color='Silver',
    model='Honda City'
)

# Log access
db.log_vehicle_access(
    license_plate='KA 02 HN 1828',
    confidence=0.90,
    camera_id='gate_1',
    frame_path='/path/to/frame.jpg',
    status='allowed'
)

print("✅ Vehicle access logged")
db.disconnect()
```

### Example 4: Get Statistics

```python
from database.supabase_manager import SupabaseManager

db = SupabaseManager()
db.connect()

# Today's stats
stats = db.get_today_statistics()
print(f"📊 Today: {stats['total_entries']} entries")
print(f"   🆔 ID Cards: {stats['id_card_entries']}")
print(f"   🚗 Vehicles: {stats['vehicle_entries']}")

# Recent ID card logs
id_logs = db.get_recent_id_card_logs(limit=10)
for log in id_logs:
    print(f"{log['moodle_id']} - {log['name']} @ {log['access_time']}")

# Recent vehicle logs
vehicle_logs = db.get_recent_vehicle_logs(limit=10)
for log in vehicle_logs:
    print(f"{log['license_plate']} @ {log['access_time']}")

db.disconnect()
```

### Example 5: Query Students

```python
from database.supabase_manager import SupabaseManager

db = SupabaseManager()
db.connect()

# Get student by Moodle ID
student = db.get_student(moodle_id='20210001')
if student:
    print(f"Name: {student['name']}")
    print(f"Dept: {student['department']}")

# Get vehicle by plate
vehicle = db.get_vehicle(license_plate='KA 02 HN 1828')
if vehicle:
    print(f"Owner: {vehicle['owner_moodle_id']}")
    print(f"Type: {vehicle['vehicle_type']}")

db.disconnect()
```

---

## 🔧 Integration with Existing Code

### Modify `batch_process_id_cards.py`

Add after successful extraction:

```python
# At the top
from database.supabase_manager import SupabaseManager

# In __init__
self.db = SupabaseManager()
if self.db.connect():
    self.db.create_tables()

# After successful extraction
if card_data.get('moodle_id'):
    self.db.insert_student(
        moodle_id=card_data['moodle_id'],
        name=card_data.get('name'),
        department=card_data.get('department'),
        card_image_path=image_path
    )
```

### Modify `live_camera_visual.py`

Add real-time logging:

```python
# At the top
from database.supabase_manager import SupabaseManager

# In __init__
self.db = SupabaseManager()
if self.db.connect():
    self.db.create_tables()

# When card detected
if card_data.get('moodle_id'):
    self.db.log_id_card_access(
        moodle_id=card_data['moodle_id'],
        name=card_data.get('name'),
        department=card_data.get('department'),
        confidence=card_data.get('confidence', 0.0),
        camera_id='live_camera_1',
        status='allowed'
    )
```

### Modify `test_indian_plates.py`

Add vehicle logging:

```python
# At the top
from database.supabase_manager import SupabaseManager

# In __init__
self.db = SupabaseManager()
if self.db.connect():
    self.db.create_tables()

# When plate detected
if plate_text:
    self.db.insert_vehicle(license_plate=plate_text)
    self.db.log_vehicle_access(
        license_plate=plate_text,
        confidence=conf,
        camera_id='gate_camera_1',
        status='allowed'
    )
```

---

## 🎯 Data Flow

### ID Card Scanning Flow:
```
1. Camera captures frame
2. YOLO detects ID card
3. EasyOCR extracts text
4. Smart validation cleans data
5. SupabaseManager.insert_student() → students table
6. SupabaseManager.log_id_card_access() → id_card_logs table
7. Statistics auto-updated
```

### Vehicle Plate Flow:
```
1. Camera captures frame
2. YOLO detects plate
3. EasyOCR extracts text
4. Indian plate formatting
5. SupabaseManager.insert_vehicle() → vehicles table
6. SupabaseManager.log_vehicle_access() → vehicle_logs table
7. Statistics auto-updated
```

---

## 🔒 Security

### ✅ Implemented:
- Environment variables for credentials
- Connection pooling (port 6543)
- Prepared statements (SQL injection prevention)
- Unique constraints on Moodle ID and license plate
- Foreign key constraints for data integrity
- Indexes for query performance

### 🛡️ Recommended:
1. **Add `.env` to `.gitignore`:**
   ```bash
   echo ".env" >> .gitignore
   ```

2. **Enable Row Level Security (RLS)** in Supabase:
   - Go to Dashboard → Database → Policies
   - Create policies for each table

3. **Use read-only user** for query-only operations

4. **Whitelist IPs** in Supabase settings (production)

---

## 📊 Viewing Data

### Supabase Dashboard:
1. Go to **https://supabase.com/dashboard**
2. Select your project
3. Click **Table Editor**
4. Browse all tables and data

### Using `setup_supabase.py`:
```bash
python setup_supabase.py
# Select option 3: View Today's Statistics
# Select option 4: View Recent Logs
```

---

## 🐛 Troubleshooting

### Issue 1: Connection Timeout
**Error:** `connection to server ... failed: timeout expired`

**Solution:**
- Go to Supabase Dashboard → Settings → Database
- Check "Connection Pooling" section
- Add your IP address to allowed IPs (or use 0.0.0.0/0 for testing)

### Issue 2: Import Errors
**Error:** `No module named 'psycopg2'`

**Solution:**
```bash
pip install psycopg2-binary
```

### Issue 3: Environment Variables Not Loading
**Error:** `SUPABASE_HOST environment variable not set`

**Solution:**
- Ensure `.env` file is in `campus-access-control` directory
- Check file content (copy from `.env.example`)
- Restart Python script

### Issue 4: Table Already Exists
**Error:** `relation "students" already exists`

**Solution:**
- Tables were already created (this is OK)
- Use `db.insert_student()` to add data

### Issue 5: Foreign Key Constraint
**Error:** `violates foreign key constraint`

**Solution:**
- Insert student first before logging access
- Or remove `owner_moodle_id` when inserting vehicle

---

## 📈 Performance Tips

1. **Use connection pooling** (port 6543 instead of 5432)
2. **Close connections** after batch operations: `db.disconnect()`
3. **Use bulk imports** for large datasets
4. **Query recent logs only** (use `limit` parameter)
5. **Create indexes** on frequently queried columns (already done)

---

## ✅ Setup Checklist

- [x] Install python-dotenv
- [x] Install psycopg2-binary
- [x] Create database/supabase_manager.py
- [x] Create .env.example
- [x] Create setup_supabase.py
- [ ] Create .env with your credentials
- [ ] Run python setup_supabase.py
- [ ] Test connection (option 1)
- [ ] Import 58 students (option 2)
- [ ] View statistics (option 3)
- [ ] Integrate with batch processor
- [ ] Integrate with live camera
- [ ] Integrate with plate recognizer
- [ ] Add .env to .gitignore

---

## 📞 Support & Resources

**Supabase:**
- Dashboard: https://supabase.com/dashboard
- Docs: https://supabase.com/docs
- Python Client: https://supabase.com/docs/reference/python

**psycopg2:**
- Docs: https://www.psycopg.org/docs/
- FAQ: https://www.psycopg.org/docs/faq.html

**Project Files:**
- Database Manager: `database/supabase_manager.py`
- Setup Script: `setup_supabase.py`
- Integration Guide: `SUPABASE_INTEGRATION_GUIDE.md`

---

## 🎯 Next Steps

### Immediate (Do Now):
1. Create `.env` file with Supabase credentials
2. Run `python setup_supabase.py` → Option 5 (Run All Setup)
3. Verify 58 students imported
4. Check Supabase dashboard to see data

### Short-term (This Week):
5. Integrate `batch_process_id_cards.py` with database
6. Integrate `live_camera_visual.py` with database
7. Integrate `test_indian_plates.py` with database
8. Test end-to-end workflow

### Long-term (Future):
9. Create Flask/Streamlit dashboard
10. Add user authentication
11. Generate PDF reports
12. Add email/SMS notifications
13. Implement visitor management
14. Add face recognition integration

---

**Status:** 🟢 **Ready for Use**

**Last Updated:** 2025-01-04

**Dependencies:** ✅ Installed

**Next Action:** Create `.env` file and run `python setup_supabase.py`
