"""
Students Router
Handles CRUD operations for student records
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.student import Student

router = APIRouter()

@router.get("/")
async def get_students(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all students with pagination
    """
    students = db.query(Student).offset(skip).limit(limit).all()
    return students

@router.get("/{moodle_id}")
async def get_student(
    moodle_id: str,
    db: Session = Depends(get_db)
):
    """
    Get student by Moodle ID
    """
    student = db.query(Student).filter(Student.moodle_id == moodle_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@router.post("/")
async def create_student(
    moodle_id: str,
    name: str,
    email: str,
    department: str,
    db: Session = Depends(get_db)
):
    """
    Create new student record
    """
    # Check if student exists
    existing = db.query(Student).filter(Student.moodle_id == moodle_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Student already exists")
    
    new_student = Student(
        moodle_id=moodle_id,
        name=name,
        email=email,
        department=department
    )
    
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    
    return new_student

@router.put("/{moodle_id}")
async def update_student(
    moodle_id: str,
    name: str = None,
    department: str = None,
    phone: str = None,
    db: Session = Depends(get_db)
):
    """
    Update student information
    """
    student = db.query(Student).filter(Student.moodle_id == moodle_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    if name:
        student.name = name
    if department:
        student.department = department
    if phone:
        student.phone = phone
    
    db.commit()
    db.refresh(student)
    
    return student

@router.delete("/{moodle_id}")
async def delete_student(
    moodle_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete student record
    """
    student = db.query(Student).filter(Student.moodle_id == moodle_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    db.delete(student)
    db.commit()
    
    return {"message": "Student deleted successfully"}
