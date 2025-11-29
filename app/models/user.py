from sqlalchemy import Boolean, Column, Integer, String, Enum
from sqlalchemy.sql import func
from app.db.base import Base
import enum

# Add this enum for user roles
class UserRole(str, enum.Enum):
    ADMIN = "admin"
    LAB_TECHNICIAN = "lab_technician"
    RECEPTIONIST = "receptionist"
    PATIENT = "patient"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    role = Column(Enum(UserRole), default=UserRole.PATIENT, nullable=False)  # Add this line

    def __repr__(self):
        return f"<User {self.email}>"