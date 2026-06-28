# OneTrade Daily Profit Bot – Backend

## Deploy auf Render.com (5 Minuten)

### Schritt 1: GitHub Repo erstellen
1. github.com → "New repository" → Name: `onetrade-bot`
2. Alle Dateien hochladen (drag & drop)

### Schritt 2: Render.com
1. render.com → "New Web Service"
2. GitHub Repo verbinden
3. Einstellungen:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Environment:** Python 3

### Schritt 3: Umgebungsvariablen setzen
In Render → Environment:
- `TG_BOT_TOKEN` = dein Bot Token
- `TG_GROUP_ID`  = -1003900515439
- `BSCSCAN_API_KEY` = (optional, von bscscan.com)

### Schritt 4: Deploy
Render gibt dir eine URL: `https://onetrade-bot.onrender.com`
Diese URL ins Admin Panel unter Einstellungen eintragen.

## API Endpoints

| Method | URL | Beschreibung |
|--------|-----|-------------|
| GET | `/` | Health Check |
| GET/POST | `/test` | Test-Nachricht senden |
| POST | `/send` | Tagesgewinn posten |
| GET | `/wallet` | Wallet Balance abrufen |

## /send Body (JSON)
```json
{
  "pct": 1.82,
  "gained": 182.00,
  "kapital": 10000,
  "balance": 10182.00,
  "note": "Starke Performance!",
  "date": "28.06.2026",
  "time": "20:00"
}
```
