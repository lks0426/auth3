from typing import Optional
from datetime import datetime, timezone # Ensure timezone is imported

from sqlmodel import select, delete
from sqlmodel.ext.asyncio.session import AsyncSession # Use AsyncSession
from app.models.auth import RefreshToken, LoginHistory, PasswordResetToken

# --- RefreshToken CRUD ---

async def create_refresh_token(
    db: AsyncSession, *, user_id: int, token: str, expires_at: datetime
) -> RefreshToken:
    db_refresh_token = RefreshToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    db.add(db_refresh_token)
    await db.commit()
    await db.refresh(db_refresh_token)
    return db_refresh_token

async def get_refresh_token_by_token(db: AsyncSession, *, token: str) -> Optional[RefreshToken]:
    statement = select(RefreshToken).where(RefreshToken.token == token)
    result = await db.exec(statement)
    return result.first()

async def delete_refresh_token(db: AsyncSession, *, db_obj: RefreshToken) -> RefreshToken:
    # Mark for deletion
    await db.delete(db_obj) # Changed from db.delete(db_obj) to await db.delete(db_obj) if using newer SQLModel/SQLAlchemy
                               # However, SQLModel's AsyncSession.delete is not awaitable.
                               # Standard practice is db.delete(synchronous), then await db.commit().
    db.delete(db_obj) # This is synchronous
    await db.commit()
    return db_obj # Object is unusable after commit if delete cascade/etc.

async def delete_all_refresh_tokens_for_user(db: AsyncSession, *, user_id: int) -> int:
    statement = delete(RefreshToken).where(RefreshToken.user_id == user_id)
    results = await db.exec(statement)
    await db.commit()
    return results.rowcount


# --- LoginHistory CRUD ---

async def create_login_history(
    db: AsyncSession,
    *,
    user_id: int,
    success: bool,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> LoginHistory:
    db_login_history = LoginHistory(
        user_id=user_id,
        success=success,
        ip_address=ip_address,
        user_agent=user_agent
    )
    db.add(db_login_history)
    await db.commit()
    await db.refresh(db_login_history)
    return db_login_history

# --- PasswordResetToken CRUD ---

async def create_password_reset_token(
    db: AsyncSession, *, user_id: int, token: str, expires_at: datetime
) -> PasswordResetToken:
    db_password_reset_token = PasswordResetToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    db.add(db_password_reset_token)
    await db.commit()
    await db.refresh(db_password_reset_token)
    return db_password_reset_token

async def get_password_reset_token_by_token(db: AsyncSession, *, token: str) -> Optional[PasswordResetToken]:
    statement = select(PasswordResetToken).where(
        PasswordResetToken.token == token,
        PasswordResetToken.used_at == None # type: ignore # SQLModel/SA typing for None
    )
    result = await db.exec(statement)
    return result.first()

async def mark_password_reset_token_as_used(db: AsyncSession, *, db_obj: PasswordResetToken) -> PasswordResetToken:
    db_obj.used_at = datetime.now(timezone.utc)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj
