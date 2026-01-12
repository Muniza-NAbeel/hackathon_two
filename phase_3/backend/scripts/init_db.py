"""
Database initialization script for Phase 3 AI Chatbot

Usage:
    python scripts/init_db.py

This script:
1. Verifies database connection
2. Creates all tables using SQLModel
3. Optionally runs Alembic migrations
4. Seeds initial data if needed
"""
import sys
from pathlib import Path

# Add app directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session, select
from app.db.database import engine, init_db
from app.models import Task, Conversation, Message


def verify_connection() -> bool:
    """
    Verify database connection is working.

    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        with Session(engine) as session:
            # Test connection with a simple query
            session.exec(select(1))
            print("✅ Database connection successful")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def create_tables() -> bool:
    """
    Create all database tables using SQLModel.

    Returns:
        bool: True if tables created successfully, False otherwise
    """
    try:
        print("Creating database tables...")
        init_db()
        print("✅ Database tables created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        return False


def verify_tables() -> bool:
    """
    Verify that all required tables exist.

    Returns:
        bool: True if all tables exist, False otherwise
    """
    try:
        with Session(engine) as session:
            # Try to query each table
            session.exec(select(Task).limit(1))
            session.exec(select(Conversation).limit(1))
            session.exec(select(Message).limit(1))
            print("✅ All tables verified successfully")
            return True
    except Exception as e:
        print(f"❌ Table verification failed: {e}")
        return False


def main():
    """
    Main initialization routine.
    """
    print("=" * 60)
    print("Phase 3 AI Chatbot - Database Initialization")
    print("=" * 60)

    # Step 1: Verify connection
    if not verify_connection():
        print("\n⚠️  Please check your DATABASE_URL in .env file")
        sys.exit(1)

    # Step 2: Create tables
    if not create_tables():
        print("\n⚠️  Failed to create database tables")
        sys.exit(1)

    # Step 3: Verify tables
    if not verify_tables():
        print("\n⚠️  Table verification failed")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("✅ Database initialization complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Run backend: uvicorn app.main:app --reload")
    print("  2. Run migrations: alembic upgrade head")
    print("  3. Run tests: pytest")


if __name__ == "__main__":
    main()
