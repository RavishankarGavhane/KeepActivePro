import os
from urllib.parse import quote
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi_backend.models import Base  # Import Base from models.py

# Get DATABASE_URL from environment, with fallback for local development
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    # Fallback to local configuration if DATABASE_URL is not set
    DB_USER = "ravishankar"
    DB_PASSWORD = quote("Ravi@1234")  # Encode special characters like '@'
    DB_HOST = "localhost"
    DB_PORT = "5432"
    DB_NAME = "KeepActivePro"
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create SQLAlchemy Engine
engine = create_engine(DATABASE_URL)

# Session Configuration
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize the Database (Create Tables)
def init_db():
    Base.metadata.create_all(bind=engine)

# Dependency to Get DB Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()