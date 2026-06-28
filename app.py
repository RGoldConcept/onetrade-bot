from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests, os, base64

app = Flask(__name__)
CORS(app)

@app.after_request
def ar(r):
    r.headers['Access-Control-Allow-Origin'] = '*'
    r.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    r.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    return r

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN","8601946674:AAGpvttyRBy7B81uU_frX8BQWk-N68lFTtQ")
GROUP_ID  = os.environ.get("TG_GROUP_ID","-1003900515439")

@app.route("/")
def index():
    return jsonify({"status":"ok","service":"OneTrade Bot"})

@app.route("/health")
def health():
    return jsonify({"status":"ok"})

@app.route("/test", methods=["GET","POST","OPTIONS"])
def test():
    if request.method=="OPTIONS": return jsonify({})
    r = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id":GROUP_ID,"text":"🤖 *OneTrade Bot* – Verbindung erfolgreich! ✅","parse_mode":"Markdown"},
        timeout=15)
    d = r.json()
    if d.get("ok"): return jsonify({"ok":True,"message":"Test-Nachricht gesendet!"})
    return jsonify({"ok":False,"error":d.get("description","Fehler")}), 400

@app.route("/send", methods=["POST","OPTIONS"])
def send():
    if request.method=="OPTIONS": return jsonify({})
    try:
        data = request.get_json(force=True, silent=True) or {}
        pct     = float(data.get("pct", 0))
        gained  = float(data.get("gained", 0))
        kapital = float(data.get("kapital", 0))
        note    = str(data.get("note", ""))
        date_str= str(data.get("date", ""))
        time_str= str(data.get("time", ""))
        png_b64 = str(data.get("image_b64", ""))

        sign  = "+" if pct >= 0 else ""
        emoji = "📈" if pct >= 0 else "📉"

        cap  = f"{emoji} *OneTrade – Tägliche Ausschüttung*\n\n"
        cap += f"📅 *Datum:* {date_str} | {time_str} Uhr\n"
        cap += "━━━━━━━━━━━━━━━━━\n"
        cap += f"💰 *Tagesgewinn:* `{sign}{pct:.4f}%`\n"
        if gained  > 0: cap += f"💵 *Ausgeschüttet:* `{gained:,.2f} USDT`\n"
        if kapital > 0: cap += f"🏦 *Eingesetztes Kapital:* `{kapital:,.2f} USDT`\n"
        cap += "━━━━━━━━━━━━━━━━━\n"
        if note: cap += f"📝 {note}\n━━━━━━━━━━━━━━━━━\n"
        cap += "🤖 _Powered by OneTrade AI System_\n"
        cap += "⚠️ _Vergangene Ergebnisse sind keine Garantie für die Zukunft._"

        has_image = png_b64 and len(png_b64) > 100
        if has_image:
            png_bytes = base64.b64decode(png_b64)
            r = requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                files={"photo": ("poster.png", png_bytes, "image/png")},
                data={"chat_id": GROUP_ID, "caption": cap, "parse_mode": "Markdown"},
                timeout=30)
        else:
            r = requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={"chat_id": GROUP_ID, "text": cap, "parse_mode": "Markdown", "disable_web_page_preview": True},
                timeout=15)

        d = r.json()
        if d.get("ok"):
            return jsonify({"ok": True, "with_image": bool(has_image)})
        return jsonify({"ok": False, "error": d.get("description", "Telegram Fehler")}), 400

    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/wallet")
def wallet():
    address  = request.args.get("address","0x17E384Fc02A4800e1cb8644CAB9daAeA9a2861A1")
    api_key  = os.environ.get("BSCSCAN_API_KEY","YourApiKeyToken")
    contract = "0x55d398326f99059fF775485246999027B3197955"
    try:
        r = requests.get(
            f"https://api.bscscan.com/api?module=account&action=tokenbalance"
            f"&contractaddress={contract}&address={address}&tag=latest&apikey={api_key}",
            timeout=10)
        d = r.json()
        if d.get("status") == "1":
            return jsonify({"ok": True, "balance": int(d["result"]) / 1e18})
        return jsonify({"ok": False, "error": d.get("message")}), 400
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
