import logging
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.schema import CreateTable

from src.app.db.base import Base
from src.app.db.models import UserInteraction

logger = logging.getLogger(__name__)


async def create_tables(engine: AsyncEngine) -> None:
    """
    Create database tables if they don't exist
    """
    async with engine.begin() as conn:
        logger.info("Creating database tables if they don't exist")

        # Create tables
        await conn.run_sync(Base.metadata.create_all)

        logger.info("Database tables created successfully")


async def drop_tables(engine: AsyncEngine) -> None:
    """
    Drop all database tables (use with caution)
    """
    async with engine.begin() as conn:
        logger.warning("Dropping all database tables!")

        # Drop tables
        await conn.run_sync(Base.metadata.drop_all)

        logger.info("Database tables dropped successfully")
