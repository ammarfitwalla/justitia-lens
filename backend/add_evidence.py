"""Add evidence files to an existing case."""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.config import settings
from app.models import Case, Evidence, EvidenceType

async def add_evidence_to_case():
    database_url = (
        f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@"
        f"{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )
    
    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Find the protest case
        result = await session.execute(
            select(Case).where(Case.title == "Protest Arrest - Case #25-7718")
        )
        case = result.scalar_one_or_none()
        
        if not case:
            print("Case not found!")
            return
        
        print(f"Found case ID: {case.id}")
        
        # Check existing evidence
        ev_result = await session.execute(
            select(Evidence).where(Evidence.case_id == case.id)
        )
        existing = ev_result.scalars().all()
        print(f"Existing evidence: {len(existing)}")
        
        # Add evidence files
        evidence_dir = settings.STORAGE_DIR + "/cases/20/evidence"
        files = sorted(os.listdir(evidence_dir))
        
        for filename in files:
            filepath = os.path.join(evidence_dir, filename)
            if os.path.isfile(filepath) and filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                # Check if already exists
                existing_check = await session.execute(
                    select(Evidence).where(Evidence.file_path == filepath)
                )
                if existing_check.scalar_one_or_none():
                    print(f"  Already exists: {filename}")
                    continue
                
                evidence = Evidence(
                    case_id=case.id,
                    file_path=filepath,
                    type=EvidenceType.IMAGE
                )
                session.add(evidence)
                print(f"  Added: {filename}")
        
        # Update thumbnail
        if files:
            case.thumbnail_path = os.path.join(evidence_dir, files[0])
        
        await session.commit()
        print("Done!")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(add_evidence_to_case())
