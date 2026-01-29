from fastapi import APIRouter, UploadFile, File, Depends, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app import models, schemas
from app.utils.storage import save_upload_file
import os

router = APIRouter()

@router.post("/cases", response_model=schemas.Case)
async def create_case(case: schemas.CaseCreate, db: AsyncSession = Depends(get_db)):
    new_case = models.Case(title=case.title, description=case.description)
    db.add(new_case)
    await db.commit()
    # await db.refresh(new_case) # Refresh is often not enough for relationships in async
    
    # Re-fetch with eager loading to satisfy Pydantic
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    
    result = await db.execute(
        select(models.Case)
        .where(models.Case.id == new_case.id)
        .options(
            selectinload(models.Case.evidence),
            selectinload(models.Case.reports),
            selectinload(models.Case.discrepancies)
        )
    )
    return result.scalar_one()

@router.get("/cases/{case_id}", response_model=schemas.Case)
async def get_case(case_id: int, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    
    result = await db.execute(
        select(models.Case)
        .where(models.Case.id == case_id)
        .options(
            selectinload(models.Case.evidence),
            selectinload(models.Case.reports),
            selectinload(models.Case.discrepancies)
        )
    )
    case = result.scalar_one_or_none()
    
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

@router.post("/upload/evidence/{case_id}", response_model=schemas.Evidence)
async def upload_evidence(
    case_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    # Check if case exists
    case = await db.get(models.Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    # Save file locally
    # Determine type based on mime type or extension
    mime_type = file.content_type
    evidence_type = models.EvidenceType.IMAGE
    if mime_type.startswith("video"):
        evidence_type = models.EvidenceType.VIDEO
    elif mime_type.startswith("audio"):
        evidence_type = models.EvidenceType.AUDIO
    
    file_path = await save_upload_file(file, subfolder="evidence")
    
    new_evidence = models.Evidence(
        case_id=case_id,
        file_path=file_path,
        type=evidence_type,
        # Default metadata could be extracted later
    )
    db.add(new_evidence)
    await db.commit()
    await db.refresh(new_evidence)
    return new_evidence

@router.post("/upload/report/{case_id}", response_model=schemas.Report)
async def upload_report(
    case_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    # Check if case exists
    case = await db.get(models.Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    if not file.filename.endswith(".pdf"):
         raise HTTPException(status_code=400, detail="Only PDF reports are supported")

    file_path = await save_upload_file(file, subfolder="reports")
    
    new_report = models.Report(
        case_id=case_id,
        file_path=file_path
    )
    db.add(new_report)
    await db.commit()
    await db.refresh(new_report)
    return new_report
