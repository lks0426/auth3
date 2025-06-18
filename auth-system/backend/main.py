from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.redis_client import init_redis_pool, close_redis_pool
from app.api.v1.router import api_v1_router # Corrected import path
from app.config import settings

@asynccontextmanager
async def lifespan(app_lifespan: FastAPI): # Parameter name changed to avoid conflict
    # Startup
    await init_redis_pool()
    print("Redis pool initialized.")
    yield
    # Shutdown
    await close_redis_pool()
    print("Redis pool closed.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.2.0", # Example version
    description="Modern Authentication System API",
    lifespan=lifespan,
    # openapi_url=f"{settings.API_V1_STR}/openapi.json" # Optional: customize openapi url
)

# Include the API router
app.include_router(api_v1_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Root"])
async def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}

# The uvicorn.run block is for direct execution,
# often not used when deploying with Gunicorn/Uvicorn workers in production.
if __name__ == "__main__":
    import uvicorn
    # For development, you might want to specify reload=True
    # Uvicorn will pick up the 'app' instance from this file.
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
