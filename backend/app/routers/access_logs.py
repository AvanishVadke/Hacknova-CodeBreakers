"""
Access Logs Router
Handles access log retrieval and analytics
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models.access_log import AccessLog

router = APIRouter()

@router.get("/")
async def get_access_logs(
    skip: int = 0,
    limit: int = 100,
    start_date: datetime = None,
    end_date: datetime = None,
    db: Session = Depends(get_db)
):
    """
    Get access logs with filtering and pagination
    """
    query = db.query(AccessLog)
    
    if start_date:
        query = query.filter(AccessLog.timestamp >= start_date)
    if end_date:
        query = query.filter(AccessLog.timestamp <= end_date)
    
    logs = query.order_by(AccessLog.timestamp.desc()).offset(skip).limit(limit).all()
    return logs

@router.get("/recent")
async def get_recent_logs(
    hours: int = Query(default=24, ge=1, le=168),
    db: Session = Depends(get_db)
):
    """
    Get recent access logs (last N hours)
    """
    since = datetime.utcnow() - timedelta(hours=hours)
    logs = db.query(AccessLog).filter(
        AccessLog.timestamp >= since
    ).order_by(AccessLog.timestamp.desc()).limit(100).all()
    
    return logs

@router.get("/student/{moodle_id}")
async def get_student_logs(
    moodle_id: str,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get access logs for a specific student
    """
    logs = db.query(AccessLog).filter(
        AccessLog.student_moodle_id == moodle_id
    ).order_by(AccessLog.timestamp.desc()).offset(skip).limit(limit).all()
    
    return logs

@router.get("/stats")
async def get_access_stats(
    days: int = Query(default=7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """
    Get access statistics for dashboard
    """
    since = datetime.utcnow() - timedelta(days=days)
    
    total_entries = db.query(AccessLog).filter(AccessLog.timestamp >= since).count()
    granted_entries = db.query(AccessLog).filter(
        AccessLog.timestamp >= since,
        AccessLog.access_granted == True
    ).count()
    alerts = db.query(AccessLog).filter(
        AccessLog.timestamp >= since,
        AccessLog.is_alert == True
    ).count()
    
    return {
        "period_days": days,
        "total_entries": total_entries,
        "granted_entries": granted_entries,
        "denied_entries": total_entries - granted_entries,
        "alerts": alerts
    }
