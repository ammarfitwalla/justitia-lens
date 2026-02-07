import asyncio
import sys
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.config import settings

async def check_tables():
    url = settings.get_database_url()
    print(f"Checking tables in: {url[:60]}...")
    engine = create_async_engine(url, echo=False)
    
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
        tables = [r[0] for r in result.fetchall()]
        print(f"Tables found: {tables}")
        
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_tables())
