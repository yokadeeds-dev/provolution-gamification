# Provolution Gamification - Setup Guide

## 🎯 Übersicht

Diese Anleitung erklärt das vollständige Setup der Provolution Gamification Platform mit FastAPI Backend, Vanilla JavaScript Frontend, Google OAuth Integration und Deployment auf Render.com + Netlify.

---

## 📋 Voraussetzungen

### System Requirements
- **Python:** 3.10+
- **Node.js:** 16+ (optional für lokale Entwicklung)
- **Git:** Installiert und konfiguriert
- **Browser:** Modern browser mit JavaScript aktiviert

### Accounts
- **GitHub:** Für Repository Management
- **Google Cloud Console:** Für OAuth Credentials
- **Render.com:** Für Backend Deployment (Free Tier möglich)
- **Netlify:** Für Frontend Deployment (Free Tier möglich)

---

## 🚀 Teil 1: Lokale Entwicklung

### Backend Setup

#### 1. Repository klonen
```bash
git clone https://github.com/yokadeeds-dev/provolution-gamification.git
cd provolution-gamification/backend
```

#### 2. Virtual Environment erstellen
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

#### 3. Dependencies installieren
```bash
pip install -r requirements.txt
```

#### 4. Environment Variables konfigurieren
Erstelle `.env` Datei im `backend/` Verzeichnis:
```env
# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here

# JWT Secret (generiere mit: python -c "import secrets; print(secrets.token_urlsafe(32))")
JWT_SECRET_KEY=your_generated_secret_key_here

# API Configuration
FRONTEND_URL=http://localhost:3000
API_VERSION=1.0.0
```

#### 5. Datenbank initialisieren
```bash
python -c "from app.database import init_db; init_db()"
```

#### 6. Server starten
```bash
uvicorn app.main:app --reload --port 8001
```

Backend läuft nun auf: **http://localhost:8001**


---

### Frontend Setup

#### 1. Zum Frontend-Verzeichnis wechseln
```bash
cd ../frontend
```

#### 2. API-URL konfigurieren
Bearbeite `config.js`:
```javascript
// Lokale Entwicklung
window.PROVOLUTION_API_URL = 'http://localhost:8001/v1';

// Production (nach Deployment)
// window.PROVOLUTION_API_URL = 'https://provolution-api.onrender.com/v1';
```

#### 3. Lokalen Server starten
```bash
# Option 1: Python Simple HTTP Server
python -m http.server 3000

# Option 2: Node.js http-server (falls installiert)
npx http-server -p 3000

# Option 3: Live Server VS Code Extension
```

Frontend läuft nun auf: **http://localhost:3000**

---

## ☁️ Teil 2: Google OAuth Setup

### 1. Google Cloud Console

1. Gehe zu: https://console.cloud.google.com
2. Erstelle neues Projekt: "Provolution Gamification"
3. Aktiviere **Google+ API**


### 2. OAuth Consent Screen konfigurieren

**Navigation:** APIs & Services → OAuth consent screen

- **User Type:** External
- **App Name:** Provolution Gamification
- **Support Email:** deine-email@example.com
- **App Logo:** Optional (1024x1024 PNG)
- **Authorized Domains:** 
  - `provolution-gamification.netlify.app`
  - `onrender.com`
- **Developer Contact:** deine-email@example.com

### 3. OAuth Credentials erstellen

**Navigation:** APIs & Services → Credentials → Create Credentials → OAuth client ID

- **Application Type:** Web application
- **Name:** Provolution Web Client
- **Authorized JavaScript Origins:**
  - `http://localhost:3000` (Entwicklung)
  - `https://provolution-gamification.netlify.app` (Production)
- **Authorized Redirect URIs:**
  - `http://localhost:3000` (Entwicklung)
  - `https://provolution-gamification.netlify.app` (Production)

**Wichtig:** Kopiere:
- Client ID
- Client Secret

### 4. Credentials in Backend eintragen

Füge in `.env` Datei ein:
```env
GOOGLE_CLIENT_ID=deine_client_id_hier
GOOGLE_CLIENT_SECRET=dein_client_secret_hier
```

---

## 🌐 Teil 3: Production Deployment


### Backend auf Render.com

#### 1. Render Account erstellen
- Gehe zu: https://render.com
- Sign up mit GitHub Account

#### 2. Neuen Web Service erstellen
- **Dashboard → New → Web Service**
- **Repository:** Wähle dein GitHub Repo
- **Name:** `provolution-api`
- **Region:** Frankfurt (EU Central)
- **Branch:** `main`
- **Root Directory:** `backend`
- **Runtime:** Python 3
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

#### 3. Environment Variables setzen
In Render Dashboard → Environment:
```
GOOGLE_CLIENT_ID=deine_client_id
GOOGLE_CLIENT_SECRET=dein_client_secret
JWT_SECRET_KEY=dein_jwt_secret
FRONTEND_URL=https://provolution-gamification.netlify.app
API_VERSION=1.0.0
```

#### 4. Deploy auslösen
- **Manual Deploy → Deploy latest commit**
- Warte auf erfolgreichen Build (~5 Minuten)

**API URL:** `https://provolution-api.onrender.com`

---

### Frontend auf Netlify


#### 1. Netlify Account erstellen
- Gehe zu: https://netlify.com
- Sign up mit GitHub Account

#### 2. Production API-URL konfigurieren
Bearbeite `frontend/config.js`:
```javascript
window.PROVOLUTION_API_URL = 'https://provolution-api.onrender.com/v1';
```

Commit und pushe Änderung:
```bash
git add frontend/config.js
git commit -m "Set production API URL"
git push origin main
```

#### 3. Site aus Git deployen
- **Sites → Add new site → Import an existing project**
- **Connect to Git provider:** GitHub
- **Repository:** Wähle dein Repo
- **Branch:** `main`
- **Base directory:** `frontend`
- **Build command:** (leer lassen)
- **Publish directory:** `.` (aktuelles Verzeichnis)

#### 4. Deploy starten
- **Deploy site**
- Warte auf erfolgreichen Build (~2 Minuten)

**Frontend URL:** `https://provolution-gamification.netlify.app`

#### 5. Custom Domain (Optional)
- **Domain settings → Add custom domain**
- Folge Netlify DNS Konfigurationsanleitung

---

## ✅ Teil 4: Verifikation


### Backend Health Check
```bash
curl https://provolution-api.onrender.com/health
```

Erwartete Response:
```json
{
  "status": "ok",
  "version": "1.0.0",
  "database": {
    "status": "healthy",
    "tables_count": 17,
    "users_count": 1,
    "challenges_count": 5
  }
}
```

### Frontend Funktionstest
1. Öffne: https://provolution-gamification.netlify.app
2. Prüfe API-Status Anzeige: "API verbunden • 5 Challenges • X Users"
3. Klicke "Anmelden" → Google OAuth Button sollte erscheinen
4. Login mit Google Account
5. Nach Login: Username, Level, XP sollten angezeigt werden

---

## 🔧 Troubleshooting

### Backend startet nicht
**Problem:** `ModuleNotFoundError`
**Lösung:**
```bash
pip install --upgrade -r requirements.txt
```

### Google OAuth schlägt fehl
**Problem:** "redirect_uri_mismatch"
**Lösung:** 
- Prüfe Authorized Redirect URIs in Google Cloud Console
- Stelle sicher dass exakte URL eingetragen ist (mit/ohne trailing slash)


### CORS Errors
**Problem:** Frontend kann Backend nicht erreichen
**Lösung:** Prüfe `app/main.py` CORS origins:
```python
origins = [
    "http://localhost:3000",
    "https://provolution-gamification.netlify.app"
]
```

### Render Free Tier Spin-down
**Problem:** Erste Request nach Inaktivität dauert lange
**Lösung:** Das ist normal für Free Tier (50s cold start)
- Upgrade auf Paid Tier für 24/7 Uptime
- Oder: Implementiere Health Check Ping alle 14 Minuten

---

## 📚 Weitere Ressourcen

- **API Dokumentation:** Siehe `API_DOCUMENTATION.md`
- **OAuth Flow:** Siehe `OAUTH_FLOW.md`
- **Backend Code:** `/backend/app/`
- **Frontend Code:** `/frontend/`
- **Render Dashboard:** https://dashboard.render.com
- **Netlify Dashboard:** https://app.netlify.com

---

## 🆘 Support

Bei Problemen oder Fragen:
- **GitHub Issues:** https://github.com/yokadeeds-dev/provolution-gamification/issues
- **Email:** support@provolution.org
- **Website:** https://provolution.org

---

**Version:** 1.0.0  
**Letzte Aktualisierung:** 29. Januar 2026  
**Autor:** Provolution Team
