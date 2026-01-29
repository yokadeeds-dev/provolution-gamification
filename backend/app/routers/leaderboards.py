# routers/leaderboards.py - Leaderboard Router
"""
Provolution Gamification - Leaderboard Endpoints
GET /leaderboards/weekly - Weekly ranking
GET /leaderboards/monthly - Monthly ranking
GET /leaderboards/regional/{region} - Regional ranking
"""

from fastapi import APIRouter, Depends, Query
from datetime import datetime, date, timedelta
from typing import Optional

from ..models import (
    LeaderboardResponse,
    LeaderboardPeriod,
    LeaderboardEntry,
    MyRank,
    UserBriefResponse
)
from ..auth import CurrentUser, get_current_user, get_current_user_optional
from ..database import get_db

router = APIRouter(prefix="/leaderboards", tags=["Leaderboards"])


def _get_week_dates() -> tuple[date, date]:
    """Get start and end of current week (Monday to Sunday)."""
    today = date.today()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    return start, end


def _get_month_dates() -> tuple[date, date]:
    """Get start and end of current month."""
    today = date.today()
    start = today.replace(day=1)
    # End of month
    if today.month == 12:
        end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    return start, end


def _build_leaderboard(
    conn,
    start_date: date,
    end_date: date,
    limit: int,
    current_user_id: Optional[int],
    region: Optional[str] = None
) -> LeaderboardResponse:
    """Build leaderboard response with rankings and user position."""
    
    # Base query - sum CO2 from completed challenges in period
    region_filter = ""
    params = [start_date.isoformat(), end_date.isoformat()]
    
    if region:
        region_filter = "AND u.region = ?"
        params.append(region)
    
    params.append(limit)
    
    # Get top users by CO2 saved in period
    rankings_data = conn.execute(
        f"""
        SELECT 
            u.id,
            u.username,
            u.display_name,
            u.avatar_emoji,
            COALESCE(SUM(c.co2_impact_kg_year), 0) as score
        FROM users u
        LEFT JOIN user_challenges uc ON uc.user_id = u.id
        LEFT JOIN challenges c ON c.id = uc.challenge_id
        WHERE (
            uc.completed_at IS NULL 
            OR (uc.completed_at >= ? AND uc.completed_at <= ?)
        )
        {region_filter}
        GROUP BY u.id
        HAVING score > 0
        ORDER BY score DESC
        LIMIT ?
        """,
        tuple(params)
    ).fetchall()
    
    rankings = []
    for i, r in enumerate(rankings_data, 1):
        rankings.append(LeaderboardEntry(
            rank=i,
            user=UserBriefResponse(
                id=r['id'],
                username=r['username'],
                display_name=r.get('display_name'),
                avatar_emoji=r.get('avatar_emoji', '🌱')
            ),
            score=r['score'],
            metric="co2_kg"
        ))
    
    # Get current user's rank if authenticated
    my_rank = None
    if current_user_id:
        # Find user's position
        user_score_result = conn.execute(
            """
            SELECT COALESCE(SUM(c.co2_impact_kg), 0) as score
            FROM user_challenges uc
            JOIN challenges c ON c.id = uc.challenge_id
            WHERE uc.user_id = ?
            AND (uc.completed_at >= ? AND uc.completed_at <= ?)
            """,
            (current_user_id, start_date.isoformat(), end_date.isoformat())
        ).fetchone()
        
        user_score = user_score_result['score'] if user_score_result else 0
        
        # Count users above and below
        above = conn.execute(
            f"""
            SELECT COUNT(DISTINCT u.id) as count
            FROM users u
            LEFT JOIN user_challenges uc ON uc.user_id = u.id
            LEFT JOIN challenges c ON c.id = uc.challenge_id
            WHERE (uc.completed_at >= ? AND uc.completed_at <= ?)
            {region_filter}
            GROUP BY u.id
            HAVING SUM(c.co2_impact_kg) > ?
            """,
            (*params[:-1], user_score)
        ).fetchall()
        
        users_above = len(above)
        
        below = conn.execute(
            f"""
            SELECT COUNT(DISTINCT u.id) as count
            FROM users u
            LEFT JOIN user_challenges uc ON uc.user_id = u.id  
            LEFT JOIN challenges c ON c.id = uc.challenge_id
            WHERE (uc.completed_at >= ? AND uc.completed_at <= ?)
            {region_filter}
            GROUP BY u.id
            HAVING SUM(c.co2_impact_kg) < ? AND SUM(c.co2_impact_kg) > 0
            """,
            (*params[:-1], user_score)
        ).fetchall()
        
        users_below = len(below)
        
        my_rank = MyRank(
            rank=users_above + 1,
            score=user_score,
            users_above=users_above,
            users_below=users_below
        )
    
    return LeaderboardResponse(
        period=LeaderboardPeriod(start=start_date, end=end_date),
        rankings=rankings,
        my_rank=my_rank
    )


@router.get("/weekly", response_model=LeaderboardResponse)
def get_weekly_leaderboard(
    limit: int = Query(10, ge=1, le=100),
    current_user: Optional[CurrentUser] = Depends(get_current_user_optional)
):
    """Get weekly CO2 savings leaderboard."""
    start, end = _get_week_dates()
    
    with get_db() as conn:
        return _build_leaderboard(
            conn,
            start,
            end,
            limit,
            current_user.id if current_user else None
        )


@router.get("/monthly", response_model=LeaderboardResponse)
def get_monthly_leaderboard(
    limit: int = Query(10, ge=1, le=100),
    current_user: Optional[CurrentUser] = Depends(get_current_user_optional)
):
    """Get monthly CO2 savings leaderboard."""
    start, end = _get_month_dates()
    
    with get_db() as conn:
        return _build_leaderboard(
            conn,
            start,
            end,
            limit,
            current_user.id if current_user else None
        )


@router.get("/regional/{region}", response_model=LeaderboardResponse)
def get_regional_leaderboard(
    region: str,
    limit: int = Query(10, ge=1, le=100),
    current_user: Optional[CurrentUser] = Depends(get_current_user_optional)
):
    """Get regional CO2 savings leaderboard."""
    start, end = _get_month_dates()  # Monthly for regional
    
    with get_db() as conn:
        return _build_leaderboard(
            conn,
            start,
            end,
            limit,
            current_user.id if current_user else None,
            region=region
        )
