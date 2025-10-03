"""
Smart Campus Access Control System - FastAPI Backend
Main application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import auth, students, vehicles, access_logs, alerts

app = FastAPI(
    title="Smart Campus Access Control API",
    description="Backend API for campus access control with ANPR, OCR, and face recognition",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(students.router, prefix="/api/students", tags=["Students"])
app.include_router(vehicles.router, prefix="/api/vehicles", tags=["Vehicles"])
app.include_router(access_logs.router, prefix="/api/access-logs", tags=["Access Logs"])
app.include_router(alerts.router, prefix="/api/alerts", tags=["Alerts"])

@app.get("/")
async def root():
    return {
        "message": "Smart Campus Access Control System API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
