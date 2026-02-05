"""
Seed script to create sample cases from existing case data.
Run this script to populate the database with sample cases for demo purposes.

Usage:
    cd backend
    python seed_sample_cases.py
"""

import asyncio
import json
import os
import sys

# Add the app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.config import settings
from app.models import Base, Case, Evidence, Report, EvidenceType

# ============================================================================
# PRE-COMPUTED ANALYSIS DATA FOR SAMPLE CASES
# ============================================================================

# Case #25-8842: Bar Disturbance - Officer claims knife, evidence shows phone
CASE_25_8842_NARRATIVE = {
    "timeline": [
        {
            "timestamp_ref": "23:45",
            "entity": "Ofc. J. Miller",
            "action": "responded to",
            "object": "disturbance call at Blue Note Bar",
            "certainty": "EXPLICIT",
            "description": "Officer responded to a disturbance call at the Blue Note Bar parking lot"
        },
        {
            "timestamp_ref": "23:45",
            "entity": "Michael Kowalski",
            "action": "observed standing near",
            "object": "white Ford F-150",
            "certainty": "EXPLICIT",
            "description": "Suspect observed standing near a white Ford F-150, appearing intoxicated and shouting at patrons"
        },
        {
            "timestamp_ref": "23:46",
            "entity": "Ofc. J. Miller",
            "action": "issued verbal command",
            "object": "to place hands on vehicle",
            "certainty": "EXPLICIT",
            "description": "Officer approached and issued verbal command for suspect to place hands on vehicle"
        },
        {
            "timestamp_ref": "23:47",
            "entity": "Michael Kowalski",
            "action": "refused to comply",
            "object": None,
            "certainty": "EXPLICIT",
            "description": "Suspect refused to comply and assumed aggressive stance, shouting 'I'm not going back!'"
        },
        {
            "timestamp_ref": "23:48",
            "entity": "Michael Kowalski",
            "action": "reached into waistband and produced",
            "object": "metallic object with 4-inch blade",
            "certainty": "EXPLICIT",
            "description": "Officer reports suspect reached into right waistband and produced a metallic object with a roughly 4-inch blade"
        },
        {
            "timestamp_ref": "23:48",
            "entity": "Ofc. J. Miller",
            "action": "drew service weapon",
            "object": None,
            "certainty": "EXPLICIT",
            "description": "Officer drew service weapon believing suspect was armed with knife and posed deadly threat"
        },
        {
            "timestamp_ref": "23:48",
            "entity": "Michael Kowalski",
            "action": "raised object in stabbing motion and lunged",
            "object": "toward officer",
            "certainty": "EXPLICIT",
            "description": "Officer reports suspect raised the object above his head in stabbing motion and lunged toward officer"
        },
        {
            "timestamp_ref": "23:49",
            "entity": "Ofc. J. Miller",
            "action": "deployed Taser",
            "object": "X26 to neutralize threat",
            "certainty": "EXPLICIT",
            "description": "Officer deployed Taser (X26) to neutralize threat, suspect taken into custody"
        },
        {
            "timestamp_ref": "23:50",
            "entity": "Metallic object",
            "action": "was recovered from",
            "object": "pavement",
            "certainty": "EXPLICIT",
            "description": "Metallic object was recovered from the pavement and logged as evidence"
        }
    ]
}

CASE_25_8842_VISION = {
    "observations": [
        {
            "timestamp_ref": "23:48:00",
            "category": "OBJECT",
            "entity": "Suspect",
            "label": "Silver smartphone in hand",
            "confidence": "HIGH",
            "details": "Suspect is pulling a silver iPhone out of his waistband. The phone screen is illuminated/lit up. The object is rectangular and consistent with a smartphone, NOT a knife.",
            "evidence_index": 1
        },
        {
            "timestamp_ref": "23:48:00",
            "category": "ACTION",
            "entity": "Suspect",
            "label": "Removing object from waistband",
            "confidence": "HIGH",
            "details": "Suspect's right hand is reaching into waistband area and producing a reflective rectangular object. Motion is consistent with retrieving a phone, not a weapon.",
            "evidence_index": 1
        },
        {
            "timestamp_ref": "23:48:00",
            "category": "ENVIRONMENT",
            "entity": "Scene",
            "label": "Night time parking lot",
            "confidence": "HIGH",
            "details": "CCTV footage shows night time scene in parking lot. Police car lights visible in background. Grainy texture typical of security camera footage.",
            "evidence_index": 1
        },
        {
            "timestamp_ref": "23:48:00",
            "category": "PERSON",
            "entity": "Suspect",
            "label": "Male in hoodie",
            "confidence": "HIGH",
            "details": "Male subject wearing hoodie standing in parking lot area.",
            "evidence_index": 1
        },
        {
            "timestamp_ref": "23:50:00",
            "category": "OBJECT",
            "entity": "Evidence on ground",
            "label": "Silver smartphone with cracked screen",
            "confidence": "HIGH",
            "details": "Flashlight photo shows silver smartphone lying on asphalt. Screen is cracked. Police evidence marker #1 placed next to it. Object is clearly a phone, NOT a knife or blade.",
            "evidence_index": 2
        },
        {
            "timestamp_ref": "23:50:00",
            "category": "ENVIRONMENT",
            "entity": "Scene",
            "label": "Asphalt ground at night",
            "confidence": "HIGH",
            "details": "Ground-level photo of asphalt parking lot surface, illuminated by flashlight. Evidence marker visible.",
            "evidence_index": 2
        }
    ]
}

CASE_25_8842_SYNTHESIS = {
    "discrepancies": [
        {
            "timestamp_ref": "23:48",
            "clean_claim": "Suspect produced a metallic object with a roughly 4-inch blade from his waistband",
            "visual_fact": "CCTV footage clearly shows suspect pulling a silver iPhone from his waistband with the screen illuminated",
            "description": "CRITICAL DISCREPANCY: Officer's report describes a knife with 4-inch blade, but video evidence shows the object was a smartphone (iPhone) with lit screen, not a weapon.",
            "status": "FLAGGED"
        },
        {
            "timestamp_ref": "23:48",
            "clean_claim": "Suspect raised the object above his head in a stabbing motion and lunged toward officer",
            "visual_fact": "Video shows suspect holding illuminated phone, motion inconsistent with stabbing gesture",
            "description": "DISCREPANCY: Officer describes aggressive stabbing motion, but visual evidence shows suspect holding a lit phone screen - not consistent with threatening knife attack posture.",
            "status": "FLAGGED"
        },
        {
            "timestamp_ref": "23:50",
            "clean_claim": "Metallic object was recovered from pavement (logged as evidence item #1)",
            "visual_fact": "Evidence photo shows a silver smartphone with cracked screen lying on pavement next to evidence marker #1",
            "description": "CRITICAL DISCREPANCY: The 'metallic object' recovered and photographed is clearly a cracked smartphone, not a knife or bladed weapon as described in the report.",
            "status": "FLAGGED"
        }
    ]
}

# Sample cases configuration
SAMPLE_CASES = [
    {
        "source_dir": "10",  # Directory name under data/cases/
        "title": "Bar Disturbance - Case #25-8842",
        "description": "A disturbance outside a bar where the officer claims the suspect pulled a knife. Visual evidence from body camera and CCTV footage shows potential discrepancies - the object appears to be a phone, not a weapon.",
        # Pre-computed analysis results
        "narrative_analysis": CASE_25_8842_NARRATIVE,
        "vision_analysis": CASE_25_8842_VISION,
        "synthesis_analysis": CASE_25_8842_SYNTHESIS,
    },
]


async def seed_sample_cases():
    """Seed sample cases from existing case directories."""
    
    # Create database connection
    database_url = (
        f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@"
        f"{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )
    
    engine = create_async_engine(database_url, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    print("\n" + "=" * 60)
    print("SAMPLE CASE SEEDER")
    print("=" * 60 + "\n")
    
    async with async_session() as session:
        for case_config in SAMPLE_CASES:
            source_dir = case_config["source_dir"]
            case_path = os.path.join(settings.STORAGE_DIR, "cases", source_dir)
            
            print(f"Processing: {case_config['title']}")
            print(f"  Source: {case_path}")
            
            if not os.path.exists(case_path):
                print(f"  ERROR: Directory not found: {case_path}")
                continue
            
            # Check if sample case with this title already exists
            existing_result = await session.execute(
                select(Case).where(
                    Case.title == case_config["title"],
                    Case.is_sample_case == True
                )
            )
            existing_case = existing_result.scalar_one_or_none()
            
            if existing_case:
                # Update existing case with new analysis data
                print(f"  UPDATING: Sample case exists, updating analysis results...")
                existing_case.narrative_analysis_json = json.dumps(case_config.get("narrative_analysis", {}))
                existing_case.vision_analysis_json = json.dumps(case_config.get("vision_analysis", {}))
                existing_case.synthesis_analysis_json = json.dumps(case_config.get("synthesis_analysis", {}))
                existing_case.analysis_status = "COMPLETED"
                await session.commit()
                print(f"  SUCCESS: Updated case with pre-computed analysis\n")
                continue
            
            # Find evidence files
            evidence_dir = os.path.join(case_path, "evidence")
            evidence_files = []
            thumbnail_path = None
            
            if os.path.exists(evidence_dir):
                for filename in sorted(os.listdir(evidence_dir)):  # Sort for consistent ordering
                    filepath = os.path.join(evidence_dir, filename)
                    if os.path.isfile(filepath):
                        ext = os.path.splitext(filename)[1].lower()
                        if ext in ['.png', '.jpg', '.jpeg', '.webp', '.gif']:
                            evidence_files.append(filepath)
                            if thumbnail_path is None:
                                thumbnail_path = filepath
            
            # Find report files
            reports_dir = os.path.join(case_path, "reports")
            report_files = []
            
            if os.path.exists(reports_dir):
                for filename in os.listdir(reports_dir):
                    filepath = os.path.join(reports_dir, filename)
                    if os.path.isfile(filepath) and filename.endswith('.pdf'):
                        report_files.append(filepath)
            
            print(f"  Found: {len(evidence_files)} evidence files, {len(report_files)} reports")
            
            # Create the case with pre-computed analysis
            new_case = Case(
                title=case_config["title"],
                description=case_config["description"],
                status="OPEN",
                analysis_status="COMPLETED",  # Already analyzed
                is_sample_case=True,
                thumbnail_path=thumbnail_path,
                # Pre-computed analysis results
                narrative_analysis_json=json.dumps(case_config.get("narrative_analysis", {})),
                vision_analysis_json=json.dumps(case_config.get("vision_analysis", {})),
                synthesis_analysis_json=json.dumps(case_config.get("synthesis_analysis", {}))
            )
            session.add(new_case)
            await session.flush()  # Get the case ID
            
            case_id = new_case.id
            print(f"  Created case ID: {case_id}")
            
            # Add evidence records
            for filepath in evidence_files:
                evidence = Evidence(
                    case_id=case_id,
                    file_path=filepath,
                    type=EvidenceType.IMAGE
                )
                session.add(evidence)
            
            # Add report records
            for filepath in report_files:
                report = Report(
                    case_id=case_id,
                    file_path=filepath
                )
                session.add(report)
            
            await session.commit()
            print(f"  SUCCESS: Sample case created with {len(evidence_files)} evidence, {len(report_files)} reports, and pre-computed analysis\n")
    
    await engine.dispose()
    print("\n" + "=" * 60)
    print("SEEDING COMPLETE")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(seed_sample_cases())

