from sqlalchemy import Column, Integer, String, Float, DateTime, func, Index
from sqlalchemy.sql import func
from .database import Base

class SensorReading(Base):
    """Model for sensor readings"""
    __tablename__ = "sensor_readings"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=func.now())
    field_id = Column(String(50), nullable=False)
    sensor_type = Column(String(50), nullable=False)
    reading_value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)
    
    # Create indexes for better query performance
    __table_args__ = (
        Index('idx_timestamp', 'timestamp'),
        Index('idx_field_id', 'field_id'),
        Index('idx_sensor_type', 'sensor_type'),
        Index('idx_field_sensor', 'field_id', 'sensor_type'),
    )

class DailyStats(Base):
    """Model for daily aggregated statistics"""
    __tablename__ = "daily_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=True), nullable=False)
    field_id = Column(String(50), nullable=False)
    sensor_type = Column(String(50), nullable=False)
    avg_value = Column(Float, nullable=False)
    min_value = Column(Float, nullable=False)
    max_value = Column(Float, nullable=False)
    count_readings = Column(Integer, nullable=False)
    
    __table_args__ = (
        Index('idx_daily_stats_date', 'date'),
        Index('idx_daily_stats_field', 'field_id'),
        Index('idx_daily_stats_sensor', 'sensor_type'),
    ) 