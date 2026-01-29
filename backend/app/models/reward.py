# models/reward.py - Reward/Hardware Package Models
"""
Provolution Gamification - Reward Models
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ShippingAddress(BaseModel):
    """Shipping address for hardware redemptions."""
    name: str = Field(..., max_length=100)
    street: str = Field(..., max_length=200)
    city: str = Field(..., max_length=100)
    postal_code: str = Field(..., max_length=10)
    country: str = Field(default="DE", max_length=2)


class HardwarePackage(BaseModel):
    """Available hardware reward package."""
    id: str
    name: str
    xp_required: int
    estimated_value: float
    contents: List[str]
    in_stock: bool = True
    user_eligible: bool = False
    user_xp_missing: int = 0


class HardwarePackagesResponse(BaseModel):
    """Response listing all available packages."""
    packages: List[HardwarePackage]
    user_total_xp: int


class RedeemRequest(BaseModel):
    """Request to redeem a hardware package."""
    shipping_address: ShippingAddress


class RedemptionInfo(BaseModel):
    """Details of a redemption."""
    id: int
    package_id: str
    status: str = "pending"  # pending, processing, shipped, delivered
    xp_spent: int


class RedeemResponse(BaseModel):
    """Response after redeeming a package."""
    success: bool
    redemption: RedemptionInfo
    user_remaining_xp: int
    message: str
