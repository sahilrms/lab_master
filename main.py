"""
Main FastAPI application for Lab Master API.
Includes:
- Async PostgreSQL connection (SQLAlchemy)
- FastAPI Users authentication (JWT)
- Auto-creation of DB tables on startup
- CORS support
"""

from contextlib import asynccontextmanager
import uuid

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# FastAPI Users package
from fastapi_users import FastAPIUsers

# Import your settings, models, schemas, and security modules
from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.core.security import get_user_manager, auth_backend
from app.db.base import Base, engine
import pydantic
print("PYDANTIC VERSION:", pydantic.VERSION)

# -----------------------------------------------------------
# Lifespan handler (replaces deprecated on_event("startup"))
# -----------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs when the application starts.
    - Creates all tables in the PostgreSQL database (async compatible)
    
    Runs again at shutdown.
    - You can add cleanup operations if needed.
    """
    # Create database tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield  # Pass control to the application

    # Cleanup (optional)
    pass


# -----------------------------------------------------------
# Initialize FastAPI App
# -----------------------------------------------------------
app = FastAPI(
    title="Lab Master API",
    description="Lab Management System",
    version="1.0.0",
    lifespan=lifespan,  # Attach lifespan handler
)


# -----------------------------------------------------------
# CORS Middleware
# Allows frontend apps (React, Next.js, etc.) to access the API
# -----------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change in production)
    allow_credentials=True,
    allow_methods=["*"],  # All HTTP methods allowed
    allow_headers=["*"],  # All headers allowed
)


# -----------------------------------------------------------
# FastAPI Users Setup
# -----------------------------------------------------------
# FastAPIUsers must know:
# - The User model
# - The type of the User ID (UUID in your case)
# - The user manager (handles DB logic)
# - The authentication backend (JWT auth)
fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,   # Dependency that returns UserManager instance
    [auth_backend]      # JWT backend (from your auth module)
)


# -----------------------------------------------------------
# Authentication Routes
# These will auto-generate:
# - /auth/jwt/login
# - /auth/jwt/logout
# - /auth/register
# - /auth/verify
# -----------------------------------------------------------

# Login / Logout route (JWT)
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)

# User Registration route
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

# Email Verification route (optional, but included)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)

# CRUD operations for users (admin-level actions)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)


# -----------------------------------------------------------
# Default Root Route
# Simple health-check endpoint
# -----------------------------------------------------------
@app.get("/")
async def root():
    """
    Root endpoint to verify the API is running.
    """
    return {"message": "Welcome to Lab Master API"}
