# models/challenge.py - Challenge Pydantic Models
"""
Provolution Gamification - Challenge Models
Request/Response schemas for challenge-related endpoints
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from enum import Enum


class ChallengeCategory(str, Enum):
    ONBOARDING = "onboarding"
    ENERGIE = "energie"
    MOBILITAET = "mobilitaet"
    COMMUNITY = "community"
    POLITIK = "politik"


class ChallengeDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class ChallengeStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class VerificationMethod(str, Enum):
    SELF_REPORT = "self_report"
    PHOTO = "photo"
    API = "api"
    HYBRID = "hybrid"


# Sub-models
class BadgeInfo(BaseModel):
    """Badge information attached to a challenge."""
    name: str
    icon: str
    tier: Optional[str] = "bronze"


class ImpactInfo(BaseModel):
    """Environmental impact information."""
    co2_kg_year: float
    savings_euro_year: Optional[float] = None
    type: str = "direct"  # direct, indirect, systemic


class VerificationInfo(BaseModel):
    """How a challenge is verified."""
    method: VerificationMethod
    type: str
    options: Optional[List[str]] = None


class ChallengeStats(BaseModel):
    """Challenge participation statistics."""
    participants_active: int = 0
    participants_completed: int = 0
    completion_rate: float = 0.0


# Request models
class ChallengeJoinRequest(BaseModel):
    """Request to join a challenge (mostly empty, just needs auth)."""
    pass


class DailyLogRequest(BaseModel):
    """Request model for logging daily progress."""
    log_date: date
    completed: bool = True
    notes: Optional[str] = Field(None, max_length=500)
    proof_type: Optional[str] = None  # photo, api, none
    proof_url: Optional[str] = None


# Response models
class ChallengeBrief(BaseModel):
    """Brief challenge info for lists."""
    id: str
    name: str
    name_emoji: str
    description: str
    category: ChallengeCategory
    difficulty: ChallengeDifficulty
    duration_days: int
    xp_reward: int
    badge: Optional[BadgeInfo] = None
    impact: ImpactInfo
    participants_count: int = 0
    user_status: Optional[str] = None  # null, "active", "completed"


class ChallengeDetail(ChallengeBrief):
    """Full challenge details."""
    description_long: Optional[str] = None
    success_criteria: List[str] = []
    verification: VerificationInfo
    stats: ChallengeStats


class ChallengeListResponse(BaseModel):
    """Response for challenge list endpoint."""
    challenges: List[ChallengeBrief]
    total: int
    offset: int = 0
    limit: int = 20


class UserChallengeStatus(BaseModel):
    """Status of a user's participation in a challenge."""
    id: int
    challenge_id: str
    status: ChallengeStatus
    started_at: datetime
    progress_percent: int = 0
    days_completed: int = 0


class ChallengeJoinResponse(BaseModel):
    """Response when joining a challenge."""
    success: bool
    user_challenge: UserChallengeStatus
    message: str


class DailyLog(BaseModel):
    """A single day's log entry."""
    id: int
    log_date: date
    completed: bool
    notes: Optional[str] = None
    proof_url: Optional[str] = None


class ProgressInfo(BaseModel):
    """Progress update info."""
    days_completed: int
    days_remaining: int
    progress_percent: int


class StreakInfo(BaseModel):
    """User streak information."""
    current: int
    bonus_at_30_days: int = 500


class DailyLogResponse(BaseModel):
    """Response when logging daily progress."""
    success: bool
    log: DailyLog
    progress: ProgressInfo
    xp_earned: int = 0
    streak: StreakInfo


class ChallengeProgressResponse(BaseModel):
    """Full progress info for a challenge."""
    challenge_id: str
    status: ChallengeStatus
    started_at: datetime
    days_completed: int
    days_remaining: int
    progress_percent: int
    logs: List[DailyLog]
    verification_status: str = "pending"
