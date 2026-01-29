# auth/__init__.py - Auth module exports
"""
Provolution Gamification - Auth Module
"""

from .jwt_handler import (
    create_access_token,
    create_refresh_token,
    verify_token,
    decode_token,
    get_user_id_from_token
)

from .password import (
    hash_password,
    verify_password
)

from .dependencies import (
    CurrentUser,
    get_current_user,
    get_current_user_optional,
    require_trust_level,
    security
)

__all__ = [
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    "decode_token",
    "get_user_id_from_token",
    "hash_password",
    "verify_password",
    "CurrentUser",
    "get_current_user",
    "get_current_user_optional",
    "require_trust_level",
    "security"
]
