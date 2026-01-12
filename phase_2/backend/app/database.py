"""Database connection and session management for Neon PostgreSQL."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.config import get_settings

settings = get_settings()

# Create async engine for Neon PostgreSQL
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
    pool_pre_ping=True,  # Check connection health before using
    pool_size=5,  # Smaller pool for serverless
    max_overflow=10,
    pool_recycle=300,  # Recycle connections after 5 minutes
    connect_args={
        "ssl": True,  # Enable SSL for Neon (asyncpg expects bool or SSLContext)
        "timeout": 30,  # Connection timeout in seconds
        "command_timeout": 30,  # Command timeout in seconds
        "server_settings": {
            "application_name": "todo_app",
        },
    },
)

# Create async session factory
async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
