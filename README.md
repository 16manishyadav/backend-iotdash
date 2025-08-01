# Field Insights Dashboard API

A FastAPI-based backend for IoT sensor data management and analytics, designed for agricultural field monitoring and insights.

## 🚀 Features

### **Core Functionalities**
- **📊 Real-time Analytics**: Comprehensive sensor data analytics with field and sensor-type specific insights
- **📡 Sensor Data Management**: Upload and manage IoT sensor readings with batch processing support
- **⚡ Background Processing**: Handle large data batches (>100 readings) asynchronously using Celery
- **🏥 Health Monitoring**: System health checks for database and Redis connections
- **🔍 Data Filtering**: Query sensor readings by field, sensor type, and time ranges
- **🗄️ Database Management**: Clear data functionality with safety warnings

### **Technical Features**
- **RESTful API**: Clean, documented API endpoints with automatic OpenAPI documentation
- **Data Validation**: Robust input validation using Pydantic schemas
- **Database Flexibility**: Support for both SQLite (local) and PostgreSQL (production)
- **Message Queue**: Redis-based Celery integration for background tasks
- **SSL Support**: Secure database connections for production deployments

## 🛠️ Tech Stack

- **FastAPI** - Modern, fast web framework with automatic API documentation
- **SQLAlchemy** - Database ORM with migration support
- **PostgreSQL** - Primary database for production (with SQLite fallback)
- **Redis** - Message broker for Celery background tasks
- **Celery** - Asynchronous task processing for large data batches
- **Pydantic** - Data validation and serialization
- **Alembic** - Database migration management
- **Render** - Cloud platform for PostgreSQL, Redis, and web service deployment

## 📋 Prerequisites

- Python 3.11+
- Git
- PostgreSQL (for production)
- Redis (for production)

## 🚀 Quick Start

### **1. Clone the Repository**
```bash
git clone <your-repository-url>
cd backend-iotdash
```

### **2. Set Up Virtual Environment**
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4. Configure Environment Variables**

Create a `.env` file in the root directory:

**For Local Development:**
```env
# Database (SQLite for local development)
DATABASE_URL=sqlite:///./field_insights.db

# App Configuration
DEBUG=true
API_HOST=0.0.0.0
API_PORT=8000
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# Optional: Redis for local development (if you have Redis installed)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

**For Production (Render):**
```env
# Database (Render PostgreSQL)
DATABASE_URL=postgres://username:password@host:port/database?sslmode=require

# Redis (Render Redis)
CELERY_BROKER_URL=redis://username:password@host:port
CELERY_RESULT_BACKEND=redis://username:password@host:port

# App Configuration
DEBUG=false
API_HOST=0.0.0.0
API_PORT=8000
ALLOWED_ORIGINS=*
```

### **5. Run the Application**
```bash
python run.py
```

The API will be available at `http://localhost:8000`

### **6. Test the API**
```bash
# Health check
curl http://localhost:8000/health

# Get analytics
curl http://localhost:8000/analytics

# Upload sample sensor data
curl -X POST http://localhost:8000/sensor-data \
  -H "Content-Type: application/json" \
  -d '[
    {
      "field_id": "field_001",
      "sensor_type": "temperature",
      "reading_value": 25.5,
      "timestamp": "2024-01-01T12:00:00Z",
      "unit": "celsius"
    }
  ]'
```

## 📚 API Documentation

Once the server is running, visit:
- **Interactive API Docs**: `http://localhost:8000/docs`
- **Alternative API Docs**: `http://localhost:8000/redoc`

### **Available Endpoints**

#### **Sensor Data Management**
- `POST /sensor-data` - Upload sensor readings (supports batch processing)
- `GET /readings` - Get sensor readings with optional filtering

#### **Analytics & Insights**
- `GET /analytics` - Get comprehensive analytics dashboard
- `GET /analytics/field/{field_id}` - Get field-specific analytics
- `GET /analytics/sensor/{sensor_type}` - Get sensor-type specific analytics

#### **System Monitoring**
- `GET /health` - System health check (database & Redis status)
- `GET /task/{task_id}` - Check background task status and progress

#### **Database Management**
- `DELETE /data/clear` - Clear all data (⚠️ Use with caution in production)

## 🌐 Production Deployment

This project is optimized for deployment on **Render** with managed services.

### **Render Services Used:**

1. **PostgreSQL Database** - Managed database service
   - Automatic backups
   - SSL connections
   - Scalable storage

2. **Redis Key-Value Store** - Message broker for Celery
   - High-performance caching
   - Reliable message queuing
   - Session storage

3. **Web Service** - Python runtime for FastAPI
   - Automatic deployments
   - SSL certificates
   - Custom domains

### **Deployment Steps:**

1. **Connect your GitHub repository to Render**
2. **Create a PostgreSQL database** on Render
3. **Create a Redis service** on Render
4. **Create a Web Service** pointing to your repository
5. **Set environment variables** in the Render dashboard
6. **Deploy!** Render will automatically build and deploy your application

### **Environment Variables for Render:**

```env
# Database (from Render PostgreSQL dashboard)
DATABASE_URL=postgres://username:password@host:port/database?sslmode=require

# Redis (from Render Redis dashboard)
CELERY_BROKER_URL=redis://username:password@host:port
CELERY_RESULT_BACKEND=redis://username:password@host:port

# App Configuration
DEBUG=false
API_HOST=0.0.0.0
API_PORT=8000
ALLOWED_ORIGINS=*

# Build Configuration (Required for Render)
PYTHON_VERSION=3.11.9
CARGO_HOME=/opt/render/project/.cargo
```

### **Render Build Command:**
```bash
pip install --upgrade pip && pip install -r requirements.txt
```

### **Why These Environment Variables Are Needed:**

- **`PYTHON_VERSION=3.11.9`**: Ensures Render uses the correct Python version that's compatible with our dependencies (especially Pydantic 1.10.13)
- **`CARGO_HOME=/opt/render/project/.cargo`**: Provides a writable directory for Rust compilation tools used by some Python packages (like `psycopg2-binary`)
- **Build Command**: Upgrades pip first to avoid compatibility issues, then installs all requirements

## 📁 Project Structure

```
backend-iotdash/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application & endpoints
│   ├── database.py          # Database configuration & connection
│   ├── models.py            # SQLAlchemy database models
│   ├── schemas.py           # Pydantic data validation schemas
│   ├── services.py          # Business logic & analytics
│   ├── tasks.py             # Celery background tasks
│   └── celery_app.py        # Celery configuration
├── alembic/                 # Database migration files
│   ├── env.py              # Migration environment
│   └── versions/           # Migration scripts
├── requirements.txt         # Python dependencies
├── runtime.txt             # Python version specification
├── render.yaml             # Render deployment configuration
├── run.py                  # Application entry point
└── README.md              # This documentation
```

## 🔧 Development

### **Database Migrations**
```bash
# Create a new migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Check migration status
alembic current
```

### **Local Development Tips**

1. **SQLite Database**: Used by default for local development
   - No setup required
   - File-based storage
   - Perfect for development and testing

2. **Redis (Optional)**: For local Celery functionality
   - Install Redis locally or use Docker
   - `docker run -d -p 6379:6379 redis:latest`

3. **Debug Mode**: Set `DEBUG=true` in `.env` for:
   - Detailed error messages
   - SQL query logging
   - Redis health check bypass

### **Testing the API**

```bash
# Health check
curl http://localhost:8000/health

# Get analytics
curl http://localhost:8000/analytics

# Upload sensor data
curl -X POST http://localhost:8000/sensor-data \
  -H "Content-Type: application/json" \
  -d '[
    {
      "field_id": "field_001",
      "sensor_type": "temperature",
      "reading_value": 25.5,
      "timestamp": "2024-01-01T12:00:00Z",
      "unit": "celsius"
    },
    {
      "field_id": "field_001",
      "sensor_type": "humidity",
      "reading_value": 60.2,
      "timestamp": "2024-01-01T12:00:00Z",
      "unit": "percent"
    }
  ]'

# Get filtered readings
curl "http://localhost:8000/readings?field_id=field_001&limit=10"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues:

1. Check the health endpoint: `GET /health`
2. Review the application logs
3. Ensure all environment variables are set correctly
4. Verify database and Redis connections

For deployment issues on Render, check the build logs in your Render dashboard. 