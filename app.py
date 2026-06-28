from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import os
import base64

app = Flask(__name__)

# CORS komplett offen - erlaubt alle Origins inkl. file://
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=False)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
def options_handler(path):
    return jsonify({}), 200

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "8601946674:AAGpvttyRBy7B81uU_frX8BQWk-N68lFTtQ")
GROUP_ID  = os.environ.get("TG_GROUP_ID",  "-1003900515439")

def send_tg_text(text):
    r = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id": GROUP_ID, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": True},
        timeout=15
    )
    return r.json()

def send_tg_photo_b64(png_b64, caption):
    png_bytes = base64.b64decode(png_b64)
    r = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
        files={"photo": ("poster.png", png_bytes, "image/png")},
        data={"chat_id": GROUP_ID, "caption": caption, "parse_mode": "Markdown"},
        timeout=30
    )
    return r.json()

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/test", methods=["GET", "POST"])
def test():
    result = send_tg_text("🤖 *OneTrade Bot* – Verbindung erfolgreich! ✅")
    if result.get("ok"):
        return jsonify({"ok": True, "message": "Test-Nachricht gesendet!"})
    return jsonify({"ok": False, "error": result.get("description", "Fehler")}), 400

@app.route("/debug", methods=["POST"])
def debug():
    data = request.get_json()
    if not data:
        return jsonify({"ok": False, "error": "Kein JSON"})
    has_image = bool(data.get("image_b64", ""))
    img_len = len(data.get("image_b64", ""))
    return jsonify({
        "ok": True,
        "has_image": has_image,
        "image_b64_length": img_len,
        "pct": data.get("pct"),
    })

@app.route("/send", methods=["POST"])
def send():
    data = request.get_json()
    if not data:
        return jsonify({"ok": False, "error": "Kein JSON Body"}), 400

    pct      = float(data.get("pct", 0))
    gained   = float(data.get("gained", 0))
    kapital  = float(data.get("kapital", 0))
    balance  = float(data.get("balance", 0))
    note     = data.get("note", "")
    date_str = data.get("date", "")
    time_str = data.get("time", "")
    png_b64  = data.get("image_b64", "")

    sign  = "+" if pct >= 0 else ""
    emoji = "📈" if pct >= 0 else "📉"

    caption = f"{emoji} *OneTrade – Tägliche Ausschüttung*\n\n"
    caption += f"📅 *Datum:* {date_str} | {time_str} Uhr\n"
    caption += "━━━━━━━━━━━━━━━━━\n"
    caption += f"💰 *Tagesgewinn:* `{sign}{pct:.4f}%`\n"
    if gained > 0: caption += f"💵 *Ausgeschüttet:* `{gained:,.2f} USDT`\n"
    if kapital > 0: caption += f"🏦 *Eingesetztes Kapital:* `{kapital:,.2f} USDT`\n"
    if balance > 0: caption += f"📊 *Wallet-Stand:* `{balance:,.2f} USDT`\n"
    caption += "━━━━━━━━━━━━━━━━━\n"
    if note: caption += f"📝 {note}\n━━━━━━━━━━━━━━━━━\n"
    caption += "🤖 _Powered by OneTrade AI System_\n"
    caption += "⚠️ _Vergangene Ergebnisse sind keine Garantie für die Zukunft._"

    if png_b64:
        result = send_tg_photo_b64(png_b64, caption)
    else:
        result = send_tg_text(caption)

    if result.get("ok"):
        return jsonify({"ok": True, "with_image": bool(png_b64)})
    return jsonify({"ok": False, "error": result.get("description", "Fehler")}), 400

@app.route("/wallet", methods=["GET"])
def wallet():
    address  = request.args.get("address", "0x17E384Fc02A4800e1cb8644CAB9daAeA9a2861A1")
    api_key  = os.environ.get("BSCSCAN_API_KEY", "YourApiKeyToken")
    contract = "0x55d398326f99059fF775485246999027B3197955"
    url = (f"https://api.bscscan.com/api?module=account&action=tokenbalance"
           f"&contractaddress={contract}&address={address}&tag=latest&apikey={api_key}")
    try:
        r = requests.get(url, timeout=10)
        d = r.json()
        if d.get("status") == "1":
            return jsonify({"ok": True, "balance": int(d["result"]) / 1e18})
        return jsonify({"ok": False, "error": d.get("message")}), 400
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
