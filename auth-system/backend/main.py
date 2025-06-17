from fastapi import FastAPI

app = FastAPI(title="Auth System API")

@app.get("/")
async def root():
    return {"message": "Welcome to the Auth System API"}

# Placeholder for future API routers
# from app.api.v1 import api_router
# app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
