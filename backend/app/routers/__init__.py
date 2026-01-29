# routers/__init__.py - Router exports
"""
Provolution Gamification - Router Module
"""

from .auth import router as auth_router
from .users import router as users_router
from .challenges import router as challenges_router
from .leaderboards import router as leaderboards_router
from .badges import router as badges_router
from .rewards import router as rewards_router

__all__ = [
    "auth_router",
    "users_router",
    "challenges_router",
    "leaderboards_router",
    "badges_router",
    "rewards_router"
]
