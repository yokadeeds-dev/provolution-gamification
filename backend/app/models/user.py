# models/user.py - User Pydantic Models
"""
Provolution Gamification - User Models
Request/Response schemas for user-related endpoints
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
import re


class UserRegisterRequest(BaseModel):
    """Request model for user registration."""
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    display_name: Optional[str] = Field(None, max_length=50)
    region: Optional[str] = Field(None, max_length=50)
    postal_code: Optional[str] = Field(None, max_length=10)
    referral_code: Optional[str] = Field(None, max_length=20)
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username darf nur Buchstaben, Zahlen und _ enthalten')
        return v.lower()
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r'[A-Z]', v):
            raise ValueError('Passwort muss mindestens einen Großbuchstaben enthalten')
        if not re.search(r'[0-9]', v):
            raise ValueError('Passwort muss mindestens eine Zahl enthalten')
        return v


class UserLoginRequest(BaseModel):
    """Request model for user login."""
    email: EmailStr
    password: str


class UserUpdateRequest(BaseModel):
    """Request model for profile updates."""
    display_name: Optional[str] = Field(None, max_length=50)
    avatar_emoji: Optional[str] = Field(None, max_length=10)
    focus_track: Optional[str] = None
    
    @field_validator('focus_track')
    @classmethod
    def validate_focus_track(cls, v: Optional[str]) -> Optional[str]:
        valid_tracks = ['energie', 'mobilitaet', 'konsum', 'community', 'politik']
        if v and v not in valid_tracks:
            raise ValueError(f'Focus track muss einer von {valid_tracks} sein')
        return v


class UserStats(BaseModel):
    """User statistics sub-model."""
    challenges_completed: int = 0
    total_co2_saved_kg: float = 0.0
    badges_earned: int = 0
    referrals_count: int = 0


class UserResponse(BaseModel):
    """Response model for user data."""
    id: int
    username: str
    display_name: Optional[str] = None
    avatar_emoji: str = "🌱"
    total_xp: int = 0
    level: int = 1
    trust_level: int = 1
    streak_days: int = 0
    region: Optional[str] = None
    referral_code: Optional[str] = None
    stats: Optional[UserStats] = None
    
    class Config:
        from_attributes = True


class UserBriefResponse(BaseModel):
    """Brief user info for leaderboards etc."""
    id: int
    username: str
    display_name: Optional[str] = None
    avatar_emoji: str = "🌱"


class AuthResponse(BaseModel):
    """Response model for authentication endpoints."""
    success: bool
    token: str
    user: UserResponse
    message: Optional[str] = None


class RegisterResponse(BaseModel):
    """Response model specifically for registration."""
    success: bool
    user: dict
    token: str
