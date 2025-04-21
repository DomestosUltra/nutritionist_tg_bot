from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from src.app.core.config import settings

# Create async engine
SQLALCHEMY_DATABASE_URL = (
    f"postgresql+asyncpg://{settings.postgres.USER}:{settings.postgres.PASSWORD}"
    f"@{settings.postgres.HOST}:{settings.postgres.PORT}/{settings.postgres.DB}"
)

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=False,
    future=True,
)

# Create async session
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Dependency for FastAPI
async def get_db() -> AsyncSession:
    """
    Dependency function that yields db sessions
    """
    async with async_session() as session:
        yield session
        await session.close()
