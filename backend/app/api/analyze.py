from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app import models, schemas
from app.services.agent_narrative import AgentNarrative
from app.services.agent_vision import AgentVision
from app.services.synthesizer import AgentSynthesizer
from typing import List
import json

router = APIRouter()

# Instantiate agents
narrative_agent = AgentNarrative()
vision_agent = AgentVision()
synthesizer_agent = AgentSynthesizer()

@router.post("/analyze/case/{case_id}/narrative", response_model=schemas.NarrativeAnalysisResult)
async def analyze_narrative(case_id: int, force_rerun: bool = False, db: AsyncSession = Depends(get_db)):
    """
    Triggers Agent 1 to read the report and extract claims.
    If already analyzed, returns cached result unless force_rerun=True.
    """
    # Get case with reports
    result = await db.execute(
        select(models.Case)
        .where(models.Case.id == case_id)
        .options(selectinload(models.Case.reports))
    )
    case = result.scalar_one_or_none()
    
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Check for cached result
    if case.narrative_analysis_json and not force_rerun:
        try:
            cached_result = json.loads(case.narrative_analysis_json)
            return schemas.NarrativeAnalysisResult(**cached_result)
        except (json.JSONDecodeError, Exception) as e:
            print(f"Failed to parse cached narrative result: {e}")
    
    # Get report
    if not case.reports:
        raise HTTPException(status_code=404, detail="No report found for this case")
    
    report = case.reports[0]
    
    # Update status to IN_PROGRESS
    case.analysis_status = "IN_PROGRESS"
    await db.commit()
    
    # Run Agent
    analysis_dict = await narrative_agent.process_report(report.file_path)
    
    if "error" in analysis_dict:
        error_msg = analysis_dict["error"]
        print(f"Narrative Agent Error: {error_msg}")
        if "429" in error_msg or "Quota" in error_msg or "ResourceExhausted" in error_msg:
            raise HTTPException(status_code=429, detail=f"Rate Limit Exceeded: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

    # Cache the result
    case.narrative_analysis_json = json.dumps(analysis_dict)
    await db.commit()
    
    # Validate & Return
    try:
        return schemas.NarrativeAnalysisResult(**analysis_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schema Validation Failed: {e}")

@router.post("/analyze/evidence/{evidence_id}", response_model=schemas.VisionAnalysisResult)
async def analyze_evidence_item(evidence_id: int, force_rerun: bool = False, db: AsyncSession = Depends(get_db)):
    """
    Triggers Agent 2 to analyze a specific piece of evidence.
    """
    evidence = await db.get(models.Evidence, evidence_id)
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
        
    if evidence.type != models.EvidenceType.IMAGE:
         raise HTTPException(status_code=400, detail="Only Image analysis supported in MVP")
    
    # Get the case to cache results
    case = await db.get(models.Case, evidence.case_id)
    
    # Check for cached result
    if case and case.vision_analysis_json and not force_rerun:
        try:
            cached_result = json.loads(case.vision_analysis_json)
            return schemas.VisionAnalysisResult(**cached_result)
        except (json.JSONDecodeError, Exception) as e:
            print(f"Failed to parse cached vision result: {e}")
    
    # Run Agent
    analysis_dict = await vision_agent.analyze_evidence(evidence.file_path)
    
    if "error" in analysis_dict:
        error_msg = analysis_dict["error"]
        if "429" in error_msg or "Quota" in error_msg or "ResourceExhausted" in error_msg:
            raise HTTPException(status_code=429, detail=f"Rate Limit Exceeded: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)
    
    # Cache the result and update status
    if case:
        case.vision_analysis_json = json.dumps(analysis_dict)
        # Mark as completed if both analyses are done
        if case.narrative_analysis_json:
            case.analysis_status = "COMPLETED"
        await db.commit()
        
    # Validate & Return
    try:
        return schemas.VisionAnalysisResult(**analysis_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schema Validation Failed: {e}")

@router.post("/analyze/case/{case_id}/rerun")
async def rerun_analysis(case_id: int, db: AsyncSession = Depends(get_db)):
    """
    Clears cached analysis results and triggers a fresh analysis.
    """
    result = await db.execute(
        select(models.Case)
        .where(models.Case.id == case_id)
        .options(
            selectinload(models.Case.reports),
            selectinload(models.Case.evidence)
        )
    )
    case = result.scalar_one_or_none()
    
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Clear cached results
    case.narrative_analysis_json = None
    case.vision_analysis_json = None
    case.analysis_status = "PENDING"
    await db.commit()
    
    # Run fresh analysis
    narrative_result = None
    vision_result = None
    
    # Narrative analysis
    if case.reports:
        try:
            narrative_res = await analyze_narrative(case_id, force_rerun=True, db=db)
            narrative_result = narrative_res
        except HTTPException as e:
            narrative_result = {"error": e.detail}
    
    # Vision analysis - now analyzes ALL images
    if case.evidence:
        try:
            vision_res = await analyze_all_evidence(case_id, force_rerun=True, db=db)
            vision_result = vision_res
        except HTTPException as e:
            vision_result = {"error": e.detail}
    
    return {
        "message": "Analysis rerun completed",
        "narrative_analysis": narrative_result,
        "vision_analysis": vision_result
    }


@router.post("/analyze/case/{case_id}/evidence", response_model=schemas.VisionAnalysisResult)
async def analyze_all_evidence(case_id: int, force_rerun: bool = False, db: AsyncSession = Depends(get_db)):
    """
    Analyzes ALL image evidence for a case and aggregates the results.
    Each observation includes the source evidence ID for reference.
    """
    # Get case with all evidence
    result = await db.execute(
        select(models.Case)
        .where(models.Case.id == case_id)
        .options(selectinload(models.Case.evidence))
    )
    case = result.scalar_one_or_none()
    
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Check for cached result
    if case.vision_analysis_json and not force_rerun:
        try:
            cached_result = json.loads(case.vision_analysis_json)
            return schemas.VisionAnalysisResult(**cached_result)
        except (json.JSONDecodeError, Exception) as e:
            print(f"Failed to parse cached vision result: {e}")
    
    # Get all image evidence
    images = [e for e in case.evidence if e.type == models.EvidenceType.IMAGE]
    
    if not images:
        raise HTTPException(status_code=404, detail="No image evidence found for this case")
    
    # Analyze each image and aggregate observations
    all_observations = []
    
    for idx, evidence in enumerate(images):
        try:
            analysis_dict = await vision_agent.analyze_evidence(evidence.file_path)
            
            if "error" in analysis_dict:
                print(f"Vision Agent Error for evidence {evidence.id}: {analysis_dict['error']}")
                continue
            
            # Add source info to each observation
            for obs in analysis_dict.get("observations", []):
                obs["evidence_id"] = evidence.id
                obs["evidence_index"] = idx + 1  # 1-based for display
                all_observations.append(obs)
                
        except Exception as e:
            print(f"Failed to analyze evidence {evidence.id}: {e}")
            continue
    
    # Build aggregated result
    aggregated_result = {"observations": all_observations}
    
    # Cache the aggregated result
    case.vision_analysis_json = json.dumps(aggregated_result)
    
    # Mark as completed if narrative is also done
    if case.narrative_analysis_json:
        case.analysis_status = "COMPLETED"
    
    await db.commit()
    
    return schemas.VisionAnalysisResult(**aggregated_result)


@router.post("/analyze/case/{case_id}/synthesize", response_model=schemas.SynthesisAnalysisResult)
async def synthesize_analysis(case_id: int, force_rerun: bool = False, db: AsyncSession = Depends(get_db)):
    """
    Cross-references narrative claims with visual observations to detect discrepancies.
    This is the core value proposition - finding contradictions between what the report says
    and what the evidence shows.
    
    Requires both narrative and vision analysis to be completed first.
    """
    # Get case with all analysis data
    result = await db.execute(
        select(models.Case)
        .where(models.Case.id == case_id)
    )
    case = result.scalar_one_or_none()
    
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Check for cached result
    if case.synthesis_analysis_json and not force_rerun:
        try:
            cached_result = json.loads(case.synthesis_analysis_json)
            return schemas.SynthesisAnalysisResult(**cached_result)
        except (json.JSONDecodeError, Exception) as e:
            print(f"Failed to parse cached synthesis result: {e}")
    
    # Verify both analyses are complete
    if not case.narrative_analysis_json:
        raise HTTPException(
            status_code=400, 
            detail="Narrative analysis must be completed before synthesis. Run narrative analysis first."
        )
    
    if not case.vision_analysis_json:
        raise HTTPException(
            status_code=400, 
            detail="Vision analysis must be completed before synthesis. Run vision analysis first."
        )
    
    # Parse cached results
    try:
        narrative_data = json.loads(case.narrative_analysis_json)
        vision_data = json.loads(case.vision_analysis_json)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse cached analysis data: {e}")
    
    # Convert to schemas for the synthesizer
    try:
        narrative_result = schemas.NarrativeAnalysisResult(**narrative_data)
        vision_result = schemas.VisionAnalysisResult(**vision_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to validate analysis schemas: {e}")
    
    # Run the synthesizer agent
    synthesis_dict = await synthesizer_agent.detect_discrepancies(narrative_result, vision_result)
    
    if "error" in synthesis_dict:
        error_msg = synthesis_dict["error"]
        print(f"Synthesizer Agent Error: {error_msg}")
        if "429" in error_msg or "Quota" in error_msg or "ResourceExhausted" in error_msg:
            raise HTTPException(status_code=429, detail=f"Rate Limit Exceeded: {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)
    
    # Cache the result
    case.synthesis_analysis_json = json.dumps(synthesis_dict)
    case.analysis_status = "COMPLETED"  # Fully complete now
    await db.commit()
    
    # Validate & Return
    try:
        return schemas.SynthesisAnalysisResult(**synthesis_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schema Validation Failed: {e}")
