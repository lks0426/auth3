from .user import (
    get_user,
    get_user_by_email,
    get_user_by_username,
    create_user,
    update_user,
    update_password,
    update_login_info,
    increment_failed_login_attempts,
    lock_user_account,
    unlock_user_account,
    activate_user,
    deactivate_user,
    verify_user,
)

from .auth import (
    create_refresh_token,
    get_refresh_token_by_token,
    delete_refresh_token,
    delete_all_refresh_tokens_for_user,
    create_login_history,
    create_password_reset_token,
    get_password_reset_token_by_token,
    mark_password_reset_token_as_used,
)

# It's common to group CRUD operations into objects like:
# from . import user, auth
# crud_user = user
# crud_auth_refresh_token = auth (if auth.py contains only refresh token ops)
# This makes it callable like: crud.user.get_user(...)

__all__ = [
    # User CRUD
    "get_user",
    "get_user_by_email",
    "get_user_by_username",
    "create_user",
    "update_user",
    "update_password",
    "update_login_info",
    "increment_failed_login_attempts",
    "lock_user_account",
    "unlock_user_account",
    "activate_user",
    "deactivate_user",
    "verify_user",
    # Auth CRUD
    "create_refresh_token",
    "get_refresh_token_by_token",
    "delete_refresh_token",
    "delete_all_refresh_tokens_for_user",
    "create_login_history",
    "create_password_reset_token",
    "get_password_reset_token_by_token",
    "mark_password_reset_token_as_used",
]
