# routers/footprint.py
"""
Provolution Gamification - Footprint API Router
Endpunkte für CO₂-Fußabdruck-Berechnung und -Verwaltung
"""

from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
from typing import Optional

from ..database import get_db
from ..auth import get_current_user, CurrentUser
from ..models.footprint import (
    FootprintInput, FootprintResult, FootprintSummary
)
from ..services.footprint_calculator import calculator

router = APIRouter(prefix="/footprint", tags=["Footprint"])


# ============================================
# PUBLIC ENDPOINTS (kein Login erforderlich)
# ============================================

@router.post("/calculate", response_model=FootprintResult)
def calculate_footprint_anonymous(data: FootprintInput):
    """
    Berechnet CO₂-Fußabdruck ohne Speicherung (für Gäste).
    Perfekt für den ersten Test des Rechners.
    """
    result = calculator.calculate(data)
    result.profile_complete = False  # Nicht gespeichert
    return result


@router.get("/factors")
def get_emission_factors():
    """
    Gibt alle Emissionsfaktoren zurück (Transparenz).
    """
    return {
        "version": calculator.version,
        "factors": calculator.factors,
        "sources": [
            {"name": "UBA", "url": "https://www.umweltbundesamt.de/themen/klima-energie/energieverbrauch"},
            {"name": "TREMOD", "url": "https://www.ifeu.de/en/methods/models/tremod/"},
            {"name": "ifeu", "url": "https://www.ifeu.de/"},
            {"name": "atmosfair", "url": "https://www.atmosfair.de/de/kompensieren/fliegen/"},
        ],
        "note": "Alle Werte in kg CO₂-Äquivalent. Stand: 2024/2025."
    }


@router.get("/averages")
def get_averages():
    """
    Gibt Vergleichswerte zurück (DE-Durchschnitt, Welt, Paris-Ziel).
    """
    return {
        "germany_average_kg": 10800,
        "world_average_kg": 4800,
        "paris_target_kg": 2000,
        "breakdown_germany": {
            "housing": 2400,
            "mobility": 3200,
            "nutrition": 1800,
            "consumption": 3400,
        },
        "source": "UBA 2024"
    }


# ============================================
# AUTHENTICATED ENDPOINTS (Login erforderlich)
# ============================================

@router.post("/me", response_model=FootprintResult)
def calculate_and_save_footprint(
    data: FootprintInput,
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Berechnet und speichert CO₂-Fußabdruck für eingeloggten User.
    Vervollständigt Challenge ON-1 "Klimaheld-Profil".
    """
    user_id = current_user.id
    
    # 1. Berechnen
    result = calculator.calculate(data)
    
    # 2. In Datenbank speichern/aktualisieren
    now = datetime.utcnow().isoformat()
    
    with get_db() as conn:
        # Prüfen ob bereits vorhanden
        existing = conn.execute(
            "SELECT id FROM user_footprint WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        
        if existing:
            # Update
            conn.execute("""
                UPDATE user_footprint SET
                    housing_type = ?, housing_size_sqm = ?, household_members = ?,
                    heating_type = ?, heating_consumption_kwh = ?, electricity_kwh = ?,
                    green_electricity = ?,
                    has_car = ?, car_fuel_type = ?, car_km_year = ?,
                    car_consumption_l_100km = ?, public_transport_km_year = ?,
                    bike_km_year = ?, flights_short_haul = ?, flights_long_haul = ?,
                    diet_type = ?, regional_seasonal = ?, food_waste_level = ?,
                    shopping_frequency = ?, secondhand_preference = ?, digital_consumption = ?,
                    co2_total_kg_year = ?, co2_housing_kg = ?, co2_mobility_kg = ?,
                    co2_nutrition_kg = ?, co2_consumption_kg = ?,
                    calculation_version = ?, last_calculated = ?, updated_at = ?
                WHERE user_id = ?
            """, (
                data.housing.housing_type, data.housing.housing_size_sqm,
                data.housing.household_members, data.housing.heating_type,
                data.housing.heating_consumption_kwh, data.housing.electricity_kwh,
                data.housing.green_electricity,
                data.mobility.has_car, data.mobility.car_fuel_type,
                data.mobility.car_km_year, data.mobility.car_consumption_l_100km,
                data.mobility.public_transport_km_year, data.mobility.bike_km_year,
                data.mobility.flights_short_haul, data.mobility.flights_long_haul,
                data.nutrition.diet_type, data.nutrition.regional_seasonal,
                data.nutrition.food_waste_level,
                data.consumption.shopping_frequency, data.consumption.secondhand_preference,
                data.consumption.digital_consumption,
                result.total_co2_kg_year, result.breakdown.housing_kg,
                result.breakdown.mobility_kg, result.breakdown.nutrition_kg,
                result.breakdown.consumption_kg,
                result.calculation_version, now, now,
                user_id
            ))
        else:
            # Insert
            conn.execute("""
                INSERT INTO user_footprint (
                    user_id,
                    housing_type, housing_size_sqm, household_members,
                    heating_type, heating_consumption_kwh, electricity_kwh,
                    green_electricity,
                    has_car, car_fuel_type, car_km_year,
                    car_consumption_l_100km, public_transport_km_year,
                    bike_km_year, flights_short_haul, flights_long_haul,
                    diet_type, regional_seasonal, food_waste_level,
                    shopping_frequency, secondhand_preference, digital_consumption,
                    co2_total_kg_year, co2_housing_kg, co2_mobility_kg,
                    co2_nutrition_kg, co2_consumption_kg,
                    calculation_version, last_calculated, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                data.housing.housing_type, data.housing.housing_size_sqm,
                data.housing.household_members, data.housing.heating_type,
                data.housing.heating_consumption_kwh, data.housing.electricity_kwh,
                data.housing.green_electricity,
                data.mobility.has_car, data.mobility.car_fuel_type,
                data.mobility.car_km_year, data.mobility.car_consumption_l_100km,
                data.mobility.public_transport_km_year, data.mobility.bike_km_year,
                data.mobility.flights_short_haul, data.mobility.flights_long_haul,
                data.nutrition.diet_type, data.nutrition.regional_seasonal,
                data.nutrition.food_waste_level,
                data.consumption.shopping_frequency, data.consumption.secondhand_preference,
                data.consumption.digital_consumption,
                result.total_co2_kg_year, result.breakdown.housing_kg,
                result.breakdown.mobility_kg, result.breakdown.nutrition_kg,
                result.breakdown.consumption_kg,
                result.calculation_version, now, now, now
            ))
        
        # 3. In User-Tabelle Baseline aktualisieren
        conn.execute(
            "UPDATE users SET co2_footprint_baseline = ?, updated_at = ? WHERE id = ?",
            (result.total_co2_kg_year, now, user_id)
        )
        
        # 4. History-Eintrag erstellen
        conn.execute("""
            INSERT INTO footprint_history (
                user_id, co2_total_kg_year, co2_housing_kg, co2_mobility_kg,
                co2_nutrition_kg, co2_consumption_kg, trigger_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, result.total_co2_kg_year, result.breakdown.housing_kg,
            result.breakdown.mobility_kg, result.breakdown.nutrition_kg,
            result.breakdown.consumption_kg,
            'initial' if not existing else 'update'
        ))
        
        # 5. Challenge ON-1 automatisch abschließen
        _complete_onboarding_challenge(conn, user_id)
        
        conn.commit()
    
    result.profile_complete = True
    return result


@router.get("/me", response_model=FootprintSummary)
def get_my_footprint(
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Gibt Zusammenfassung des eigenen Footprints zurück.
    """
    user_id = current_user.id
    
    with get_db() as conn:
        row = conn.execute("""
            SELECT co2_total_kg_year, co2_housing_kg, co2_mobility_kg,
                   co2_nutrition_kg, co2_consumption_kg, last_calculated
            FROM user_footprint WHERE user_id = ?
        """, (user_id,)).fetchone()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Noch kein CO₂-Fußabdruck berechnet. Nutze POST /footprint/me"
        )
    
    # Größte Kategorie ermitteln
    categories = {
        'Wohnen': row['co2_housing_kg'] or 0,
        'Mobilität': row['co2_mobility_kg'] or 0,
        'Ernährung': row['co2_nutrition_kg'] or 0,
        'Konsum': row['co2_consumption_kg'] or 0,
    }
    main_category = max(categories, key=categories.get)
    
    total = row['co2_total_kg_year'] or 0
    vs_germany = round((total - 10800) / 10800 * 100, 1)
    sec_score = calculator._calc_sec_score(total)
    
    return FootprintSummary(
        total_co2_kg_year=total,
        main_category=main_category,
        vs_germany_percent=vs_germany,
        last_calculated=row['last_calculated'],
        sec_score=sec_score
    )


@router.get("/me/history")
def get_footprint_history(
    current_user: CurrentUser = Depends(get_current_user),
    limit: int = 10
):
    """
    Gibt Footprint-Verlauf zurück (für Trend-Anzeige).
    """
    user_id = current_user.id
    
    with get_db() as conn:
        rows = conn.execute("""
            SELECT recorded_at, co2_total_kg_year, co2_housing_kg,
                   co2_mobility_kg, co2_nutrition_kg, co2_consumption_kg, trigger_type
            FROM footprint_history
            WHERE user_id = ?
            ORDER BY recorded_at DESC
            LIMIT ?
        """, (user_id, limit)).fetchall()
    
    return [dict(row) for row in rows]


@router.get("/me/full")
def get_full_footprint_data(
    current_user: CurrentUser = Depends(get_current_user)
):
    """
    Gibt vollständige Footprint-Daten zurück (für Bearbeitung).
    """
    user_id = current_user.id
    
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM user_footprint WHERE user_id = ?",
            (user_id,)
        ).fetchone()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Noch kein CO₂-Fußabdruck berechnet"
        )
    
    return dict(row)


# ============================================
# HELPER FUNCTIONS
# ============================================

def _complete_onboarding_challenge(conn, user_id: int):
    """
    Schließt Challenge ON-1 automatisch ab wenn Footprint berechnet.
    """
    # Prüfen ob User Challenge ON-1 hat und sie noch aktiv ist
    challenge = conn.execute("""
        SELECT id, status FROM user_challenges
        WHERE user_id = ? AND challenge_id = 'ON-1' AND status = 'active'
    """, (user_id,)).fetchone()
    
    if challenge:
        now = datetime.utcnow().isoformat()
        
        # Challenge abschließen
        conn.execute("""
            UPDATE user_challenges SET
                status = 'completed',
                completed_at = ?,
                progress_percent = 100,
                verification_status = 'verified',
                verified_at = ?,
                xp_earned = 50
            WHERE id = ?
        """, (now, now, challenge['id']))
        
        # XP gutschreiben
        conn.execute("""
            INSERT INTO xp_transactions (user_id, amount, type, reference_type, reference_id, description)
            VALUES (?, 50, 'challenge', 'challenge', 'ON-1', 'Klimaheld-Profil abgeschlossen')
        """, (user_id,))
        
        # User XP aktualisieren
        conn.execute(
            "UPDATE users SET total_xp = total_xp + 50, updated_at = ? WHERE id = ?",
            (now, user_id)
        )
        
        # Badge vergeben
        existing_badge = conn.execute(
            "SELECT id FROM user_badges WHERE user_id = ? AND badge_id = 'klimaheld_in_spe'",
            (user_id,)
        ).fetchone()
        
        if not existing_badge:
            conn.execute("""
                INSERT INTO user_badges (user_id, badge_id, challenge_id)
                VALUES (?, 'klimaheld_in_spe', 'ON-1')
            """, (user_id,))
