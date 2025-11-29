from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from enum import Enum
from app.models.test import TestStatus, TestType

class TestBase(BaseModel):
    patient_id: int
    test_type: TestType
    notes: Optional[str] = None

class TestCreate(TestBase):
    sample_types: List[str] = Field(..., description="List of sample types for this test")

class TestUpdate(BaseModel):
    status: Optional[TestStatus] = None
    result: Optional[str] = None
    notes: Optional[str] = None

class TestInDB(TestBase):
    id: int
    status: TestStatus
    ordered_by: int
    collected_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[str] = None

    class Config:
        from_attributes = True

class SampleBase(BaseModel):
    sample_type: str
    notes: Optional[str] = None

class SampleCreate(SampleBase):
    pass

class SampleUpdate(BaseModel):
    status: Optional[TestStatus] = None
    notes: Optional[str] = None

class SampleInDB(SampleBase):
    id: int
    test_id: int
    status: TestStatus
    collection_time: datetime

    class Config:
        from_attributes = True

class TestWithSamples(TestInDB):
    samples: List[SampleInDB] = []

class TestResult(BaseModel):
    result: str
    completed_at: datetime = Field(default_factory=datetime.now)
