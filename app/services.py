from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Optional
from datetime import datetime, timedelta

from .models import SensorReading, DailyStats
from .schemas import SensorReadingCreate, AnalyticsResponse
from .tasks import process_sensor_data_batch

class SensorService:
    """Service class for sensor data operations"""
    
    @staticmethod
    def create_sensor_reading(db: Session, reading: SensorReadingCreate) -> SensorReading:
        """Create a single sensor reading"""
        db_reading = SensorReading(**reading.dict())
        db.add(db_reading)
        db.commit()
        db.refresh(db_reading)
        return db_reading
    
    @staticmethod
    def create_sensor_readings_batch(db: Session, readings: List[SensorReadingCreate]) -> List[SensorReading]:
        """Create multiple sensor readings in a batch"""
        db_readings = []
        for reading in readings:
            db_reading = SensorReading(**reading.dict())
            db.add(db_reading)
            db_readings.append(db_reading)
        
        db.commit()
        for reading in db_readings:
            db.refresh(reading)
        
        return db_readings
    
    @staticmethod
    def process_large_batch(readings: List[SensorReadingCreate]) -> str:
        """Process large batch of readings using Celery background task"""
        # Convert to dict for Celery serialization
        readings_data = [reading.dict() for reading in readings]
        
        # Start background task
        task = process_sensor_data_batch.delay(readings_data)
        
        return task.id
    
    @staticmethod
    def get_recent_readings(db: Session, limit: int = 10) -> List[SensorReading]:
        """Get recent sensor readings"""
        return db.query(SensorReading).order_by(
            SensorReading.timestamp.desc()
        ).limit(limit).all()

class AnalyticsService:
    """Service class for analytics operations"""
    
    @staticmethod
    def get_analytics(db: Session) -> AnalyticsResponse:
        """Get comprehensive analytics data"""
        
        # Get total readings count
        total_readings = db.query(SensorReading).count()
        
        # Get unique fields and sensor types
        fields = [r[0] for r in db.query(SensorReading.field_id).distinct()]
        sensor_types = [r[0] for r in db.query(SensorReading.sensor_type).distinct()]
        
        # Calculate averages by field
        avg_by_field = {}
        for field in fields:
            result = db.query(func.avg(SensorReading.reading_value)).filter(
                SensorReading.field_id == field
            ).scalar()
            avg_by_field[field] = float(result) if result else 0.0
        
        # Calculate averages by sensor type
        avg_by_sensor_type = {}
        for sensor_type in sensor_types:
            result = db.query(func.avg(SensorReading.reading_value)).filter(
                SensorReading.sensor_type == sensor_type
            ).scalar()
            avg_by_sensor_type[sensor_type] = float(result) if result else 0.0
        
        # Get recent readings
        recent_readings = SensorService.get_recent_readings(db, 5)
        
        return AnalyticsResponse(
            total_readings=total_readings,
            fields=fields,
            sensor_types=sensor_types,
            average_by_field=avg_by_field,
            average_by_sensor_type=avg_by_sensor_type,
            recent_readings=recent_readings
        )
    
    @staticmethod
    def get_field_analytics(db: Session, field_id: str) -> Dict:
        """Get analytics for a specific field"""
        readings = db.query(SensorReading).filter(
            SensorReading.field_id == field_id
        ).all()
        
        if not readings:
            return {}
        
        values = [r.reading_value for r in readings]
        
        return {
            'field_id': field_id,
            'total_readings': len(readings),
            'avg_value': sum(values) / len(values),
            'min_value': min(values),
            'max_value': max(values),
            'sensor_types': list(set(r.sensor_type for r in readings))
        }
    
    @staticmethod
    def get_sensor_type_analytics(db: Session, sensor_type: str) -> Dict:
        """Get analytics for a specific sensor type"""
        readings = db.query(SensorReading).filter(
            SensorReading.sensor_type == sensor_type
        ).all()
        
        if not readings:
            return {}
        
        values = [r.reading_value for r in readings]
        
        return {
            'sensor_type': sensor_type,
            'total_readings': len(readings),
            'avg_value': sum(values) / len(values),
            'min_value': min(values),
            'max_value': max(values),
            'fields': list(set(r.field_id for r in readings))
        }

class HealthService:
    """Service class for health checks"""
    
    @staticmethod
    def check_database_connection(db: Session) -> bool:
        """Check if database connection is working"""
        try:
            from sqlalchemy import text
            db.execute(text("SELECT 1"))
            return True
        except Exception:
            return False
    
    @staticmethod
    def check_redis_connection() -> bool:
        """Check if Redis connection is working"""
        try:
            import redis
            from .celery_app import celery_app
            
            # Get Redis URL from Celery config
            redis_url = celery_app.conf.broker_url
            if redis_url.startswith('redis://'):
                # Parse Redis URL
                redis_url = redis_url.replace('redis://', '')
                if '@' in redis_url:
                    # Handle password
                    auth, rest = redis_url.split('@', 1)
                    password = auth.split(':', 1)[1] if ':' in auth else None
                    host_port = rest.split('/', 1)[0]
                    host, port = host_port.split(':')
                    port = int(port)
                else:
                    # No password
                    host_port = redis_url.split('/', 1)[0]
                    host, port = host_port.split(':')
                    port = int(port)
                    password = None
                
                # Test connection
                r = redis.Redis(host=host, port=port, password=password, socket_connect_timeout=5)
                r.ping()
                return True
            else:
                # Fallback to Celery inspect
                celery_app.control.inspect().active()
                return True
        except Exception:
            return False 