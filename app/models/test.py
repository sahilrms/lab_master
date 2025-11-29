from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
import enum

class TestStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TestType(str, enum.Enum):
    BLOOD_TEST = "blood_test"
    URINE_TEST = "urine_test"
    XRAY = "xray"
    MRI = "mri"
    CT_SCAN = "ct_scan"
    ULTRASOUND = "ultrasound"
    STOOL_TEST = "stool_test"

class Test(Base):
    __tablename__ = "tests"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey('users.id'))
    test_type = Column(Enum(TestType), nullable=False)
    status = Column(Enum(TestStatus), default=TestStatus.PENDING)
    ordered_by = Column(Integer, ForeignKey('users.id'))
    collected_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(String, nullable=True)
    result = Column(String, nullable=True)
    
    # Relationships
    patient = relationship("User", foreign_keys=[patient_id])
    ordered_by_user = relationship("User", foreign_keys=[ordered_by])
    samples = relationship("Sample", back_populates="test")

class Sample(Base):
    __tablename__ = "samples"

    id = Column(Integer, primary_key=True, index=True)
    test_id = Column(Integer, ForeignKey('tests.id'))
    sample_type = Column(String, nullable=False)
    collection_time = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(Enum(TestStatus), default=TestStatus.PENDING)
    notes = Column(String, nullable=True)
    
    # Relationships
    test = relationship("Test", back_populates="samples")
