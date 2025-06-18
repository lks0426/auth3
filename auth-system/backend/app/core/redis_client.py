import redis.asyncio as redis # Use async redis
from app.config import settings

# Global Redis client instance, configured for async/await
# The client should be initialized when the application starts.
# For FastAPI, this can be done in a startup event or by simply defining it globally
# if the settings are available at import time.

redis_client: redis.Redis

async def init_redis_pool():
    """
    Call this function during FastAPI startup to initialize the Redis client.
    """
    global redis_client
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    # You could also use redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB, decode_responses=True)
    # if you prefer separate host/port/db settings.

async def get_redis_client() -> redis.Redis:
    """
    Dependency to get the Redis client.
    Ensures the client is initialized. This is a simple way; for robust applications,
    consider managing the lifecycle with FastAPI events (startup/shutdown).
    """
    if not hasattr(redis_client, 'connection_pool'): # A simple check if it's initialized
        # This path should ideally not be hit if init_redis_pool is called on startup.
        # Consider raising an exception or logging a warning if called before initialization.
        await init_redis_pool() # Fallback initialization, not ideal for every get call.
    return redis_client

async def close_redis_pool():
    """
    Call this function during FastAPI shutdown to close Redis connections.
    """
    if hasattr(redis_client, 'close'): # Older versions of redis-py
        await redis_client.close()
    if hasattr(redis_client, 'connection_pool'): # For redis-py 4.x which uses connection pool
        await redis_client.connection_pool.disconnect()


async def ping_redis(client: redis.Redis = None) -> bool:
    """
    Optional: A function to check connection.
    If client is not provided, it will try to get one using the dependency.
    """
    if client is None:
        client = await get_redis_client()
    try:
        await client.ping()
        return True
    except Exception:
        # Log the exception for debugging
        return False

# Note: The direct global `redis_client = redis.from_url(...)` is also common,
# but initializing in a startup event (`init_redis_pool`) and closing on shutdown
# (`close_redis_pool`) is generally better for resource management in async apps.
# The `get_redis_client` would then just return the globally initialized client.
# For this iteration, init_redis_pool should be called in main.py startup.
