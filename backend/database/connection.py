import os
from contextlib import asynccontextmanager
import asyncpg


DATABASE_URL = os.getenv("DATABASE_URL")
pool = None


async def init_db():
    global pool
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    pool = await asyncpg.create_pool(
        DATABASE_URL,
        min_size=1,
        max_size=10,
        command_timeout=60
    )
    print("✅ Database connection pool created")


async def close_db():
    global pool
    if pool:
        await pool.close()
        print("✅ Database connection pool closed")


async def get_db():
    if not pool:
        raise RuntimeError("Database pool not initialized")
    async with pool.acquire() as connection:
        yield connection
