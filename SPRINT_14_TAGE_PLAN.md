# 🎯 PROVOLUTION: Realistischer 14-Tage-Sprint
## Stand: 29.01.2026 | Ziel: Förderantrag-Ready

---

## 📊 AUSGANGSLAGE (Ehrliche Bestandsaufnahme)

### ✅ Was du HAST (mehr als gedacht!)
- **FastAPI-Backend** (Port 8001) - funktionsfähig
- **Frontend** (Port 3000) - Login, Challenges, CO₂-Rechner
- **SQLite-Datenbank** mit Schema
- **24 Emissionsfaktoren** (UBA/TREMOD/ifeu)
- **SEC-Score Integration** (unique!)
- **Provolution-Framework** (5 Bände, wissenschaftlich fundiert)

### ❌ Was FEHLT für Förderantrag
1. Live-Demo (nur lokal)
2. DSGVO-Compliance (Privacy Policy)
3. Vereins-Registrierung
4. Screenshots/Dokumentation für Antrag

### ⚠️ Deine Constraints (realistisch)
- Einzelperson, nebenberuflich
- Keine Bonität (nur Zuschüsse, keine Kredite)
- Begrenzte Zeit pro Tag (~3-4h produktiv)
- Technisch versiert, aber kein DevOps-Experte

---

## 🗓️ DER PLAN: 14 TAGE, 3 TRACKS PARALLEL

### TRACK A: App Live (Priorität 1)
### TRACK B: Verein Gründen (Priorität 2)  
### TRACK C: Förderantrag (Priorität 3)

---

## WOCHE 1: FOUNDATION

### 📅 TAG 1 (Mi, 29.01.) - SETUP
**Ziel:** Deployment-Umgebung vorbereiten

| Zeit | Task | Track |
|------|------|-------|
| 1h | Render.com Account erstellen (GitHub OAuth) | A |
| 1h | `render.yaml` + `Procfile` erstellen | A |
| 30min | Gründungsmitglieder kontaktieren (3 Personen) | B |
| 30min | Satzung personalisieren (Namen eintragen) | B |

**Deliverables:**
- [ ] Render-Account aktiv
- [ ] Repo `provolution-gamification` auf GitHub
- [ ] 3 Gründungsmitglieder zugesagt

---

### 📅 TAG 2 (Do, 30.01.) - DEPLOY ATTEMPT 1
**Ziel:** Erste Version live

| Zeit | Task | Track |
|------|------|-------|
| 2h | Backend auf Render deployen | A |
| 1h | Fehler debuggen (erwartet!) | A |
| 1h | Satzung von 3 Personen unterschreiben lassen | B |

**Deliverables:**
- [ ] Backend läuft auf `*.onrender.com` (oder Fehlerliste)
- [ ] Satzung mit 3+ Unterschriften (Scan)

---

### 📅 TAG 3 (Fr, 31.01.) - STABILISIEREN
**Ziel:** App funktioniert online

| Zeit | Task | Track |
|------|------|-------|
| 2h | Deploy-Probleme lösen | A |
| 1h | Frontend auf Netlify deployen (Static) | A |
| 1h | Notar-Termin buchen (nächste Woche) | B |

**Deliverables:**
- [ ] Backend API erreichbar
- [ ] Frontend unter `app.provolution.org` (Subdomain)
- [ ] Notar-Termin bestätigt

---

### 📅 TAG 4-5 (Sa/So, 01-02.02.) - WOCHENENDE PAUSE
**Optional:** Dokumentation lesen, Perplexity-Recherche verdauen

---

### 📅 TAG 6 (Mo, 03.02.) - DSGVO + POLISH
**Ziel:** Rechtlich abgesichert

| Zeit | Task | Track |
|------|------|-------|
| 1h | Privacy Policy generieren (dsgvo-generator.de) | A |
| 1h | Impressum erstellen | A |
| 1h | Cookie-Banner (wenn Analytics) | A |
| 1h | Hans Sauer Stiftung Antrag vorbereiten | C |

**Deliverables:**
- [ ] `/privacy` und `/impressum` Seiten live
- [ ] Antrags-Entwurf Hans Sauer (50%)

---

### 📅 TAG 7 (Di, 04.02.) - NOTAR
**Ziel:** Verein notariell angemeldet

| Zeit | Task | Track |
|------|------|-------|
| 2h | Notar-Termin (du + 1 Vorstand) | B |
| 1h | Post an Amtsgericht (Notar macht meist) | B |
| 1h | Screenshots der App für Antrag | C |

**Deliverables:**
- [ ] Vereinsanmeldung beim Notar eingereicht
- [ ] 5+ App-Screenshots für Förderantrag

---

## WOCHE 2: ANTRAG + FINISH

### 📅 TAG 8 (Mi, 05.02.) - ANTRAG SCHREIBEN
**Ziel:** Hans Sauer Antrag fertig

| Zeit | Task | Track |
|------|------|-------|
| 3h | Hans Sauer Antrag finalisieren | C |
| 1h | App-Testing (10 Testdurchläufe) | A |

**Deliverables:**
- [ ] Antrag eingereicht (Online-Formular)
- [ ] App getestet, Bugs notiert

---

### 📅 TAG 9 (Do, 06.02.) - BUGFIX
**Ziel:** Kritische Bugs beheben

| Zeit | Task | Track |
|------|------|-------|
| 3h | Top-3 Bugs fixen | A |
| 1h | Finanzamt-Formulare vorbereiten (Gemeinnützigkeit) | B |

---

### 📅 TAG 10 (Fr, 07.02.) - HAGEN-KONTAKT
**Ziel:** Erste Partneranfrage

| Zeit | Task | Track |
|------|------|-------|
| 1h | E-Mail an Dr. Noroschat (Hagen UDP) | C |
| 1h | E-Mail an Stadt Hamm (Klimaschutzbeauftragter) | C |
| 2h | App-Optimierung (Mobile Check) | A |

**Deliverables:**
- [ ] Hagen-Mail gesendet
- [ ] Hamm-Mail gesendet
- [ ] App auf Mobile getestet

---

### 📅 TAG 11-12 (Sa/So, 08-09.02.) - WOCHENENDE
**Optional:** NKI-Antrag vorbereiten

---

### 📅 TAG 13 (Mo, 10.02.) - NKI VORBEREITEN
**Ziel:** NKI-Antrag 50% fertig

| Zeit | Task | Track |
|------|------|-------|
| 2h | NKI-Antrag ausfüllen (klimaschutz.de) | C |
| 1h | Budget-Kalkulation | C |
| 1h | Partner-Brief für Hamm/Hagen | C |

---

### 📅 TAG 14 (Di, 11.02.) - SPRINT ABSCHLUSS
**Ziel:** Alles dokumentiert, nächste Phase geplant

| Zeit | Task | Track |
|------|------|-------|
| 1h | Sprint-Review: Was geschafft? | - |
| 1h | GitHub README aktualisieren | A |
| 1h | Phase-2-Planung | - |
| 1h | Celebration! 🎉 | - |

---

## 📋 CHECKLISTE: SPRINT-ERFOLG

### Minimum Viable Success (MUSS erreicht werden)
- [ ] App live unter `*.onrender.com` oder `app.provolution.org`
- [ ] Verein beim Notar angemeldet
- [ ] 1 Förderantrag eingereicht (Hans Sauer)
- [ ] Privacy Policy + Impressum online

### Nice to Have
- [ ] Hagen/Hamm-Kontakt hergestellt
- [ ] NKI-Antrag 50% fertig
- [ ] Mobile-optimiert
- [ ] 3+ Test-User registriert

### Bonus (wenn Zeit)
- [ ] Leaderboard funktioniert
- [ ] PLZ-Aggregation
- [ ] Gemeinnützigkeit beantragt

---

## 🔧 TECHNISCHE QUICK-GUIDES

### Render.com Deploy (5 Schritte)

```bash
# 1. In gamification/backend/
cd "C:\Users\yoka\Documents\CLAUDE WORKSPACE\Save the Provolution\80_MARKETING\gamification\backend"

# 2. Procfile erstellen
echo "web: uvicorn app.main:app --host 0.0.0.0 --port $PORT" > Procfile

# 3. render.yaml erstellen (siehe unten)

# 4. Git Push
git add .
git commit -m "Render deploy config"
git push origin main

# 5. Auf render.com: New Web Service → GitHub Repo wählen → Deploy
```

### render.yaml Inhalt:
```yaml
services:
  - type: web
    name: provolution-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
```

---

## 📧 E-MAIL TEMPLATES

### An Dr. Noroschat (Hagen UDP)
```
Betreff: Kooperationsanfrage: Citizen-CO₂-Daten für Hagen UDP

Sehr geehrter Herr Dr. Noroschat,

als Entwickler der Open-Source-Plattform "Provolution" (Citizen-Science 
CO₂-Tracking mit Gamification) aus Hamm interessiere ich mich für eine 
Pilot-Integration mit der Hagen Urban Data Platform.

Provolution liefert anonyme, PLZ-aggregierte Haushalts-CO₂-Daten, die 
Ihre Sensor-Daten ideal ergänzen würden (Bottom-Up + Top-Down).

Live-Demo: [app.provolution.org]
GitHub: github.com/yokadeeds-dev/provolution-gamification

Hätten Sie Interesse an einem 15-minütigen Austausch?

Mit freundlichen Grüßen
[Ihr Name]
Provolution / Hamm
```

### An Stadt Hamm (Klimaschutz)
```
Betreff: Citizen-Science Klimaschutz-App: Pilotprojekt für Hamm?

Sehr geehrte Damen und Herren,

ich entwickle "Provolution", eine Citizen-Science-Plattform für 
CO₂-Tracking mit Gamification-Elementen. Als Hammer Bürger würde 
ich gerne einen lokalen Pilot starten.

Die App liefert anonyme, PLZ-basierte Daten für kommunale 
Klimaberichte - ähnlich dem Hagen UDP-Projekt.

Gibt es Interesse an einem Austausch mit dem Klimaschutzbeauftragten?

Mit freundlichen Grüßen
[Ihr Name]
```

---

## 💰 BUDGET-REALITÄT (Phase 1)

| Posten | Kosten | Quelle |
|--------|--------|--------|
| Render.com (3 Monate) | €0 | Free Tier |
| Domain (bereits vorhanden) | €0 | provolution.org |
| Notar Vereinsgründung | €35-60 | Eigenkapital |
| Erste Hosting-Kosten | €0-21 | Free Tier / später |
| **Gesamt Phase 1** | **~€50** | Machbar! |

**Förderung (wenn bewilligt):**
- Hans Sauer: €20.000-50.000
- NKI (später): €50.000-100.000

---

## ⚠️ RISIKEN + MITIGATION

| Risiko | Wahrscheinlichkeit | Mitigation |
|--------|-------------------|------------|
| Deploy scheitert | Mittel | Backup: PythonAnywhere (einfacher) |
| Notar-Termin verzögert | Niedrig | Online-Notar als Alternative |
| Förderung abgelehnt | Mittel | 3 Anträge parallel (diversifizieren) |
| Burnout | Hoch | Strikte Pausen, Wochenende frei |

---

## 🎯 NACH DEM SPRINT (Phase 2, Feb-März)

1. **VR-Eintrag abwarten** (2-4 Wochen)
2. **Gemeinnützigkeit beantragen** (Finanzamt)
3. **NKI-Antrag finalisieren** (mit Partner-Zusagen)
4. **Hagen-PoC starten** (wenn Kontakt positiv)
5. **10 Beta-User gewinnen** (Hamm-Lokalnetzwerk)

---

## 📌 DAILY CHECK-IN FORMAT

Jeden Abend 5 Minuten:
```
✅ Was habe ich heute geschafft?
❌ Was hat nicht geklappt?
📅 Was ist morgen Prio 1?
🔋 Energie-Level (1-10)?
```

---

**Du schaffst das! 14 Tage, fokussiert, realistisch. 🚀**

*Erstellt: 29.01.2026 | Nächstes Review: 11.02.2026*
