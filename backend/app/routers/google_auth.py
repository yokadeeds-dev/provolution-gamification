# routers/google_auth.py
"""
Google OAuth Authentication for Provolution Gamification
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from datetime import datetime, timedelta
import os
import secrets
import jwt

from ..database import get_db

router = APIRouter(prefix="/auth/google", tags=["Google Auth"])

# Config
JWT_SECRET = os.environ.get("JWT_SECRET", "provolution-dev-secret-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24 * 7  # 1 week


class GoogleTokenRequest(BaseModel):
    """Request body for Google token verification."""
    credential: str  # Google ID token from frontend


class GoogleAuthResponse(BaseModel):
    """Response after successful Google auth."""
    access_token: str
    token_type: str = "bearer"
    user: dict


def create_jwt_token(user_id: int, email: str) -> str:
    """Create JWT token for authenticated user."""
    expiration = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expiration,
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_google_token(credential: str) -> dict:
    """
    Verify Google ID token.
    In production, this should properly validate the token with Google.
    For now, we decode it without verification for development.
    """
    try:
        # Decode JWT without verification (for development)
        # In production, use google.oauth2.id_token.verify_oauth2_token
        import base64
        import json
        
        # Google ID tokens are JWTs - decode the payload
        parts = credential.split('.')
        if len(parts) != 3:
            raise ValueError("Invalid token format")
        
        # Decode payload (middle part)
        payload = parts[1]
        # Add padding if needed
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += '=' * padding
        
        decoded = base64.urlsafe_b64decode(payload)
        data = json.loads(decoded)
        
        # Extract user info
        return {
            "google_id": data.get("sub"),
            "email": data.get("email"),
            "name": data.get("name"),
            "picture": data.get("picture"),
            "email_verified": data.get("email_verified", False)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google token: {str(e)}"
        )


def generate_username(email: str, name: str = None) -> str:
    """Generate unique username from email/name."""
    if name:
        base = name.lower().replace(' ', '_')[:15]
    else:
        base = email.split('@')[0][:15]
    
    # Add random suffix
    suffix = secrets.token_hex(3)
    return f"{base}_{suffix}"


@router.post("/callback", response_model=GoogleAuthResponse)
def google_auth_callback(request: GoogleTokenRequest):
    """
    Handle Google OAuth callback.
    Verifies token, creates/updates user, returns JWT.
    """
    # Verify Google token
    google_user = verify_google_token(request.credential)
    
    if not google_user.get("email"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not provided by Google"
        )
    
    google_id = google_user["google_id"]
    email = google_user["email"]
    name = google_user.get("name", "")
    picture = google_user.get("picture", "")
    
    now = datetime.utcnow().isoformat()
    
    with get_db() as conn:
        # Check if user exists by Google ID
        existing = conn.execute(
            "SELECT * FROM users WHERE google_id = ?",
            (google_id,)
        ).fetchone()
        
        if existing:
            # Update last login
            conn.execute(
                "UPDATE users SET last_login = ?, updated_at = ? WHERE id = ?",
                (now, now, existing['id'])
            )
            user = existing
        else:
            # Check if email already exists (local account)
            email_exists = conn.execute(
                "SELECT * FROM users WHERE email = ?",
                (email,)
            ).fetchone()
            
            if email_exists:
                # Link Google to existing account
                conn.execute("""
                    UPDATE users SET 
                        google_id = ?,
                        auth_provider = 'google',
                        avatar_url = COALESCE(avatar_url, ?),
                        last_login = ?,
                        updated_at = ?
                    WHERE id = ?
                """, (google_id, picture, now, now, email_exists['id']))
                user = email_exists
            else:
                # Create new user
                username = generate_username(email, name)
                referral_code = secrets.token_hex(6).upper()
                
                cursor = conn.execute("""
                    INSERT INTO users (
                        username, email, google_id, auth_provider,
                        display_name, avatar_url, referral_code,
                        created_at, updated_at, last_login
                    ) VALUES (?, ?, ?, 'google', ?, ?, ?, ?, ?, ?)
                """, (
                    username, email, google_id,
                    name or username, picture, referral_code,
                    now, now, now
                ))
                
                user_id = cursor.lastrowid
                user = conn.execute(
                    "SELECT * FROM users WHERE id = ?",
                    (user_id,)
                ).fetchone()
        
        conn.commit()
    
    # Create JWT token
    token = create_jwt_token(user['id'], user['email'])
    
    # Return response
    return GoogleAuthResponse(
        access_token=token,
        user={
            "id": user['id'],
            "username": user['username'],
            "email": user['email'],
            "display_name": user.get('display_name') or user['username'],
            "avatar_emoji": user.get('avatar_emoji', '🌱'),
            "avatar_url": user.get('avatar_url'),
            "total_xp": user.get('total_xp', 0),
            "level": user.get('level', 1),
            "auth_provider": user.get('auth_provider', 'google')
        }
    )


@router.get("/config")
def get_google_config():
    """
    Return Google OAuth client ID for frontend.
    """
    client_id = os.environ.get("GOOGLE_CLIENT_ID", "")
    
    if not client_id:
        return {
            "enabled": False,
            "message": "Google OAuth not configured. Set GOOGLE_CLIENT_ID environment variable."
        }
    
    return {
        "enabled": True,
        "client_id": client_id
    }
