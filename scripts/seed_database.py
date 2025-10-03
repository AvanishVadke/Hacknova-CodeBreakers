"""
Database Seeding Script
Populates database with initial data from CSV files
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.database import Base
from backend.app.models.student import Student
from backend.app.models.vehicle import Vehicle
from backend.app.core.config import settings
from datetime import datetime

def seed_database():
    """
    Seed database with initial data from CSV files
    """
    print("🌱 Starting database seeding...")
    
    # Create engine and session
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Load students CSV
        students_df = pd.read_csv('data/students.csv')
        print(f"📚 Loading {len(students_df)} students...")
        
        for _, row in students_df.iterrows():
            student = Student(
                moodle_id=row['moodle_id'],
                name=row['name'],
                email=row['email'],
                department=row['department'],
                phone=row.get('phone', ''),
                is_active=True
            )
            db.add(student)
        
        db.commit()
        print("✅ Students loaded successfully")
        
        # Load vehicles CSV
        vehicles_df = pd.read_csv('data/vehicles.csv')
        print(f"🚗 Loading {len(vehicles_df)} vehicles...")
        
        for _, row in vehicles_df.iterrows():
            vehicle = Vehicle(
                plate_number=row['plate_number'],
                owner_moodle_id=row['owner_moodle_id'],
                make=row.get('make', ''),
                model=row.get('model', ''),
                color=row.get('color', ''),
                vehicle_type=row.get('vehicle_type', 'car'),
                is_active=True
            )
            db.add(vehicle)
        
        db.commit()
        print("✅ Vehicles loaded successfully")
        
        print("🎉 Database seeding completed!")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
