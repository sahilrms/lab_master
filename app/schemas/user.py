# User schemas for data validation and serialization
from pydantic import BaseModel, EmailStr
from pydantic import ConfigDict
from typing import Optional
from app.models.user import UserRole

# Base schema with common user fields
class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # Allow creation from ORM objects

    email: EmailStr  # User's email address
    is_active: bool = True  # Is the user account active?
    is_superuser: bool = False  # Does the user have admin privileges?
    is_verified: bool = False  # Has the user verified their email?
    role: UserRole = UserRole.PATIENT  # User's role in the system

# Schema for user registration
class UserCreate(UserBase):
    password: str  # Password for new user

    def create_update_dict(self):
        # Used internally by FastAPI-Users for DB operations
        return self.model_dump()

# Schema for updating user info (all fields optional)
class UserUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: Optional[EmailStr] = None  # Optional new email
    password: Optional[str] = None  # Optional new password
    is_active: Optional[bool] = None  # Optional active status
    is_superuser: Optional[bool] = None  # Optional admin status
    is_verified: Optional[bool] = None  # Optional verification status
    role: Optional[UserRole] = None  # Optional new role

    def create_update_dict(self):
        # Used internally by FastAPI-Users for DB operations
        return self.model_dump(exclude_unset=True)

# Schema for reading user info (API responses)
class UserRead(UserBase):
    id: int  # User's unique database ID
