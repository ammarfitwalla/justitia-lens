"""
Migration script to upload existing sample case files to Supabase Storage.
Uses LOCAL database to read data, uploads files to Supabase.

Usage:
    cd backend
    .\venv\Scripts\python.exe migrate_to_supabase.py
"""

import asyncio
import os
import sys
import httpx

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.config import settings
from app.models import Case, Evidence, Report


async def upload_to_supabase_storage(file_path: str, storage_path: str) -> str:
    """Upload a file to Supabase Storage using REST API."""
    url = f"{settings.SUPABASE_URL}/storage/v1/object/{settings.SUPABASE_BUCKET}/{storage_path}"
    
    with open(file_path, "rb") as f:
        content = f.read()
    
    # Determine content type
    ext = os.path.splitext(file_path)[1].lower()
    content_type = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".pdf": "application/pdf",
        ".mp4": "video/mp4",
    }.get(ext, "application/octet-stream")
    
    headers = {
        "Authorization": f"Bearer {settings.SUPABASE_KEY}",
        "Content-Type": content_type,
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, content=content, headers=headers)
        
        if response.status_code in [200, 201]:
            # Success - get public URL
            public_url = f"{settings.SUPABASE_URL}/storage/v1/object/public/{settings.SUPABASE_BUCKET}/{storage_path}"
            return public_url
        elif response.status_code == 409:
            # File already exists - return the public URL anyway
            public_url = f"{settings.SUPABASE_URL}/storage/v1/object/public/{settings.SUPABASE_BUCKET}/{storage_path}"
            return public_url
        else:
            raise Exception(f"Upload failed: {response.status_code} - {response.text}")


async def migrate_files():
    """Upload all local files to Supabase and update DB paths."""
    
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        print("ERROR: SUPABASE_URL and SUPABASE_KEY must be set in .env")
        return
    
    # Connect to database using settings URL (Supabase)
    database_url = settings.get_database_url()
    
    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    print(f"\n{'='*60}")
    print("SUPABASE STORAGE MIGRATION")
    print(f"{'='*60}")
    print(f"Bucket: {settings.SUPABASE_BUCKET}")
    print(f"Supabase: {settings.SUPABASE_URL}")
    print(f"Database: {database_url[:50]}...")
    print(f"{'='*60}\n")
    
    async with async_session() as session:
        # Get all evidence records
        result = await session.execute(select(Evidence))
        evidences = result.scalars().all()
        
        print(f"Found {len(evidences)} evidence records\n")
        
        for ev in evidences:
            # Skip if already a URL
            if ev.file_path and (ev.file_path.startswith("http://") or ev.file_path.startswith("https://")):
                print(f"  [SKIP] ID {ev.id}: Already a URL")
                continue
            
            # Check if local file exists
            if not ev.file_path or not os.path.exists(ev.file_path):
                print(f"  [WARN] ID {ev.id}: File not found: {ev.file_path}")
                continue
            
            # Upload to Supabase
            filename = os.path.basename(ev.file_path)
            storage_path = f"cases/{ev.case_id}/evidence/{filename}"
            
            try:
                public_url = await upload_to_supabase_storage(ev.file_path, storage_path)
                ev.file_path = public_url
                print(f"  [OK] ID {ev.id}: {filename} -> Supabase")
                
            except Exception as e:
                print(f"  [ERR] ID {ev.id}: {e}")
        
        # Handle Reports too
        result = await session.execute(select(Report))
        reports = result.scalars().all()
        
        print(f"\nFound {len(reports)} report records\n")
        
        for report in reports:
            if report.file_path and (report.file_path.startswith("http://") or report.file_path.startswith("https://")):
                print(f"  [SKIP] ID {report.id}: Already a URL")
                continue
            
            if not report.file_path or not os.path.exists(report.file_path):
                print(f"  [WARN] ID {report.id}: File not found: {report.file_path}")
                continue
            
            filename = os.path.basename(report.file_path)
            storage_path = f"cases/{report.case_id}/reports/{filename}"
            
            try:
                public_url = await upload_to_supabase_storage(report.file_path, storage_path)
                report.file_path = public_url
                print(f"  [OK] ID {report.id}: {filename} -> Supabase")
                
            except Exception as e:
                print(f"  [ERR] ID {report.id}: {e}")
        
        # Update case thumbnails
        result = await session.execute(select(Case))
        cases = result.scalars().all()
        
        print(f"\nUpdating {len(cases)} case thumbnails...\n")
        
        for case in cases:
            if case.thumbnail_path and not (case.thumbnail_path.startswith("http://") or case.thumbnail_path.startswith("https://")):
                # Find the corresponding evidence URL
                ev_result = await session.execute(
                    select(Evidence).where(Evidence.case_id == case.id).limit(1)
                )
                first_ev = ev_result.scalar_one_or_none()
                if first_ev and first_ev.file_path:
                    case.thumbnail_path = first_ev.file_path
                    print(f"  [OK] Case {case.id}: Thumbnail updated")
        
        await session.commit()
    
    await engine.dispose()
    
    print(f"\n{'='*60}")
    print("MIGRATION COMPLETE")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(migrate_files())
