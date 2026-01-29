-- PROVOLUTION GAMIFICATION DATABASE SCHEMA
-- SQLite / PostgreSQL kompatibel
-- Version: 1.0
-- Erstellt: 2026-01-28

-- ============================================
-- USERS & AUTHENTICATION
-- ============================================

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    display_name VARCHAR(100),
    avatar_emoji VARCHAR(10) DEFAULT '🌱',
    
    -- Gamification Stats
    total_xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    trust_level INTEGER DEFAULT 1,
    streak_days INTEGER DEFAULT 0,
    streak_last_activity DATE,
    
    -- Profile
    region VARCHAR(50),
    postal_code VARCHAR(10),
    co2_footprint_baseline DECIMAL(10,2),
    focus_track VARCHAR(50), -- 'mobility', 'energy', 'food', 'consumption', 'politics'
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    
    -- Referral
    referral_code VARCHAR(20) UNIQUE,
    referred_by INTEGER REFERENCES users(id)
);

-- ============================================
-- CHALLENGES
-- ============================================

CREATE TABLE challenges (
    id VARCHAR(10) PRIMARY KEY, -- z.B. 'EN-1', 'MO-2'
    category VARCHAR(50) NOT NULL, -- 'onboarding', 'energie', 'mobilitaet', 'community', 'politik'
    name VARCHAR(100) NOT NULL,
    name_emoji VARCHAR(150),
    description TEXT,
    description_long TEXT,
    
    -- Difficulty & Rewards
    duration_days INTEGER NOT NULL,
    xp_reward INTEGER NOT NULL,
    difficulty VARCHAR(20), -- 'easy', 'medium', 'hard', 'expert'
    
    -- Success Criteria (JSON)
    success_criteria JSON,
    
    -- Verification
    verification_method VARCHAR(50), -- 'automatic', 'self_report', 'photo_proof', 'community_review'
    verification_type VARCHAR(50),
    auto_verify BOOLEAN DEFAULT FALSE,
    spot_check_rate DECIMAL(3,2) DEFAULT 0.1,
    
    -- Badge
    badge_name VARCHAR(100),
    badge_icon VARCHAR(10),
    badge_tier VARCHAR(20), -- 'bronze', 'silver', 'gold', 'platinum'
    
    -- Impact
    co2_impact_kg_year DECIMAL(10,2),
    savings_euro_year DECIMAL(10,2),
    impact_type VARCHAR(50), -- 'direct', 'indirect', 'systemic', 'multiplier'
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_featured BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- USER CHALLENGES (Participation)
-- ============================================

CREATE TABLE user_challenges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    challenge_id VARCHAR(10) REFERENCES challenges(id),
    
    -- Status
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'completed', 'failed', 'abandoned'
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Progress
    progress_percent INTEGER DEFAULT 0,
    days_completed INTEGER DEFAULT 0,
    
    -- Verification
    verification_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'verified', 'rejected', 'spot_check'
    verified_at TIMESTAMP,
    verified_by INTEGER REFERENCES users(id),
    
    -- XP awarded
    xp_earned INTEGER DEFAULT 0,
    
    UNIQUE(user_id, challenge_id, started_at)
);

-- ============================================
-- CHALLENGE LOGS (Daily Progress)
-- ============================================

CREATE TABLE challenge_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_challenge_id INTEGER REFERENCES user_challenges(id) ON DELETE CASCADE,
    
    log_date DATE NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    notes TEXT,
    
    -- Proof
    proof_type VARCHAR(50), -- 'photo', 'screenshot', 'api_data', 'self_report'
    proof_url VARCHAR(500),
    proof_data JSON,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_challenge_id, log_date)
);

-- ============================================
-- BADGES
-- ============================================

CREATE TABLE badges (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    icon VARCHAR(10),
    tier VARCHAR(20), -- 'bronze', 'silver', 'gold', 'platinum'
    category VARCHAR(50), -- 'onboarding', 'habit', 'impact', 'community', 'politik'
    
    -- Requirements (JSON)
    requirements JSON,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_badges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    badge_id VARCHAR(50) REFERENCES badges(id),
    
    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    challenge_id VARCHAR(10) REFERENCES challenges(id), -- Which challenge earned this badge
    
    UNIQUE(user_id, badge_id)
);

-- ============================================
-- XP TRANSACTIONS
-- ============================================

CREATE TABLE xp_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    
    amount INTEGER NOT NULL,
    type VARCHAR(50) NOT NULL, -- 'challenge', 'streak', 'referral', 'bonus', 'first_time', 'social'
    
    -- Reference
    reference_type VARCHAR(50), -- 'challenge', 'badge', 'referral', 'streak'
    reference_id VARCHAR(50),
    
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- LEADERBOARDS
-- ============================================

CREATE TABLE leaderboard_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    leaderboard_type VARCHAR(50) NOT NULL, -- 'weekly_xp', 'monthly_co2', 'lifetime_xp', 'regional'
    period_start DATE,
    period_end DATE,
    region VARCHAR(50), -- For regional leaderboards
    
    -- Snapshot Data (JSON array of {rank, user_id, score})
    rankings JSON,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- TEAMS
-- ============================================

CREATE TABLE teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    
    -- Team Stats
    total_xp INTEGER DEFAULT 0,
    total_co2_saved DECIMAL(10,2) DEFAULT 0,
    member_count INTEGER DEFAULT 0,
    
    -- Creator
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE team_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id INTEGER REFERENCES teams(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    
    role VARCHAR(20) DEFAULT 'member', -- 'captain', 'member'
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(team_id, user_id)
);

-- ============================================
-- REFERRALS
-- ============================================

CREATE TABLE referrals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    referrer_id INTEGER REFERENCES users(id),
    referred_id INTEGER REFERENCES users(id),
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'completed', 'expired'
    completed_at TIMESTAMP,
    
    -- XP
    referrer_xp_earned INTEGER DEFAULT 0,
    referred_xp_earned INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(referred_id)
);

-- ============================================
-- HARDWARE REWARDS
-- ============================================

CREATE TABLE hardware_packages (
    id VARCHAR(20) PRIMARY KEY, -- 'bronze', 'silver', 'gold'
    name VARCHAR(100) NOT NULL,
    description TEXT,
    
    xp_required INTEGER NOT NULL,
    estimated_value DECIMAL(10,2),
    
    -- Contents (JSON array)
    contents JSON,
    
    is_active BOOLEAN DEFAULT TRUE,
    stock_count INTEGER DEFAULT 0
);

CREATE TABLE hardware_redemptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER REFERENCES users(id),
    package_id VARCHAR(20) REFERENCES hardware_packages(id),
    
    -- Status
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'processing', 'shipped', 'delivered', 'cancelled'
    
    -- Shipping
    shipping_address JSON,
    tracking_number VARCHAR(100),
    
    -- XP deducted
    xp_spent INTEGER NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    shipped_at TIMESTAMP,
    delivered_at TIMESTAMP
);

-- ============================================
-- INDEXES
-- ============================================

CREATE INDEX idx_users_total_xp ON users(total_xp DESC);
CREATE INDEX idx_users_region ON users(region);
CREATE INDEX idx_users_referral_code ON users(referral_code);

CREATE INDEX idx_user_challenges_user ON user_challenges(user_id);
CREATE INDEX idx_user_challenges_status ON user_challenges(status);

CREATE INDEX idx_xp_transactions_user ON xp_transactions(user_id);
CREATE INDEX idx_xp_transactions_created ON xp_transactions(created_at);

CREATE INDEX idx_challenge_logs_date ON challenge_logs(log_date);

-- ============================================
-- VIEWS
-- ============================================

-- User Stats View
CREATE VIEW user_stats AS
SELECT 
    u.id,
    u.username,
    u.display_name,
    u.total_xp,
    u.level,
    u.streak_days,
    COUNT(DISTINCT uc.id) FILTER (WHERE uc.status = 'completed') as challenges_completed,
    COALESCE(SUM(c.co2_impact_kg_year) FILTER (WHERE uc.status = 'completed'), 0) as total_co2_saved,
    COUNT(DISTINCT ub.badge_id) as badges_earned
FROM users u
LEFT JOIN user_challenges uc ON u.id = uc.user_id
LEFT JOIN challenges c ON uc.challenge_id = c.id
LEFT JOIN user_badges ub ON u.id = ub.user_id
GROUP BY u.id;

-- Weekly Leaderboard View
CREATE VIEW weekly_leaderboard AS
SELECT 
    u.id,
    u.username,
    u.display_name,
    u.avatar_emoji,
    SUM(xt.amount) as weekly_xp
FROM users u
JOIN xp_transactions xt ON u.id = xt.user_id
WHERE xt.created_at >= date('now', '-7 days')
GROUP BY u.id
ORDER BY weekly_xp DESC
LIMIT 100;

-- ============================================
-- INITIAL DATA
-- ============================================

-- Insert Hardware Packages
INSERT INTO hardware_packages (id, name, description, xp_required, estimated_value, contents) VALUES
('bronze', 'Bronze-Paket', 'Starter-Kit für Energiesparer', 50000, 50.00, 
 '["Smart Plug mit Verbrauchsmessung", "LED-Sparlampen-Set (5 Stück)", "Wasserspar-Duschkopf"]'),
('silver', 'Silber-Paket', 'Fortgeschrittenes Energie-Monitoring', 150000, 150.00,
 '["Smart Thermostat", "Energiemessgerät (Gesamtverbrauch)", "Zeitschaltuhren-Set"]'),
('gold', 'Gold-Paket', 'Premium Smart Home Upgrade', 400000, 500.00,
 '["Smart Home Hub", "Balkonkraftwerk-Gutschein (100€)", "E-Bike-Gutschein (200€)"]');

-- Insert Standard Badges
INSERT INTO badges (id, name, description, icon, tier, category) VALUES
('klimaheld_in_spe', 'Klimaheld in spe', 'Profil vervollständigt', '🌱', 'bronze', 'onboarding'),
('ideengeber', 'Ideengeber', 'Erste Idee eingereicht', '💡', 'bronze', 'onboarding'),
('community_mitglied', 'Community-Mitglied', 'Erste Community-Interaktion', '💬', 'bronze', 'onboarding'),
('strom_ninja', 'Strom-Ninja', 'Standby-Killer Challenge gemeistert', '⚡', 'silver', 'habit'),
('waerme_optimierer', 'Wärme-Optimierer', 'Heiz-Held Challenge gemeistert', '🌡️', 'gold', 'habit'),
('pedalritter', 'Pedalritter', 'Fahrrad-Pendler Challenge gemeistert', '🚲', 'gold', 'habit'),
('100kg_club', '100kg Club', '100 kg CO₂ vermieden', '🌍', 'silver', 'impact'),
('tonnen_titan', 'Tonnen-Titan', '1.000 kg CO₂ vermieden', '💪', 'gold', 'impact'),
('recruiter', 'Recruiter', '3 Freunde eingeladen', '👥', 'silver', 'community'),
('influencer', 'Influencer', '10+ erfolgreiche Referrals', '📢', 'gold', 'community'),
('demokratie_starter', 'Stimme erhoben', '3 Petitionen unterschrieben', '🗳️', 'silver', 'politik'),
('druck_macher', 'Druck-Macher', 'Politiker kontaktiert', '📧', 'gold', 'politik');
