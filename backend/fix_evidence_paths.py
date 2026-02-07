"""Fix evidence paths for case 13 - Bar Disturbance."""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.config import settings
from app.models import Evidence, Case

async def fix_evidence():
    database_url = (
        f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@"
        f"{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )
    
    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Get evidence for case 13
        result = await session.execute(
            select(Evidence).where(Evidence.case_id == 13).order_by(Evidence.id)
        )
        evidences = result.scalars().all()
        
        # Get actual files in directory
        evidence_dir = os.path.join(settings.STORAGE_DIR, "cases", "10", "evidence")
        actual_files = sorted([f for f in os.listdir(evidence_dir) 
                              if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))])
        
        print(f"DB Evidence records: {len(evidences)}")
        print(f"Actual files: {len(actual_files)}")
        for f in actual_files:
            print(f"  - {f}")
        
        # Update paths
        for i, ev in enumerate(evidences):
            if i < len(actual_files):
                new_path = os.path.join(evidence_dir, actual_files[i])
                print(f"\nUpdating ID {ev.id}:")
                print(f"  Old: {ev.file_path}")
                print(f"  New: {new_path}")
                ev.file_path = new_path
        
        # Update case thumbnail
        case_result = await session.execute(select(Case).where(Case.id == 13))
        case = case_result.scalar_one_or_none()
        if case and actual_files:
            case.thumbnail_path = os.path.join(evidence_dir, actual_files[0])
            print(f"\nUpdated thumbnail: {case.thumbnail_path}")
        
        await session.commit()
        print("\nDone!")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(fix_evidence())
