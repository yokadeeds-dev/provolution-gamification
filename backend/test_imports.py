#!/usr/bin/env python
"""
Test script to verify all imports work correctly.
Run from backend directory: python test_imports.py
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing imports...")
print("-" * 40)

try:
    print("1. Testing database...")
    from app.database import get_db, check_database_health
    print("   ✅ database module OK")
except Exception as e:
    print(f"   ❌ database: {e}")

try:
    print("2. Testing auth...")
    from app.auth import (
        create_access_token, 
        verify_password, 
        hash_password,
        get_current_user
    )
    print("   ✅ auth module OK")
except Exception as e:
    print(f"   ❌ auth: {e}")

try:
    print("3. Testing models...")
    from app.models import (
        UserRegisterRequest,
        ChallengeListResponse,
        LeaderboardResponse,
        Badge,
        HardwarePackage
    )
    print("   ✅ models module OK")
except Exception as e:
    print(f"   ❌ models: {e}")

try:
    print("4. Testing routers...")
    from app.routers import (
        auth_router,
        users_router,
        challenges_router,
        leaderboards_router,
        badges_router,
        rewards_router
    )
    print("   ✅ routers module OK")
except Exception as e:
    print(f"   ❌ routers: {e}")

try:
    print("5. Testing main app...")
    from app.main import app
    print("   ✅ main app OK")
    print(f"   App: {app.title} v{app.version}")
except Exception as e:
    print(f"   ❌ main: {e}")

try:
    print("6. Testing database health...")
    health = check_database_health()
    if health['status'] == 'healthy':
        print(f"   ✅ Database healthy")
        print(f"   - Tables: {health['tables_count']}")
        print(f"   - Users: {health['users_count']}")
        print(f"   - Challenges: {health['challenges_count']}")
    else:
        print(f"   ⚠️ Database issue: {health.get('error', 'unknown')}")
except Exception as e:
    print(f"   ❌ health check: {e}")

print("-" * 40)
print("Import test complete!")
print("\nTo start the server, run:")
print("  uvicorn app.main:app --reload")
