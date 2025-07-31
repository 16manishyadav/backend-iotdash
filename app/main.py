from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import os
from dotenv import load_dotenv
from datetime import datetime

from .database import get_db, create_tables
from .models import SensorReading, DailyStats
from .schemas import (
    SensorReadingCreate, 
    SensorReading as SensorReadingSchema,
    AnalyticsResponse,
    HealthResponse,
    TaskResponse
)
from .services import SensorService, AnalyticsService, HealthService
from .celery_app import celery_app

load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Field Insights Dashboard API",
    description="API for IoT sensor data management and analytics",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Field Insights Dashboard API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.post("/sensor-data", response_model=List[SensorReadingSchema], tags=["Sensor Data"])
async def create_sensor_data(
    readings: List[SensorReadingCreate],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Upload sensor readings to the database.
    
    - For small batches (< 100 readings): Process immediately
    - For large batches (≥ 100 readings): Process in background using Celery
    """
    try:
        if len(readings) > 100:
            # Use background processing for large batches
            task_id = SensorService.process_large_batch(readings)
            return {
                "message": f"Processing {len(readings)} readings in background",
                "task_id": task_id,
                "status": "processing"
            }
        else:
            # Process immediately for small batches
            db_readings = SensorService.create_sensor_readings_batch(db, readings)
            return db_readings
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing sensor data: {str(e)}")

@app.get("/analytics", response_model=AnalyticsResponse, tags=["Analytics"])
async def get_analytics(db: Session = Depends(get_db)):
    """
    Get comprehensive analytics and statistics for sensor data.
    
    Returns:
    - Total number of readings
    - List of fields and sensor types
    - Average readings by field and sensor type
    - Recent readings
    """
    try:
        analytics = AnalyticsService.get_analytics(db)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching analytics: {str(e)}")

@app.get("/analytics/field/{field_id}", tags=["Analytics"])
async def get_field_analytics(field_id: str, db: Session = Depends(get_db)):
    """Get analytics for a specific field"""
    try:
        analytics = AnalyticsService.get_field_analytics(db, field_id)
        if not analytics:
            raise HTTPException(status_code=404, detail=f"Field {field_id} not found")
        return analytics
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching field analytics: {str(e)}")

@app.get("/analytics/sensor/{sensor_type}", tags=["Analytics"])
async def get_sensor_type_analytics(sensor_type: str, db: Session = Depends(get_db)):
    """Get analytics for a specific sensor type"""
    try:
        analytics = AnalyticsService.get_sensor_type_analytics(db, sensor_type)
        if not analytics:
            raise HTTPException(status_code=404, detail=f"Sensor type {sensor_type} not found")
        return analytics
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sensor analytics: {str(e)}")

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint to verify system status.
    
    Checks:
    - Database connection
    - Redis connection (for Celery)
    - Overall system status
    """
    try:
        db_connected = HealthService.check_database_connection(db)
        redis_connected = HealthService.check_redis_connection()
        
        status = "healthy" if db_connected and redis_connected else "unhealthy"
        
        return HealthResponse(
            status=status,
            timestamp=datetime.now(),
            database_connected=db_connected,
            redis_connected=redis_connected
        )
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.now(),
            database_connected=False,
            redis_connected=False
        )

@app.get("/task/{task_id}", response_model=TaskResponse, tags=["Tasks"])
async def get_task_status(task_id: str):
    """
    Get the status of a background task.
    
    Returns task status, progress, and result if completed.
    """
    try:
        task = celery_app.AsyncResult(task_id)
        
        if task.state == 'PENDING':
            response = {
                'task_id': task_id,
                'status': 'PENDING',
                'message': 'Task is pending'
            }
        elif task.state == 'PROGRESS':
            response = {
                'task_id': task_id,
                'status': 'PROGRESS',
                'message': f'Task is in progress: {task.info.get("current", 0)}/{task.info.get("total", 0)}'
            }
        elif task.state == 'SUCCESS':
            response = {
                'task_id': task_id,
                'status': 'SUCCESS',
                'message': task.info.get('message', 'Task completed successfully')
            }
        else:
            response = {
                'task_id': task_id,
                'status': 'FAILURE',
                'message': str(task.info)
            }
        
        return TaskResponse(**response)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking task status: {str(e)}")

@app.get("/readings", response_model=List[SensorReadingSchema], tags=["Sensor Data"])
async def get_readings(
    limit: int = 100,
    offset: int = 0,
    field_id: str = None,
    sensor_type: str = None,
    db: Session = Depends(get_db)
):
    """
    Get sensor readings with optional filtering.
    
    Parameters:
    - limit: Maximum number of readings to return (default: 100)
    - offset: Number of readings to skip (default: 0)
    - field_id: Filter by field ID
    - sensor_type: Filter by sensor type
    """
    try:
        query = db.query(SensorReading)
        
        if field_id:
            query = query.filter(SensorReading.field_id == field_id)
        
        if sensor_type:
            query = query.filter(SensorReading.sensor_type == sensor_type)
        
        readings = query.order_by(SensorReading.timestamp.desc()).offset(offset).limit(limit).all()
        return readings
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching readings: {str(e)}")

@app.delete("/data/clear", tags=["Database Management"])
async def clear_all_data(db: Session = Depends(get_db)):
    """
    Delete all data from the database.
    
    ⚠️ WARNING: This will permanently delete ALL sensor readings and daily stats.
    Use with caution, especially in production environments.
    
    Returns:
    - Number of sensor readings deleted
    - Number of daily stats deleted
    """
    try:
        # Delete all sensor readings
        sensor_readings_deleted = db.query(SensorReading).delete()
        
        # Delete all daily stats
        daily_stats_deleted = db.query(DailyStats).delete()
        
        # Commit the changes
        db.commit()
        
        return {
            "message": "All data cleared successfully",
            "sensor_readings_deleted": sensor_readings_deleted,
            "daily_stats_deleted": daily_stats_deleted,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error clearing data: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=os.getenv("DEBUG", "True").lower() == "true"
    ) 