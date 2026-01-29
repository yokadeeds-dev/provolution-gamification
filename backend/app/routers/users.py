# routers/users.py - User Profile Router
"""
Provolution Gamification - User Endpoints
GET /users/me - Get own profile
PUT /users/me - Update profile
GET /users/{id}/stats - Get user stats
"""

from fastapi import APIRouter, Depends, HTTPException, status

from ..models import UserResponse, UserUpdateRequest, UserStats
from ..auth import CurrentUser, get_current_user
from ..database import get_db

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: CurrentUser = Depends(get_current_user)):
    """
    Get the current user's full profile.
    Requires authentication.
    """
    with get_db() as conn:
        user = conn.execute(
            "SELECT * FROM users WHERE id = ?",
            (current_user.id,)
        ).fetchone()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "User nicht gefunden"
                    }
                }
            )
        
        # Get stats
        stats = _get_user_stats(conn, current_user.id)
        
        return UserResponse(
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


@router.put("/me", response_model=UserResponse)
def update_my_profile(
    request: UserUpdateRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Update current user's profile.
    Only provided fields will be updated.
    """
    with get_db() as conn:
        # Build update query dynamically
        updates = []
        params = []
        
        if request.display_name is not None:
            updates.append("display_name = ?")
            params.append(request.display_name)
        
        if request.avatar_emoji is not None:
            updates.append("avatar_emoji = ?")
            params.append(request.avatar_emoji)
        
        if request.focus_track is not None:
            updates.append("focus_track = ?")
            params.append(request.focus_track)
        
        if not updates:
            # Nothing to update, just return current profile
            return get_my_profile(current_user)
        
        # Execute update
        params.append(current_user.id)
        conn.execute(
            f"UPDATE users SET {', '.join(updates)} WHERE id = ?",
            tuple(params)
        )
        
        # Return updated profile
        return get_my_profile(current_user)


@router.get("/{user_id}/stats")
def get_user_stats(user_id: int, current_user: CurrentUser = Depends(get_current_user)):
    """
    Get statistics for a specific user.
    Can view own stats or other users' public stats.
    """
    with get_db() as conn:
        user = conn.execute(
            "SELECT id, username, display_name, avatar_emoji FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "User nicht gefunden"
                    }
                }
            )
        
        stats = _get_user_stats(conn, user_id)
        
        return {
            "user": {
                "id": user['id'],
                "username": user['username'],
                "display_name": user.get('display_name'),
                "avatar_emoji": user.get('avatar_emoji', '🌱')
            },
            "stats": stats.model_dump()
        }


def _get_user_stats(conn, user_id: int) -> UserStats:
    """Helper to calculate user statistics."""
    # Get user's CO2 savings
    user = conn.execute(
        "SELECT total_co2_saved_kg FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()
    
    total_co2 = user.get('total_co2_saved_kg', 0) if user else 0
    
    # Count completed challenges
    completed = conn.execute(
        """
        SELECT COUNT(*) as count FROM user_challenges 
        WHERE user_id = ? AND status = 'completed'
        """,
        (user_id,)
    ).fetchone()
    
    # Count badges
    badges = conn.execute(
        "SELECT COUNT(*) as count FROM user_badges WHERE user_id = ?",
        (user_id,)
    ).fetchone()
    
    # Count referrals
    referrals = conn.execute(
        "SELECT COUNT(*) as count FROM users WHERE referred_by = ?",
        (user_id,)
    ).fetchone()
    
    return UserStats(
        challenges_completed=completed['count'] if completed else 0,
        total_co2_saved_kg=total_co2 or 0,
        badges_earned=badges['count'] if badges else 0,
        referrals_count=referrals['count'] if referrals else 0
    )
