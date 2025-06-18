from typing import Optional, Any
from datetime import datetime, timezone # Ensure timezone is imported

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession # Use AsyncSession
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserUpdateAdmin # Schemas used for input type hinting
from app.core.security import get_password_hash


async def get_user(db: AsyncSession, user_id: int) -> Optional[User]:
    return await db.get(User, user_id)

async def get_user_by_email(db: AsyncSession, *, email: str) -> Optional[User]:
    statement = select(User).where(User.email == email)
    result = await db.exec(statement)
    return result.first()

async def get_user_by_username(db: AsyncSession, *, username: str) -> Optional[User]:
    statement = select(User).where(User.username == username)
    result = await db.exec(statement)
    return result.first()

async def create_user(db: AsyncSession, *, user_in: UserCreate) -> User:
    hashed_password = get_password_hash(user_in.password)
    # Ensure datetime is timezone-aware if your DB expects it (PostgreSQL often does)
    db_user = User(
        **user_in.model_dump(exclude={"password"}),
        hashed_password=hashed_password,
        password_changed_at=datetime.now(timezone.utc)
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def update_user(db: AsyncSession, *, db_obj: User, obj_in: UserUpdate | UserUpdateAdmin | dict[str, Any]) -> User:
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_obj, field, value)

    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def update_password(db: AsyncSession, *, db_obj: User, new_password: str) -> User:
    db_obj.hashed_password = get_password_hash(new_password)
    db_obj.password_changed_at = datetime.now(timezone.utc)
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def update_login_info(db: AsyncSession, *, user: User, login_ip: str) -> User:
    user.last_login = datetime.now(timezone.utc)
    user.login_ip = login_ip
    user.failed_login_attempts = 0
    user.locked_until = None
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def increment_failed_login_attempts(db: AsyncSession, *, user: User) -> User:
    user.failed_login_attempts += 1
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def lock_user_account(db: AsyncSession, *, user: User, until: datetime) -> User:
    user.locked_until = until
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def unlock_user_account(db: AsyncSession, *, user: User) -> User:
    user.locked_until = None
    user.failed_login_attempts = 0
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def activate_user(db: AsyncSession, *, user: User) -> User:
    user.is_active = True
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def deactivate_user(db: AsyncSession, *, user: User) -> User:
    user.is_active = False
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def verify_user(db: AsyncSession, *, user: User) -> User:
    user.is_verified = True
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
