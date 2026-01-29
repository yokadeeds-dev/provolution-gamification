# models/leaderboard.py - Leaderboard Pydantic Models
"""
Provolution Gamification - Leaderboard Models
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import date
from .user import UserBriefResponse


class LeaderboardPeriod(BaseModel):
    """Time period for leaderboard."""
    start: date
    end: date


class LeaderboardEntry(BaseModel):
    """Single entry in a leaderboard."""
    rank: int
    user: UserBriefResponse
    score: float
    metric: str = "co2_kg"  # co2_kg, xp, challenges


class MyRank(BaseModel):
    """Current user's ranking info."""
    rank: int
    score: float
    users_above: int
    users_below: int


class LeaderboardResponse(BaseModel):
    """Full leaderboard response."""
    period: LeaderboardPeriod
    rankings: List[LeaderboardEntry]
    my_rank: Optional[MyRank] = None
