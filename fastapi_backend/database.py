import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi_backend.models import Base  # Import Base from models.py

# Read DATABASE_URL from Railway Environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL is not set. Make sure to set it in Railway.")

# Create SQLAlchemy Engine with Connection Pooling
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Session Configuration
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize the Database (Create Tables)
def init_db():
    """Initializes the database tables."""
    Base.metadata.create_all(bind=engine)

# Dependency to Get DB Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
