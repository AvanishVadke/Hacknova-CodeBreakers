"""
Vehicles Router
Handles CRUD operations for vehicle records
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.vehicle import Vehicle

router = APIRouter()

@router.get("/")
async def get_vehicles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all vehicles with pagination"""
    vehicles = db.query(Vehicle).offset(skip).limit(limit).all()
    return vehicles

@router.get("/{plate_number}")
async def get_vehicle(
    plate_number: str,
    db: Session = Depends(get_db)
):
    """Get vehicle by plate number"""
    vehicle = db.query(Vehicle).filter(Vehicle.plate_number == plate_number).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle

@router.post("/")
async def create_vehicle(
    plate_number: str,
    owner_moodle_id: str,
    make: str = None,
    model: str = None,
    color: str = None,
    vehicle_type: str = "car",
    db: Session = Depends(get_db)
):
    """Register new vehicle"""
    # Check if vehicle exists
    existing = db.query(Vehicle).filter(Vehicle.plate_number == plate_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Vehicle already registered")
    
    new_vehicle = Vehicle(
        plate_number=plate_number,
        owner_moodle_id=owner_moodle_id,
        make=make,
        model=model,
        color=color,
        vehicle_type=vehicle_type
    )
    
    db.add(new_vehicle)
    db.commit()
    db.refresh(new_vehicle)
    
    return new_vehicle

@router.delete("/{plate_number}")
async def delete_vehicle(
    plate_number: str,
    db: Session = Depends(get_db)
):
    """Delete vehicle record"""
    vehicle = db.query(Vehicle).filter(Vehicle.plate_number == plate_number).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    
    db.delete(vehicle)
    db.commit()
    
    return {"message": "Vehicle deleted successfully"}
