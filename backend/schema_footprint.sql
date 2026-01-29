-- PROVOLUTION CO₂-FOOTPRINT SCHEMA
-- Erweiterung für CO₂-Fußabdruck-Rechner
-- Version: 1.0
-- Erstellt: 2026-01-29

-- ============================================
-- USER FOOTPRINT DATA
-- ============================================

CREATE TABLE IF NOT EXISTS user_footprint (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    
    -- === WOHNEN / ENERGIE ===
    housing_type VARCHAR(20), -- 'apartment', 'house', 'shared'
    housing_size_sqm INTEGER,
    household_members INTEGER DEFAULT 1,
    heating_type VARCHAR(20), -- 'gas', 'oil', 'district', 'heatpump', 'wood', 'electric'
    heating_consumption_kwh INTEGER, -- Jahresverbrauch (optional, sonst Schätzung)
    electricity_kwh INTEGER, -- Jahresverbrauch (optional)
    green_electricity BOOLEAN DEFAULT FALSE,
    
    -- === MOBILITÄT ===
    has_car BOOLEAN DEFAULT FALSE,
    car_fuel_type VARCHAR(20), -- 'petrol', 'diesel', 'hybrid', 'electric', 'none'
    car_km_year INTEGER DEFAULT 0,
    car_consumption_l_100km DECIMAL(4,1), -- Verbrauch (optional)
    public_transport_km_year INTEGER DEFAULT 0,
    bike_km_year INTEGER DEFAULT 0,
    flights_short_haul INTEGER DEFAULT 0, -- <1500km, Hin+Rück = 2
    flights_long_haul INTEGER DEFAULT 0, -- >1500km
    
    -- === ERNÄHRUNG ===
    diet_type VARCHAR(20), -- 'vegan', 'vegetarian', 'flexitarian', 'mixed', 'meat_heavy'
    regional_seasonal BOOLEAN DEFAULT FALSE, -- Bevorzugt regional/saisonal
    food_waste_level VARCHAR(10), -- 'low', 'medium', 'high'
    
    -- === KONSUM ===
    shopping_frequency VARCHAR(10), -- 'minimal', 'moderate', 'frequent'
    secondhand_preference BOOLEAN DEFAULT FALSE,
    digital_consumption VARCHAR(10), -- 'low', 'medium', 'high' (Streaming etc.)
    
    -- === BERECHNETE WERTE ===
    co2_total_kg_year DECIMAL(10,2),
    co2_housing_kg DECIMAL(10,2),
    co2_mobility_kg DECIMAL(10,2),
    co2_nutrition_kg DECIMAL(10,2),
    co2_consumption_kg DECIMAL(10,2),
    
    -- === META ===
    calculation_version VARCHAR(10) DEFAULT '1.0',
    last_calculated TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index für schnellen User-Lookup
CREATE INDEX IF NOT EXISTS idx_user_footprint_user ON user_footprint(user_id);

-- ============================================
-- EMISSION FACTORS (Deutsche Durchschnittswerte)
-- ============================================

CREATE TABLE IF NOT EXISTS emission_factors (
    id VARCHAR(50) PRIMARY KEY,
    category VARCHAR(30) NOT NULL,
    subcategory VARCHAR(50),
    factor_value DECIMAL(10,4) NOT NULL,
    unit VARCHAR(30) NOT NULL,
    source VARCHAR(100),
    valid_from DATE,
    valid_until DATE,
    notes TEXT
);

-- Initiale Emissionsfaktoren (basierend auf UBA/TREMOD/ifeu 2024/2025)
INSERT OR REPLACE INTO emission_factors (id, category, subcategory, factor_value, unit, source, notes) VALUES
-- Heizung (kg CO₂ pro kWh)
('heating_gas', 'housing', 'heating', 0.201, 'kg_co2_per_kwh', 'UBA 2024', 'Erdgas inkl. Vorkette'),
('heating_oil', 'housing', 'heating', 0.266, 'kg_co2_per_kwh', 'UBA 2024', 'Heizöl inkl. Vorkette'),
('heating_district', 'housing', 'heating', 0.183, 'kg_co2_per_kwh', 'UBA 2024', 'Fernwärme DE-Mix'),
('heating_heatpump', 'housing', 'heating', 0.097, 'kg_co2_per_kwh', 'UBA 2024', 'Wärmepumpe mit DE-Strommix'),
('heating_wood', 'housing', 'heating', 0.023, 'kg_co2_per_kwh', 'UBA 2024', 'Holzpellets'),
('heating_electric', 'housing', 'heating', 0.380, 'kg_co2_per_kwh', 'UBA 2024', 'Direktstrom'),

-- Strom (kg CO₂ pro kWh)
('electricity_mix', 'housing', 'electricity', 0.380, 'kg_co2_per_kwh', 'UBA 2024', 'DE-Strommix'),
('electricity_green', 'housing', 'electricity', 0.020, 'kg_co2_per_kwh', 'UBA 2024', 'Ökostrom zertifiziert'),

-- Mobilität Auto (kg CO₂ pro km)
('car_petrol', 'mobility', 'car', 0.152, 'kg_co2_per_km', 'TREMOD 2024', 'Benzin-PKW Durchschnitt'),
('car_diesel', 'mobility', 'car', 0.142, 'kg_co2_per_km', 'TREMOD 2024', 'Diesel-PKW Durchschnitt'),
('car_hybrid', 'mobility', 'car', 0.105, 'kg_co2_per_km', 'TREMOD 2024', 'Hybrid-PKW'),
('car_electric', 'mobility', 'car', 0.053, 'kg_co2_per_km', 'TREMOD 2024', 'E-Auto DE-Strommix'),

-- Mobilität ÖPNV (kg CO₂ pro Personenkilometer)
('public_transport', 'mobility', 'public', 0.055, 'kg_co2_per_pkm', 'TREMOD 2024', 'ÖPNV Durchschnitt DE'),
('train_long', 'mobility', 'train', 0.029, 'kg_co2_per_pkm', 'DB 2024', 'Fernverkehr'),

-- Flüge (kg CO₂ pro Flug, inkl. RFI-Faktor 2.7)
('flight_short', 'mobility', 'flight', 0.380, 'kg_co2_per_km', 'atmosfair 2024', 'Kurzstrecke <1500km inkl. RFI'),
('flight_long', 'mobility', 'flight', 0.280, 'kg_co2_per_km', 'atmosfair 2024', 'Langstrecke >1500km inkl. RFI'),

-- Ernährung (kg CO₂ pro Jahr, Baseline)
('diet_vegan', 'nutrition', 'diet', 940, 'kg_co2_per_year', 'ifeu 2024', 'Vegane Ernährung'),
('diet_vegetarian', 'nutrition', 'diet', 1220, 'kg_co2_per_year', 'ifeu 2024', 'Vegetarisch'),
('diet_flexitarian', 'nutrition', 'diet', 1580, 'kg_co2_per_year', 'ifeu 2024', 'Flexitarisch'),
('diet_mixed', 'nutrition', 'diet', 1760, 'kg_co2_per_year', 'ifeu 2024', 'Mischkost DE-Durchschnitt'),
('diet_meat_heavy', 'nutrition', 'diet', 2400, 'kg_co2_per_year', 'ifeu 2024', 'Fleischlastig'),

-- Konsum (kg CO₂ pro Jahr, Baseline)
('consumption_minimal', 'consumption', 'shopping', 1200, 'kg_co2_per_year', 'UBA 2024', 'Minimaler Konsum'),
('consumption_moderate', 'consumption', 'shopping', 2200, 'kg_co2_per_year', 'UBA 2024', 'Durchschnittlicher Konsum'),
('consumption_frequent', 'consumption', 'shopping', 3500, 'kg_co2_per_year', 'UBA 2024', 'Häufiger Konsum'),

-- Digital (kg CO₂ pro Jahr)
('digital_low', 'consumption', 'digital', 50, 'kg_co2_per_year', 'Borderstep 2024', 'Wenig Streaming'),
('digital_medium', 'consumption', 'digital', 150, 'kg_co2_per_year', 'Borderstep 2024', 'Durchschnitt'),
('digital_high', 'consumption', 'digital', 350, 'kg_co2_per_year', 'Borderstep 2024', 'Intensives Streaming');

-- ============================================
-- FOOTPRINT HISTORY (für Trends)
-- ============================================

CREATE TABLE IF NOT EXISTS footprint_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    co2_total_kg_year DECIMAL(10,2),
    co2_housing_kg DECIMAL(10,2),
    co2_mobility_kg DECIMAL(10,2),
    co2_nutrition_kg DECIMAL(10,2),
    co2_consumption_kg DECIMAL(10,2),
    trigger_type VARCHAR(20) -- 'initial', 'update', 'challenge_complete'
);

CREATE INDEX IF NOT EXISTS idx_footprint_history_user ON footprint_history(user_id);
