from typing import Optional
from pydantic import EmailStr, validator
from sqlmodel import SQLModel

from app.core.security import is_password_strong

class TokenResponse(SQLModel):
    access_token: str
    refresh_token: Optional[str] = None # May not always be included in body (e.g. HttpOnly cookie)
    token_type: str = "bearer"

class LoginRequest(SQLModel):
    username: str # Could be email or username
    password: str

class PasswordResetRequest(SQLModel):
    email: EmailStr

class PasswordResetConfirm(SQLModel):
    token: str
    new_password: str

    @validator('new_password')
    def password_must_be_strong(cls, v: str) -> str:
        if not is_password_strong(v):
            raise ValueError(
                "Password must be at least 8 characters long and include "
                "an uppercase letter, a lowercase letter, a digit, "
                "and a special character."
            )
        return v

class TokenData(SQLModel):
    # 'sub' (subject) is the standard claim for user identifier in JWT
    sub: Optional[str] = None
    # You can add other fields you expect in your token payload, e.g., 'type' for refresh tokens

class RefreshTokenRequest(SQLModel):
    refresh_token: str
