"""
Database session management for Phase 3 AI Chatbot

Provides:
- SQLModel async engine configuration
- Async session factory for dependency injection
- Database initialization
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from app.config import settings


# Create async database engine
# echo=True for development (logs SQL queries)
# pool_pre_ping=True to handle stale connections
# Convert postgresql:// to postgresql+asyncpg:// for async support
database_url = settings.DATABASE_URL

if database_url.startswith("postgresql://"):
    # Replace postgresql:// with postgresql+asyncpg://
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    # Remove parameters that asyncpg doesn't support
    # sslmode -> ssl, channel_binding is not supported by asyncpg
    if "sslmode=require" in database_url:
        database_url = database_url.replace("sslmode=require", "ssl=require")
    if "sslmode=disable" in database_url:
        database_url = database_url.replace("sslmode=disable", "ssl=disable")
    if "&channel_binding=require" in database_url:
        database_url = database_url.replace("&channel_binding=require", "")
    if "?channel_binding=require" in database_url:
        database_url = database_url.replace("?channel_binding=require", "")

elif database_url.startswith("sqlite://"):
    # For SQLite, use aiosqlite
    database_url = database_url.replace("sqlite://", "sqlite+aiosqlite://", 1)

# Create engine with appropriate settings based on database type
is_sqlite = "sqlite" in database_url

if is_sqlite:
    # SQLite doesn't support connection pooling options
    from sqlalchemy.pool import StaticPool
    engine = create_async_engine(
        database_url,
        echo=settings.DEBUG,
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    # PostgreSQL with connection pool settings for Neon
    engine = create_async_engine(
        database_url,
        echo=settings.DEBUG,
        future=True,
        # Connection Pool Settings for Serverless DBs (Neon)
        pool_size=5,  # Small pool for free tier
        max_overflow=10,  # Allow up to 15 total connections during spikes
        pool_timeout=30,  # Wait up to 30s for connection from pool
        pool_recycle=3600,  # Recycle connections after 1 hour
        pool_pre_ping=True,  # Verify connections before using them
        # asyncpg-specific settings for Neon cold starts
        connect_args={
            "timeout": 30,  # Connection timeout (increased for cold starts)
            "command_timeout": 30,  # Query timeout (increased for auth queries)
            "server_settings": {
                "application_name": "phase3_todo_app",
            },
        },
    )

# Create async session factory
async_session_maker = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Database session dependency for FastAPI.

    Yields an async database session that is automatically closed after use.
    Use this as a FastAPI dependency for route handlers.

    Example:
        @app.get("/tasks")
        async def get_tasks(session: AsyncSession = Depends(get_session)):
            result = await session.execute(select(Task))
            tasks = result.scalars().all()
            return tasks

    Yields:
        AsyncSession: SQLAlchemy async database session
    """
    session = async_session_maker()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def init_db() -> None:
    """
    Initialize database by creating all tables.

    This is called on application startup to ensure all tables exist.
    In production, use Alembic migrations instead.

    Note:
        - Creates tables only if they don't exist
        - Safe to call multiple times
        - Does NOT run migrations (use Alembic for that)
    """
    # Import all models to register them with SQLModel
    from app.models import Task, Conversation, Message, User

    # Create all tables using async engine
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def warm_up_connection_pool() -> None:
    """
    Pre-warm the connection pool at startup.

    This prevents the first request from timing out due to:
    - Neon serverless cold starts (2-5 seconds)
    - Connection pool initialization overhead
    - SSL handshake delays

    Called during FastAPI startup event.
    """
    from sqlalchemy import text

    try:
        # Execute a simple query to initialize the pool
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        print("✅ Database connection pool warmed up successfully")
    except Exception as e:
        print(f"⚠️  Failed to warm up connection pool: {e}")
        print("   First request may experience timeout - retry will work")
