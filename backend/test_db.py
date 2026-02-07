"""Test Supabase database connection."""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.config import settings


async def test_connection():
    url = settings.get_database_url()
    print(f"Testing connection to: {url[:60]}...")
    
    try:
        engine = create_async_engine(url, echo=False)
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("✅ Connected to Supabase PostgreSQL!")
        await engine.dispose()
    except Exception as e:
        print(f"❌ Connection failed: {e}")


if __name__ == "__main__":
    asyncio.run(test_connection())
