from celery import current_task
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import logging
from typing import List, Dict

from .celery_app import celery_app
from .database import SessionLocal
from .models import SensorReading, DailyStats
from .schemas import SensorReadingCreate

logger = logging.getLogger(__name__)

@celery_app.task(bind=True)
def process_sensor_data_batch(self, readings_data: List[Dict]):
    """
    Background task to process a batch of sensor readings
    """
    try:
        self.update_state(state='PROGRESS', meta={'current': 0, 'total': len(readings_data)})
        
        db = SessionLocal()
        processed_count = 0
        
        try:
            for i, reading_data in enumerate(readings_data):
                # Create sensor reading
                reading = SensorReading(
                    timestamp=reading_data['timestamp'],
                    field_id=reading_data['field_id'],
                    sensor_type=reading_data['sensor_type'],
                    reading_value=reading_data['reading_value'],
                    unit=reading_data['unit']
                )
                
                db.add(reading)
                processed_count += 1
                
                # Update progress every 10 items
                if i % 10 == 0:
                    self.update_state(
                        state='PROGRESS',
                        meta={'current': i, 'total': len(readings_data)}
                    )
            
            db.commit()
            
            # Trigger analytics calculation
            calculate_daily_stats.delay()
            
            return {
                'status': 'SUCCESS',
                'processed_count': processed_count,
                'message': f'Successfully processed {processed_count} sensor readings'
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error processing sensor data batch: {str(e)}")
        return {
            'status': 'FAILURE',
            'error': str(e)
        }

@celery_app.task
def calculate_daily_stats():
    """
    Background task to calculate daily statistics
    """
    try:
        db = SessionLocal()
        
        try:
            # Get yesterday's date
            yesterday = datetime.now().date() - timedelta(days=1)
            
            # Calculate daily stats for each field and sensor type
            stats_query = db.query(
                SensorReading.field_id,
                SensorReading.sensor_type,
                func.avg(SensorReading.reading_value).label('avg_value'),
                func.min(SensorReading.reading_value).label('min_value'),
                func.max(SensorReading.reading_value).label('max_value'),
                func.count(SensorReading.id).label('count_readings')
            ).filter(
                func.date(SensorReading.timestamp) == yesterday
            ).group_by(
                SensorReading.field_id,
                SensorReading.sensor_type
            )
            
            # Delete existing stats for yesterday
            db.query(DailyStats).filter(
                func.date(DailyStats.date) == yesterday
            ).delete()
            
            # Insert new stats
            for stat in stats_query.all():
                daily_stat = DailyStats(
                    date=yesterday,
                    field_id=stat.field_id,
                    sensor_type=stat.sensor_type,
                    avg_value=float(stat.avg_value),
                    min_value=float(stat.min_value),
                    max_value=float(stat.max_value),
                    count_readings=int(stat.count_readings)
                )
                db.add(daily_stat)
            
            db.commit()
            
            return {
                'status': 'SUCCESS',
                'message': f'Daily stats calculated for {yesterday}'
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error calculating daily stats: {str(e)}")
        return {
            'status': 'FAILURE',
            'error': str(e)
        }

@celery_app.task
def cleanup_old_data():
    """
    Background task to cleanup old sensor data (keep last 90 days)
    """
    try:
        db = SessionLocal()
        
        try:
            # Calculate cutoff date (90 days ago)
            cutoff_date = datetime.now() - timedelta(days=90)
            
            # Delete old sensor readings
            deleted_count = db.query(SensorReading).filter(
                SensorReading.timestamp < cutoff_date
            ).delete()
            
            db.commit()
            
            return {
                'status': 'SUCCESS',
                'deleted_count': deleted_count,
                'message': f'Cleaned up {deleted_count} old sensor readings'
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error cleaning up old data: {str(e)}")
        return {
            'status': 'FAILURE',
            'error': str(e)
        } 