import os
import sys

# Calculate the path to the project's root directory from env.py's location
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, project_root)

from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context

from app.config import DATABASE_URL
from app.database import Base
from app import models  # Ensure this import loads all models

config = context.config

# Set up logging from alembic.ini (only for logging configuration)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Use Base.metadata as target_metadata
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = create_engine(DATABASE_URL, poolclass=pool.NullPool, future=True)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
