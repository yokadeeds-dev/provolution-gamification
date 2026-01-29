# PROVOLUTION GAMIFICATION API SPECIFICATION
## Version 1.0

**Base URL:** `https://api.provolution.org/v1`
**Authentication:** Bearer Token (JWT)

---

## 📋 ENDPOINTS ÜBERSICHT

### Users
- `POST /auth/register` - Registrierung
- `POST /auth/login` - Login
- `GET /users/me` - Eigenes Profil
- `PUT /users/me` - Profil aktualisieren
- `GET /users/{id}/stats` - User-Statistiken

### Challenges
- `GET /challenges` - Alle Challenges
- `GET /challenges/{id}` - Challenge-Details
- `POST /challenges/{id}/join` - Challenge beitreten
- `POST /challenges/{id}/log` - Tages-Log erstellen
- `GET /challenges/{id}/progress` - Eigener Fortschritt

### Leaderboards
- `GET /leaderboards/weekly` - Wöchentliches Ranking
- `GET /leaderboards/monthly` - Monatliches Ranking
- `GET /leaderboards/regional/{region}` - Regional-Ranking

### Badges
- `GET /badges` - Alle Badges
- `GET /badges/my` - Eigene Badges

### Teams
- `POST /teams` - Team erstellen
- `GET /teams/{id}` - Team-Details
- `POST /teams/{id}/join` - Team beitreten

### Rewards
- `GET /rewards/packages` - Hardware-Pakete
- `POST /rewards/redeem/{package_id}` - Paket einlösen

---

## 🔐 AUTHENTICATION

### Register
```http
POST /auth/register
Content-Type: application/json

{
  "username": "klimaheld_2026",
  "email": "user@example.com",
  "password": "securePassword123",
  "display_name": "Klima Held",
  "region": "NRW",
  "postal_code": "59065",
  "referral_code": "FRIEND123"  // Optional
}
```

**Response:**
```json
{
  "success": true,
  "user": {
    "id": 123,
    "username": "klimaheld_2026",
    "referral_code": "KLIMA123"
  },
  "token": "eyJhbGciOiJIUzI1NiIs..."
}
```

### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response:**
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 123,
    "username": "klimaheld_2026",
    "total_xp": 1250,
    "level": 3,
    "streak_days": 7
  }
}
```

---

## 👤 USER ENDPOINTS

### Get My Profile
```http
GET /users/me
Authorization: Bearer {token}
```

**Response:**
```json
{
  "id": 123,
  "username": "klimaheld_2026",
  "display_name": "Klima Held",
  "avatar_emoji": "🌳",
  "total_xp": 1250,
  "level": 3,
  "trust_level": 2,
  "streak_days": 7,
  "region": "NRW",
  "referral_code": "KLIMA123",
  "stats": {
    "challenges_completed": 5,
    "total_co2_saved_kg": 234.5,
    "badges_earned": 3,
    "referrals_count": 2
  }
}
```

### Update Profile
```http
PUT /users/me
Authorization: Bearer {token}
Content-Type: application/json

{
  "display_name": "Super Klimaheld",
  "avatar_emoji": "🌍",
  "focus_track": "mobility"
}
```

---

## 🏆 CHALLENGE ENDPOINTS

### List Challenges
```http
GET /challenges?category=energie&status=active
Authorization: Bearer {token}
```

**Query Parameters:**
- `category`: Filter by category (onboarding, energie, mobilitaet, community, politik)
- `status`: active, completed, all
- `difficulty`: easy, medium, hard, expert
- `limit`: Max results (default: 20)
- `offset`: Pagination offset

**Response:**
```json
{
  "challenges": [
    {
      "id": "EN-1",
      "name": "Standby-Killer",
      "name_emoji": "⚡ Standby-Killer",
      "description": "Schalte alle Geräte nachts komplett aus - 14 Tage",
      "category": "energie",
      "difficulty": "medium",
      "duration_days": 14,
      "xp_reward": 150,
      "badge": {
        "name": "Strom-Ninja",
        "icon": "⚡"
      },
      "impact": {
        "co2_kg_year": 100,
        "type": "direct"
      },
      "participants_count": 847,
      "user_status": null  // null, "active", "completed"
    }
  ],
  "total": 15,
  "offset": 0,
  "limit": 20
}
```

### Get Challenge Details
```http
GET /challenges/EN-1
Authorization: Bearer {token}
```

**Response:**
```json
{
  "id": "EN-1",
  "name": "Standby-Killer",
  "name_emoji": "⚡ Standby-Killer",
  "description": "Schalte alle Geräte nachts komplett aus - 14 Tage",
  "description_long": "Standby-Verbrauch macht bis zu 10% deines Stromverbrauchs aus...",
  "category": "energie",
  "difficulty": "medium",
  "duration_days": 14,
  "xp_reward": 150,
  "success_criteria": [
    "14 Tage täglich bestätigt",
    "Mindestens 5 Geräte auf Steckerleiste",
    "Nacht-Routine etabliert"
  ],
  "verification": {
    "method": "hybrid",
    "type": "self_report",
    "options": ["smart_plug_api", "photo_proof"]
  },
  "badge": {
    "name": "Strom-Ninja",
    "icon": "⚡",
    "tier": "silver"
  },
  "impact": {
    "co2_kg_year": 100,
    "savings_euro_year": 50,
    "type": "direct"
  },
  "stats": {
    "participants_active": 847,
    "participants_completed": 523,
    "completion_rate": 0.72
  }
}
```

### Join Challenge
```http
POST /challenges/EN-1/join
Authorization: Bearer {token}
```

**Response:**
```json
{
  "success": true,
  "user_challenge": {
    "id": 456,
    "challenge_id": "EN-1",
    "status": "active",
    "started_at": "2026-01-28T10:00:00Z",
    "progress_percent": 0,
    "days_completed": 0
  },
  "message": "Challenge gestartet! Viel Erfolg beim Standby-Killer!"
}
```

### Log Daily Progress
```http
POST /challenges/EN-1/log
Authorization: Bearer {token}
Content-Type: application/json

{
  "log_date": "2026-01-28",
  "completed": true,
  "notes": "Alle Geräte ausgeschaltet, Steckerleiste im Wohnzimmer und Büro",
  "proof_type": "photo",
  "proof_url": "https://cdn.provolution.org/proofs/123/day1.jpg"
}
```

**Response:**
```json
{
  "success": true,
  "log": {
    "id": 789,
    "log_date": "2026-01-28",
    "completed": true
  },
  "progress": {
    "days_completed": 1,
    "days_remaining": 13,
    "progress_percent": 7
  },
  "xp_earned": 0,  // XP wird erst bei Completion vergeben
  "streak": {
    "current": 8,
    "bonus_at_30_days": 500
  }
}
```

### Get My Progress
```http
GET /challenges/EN-1/progress
Authorization: Bearer {token}
```

**Response:**
```json
{
  "challenge_id": "EN-1",
  "status": "active",
  "started_at": "2026-01-28T10:00:00Z",
  "days_completed": 7,
  "days_remaining": 7,
  "progress_percent": 50,
  "logs": [
    {
      "log_date": "2026-01-28",
      "completed": true,
      "notes": "Tag 1 geschafft!"
    },
    // ... more logs
  ],
  "verification_status": "pending"
}
```

---

## 📊 LEADERBOARD ENDPOINTS

### Weekly Leaderboard
```http
GET /leaderboards/weekly?limit=10
Authorization: Bearer {token}
```

**Response:**
```json
{
  "period": {
    "start": "2026-01-20",
    "end": "2026-01-27"
  },
  "rankings": [
    {
      "rank": 1,
      "user": {
        "id": 45,
        "username": "KlimaHeld_NRW",
        "display_name": "Klima Held",
        "avatar_emoji": "🌳"
      },
      "score": 847,
      "metric": "co2_kg"
    },
    {
      "rank": 2,
      "user": {
        "id": 78,
        "username": "GreenWarrior23",
        "display_name": "Green Warrior",
        "avatar_emoji": "🌱"
      },
      "score": 723,
      "metric": "co2_kg"
    }
  ],
  "my_rank": {
    "rank": 42,
    "score": 125,
    "users_above": 41,
    "users_below": 158
  }
}
```

---

## 🏅 BADGE ENDPOINTS

### My Badges
```http
GET /badges/my
Authorization: Bearer {token}
```

**Response:**
```json
{
  "badges": [
    {
      "id": "klimaheld_in_spe",
      "name": "Klimaheld in spe",
      "icon": "🌱",
      "tier": "bronze",
      "earned_at": "2026-01-15T14:30:00Z",
      "challenge_id": "ON-1"
    },
    {
      "id": "strom_ninja",
      "name": "Strom-Ninja",
      "icon": "⚡",
      "tier": "silver",
      "earned_at": "2026-01-25T18:45:00Z",
      "challenge_id": "EN-1"
    }
  ],
  "total_earned": 2,
  "next_badge": {
    "id": "100kg_club",
    "name": "100kg Club",
    "icon": "🌍",
    "progress": 0.65,
    "requirement": "100 kg CO₂ vermieden"
  }
}
```

---

## 🎁 REWARDS ENDPOINTS

### List Hardware Packages
```http
GET /rewards/packages
Authorization: Bearer {token}
```

**Response:**
```json
{
  "packages": [
    {
      "id": "bronze",
      "name": "Bronze-Paket",
      "xp_required": 50000,
      "estimated_value": 50.00,
      "contents": [
        "Smart Plug mit Verbrauchsmessung",
        "LED-Sparlampen-Set (5 Stück)",
        "Wasserspar-Duschkopf"
      ],
      "in_stock": true,
      "user_eligible": false,
      "user_xp_missing": 48750
    },
    {
      "id": "silver",
      "name": "Silber-Paket",
      "xp_required": 150000,
      "estimated_value": 150.00,
      "contents": [
        "Smart Thermostat",
        "Energiemessgerät",
        "Zeitschaltuhren-Set"
      ],
      "in_stock": true,
      "user_eligible": false,
      "user_xp_missing": 148750
    }
  ],
  "user_total_xp": 1250
}
```

### Redeem Package
```http
POST /rewards/redeem/bronze
Authorization: Bearer {token}
Content-Type: application/json

{
  "shipping_address": {
    "name": "Max Mustermann",
    "street": "Klimastraße 42",
    "city": "Hamm",
    "postal_code": "59065",
    "country": "DE"
  }
}
```

**Response:**
```json
{
  "success": true,
  "redemption": {
    "id": 123,
    "package_id": "bronze",
    "status": "pending",
    "xp_spent": 50000
  },
  "user_remaining_xp": 50000,
  "message": "Bronze-Paket bestellt! Du erhältst eine E-Mail mit Tracking-Info."
}
```

---

## ⚠️ ERROR RESPONSES

### Standard Error Format
```json
{
  "success": false,
  "error": {
    "code": "CHALLENGE_ALREADY_JOINED",
    "message": "Du nimmst bereits an dieser Challenge teil.",
    "details": {
      "challenge_id": "EN-1",
      "user_challenge_id": 456
    }
  }
}
```

### Error Codes
| Code | HTTP Status | Description |
|------|-------------|-------------|
| `UNAUTHORIZED` | 401 | Token fehlt oder ungültig |
| `FORBIDDEN` | 403 | Keine Berechtigung |
| `NOT_FOUND` | 404 | Resource nicht gefunden |
| `CHALLENGE_ALREADY_JOINED` | 409 | Bereits bei Challenge dabei |
| `INSUFFICIENT_XP` | 400 | Nicht genug XP für Reward |
| `VALIDATION_ERROR` | 422 | Ungültige Eingabedaten |
| `RATE_LIMITED` | 429 | Zu viele Requests |

---

## 📝 RATE LIMITS

| Endpoint Category | Limit |
|-------------------|-------|
| Authentication | 10/min |
| Read (GET) | 100/min |
| Write (POST/PUT) | 30/min |
| Leaderboards | 20/min |

---

## 🔄 WEBHOOKS (Future)

Für Integrationen werden folgende Webhooks geplant:

- `challenge.completed` - User hat Challenge abgeschlossen
- `badge.earned` - User hat Badge verdient
- `xp.milestone` - User hat XP-Meilenstein erreicht
- `referral.completed` - Referral erfolgreich

---

*API Version: 1.0 | Stand: 2026-01-28*
