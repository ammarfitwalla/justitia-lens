"""Check evidence for a specific case."""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.config import settings
from app.models import Evidence, Case

async def check_evidence(case_id: int = None):
    database_url = settings.get_database_url()
    
    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    print(f"Checking DB: {database_url[:60]}...")
    
    async with async_session() as session:
        if case_id:
            # Check specific case
            query = select(Evidence).where(Evidence.case_id == case_id)
        else:
            # Check all evidence (limit 20)
            query = select(Evidence).limit(20)
            
        result = await session.execute(query)
        evidences = result.scalars().all()
        
        print(f"\nFound {len(evidences)} evidence records:")
        for ev in evidences:
            print(f"  ID {ev.id} (Case {ev.case_id}): {ev.file_path}")
            
    await engine.dispose()

if __name__ == "__main__":
    case_id = int(sys.argv[1]) if len(sys.argv) > 1 else None
    asyncio.run(check_evidence(case_id))
