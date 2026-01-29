# models/badge.py - Badge Pydantic Models
"""
Provolution Gamification - Badge Models
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class Badge(BaseModel):
    """Badge information."""
    id: str
    name: str
    icon: str
    tier: str = "bronze"  # bronze, silver, gold, platinum
    description: Optional[str] = None
    requirement: Optional[str] = None


class EarnedBadge(Badge):
    """Badge that a user has earned."""
    earned_at: datetime
    challenge_id: Optional[str] = None


class NextBadge(BaseModel):
    """Information about user's next achievable badge."""
    id: str
    name: str
    icon: str
    progress: float  # 0.0 to 1.0
    requirement: str


class MyBadgesResponse(BaseModel):
    """Response for user's badges."""
    badges: List[EarnedBadge]
    total_earned: int
    next_badge: Optional[NextBadge] = None


class AllBadgesResponse(BaseModel):
    """Response listing all available badges."""
    badges: List[Badge]
    total: int
