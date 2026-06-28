from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)  # Erlaubt Calls vom Artifact/Browser

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "8601946674:AAGpvttyRBy7B81uU_frX8BQWk-N68lFTtQ")
GROUP_ID  = os.environ.get("TG_GROUP_ID",  "-1003900515439")

def send_tg(text=None, photo_url=None, caption=None):
    base = f"https://api.telegram.org/bot{BOT_TOKEN}"
    if photo_url:
        r = requests.post(f"{base}/sendPhoto", json={
            "chat_id": GROUP_ID,
            "photo": photo_url,
            "caption": caption or "",
            "parse_mode": "Markdown"
        }, timeout=15)
    else:
        r = requests.post(f"{base}/sendMessage", json={
            "chat_id": GROUP_ID,
            "text": text,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }, timeout=15)
    return r.json()

# ── Health Check ──────────────────────────────────────────────────────────────
@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "OneTrade Daily Profit Bot"})

# ── Bot testen ────────────────────────────────────────────────────────────────
@app.route("/test", methods=["GET", "POST"])
def test():
    result = send_tg("🤖 *OneTrade Bot* – Verbindung erfolgreich! ✅")
    if result.get("ok"):
        return jsonify({"ok": True, "message": "Test-Nachricht gesendet!"})
    return jsonify({"ok": False, "error": result.get("description", "Unbekannter Fehler")}), 400

# ── Nachricht senden ──────────────────────────────────────────────────────────
@app.route("/send", methods=["POST"])
def send():
    data = request.get_json()
    if not data:
        return jsonify({"ok": False, "error": "Kein JSON Body"}), 400

    pct          = float(data.get("pct", 0))
    gained       = float(data.get("gained", 0))
    kapital      = float(data.get("kapital", 0))
    balance      = float(data.get("balance", 0))
    note         = data.get("note", "")
    date_str     = data.get("date", "")
    time_str     = data.get("time", "")

    sign  = "+" if pct >= 0 else ""
    emoji = "📈" if pct >= 0 else "📉"

    text = f"""{emoji} *OneTrade – Tägliche Ausschüttung*

📅 *Datum:* {date_str} | {time_str} Uhr
━━━━━━━━━━━━━━━━━
💰 *Tagesgewinn:* `{sign}{pct:.4f}%`
💵 *Ausgeschüttet:* `{gained:,.2f} USDT`
"""
    if kapital > 0:
        text += f"🏦 *Eingesetztes Kapital:* `{kapital:,.2f} USDT`\n"
    if balance > 0:
        text += f"📊 *Wallet-Stand:* `{balance:,.2f} USDT`\n"

    text += "━━━━━━━━━━━━━━━━━\n"
    if note:
        text += f"📝 {note}\n━━━━━━━━━━━━━━━━━\n"

    text += "🤖 _Powered by OneTrade AI System_\n"
    text += "⚠️ _Vergangene Ergebnisse sind keine Garantie für die Zukunft._"

    result = send_tg(text=text)
    if result.get("ok"):
        return jsonify({"ok": True, "message": "Nachricht gesendet!"})
    return jsonify({"ok": False, "error": result.get("description", "Unbekannter Fehler")}), 400

# ── Wallet Balance abrufen (BSC) ──────────────────────────────────────────────
@app.route("/wallet", methods=["GET"])
def wallet():
    address  = request.args.get("address", "0x17E384Fc02A4800e1cb8644CAB9daAeA9a2861A1")
    api_key  = os.environ.get("BSCSCAN_API_KEY", "YourApiKeyToken")
    contract = "0x55d398326f99059fF775485246999027B3197955"

    url = (f"https://api.bscscan.com/api?module=account&action=tokenbalance"
           f"&contractaddress={contract}&address={address}"
           f"&tag=latest&apikey={api_key}")
    try:
        r = requests.get(url, timeout=10)
        d = r.json()
        if d.get("status") == "1":
            balance = int(d["result"]) / 1e18
            return jsonify({"ok": True, "balance": balance})
        return jsonify({"ok": False, "error": d.get("message", "API Fehler")}), 400
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
