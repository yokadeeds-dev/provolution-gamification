# routers/auth.py - Authentication Router
"""
Provolution Gamification - Authentication Endpoints
POST /auth/register - User registration
POST /auth/login - User login
"""

from fastapi import APIRouter, HTTPException, status
from datetime import datetime
import secrets
import string

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


def generate_referral_code(length: int = 8) -> str:
    """Generate a unique referral code."""
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


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
