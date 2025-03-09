from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote
from backend.models import Base  # Import Base from models.py
import os


# AWS RDS Database Configuration
DB_USER = "ravipostgres"
DB_PASSWORD = quote("Ravi#1234")  
DB_HOST = "keepactivepro-db.ct8akq62elqa.eu-north-1.rds.amazonaws.com"
DB_PORT = "5432"
DB_NAME = "postgres"


# AWS RDS PostgreSQL Connection String
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


# Create SQLAlchemy Engine
engine = create_engine(DATABASE_URL)


# Configure Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Initialize the Database & Create Tables
def init_db():
    Base.metadata.create_all(bind=engine)  # Create all tables in DB


# Dependency to Get Database Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
