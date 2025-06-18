from typing import AsyncGenerator, Annotated # Annotated for Python 3.9+ for Depends

from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import Depends

from app.database import async_engine # Assuming async_engine from database.py
from app.config import Settings, get_settings # Import get_settings

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get an async database session.
    """
    async with AsyncSession(async_engine) as session:
        yield session

# Type alias for dependency injection convenience
ActiveSession = Annotated[AsyncSession, Depends(get_db)]
CurrentSettings = Annotated[Settings, Depends(get_settings)]

# You can also define other common dependencies here, for example:
# from app.api.v1.auth import get_current_user # Assuming get_current_user will be there
# CurrentUser = Annotated[User, Depends(get_current_user)] # User model from app.models.user
