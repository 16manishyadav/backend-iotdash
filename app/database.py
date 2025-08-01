from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import urllib.parse

load_dotenv()

def get_database_url():
    """Get database URL with proper handling for Render PostgreSQL"""
    database_url = os.getenv("DATABASE_URL")
    
    if database_url:
        # Handle Render's PostgreSQL URL format
        if database_url.startswith("postgres://"):
            # Convert postgres:// to postgresql+pg8000:// for pg8000
            database_url = database_url.replace("postgres://", "postgresql+pg8000://", 1)
        elif database_url.startswith("postgresql://") and "+" not in database_url:
            # If it's already postgresql:// but no driver specified, add pg8000
            database_url = database_url.replace("postgresql://", "postgresql+pg8000://", 1)
        
        return database_url
    
    # Fallback to SQLite for local development
    return "sqlite:///./field_insights.db"

# Database URL from environment variable
DATABASE_URL = get_database_url()

# Create SQLAlchemy engine with appropriate configuration
if DATABASE_URL.startswith("postgresql"):
    # PostgreSQL configuration with SSL for Render
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=os.getenv("DEBUG", "False").lower() == "true",
        connect_args={
            "sslmode": "require"  # Force SSL for Render PostgreSQL
        }
    )
else:
    # SQLite configuration
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
    )

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine) 