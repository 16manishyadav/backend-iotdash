from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict

class SensorReadingBase(BaseModel):
    """Base schema for sensor reading"""
    timestamp: datetime
    field_id: str = Field(..., min_length=1, max_length=50)
    sensor_type: str = Field(..., min_length=1, max_length=50)
    reading_value: float
    unit: str = Field(..., min_length=1, max_length=20)

class SensorReadingCreate(SensorReadingBase):
    """Schema for creating sensor readings"""
    pass

class SensorReading(SensorReadingBase):
    """Schema for sensor reading response"""
    id: int
    
    class Config:
        orm_mode = True

class SensorReadingBatch(BaseModel):
    """Schema for batch sensor readings"""
    readings: List[SensorReadingCreate]

class AnalyticsResponse(BaseModel):
    """Schema for analytics response"""
    total_readings: int
    fields: List[str]
    sensor_types: List[str]
    average_by_field: Dict[str, float]
    average_by_sensor_type: Dict[str, float]
    recent_readings: Optional[List[SensorReading]] = None

class HealthResponse(BaseModel):
    """Schema for health check response"""
    status: str
    timestamp: datetime
    database_connected: bool
    redis_connected: bool

class TaskResponse(BaseModel):
    """Schema for task response"""
    task_id: str
    status: str
    message: str 