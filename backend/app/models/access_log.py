"""
Access Log Model
Records all access attempts with recognition results
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class AccessLog(Base):
    __tablename__ = "access_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    student_moodle_id = Column(String, ForeignKey("students.moodle_id"))
    vehicle_plate = Column(String, ForeignKey("vehicles.plate_number"))
    
    # Recognition results
    entry_type = Column(String)  # "vehicle", "face", "id_card"
    recognition_confidence = Column(Float)
    
    # Status
    access_granted = Column(Boolean, default=False)
    is_alert = Column(Boolean, default=False)
    alert_reason = Column(String)
    
    # Metadata
    location = Column(String)  # gate/entry point
    image_path = Column(String)  # path to captured image
    additional_data = Column(JSON)  # any extra data
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    student = relationship("Student", back_populates="access_logs")
    vehicle = relationship("Vehicle", back_populates="access_logs")
