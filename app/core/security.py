# Handles authentication setup and user management logic
# This file configures JWT authentication, user manager, and DB dependencies for FastAPI-Users.
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi_users import BaseUserManager, IntegerIDMixin
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_users import FastAPIUsers

from app.core.config import settings
from app.models.user import User, UserRole  # Import User model and UserRole
from app.db.base import get_async_session

SECRET = settings.SECRET_KEY

# JWT Authentication
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)

async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/jwt/login")

# Initialize FastAPIUsers
fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend])

# Get the current active user
current_active_user = fastapi_users.current_user(active=True)

async def get_current_active_user(user = Depends(current_active_user)):
    """Dependency to get the current active user"""
    return user

# Role-based access control dependencies
async def require_admin(user: User = Depends(get_current_active_user)):
    """Dependency to require admin role"""
    if user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

async def get_current_receptionist(user: User = Depends(get_current_active_user)):
    """Dependency to require receptionist or admin role"""
    if user.role not in [UserRole.RECEPTIONIST, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Receptionist or Admin access required"
        )
    return user

async def get_current_technician(user: User = Depends(get_current_active_user)):
    """Dependency to require lab technician or admin role"""
    if user.role not in [UserRole.LAB_TECHNICIAN, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Lab technician or Admin access required"
        )
    return user