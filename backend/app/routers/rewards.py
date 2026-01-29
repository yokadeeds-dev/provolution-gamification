# routers/rewards.py - Hardware Rewards Router
"""
Provolution Gamification - Reward Endpoints
GET /rewards/packages - List available hardware packages
POST /rewards/redeem/{package_id} - Redeem a package
"""

from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime

from ..models import (
    HardwarePackage,
    HardwarePackagesResponse,
    RedeemRequest,
    RedeemResponse,
    RedemptionInfo
)
from ..auth import CurrentUser, get_current_user
from ..database import get_db

router = APIRouter(prefix="/rewards", tags=["Rewards"])


@router.get("/packages", response_model=HardwarePackagesResponse)
def list_packages(current_user: CurrentUser = Depends(get_current_user)):
    """List all available hardware reward packages."""
    with get_db() as conn:
        packages_data = conn.execute(
            """
            SELECT * FROM hardware_packages
            WHERE is_active = 1
            ORDER BY xp_required ASC
            """
        ).fetchall()
        
        user_xp = current_user.total_xp
        
        packages = []
        for p in packages_data:
            # Parse contents (stored as semicolon-separated)
            contents = []
            if p.get('contents'):
                contents = [c.strip() for c in p['contents'].split(';') if c.strip()]
            
            xp_required = p['xp_required']
            user_eligible = user_xp >= xp_required
            xp_missing = max(0, xp_required - user_xp)
            
            packages.append(HardwarePackage(
                id=p['id'],
                name=p['name'],
                xp_required=xp_required,
                estimated_value=p.get('estimated_value', 0),
                contents=contents,
                in_stock=p.get('stock_count', 0) > 0,
                user_eligible=user_eligible,
                user_xp_missing=xp_missing
            ))
        
        return HardwarePackagesResponse(
            packages=packages,
            user_total_xp=user_xp
        )


@router.post("/redeem/{package_id}", response_model=RedeemResponse)
def redeem_package(
    package_id: str,
    request: RedeemRequest,
    current_user: CurrentUser = Depends(get_current_user)
):
    """Redeem a hardware package using XP."""
    with get_db() as conn:
        # Get package
        package = conn.execute(
            "SELECT * FROM hardware_packages WHERE id = ? AND is_active = 1",
            (package_id,)
        ).fetchone()
        
        if not package:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "Paket nicht gefunden"
                    }
                }
            )
        
        # Check stock
        if package.get('stock_count', 0) <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "error": {
                        "code": "OUT_OF_STOCK",
                        "message": "Paket nicht mehr verfügbar"
                    }
                }
            )
        
        # Check XP
        user_xp = current_user.total_xp
        xp_required = package['xp_required']
        
        if user_xp < xp_required:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "success": False,
                    "error": {
                        "code": "INSUFFICIENT_XP",
                        "message": f"Du brauchst {xp_required} XP, hast aber nur {user_xp}",
                        "details": {
                            "required": xp_required,
                            "current": user_xp,
                            "missing": xp_required - user_xp
                        }
                    }
                }
            )
        
        # Create redemption record
        now = datetime.utcnow().isoformat()
        shipping = request.shipping_address
        
        cursor = conn.execute(
            """
            INSERT INTO redemptions (
                user_id, package_id, status, xp_spent,
                shipping_name, shipping_street, shipping_city,
                shipping_postal_code, shipping_country,
                created_at
            ) VALUES (?, ?, 'pending', ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                current_user.id,
                package_id,
                xp_required,
                shipping.name,
                shipping.street,
                shipping.city,
                shipping.postal_code,
                shipping.country,
                now
            )
        )
        
        # Deduct XP
        conn.execute(
            "UPDATE users SET total_xp = total_xp - ? WHERE id = ?",
            (xp_required, current_user.id)
        )
        
        # Decrease stock
        conn.execute(
            "UPDATE hardware_packages SET stock_count = stock_count - 1 WHERE id = ?",
            (package_id,)
        )
        
        remaining_xp = user_xp - xp_required
        
        return RedeemResponse(
            success=True,
            redemption=RedemptionInfo(
                id=cursor.lastrowid,
                package_id=package_id,
                status="pending",
                xp_spent=xp_required
            ),
            user_remaining_xp=remaining_xp,
            message=f"{package['name']} bestellt! Du erhältst eine E-Mail mit Tracking-Info."
        )
