# routers/badges.py - Badge Router
"""
Provolution Gamification - Badge Endpoints
GET /badges - List all badges
GET /badges/my - Get user's earned badges
"""

from fastapi import APIRouter, Depends
from datetime import datetime
from typing import Optional

from ..models import (
    Badge,
    EarnedBadge,
    NextBadge,
    MyBadgesResponse,
    AllBadgesResponse
)
from ..auth import CurrentUser, get_current_user
from ..database import get_db

router = APIRouter(prefix="/badges", tags=["Badges"])


@router.get("", response_model=AllBadgesResponse)
def list_all_badges():
    """List all available badges in the system."""
    with get_db() as conn:
        badges_data = conn.execute(
            """
            SELECT * FROM badges
            ORDER BY tier, name
            """
        ).fetchall()
        
        badges = [
            Badge(
                id=b['id'],
                name=b['name'],
                icon=b['icon'],
                tier=b.get('tier', 'bronze'),
                description=b.get('description'),
                requirement=b.get('requirement')
            )
            for b in badges_data
        ]
        
        return AllBadgesResponse(
            badges=badges,
            total=len(badges)
        )


@router.get("/my", response_model=MyBadgesResponse)
def get_my_badges(current_user: CurrentUser = Depends(get_current_user)):
    """Get badges earned by the current user."""
    with get_db() as conn:
        # Get earned badges
        earned_data = conn.execute(
            """
            SELECT b.*, ub.earned_at, ub.challenge_id
            FROM user_badges ub
            JOIN badges b ON b.id = ub.badge_id
            WHERE ub.user_id = ?
            ORDER BY ub.earned_at DESC
            """,
            (current_user.id,)
        ).fetchall()
        
        badges = [
            EarnedBadge(
                id=b['id'],
                name=b['name'],
                icon=b['icon'],
                tier=b.get('tier', 'bronze'),
                description=b.get('description'),
                earned_at=datetime.fromisoformat(b['earned_at']),
                challenge_id=b.get('challenge_id')
            )
            for b in earned_data
        ]
        
        # Determine next badge (simplified - based on CO2 milestones)
        next_badge = None
        user_co2 = current_user.data.get('total_co2_saved_kg', 0)
        
        # CO2 milestone badges
        milestones = [
            (100, "100kg_club", "100kg Club", "🌍", "100 kg CO₂ vermieden"),
            (500, "500kg_champion", "500kg Champion", "🏆", "500 kg CO₂ vermieden"),
            (1000, "tonne_titan", "Tonnen-Titan", "💎", "1 Tonne CO₂ vermieden"),
        ]
        
        for threshold, badge_id, name, icon, requirement in milestones:
            if user_co2 < threshold:
                progress = user_co2 / threshold
                next_badge = NextBadge(
                    id=badge_id,
                    name=name,
                    icon=icon,
                    progress=round(progress, 2),
                    requirement=requirement
                )
                break
        
        return MyBadgesResponse(
            badges=badges,
            total_earned=len(badges),
            next_badge=next_badge
        )
