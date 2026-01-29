# routers/challenges.py - Challenge Router
"""
Provolution Gamification - Challenge Endpoints
GET /challenges - List all challenges
GET /challenges/{id} - Get challenge details  
POST /challenges/{id}/join - Join a challenge
POST /challenges/{id}/log - Log daily progress
GET /challenges/{id}/progress - Get user's progress
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import datetime, date
from typing import Optional

from ..models import (
    ChallengeCategory,
    ChallengeDifficulty,
    ChallengeStatus,
    ChallengeBrief,
    ChallengeDetail,
    ChallengeListResponse,
    ChallengeJoinResponse,
    DailyLogRequest,
    DailyLogResponse,
    ChallengeProgressResponse,
    UserChallengeStatus,
    BadgeInfo,
    ImpactInfo,
    VerificationInfo,
    ChallengeStats,
    DailyLog,
    ProgressInfo,
    StreakInfo
)
from ..auth import CurrentUser, get_current_user, get_current_user_optional
from ..database import get_db

router = APIRouter(prefix="/challenges", tags=["Challenges"])


@router.get("", response_model=ChallengeListResponse)
def list_challenges(
    category: Optional[ChallengeCategory] = None,
    status: Optional[str] = Query(None, description="active, completed, all"),
    difficulty: Optional[ChallengeDifficulty] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: Optional[CurrentUser] = Depends(get_current_user_optional)
):
    """
    List all available challenges with optional filters.
    Works both authenticated and anonymous.
    """
    with get_db() as conn:
        # Build query
        where_clauses = ["is_active = 1"]
        params = []
        
        if category:
            where_clauses.append("category = ?")
            params.append(category.value)
        
        if difficulty:
            where_clauses.append("difficulty = ?")
            params.append(difficulty.value)
        
        where_sql = " AND ".join(where_clauses)
        
        # Get total count
        count_result = conn.execute(
            f"SELECT COUNT(*) as total FROM challenges WHERE {where_sql}",
            tuple(params)
        ).fetchone()
        total = count_result['total'] if count_result else 0
        
        # Get challenges
        params.extend([limit, offset])
        challenges_data = conn.execute(
            f"""
            SELECT * FROM challenges 
            WHERE {where_sql}
            ORDER BY sort_order, id
            LIMIT ? OFFSET ?
            """,
            tuple(params)
        ).fetchall()
        
        challenges = []
        for c in challenges_data:
            # Get participant count
            participants = conn.execute(
                "SELECT COUNT(*) as count FROM user_challenges WHERE challenge_id = ?",
                (c['id'],)
            ).fetchone()
            
            # Check user status if authenticated
            user_status = None
            if current_user:
                uc = conn.execute(
                    """
                    SELECT status FROM user_challenges 
                    WHERE user_id = ? AND challenge_id = ?
                    """,
                    (current_user.id, c['id'])
                ).fetchone()
                if uc:
                    user_status = uc['status']
            
            # Apply status filter if provided
            if status == "active" and user_status != "active":
                continue
            if status == "completed" and user_status != "completed":
                continue
            
            challenges.append(ChallengeBrief(
                id=c['id'],
                name=c['name'],
                name_emoji=c.get('name_emoji') or f"🎯 {c['name']}",
                description=c['description'],
                category=c['category'],
                difficulty=c['difficulty'],
                duration_days=c['duration_days'],
                xp_reward=c['xp_reward'],
                badge=BadgeInfo(
                    name=c.get('badge_name', ''),
                    icon=c.get('badge_icon', '🏅'),
                    tier=c.get('badge_tier', 'bronze')
                ) if c.get('badge_name') else None,
                impact=ImpactInfo(
                    co2_kg_year=c.get('co2_impact_kg_year') or 0,
                    savings_euro_year=c.get('savings_euro_year'),
                    type=c.get('impact_type', 'direct')
                ),
                participants_count=participants['count'] if participants else 0,
                user_status=user_status
            ))
        
        return ChallengeListResponse(
            challenges=challenges,
            total=total,
            offset=offset,
            limit=limit
        )


@router.get("/{challenge_id}", response_model=ChallengeDetail)
def get_challenge(
    challenge_id: str,
    current_user: Optional[CurrentUser] = Depends(get_current_user_optional)
):
    """Get detailed information about a specific challenge."""
    with get_db() as conn:
        c = conn.execute(
            "SELECT * FROM challenges WHERE id = ?",
            (challenge_id,)
        ).fetchone()
        
        if not c:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "Challenge nicht gefunden"
                    }
                }
            )
        
        # Get stats
        stats_data = conn.execute(
            """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
            FROM user_challenges WHERE challenge_id = ?
            """,
            (challenge_id,)
        ).fetchone()
        
        completion_rate = 0.0
        if stats_data and stats_data['total'] > 0:
            completion_rate = stats_data['completed'] / stats_data['total']
        
        # Parse success criteria (stored as JSON or semicolon-separated)
        criteria = c.get('success_criteria', '')
        if criteria:
            success_criteria = [s.strip() for s in criteria.split(';') if s.strip()]
        else:
            success_criteria = []
        
        # Parse verification options
        verification_options = []
        if c.get('verification_options'):
            verification_options = [v.strip() for v in c['verification_options'].split(',')]
        
        return ChallengeDetail(
            id=c['id'],
            name=c['name'],
            name_emoji=c.get('name_emoji') or f"🎯 {c['name']}",
            description=c['description'],
            description_long=c.get('description_long'),
            category=c['category'],
            difficulty=c['difficulty'],
            duration_days=c['duration_days'],
            xp_reward=c['xp_reward'],
            success_criteria=success_criteria,
            verification=VerificationInfo(
                method=c.get('verification_method', 'self_report'),
                type=c.get('verification_type', 'self_report'),
                options=verification_options if verification_options else None
            ),
            badge=BadgeInfo(
                name=c.get('badge_name', ''),
                icon=c.get('badge_icon', '🏅'),
                tier=c.get('badge_tier', 'bronze')
            ) if c.get('badge_name') else None,
            impact=ImpactInfo(
                co2_kg_year=c.get('co2_impact_kg_year') or 0,
                savings_euro_year=c.get('savings_euro_year'),
                type=c.get('impact_type', 'direct')
            ),
            participants_count=stats_data['total'] if stats_data else 0,
            user_status=None,
            stats=ChallengeStats(
                participants_active=stats_data['active'] if stats_data else 0,
                participants_completed=stats_data['completed'] if stats_data else 0,
                completion_rate=round(completion_rate, 2)
            )
        )


@router.post("/{challenge_id}/join", response_model=ChallengeJoinResponse)
def join_challenge(
    challenge_id: str,
    current_user: CurrentUser = Depends(get_current_user)
):
    """Join a challenge. Requires authentication."""
    with get_db() as conn:
        # Check challenge exists
        challenge = conn.execute(
            "SELECT * FROM challenges WHERE id = ? AND is_active = 1",
            (challenge_id,)
        ).fetchone()
        
        if not challenge:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "Challenge nicht gefunden"
                    }
                }
            )
        
        # Check not already joined
        existing = conn.execute(
            """
            SELECT id, status FROM user_challenges 
            WHERE user_id = ? AND challenge_id = ?
            """,
            (current_user.id, challenge_id)
        ).fetchone()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "success": False,
                    "error": {
                        "code": "CHALLENGE_ALREADY_JOINED",
                        "message": "Du nimmst bereits an dieser Challenge teil.",
                        "details": {
                            "challenge_id": challenge_id,
                            "user_challenge_id": existing['id']
                        }
                    }
                }
            )
        
        # Join challenge
        now = datetime.utcnow().isoformat()
        cursor = conn.execute(
            """
            INSERT INTO user_challenges (
                user_id, challenge_id, status, started_at, progress_percent
            ) VALUES (?, ?, 'active', ?, 0)
            """,
            (current_user.id, challenge_id, now)
        )
        
        return ChallengeJoinResponse(
            success=True,
            user_challenge=UserChallengeStatus(
                id=cursor.lastrowid,
                challenge_id=challenge_id,
                status=ChallengeStatus.ACTIVE,
                started_at=datetime.fromisoformat(now),
                progress_percent=0,
                days_completed=0
            ),
            message=f"Challenge gestartet! Viel Erfolg beim {challenge['name']}!"
        )


@router.post("/{challenge_id}/log", response_model=DailyLogResponse)
def log_daily_progress(
    challenge_id: str,
    request: DailyLogRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """Log daily progress for a challenge."""
    with get_db() as conn:
        # Get user challenge
        uc = conn.execute(
            """
            SELECT uc.*, c.duration_days, c.xp_reward, c.name
            FROM user_challenges uc
            JOIN challenges c ON c.id = uc.challenge_id
            WHERE uc.user_id = ? AND uc.challenge_id = ? AND uc.status = 'active'
            """,
            (current_user.id, challenge_id)
        ).fetchone()
        
        if not uc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "Aktive Challenge nicht gefunden"
                    }
                }
            )
        
        # Check if already logged today
        existing_log = conn.execute(
            """
            SELECT id FROM challenge_logs 
            WHERE user_challenge_id = ? AND log_date = ?
            """,
            (uc['id'], request.log_date.isoformat())
        ).fetchone()
        
        if existing_log:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "success": False,
                    "error": {
                        "code": "ALREADY_LOGGED",
                        "message": "Heute wurde bereits geloggt"
                    }
                }
            )
        
        # Insert log
        cursor = conn.execute(
            """
            INSERT INTO challenge_logs (
                user_challenge_id, log_date, completed, notes, 
                proof_type, proof_url, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                uc['id'],
                request.log_date.isoformat(),
                request.completed,
                request.notes,
                request.proof_type,
                request.proof_url,
                datetime.utcnow().isoformat()
            )
        )
        
        # Count completed days
        completed_days = conn.execute(
            """
            SELECT COUNT(*) as count FROM challenge_logs 
            WHERE user_challenge_id = ? AND completed = 1
            """,
            (uc['id'],)
        ).fetchone()['count']
        
        days_remaining = uc['duration_days'] - completed_days
        progress_percent = int((completed_days / uc['duration_days']) * 100)
        
        # Update user_challenge progress
        conn.execute(
            """
            UPDATE user_challenges 
            SET progress_percent = ?, days_completed = ?
            WHERE id = ?
            """,
            (progress_percent, completed_days, uc['id'])
        )
        
        # Check if challenge completed
        xp_earned = 0
        if completed_days >= uc['duration_days']:
            conn.execute(
                """
                UPDATE user_challenges 
                SET status = 'completed', completed_at = ?
                WHERE id = ?
                """,
                (datetime.utcnow().isoformat(), uc['id'])
            )
            
            # Award XP
            xp_earned = uc['xp_reward']
            conn.execute(
                "UPDATE users SET total_xp = total_xp + ? WHERE id = ?",
                (xp_earned, current_user.id)
            )
        
        # Update streak (simplified)
        user = conn.execute(
            "SELECT streak_days FROM users WHERE id = ?",
            (current_user.id,)
        ).fetchone()
        current_streak = user['streak_days'] if user else 0
        
        return DailyLogResponse(
            success=True,
            log=DailyLog(
                id=cursor.lastrowid,
                log_date=request.log_date,
                completed=request.completed,
                notes=request.notes,
                proof_url=request.proof_url
            ),
            progress=ProgressInfo(
                days_completed=completed_days,
                days_remaining=max(0, days_remaining),
                progress_percent=min(100, progress_percent)
            ),
            xp_earned=xp_earned,
            streak=StreakInfo(
                current=current_streak + 1 if request.completed else current_streak,
                bonus_at_30_days=500
            )
        )


@router.get("/{challenge_id}/progress", response_model=ChallengeProgressResponse)
def get_challenge_progress(
    challenge_id: str,
    current_user: CurrentUser = Depends(get_current_user)
):
    """Get user's progress on a specific challenge."""
    with get_db() as conn:
        uc = conn.execute(
            """
            SELECT uc.*, c.duration_days
            FROM user_challenges uc
            JOIN challenges c ON c.id = uc.challenge_id
            WHERE uc.user_id = ? AND uc.challenge_id = ?
            """,
            (current_user.id, challenge_id)
        ).fetchone()
        
        if not uc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "Du nimmst nicht an dieser Challenge teil"
                    }
                }
            )
        
        # Get all logs
        logs_data = conn.execute(
            """
            SELECT * FROM challenge_logs 
            WHERE user_challenge_id = ?
            ORDER BY log_date DESC
            """,
            (uc['id'],)
        ).fetchall()
        
        logs = [
            DailyLog(
                id=log['id'],
                log_date=date.fromisoformat(log['log_date']),
                completed=log['completed'],
                notes=log.get('notes'),
                proof_url=log.get('proof_url')
            )
            for log in logs_data
        ]
        
        days_completed = sum(1 for log in logs if log.completed)
        days_remaining = max(0, uc['duration_days'] - days_completed)
        
        return ChallengeProgressResponse(
            challenge_id=challenge_id,
            status=uc['status'],
            started_at=datetime.fromisoformat(uc['started_at']),
            days_completed=days_completed,
            days_remaining=days_remaining,
            progress_percent=uc['progress_percent'],
            logs=logs,
            verification_status=uc.get('verification_status', 'pending')
        )
