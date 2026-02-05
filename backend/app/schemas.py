from pydantic import BaseModel, ConfigDict
from enum import Enum
from typing import List, Optional
from datetime import datetime

class EvidenceType(str, Enum):
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    AUDIO = "AUDIO"

class DiscrepancyStatus(str, Enum):
    FLAGGED = "FLAGGED"
    REVIEWED = "REVIEWED"
    DISMISSED = "DISMISSED"

# --- Discrepancy Schemas ---
class DiscrepancyBase(BaseModel):
    clean_claim: str
    visual_fact: str
    description: Optional[str] = None
    status: DiscrepancyStatus = DiscrepancyStatus.FLAGGED

class DiscrepancyCreate(DiscrepancyBase):
    pass

class Discrepancy(DiscrepancyBase):
    id: int
    case_id: int
    evidence_id: Optional[int] = None
    report_id: Optional[int] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# --- Evidence Schemas ---
class EvidenceBase(BaseModel):
    type: EvidenceType
    metadata_json: Optional[str] = None

class EvidenceCreate(EvidenceBase):
    pass

class Evidence(EvidenceBase):
    id: int
    case_id: int
    file_path: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# --- Report Schemas ---
class ReportBase(BaseModel):
    pass

class Report(ReportBase):
    id: int
    case_id: int
    file_path: str
    narrative_text: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# --- Case Schemas ---
class CaseBase(BaseModel):
    title: str
    description: Optional[str] = None

class CaseCreate(CaseBase):
    pass

class Case(CaseBase):
    id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    analysis_status: str = "PENDING"
    narrative_analysis_json: Optional[str] = None
    vision_analysis_json: Optional[str] = None
    synthesis_analysis_json: Optional[str] = None
    is_sample_case: bool = False
    thumbnail_path: Optional[str] = None
    evidence: List[Evidence] = []
    reports: List[Report] = []
    discrepancies: List[Discrepancy] = []

    model_config = ConfigDict(from_attributes=True)

class CaseListItem(BaseModel):
    """Schema for listing cases with counts instead of full nested objects"""
    id: int
    title: str
    description: Optional[str] = None
    status: str
    analysis_status: str = "PENDING"
    created_at: datetime
    updated_at: Optional[datetime] = None
    evidence_count: int = 0
    report_count: int = 0
    is_sample_case: bool = False
    thumbnail_path: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

# --- Agent Analysis Schemas ---

class VisionObservation(BaseModel):
    timestamp_ref: str
    category: str
    entity: str
    label: str
    confidence: str # LOW, MEDIUM, HIGH
    details: Optional[str] = None
    evidence_id: Optional[int] = None  # Which evidence this observation came from
    evidence_index: Optional[int] = None  # 1-based index for display

class VisionAnalysisResult(BaseModel):
    observations: List[VisionObservation]

class NarrativeClaim(BaseModel):
    timestamp_ref: Optional[str] = None
    entity: str
    action: str
    object: Optional[str] = None
    certainty: str # EXPLICIT, IMPLIED
    description: str

class NarrativeAnalysisResult(BaseModel):
    timeline: List[NarrativeClaim]

# --- Synthesis/Discrepancy Detection Schemas ---

class SynthesisDiscrepancy(BaseModel):
    timestamp_ref: Optional[str] = None
    clean_claim: str  # What the report says
    visual_fact: str  # What the evidence shows
    description: str  # Explanation of the discrepancy
    status: str = "FLAGGED"

class SynthesisAnalysisResult(BaseModel):
    discrepancies: List[SynthesisDiscrepancy]
