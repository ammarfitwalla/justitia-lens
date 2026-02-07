"""Check and swap evidence order for protest case."""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.config import settings
from app.models import Evidence

async def check_and_swap():
    database_url = (
        f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@"
        f"{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )
    
    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Get evidence for case 16 (protest case)
        result = await session.execute(
            select(Evidence).where(Evidence.case_id == 16).order_by(Evidence.id)
        )
        evidences = result.scalars().all()
        
        print("Current order:")
        for i, ev in enumerate(evidences, 1):
            filename = os.path.basename(ev.file_path)
            print(f"  #{i} (DB ID {ev.id}): {filename}")
        
        if len(evidences) == 2:
            # Swap file paths
            path1, path2 = evidences[0].file_path, evidences[1].file_path
            evidences[0].file_path = path2
            evidences[1].file_path = path1
            
            await session.commit()
            print("\nSwapped! New order:")
            for i, ev in enumerate(evidences, 1):
                filename = os.path.basename(ev.file_path)
                print(f"  #{i} (DB ID {ev.id}): {filename}")
        else:
            print(f"Expected 2 evidence items, found {len(evidences)}")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_and_swap())
