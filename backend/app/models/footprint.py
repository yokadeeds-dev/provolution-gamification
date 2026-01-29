# models/footprint.py - CO₂-Footprint Pydantic Models
"""
Provolution Gamification - CO₂-Footprint Models
Request/Response schemas for footprint calculation
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
from datetime import datetime
from decimal import Decimal


# ============================================
# INPUT MODELS
# ============================================

class FootprintHousingInput(BaseModel):
    """Wohnen/Energie-Daten"""
    housing_type: Literal['apartment', 'house', 'shared'] = 'apartment'
    housing_size_sqm: int = Field(ge=10, le=500, default=80)
    household_members: int = Field(ge=1, le=10, default=2)
    heating_type: Literal['gas', 'oil', 'district', 'heatpump', 'wood', 'electric'] = 'gas'
    heating_consumption_kwh: Optional[int] = Field(None, ge=0, le=50000)
    electricity_kwh: Optional[int] = Field(None, ge=0, le=20000)
    green_electricity: bool = False


class FootprintMobilityInput(BaseModel):
    """Mobilitäts-Daten"""
    has_car: bool = False
    car_fuel_type: Optional[Literal['petrol', 'diesel', 'hybrid', 'electric']] = None
    car_km_year: int = Field(ge=0, le=100000, default=0)
    car_consumption_l_100km: Optional[float] = Field(None, ge=3, le=20)
    public_transport_km_year: int = Field(ge=0, le=50000, default=0)
    bike_km_year: int = Field(ge=0, le=30000, default=0)
    flights_short_haul: int = Field(ge=0, le=50, default=0)  # Anzahl Flüge <1500km
    flights_long_haul: int = Field(ge=0, le=20, default=0)   # Anzahl Flüge >1500km


class FootprintNutritionInput(BaseModel):
    """Ernährungs-Daten"""
    diet_type: Literal['vegan', 'vegetarian', 'flexitarian', 'mixed', 'meat_heavy'] = 'mixed'
    regional_seasonal: bool = False
    food_waste_level: Literal['low', 'medium', 'high'] = 'medium'


class FootprintConsumptionInput(BaseModel):
    """Konsum-Daten"""
    shopping_frequency: Literal['minimal', 'moderate', 'frequent'] = 'moderate'
    secondhand_preference: bool = False
    digital_consumption: Literal['low', 'medium', 'high'] = 'medium'


class FootprintInput(BaseModel):
    """Kompletter Footprint-Input für Berechnung"""
    housing: FootprintHousingInput = FootprintHousingInput()
    mobility: FootprintMobilityInput = FootprintMobilityInput()
    nutrition: FootprintNutritionInput = FootprintNutritionInput()
    consumption: FootprintConsumptionInput = FootprintConsumptionInput()


# ============================================
# OUTPUT MODELS
# ============================================

class FootprintBreakdown(BaseModel):
    """Aufschlüsselung nach Kategorien"""
    housing_kg: float
    mobility_kg: float
    nutrition_kg: float
    consumption_kg: float
    total_kg: float
    
    # Prozentuale Anteile
    housing_percent: float
    mobility_percent: float
    nutrition_percent: float
    consumption_percent: float


class FootprintComparison(BaseModel):
    """Vergleich mit Durchschnittswerten"""
    user_total_kg: float
    germany_average_kg: float = 10800  # DE-Durchschnitt ca. 10,8t/Jahr
    world_average_kg: float = 4800     # Welt-Durchschnitt ca. 4,8t/Jahr
    paris_target_kg: float = 2000      # 2-Tonnen-Ziel (Paris-kompatibel)
    
    vs_germany_percent: float  # +/- % gegenüber DE-Durchschnitt
    vs_world_percent: float
    vs_paris_percent: float


class FootprintRecommendation(BaseModel):
    """Empfehlung zur CO₂-Reduktion"""
    category: str
    action: str
    potential_savings_kg: float
    difficulty: Literal['easy', 'medium', 'hard']
    challenge_id: Optional[str] = None  # Verknüpfung zu passender Challenge


class FootprintResult(BaseModel):
    """Komplettes Ergebnis der Footprint-Berechnung"""
    success: bool = True
    calculation_version: str = "1.0"
    calculated_at: datetime
    
    # Kern-Ergebnisse
    total_co2_kg_year: float
    breakdown: FootprintBreakdown
    comparison: FootprintComparison
    
    # Empfehlungen
    recommendations: list[FootprintRecommendation] = []
    
    # SEC-Score (Provolution-spezifisch)
    sec_score: Optional[float] = None  # 0-10 basierend auf Footprint vs. Ziel
    
    # Für Challenge ON-1
    profile_complete: bool = False
    
    class Config:
        from_attributes = True


class FootprintSummary(BaseModel):
    """Kurze Zusammenfassung für Profil-Anzeige"""
    total_co2_kg_year: float
    main_category: str  # Größter Verursacher
    vs_germany_percent: float
    last_calculated: Optional[datetime] = None
    sec_score: Optional[float] = None


# ============================================
# DATABASE MODELS (for ORM/Response)
# ============================================

class UserFootprintDB(BaseModel):
    """Vollständiger Footprint aus Datenbank"""
    id: int
    user_id: int
    
    # Housing
    housing_type: Optional[str]
    housing_size_sqm: Optional[int]
    household_members: int
    heating_type: Optional[str]
    heating_consumption_kwh: Optional[int]
    electricity_kwh: Optional[int]
    green_electricity: bool
    
    # Mobility
    has_car: bool
    car_fuel_type: Optional[str]
    car_km_year: int
    car_consumption_l_100km: Optional[float]
    public_transport_km_year: int
    bike_km_year: int
    flights_short_haul: int
    flights_long_haul: int
    
    # Nutrition
    diet_type: Optional[str]
    regional_seasonal: bool
    food_waste_level: Optional[str]
    
    # Consumption
    shopping_frequency: Optional[str]
    secondhand_preference: bool
    digital_consumption: Optional[str]
    
    # Calculated
    co2_total_kg_year: Optional[float]
    co2_housing_kg: Optional[float]
    co2_mobility_kg: Optional[float]
    co2_nutrition_kg: Optional[float]
    co2_consumption_kg: Optional[float]
    
    calculation_version: str
    last_calculated: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
