import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

# Use environment variable for database URL if provided, otherwise default to sqlite+aiosqlite
# Postgres example: "postgresql+asyncpg://user:password@localhost/dbname"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./chess.db")

engine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
