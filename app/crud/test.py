from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
from app.models.test import Test, Sample, TestStatus
from app.schemas.test import TestCreate, TestUpdate, SampleCreate, SampleUpdate

def create_test(db: Session, test: TestCreate, ordered_by: int) -> Test:
    db_test = Test(
        patient_id=test.patient_id,
        test_type=test.test_type,
        ordered_by=ordered_by,
        notes=test.notes,
        status=TestStatus.PENDING
    )
    db.add(db_test)
    db.commit()
    db.refresh(db_test)
    
    # Create samples for the test
    for sample_type in test.sample_types:
        create_sample(db, SampleCreate(sample_type=sample_type, notes=test.notes), db_test.id)
    
    return db_test

def get_test(db: Session, test_id: int) -> Optional[Test]:
    return db.scalar(select(Test).where(Test.id == test_id))

def get_tests(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    patient_id: Optional[int] = None,
    status: Optional[TestStatus] = None
) -> List[Test]:
    query = select(Test)
    if patient_id:
        query = query.where(Test.patient_id == patient_id)
    if status:
        query = query.where(Test.status == status)
    
    query = query.offset(skip).limit(limit)
    result = db.execute(query)
    return result.scalars().all()

def update_test(db: Session, test_id: int, test_update: TestUpdate) -> Optional[Test]:
    db_test = get_test(db, test_id)
    if not db_test:
        return None
    
    update_data = test_update.model_dump(exclude_unset=True)
    
    # If test is being marked as completed, set completed_at
    if 'status' in update_data and update_data['status'] == TestStatus.COMPLETED:
        update_data['completed_at'] = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(db_test, field, value)
    
    db.commit()
    db.refresh(db_test)
    return db_test

def create_sample(db: Session, sample: SampleCreate, test_id: int) -> Sample:
    db_sample = Sample(
        test_id=test_id,
        sample_type=sample.sample_type,
        notes=sample.notes,
        status=TestStatus.PENDING
    )
    db.add(db_sample)
    db.commit()
    db.refresh(db_sample)
    return db_sample

def get_sample(db: Session, sample_id: int) -> Optional[Sample]:
    return db.scalar(select(Sample).where(Sample.id == sample_id))

def get_samples_by_test(db: Session, test_id: int) -> List[Sample]:
    result = db.execute(select(Sample).where(Sample.test_id == test_id))
    return result.scalars().all()

def update_sample(db: Session, sample_id: int, sample_update: SampleUpdate) -> Optional[Sample]:
    db_sample = get_sample(db, sample_id)
    if not db_sample:
        return None
    
    update_data = sample_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_sample, field, value)
    
    db.commit()
    db.refresh(db_sample)
    
    # If all samples are completed, update test status
    test_samples = get_samples_by_test(db, db_sample.test_id)
    if all(sample.status == TestStatus.COMPLETED for sample in test_samples):
        update_test(db, db_sample.test_id, TestUpdate(status=TestStatus.COMPLETED))
    
    return db_sample
