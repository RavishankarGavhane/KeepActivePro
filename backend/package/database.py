# fastapi_backend/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote
from .models import Base  # Import Base from models.py


# Database Configuration
DB_USER = "ravishankar"
DB_PASSWORD = quote("Ravi@1234")
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "KeepActivePro"


DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


# Create SQLAlchemy Engine
engine = create_engine(DATABASE_URL)

# Session Configuration
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize the Database
def init_db():
    Base.metadata.create_all(bind=engine)

# Dependency to Get DB Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()