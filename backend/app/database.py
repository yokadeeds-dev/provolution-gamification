# database.py - SQLite Database Connection
"""
Provolution Gamification - Database Connection Layer
Async SQLite with connection pooling
Cloud-ready for Render.com deployment
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional
import os

# Database path - use environment variable or default
# On Render: /opt/render/project/src/ is the working directory
def get_db_path() -> Path:
    """Get path to database file, cloud-compatible."""
    # Check for explicit path from environment
    env_path = os.environ.get('DATABASE_PATH')
    if env_path:
        return Path(env_path)
    
    # Default: relative to this file (works locally and on Render)
    return Path(__file__).parent.parent / "provolution_gamification.db"

DB_PATH = get_db_path()


def dict_factory(cursor: sqlite3.Cursor, row: tuple) -> dict:
    """Convert SQLite rows to dictionaries."""
    fields = [column[0] for column in cursor.description]
    return dict(zip(fields, row))


def ensure_database_exists():
    """Ensure database file exists, initialize if needed."""
    if not DB_PATH.exists():
        print(f"[DB] Database not found at {DB_PATH}, initializing...")
        initialize_database()
    return True


def initialize_database():
    """Create database schema if not exists."""
    import json
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Core tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255),
            google_id VARCHAR(255) UNIQUE,
            auth_provider VARCHAR(20) DEFAULT 'local',
            display_name VARCHAR(100),
            avatar_emoji VARCHAR(10) DEFAULT '🌱',
            avatar_url VARCHAR(500),
            total_xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            trust_level INTEGER DEFAULT 1,
            streak_days INTEGER DEFAULT 0,
            streak_last_activity DATE,
            region VARCHAR(50),
            postal_code VARCHAR(10),
            co2_footprint_baseline REAL,
            focus_track VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            referral_code VARCHAR(20) UNIQUE,
            referred_by INTEGER REFERENCES users(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS challenges (
            id VARCHAR(10) PRIMARY KEY,
            category VARCHAR(50) NOT NULL,
            name VARCHAR(100) NOT NULL,
            name_emoji VARCHAR(150),
            description TEXT,
            description_long TEXT,
            duration_days INTEGER NOT NULL,
            xp_reward INTEGER NOT NULL,
            difficulty VARCHAR(20),
            success_criteria TEXT,
            verification_method VARCHAR(50),
            verification_type VARCHAR(50),
            auto_verify INTEGER DEFAULT 0,
            spot_check_rate REAL DEFAULT 0.1,
            badge_name VARCHAR(100),
            badge_icon VARCHAR(10),
            badge_tier VARCHAR(20),
            co2_impact_kg_year REAL,
            savings_euro_year REAL,
            impact_type VARCHAR(50),
            is_active INTEGER DEFAULT 1,
            is_featured INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_challenges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            challenge_id VARCHAR(10) REFERENCES challenges(id),
            status VARCHAR(20) DEFAULT 'active',
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            progress_percent INTEGER DEFAULT 0,
            days_completed INTEGER DEFAULT 0,
            verification_status VARCHAR(20) DEFAULT 'pending',
            verified_at TIMESTAMP,
            verified_by INTEGER REFERENCES users(id),
            xp_earned INTEGER DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS challenge_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_challenge_id INTEGER REFERENCES user_challenges(id) ON DELETE CASCADE,
            log_date DATE NOT NULL,
            completed INTEGER DEFAULT 0,
            notes TEXT,
            proof_type VARCHAR(50),
            proof_url VARCHAR(500),
            proof_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS badges (
            id VARCHAR(50) PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            icon VARCHAR(10),
            tier VARCHAR(20),
            category VARCHAR(50),
            requirements TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_badges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            badge_id VARCHAR(50) REFERENCES badges(id),
            earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            challenge_id VARCHAR(10) REFERENCES challenges(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS xp_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            amount INTEGER NOT NULL,
            type VARCHAR(50) NOT NULL,
            reference_type VARCHAR(50),
            reference_id VARCHAR(50),
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            total_xp INTEGER DEFAULT 0,
            total_co2_saved REAL DEFAULT 0,
            member_count INTEGER DEFAULT 0,
            created_by INTEGER REFERENCES users(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS team_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id INTEGER REFERENCES teams(id) ON DELETE CASCADE,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            role VARCHAR(20) DEFAULT 'member',
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hardware_packages (
            id VARCHAR(20) PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            xp_required INTEGER NOT NULL,
            estimated_value REAL,
            contents TEXT,
            is_active INTEGER DEFAULT 1,
            stock_count INTEGER DEFAULT 0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hardware_redemptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id),
            package_id VARCHAR(20) REFERENCES hardware_packages(id),
            status VARCHAR(20) DEFAULT 'pending',
            shipping_address TEXT,
            tracking_number VARCHAR(100),
            xp_spent INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            shipped_at TIMESTAMP,
            delivered_at TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS referrals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            referrer_id INTEGER REFERENCES users(id),
            referred_id INTEGER REFERENCES users(id),
            status VARCHAR(20) DEFAULT 'pending',
            completed_at TIMESTAMP,
            referrer_xp_earned INTEGER DEFAULT 0,
            referred_xp_earned INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # CO2 Footprint Tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emission_factors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category VARCHAR(50) NOT NULL,
            subcategory VARCHAR(50) NOT NULL,
            name VARCHAR(100) NOT NULL,
            factor_value REAL NOT NULL,
            unit VARCHAR(50) NOT NULL,
            source VARCHAR(200),
            year INTEGER,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_footprint (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE CASCADE,
            housing_type VARCHAR(20),
            housing_size_sqm INTEGER,
            household_members INTEGER DEFAULT 1,
            heating_type VARCHAR(20),
            heating_consumption_kwh INTEGER,
            electricity_kwh INTEGER,
            green_electricity BOOLEAN DEFAULT FALSE,
            has_car BOOLEAN DEFAULT FALSE,
            car_fuel_type VARCHAR(20),
            car_km_year INTEGER DEFAULT 0,
            car_consumption_l_100km REAL,
            public_transport_km_year INTEGER DEFAULT 0,
            bike_km_year INTEGER DEFAULT 0,
            flights_short_haul INTEGER DEFAULT 0,
            flights_long_haul INTEGER DEFAULT 0,
            diet_type VARCHAR(20),
            regional_seasonal BOOLEAN DEFAULT FALSE,
            food_waste_level VARCHAR(10),
            shopping_frequency VARCHAR(10),
            secondhand_preference BOOLEAN DEFAULT FALSE,
            digital_consumption VARCHAR(10),
            co2_total_kg_year REAL,
            co2_housing_kg REAL,
            co2_mobility_kg REAL,
            co2_nutrition_kg REAL,
            co2_consumption_kg REAL,
            calculation_version VARCHAR(10) DEFAULT '1.0',
            last_calculated TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS footprint_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            co2_total_kg_year REAL,
            co2_housing_kg REAL,
            co2_mobility_kg REAL,
            co2_nutrition_kg REAL,
            co2_consumption_kg REAL,
            trigger_type VARCHAR(20)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS footprint_inputs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            input_date DATE NOT NULL,
            category VARCHAR(50) NOT NULL,
            subcategory VARCHAR(50),
            value REAL NOT NULL,
            unit VARCHAR(50),
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_total_xp ON users(total_xp DESC)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_region ON users(region)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_challenges_user ON user_challenges(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_challenges_status ON user_challenges(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_xp_transactions_user ON xp_transactions(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_footprint_user ON user_footprint(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_footprint_history_user ON footprint_history(user_id)')
    
    # Insert default emission factors
    emission_factors = [
        ('mobility', 'car', 'Benzin PKW (Durchschnitt)', 0.21, 'kg CO2/km', 'UBA TREMOD 2023', 2023, None),
        ('mobility', 'car', 'Diesel PKW (Durchschnitt)', 0.18, 'kg CO2/km', 'UBA TREMOD 2023', 2023, None),
        ('mobility', 'car', 'Elektro PKW (DE-Strommix)', 0.08, 'kg CO2/km', 'UBA 2023', 2023, None),
        ('mobility', 'public', 'ÖPNV Bus', 0.08, 'kg CO2/km', 'UBA TREMOD 2023', 2023, None),
        ('mobility', 'public', 'Bahn Nahverkehr', 0.06, 'kg CO2/km', 'UBA TREMOD 2023', 2023, None),
        ('mobility', 'public', 'Bahn Fernverkehr', 0.03, 'kg CO2/km', 'UBA TREMOD 2023', 2023, None),
        ('mobility', 'flight', 'Kurzstreckenflug (<1500km)', 0.28, 'kg CO2/km', 'UBA 2023 inkl. RFI', 2023, 'inkl. RFI-Faktor'),
        ('mobility', 'flight', 'Langstreckenflug (>1500km)', 0.20, 'kg CO2/km', 'UBA 2023 inkl. RFI', 2023, 'inkl. RFI-Faktor'),
        ('housing', 'heating', 'Erdgas', 0.20, 'kg CO2/kWh', 'UBA 2023', 2023, None),
        ('housing', 'heating', 'Heizöl', 0.27, 'kg CO2/kWh', 'UBA 2023', 2023, None),
        ('housing', 'heating', 'Fernwärme (Durchschnitt)', 0.18, 'kg CO2/kWh', 'UBA 2023', 2023, None),
        ('housing', 'heating', 'Wärmepumpe (DE-Strommix)', 0.12, 'kg CO2/kWh', 'UBA 2023', 2023, None),
        ('housing', 'electricity', 'Deutscher Strommix', 0.42, 'kg CO2/kWh', 'UBA 2023', 2023, None),
        ('housing', 'electricity', 'Ökostrom (zertifiziert)', 0.04, 'kg CO2/kWh', 'UBA 2023', 2023, None),
        ('nutrition', 'meat', 'Rindfleisch', 13.6, 'kg CO2/kg', 'ifeu 2020', 2020, None),
        ('nutrition', 'meat', 'Schweinefleisch', 4.6, 'kg CO2/kg', 'ifeu 2020', 2020, None),
        ('nutrition', 'meat', 'Geflügel', 5.5, 'kg CO2/kg', 'ifeu 2020', 2020, None),
        ('nutrition', 'dairy', 'Milch', 1.4, 'kg CO2/L', 'ifeu 2020', 2020, None),
        ('nutrition', 'dairy', 'Käse', 8.5, 'kg CO2/kg', 'ifeu 2020', 2020, None),
        ('nutrition', 'dairy', 'Butter', 9.0, 'kg CO2/kg', 'ifeu 2020', 2020, None),
        ('nutrition', 'plant', 'Gemüse (saisonal)', 0.3, 'kg CO2/kg', 'ifeu 2020', 2020, None),
        ('nutrition', 'plant', 'Obst (regional)', 0.4, 'kg CO2/kg', 'ifeu 2020', 2020, None),
        ('consumption', 'goods', 'Kleidung (Durchschnitt)', 15.0, 'kg CO2/Stück', 'UBA 2022', 2022, None),
        ('consumption', 'electronics', 'Smartphone', 70.0, 'kg CO2/Gerät', 'Fraunhofer 2022', 2022, None),
    ]
    
    cursor.execute("SELECT COUNT(*) FROM emission_factors")
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
            INSERT INTO emission_factors (category, subcategory, name, factor_value, unit, source, year, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', emission_factors)
        print(f"[DB] Inserted {len(emission_factors)} emission factors")
    
    # Insert default badges
    badges = [
        ('klimaheld_in_spe', 'Klimaheld in spe', 'Profil vervollständigt', '🌱', 'bronze', 'onboarding'),
        ('ideengeber', 'Ideengeber', 'Erste Idee eingereicht', '💡', 'bronze', 'onboarding'),
        ('community_mitglied', 'Community-Mitglied', 'Erste Community-Interaktion', '💬', 'bronze', 'onboarding'),
        ('strom_ninja', 'Strom-Ninja', 'Standby-Killer Challenge gemeistert', '⚡', 'silver', 'habit'),
        ('100kg_club', '100kg Club', '100 kg CO₂ vermieden', '🌍', 'silver', 'impact'),
        ('co2_tracker', 'CO₂-Tracker', 'Ersten CO₂-Fußabdruck berechnet', '📊', 'bronze', 'footprint'),
    ]
    
    cursor.execute("SELECT COUNT(*) FROM badges")
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
            INSERT INTO badges (id, name, description, icon, tier, category)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', badges)
        print(f"[DB] Inserted {len(badges)} badges")
    
    # Insert sample challenges
    challenges = [
        ('EN-1', 'energy', 'Standby-Killer', '⚡ Standby-Killer', 'Schalte alle Standby-Geräte konsequent aus', 'Identifiziere und eliminiere alle Standby-Verbraucher in deinem Haushalt für 7 Tage.', 7, 150, 'easy', '["7 Tage ohne Standby", "Mind. 5 Geräte identifiziert"]', 'self_report', 'checklist', 1, 0.1, 'Strom-Ninja', '⚡', 'silver', 50.0, 30.0, 'energy', 1, 1),
        ('EN-2', 'energy', 'LED-Umrüster', '💡 LED-Umrüster', 'Ersetze 5 alte Glühbirnen durch LEDs', 'Tausche mindestens 5 herkömmliche Glühbirnen oder Halogenlampen gegen LED-Lampen aus.', 14, 200, 'easy', '["5+ Lampen getauscht", "Foto-Dokumentation"]', 'photo_proof', 'photo', 0, 0.2, 'Licht-Champion', '💡', 'bronze', 80.0, 40.0, 'energy', 1, 0),
        ('MO-1', 'mobility', 'Fahrrad-Pendler', '🚲 Fahrrad-Pendler', 'Fahre 5 Tage mit dem Rad zur Arbeit', 'Ersetze deine Auto-Pendelstrecke für 5 Arbeitstage durch das Fahrrad.', 7, 250, 'medium', '["5 Tage Rad-Pendeln", "Mind. 5km pro Tag"]', 'gps_track', 'automatic', 1, 0.05, 'Pedalritter', '🚲', 'gold', 200.0, 100.0, 'mobility', 1, 1),
        ('NU-1', 'nutrition', 'Veggie-Woche', '🥗 Veggie-Woche', 'Eine Woche vegetarisch essen', 'Ernähre dich 7 Tage lang komplett vegetarisch.', 7, 200, 'medium', '["7 Tage vegetarisch", "Keine Fleischprodukte"]', 'self_report', 'checklist', 1, 0.1, 'Gemüse-Held', '🥗', 'silver', 150.0, 50.0, 'nutrition', 1, 1),
        ('ON-1', 'onboarding', 'CO₂-Footprint Tracker', '📊 CO₂-Footprint', 'Berechne deinen persönlichen CO₂-Fußabdruck', 'Nutze unseren Rechner um deinen Baseline-Fußabdruck zu ermitteln.', 1, 100, 'easy', '["Footprint berechnet", "Alle Kategorien ausgefüllt"]', 'automatic', 'system', 1, 0.0, 'CO₂-Tracker', '📊', 'bronze', 0.0, 0.0, 'onboarding', 1, 1),
    ]
    
    cursor.execute("SELECT COUNT(*) FROM challenges")
    if cursor.fetchone()[0] == 0:
        cursor.executemany('''
            INSERT INTO challenges (id, category, name, name_emoji, description, description_long, duration_days, xp_reward, difficulty, success_criteria, verification_method, verification_type, auto_verify, spot_check_rate, badge_name, badge_icon, badge_tier, co2_impact_kg_year, savings_euro_year, impact_type, is_active, is_featured)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', challenges)
        print(f"[DB] Inserted {len(challenges)} challenges")
    
    conn.commit()
    conn.close()
    print(f"[DB] Database initialized at {DB_PATH}")


@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager for database connections.
    Ensures proper connection handling and cleanup.
    """
    ensure_database_exists()
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.row_factory = dict_factory
        conn.execute("PRAGMA foreign_keys = ON")
        yield conn
        conn.commit()
    except sqlite3.Error as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()


class DatabaseManager:
    """Singleton database manager for FastAPI dependency injection."""
    
    _instance: Optional['DatabaseManager'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.db_path = DB_PATH
        ensure_database_exists()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a new database connection."""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = dict_factory
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    
    def execute_query(self, query: str, params: tuple = ()) -> list[dict]:
        """Execute a SELECT query and return results."""
        with get_db() as conn:
            cursor = conn.execute(query, params)
            return cursor.fetchall()
    
    def execute_write(self, query: str, params: tuple = ()) -> int:
        """Execute an INSERT/UPDATE/DELETE and return affected row id."""
        with get_db() as conn:
            cursor = conn.execute(query, params)
            return cursor.lastrowid
    
    def execute_many(self, query: str, params_list: list[tuple]) -> int:
        """Execute multiple write operations."""
        with get_db() as conn:
            cursor = conn.executemany(query, params_list)
            return cursor.rowcount


def get_database() -> DatabaseManager:
    """FastAPI dependency for database access."""
    return DatabaseManager()


def check_database_health() -> dict:
    """Check if database is accessible and return stats."""
    try:
        ensure_database_exists()
        with get_db() as conn:
            tables = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
            
            user_count = conn.execute("SELECT COUNT(*) as c FROM users").fetchone()['c']
            challenge_count = conn.execute("SELECT COUNT(*) as c FROM challenges").fetchone()['c']
            
            return {
                "status": "healthy",
                "database": str(DB_PATH),
                "tables_count": len(tables),
                "users_count": user_count,
                "challenges_count": challenge_count
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
