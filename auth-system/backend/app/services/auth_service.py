from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import uuid # For password reset token generation if not using JWT for it

from fastapi import HTTPException, status
from sqlmodel import Session

from app.models.user import User
from app.models.auth import RefreshToken, PasswordResetToken # LoginHistory is used by CRUD directly
from app.schemas.user import UserCreate # For type hinting input
from app.schemas.auth import TokenData # For type hinting decoded token payload
from app.config import Settings # To access settings like expiry times, secret key etc.

from app.core import security # security functions
from app.services import email_service # email sending functions
from app.crud import user as crud_user
from app.crud import auth as crud_auth


class AuthService:
    async def register_user(self, db: Session, *, user_in: UserCreate, settings: Settings) -> User:
        existing_user_by_email = crud_user.get_user_by_email(db, email=user_in.email)
        if existing_user_by_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists.",
            )
        existing_user_by_username = crud_user.get_user_by_username(db, username=user_in.username)
        if existing_user_by_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this username already exists.",
            )

        user = crud_user.create_user(db=db, user_in=user_in)

        # Send verification email (if EMAILS_ENABLED)
        # This part can be conditional based on settings.EMAIL_VERIFICATION_REQUIRED
        # For now, let's assume we send it if emails are generally enabled.
        if settings.EMAILS_ENABLED:
            # Generate a verification token (e.g., a short-lived JWT or a simple UUID token)
            # Storing this token and associating with user might be needed if not using self-contained JWT
            # For simplicity, let's assume a JWT-like token for verification for now.
            # This token would be different from password reset.
            # verification_jwt = security.create_access_token(
            #     data={"sub": user.email, "type": "email_verification"}, # Or user.id
            #     expires_delta=timedelta(hours=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS)
            # )
            # await email_service.send_registration_verification_email(
            #     email_to=user.email, username=user.username, verification_token=verification_jwt
            # )
            pass # Placeholder for email verification flow as it's not detailed for this method in prompt

        return user

    async def authenticate_user(
        self, db: Session, *, username: str, password: str, login_ip: str, settings: Settings
    ) -> User:
        user = crud_user.get_user_by_username(db, username=username)
        if not user: # Try by email if username fails
            user = crud_user.get_user_by_email(db, email=username)

        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

        if user.locked_until and user.locked_until > datetime.now(timezone.utc):
            lockout_time_left = user.locked_until - datetime.now(timezone.utc)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Account locked. Try again in {int(lockout_time_left.total_seconds() / 60)} minutes.",
            )

        if not security.verify_password(password, user.hashed_password):
            crud_user.increment_failed_login_attempts(db=db, user=user)
            if user.failed_login_attempts >= settings.MAX_FAILED_LOGIN_ATTEMPTS:
                lock_duration = timedelta(minutes=settings.ACCOUNT_LOCKOUT_MINUTES)
                lock_until_time = datetime.now(timezone.utc) + lock_duration
                crud_user.lock_user_account(db=db, user=user, until=lock_until_time)
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Account locked due to too many failed login attempts. Try again in {settings.ACCOUNT_LOCKOUT_MINUTES} minutes.",
                )
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

        # If password is correct, update login info and reset failed attempts
        user = crud_user.update_login_info(db=db, user=user, login_ip=login_ip)
        return user

    async def create_tokens(self, db: Session, *, user: User, settings: Settings) -> Dict[str, Any]:
        access_token = security.create_access_token(
            subject=user.id, expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        refresh_token_expires = datetime.now(timezone.utc) + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        refresh_token_str = security.create_refresh_token(
            subject=user.id, expires_delta=timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        )

        crud_auth.create_refresh_token(
            db=db, user_id=user.id, token=refresh_token_str, expires_at=refresh_token_expires
        )

        return {"access_token": access_token, "refresh_token": refresh_token_str, "token_type": "bearer"}

    async def refresh_access_token(self, db: Session, *, refresh_token_str: str, settings: Settings) -> Dict[str, str]:
        payload = await security.decode_token(refresh_token_str)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token payload")

        if await security.is_token_blacklisted(refresh_token_str):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token blacklisted")

        db_refresh_token = crud_auth.get_refresh_token_by_token(db=db, token=refresh_token_str)
        if not db_refresh_token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token not found or revoked")

        if db_refresh_token.user_id != int(user_id):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token user mismatch")

        if db_refresh_token.expires_at < datetime.now(timezone.utc):
            # Optionally delete expired token
            crud_auth.delete_refresh_token(db=db, db_obj=db_refresh_token)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")

        user = crud_user.get_user(db=db, user_id=int(user_id))
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

        # Optional: Token Rotation - Blacklist old, issue new refresh token
        # await security.add_token_to_blacklist(refresh_token_str, timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES))
        # crud_auth.delete_refresh_token(db=db, db_obj=db_refresh_token)
        # new_tokens = await self.create_tokens(db=db, user=user, settings=settings)
        # return new_tokens

        # For now, just issue a new access token
        new_access_token = security.create_access_token(
            subject=user.id, expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        return {"access_token": new_access_token, "token_type": "bearer"}


    async def logout_user(
        self, db: Session, *, token: str, refresh_token_str: Optional[str], settings: Settings
    ) -> bool:
        # Blacklist access token
        # Expiry for blacklist should match original token's remaining validity ideally.
        # Decoding to get 'exp' is more accurate, but for simplicity using configured expiry.
        access_token_expiry_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        await security.add_token_to_blacklist(token, expires_in=access_token_expiry_delta)

        if refresh_token_str:
            db_refresh_token = crud_auth.get_refresh_token_by_token(db=db, token=refresh_token_str)
            if db_refresh_token:
                # Blacklist the refresh token in Redis
                refresh_token_actual_expires_at = db_refresh_token.expires_at
                remaining_validity = refresh_token_actual_expires_at - datetime.now(timezone.utc)
                if remaining_validity.total_seconds() > 0:
                    await security.add_token_to_blacklist(refresh_token_str, expires_in=remaining_validity)
                # Delete from DB
                crud_auth.delete_refresh_token(db=db, db_obj=db_refresh_token)
        return True

    async def request_password_reset(self, db: Session, *, email: str, settings: Settings) -> bool:
        user = crud_user.get_user_by_email(db=db, email=email)
        if not user or not user.is_active:
            # Do not reveal if user exists or not for security, just log and return as if sent
            print(f"Password reset request for non-existent or inactive user: {email}")
            return True # Pretend it was successful

        # Token is generated by PasswordResetToken model's default_factory
        expires_delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
        expires_at = datetime.now(timezone.utc) + expires_delta

        # Create a new token (model will generate the token string)
        # We need the actual token string to send in email, so let model generate it first then retrieve
        temp_token_obj = PasswordResetToken(user_id=user.id, expires_at=expires_at) # token field gets default

        created_db_token = crud_auth.create_password_reset_token(
            db=db, user_id=user.id, token=temp_token_obj.token, expires_at=expires_at
        )

        if settings.EMAILS_ENABLED:
            await email_service.send_password_reset_email(
                email_to=user.email, username=user.username, reset_token=created_db_token.token
            )
        else:
            print(f"Password reset token for {email} (user: {user.username}): {created_db_token.token}")

        return True

    async def reset_password(self, db: Session, *, token: str, new_password: str, settings: Settings) -> bool:
        db_token = crud_auth.get_password_reset_token_by_token(db=db, token=token)

        if not db_token:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired password reset token.")

        if db_token.expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password reset token expired.")

        if db_token.used_at is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password reset token already used.")

        user = crud_user.get_user(db=db, user_id=db_token.user_id)
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found or inactive.")

        crud_user.update_password(db=db, db_obj=user, new_password=new_password)
        crud_auth.mark_password_reset_token_as_used(db=db, db_obj=db_token)

        if settings.EMAILS_ENABLED:
            await email_service.send_password_change_notification_email(email_to=user.email, username=user.username)

        return True
