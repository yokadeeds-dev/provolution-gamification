# models/__init__.py - Model exports
"""
Provolution Gamification - Model Exports
"""

from .user import (
    UserRegisterRequest,
    UserLoginRequest,
    UserUpdateRequest,
    UserResponse,
    UserBriefResponse,
    UserStats,
    AuthResponse,
    RegisterResponse
)

from .challenge import (
    ChallengeCategory,
    ChallengeDifficulty,
    ChallengeStatus,
    VerificationMethod,
    BadgeInfo,
    ImpactInfo,
    VerificationInfo,
    ChallengeStats,
    ChallengeBrief,
    ChallengeDetail,
    ChallengeListResponse,
    ChallengeJoinRequest,
    ChallengeJoinResponse,
    DailyLogRequest,
    DailyLogResponse,
    ChallengeProgressResponse,
    UserChallengeStatus,
    DailyLog,
    ProgressInfo,
    StreakInfo
)

from .leaderboard import (
    LeaderboardPeriod,
    LeaderboardEntry,
    LeaderboardResponse,
    MyRank
)

from .badge import (
    Badge,
    EarnedBadge,
    NextBadge,
    MyBadgesResponse,
    AllBadgesResponse
)

from .reward import (
    HardwarePackage,
    HardwarePackagesResponse,
    ShippingAddress,
    RedeemRequest,
    RedeemResponse,
    RedemptionInfo
)

__all__ = [
    # User
    "UserRegisterRequest",
    "UserLoginRequest", 
    "UserUpdateRequest",
    "UserResponse",
    "UserBriefResponse",
    "UserStats",
    "AuthResponse",
    "RegisterResponse",
    # Challenge
    "ChallengeCategory",
    "ChallengeDifficulty",
    "ChallengeStatus",
    "VerificationMethod",
    "BadgeInfo",
    "ImpactInfo",
    "VerificationInfo",
    "ChallengeStats",
    "ChallengeBrief",
    "ChallengeDetail",
    "ChallengeListResponse",
    "ChallengeJoinRequest",
    "ChallengeJoinResponse",
    "DailyLogRequest",
    "DailyLogResponse",
    "ChallengeProgressResponse",
    "UserChallengeStatus",
    "DailyLog",
    "ProgressInfo",
    "StreakInfo",
    # Leaderboard
    "LeaderboardPeriod",
    "LeaderboardEntry",
    "LeaderboardResponse",
    "MyRank",
    # Badge
    "Badge",
    "EarnedBadge",
    "NextBadge",
    "MyBadgesResponse",
    "AllBadgesResponse",
    # Reward
    "HardwarePackage",
    "HardwarePackagesResponse",
    "ShippingAddress",
    "RedeemRequest",
    "RedeemResponse",
    "RedemptionInfo",
]
