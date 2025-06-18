from typing import Annotated, Any
from datetime import timedelta


from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlmodel.ext.asyncio.session import AsyncSession

from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import TokenResponse, PasswordResetRequest, PasswordResetConfirm
from app.schemas.common import Message
from app.services.auth_service import AuthService
from app.crud import user as crud_user # For get_current_user
from app.models.user import User as UserModel # For type hinting User model
from app.config import Settings, get_settings
from app.dependencies import get_db, CurrentSettings, ActiveSession
from app.core.security import decode_token, JWTError # decode_token was updated in security.py

router = APIRouter(prefix="/auth", tags=["authentication"])

# This scheme should point to the login URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
# Note: tokenUrl should match the actual login endpoint path if prefix is used in main.py

# Dependency to get the current user from JWT token
async def get_current_user(
    db: ActiveSession, # Use ActiveSession from dependencies
    token: Annotated[str, Depends(oauth2_scheme)],
    settings_obj: CurrentSettings # Use CurrentSettings from dependencies
) -> UserModel:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = await decode_token(token) # decode_token made async in security.py
    if payload is None or payload.get("sub") is None:
        raise credentials_exception

    user_id = payload.get("sub")
    user = await crud_user.get_user(db, user_id=int(user_id)) # crud_user.get_user is now async
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return user

CurrentUser = Annotated[UserModel, Depends(get_current_user)]


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_new_user(
    user_in: UserCreate,
    db: ActiveSession,
    settings_obj: CurrentSettings,
    auth_service: AuthService = Depends() # AuthService can be a dependency itself
):
    # If AuthService methods are static or class methods not needing instance state:
    # user = await AuthService.register_user(db=db, user_in=user_in, settings=settings_obj)
    # For this example, assuming AuthService can be instantiated or its methods are static/classmethod
    # Or, make AuthService methods take `self` and instantiate it: auth_service = AuthService()
    service = AuthService()
    user = await service.register_user(db=db, user_in=user_in, settings=settings_obj)
    return user

@router.post("/login", response_model=TokenResponse)
async def login_for_access_token(
    response: Response, # To set HttpOnly cookie
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: ActiveSession,
    settings_obj: CurrentSettings,
    request: Request # To get login IP
):
    # For login_ip, it's better to trust X-Forwarded-For if behind a proxy
    login_ip = request.client.host if request.client else "unknown"

    service = AuthService()
    user = await service.authenticate_user(
        db=db, username=form_data.username, password=form_data.password, login_ip=login_ip, settings=settings_obj
    )
    if not user: # Should be handled by exceptions in authenticate_user, but as a safeguard
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    tokens = await service.create_tokens(db=db, user=user, settings=settings_obj)

    # Set refresh token in HttpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        max_age=settings_obj.REFRESH_TOKEN_EXPIRE_MINUTES * 60, # in seconds
        expires=settings_obj.REFRESH_TOKEN_EXPIRE_MINUTES * 60, # for older browsers
        path="/api/v1/auth", # Path where this cookie is valid
        samesite="lax", # Consider "strict" if applicable
        secure=not settings_obj.DEBUG,  # True in production (HTTPS)
    )
    return {"access_token": tokens["access_token"], "token_type": tokens["token_type"]}


@router.post("/logout", response_model=Message)
async def logout(
    response: Response, # To clear cookie
    request: Request, # To get current tokens if needed (e.g. from cookies)
    db: ActiveSession,
    settings_obj: CurrentSettings,
    current_user: CurrentUser, # Ensures user is authenticated
    token: Annotated[str, Depends(oauth2_scheme)] # The access token used for auth
):
    refresh_token_from_cookie = request.cookies.get("refresh_token")
    service = AuthService()
    await service.logout_user(
        db=db, user=current_user, token=token, refresh_token_str=refresh_token_from_cookie, settings=settings_obj
    )
    response.delete_cookie(key="refresh_token", path="/api/v1/auth")
    return {"message": "Successfully logged out"}

@router.post("/refresh", response_model=TokenResponse)
async def refresh_access(
    request: Request, # To get refresh_token from cookie
    db: ActiveSession,
    settings_obj: CurrentSettings
):
    refresh_token_str = request.cookies.get("refresh_token")
    if not refresh_token_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found in cookies"
        )
    service = AuthService()
    new_tokens = await service.refresh_access_token(db=db, refresh_token_str=refresh_token_str, settings=settings_obj)
    # If token rotation is implemented and a new refresh token is issued, update the cookie here.
    return new_tokens


@router.post("/forgot-password", response_model=Message)
async def request_password_reset_email(
    password_reset_request: PasswordResetRequest,
    db: ActiveSession,
    settings_obj: CurrentSettings
):
    service = AuthService()
    await service.request_password_reset(db=db, email=password_reset_request.email, settings=settings_obj)
    return {"message": "If an account with that email exists, a password reset link has been sent."}

@router.post("/reset-password", response_model=Message)
async def reset_user_password(
    password_reset_confirm: PasswordResetConfirm,
    db: ActiveSession,
    settings_obj: CurrentSettings
):
    service = AuthService()
    success = await service.reset_password(
        db=db, token=password_reset_confirm.token, new_password=password_reset_confirm.new_password, settings=settings_obj
    )
    if not success: # Should be handled by exceptions in reset_password
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset failed. Invalid or expired token."
        )
    return {"message": "Password has been reset successfully."}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: CurrentUser):
    # current_user is already a UserModel instance from get_current_user
    # UserResponse will automatically map fields.
    return current_user
