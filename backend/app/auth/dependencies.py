# auth/dependencies.py - FastAPI Auth Dependencies
"""
Provolution Gamification - Authentication Dependencies
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

from .jwt_handler import verify_token, get_user_id_from_token
from ..database import get_db


# Bearer token security scheme
security = HTTPBearer(auto_error=False)


class CurrentUser:
    """Represents the currently authenticated user."""
    def __init__(self, user_id: int, username: str, data: dict = None):
        self.id = user_id
        self.username = username
        self.data = data or {}
    
    @property
    def total_xp(self) -> int:
        return self.data.get('total_xp', 0)
    
    @property
    def level(self) -> int:
        return self.data.get('level', 1)
    
    @property
    def trust_level(self) -> int:
        return self.data.get('trust_level', 1)


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[CurrentUser]:
    """
    Get current user if authenticated, None otherwise.
    Use this for endpoints that work both authenticated and anonymous.
    """
    if not credentials:
        return None
    
    token = credentials.credentials
    payload = verify_token(token)
    
    if not payload:
        return None
    
    user_id = int(payload.get("sub", 0))
    username = payload.get("username", "")
    
    if not user_id:
        return None
    
    # Fetch full user data from database
    with get_db() as conn:
        user_data = conn.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()
        
        if not user_data:
            return None
        
        return CurrentUser(
            user_id=user_id,
            username=username,
            data=dict(user_data)
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> CurrentUser:
    """
    Get current authenticated user. Raises 401 if not authenticated.
    Use this for endpoints that require authentication.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": "Token fehlt"
                }
            },
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = credentials.credentials
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": "Token ungültig oder abgelaufen"
                }
            },
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user_id = int(payload.get("sub", 0))
    username = payload.get("username", "")
    
    # Fetch full user data
    with get_db() as conn:
        user_data = conn.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "success": False,
                    "error": {
                        "code": "UNAUTHORIZED",
                        "message": "User nicht gefunden"
                    }
                }
            )
        
        return CurrentUser(
            user_id=user_id,
            username=username,
            data=dict(user_data)
        )


def require_trust_level(min_level: int):
    """
    Dependency factory for requiring minimum trust level.
    
    Usage:
        @router.post("/admin/action")
        def admin_action(user: CurrentUser = Depends(require_trust_level(3))):
            ...
    """
    def check_trust_level(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.trust_level < min_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "success": False,
                    "error": {
                        "code": "FORBIDDEN",
                        "message": f"Trust Level {min_level} erforderlich"
                    }
                }
            )
        return user
    
    return check_trust_level
