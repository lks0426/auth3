from datetime import datetime, timedelta
from typing import Optional
import uuid # For UUID tokens

from sqlmodel import Field, SQLModel, Relationship # Relationship might be needed later

# Assuming a User model exists in .user for potential relationships
# from .user import User # Uncomment if direct relationships are added in this step

class RefreshTokenBase(SQLModel):
    user_id: int = Field(foreign_key="user.id") # Assuming user.id is an int
    token: str = Field(index=True, unique=True)
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    # revoked_at: Optional[datetime] = Field(default=None) # Consider if needed for blacklist tracking here

class RefreshToken(RefreshTokenBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # user: Optional["User"] = Relationship(back_populates="refresh_tokens") # Example relationship

class LoginHistoryBase(SQLModel):
    user_id: int = Field(foreign_key="user.id")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    success: bool

class LoginHistory(LoginHistoryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # user: Optional["User"] = Relationship(back_populates="login_history") # Example relationship

class PasswordResetTokenBase(SQLModel):
    user_id: int = Field(foreign_key="user.id")
    token: str = Field(default_factory=lambda: str(uuid.uuid4()), unique=True, index=True)
    expires_at: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(hours=1)) # Default 1 hour expiry
    created_at: datetime = Field(default_factory=datetime.utcnow)
    used_at: Optional[datetime] = Field(default=None, nullable=True)

class PasswordResetToken(PasswordResetTokenBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # user: Optional["User"] = Relationship(back_populates="password_reset_tokens") # Example relationship
