from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import datetime

class UserBase(SQLModel):
    username: str = Field(unique=True, index=True)
    email: str = Field(unique=True, index=True)
    full_name: Optional[str] = None

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str

    # New fields for Phase 2
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    is_superuser: bool = Field(default=False)
    failed_login_attempts: int = Field(default=0)
    locked_until: Optional[datetime] = Field(default=None, nullable=True) # Ensure DB schema allows NULL
    last_login: Optional[datetime] = Field(default=None, nullable=True)    # Ensure DB schema allows NULL
    login_ip: Optional[str] = Field(default=None, nullable=True)          # Ensure DB schema allows NULL
    password_changed_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int

# Add other necessary User related Pydantic models here if needed for Phase 1
# For example UserUpdate etc.
