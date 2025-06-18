from typing import Optional, Any
from datetime import datetime
from pydantic import validator, EmailStr
from sqlmodel import SQLModel # Used as a base for schema definitions as well

# Import UserBase from models to ensure consistency if desired,
# or redefine common fields here if schemas should be fully independent.
# For this task, we'll inherit from the SQLModel-based UserBase from models.
from app.models.user import UserBase as UserModelBase # Alias to avoid confusion
from app.core.security import is_password_strong

# Schema for base user properties (can be used for UserResponse as well)
# This UserBase schema is for data transfer, distinct from the UserBase model if fields differ.
# However, since UserBase model is simple and SQLModel-based, it can be reused.
class UserBase(SQLModel): # This is for schemas, can be same as model's UserBase
    username: str
    email: EmailStr # Use EmailStr for validation
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

    @validator('password')
    def password_must_be_strong(cls, v: str) -> str:
        if not is_password_strong(v):
            raise ValueError(
                "Password must be at least 8 characters long and include "
                "an uppercase letter, a lowercase letter, a digit, "
                "and a special character."
            )
        return v

class UserResponse(UserBase): # Inherits username, email, full_name
    id: int
    is_active: bool
    is_verified: bool
    is_superuser: bool
    last_login: Optional[datetime] = None
    login_ip: Optional[str] = None
    password_changed_at: datetime # Assuming this is always set on user creation/retrieval

# Schema for updating user information (by user themselves or admin)
class UserUpdate(SQLModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    # Add other fields that can be updated
    # For admin updates, a separate UserUpdateAdmin schema might be needed
    # to include fields like is_active, is_verified, is_superuser.

# Schema for admin to update user details (more privileged)
class UserUpdateAdmin(UserUpdate):
    username: Optional[str] = None # Admins might be able to change username
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_superuser: Optional[bool] = None

# Schema for changing password
class UserPasswordChange(SQLModel):
    current_password: str
    new_password: str

    @validator('new_password')
    def new_password_must_be_strong(cls, v: str) -> str:
        if not is_password_strong(v):
            raise ValueError(
                "Password must be at least 8 characters long and include "
                "an uppercase letter, a lowercase letter, a digit, "
                "and a special character."
            )
        return v
