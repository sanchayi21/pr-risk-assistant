from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv
import os

# Load values from .env file into environment
load_dotenv()

# Read the database URL from .env
DATABASE_URL = os.getenv("DATABASE_URL")

# SQLAlchemy needs a slightly different URL format for async postgres
# Change "postgresql://" to "postgresql+asyncpg://"
DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
DATABASE_URL = DATABASE_URL.split("?")[0]  # remove ?sslmode=require
# Create the engine - this is the actual connection to your database
engine = create_async_engine(DATABASE_URL, echo=True)

# SessionLocal is a factory - every time you call it, you get a new database session
SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class - all our database table models will inherit from this
class Base(DeclarativeBase):
    pass

# Dependency - FastAPI will call this to give each route its own DB session
async def get_db():
    async with SessionLocal() as session:
        yield session