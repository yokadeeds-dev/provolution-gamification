#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PROVOLUTION GAMIFICATION DATABASE INITIALIZER
Lädt challenges.json und initialisiert die SQLite-Datenbank

Usage:
    python init_database.py [--reset]
"""

import sqlite3
import json
import os
import sys
import argparse
from datetime import datetime

# Fix für Windows Console Encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Pfade
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CHALLENGES_PATH = os.path.join(SCRIPT_DIR, '..', 'challenges.json')
DB_PATH = os.path.join(SCRIPT_DIR, 'provolution_gamification.db')


def load_challenges():
    """Lädt die Challenges aus der JSON-Datei."""
    with open(CHALLENGES_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_schema(cursor):
    """Erstellt das Datenbankschema direkt."""
    
    # Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            display_name VARCHAR(100),
            avatar_emoji VARCHAR(10) DEFAULT '🌱',
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
    
    # Challenges Table
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
    
    # User Challenges Table
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
    
    # Challenge Logs Table
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
    
    # Badges Table
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
    
    # User Badges Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_badges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            badge_id VARCHAR(50) REFERENCES badges(id),
            earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            challenge_id VARCHAR(10) REFERENCES challenges(id)
        )
    ''')
    
    # XP Transactions Table
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
    
    # Teams Table
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
    
    # Team Members Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS team_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id INTEGER REFERENCES teams(id) ON DELETE CASCADE,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            role VARCHAR(20) DEFAULT 'member',
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Hardware Packages Table
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
    
    # Hardware Redemptions Table
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
    
    # Referrals Table
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
    
    # Indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_total_xp ON users(total_xp DESC)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_region ON users(region)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_challenges_user ON user_challenges(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_challenges_status ON user_challenges(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_xp_transactions_user ON xp_transactions(user_id)')
    
    print("✓ Schema erstellt")


def init_database(reset=False):
    """Initialisiert die Datenbank."""
    
    if reset and os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"✓ Alte Datenbank gelöscht: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    create_schema(cursor)
    conn.commit()
    
    return conn, cursor


def import_challenges(cursor):
    """Importiert Challenges aus der JSON-Datei."""
    
    data = load_challenges()
    challenges = data.get('challenges', [])
    
    print(f"Importiere {len(challenges)} Challenges...")
    
    success_count = 0
    for challenge in challenges:
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO challenges (
                    id, category, name, name_emoji, description, description_long,
                    duration_days, xp_reward, difficulty, success_criteria,
                    verification_method, verification_type, auto_verify, spot_check_rate,
                    badge_name, badge_icon, badge_tier,
                    co2_impact_kg_year, savings_euro_year, impact_type, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                challenge['id'],
                challenge['category'],
                challenge['name'],
                challenge.get('name_emoji'),
                challenge['description'],
                challenge.get('description_long'),
                challenge['duration_days'],
                challenge['xp_reward'],
                challenge.get('difficulty'),
                json.dumps(challenge.get('success_criteria', [])),
                challenge.get('verification', {}).get('method'),
                challenge.get('verification', {}).get('type'),
                1 if challenge.get('verification', {}).get('auto_verify', False) else 0,
                challenge.get('verification', {}).get('spot_check_rate', 0.1),
                challenge.get('badge', {}).get('name'),
                challenge.get('badge', {}).get('icon'),
                challenge.get('badge', {}).get('tier'),
                challenge.get('impact', {}).get('co2_kg_year'),
                challenge.get('impact', {}).get('savings_euro_year'),
                challenge.get('impact', {}).get('type'),
                1
            ))
            print(f"  ✓ {challenge['id']}: {challenge['name']}")
            success_count += 1
        except Exception as e:
            print(f"  ✗ {challenge['id']}: {e}")
    
    print(f"✓ {success_count}/{len(challenges)} Challenges importiert")


def import_badges(cursor):
    """Importiert Standard-Badges."""
    
    badges = [
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
        ('druck_macher', 'Druck-Macher', 'Politiker kontaktiert', '📧', 'gold', 'politik'),
    ]
    
    print(f"Importiere {len(badges)} Badges...")
    
    for badge in badges:
        cursor.execute('''
            INSERT OR REPLACE INTO badges (id, name, description, icon, tier, category)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', badge)
    
    print(f"✓ {len(badges)} Badges importiert")


def import_hardware_packages(cursor):
    """Importiert Hardware-Pakete."""
    
    packages = [
        ('bronze', 'Bronze-Paket', 'Starter-Kit für Energiesparer', 50000, 50.00,
         '["Smart Plug mit Verbrauchsmessung", "LED-Sparlampen-Set (5 Stück)", "Wasserspar-Duschkopf"]'),
        ('silver', 'Silber-Paket', 'Fortgeschrittenes Energie-Monitoring', 150000, 150.00,
         '["Smart Thermostat", "Energiemessgerät (Gesamtverbrauch)", "Zeitschaltuhren-Set"]'),
        ('gold', 'Gold-Paket', 'Premium Smart Home Upgrade', 400000, 500.00,
         '["Smart Home Hub", "Balkonkraftwerk-Gutschein (100€)", "E-Bike-Gutschein (200€)"]'),
    ]
    
    print(f"Importiere {len(packages)} Hardware-Pakete...")
    
    for pkg in packages:
        cursor.execute('''
            INSERT OR REPLACE INTO hardware_packages (id, name, description, xp_required, estimated_value, contents)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', pkg)
    
    print(f"✓ {len(packages)} Hardware-Pakete importiert")


def create_test_user(cursor):
    """Erstellt einen Test-User für Entwicklung."""
    
    cursor.execute('''
        INSERT OR IGNORE INTO users (
            username, email, password_hash, display_name, avatar_emoji,
            total_xp, level, trust_level, region, postal_code, referral_code
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        'test_user',
        'test@provolution.org',
        'HASH_PLACEHOLDER',
        'Test User',
        '🌱',
        1250,
        3,
        2,
        'NRW',
        '59065',
        'TESTCODE123'
    ))
    
    print("✓ Test-User erstellt: test_user (1250 XP)")


def verify_database(cursor):
    """Überprüft die Datenbank-Integrität."""
    
    print("\n" + "=" * 40)
    print("DATENBANK-STATISTIKEN")
    print("=" * 40)
    
    tables = [
        ('challenges', 'Challenges'),
        ('badges', 'Badges'),
        ('hardware_packages', 'Hardware-Pakete'),
        ('users', 'Users'),
    ]
    
    for table, label in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {label}: {count}")
    
    # Challenge-Kategorien
    cursor.execute("SELECT category, COUNT(*) FROM challenges GROUP BY category ORDER BY category")
    print("\nChallenges nach Kategorie:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")


def main():
    parser = argparse.ArgumentParser(description='Initialisiert die Provolution Gamification Datenbank')
    parser.add_argument('--reset', action='store_true', help='Löscht bestehende Datenbank und erstellt neu')
    args = parser.parse_args()
    
    print("=" * 50)
    print("PROVOLUTION GAMIFICATION DATABASE INITIALIZER")
    print("=" * 50)
    print()
    
    if not os.path.exists(CHALLENGES_PATH):
        print(f"FEHLER: Challenges nicht gefunden: {CHALLENGES_PATH}")
        return 1
    
    # Initialisiere Datenbank
    conn, cursor = init_database(reset=args.reset)
    
    # Importiere Daten
    import_challenges(cursor)
    import_badges(cursor)
    import_hardware_packages(cursor)
    create_test_user(cursor)
    
    # Commit
    conn.commit()
    
    # Verifiziere
    verify_database(cursor)
    
    # Schließe Verbindung
    conn.close()
    
    print()
    print("=" * 50)
    print(f"✓ Datenbank erstellt: {DB_PATH}")
    print("=" * 50)
    
    return 0


if __name__ == '__main__':
    exit(main())
