# Provolution Gamification - Render.com Deployment

## Schnell-Setup (5 Minuten)

### 1. Procfile erstellen
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### 2. render.yaml erstellen
```yaml
services:
  - type: web
    name: provolution-api
    env: python
    region: frankfurt  # EU für DSGVO
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: JWT_SECRET
        generateValue: true
      - key: DATABASE_URL
        value: sqlite:///./provolution_gamification.db
```

### 3. requirements.txt prüfen
Bereits vorhanden - keine Änderung nötig.

### 4. Git Push
```bash
cd "C:\Users\yoka\Documents\CLAUDE WORKSPACE\Save the Provolution\80_MARKETING\gamification\backend"
git add Procfile render.yaml
git commit -m "Add Render deployment config"
git push origin main
```

### 5. Auf Render.com
1. Login mit GitHub
2. "New" → "Web Service"
3. Repository wählen
4. Deploy klicken
5. Warten (2-5 Minuten)

## Troubleshooting

### Problem: "No module named 'app'"
**Lösung:** Root Directory auf `backend` setzen in Render Settings

### Problem: Port Error
**Lösung:** Prüfen ob `--port $PORT` korrekt ist (ohne Anführungszeichen)

### Problem: SQLite funktioniert nicht
**Lösung:** Für Production PostgreSQL nutzen (später), SQLite reicht für Demo

## Nach erfolgreichem Deploy

URL wird sein: `https://provolution-api-xxxx.onrender.com`

Custom Domain später: `api.provolution.org`
