# Field Insights Dashboard - Complete Setup Guide

## Current State Summary

**✅ Completed:**
- Project structure created (backend, frontend directories)
- Backend Python virtual environment created and activated
- All Python dependencies installed successfully
- Backend code implemented (FastAPI, SQLAlchemy, Celery, Redis)
- Frontend Next.js app created with Tailwind CSS
- Frontend components implemented (Dashboard, SensorDataForm, Header)
- API service and data generator implemented

**⏳ Pending:**
- PostgreSQL installation and database setup
- Redis installation and setup
- Environment variables configuration
- Backend server startup and testing
- Frontend-backend integration testing

## Backend Setup Instructions

### Prerequisites Installation

#### 1. Install PostgreSQL

**Download and Install:**
1. Go to: https://www.postgresql.org/download/windows/
2. Download PostgreSQL 15 or 16
3. Run installer with these settings:
   - **Password for postgres user:** `password` (or remember what you set)
   - **Port:** `5432` (default)
   - **Install all components**

**After Installation:**
1. Open Command Prompt as Administrator
2. Navigate to PostgreSQL bin directory (usually `C:\Program Files\PostgreSQL\15\bin`)
3. Create database:
   ```bash
   psql -U postgres
   # Enter password when prompted
   CREATE DATABASE field_insights_db;
   \q
   ```

#### 2. Install Redis

**Option A: Docker (Recommended)**
1. Download Docker Desktop: https://www.docker.com/products/docker-desktop/
2. Install and restart computer
3. Open Docker Desktop
4. Run Redis:
   ```bash
   docker run -d -p 6379:6379 redis:alpine
   ```

**Option B: Redis for Windows**
1. Download: https://github.com/microsoftarchive/redis/releases
2. Extract and run `redis-server.exe`

**Option C: Redis Cloud (Free)**
1. Go to: https://redis.com/try-free/
2. Create account and get connection string
3. Update `.env` file with cloud Redis URL

### Environment Configuration

#### 3. Create .env File

Create `.env` file in `backend` directory with this content:

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/field_insights_db

# Redis Configuration (for Celery)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# CORS Settings
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

**Important:** Replace `password` with your actual PostgreSQL password.

### Backend Startup

#### 4. Activate Virtual Environment

```bash
cd backend
.\venv\Scripts\activate
```

#### 5. Test Connections

```bash
# Test database connection
python -c "from app.database import engine; engine.connect(); print('Database OK!')"

# Test Redis connection
python -c "import redis; r = redis.Redis(); r.ping(); print('Redis OK!')"
```

#### 6. Start Backend Services

**Terminal 1: Start FastAPI server**
```bash
python run.py
```

**Terminal 2: Start Celery worker**
```bash
celery -A app.celery_app worker --loglevel=info
```

#### 7. Test Backend

1. **Health Check:** http://localhost:8000/health
2. **API Docs:** http://localhost:8000/docs
3. **Test API endpoints using the documentation**

## Frontend Setup Instructions

### Prerequisites

- Node.js 18+ installed
- npm or yarn package manager

### Frontend Startup

#### 1. Navigate to Frontend Directory

```bash
cd frontend/my-app
```

#### 2. Install Dependencies

```bash
npm install
```

#### 3. Start Development Server

```bash
npm run dev
```

#### 4. Access Frontend

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## Project Structure

```
project/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── database.py          # Database configuration
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── services.py          # Business logic
│   │   ├── tasks.py             # Celery tasks
│   │   └── celery_app.py        # Celery configuration
│   ├── venv/                    # Python virtual environment
│   ├── requirements.txt
│   ├── run.py                   # Startup script
│   ├── .env                     # Environment variables
│   └── README.md
├── frontend/
│   └── my-app/
│       ├── src/
│       │   ├── app/
│       │   │   └── page.tsx     # Main page
│       │   ├── components/
│       │   │   ├── Header.tsx
│       │   │   ├── Dashboard.tsx
│       │   │   ├── SensorDataForm.tsx
│       │   │   └── DataGeneratorConfig.tsx
│       │   └── lib/
│       │       ├── api.ts        # API service
│       │       └── dataGenerator.ts
│       ├── package.json
│       └── tailwind.config.js
└── setup.md                     # This file
```

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

## Troubleshooting

### Common Issues

1. **PostgreSQL Connection Error:**
   - Check if PostgreSQL service is running
   - Verify password in `.env` file
   - Ensure database `field_insights_db` exists

2. **Redis Connection Error:**
   - Check if Redis is running on port 6379
   - If using Docker, ensure container is running
   - Verify Redis URL in `.env` file

3. **CORS Issues:**
   - Check `ALLOWED_ORIGINS` in `.env` file
   - Ensure frontend URL is included

4. **Celery Worker Issues:**
   - Ensure Redis is running
   - Check Celery configuration
   - Verify task imports

### Testing Commands

```bash
# Test database
python -c "from app.database import engine; engine.connect(); print('Database OK!')"

# Test Redis
python -c "import redis; r = redis.Redis(); r.ping(); print('Redis OK!')"

# Test FastAPI app
python -c "from app.main import app; print('FastAPI OK!')"

# Test Celery
python -c "from app.celery_app import celery_app; print('Celery OK!')"
```

## Development Workflow

1. **Start Backend:**
   ```bash
   cd backend
   .\venv\Scripts\activate
   python run.py
   ```

2. **Start Celery Worker (new terminal):**
   ```bash
   cd backend
   .\venv\Scripts\activate
   celery -A app.celery_app worker --loglevel=info
   ```

3. **Start Frontend (new terminal):**
   ```bash
   cd frontend/my-app
   npm run dev
   ```

4. **Access Applications:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:password@localhost:5432/field_insights_db` |
| `CELERY_BROKER_URL` | Redis broker URL | `redis://localhost:6379/0` |
| `CELERY_RESULT_BACKEND` | Redis result backend | `redis://localhost:6379/0` |
| `API_HOST` | API host address | `0.0.0.0` |
| `API_PORT` | API port | `8000` |
| `DEBUG` | Debug mode | `True` |
| `ALLOWED_ORIGINS` | CORS allowed origins | `http://localhost:3000` |

## Next Steps

1. **Complete PostgreSQL installation**
2. **Complete Redis installation**
3. **Create and configure `.env` file**
4. **Test all connections**
5. **Start backend services**
6. **Test API endpoints**
7. **Start frontend and test integration**
8. **Generate and upload test data**
9. **Verify dashboard functionality**

## Current Status

- ✅ Backend code implemented
- ✅ Frontend code implemented
- ✅ Dependencies installed
- ⏳ PostgreSQL installation pending
- ⏳ Redis installation pending
- ⏳ Environment configuration pending
- ⏳ Service startup and testing pending

## Notes

- Virtual environment is already created and activated
- All Python dependencies are installed
- Backend code is ready to run
- Frontend code is ready to run
- Need to install PostgreSQL and Redis to complete setup 