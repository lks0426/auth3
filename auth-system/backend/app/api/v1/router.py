from fastapi import APIRouter
from . import auth as auth_router_module # Use a different name to avoid conflict with the variable
# from . import users as users_router_module # Assuming you might have a users router
# from . import health as health_router_module # Assuming you might have a health router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router_module.router) # Use the router object from the imported module
# api_v1_router.include_router(users_router_module.router, prefix="/users", tags=["users"])
# api_v1_router.include_router(health_router_module.router, prefix="/health", tags=["health"])
