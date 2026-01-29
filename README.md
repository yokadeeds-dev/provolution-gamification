# Provolution Gamification

🌍 **CO₂-Tracking mit Gamification** - Challenges, Badges, Leaderboards

## Features

- **CO₂-Fußabdruck-Rechner** mit 24 Emissionsfaktoren (UBA/TREMOD/ifeu)
- **Challenges** für Klimaschutz-Aktionen (Energie, Mobilität, Ernährung)
- **XP & Badges** für Motivation
- **Leaderboards** (regional, wöchentlich, monatlich)
- **SEC-Score Integration** (Provolution Framework)

## Tech Stack

**Backend:** FastAPI + SQLite + JWT Auth
**Frontend:** Vanilla JS + CSS
**Hosting:** Render.com (API) + Netlify (Frontend)

## Quick Start (Lokal)

```bash
# Backend starten
cd backend
pip install -r requirements.txt
uvicorn app.main:app --port 8001 --reload

# Frontend öffnen
# Einfach frontend/index.html im Browser öffnen
```

## API Dokumentation

Nach dem Start: http://localhost:8001/docs

## Deployment

- **Backend:** Render.com (siehe `backend/DEPLOY_RENDER.md`)
- **Frontend:** Netlify (automatisch via `frontend/netlify.toml`)

## Lizenz

Open Source - Teil des [Provolution](https://provolution.org) Projekts

## Links

- 🌐 Website: [provolution.org](https://provolution.org)
- 📚 Framework: [Provolution Scientific Work](https://github.com/yokadeeds-dev/Provolution)
