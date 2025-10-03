"""
Dataset Management Utilities
Tools for managing student, vehicle, and access log datasets
"""

import pandas as pd
import os
from datetime import datetime

def add_student(moodle_id: str, name: str, email: str, department: str, phone: str = "", vehicle_number: str = ""):
    """Add new student to CSV"""
    csv_path = "data/students.csv"
    
    new_student = {
        "moodle_id": moodle_id,
        "name": name,
        "email": email,
        "department": department,
        "phone": phone,
        "vehicle_number": vehicle_number,
        "face_embedding_path": f"embeddings/{moodle_id}.npy"
    }
    
    df = pd.read_csv(csv_path)
    df = pd.concat([df, pd.DataFrame([new_student])], ignore_index=True)
    df.to_csv(csv_path, index=False)
    print(f"✅ Added student: {name} ({moodle_id})")

def add_vehicle(plate_number: str, owner_moodle_id: str, make: str = "", model: str = "", color: str = "", vehicle_type: str = "car"):
    """Add new vehicle to CSV"""
    csv_path = "data/vehicles.csv"
    
    new_vehicle = {
        "plate_number": plate_number,
        "owner_moodle_id": owner_moodle_id,
        "make": make,
        "model": model,
        "color": color,
        "vehicle_type": vehicle_type,
        "registration_date": datetime.now().strftime("%Y-%m-%d")
    }
    
    df = pd.read_csv(csv_path)
    df = pd.concat([df, pd.DataFrame([new_vehicle])], ignore_index=True)
    df.to_csv(csv_path, index=False)
    print(f"✅ Added vehicle: {plate_number} for {owner_moodle_id}")

def list_students():
    """List all students"""
    df = pd.read_csv("data/students.csv")
    print("\n📚 Students:")
    print(df.to_string(index=False))

def list_vehicles():
    """List all vehicles"""
    df = pd.read_csv("data/vehicles.csv")
    print("\n🚗 Vehicles:")
    print(df.to_string(index=False))

if __name__ == "__main__":
    print("📊 Dataset Management Utilities")
    print("=" * 50)
    
    # Example usage
    list_students()
    list_vehicles()
