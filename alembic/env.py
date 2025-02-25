from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context
import sys
import os
from urllib.parse import quote

# Add FastAPI backend path to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "fastapi_backend")))

# Set up Python logging
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import Base from models.py
from fastapi_backend.models import Base

# Database Configuration (Encode Special Characters)
DB_USER = "ravishankar"
DB_PASSWORD = quote("Ravi@1234")  # Properly encode special characters
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "KeepActivePro"

# Generate the DATABASE_URL
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Set target metadata
target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure(
        url=DATABASE_URL,  # Pass URL directly
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = create_engine(DATABASE_URL, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
