"""
Vehicle Model
Represents registered vehicles with license plate information
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Vehicle(Base):
    __tablename__ = "vehicles"
    
    id = Column(Integer, primary_key=True, index=True)
    plate_number = Column(String, unique=True, index=True, nullable=False)
    owner_moodle_id = Column(String, ForeignKey("students.moodle_id"), nullable=False)
    
    # Vehicle details
    make = Column(String)
    model = Column(String)
    color = Column(String)
    vehicle_type = Column(String)  # car, bike, etc.
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("Student", back_populates="vehicles")
    access_logs = relationship("AccessLog", back_populates="vehicle")
