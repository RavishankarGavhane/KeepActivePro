from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote
from .models import Base  # Import Base from models.py
import os

# ✅ Fetch Database Credentials from Environment Variables
DB_USER = os.getenv("DB_USER", "ravipostgres")
DB_PASSWORD = quote(os.getenv("DB_PASSWORD", "Ravi#1234"))
DB_HOST = os.getenv("DB_HOST", "keepactivepro-db.ct8akq62elqa.eu-north-1.rds.amazonaws.com")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "postgres")

# ✅ AWS RDS PostgreSQL Connection String
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# ✅ Create SQLAlchemy Engine
engine = create_engine(DATABASE_URL)

# ✅ Configure Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ✅ Initialize the Database
def init_db():
    Base.metadata.create_all(bind=engine)

# ✅ Dependency to Get Database Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
