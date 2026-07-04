import asyncio
from database import engine, Base
import models  # this import is important - it registers all models with Base

async def init_db():
    async with engine.begin() as conn:
        print("Creating tables...")
        await conn.run_sync(Base.metadata.create_all)
        print("Done! All tables created successfully.")

asyncio.run(init_db())