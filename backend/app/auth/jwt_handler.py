# auth/jwt_handler.py - JWT Token Management
"""
Provolution Gamification - JWT Authentication Handler
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
import secrets
from pydantic import BaseModel


# Configuration - In production, use environment variables!
class JWTSettings(BaseModel):
    """JWT configuration settings."""
    secret_key: str = secrets.token_hex(32)  # Generate new key on startup
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours
    refresh_token_expire_days: int = 30


# Singleton settings instance
_settings: Optional[JWTSettings] = None


def get_jwt_settings() -> JWTSettings:
    """Get or create JWT settings."""
    global _settings
    if _settings is None:
        _settings = JWTSettings()
    return _settings


def create_access_token(user_id: int, username: str) -> str:
    """
    Create a new JWT access token.
    
    Args:
        user_id: Database user ID
        username: User's username
        
    Returns:
        Encoded JWT token string
    """
    settings = get_jwt_settings()
    
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    
    payload = {
        "sub": str(user_id),
        "username": username,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access"
    }
    
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(user_id: int) -> str:
    """
    Create a new JWT refresh token.
    
    Args:
        user_id: Database user ID
        
    Returns:
        Encoded JWT refresh token string
    """
    settings = get_jwt_settings()
    
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days
    )
    
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh"
    }
    
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> dict:
    """
    Decode and validate a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded payload dictionary
        
    Raises:
        jwt.ExpiredSignatureError: Token has expired
        jwt.InvalidTokenError: Token is invalid
    """
    settings = get_jwt_settings()
    
    payload = jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.algorithm]
    )
    
    return payload


def verify_token(token: str) -> Optional[dict]:
    """
    Verify a token and return payload if valid.
    
    Args:
        token: JWT token string
        
    Returns:
        Payload dict if valid, None if invalid
    """
    try:
        return decode_token(token)
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_user_id_from_token(token: str) -> Optional[int]:
    """
    Extract user ID from a valid token.
    
    Args:
        token: JWT token string
        
    Returns:
        User ID if token is valid, None otherwise
    """
    payload = verify_token(token)
    if payload and "sub" in payload:
        try:
            return int(payload["sub"])
        except ValueError:
            return None
    return None
