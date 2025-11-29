from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.base import get_async_session
from app.models.user import User, UserRole
from app.models.test_type import TestTypeConfig
from app.schemas.test_type import (
    TestTypeCreate, 
    TestTypeUpdate, 
    TestTypeInDB,
    SAMPLE_TEST_TYPES
)
from app.crud.test_type import (
    get_test_type,
    get_test_type_by_code,
    get_test_types as crud_get_test_types,
    create_test_type as crud_create_test_type,
    update_test_type as crud_update_test_type,
    delete_test_type as crud_delete_test_type,
    get_test_type_parameters,
    seed_test_types
)
from app.core.security import get_current_active_user, require_admin

router = APIRouter()

@router.get("/", response_model=List[TestTypeInDB])
async def get_test_types(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_async_session),
    _: User = Depends(get_current_active_user)
):
    """
    Get a list of test types with optional filtering.
    """
    return await crud_get_test_types(
        db, 
        skip=skip, 
        limit=limit, 
        category=category,
        is_active=is_active
    )

@router.get("/{test_type_id}", response_model=TestTypeInDB)
async def read_test_type(
    test_type_id: int,
    db: Session = Depends(get_async_session),
    _: User = Depends(get_current_active_user)
):
    """
    Get a specific test type by ID.
    """
    db_test_type = await get_test_type(db, test_type_id=test_type_id)
    if db_test_type is None:
        raise HTTPException(status_code=404, detail="Test type not found")
    return db_test_type

@router.get("/code/{test_type_code}", response_model=TestTypeInDB)
async def read_test_type_by_code(
    test_type_code: str,
    db: Session = Depends(get_async_session),
    _: User = Depends(get_current_active_user)
):
    """
    Get a specific test type by its code.
    """
    db_test_type = await get_test_type_by_code(db, code=test_type_code.upper())
    if db_test_type is None:
        raise HTTPException(status_code=404, detail="Test type not found")
    return db_test_type

@router.post("/", response_model=TestTypeInDB, status_code=status.HTTP_201_CREATED)
async def create_test_type(
    test_type_in: TestTypeCreate,
    db: Session = Depends(get_async_session),
    _: User = Depends(require_admin)
):
    """
    Create a new test type.
    """
    try:
        return await crud_create_test_type(db=db, test_type_in=test_type_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{test_type_id}", response_model=TestTypeInDB)
async def update_test_type(
    test_type_id: int,
    test_type_in: TestTypeUpdate,
    db: Session = Depends(get_async_session),
    _: User = Depends(require_admin)
):
    """
    Update a test type.
    """
    db_test_type = await get_test_type(db, test_type_id=test_type_id)
    if db_test_type is None:
        raise HTTPException(status_code=404, detail="Test type not found")
    
    try:
        return await crud_update_test_type(
            db=db, 
            db_test_type=db_test_type, 
            test_type_in=test_type_in
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{test_type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_test_type(
    test_type_id: int,
    db: Session = Depends(get_async_session),
    _: User = Depends(require_admin)
):
    """
    Delete a test type.
    """
    try:
        success = delete_test_type(db, test_type_id=test_type_id)
        if not success:
            raise HTTPException(status_code=404, detail="Test type not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{test_type_id}/parameters")
async def get_parameters_for_test_type(
    test_type_id: int,
    db: Session = Depends(get_async_session),
    _: User = Depends(get_current_active_user)
):
    """
    Get the parameters for a specific test type.
    """
    try:
        return await get_test_type_parameters(db, test_type_id=test_type_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/seed", status_code=status.HTTP_201_CREATED)
async def seed_sample_test_types(
    db: Session = Depends(get_async_session),
    _: User = Depends(require_admin)
):
    """
    Seed the database with sample test types.
    """
    try:
        created = await seed_test_types(db)
        return {"message": f"Successfully created {len(created)} test types"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error seeding test types: {str(e)}")

@router.get("/samples/list", response_model=List[dict])
async def list_sample_test_types():
    """
    Get a list of sample test types that can be created.
    This endpoint doesn't modify the database, just returns the sample data.
    """
    return SAMPLE_TEST_TYPES
