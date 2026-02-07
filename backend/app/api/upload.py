from fastapi import APIRouter, UploadFile, File, Depends, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func as sql_func
from sqlalchemy.orm import selectinload
from app.database import get_db
from app import models, schemas
from app.utils.storage import save_upload_file
from typing import List
import os

router = APIRouter()

@router.get("/cases", response_model=List[schemas.CaseListItem])
async def list_cases(db: AsyncSession = Depends(get_db)):
    """List all cases with their evidence and report counts."""
    # Query cases with counts using subqueries
    evidence_count_subq = (
        select(models.Evidence.case_id, sql_func.count(models.Evidence.id).label("evidence_count"))
        .group_by(models.Evidence.case_id)
        .subquery()
    )
    report_count_subq = (
        select(models.Report.case_id, sql_func.count(models.Report.id).label("report_count"))
        .group_by(models.Report.case_id)
        .subquery()
    )
    
    result = await db.execute(
        select(
            models.Case,
            sql_func.coalesce(evidence_count_subq.c.evidence_count, 0).label("evidence_count"),
            sql_func.coalesce(report_count_subq.c.report_count, 0).label("report_count")
        )
        .outerjoin(evidence_count_subq, models.Case.id == evidence_count_subq.c.case_id)
        .outerjoin(report_count_subq, models.Case.id == report_count_subq.c.case_id)
        .order_by(models.Case.created_at.desc())
    )
    
    cases = []
    for row in result.all():
        case = row[0]
        cases.append(schemas.CaseListItem(
            id=case.id,
            title=case.title,
            description=case.description,
            status=case.status,
            analysis_status=case.analysis_status or "PENDING",
            created_at=case.created_at,
            updated_at=case.updated_at,
            evidence_count=row[1],
            report_count=row[2]
        ))
    
    return cases

@router.get("/sample-cases", response_model=List[schemas.CaseListItem])
async def list_sample_cases(db: AsyncSession = Depends(get_db)):
    """List all sample cases for demo purposes."""
    # Query only sample cases with counts using subqueries
    evidence_count_subq = (
        select(models.Evidence.case_id, sql_func.count(models.Evidence.id).label("evidence_count"))
        .group_by(models.Evidence.case_id)
        .subquery()
    )
    report_count_subq = (
        select(models.Report.case_id, sql_func.count(models.Report.id).label("report_count"))
        .group_by(models.Report.case_id)
        .subquery()
    )
    
    result = await db.execute(
        select(
            models.Case,
            sql_func.coalesce(evidence_count_subq.c.evidence_count, 0).label("evidence_count"),
            sql_func.coalesce(report_count_subq.c.report_count, 0).label("report_count")
        )
        .where(models.Case.is_sample_case == True)
        .outerjoin(evidence_count_subq, models.Case.id == evidence_count_subq.c.case_id)
        .outerjoin(report_count_subq, models.Case.id == report_count_subq.c.case_id)
        .order_by(models.Case.created_at.desc())
    )
    
    cases = []
    for row in result.all():
        case = row[0]
        cases.append(schemas.CaseListItem(
            id=case.id,
            title=case.title,
            description=case.description,
            status=case.status,
            analysis_status=case.analysis_status or "PENDING",
            created_at=case.created_at,
            updated_at=case.updated_at,
            evidence_count=row[1],
            report_count=row[2],
            is_sample_case=True,
            thumbnail_path=case.thumbnail_path
        ))
    
    return cases

@router.post("/cases", response_model=schemas.Case)
async def create_case(case: schemas.CaseCreate, db: AsyncSession = Depends(get_db)):
    new_case = models.Case(title=case.title, description=case.description)
    db.add(new_case)
    await db.commit()
    
    # Re-fetch with eager loading to satisfy Pydantic
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

@router.delete("/cases/{case_id}")
async def delete_case(case_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a case and all associated files."""
    case = await db.get(models.Case, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Prevent deletion of sample cases
    if case.is_sample_case:
        raise HTTPException(status_code=403, detail="Sample cases cannot be deleted")
    
    # Delete the case (cascade will handle related records)
    await db.delete(case)
    await db.commit()
    
    # Optionally delete files from disk
    from app.config import settings
    import shutil
    case_dir = os.path.join(settings.STORAGE_DIR, "cases", str(case_id))
    if os.path.exists(case_dir):
        shutil.rmtree(case_dir)
    
    return {"message": f"Case {case_id} deleted successfully"}

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
        
    # Check evidence limit (Max 3)
    result = await db.execute(
        select(sql_func.count(models.Evidence.id))
        .where(models.Evidence.case_id == case_id)
    )
    current_count = result.scalar()
    if current_count >= 3:
        raise HTTPException(status_code=400, detail="Maximum 3 evidence files allowed per case")

    # Determine type based on mime type or extension
    mime_type = file.content_type
    evidence_type = models.EvidenceType.IMAGE
    if mime_type.startswith("video"):
        evidence_type = models.EvidenceType.VIDEO
    elif mime_type.startswith("audio"):
        evidence_type = models.EvidenceType.AUDIO
    
    # Save file to case-specific directory
    file_path = await save_upload_file(file, case_id=case_id, subfolder="evidence")
    
    new_evidence = models.Evidence(
        case_id=case_id,
        file_path=file_path,
        type=evidence_type,
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
         
    # Check file size (Limit 20MB)
    MAX_SIZE = 20 * 1024 * 1024 # 20MB
    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 20MB")
    
    # Reset file cursor for saving
    await file.seek(0)

    # Save file to case-specific directory
    file_path = await save_upload_file(file, case_id=case_id, subfolder="reports")
    
    new_report = models.Report(
        case_id=case_id,
        file_path=file_path
    )
    db.add(new_report)
    await db.commit()
    await db.refresh(new_report)
    return new_report

