"""Alembic environment configuration for async SQLModel."""

import asyncio
import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlmodel import SQLModel

from app.config import get_settings
from app.models import Task, User  # noqa: F401 - Import models for metadata

# Alembic Config object
config = context.config

# Override sqlalchemy.url with our settings
# First try to get from environment directly (for Hugging Face Spaces)
database_url = os.environ.get("DATABASE_URL")

if not database_url:
    # Fallback to settings
    settings = get_settings()
    database_url = settings.database_url

# Debug logging
print(f"[ALEMBIC DEBUG] DATABASE_URL source: {'os.environ' if os.environ.get('DATABASE_URL') else 'settings'}", file=sys.stderr)
print(f"[ALEMBIC DEBUG] DATABASE_URL (masked): {database_url.split('@')[-1] if '@' in database_url else 'INVALID'}", file=sys.stderr)

if not database_url or database_url == "postgresql+asyncpg://localhost/todo_db":
    print("[ALEMBIC ERROR] DATABASE_URL not set or using default value!", file=sys.stderr)
    print("[ALEMBIC ERROR] Available env vars:", list(os.environ.keys()), file=sys.stderr)
    raise ValueError("DATABASE_URL environment variable is not set properly")

config.set_main_option("sqlalchemy.url", database_url)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# SQLModel metadata for autogenerate
target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations with connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in async mode."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args={
            "ssl": True,  # Enable SSL for Neon
            "timeout": 30,  # Connection timeout
            "command_timeout": 30,  # Command timeout
        },
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
