from pydantic import BaseModel, EmailStr
from pydantic import ConfigDict
from typing import Optional
from app.models.user import UserRole


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
    role: UserRole = UserRole.PATIENT


class UserCreate(UserBase):
    password: str

    def create_update_dict(self):
        return self.model_dump()


class UserUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    is_verified: Optional[bool] = None
    role: Optional[UserRole] = None

    def create_update_dict(self):
        return self.model_dump(exclude_unset=True)


class UserRead(UserBase):
    id: int
