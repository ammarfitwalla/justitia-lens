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
    evidence: List[Evidence] = []
    reports: List[Report] = []
    discrepancies: List[Discrepancy] = []

    model_config = ConfigDict(from_attributes=True)

# --- Agent Analysis Schemas ---

class VisionObservation(BaseModel):
    timestamp_ref: str
    category: str
    entity: str
    label: str
    confidence: str # LOW, MEDIUM, HIGH
    details: Optional[str] = None

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

