# This file makes 'schemas' a Python package.

from .common import Message # Assuming common.py might be created later or exists
from .user import (
    UserBase,
    UserCreate,
    UserResponse,
    UserUpdate,
    UserUpdateAdmin,
    UserPasswordChange
)
from .auth import (
    TokenResponse,
    LoginRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    TokenData,
    RefreshTokenRequest
)

__all__ = [
    "Message", # For generic messages
    "UserBase",
    "UserCreate",
    "UserResponse",
    "UserUpdate",
    "UserUpdateAdmin",
    "UserPasswordChange",
    "TokenResponse",
    "LoginRequest",
    "PasswordResetRequest",
    "PasswordResetConfirm",
    "TokenData",
    "RefreshTokenRequest",
]
