from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from fast_zero.settings import Settings

async_engine = create_async_engine(Settings().DATABASE_URL)


async def get_session():  # pragma: no cover.
    async with AsyncSession(async_engine, expire_on_commit=False) as session:
        yield session
