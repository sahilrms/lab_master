from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.base import get_async_session
from app.models.user import User, UserRole
from app.models.test import Test, Sample, TestStatus
from app.schemas.test import TestCreate, TestInDB, TestUpdate, SampleInDB, SampleUpdate, TestWithSamples, TestResult
from app.crud.test import create_test, get_test, get_tests, update_test, create_sample, get_sample, update_sample, get_samples_by_test
from app.core.security import (
    get_current_active_user,
    get_current_receptionist,
    get_current_technician
)

router = APIRouter()

# Test endpoints
@router.post("/tests/", response_model=TestInDB, status_code=status.HTTP_201_CREATED)
async def create_new_test(
    test: TestCreate,
    db: Session = Depends(get_async_session),
    current_user: User = Depends(get_current_receptionist)
):
    """
    Create a new test order (Receptionist only)
    """
    return await create_test(db, test, current_user.id)

@router.get("/tests/", response_model=List[TestInDB])
async def list_tests(
    skip: int = 0,
    limit: int = 100,
    patient_id: int = None,
    status: TestStatus = None,
    db: Session = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    List all tests with optional filtering (All authenticated users with different access levels)
    """
    # Non-admin users can only see their own tests or tests they ordered
    if current_user.role == UserRole.PATIENT:
        if patient_id and patient_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to view these tests")
        return await get_tests(db, skip=skip, limit=limit, patient_id=current_user.id, status=status)
    
    # Technicians can see all tests but filter by patient if needed
    if current_user.role == UserRole.LAB_TECHNICIAN:
        return await get_tests(db, skip=skip, limit=limit, patient_id=patient_id, status=status)
    
    # Receptionists and admins can see all tests
    return await get_tests(db, skip=skip, limit=limit, patient_id=patient_id, status=status)

@router.get("/tests/{test_id}", response_model=TestWithSamples)
async def read_test(
    test_id: int,
    db: Session = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific test with its samples
    """
    db_test = await get_test(db, test_id)
    if not db_test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    # Check permissions - Admin can view any test, patients can only view their own
    if current_user.role == UserRole.PATIENT and db_test.patient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this test")
    
    # Get samples for this test
    samples = await get_samples_by_test(db, test_id)
    test_data = TestWithSamples(**db_test.__dict__, samples=samples)
    return test_data

@router.patch("/tests/{test_id}", response_model=TestInDB)
async def update_test_status(
    test_id: int,
    test_update: TestUpdate,
    db: Session = Depends(get_async_session),
    current_user: User = Depends(get_current_technician)
):
    """
    Update test status or results (Technician only)
    """
    db_test = await update_test(db, test_id, test_update)
    if not db_test:
        raise HTTPException(status_code=404, detail="Test not found")
    return db_test

# Sample endpoints
@router.get("/samples/{sample_id}", response_model=SampleInDB)
async def read_sample(
    sample_id: int,
    db: Session = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific sample
    """
    db_sample = await get_sample(db, sample_id)
    if not db_sample:
        raise HTTPException(status_code=404, detail="Sample not found")
    
    # Check permissions - Admin can view any sample, patients can only view their own
    test = await get_test(db, db_sample.test_id)
    if current_user.role == UserRole.PATIENT and test.patient_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this sample")
    
    return db_sample

@router.patch("/samples/{sample_id}", response_model=SampleInDB)
async def update_sample_status(
    sample_id: int,
    sample_update: SampleUpdate,
    db: Session = Depends(get_async_session),
    current_user: User = Depends(get_current_technician)
):
    """
    Update sample status (Technician only)
    """
    db_sample = await update_sample(db, sample_id, sample_update)
    if not db_sample:
        raise HTTPException(status_code=404, detail="Sample not found")
    return db_sample

@router.post("/tests/{test_id}/result", response_model=TestInDB)
async def add_test_result(
    test_id: int,
    result: TestResult,
    db: Session = Depends(get_async_session),
    current_user: User = Depends(get_current_technician)
):
    """
    Add test results (Technician only)
    """
    test_update = TestUpdate(
        status=TestStatus.COMPLETED,
        result=result.result,
        completed_at=result.completed_at
    )
    return await update_test(db, test_id, test_update)
