-- SCHEMA UPDATE: Adjust table/column names for API compatibility
-- Run after initial schema.sql

-- Add missing columns to users if they don't exist
-- SQLite doesn't support IF NOT EXISTS for columns, so this is idempotent via try/fail

-- For users table - add last_active and total_co2_saved_kg
ALTER TABLE users ADD COLUMN last_active TIMESTAMP;
ALTER TABLE users ADD COLUMN total_co2_saved_kg DECIMAL(10,2) DEFAULT 0;

-- For challenges - add missing columns 
ALTER TABLE challenges ADD COLUMN icon VARCHAR(10) DEFAULT '🎯';
ALTER TABLE challenges ADD COLUMN sort_order INTEGER DEFAULT 100;
ALTER TABLE challenges ADD COLUMN co2_impact_kg DECIMAL(10,2);
ALTER TABLE challenges ADD COLUMN savings_euro DECIMAL(10,2);
ALTER TABLE challenges ADD COLUMN verification_options VARCHAR(200);

-- Create daily_logs as alias view or rename
-- If challenge_logs exists, create view
CREATE VIEW IF NOT EXISTS daily_logs AS 
SELECT 
    id,
    user_challenge_id,
    log_date,
    completed,
    notes,
    proof_type,
    proof_url,
    created_at
FROM challenge_logs;

-- Create redemptions table if not exists (different name than hardware_redemptions)
CREATE TABLE IF NOT EXISTS redemptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    package_id VARCHAR(20) REFERENCES hardware_packages(id),
    status VARCHAR(20) DEFAULT 'pending',
    xp_spent INTEGER NOT NULL,
    shipping_name VARCHAR(100),
    shipping_street VARCHAR(200),
    shipping_city VARCHAR(100),
    shipping_postal_code VARCHAR(10),
    shipping_country VARCHAR(2) DEFAULT 'DE',
    tracking_number VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    shipped_at TIMESTAMP,
    delivered_at TIMESTAMP
);

-- Update co2_impact_kg from co2_impact_kg_year if exists
UPDATE challenges 
SET co2_impact_kg = co2_impact_kg_year 
WHERE co2_impact_kg IS NULL AND co2_impact_kg_year IS NOT NULL;

UPDATE challenges
SET savings_euro = savings_euro_year
WHERE savings_euro IS NULL AND savings_euro_year IS NOT NULL;

-- Add stock_count default
UPDATE hardware_packages SET stock_count = 10 WHERE stock_count = 0;
