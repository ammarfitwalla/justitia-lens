from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app import models, schemas
from app.services.agent_narrative import AgentNarrative
from app.services.agent_vision import AgentVision
from typing import List

router = APIRouter()

# Instantiate agents
narrative_agent = AgentNarrative()
vision_agent = AgentVision()

@router.post("/analyze/case/{case_id}/narrative", response_model=schemas.NarrativeAnalysisResult)
async def analyze_narrative(case_id: int, db: AsyncSession = Depends(get_db)):
    """
    Triggers Agent 1 to read the report and extract claims.
    """
    # 1. Get Report
    result = await db.execute(
        models.Report.__table__.select().where(models.Report.case_id == case_id)
    )
    report = result.first()
    
    if not report:
        raise HTTPException(status_code=404, detail="No report found for this case")
        
    # 2. Run Agent
    analysis_dict = await narrative_agent.process_report(report.file_path)
    
    if "error" in analysis_dict:
         raise HTTPException(status_code=500, detail=analysis_dict["error"])

    # 3. Validate & Return
    try:
        return schemas.NarrativeAnalysisResult(**analysis_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schema Validation Failed: {e}")

@router.post("/analyze/evidence/{evidence_id}", response_model=schemas.VisionAnalysisResult)
async def analyze_evidence_item(evidence_id: int, db: AsyncSession = Depends(get_db)):
    """
    Triggers Agent 2 to analyze a specific piece of evidence.
    """
    evidence = await db.get(models.Evidence, evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
        
    if evidence.type != models.EvidenceType.IMAGE:
         raise HTTPException(status_code=400, detail="Only Image analysis supported in MVP")
         
    # Run Agent
    analysis_dict = await vision_agent.analyze_evidence(evidence.file_path)
    
    if "error" in analysis_dict:
         raise HTTPException(status_code=500, detail=analysis_dict["error"])
         
    # Validate & Return
    try:
        return schemas.VisionAnalysisResult(**analysis_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schema Validation Failed: {e}")

