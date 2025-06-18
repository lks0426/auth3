from datetime import datetime, timedelta, timezone
from typing import Optional, Any
import re

from jose import JWTError, jwt
from passlib.context import CryptContext
# from passlib.hash import argon2 # CryptContext will manage this

from app.config import settings
from app.core.redis_client import redis_client # Assuming redis_client is the initialized client instance

# If using the get_redis_client dependency pattern:
# from app.core.redis_client import get_redis_client
# And then in functions: client = await get_redis_client()

# Password hashing context
# Using Argon2id as the primary scheme
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")

ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_MINUTES = settings.REFRESH_TOKEN_EXPIRE_MINUTES
SECRET_KEY = settings.SECRET_KEY


def create_access_token(subject: Any, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject: Any, expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"} # Add a type claim
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hashes a plain password."""
    return pwd_context.hash(password)

def is_password_strong(password: str) -> bool:
    """
    Checks if the password meets strength requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password): # Basic set of special chars
        return False
    return True

async def add_token_to_blacklist(token: str, expires_in: timedelta):
    """
    Adds a token to the Redis blacklist with an expiry time.
    The token itself is used as the key.
    """
    # For the global client pattern, ensure redis_client is initialized (e.g., on app startup)
    # If using get_redis_client: client = await get_redis_client()
    await redis_client.setex(f"blacklist:{token}", int(expires_in.total_seconds()), "blacklisted")

async def is_token_blacklisted(token: str) -> bool:
    """
    Checks if a token is in the Redis blacklist.
    """
    # If using get_redis_client: client = await get_redis_client()
    return await redis_client.exists(f"blacklist:{token}") > 0

# Helper to decode tokens (can be expanded for more robust error handling)
async def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError: # Catches various JWT errors like ExpiredSignatureError, InvalidTokenError
        return None
