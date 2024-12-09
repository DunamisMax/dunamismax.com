from logging.config import fileConfig
from sqlalchemy import create_engine
from sqlalchemy import pool
from alembic import context

from app.config import DATABASE_URL

config = context.config

# Set up logging from alembic.ini (only for logging config, not DB URL)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# If you have models metadata, import and set here:
# from app.models import Base
# target_metadata = Base.metadata
target_metadata = None


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    # Use the DATABASE_URL from .env directly
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
    # Use the DATABASE_URL from .env directly
    connectable = create_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
        future=True
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
