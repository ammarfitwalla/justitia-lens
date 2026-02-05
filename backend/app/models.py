from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class EvidenceType(str, enum.Enum):
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    AUDIO = "AUDIO"

class DiscrepancyStatus(str, enum.Enum):
    FLAGGED = "FLAGGED"
    REVIEWED = "REVIEWED"
    DISMISSED = "DISMISSED"

class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text, nullable=True)
    status = Column(String, default="OPEN")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Analysis cache fields
    narrative_analysis_json = Column(Text, nullable=True)  # Cached narrative agent result
    vision_analysis_json = Column(Text, nullable=True)     # Cached vision agent result
    synthesis_analysis_json = Column(Text, nullable=True)  # Cached discrepancy detection result
    analysis_status = Column(String, default="PENDING")    # PENDING, IN_PROGRESS, COMPLETED
    
    # Sample case fields
    is_sample_case = Column(Boolean, default=False)  # True for pre-loaded sample cases
    thumbnail_path = Column(String, nullable=True)   # Path to thumbnail image for display

    evidence = relationship("Evidence", back_populates="case", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="case", cascade="all, delete-orphan")
    discrepancies = relationship("Discrepancy", back_populates="case", cascade="all, delete-orphan")

class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    file_path = Column(String, nullable=False)
    file_hash = Column(String, nullable=True)
    type = Column(Enum(EvidenceType), default=EvidenceType.IMAGE)
    metadata_json = Column(Text, nullable=True) # JSON string for generic metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    case = relationship("Case", back_populates="evidence")
    discrepancies = relationship("Discrepancy", back_populates="evidence")

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    file_path = Column(String, nullable=False)
    narrative_text = Column(Text, nullable=True) # Extracted text
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    case = relationship("Case", back_populates="reports")

class Discrepancy(Base):
    __tablename__ = "discrepancies"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    evidence_id = Column(Integer, ForeignKey("evidence.id"), nullable=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=True)
    
    clean_claim = Column(Text, nullable=False) # "Suspect held knife"
    visual_fact = Column(Text, nullable=False) # "Suspect held phone"
    description = Column(Text, nullable=True) # "Object mismatch"
    status = Column(Enum(DiscrepancyStatus), default=DiscrepancyStatus.FLAGGED)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    case = relationship("Case", back_populates="discrepancies")
    evidence = relationship("Evidence", back_populates="discrepancies")
    # report relation could be added effectively
