from sqlmodel.ext.asyncio.session import AsyncEngine # Use this for the engine object itself
from sqlalchemy.ext.asyncio import create_async_engine # Use this function to create the engine instance
from app.config import settings

# For async operations with SQLModel/SQLAlchemy
# The URL should already be async-compatible (e.g., "postgresql+asyncpg://...")
async_engine = AsyncEngine(
    create_async_engine(settings.DATABASE_URL, echo=settings.DB_ECHO_LOG)
)

# Note on SQLModel.metadata.create_all(engine):
# This is typically used for synchronous engine setup during development or testing.
# For asynchronous engines and production, Alembic migrations are the standard way
# to create and update database schema. Avoid calling create_all with an async engine
# unless specifically guided by SQLModel documentation for such a use case.
# Alembic handles schema creation based on your models and migration scripts.

# If you still need a synchronous engine for some specific tools or scripts (not for FastAPI app):
# from sqlmodel import create_engine
# sync_engine = create_engine(settings.DATABASE_URL.replace("+asyncpg", ""), echo=settings.DB_ECHO_LOG) # Example: replace async driver
# Be careful with this, DATABASE_URL might need adjustment for sync drivers.
