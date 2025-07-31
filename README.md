# Field Insights Dashboard - Backend

A FastAPI-based backend for the Field Insights Dashboard with PostgreSQL database and Celery background processing.

## Features

- **RESTful API**: FastAPI with automatic OpenAPI documentation
- **Database Integration**: PostgreSQL with SQLAlchemy ORM
- **Background Processing**: Celery with Redis for async tasks
- **Real-time Analytics**: Comprehensive sensor data analytics
- **Health Monitoring**: System health checks and status monitoring
- **CORS Support**: Cross-origin resource sharing for frontend integration

## Tech Stack

- **Framework**: FastAPI (Python web framework)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Background Tasks**: Celery with Redis broker
- **Validation**: Pydantic schemas
- **Documentation**: Automatic OpenAPI/Swagger docs

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL
- Redis

### Installation

1. **Clone and navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   .\venv\Scripts\activate  # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp env.example .env
   # Edit .env with your database and Redis settings
   ```

5. **Set up PostgreSQL database:**
   ```sql
   CREATE DATABASE field_insights_db;
   ```

6. **Start Redis:**
   ```bash
   # Using Docker
   docker run -d -p 6379:6379 redis:alpine
   
   # Or install Redis locally
   ```

### Running the Application

1. **Start the FastAPI server:**
   ```bash
   python run.py
   # or
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start Celery worker (in new terminal):**
   ```bash
   celery -A app.celery_app worker --loglevel=info
   ```

3. **Access the API:**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## API Endpoints

### Sensor Data

- `POST /sensor-data` - Upload sensor readings
- `GET /readings` - Get sensor readings with filtering

### Analytics

- `GET /analytics` - Get comprehensive analytics
- `GET /analytics/field/{field_id}` - Get field-specific analytics
- `GET /analytics/sensor/{sensor_type}` - Get sensor-type analytics

### System

- `GET /health` - Health check
- `GET /task/{task_id}` - Check background task status

## Database Schema

### Sensor Readings Table
```sql
CREATE TABLE sensor_readings (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    field_id VARCHAR(50) NOT NULL,
    sensor_type VARCHAR(50) NOT NULL,
    reading_value FLOAT NOT NULL,
    unit VARCHAR(20) NOT NULL
);
```

### Daily Stats Table
```sql
CREATE TABLE daily_stats (
    id SERIAL PRIMARY KEY,
    date TIMESTAMP WITH TIME ZONE NOT NULL,
    field_id VARCHAR(50) NOT NULL,
    sensor_type VARCHAR(50) NOT NULL,
    avg_value FLOAT NOT NULL,
    min_value FLOAT NOT NULL,
    max_value FLOAT NOT NULL,
    count_readings INTEGER NOT NULL
);
```

## Background Tasks

### Celery Tasks

1. **process_sensor_data_batch**: Process large batches of sensor data
2. **calculate_daily_stats**: Calculate daily statistics
3. **cleanup_old_data**: Clean up old sensor data (90+ days)

### Task Monitoring

- Check task status: `GET /task/{task_id}`
- Monitor progress for large data uploads
- Automatic daily stats calculation

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:password@localhost:5432/field_insights_db` |
| `CELERY_BROKER_URL` | Redis broker URL | `redis://localhost:6379/0` |
| `CELERY_RESULT_BACKEND` | Redis result backend | `redis://localhost:6379/0` |
| `API_HOST` | API host address | `0.0.0.0` |
| `API_PORT` | API port | `8000` |
| `DEBUG` | Debug mode | `True` |
| `ALLOWED_ORIGINS` | CORS allowed origins | `http://localhost:3000` |

## Development

### Project Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database configuration
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── services.py          # Business logic
│   ├── tasks.py             # Celery tasks
│   └── celery_app.py        # Celery configuration
├── requirements.txt
├── run.py                   # Startup script
├── env.example              # Environment template
└── README.md
```

### Adding New Endpoints

1. **Create schema** in `schemas.py`
2. **Add service method** in `services.py`
3. **Create endpoint** in `main.py`
4. **Update documentation**

### Database Migrations

The application creates tables automatically on startup. For production, consider using Alembic for migrations.

## Production Deployment

### Docker Setup

1. **Create Dockerfile:**
   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["python", "run.py"]
   ```

2. **Create docker-compose.yml:**
   ```yaml
   version: '3.8'
   services:
     api:
       build: .
       ports:
         - "8000:8000"
       environment:
         - DATABASE_URL=postgresql://postgres:password@db:5432/field_insights_db
       depends_on:
         - db
         - redis
     
     db:
       image: postgres:13
       environment:
         POSTGRES_DB: field_insights_db
         POSTGRES_USER: postgres
         POSTGRES_PASSWORD: password
       volumes:
         - postgres_data:/var/lib/postgresql/data
     
     redis:
       image: redis:alpine
     
     celery:
       build: .
       command: celery -A app.celery_app worker --loglevel=info
       depends_on:
         - redis
         - db
   
   volumes:
     postgres_data:
   ```

### Environment Setup

1. **Set production environment variables**
2. **Configure database with proper credentials**
3. **Set up Redis for production**
4. **Configure CORS for your domain**

## Monitoring and Logging

### Health Checks

- Database connection status
- Redis connection status
- Overall system health

### Logging

- Application logs with structured format
- Celery task logs
- Database query logs (in debug mode)

## API Documentation

Visit http://localhost:8000/docs for interactive API documentation.

## Testing

### Manual Testing

1. **Health Check:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Upload Sensor Data:**
   ```bash
   curl -X POST "http://localhost:8000/sensor-data" \
        -H "Content-Type: application/json" \
        -d '[
          {
            "timestamp": "2024-01-01T10:00:00Z",
            "field_id": "field_001",
            "sensor_type": "soil_moisture",
            "reading_value": 45.2,
            "unit": "%"
          }
        ]'
   ```

3. **Get Analytics:**
   ```bash
   curl http://localhost:8000/analytics
   ```

## Troubleshooting

### Common Issues

1. **Database Connection Error:**
   - Check PostgreSQL is running
   - Verify DATABASE_URL in .env
   - Ensure database exists

2. **Redis Connection Error:**
   - Check Redis is running
   - Verify CELERY_BROKER_URL in .env

3. **CORS Issues:**
   - Update ALLOWED_ORIGINS in .env
   - Check frontend URL is included

4. **Celery Worker Not Starting:**
   - Ensure Redis is running
   - Check Celery configuration
   - Verify task imports

## License

MIT License - see LICENSE file for details 