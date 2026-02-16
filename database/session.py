from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from config.settings import settings

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.LOG_LEVEL == "DEBUG",
    future=True,
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    """
    Dependency function to get database session.
    Usage:
        async with get_db() as session:
            await session.execute(...)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
