"""
Alerts Router
Handles security alerts and notifications
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.access_log import AccessLog

router = APIRouter()

@router.get("/")
async def get_alerts(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Get all security alerts
    """
    alerts = db.query(AccessLog).filter(
        AccessLog.is_alert == True
    ).order_by(AccessLog.timestamp.desc()).offset(skip).limit(limit).all()
    
    return alerts

@router.get("/unresolved")
async def get_unresolved_alerts(
    db: Session = Depends(get_db)
):
    """
    Get unresolved alerts requiring attention
    """
    # TODO: Add resolution status tracking
    alerts = db.query(AccessLog).filter(
        AccessLog.is_alert == True,
        AccessLog.access_granted == False
    ).order_by(AccessLog.timestamp.desc()).limit(50).all()
    
    return alerts

@router.get("/count")
async def get_alert_count(
    db: Session = Depends(get_db)
):
    """
    Get total count of active alerts
    """
    count = db.query(AccessLog).filter(
        AccessLog.is_alert == True,
        AccessLog.access_granted == False
    ).count()
    
    return {"alert_count": count}
