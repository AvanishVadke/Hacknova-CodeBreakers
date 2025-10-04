"""
Supabase Database Manager
Handles all database operations for the campus access control system
Stores ID card data, vehicle plates, and access logs
"""

import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
from dotenv import load_dotenv
import os
from datetime import datetime
from pathlib import Path
import json

# Load environment variables
load_dotenv()


class SupabaseManager:
    """
    Manages Supabase database connections and operations
    """
    
    def __init__(self):
        """Initialize database connection"""
        self.connection = None
        self.cursor = None
        
        # Load credentials
        self.user = os.getenv("SUPABASE_USER")
        self.password = os.getenv("SUPABASE_PASSWORD")
        self.host = os.getenv("SUPABASE_HOST")
        self.port = os.getenv("SUPABASE_PORT", "5432")
        self.dbname = os.getenv("SUPABASE_DBNAME")
        
        print("=" * 70)
        print("🗄️  SUPABASE DATABASE MANAGER")
        print("=" * 70)
    
    def connect(self):
        """Connect to Supabase database"""
        try:
            self.connection = psycopg2.connect(
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                dbname=self.dbname
            )
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            print("✅ Connected to Supabase database")
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to Supabase: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("🔌 Disconnected from database")
    
    def create_tables(self):
        """Create all required tables for campus access control"""
        try:
            # Students table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id SERIAL PRIMARY KEY,
                    moodle_id VARCHAR(20) UNIQUE NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    department VARCHAR(100),
                    photo_path TEXT,
                    card_image_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Vehicles table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS vehicles (
                    id SERIAL PRIMARY KEY,
                    license_plate VARCHAR(20) UNIQUE NOT NULL,
                    owner_moodle_id VARCHAR(20),
                    vehicle_type VARCHAR(50),
                    color VARCHAR(50),
                    model VARCHAR(100),
                    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (owner_moodle_id) REFERENCES students(moodle_id)
                );
            """)
            
            # ID card access logs
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS id_card_logs (
                    id SERIAL PRIMARY KEY,
                    moodle_id VARCHAR(20),
                    name VARCHAR(100),
                    department VARCHAR(100),
                    confidence_score FLOAT,
                    access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    camera_id VARCHAR(50),
                    frame_path TEXT,
                    status VARCHAR(20) DEFAULT 'allowed',
                    FOREIGN KEY (moodle_id) REFERENCES students(moodle_id)
                );
            """)
            
            # Vehicle access logs
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS vehicle_logs (
                    id SERIAL PRIMARY KEY,
                    license_plate VARCHAR(20),
                    confidence_score FLOAT,
                    access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    camera_id VARCHAR(50),
                    frame_path TEXT,
                    status VARCHAR(20) DEFAULT 'allowed',
                    FOREIGN KEY (license_plate) REFERENCES vehicles(license_plate)
                );
            """)
            
            # Access statistics
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS access_statistics (
                    id SERIAL PRIMARY KEY,
                    date DATE DEFAULT CURRENT_DATE,
                    id_card_entries INT DEFAULT 0,
                    vehicle_entries INT DEFAULT 0,
                    total_entries INT DEFAULT 0,
                    UNIQUE(date)
                );
            """)
            
            # Create indexes for performance
            self.cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_students_moodle_id ON students(moodle_id);
                CREATE INDEX IF NOT EXISTS idx_vehicles_plate ON vehicles(license_plate);
                CREATE INDEX IF NOT EXISTS idx_id_logs_time ON id_card_logs(access_time);
                CREATE INDEX IF NOT EXISTS idx_vehicle_logs_time ON vehicle_logs(access_time);
            """)
            
            self.connection.commit()
            print("✅ All tables created successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            self.connection.rollback()
            return False
    
    def insert_student(self, moodle_id, name, department=None, photo_path=None, card_image_path=None):
        """Insert or update student record"""
        try:
            self.cursor.execute("""
                INSERT INTO students (moodle_id, name, department, photo_path, card_image_path)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (moodle_id) 
                DO UPDATE SET 
                    name = EXCLUDED.name,
                    department = EXCLUDED.department,
                    photo_path = EXCLUDED.photo_path,
                    card_image_path = EXCLUDED.card_image_path,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id;
            """, (moodle_id, name, department, photo_path, card_image_path))
            
            result = self.cursor.fetchone()
            self.connection.commit()
            print(f"✅ Student {moodle_id} - {name} saved")
            return result['id']
            
        except Exception as e:
            print(f"❌ Error inserting student: {e}")
            self.connection.rollback()
            return None
    
    def insert_vehicle(self, license_plate, owner_moodle_id=None, vehicle_type=None, color=None, model=None):
        """Insert or update vehicle record"""
        try:
            self.cursor.execute("""
                INSERT INTO vehicles (license_plate, owner_moodle_id, vehicle_type, color, model)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (license_plate) 
                DO UPDATE SET 
                    owner_moodle_id = EXCLUDED.owner_moodle_id,
                    vehicle_type = EXCLUDED.vehicle_type,
                    color = EXCLUDED.color,
                    model = EXCLUDED.model
                RETURNING id;
            """, (license_plate, owner_moodle_id, vehicle_type, color, model))
            
            result = self.cursor.fetchone()
            self.connection.commit()
            print(f"✅ Vehicle {license_plate} saved")
            return result['id']
            
        except Exception as e:
            print(f"❌ Error inserting vehicle: {e}")
            self.connection.rollback()
            return None
    
    def log_id_card_access(self, moodle_id, name, department=None, confidence=None, 
                          camera_id=None, frame_path=None, status='allowed'):
        """Log an ID card access event"""
        try:
            self.cursor.execute("""
                INSERT INTO id_card_logs 
                (moodle_id, name, department, confidence_score, camera_id, frame_path, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, (moodle_id, name, department, confidence, camera_id, frame_path, status))
            
            result = self.cursor.fetchone()
            self.connection.commit()
            
            # Update statistics
            self._update_statistics('id_card')
            
            print(f"✅ ID card access logged: {moodle_id} - {name}")
            return result['id']
            
        except Exception as e:
            print(f"❌ Error logging ID card access: {e}")
            self.connection.rollback()
            return None
    
    def log_vehicle_access(self, license_plate, confidence=None, camera_id=None, 
                          frame_path=None, status='allowed'):
        """Log a vehicle access event"""
        try:
            self.cursor.execute("""
                INSERT INTO vehicle_logs 
                (license_plate, confidence_score, camera_id, frame_path, status)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id;
            """, (license_plate, confidence, camera_id, frame_path, status))
            
            result = self.cursor.fetchone()
            self.connection.commit()
            
            # Update statistics
            self._update_statistics('vehicle')
            
            print(f"✅ Vehicle access logged: {license_plate}")
            return result['id']
            
        except Exception as e:
            print(f"❌ Error logging vehicle access: {e}")
            self.connection.rollback()
            return None
    
    def _update_statistics(self, access_type):
        """Update daily access statistics"""
        try:
            if access_type == 'id_card':
                self.cursor.execute("""
                    INSERT INTO access_statistics (date, id_card_entries, total_entries)
                    VALUES (CURRENT_DATE, 1, 1)
                    ON CONFLICT (date) 
                    DO UPDATE SET 
                        id_card_entries = access_statistics.id_card_entries + 1,
                        total_entries = access_statistics.total_entries + 1;
                """)
            elif access_type == 'vehicle':
                self.cursor.execute("""
                    INSERT INTO access_statistics (date, vehicle_entries, total_entries)
                    VALUES (CURRENT_DATE, 1, 1)
                    ON CONFLICT (date) 
                    DO UPDATE SET 
                        vehicle_entries = access_statistics.vehicle_entries + 1,
                        total_entries = access_statistics.total_entries + 1;
                """)
            
            self.connection.commit()
            
        except Exception as e:
            print(f"⚠️  Warning: Could not update statistics: {e}")
    
    def get_student(self, moodle_id):
        """Get student details by Moodle ID"""
        try:
            self.cursor.execute("""
                SELECT * FROM students WHERE moodle_id = %s;
            """, (moodle_id,))
            
            return self.cursor.fetchone()
            
        except Exception as e:
            print(f"❌ Error fetching student: {e}")
            return None
    
    def get_vehicle(self, license_plate):
        """Get vehicle details by license plate"""
        try:
            self.cursor.execute("""
                SELECT v.*, s.name as owner_name, s.department as owner_department
                FROM vehicles v
                LEFT JOIN students s ON v.owner_moodle_id = s.moodle_id
                WHERE v.license_plate = %s;
            """, (license_plate,))
            
            return self.cursor.fetchone()
            
        except Exception as e:
            print(f"❌ Error fetching vehicle: {e}")
            return None
    
    def get_recent_id_card_logs(self, limit=10):
        """Get recent ID card access logs"""
        try:
            self.cursor.execute("""
                SELECT * FROM id_card_logs 
                ORDER BY access_time DESC 
                LIMIT %s;
            """, (limit,))
            
            return self.cursor.fetchall()
            
        except Exception as e:
            print(f"❌ Error fetching logs: {e}")
            return []
    
    def get_recent_vehicle_logs(self, limit=10):
        """Get recent vehicle access logs"""
        try:
            self.cursor.execute("""
                SELECT * FROM vehicle_logs 
                ORDER BY access_time DESC 
                LIMIT %s;
            """, (limit,))
            
            return self.cursor.fetchall()
            
        except Exception as e:
            print(f"❌ Error fetching logs: {e}")
            return []
    
    def get_today_statistics(self):
        """Get today's access statistics"""
        try:
            self.cursor.execute("""
                SELECT * FROM access_statistics 
                WHERE date = CURRENT_DATE;
            """)
            
            return self.cursor.fetchone()
            
        except Exception as e:
            print(f"❌ Error fetching statistics: {e}")
            return None
    
    def bulk_import_students_from_json(self, json_path):
        """Import students from batch processing JSON"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            inserted = 0
            for record in data:
                if record.get('success') and record.get('moodle_id'):
                    result = self.insert_student(
                        moodle_id=record['moodle_id'],
                        name=record.get('name'),
                        department=record.get('department'),
                        card_image_path=record.get('image_path')
                    )
                    if result:
                        inserted += 1
            
            print(f"✅ Imported {inserted} students from {json_path}")
            return inserted
            
        except Exception as e:
            print(f"❌ Error importing students: {e}")
            return 0


def test_connection():
    """Test database connection and setup"""
    db = SupabaseManager()
    
    if db.connect():
        # Create tables
        db.create_tables()
        
        # Test insert
        print("\n📝 Testing student insert...")
        db.insert_student(
            moodle_id="22102003",
            name="AVANISH VADKE",
            department="COMPUTER ENGINEERING"
        )
        
        print("\n📝 Testing vehicle insert...")
        db.insert_vehicle(
            license_plate="KA 02 HN 1828",
            owner_moodle_id="22102003",
            vehicle_type="Car"
        )
        
        print("\n📝 Testing access log...")
        db.log_id_card_access(
            moodle_id="22102003",
            name="AVANISH VADKE",
            department="COMPUTER ENGINEERING",
            confidence=0.95,
            camera_id="entrance_1",
            status="allowed"
        )
        
        print("\n📊 Today's statistics:")
        stats = db.get_today_statistics()
        if stats:
            print(f"  ID Cards: {stats['id_card_entries']}")
            print(f"  Vehicles: {stats['vehicle_entries']}")
            print(f"  Total: {stats['total_entries']}")
        
        db.disconnect()
        print("\n✅ All tests passed!")


if __name__ == "__main__":
    test_connection()
