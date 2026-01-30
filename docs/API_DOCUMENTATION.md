# Provolution Gamification - API Documentation

## 🌐 Base URL

**Production:** `https://provolution-api.onrender.com`  
**Development:** `http://localhost:8001`

**API Version:** `v1`  
**API Prefix:** `/v1`

---

## 🔐 Authentication

Die API verwendet **JWT (JSON Web Tokens)** für Authentication.

### Token Format
```
Authorization: Bearer <jwt_token>
```

### Token erhalten
Über `/v1/auth/login` oder `/v1/auth/google` Endpoint.

**Token Lebensdauer:** 7 Tage

---

## 📡 Endpoints

### Health Check

#### `GET /health`
Prüft API-Status und Datenbank-Verbindung.

**Request:**
```bash
curl https://provolution-api.onrender.com/health
```

**Response:** `200 OK`
```json
{
  "status": "ok",
  "version": "1.0.0",
  "database": {
    "status": "healthy",
    "database": "/path/to/database.db",
    "tables_count": 17,
    "users_count": 5,
    "challenges_count": 5
  }
}
```

---

## 🔑 Authentication Endpoints

### Register User

#### `POST /v1/auth/register`
Erstellt neuen User Account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123",
  "username": "username"
}
```

**Response:** `201 Created`
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "xp": 0,
    "level": 1,
    "created_at": "2026-01-29T20:00:00Z"
  }
}
```

**Errors:**
- `400 Bad Request`: Email bereits registriert
- `422 Unprocessable Entity`: Ungültige Input-Daten

---

### Login

#### `POST /v1/auth/login`
Anmeldung mit Email/Passwort.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "username",
    "xp": 150,
    "level": 2
  }
}
```

**Errors:**
- `401 Unauthorized`: Falsche Email oder Passwort

---

### Google OAuth Login

#### `POST /v1/auth/google`
Anmeldung via Google OAuth Token.

**Request Body:**
```json
{
  "token": "google_oauth_token_here"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 2,
    "email": "user@gmail.com",
    "username": "John Doe",
    "google_id": "1234567890",
    "xp": 0,
    "level": 1
  }
}
```

**Errors:**
- `401 Unauthorized`: Ungültiges Google Token

---

### Get Current User

#### `GET /v1/auth/me`
Gibt aktuell angemeldeten User zurück.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "xp": 250,
  "level": 3,
  "avatar_url": null,
  "region": "NRW",
  "created_at": "2026-01-29T20:00:00Z"
}
```

**Errors:**
- `401 Unauthorized`: Token fehlt oder ungültig

---

## 🎯 Challenge Endpoints

### List All Challenges

#### `GET /v1/challenges`
Gibt alle verfügbaren Challenges zurück.

**Response:** `200 OK`
```json
[
  {
    "id": 1,
    "title": "Fahrrad statt Auto",
    "description": "Fahre diese Woche mit dem Fahrrad zur Arbeit",
    "category": "mobility",
    "difficulty": "easy",
    "xp_reward": 50,
    "co2_savings": 15.5,
    "duration_days": 7,
    "is_active": true
  },
  {
    "id": 2,
    "title": "Vegetarische Woche",
    "description": "Ernähre dich 7 Tage rein vegetarisch",
    "category": "nutrition",
    "difficulty": "medium",
    "xp_reward": 100,
    "co2_savings": 25.0,
    "duration_days": 7,
    "is_active": true
  }
]
```

---

### Get Challenge by ID

#### `GET /v1/challenges/{challenge_id}`
Gibt spezifische Challenge zurück.

**Response:** `200 OK`
```json
{
  "id": 1,
  "title": "Fahrrad statt Auto",
  "description": "Fahre diese Woche mit dem Fahrrad zur Arbeit",
  "category": "mobility",
  "difficulty": "easy",
  "xp_reward": 50,
  "co2_savings": 15.5,
  "duration_days": 7,
  "is_active": true
}
```

**Errors:**
- `404 Not Found`: Challenge existiert nicht

---

### Start Challenge

#### `POST /v1/challenges/{challenge_id}/start`
Startet Challenge für angemeldeten User.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:** `200 OK`
```json
{
  "id": 15,
  "user_id": 1,
  "challenge_id": 1,
  "status": "active",
  "progress": 0,
  "started_at": "2026-01-29T20:00:00Z",
  "completed_at": null
}
```

**Errors:**
- `400 Bad Request`: Challenge bereits aktiv
- `401 Unauthorized`: Nicht angemeldet
- `404 Not Found`: Challenge existiert nicht

---

### Complete Challenge

#### `POST /v1/challenges/{challenge_id}/complete`
Schließt aktive Challenge ab und vergibt XP.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:** `200 OK`
```json
{
  "id": 15,
  "user_id": 1,
  "challenge_id": 1,
  "status": "completed",
  "progress": 100,
  "xp_earned": 50,
  "completed_at": "2026-02-05T20:00:00Z"
}
```

**Errors:**
- `400 Bad Request`: Challenge nicht aktiv
- `401 Unauthorized`: Nicht angemeldet

---

## 📊 User Progress Endpoints


### Get User Progress

#### `GET /v1/users/me/progress`
Gibt Fortschritt des angemeldeten Users zurück.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response:** `200 OK`
```json
{
  "user": {
    "id": 1,
    "username": "username",
    "level": 3,
    "xp": 250,
    "xp_to_next_level": 50,
    "total_co2_saved": 125.5
  },
  "active_challenges": [
    {
      "id": 15,
      "challenge": {
        "title": "Fahrrad statt Auto",
        "xp_reward": 50
      },
      "progress": 60,
      "started_at": "2026-01-29T20:00:00Z"
    }
  ],
  "completed_challenges_count": 12,
  "total_challenges_count": 5
}
```

---

## 🏆 Leaderboard Endpoints

### Get Leaderboard

#### `GET /v1/leaderboard`
Gibt Rangliste aller User zurück.

**Query Parameters:**
- `timeframe` (optional): `week` | `month` | `all` (default: `week`)
- `limit` (optional): Anzahl Einträge (default: 10, max: 100)

**Request:**
```bash
GET /v1/leaderboard?timeframe=week&limit=10
```

**Response:** `200 OK`
```json
[
  {
    "rank": 1,
    "user": {
      "id": 5,
      "username": "EcoWarrior",
      "avatar_url": null,
      "region": "NRW"
    },
    "xp": 850,
    "level": 8,
    "co2_saved": 450.5,
    "challenges_completed": 25
  },
  {
    "rank": 2,
    "user": {
      "id": 1,
      "username": "ClimateChamp",
      "avatar_url": null,
      "region": "Bayern"
    },
    "xp": 720,
    "level": 7,
    "co2_saved": 380.0,
    "challenges_completed": 20
  }
]
```

---

## 🌍 CO₂-Footprint Endpoints

### Calculate Footprint

#### `POST /v1/footprint/calculate`
Berechnet CO₂-Fußabdruck basierend auf User-Input.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
  "housing": {
    "type": "apartment",
    "size_sqm": 80,
    "residents": 2,
    "heating_type": "gas",
    "electricity_green": false
  },
  "mobility": {
    "car_km_year": 10000,
    "car_type": "gasoline",
    "public_transport_km_year": 2000,
    "flights_short": 2,
    "flights_long": 1
  },
  "nutrition": {
    "diet_type": "omnivore",
    "organic_percentage": 30,
    "regional_percentage": 50
  },
  "consumption": {
    "shopping_frequency": "moderate",
    "electronics_new_per_year": 2,
    "clothing_new_per_year": 20
  }
}
```

**Response:** `200 OK`
```json
{
  "total_co2_tons_year": 8.5,
  "breakdown": {
    "housing": 2.1,
    "mobility": 3.2,
    "nutrition": 1.8,
    "consumption": 1.4
  },
  "comparison": {
    "german_average": 11.0,
    "global_average": 4.5,
    "1_5_degree_target": 2.5
  },
  "recommendations": [
    "Wechsel zu Öko-Strom",
    "Reduziere Autofahrten um 50%",
    "Erhöhe Anteil vegetarischer Mahlzeiten"
  ]
}
```


---

### Save Footprint

#### `POST /v1/footprint/save`
Speichert berechneten Footprint für User.

**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Request Body:**
```json
{
  "total_co2_tons_year": 8.5,
  "breakdown": {
    "housing": 2.1,
    "mobility": 3.2,
    "nutrition": 1.8,
    "consumption": 1.4
  }
}
```

**Response:** `201 Created`
```json
{
  "id": 42,
  "user_id": 1,
  "total_co2_tons_year": 8.5,
  "created_at": "2026-01-29T20:00:00Z"
}
```

---

## 📈 Statistics Endpoints

### Get Global Stats

#### `GET /v1/stats/global`
Gibt globale Plattform-Statistiken zurück.

**Response:** `200 OK`
```json
{
  "total_users": 1523,
  "total_challenges_completed": 8945,
  "total_co2_saved_tons": 567.8,
  "active_users_today": 234,
  "most_popular_challenge": {
    "id": 1,
    "title": "Fahrrad statt Auto",
    "completions": 892
  }
}
```

---

## 🚨 Error Responses

Alle Endpoints können folgende Error-Responses zurückgeben:

### 400 Bad Request
```json
{
  "detail": "Beschreibung des Fehlers"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## 🔒 Rate Limiting

**Free Tier (Render.com):**
- Keine expliziten Rate Limits
- Cold Start nach 15 Minuten Inaktivität (~50s)

**Best Practice:**
- Max 100 Requests pro Minute pro User
- Implementiere Retry-Logic mit exponential backoff

---

## 📚 Data Models

### User Model
```typescript
interface User {
  id: number;
  email: string;
  username: string;
  xp: number;
  level: number;
  avatar_url: string | null;
  region: string | null;
  google_id: string | null;
  created_at: string; // ISO 8601
  updated_at: string; // ISO 8601
}
```

### Challenge Model
```typescript
interface Challenge {
  id: number;
  title: string;
  description: string;
  category: "mobility" | "nutrition" | "energy" | "consumption" | "other";
  difficulty: "easy" | "medium" | "hard";
  xp_reward: number;
  co2_savings: number; // kg CO₂
  duration_days: number;
  is_active: boolean;
}
```

### UserChallenge Model
```typescript
interface UserChallenge {
  id: number;
  user_id: number;
  challenge_id: number;
  status: "active" | "completed" | "failed";
  progress: number; // 0-100
  started_at: string; // ISO 8601
  completed_at: string | null; // ISO 8601
}
```

---

## 🌐 CORS Configuration

**Allowed Origins:**
- `http://localhost:3000` (Development)
- `https://provolution-gamification.netlify.app` (Production)

**Allowed Methods:**
- GET, POST, PUT, DELETE, OPTIONS

**Allowed Headers:**
- Content-Type, Authorization

---

## 📝 Changelog

### Version 1.0.0 (2026-01-29)
- Initial API Release
- Google OAuth Integration
- CO₂-Footprint Calculator
- Challenge System
- Leaderboard
- User Progress Tracking

---

**API Base URL:** https://provolution-api.onrender.com  
**Documentation Version:** 1.0.0  
**Last Updated:** 29. Januar 2026
