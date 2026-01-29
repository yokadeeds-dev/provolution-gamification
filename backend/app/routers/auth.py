# routers/auth.py - Authentication Router
"""
Provolution Gamification - Authentication Endpoints
POST /auth/register - User registration
POST /auth/login - User login
POST /auth/google - Google OAuth login
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from datetime import datetime
import secrets
import string
import os

from ..models import (
    UserRegisterRequest,
    UserLoginRequest,
    AuthResponse,
    RegisterResponse,
    UserResponse,
    UserStats
)
from ..auth import hash_password, verify_password, create_access_token
from ..database import get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Google OAuth
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '249276087645-8db6c2913bgsv3p0p4c7njde3j5kvr6c.apps.googleusercontent.com')


class GoogleAuthRequest(BaseModel):
    credential: str


def generate_referral_code(length: int = 8) -> str:
    """Generate a unique referral code."""
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


def verify_google_token(credential: str) -> dict:
    """Verify Google ID token and return user info."""
    try:
        from google.oauth2 import id_token
        from google.auth.transport import requests
        
        idinfo = id_token.verify_oauth2_token(
            credential, 
            requests.Request(), 
            GOOGLE_CLIENT_ID
        )
        
        return {
            'google_id': idinfo['sub'],
            'email': idinfo['email'],
            'name': idinfo.get('name', ''),
            'picture': idinfo.get('picture', ''),
            'email_verified': idinfo.get('email_verified', False)
        }
    except ImportError:
        # Fallback: decode JWT manually (less secure but works without google-auth)
        import json
        import base64
        
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
        idinfo = json.loads(decoded)
        
        # Verify audience
        if idinfo.get('aud') != GOOGLE_CLIENT_ID:
            raise ValueError("Invalid audience")
        
        # Check expiration
        import time
        if idinfo.get('exp', 0) < time.time():
            raise ValueError("Token expired")
        
        return {
            'google_id': idinfo['sub'],
            'email': idinfo['email'],
            'name': idinfo.get('name', ''),
            'picture': idinfo.get('picture', ''),
            'email_verified': idinfo.get('email_verified', False)
        }
    except Exception as e:
        raise ValueError(f"Token verification failed: {str(e)}")


@router.post("/google")
def google_auth(request: GoogleAuthRequest):
    """
    Authenticate with Google OAuth.
    
    - Verifies Google ID token
    - Creates new user if not exists
    - Returns JWT token
    """
    try:
        google_info = verify_google_token(request.credential)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error": {
                    "code": "INVALID_GOOGLE_TOKEN",
                    "message": str(e)
                }
            }
        )
    
    with get_db() as conn:
        # Check if user exists by google_id
        user = conn.execute(
            "SELECT * FROM users WHERE google_id = ?",
            (google_info['google_id'],)
        ).fetchone()
        
        is_new_user = False
        
        if not user:
            # Check if email exists (link accounts)
            user = conn.execute(
                "SELECT * FROM users WHERE email = ?",
                (google_info['email'],)
            ).fetchone()
            
            if user:
                # Link Google to existing account
                conn.execute(
                    "UPDATE users SET google_id = ? WHERE id = ?",
                    (google_info['google_id'], user['id'])
                )
            else:
                # Create new user
                is_new_user = True
                
                # Generate username from email
                base_username = google_info['email'].split('@')[0].lower()
                base_username = ''.join(c for c in base_username if c.isalnum() or c == '_')[:20]
                username = base_username
                
                # Ensure unique username
                counter = 1
                while conn.execute(
                    "SELECT id FROM users WHERE username = ?",
                    (username,)
                ).fetchone():
                    username = f"{base_username}{counter}"
                    counter += 1
                
                # Generate referral code
                referral_code = generate_referral_code()
                while conn.execute(
                    "SELECT id FROM users WHERE referral_code = ?",
                    (referral_code,)
                ).fetchone():
                    referral_code = generate_referral_code()
                
                now = datetime.utcnow().isoformat()
                cursor = conn.execute(
                    """
                    INSERT INTO users (
                        username, email, password_hash, display_name,
                        google_id, avatar_emoji, referral_code,
                        created_at, last_active
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        username,
                        google_info['email'],
                        '',  # No password for Google users
                        google_info['name'] or username,
                        google_info['google_id'],
                        '🌱',
                        referral_code,
                        now,
                        now
                    )
                )
                
                # Fetch the new user
                user = conn.execute(
                    "SELECT * FROM users WHERE id = ?",
                    (cursor.lastrowid,)
                ).fetchone()
        
        # Update last_active
        conn.execute(
            "UPDATE users SET last_active = ? WHERE id = ?",
            (datetime.utcnow().isoformat(), user['id'])
        )
        
        # Create token
        token = create_access_token(user['id'], user['username'])
        
        # Get user stats
        stats = UserStats(
            challenges_completed=0,
            total_co2_saved_kg=user.get('total_co2_saved_kg', 0) or 0,
            badges_earned=0,
            referrals_count=0
        )
        
        user_response = UserResponse(
            id=user['id'],
            username=user['username'],
            display_name=user.get('display_name'),
            avatar_emoji=user.get('avatar_emoji', '🌱'),
            total_xp=user.get('total_xp', 0),
            level=user.get('level', 1),
            trust_level=user.get('trust_level', 1),
            streak_days=user.get('streak_days', 0),
            region=user.get('region'),
            referral_code=user.get('referral_code'),
            stats=stats
        )
        
        return {
            "success": True,
            "token": token,
            "user": user_response,
            "is_new_user": is_new_user
        }


@router.post("/register", response_model=RegisterResponse)
def register(request: UserRegisterRequest):
    """
    Register a new user account.
    
    - Creates user with hashed password
    - Generates unique referral code
    - Processes referral bonus if code provided
    - Returns JWT token for immediate login
    """
    with get_db() as conn:
        # Check if email already exists
        existing = conn.execute(
            "SELECT id FROM users WHERE email = ?",
            (request.email,)
        ).fetchone()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "success": False,
                    "error": {
                        "code": "EMAIL_EXISTS",
                        "message": "Diese E-Mail ist bereits registriert"
                    }
                }
            )
        
        # Check if username exists
        existing_username = conn.execute(
            "SELECT id FROM users WHERE username = ?",
            (request.username.lower(),)
        ).fetchone()
        
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "success": False,
                    "error": {
                        "code": "USERNAME_EXISTS",
                        "message": "Dieser Benutzername ist bereits vergeben"
                    }
                }
            )
        
        # Hash password
        password_hash = hash_password(request.password)
        
        # Generate referral code
        referral_code = generate_referral_code()
        while conn.execute(
            "SELECT id FROM users WHERE referral_code = ?",
            (referral_code,)
        ).fetchone():
            referral_code = generate_referral_code()
        
        # Process referrer if code provided
        referrer_id = None
        if request.referral_code:
            referrer = conn.execute(
                "SELECT id FROM users WHERE referral_code = ?",
                (request.referral_code.upper(),)
            ).fetchone()
            if referrer:
                referrer_id = referrer['id']
        
        # Insert new user
        now = datetime.utcnow().isoformat()
        cursor = conn.execute(
            """
            INSERT INTO users (
                username, email, password_hash, display_name,
                region, postal_code, referral_code, referred_by,
                created_at, last_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                request.username.lower(),
                request.email,
                password_hash,
                request.display_name or request.username,
                request.region,
                request.postal_code,
                referral_code,
                referrer_id,
                now,
                now
            )
        )
        user_id = cursor.lastrowid
        
        # Award referral bonus to referrer
        if referrer_id:
            conn.execute(
                """
                UPDATE users 
                SET total_xp = total_xp + 100
                WHERE id = ?
                """,
                (referrer_id,)
            )
        
        # Create JWT token
        token = create_access_token(user_id, request.username.lower())
        
        return RegisterResponse(
            success=True,
            user={
                "id": user_id,
                "username": request.username.lower(),
                "referral_code": referral_code
            },
            token=token
        )


@router.post("/login", response_model=AuthResponse)
def login(request: UserLoginRequest):
    """
    Authenticate user and return JWT token.
    
    - Verifies email and password
    - Updates last_active timestamp
    - Returns user profile with token
    """
    with get_db() as conn:
        # Find user by email
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (request.email,)
        ).fetchone()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "success": False,
                    "error": {
                        "code": "INVALID_CREDENTIALS",
                        "message": "E-Mail oder Passwort falsch"
                    }
                }
            )
        
        # Check if user has a password (might be Google-only user)
        if not user.get('password_hash'):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "success": False,
                    "error": {
                        "code": "GOOGLE_ACCOUNT",
                        "message": "Dieses Konto nutzt Google-Anmeldung. Bitte mit Google anmelden."
                    }
                }
            )
        
        # Verify password
        if not verify_password(request.password, user['password_hash']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "success": False,
                    "error": {
                        "code": "INVALID_CREDENTIALS",
                        "message": "E-Mail oder Passwort falsch"
                    }
                }
            )
        
        # Update last_active
        conn.execute(
            "UPDATE users SET last_active = ? WHERE id = ?",
            (datetime.utcnow().isoformat(), user['id'])
        )
        
        # Create token
        token = create_access_token(user['id'], user['username'])
        
        # Get user stats
        stats = UserStats(
            challenges_completed=0,
            total_co2_saved_kg=user.get('total_co2_saved_kg', 0) or 0,
            badges_earned=0,
            referrals_count=0
        )
        
        # Count completed challenges
        completed = conn.execute(
            """
            SELECT COUNT(*) as count FROM user_challenges 
            WHERE user_id = ? AND status = 'completed'
            """,
            (user['id'],)
        ).fetchone()
        stats.challenges_completed = completed['count'] if completed else 0
        
        # Count badges
        badges = conn.execute(
            "SELECT COUNT(*) as count FROM user_badges WHERE user_id = ?",
            (user['id'],)
        ).fetchone()
        stats.badges_earned = badges['count'] if badges else 0
        
        # Count referrals
        referrals = conn.execute(
            "SELECT COUNT(*) as count FROM users WHERE referred_by = ?",
            (user['id'],)
        ).fetchone()
        stats.referrals_count = referrals['count'] if referrals else 0
        
        user_response = UserResponse(
            id=user['id'],
            username=user['username'],
            display_name=user.get('display_name'),
            avatar_emoji=user.get('avatar_emoji', '🌱'),
            total_xp=user.get('total_xp', 0),
            level=user.get('level', 1),
            trust_level=user.get('trust_level', 1),
            streak_days=user.get('streak_days', 0),
            region=user.get('region'),
            referral_code=user.get('referral_code'),
            stats=stats
        )
        
        return AuthResponse(
            success=True,
            token=token,
            user=user_response
        )
