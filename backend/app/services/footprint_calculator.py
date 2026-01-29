# services/footprint_calculator.py
"""
Provolution CO₂-Footprint Calculator
Berechnet persönlichen CO₂-Fußabdruck basierend auf UBA/TREMOD/ifeu Faktoren
"""

from datetime import datetime
from typing import Optional
from ..models.footprint import (
    FootprintInput, FootprintResult, FootprintBreakdown,
    FootprintComparison, FootprintRecommendation
)


# ============================================
# EMISSIONSFAKTOREN (kg CO₂)
# Basierend auf UBA/TREMOD/ifeu 2024
# ============================================

EMISSION_FACTORS = {
    # Heizung (kg CO₂ pro kWh)
    'heating': {
        'gas': 0.201,
        'oil': 0.266,
        'district': 0.183,
        'heatpump': 0.097,
        'wood': 0.023,
        'electric': 0.380,
    },
    # Strom (kg CO₂ pro kWh)
    'electricity': {
        'mix': 0.380,
        'green': 0.020,
    },
    # Auto (kg CO₂ pro km)
    'car': {
        'petrol': 0.152,
        'diesel': 0.142,
        'hybrid': 0.105,
        'electric': 0.053,
    },
    # ÖPNV (kg CO₂ pro km)
    'public_transport': 0.055,
    # Flüge (kg CO₂ pro Flug, Durchschnittsdistanz * Faktor inkl. RFI)
    'flight': {
        'short': 750 * 0.380,   # ~285 kg pro Kurzstreckenflug
        'long': 6000 * 0.280,   # ~1680 kg pro Langstreckenflug
    },
    # Ernährung (kg CO₂ pro Jahr)
    'diet': {
        'vegan': 940,
        'vegetarian': 1220,
        'flexitarian': 1580,
        'mixed': 1760,
        'meat_heavy': 2400,
    },
    # Konsum (kg CO₂ pro Jahr)
    'consumption': {
        'minimal': 1200,
        'moderate': 2200,
        'frequent': 3500,
    },
    # Digital (kg CO₂ pro Jahr)
    'digital': {
        'low': 50,
        'medium': 150,
        'high': 350,
    },
}

# Durchschnittswerte für Schätzungen
DEFAULTS = {
    'heating_kwh_per_sqm': 120,  # kWh/m²/Jahr für Heizung
    'electricity_kwh_per_person': 1300,  # kWh/Person/Jahr
}


class FootprintCalculator:
    """CO₂-Fußabdruck-Rechner"""
    
    def __init__(self):
        self.factors = EMISSION_FACTORS
        self.version = "1.0"
    
    def calculate(self, data: FootprintInput) -> FootprintResult:
        """Berechnet den kompletten CO₂-Fußabdruck"""
        
        # 1. Einzelne Kategorien berechnen
        housing_kg = self._calc_housing(data.housing)
        mobility_kg = self._calc_mobility(data.mobility)
        nutrition_kg = self._calc_nutrition(data.nutrition)
        consumption_kg = self._calc_consumption(data.consumption)
        
        total_kg = housing_kg + mobility_kg + nutrition_kg + consumption_kg
        
        # 2. Breakdown erstellen
        breakdown = FootprintBreakdown(
            housing_kg=round(housing_kg, 1),
            mobility_kg=round(mobility_kg, 1),
            nutrition_kg=round(nutrition_kg, 1),
            consumption_kg=round(consumption_kg, 1),
            total_kg=round(total_kg, 1),
            housing_percent=round(housing_kg / total_kg * 100, 1) if total_kg > 0 else 0,
            mobility_percent=round(mobility_kg / total_kg * 100, 1) if total_kg > 0 else 0,
            nutrition_percent=round(nutrition_kg / total_kg * 100, 1) if total_kg > 0 else 0,
            consumption_percent=round(consumption_kg / total_kg * 100, 1) if total_kg > 0 else 0,
        )
        
        # 3. Vergleich mit Durchschnittswerten
        comparison = self._calc_comparison(total_kg)
        
        # 4. Empfehlungen generieren
        recommendations = self._generate_recommendations(data, breakdown)
        
        # 5. SEC-Score berechnen (Provolution-spezifisch)
        sec_score = self._calc_sec_score(total_kg)
        
        return FootprintResult(
            success=True,
            calculation_version=self.version,
            calculated_at=datetime.utcnow(),
            total_co2_kg_year=round(total_kg, 1),
            breakdown=breakdown,
            comparison=comparison,
            recommendations=recommendations[:5],  # Top 5 Empfehlungen
            sec_score=sec_score,
            profile_complete=True,
        )
    
    def _calc_housing(self, h) -> float:
        """Berechnet CO₂ für Wohnen/Energie"""
        co2 = 0.0
        
        # Heizung
        if h.heating_consumption_kwh:
            heating_kwh = h.heating_consumption_kwh
        else:
            # Schätzung basierend auf Wohnfläche
            heating_kwh = h.housing_size_sqm * DEFAULTS['heating_kwh_per_sqm']
        
        # Pro Kopf teilen
        heating_kwh_per_person = heating_kwh / h.household_members
        heating_factor = self.factors['heating'].get(h.heating_type, 0.201)
        co2 += heating_kwh_per_person * heating_factor
        
        # Strom
        if h.electricity_kwh:
            electricity_kwh = h.electricity_kwh / h.household_members
        else:
            electricity_kwh = DEFAULTS['electricity_kwh_per_person']
        
        elec_factor = self.factors['electricity']['green' if h.green_electricity else 'mix']
        co2 += electricity_kwh * elec_factor
        
        return co2
    
    def _calc_mobility(self, m) -> float:
        """Berechnet CO₂ für Mobilität"""
        co2 = 0.0
        
        # Auto
        if m.has_car and m.car_fuel_type and m.car_km_year > 0:
            car_factor = self.factors['car'].get(m.car_fuel_type, 0.152)
            co2 += m.car_km_year * car_factor
        
        # ÖPNV
        co2 += m.public_transport_km_year * self.factors['public_transport']
        
        # Fahrrad = 0 CO₂ (aber gut für Empfehlungen)
        
        # Flüge
        co2 += m.flights_short_haul * self.factors['flight']['short']
        co2 += m.flights_long_haul * self.factors['flight']['long']
        
        return co2
    
    def _calc_nutrition(self, n) -> float:
        """Berechnet CO₂ für Ernährung"""
        base_co2 = self.factors['diet'].get(n.diet_type, 1760)
        
        # Bonus für regional/saisonal (-10%)
        if n.regional_seasonal:
            base_co2 *= 0.90
        
        # Malus für Food Waste
        waste_multiplier = {
            'low': 0.95,
            'medium': 1.0,
            'high': 1.10,
        }
        base_co2 *= waste_multiplier.get(n.food_waste_level, 1.0)
        
        return base_co2
    
    def _calc_consumption(self, c) -> float:
        """Berechnet CO₂ für Konsum"""
        base_co2 = self.factors['consumption'].get(c.shopping_frequency, 2200)
        
        # Bonus für Secondhand (-15%)
        if c.secondhand_preference:
            base_co2 *= 0.85
        
        # Digital
        digital_co2 = self.factors['digital'].get(c.digital_consumption, 150)
        
        return base_co2 + digital_co2
    
    def _calc_comparison(self, total_kg: float) -> FootprintComparison:
        """Vergleicht mit Durchschnittswerten"""
        germany_avg = 10800  # kg CO₂/Jahr
        world_avg = 4800
        paris_target = 2000
        
        return FootprintComparison(
            user_total_kg=round(total_kg, 1),
            germany_average_kg=germany_avg,
            world_average_kg=world_avg,
            paris_target_kg=paris_target,
            vs_germany_percent=round((total_kg - germany_avg) / germany_avg * 100, 1),
            vs_world_percent=round((total_kg - world_avg) / world_avg * 100, 1),
            vs_paris_percent=round((total_kg - paris_target) / paris_target * 100, 1),
        )
    
    def _calc_sec_score(self, total_kg: float) -> float:
        """
        Berechnet SEC-Score (0-10) basierend auf Footprint
        10 = Paris-kompatibel (≤2t), 0 = >15t
        """
        if total_kg <= 2000:
            return 10.0
        elif total_kg >= 15000:
            return 0.0
        else:
            # Lineare Interpolation zwischen 2t (10) und 15t (0)
            score = 10 - (total_kg - 2000) / (15000 - 2000) * 10
            return round(max(0, min(10, score)), 1)
    
    def _generate_recommendations(self, data: FootprintInput, breakdown: FootprintBreakdown) -> list[FootprintRecommendation]:
        """Generiert personalisierte Empfehlungen"""
        recs = []
        
        # Mobilität: Flüge reduzieren
        if data.mobility.flights_long_haul > 0:
            savings = data.mobility.flights_long_haul * self.factors['flight']['long'] * 0.5
            recs.append(FootprintRecommendation(
                category="mobility",
                action="Langstreckenflüge halbieren oder durch Bahn ersetzen",
                potential_savings_kg=round(savings, 0),
                difficulty="hard",
                challenge_id="MO-3"
            ))
        
        if data.mobility.flights_short_haul > 2:
            savings = (data.mobility.flights_short_haul - 2) * self.factors['flight']['short']
            recs.append(FootprintRecommendation(
                category="mobility",
                action="Kurzstreckenflüge durch Bahn ersetzen",
                potential_savings_kg=round(savings, 0),
                difficulty="medium",
                challenge_id="MO-2"
            ))
        
        # Mobilität: Auto
        if data.mobility.has_car and data.mobility.car_km_year > 5000:
            if data.mobility.car_fuel_type in ['petrol', 'diesel']:
                savings = data.mobility.car_km_year * 0.3 * (
                    self.factors['car'][data.mobility.car_fuel_type] - self.factors['public_transport']
                )
                recs.append(FootprintRecommendation(
                    category="mobility",
                    action="30% der Autofahrten durch ÖPNV/Fahrrad ersetzen",
                    potential_savings_kg=round(savings, 0),
                    difficulty="medium",
                    challenge_id="MO-1"
                ))
        
        # Energie: Ökostrom
        if not data.housing.green_electricity:
            elec_kwh = data.housing.electricity_kwh or DEFAULTS['electricity_kwh_per_person']
            savings = elec_kwh * (self.factors['electricity']['mix'] - self.factors['electricity']['green'])
            recs.append(FootprintRecommendation(
                category="housing",
                action="Zu Ökostrom wechseln",
                potential_savings_kg=round(savings, 0),
                difficulty="easy",
                challenge_id="EN-1"
            ))
        
        # Energie: Heizung optimieren
        if data.housing.heating_type in ['oil', 'electric']:
            recs.append(FootprintRecommendation(
                category="housing",
                action="Heizung auf Wärmepumpe oder Fernwärme umstellen",
                potential_savings_kg=round(breakdown.housing_kg * 0.4, 0),
                difficulty="hard",
                challenge_id="EN-2"
            ))
        
        # Ernährung
        if data.nutrition.diet_type in ['mixed', 'meat_heavy']:
            current = self.factors['diet'][data.nutrition.diet_type]
            target = self.factors['diet']['flexitarian']
            recs.append(FootprintRecommendation(
                category="nutrition",
                action="Fleischkonsum reduzieren (flexitarisch)",
                potential_savings_kg=round(current - target, 0),
                difficulty="medium",
                challenge_id=None
            ))
        
        # Regional/Saisonal
        if not data.nutrition.regional_seasonal:
            recs.append(FootprintRecommendation(
                category="nutrition",
                action="Mehr regionale und saisonale Produkte kaufen",
                potential_savings_kg=round(breakdown.nutrition_kg * 0.1, 0),
                difficulty="easy",
                challenge_id=None
            ))
        
        # Konsum
        if data.consumption.shopping_frequency == 'frequent':
            savings = self.factors['consumption']['frequent'] - self.factors['consumption']['moderate']
            recs.append(FootprintRecommendation(
                category="consumption",
                action="Bewusster konsumieren, weniger Neukäufe",
                potential_savings_kg=round(savings, 0),
                difficulty="medium",
                challenge_id=None
            ))
        
        if not data.consumption.secondhand_preference:
            recs.append(FootprintRecommendation(
                category="consumption",
                action="Secondhand-Produkte bevorzugen",
                potential_savings_kg=round(breakdown.consumption_kg * 0.15, 0),
                difficulty="easy",
                challenge_id=None
            ))
        
        # Sortieren nach Einsparpotenzial
        recs.sort(key=lambda x: x.potential_savings_kg, reverse=True)
        
        return recs


# Singleton-Instanz
calculator = FootprintCalculator()
