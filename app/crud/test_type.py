from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from app.models.test_type import TestTypeConfig
from app.schemas.test_type import TestTypeCreate, TestTypeUpdate, SAMPLE_TEST_TYPES

async def get_test_type(db: Session, test_type_id: int) -> Optional[TestTypeConfig]:
    """Get a single test type by ID."""
    return await db.get(TestTypeConfig, test_type_id)

async def get_test_type_by_code(db: Session, code: str) -> Optional[TestTypeConfig]:
    """Get a test type by its code."""
    return db.query(TestTypeConfig).filter(TestTypeConfig.code == code.upper()).first()

async def get_test_types(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    category: Optional[str] = None,
    is_active: Optional[bool] = None
) -> List[TestTypeConfig]:
    """Get a list of test types with optional filtering."""
    query = db.query(TestTypeConfig)
    
    if category:
        query = query.filter(TestTypeConfig.category == category)
    if is_active is not None:
        query = query.filter(TestTypeConfig.is_active == is_active)
        
    return query.offset(skip).limit(limit).all()

async def create_test_type(db: Session, test_type_in: TestTypeCreate) -> TestTypeConfig:
    """Create a new test type."""
    # Check if test type with this code already exists
    existing = await get_test_type_by_code(db, test_type_in.code)
    if existing:
        raise ValueError(f"Test type with code '{test_type_in.code}' already exists")
    
    # Create the test type
    db_test_type = TestTypeConfig(**test_type_in.dict())
    db.add(db_test_type)
    await db.commit()
    await db.refresh(db_test_type)
    return db_test_type

async def update_test_type(
    db: Session, 
    db_test_type: TestTypeConfig, 
    test_type_in: TestTypeUpdate
) -> TestTypeConfig:
    """Update an existing test type."""
    update_data = test_type_in.dict(exclude_unset=True)
    
    # Update fields
    for field, value in update_data.items():
        setattr(db_test_type, field, value)
    
    db.add(db_test_type)
    await db.commit()
    await db.refresh(db_test_type)
    return db_test_type

def delete_test_type(db: Session, test_type_id: int) -> bool:
    """Delete a test type."""
    # Check if there are any tests using this test type
    test_type = db.get(TestTypeConfig, test_type_id)
    if not test_type:
        return False
        
    if test_type.tests:
        raise ValueError("Cannot delete test type that has associated tests")
    
    db.delete(test_type)
    db.commit()
    return True

async def get_test_type_parameters(
    db: Session, 
    test_type_id: int
) -> List[Dict[str, Any]]:
    """Get the parameters for a specific test type."""
    test_type = await get_test_type(db, test_type_id)
    if not test_type:
        raise ValueError(f"Test type with ID {test_type_id} not found")
    
    return test_type.parameters or []

async def seed_test_types(db: Session) -> List[TestTypeConfig]:
    """Seed the database with sample test types."""
    created = []
    
    for test_type_data in SAMPLE_TEST_TYPES:
        # Check if test type with this code already exists
        existing = await get_test_type_by_code(db, test_type_data["code"])
        if existing:
            continue
            
        # Create the test type
        test_type_in = TestTypeCreate(**test_type_data)
        db_test_type = await create_test_type(db, test_type_in)
        created.append(db_test_type)
    
    return created
