# Provolution Gamification API

FastAPI-basiertes Backend für das Provolution Klima-Gamification-System.

## 🚀 Quick Start

### Windows
```bash
# Setup (einmalig)
setup.bat

# Server starten
run_server.bat
```

### Linux/Mac
```bash
# Setup (einmalig)
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python init_database.py

# Server starten
./run_server.sh
```

## 📚 API Dokumentation

Nach Start des Servers:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🔑 Authentication

Die API nutzt JWT Bearer Tokens.

### Registrierung
```bash
curl -X POST http://localhost:8000/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "klimaheld",
    "email": "user@example.com",
    "password": "SecurePass123"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123"
  }'
```

### Authentifizierte Anfragen
```bash
curl http://localhost:8000/v1/users/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 📁 Projektstruktur

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI App
│   ├── database.py       # SQLite Connection
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── jwt_handler.py    # JWT Token Management
│   │   ├── password.py       # bcrypt Hashing
│   │   └── dependencies.py   # FastAPI Dependencies
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py          # User Schemas
│   │   ├── challenge.py     # Challenge Schemas
│   │   ├── leaderboard.py   # Leaderboard Schemas
│   │   ├── badge.py         # Badge Schemas
│   │   └── reward.py        # Reward Schemas
│   └── routers/
│       ├── __init__.py
│       ├── auth.py          # /auth Endpoints
│       ├── users.py         # /users Endpoints
│       ├── challenges.py    # /challenges Endpoints
│       ├── leaderboards.py  # /leaderboards Endpoints
│       ├── badges.py        # /badges Endpoints
│       └── rewards.py       # /rewards Endpoints
├── schema.sql               # Database Schema
├── schema_update.sql        # Schema Migrations
├── init_database.py         # DB Initialization
├── requirements.txt         # Python Dependencies
├── setup.bat               # Windows Setup
├── run_server.bat          # Windows Start
└── run_server.sh           # Linux/Mac Start
```

## 🛠️ API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/v1/auth/register` | Neuen User registrieren |
| POST | `/v1/auth/login` | User einloggen |

### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v1/users/me` | Eigenes Profil |
| PUT | `/v1/users/me` | Profil aktualisieren |
| GET | `/v1/users/{id}/stats` | User-Statistiken |

### Challenges
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v1/challenges` | Alle Challenges |
| GET | `/v1/challenges/{id}` | Challenge Details |
| POST | `/v1/challenges/{id}/join` | Challenge beitreten |
| POST | `/v1/challenges/{id}/log` | Täglichen Fortschritt loggen |
| GET | `/v1/challenges/{id}/progress` | Eigener Fortschritt |

### Leaderboards
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v1/leaderboards/weekly` | Wöchentliches Ranking |
| GET | `/v1/leaderboards/monthly` | Monatliches Ranking |
| GET | `/v1/leaderboards/regional/{region}` | Regional-Ranking |

### Badges
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v1/badges` | Alle Badges |
| GET | `/v1/badges/my` | Eigene Badges |

### Rewards
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/v1/rewards/packages` | Hardware-Pakete |
| POST | `/v1/rewards/redeem/{id}` | Paket einlösen |

## 🔒 Sicherheit

- Passwörter werden mit bcrypt (12 Rounds) gehasht
- JWT Tokens laufen nach 24 Stunden ab
- CORS ist für bekannte Domains konfiguriert
- Rate Limiting sollte für Produktion aktiviert werden

## 🗃️ Datenbank

SQLite-Datenbank: `provolution_gamification.db`

Neu initialisieren:
```bash
python init_database.py
```

Schema-Updates anwenden:
```bash
sqlite3 provolution_gamification.db < schema_update.sql
```

## 🚢 Production Deployment

Für Production:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Empfohlene Anpassungen:
1. JWT Secret Key aus Environment Variable
2. CORS Origins einschränken
3. Rate Limiting aktivieren
4. HTTPS via Reverse Proxy (nginx/Caddy)
5. PostgreSQL statt SQLite für Skalierung

## 📝 Lizenz

Teil des Provolution Climate Framework.
Open Humanity License / CC0
