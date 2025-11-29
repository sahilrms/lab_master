"""
Main FastAPI application for Lab Master API.

Features:
- Async PostgreSQL + SQLAlchemy
- FastAPI Users (JWT authentication)
- Auto-create database tables
- CORS enabled
"""

# -----------------------------------------------------------
# Imports
# -----------------------------------------------------------
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, status, Path
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.core.config import settings
from app.core.security import (
    get_user_manager, 
    auth_backend, 
    fastapi_users,
    current_active_user,
    require_admin,
    get_current_receptionist,
    get_current_technician
)
from app.db.base import Base, engine, get_async_session
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.models.test import Test, Sample
from app.api.endpoints.tests import router as test_router
from app.api.endpoints.test_types import router as test_types_router


# -----------------------------------------------------------
# Lifespan: Auto-create Database Tables
# -----------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


# -----------------------------------------------------------
# Initialize FastAPI App
# -----------------------------------------------------------
app = FastAPI(
    title="Lab Master API",
    description="Lab Management System",
    version="1.0.0",
    lifespan=lifespan,
)


# -----------------------------------------------------------
# CORS Middleware
# -----------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------------------------
# Authentication Routes (JWT + Register + Verify)
# -----------------------------------------------------------
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)

# Include test management endpoints
app.include_router(
    test_router,
    prefix="/api/v1",
    tags=["tests"],
)

# Include test types endpoints
app.include_router(
    test_types_router,
    prefix="/api/v1/test-types",
    tags=["test-types"]
)
# -----------------------------------------------------------
# User Profile Routes
# -----------------------------------------------------------
@app.get("/users/me", response_model=UserRead, tags=["users"])
async def read_own_profile(user=Depends(current_active_user)):
    return user


@app.patch("/users/me", response_model=UserRead, tags=["users"])
async def update_own_profile(
    user_update: UserUpdate,
    user=Depends(current_active_user),
    user_manager=Depends(get_user_manager),
):
    updated_user = await user_manager.update(
        user_update.create_update_dict(),
        user,
    )
    return updated_user


# -----------------------------------------------------------
# Admin Route: List Users
# -----------------------------------------------------------
@app.get("/admin/users", response_model=list[UserRead], tags=["admin"])
async def admin_list_users(
    skip: int = 0,
    limit: int = 100,
    session=Depends(get_async_session),
    _: User = Depends(require_admin),
):
    result = await session.execute(
        select(User).offset(skip).limit(limit)
    )
    return result.scalars().all()


# -----------------------------------------------------------
# Admin Route: Change User Role
# -----------------------------------------------------------
@app.patch("/admin/users/{user_id}/role", response_model=UserRead, tags=["admin"])
async def admin_change_user_role(
    user_id: int = Path(..., description="Target user ID"),
    new_role: UserRole = UserRole.PATIENT,
    user_manager=Depends(get_user_manager),
    _: User = Depends(require_admin),
):
    user = await user_manager.user_db.get(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await user_manager.user_db.update(user, {"role": new_role})
    user.role = new_role
    return user


# -----------------------------------------------------------
# Root Endpoint
# -----------------------------------------------------------
@app.get("/", tags=["root"])
async def root():
    return {"message": "Welcome to Lab Master API"}
