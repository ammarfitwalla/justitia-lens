"""Quick script to check case 13 data in database"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.models import Case

async def check():
    url = (
        f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@"
        f"{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )
    engine = create_async_engine(url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Check case 13
        result = await session.execute(select(Case).where(Case.id == 13))
        c = result.scalar_one_or_none()
        
        if c:
            print(f"Case ID: {c.id}")
            print(f"Title: {c.title}")
            print(f"Is Sample: {c.is_sample_case}")
            print(f"Analysis Status: {c.analysis_status}")
            print(f"Has Narrative JSON: {bool(c.narrative_analysis_json)}")
            print(f"Has Vision JSON: {bool(c.vision_analysis_json)}")
            print(f"Has Synthesis JSON: {bool(c.synthesis_analysis_json)}")
            if c.vision_analysis_json:
                import json
                parsed = json.loads(c.vision_analysis_json)
                print(f"Vision JSON observations count: {len(parsed.get('observations', []))}")
                if parsed.get('observations'):
                    print(f"First observation: {parsed['observations'][0].get('label', 'N/A')}")
            else:
                print("Vision JSON is NULL or empty!")
        else:
            print("Case 13 not found!")
        
        # List all sample cases
        print("\n--- All Sample Cases ---")
        result = await session.execute(select(Case).where(Case.is_sample_case == True))
        for sc in result.scalars().all():
            print(f"  ID: {sc.id}, Title: {sc.title}, Has Vision: {bool(sc.vision_analysis_json)}")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check())
