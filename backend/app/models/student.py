"""
Student Model
Represents student information with face embeddings
"""

from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    moodle_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    department = Column(String)
    phone = Column(String)
    
    # Face recognition data (stored as JSON array of embeddings)
    face_embedding = Column(JSON)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    vehicles = relationship("Vehicle", back_populates="owner")
    access_logs = relationship("AccessLog", back_populates="student")
