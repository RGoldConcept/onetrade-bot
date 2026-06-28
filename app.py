from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import base64

app = Flask(__name__)
CORS(app)

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "8601946674:AAGpvttyRBy7B81uU_frX8BQWk-N68lFTtQ")
GROUP_ID  = os.environ.get("TG_GROUP_ID",  "-1003900515439")

def build_poster_html(pct, gained, kapital, date_str):
    sign = "+" if pct >= 0 else ""
    pct_str = f"{sign}{pct:.2f}%"
    gained_str = f"+{gained:,.2f} USDT" if gained > 0 else ""
    kap_str = f"{kapital:,.2f} USDT" if kapital > 0 else ""
    bars = [18,22,20,28,30,40,52,68,80,95]
    bar_html = "".join(
        f'<div style="flex:1;height:{h}%;background:linear-gradient(180deg,#00dca8,#0ea5e9);'
        f'opacity:{0.3+i/len(bars)*0.7:.2f};border-radius:3px 3px 0 0;box-shadow:0 0 6px #00dca840;"></div>'
        for i, h in enumerate(bars)
    )
    extra = ""
    if gained_str:
        extra = f'<div style="font-size:11px;color:#00dca870;text-align:center;margin-bottom:4px;">💵 {gained_str}'
        if kap_str:
            extra += f' &nbsp;|&nbsp; 🏦 {kap_str}'
        extra += '</div>'

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
*{{margin:0;padding:0;box-sizing:border-box;}}
body{{width:600px;height:600px;overflow:hidden;background:#050d1a;font-family:Arial,sans-serif;color:#fff;position:relative;}}
.dots{{position:absolute;inset:0;background-image:radial-gradient(circle,#00dca818 1px,transparent 1px);background-size:28px 28px;}}
.wrap{{position:relative;z-index:1;display:flex;flex-direction:column;align-items:center;padding:22px 28px 14px;height:100%;}}
.logo-t{{width:36px;height:36px;position:relative;margin-bottom:6px;}}
.logo-t::before{{content:"";position:absolute;top:0;left:50%;transform:translateX(-50%);width:36px;height:6px;background:linear-gradient(90deg,#00dca8,#60efff);border-radius:3px;}}
.logo-t::after{{content:"";position:absolute;top:6px;left:50%;transform:translateX(-50%);width:6px;height:30px;background:linear-gradient(180deg,#00dca8,#0ea5e9);border-radius:3px;}}
</style></head><body>
<div class="dots"></div>
<div class="wrap">
  <div class="logo-t"></div>
  <div style="font-size:13px;font-weight:900;letter-spacing:4px;margin-bottom:2px;">ONE<span style="color:#00dca8;">TRADE</span></div>
  <div style="font-size:20px;font-weight:900;letter-spacing:5px;margin:2px 0;">DAILY PERFORMANCE</div>
  <div style="font-size:10px;color:#4a7090;letter-spacing:2px;margin-bottom:8px;">📅 {date_str}</div>
  <div style="width:100%;background:linear-gradient(135deg,#0a1a2e,#0d2040);border:1.5px solid #00dca8;border-radius:14px;padding:14px 20px 10px;position:relative;overflow:hidden;margin-bottom:10px;">
    <div style="position:absolute;right:16px;top:50%;transform:translateY(-50%);font-size:48px;opacity:0.12;">↗</div>
    <div style="font-size:9px;color:#00dca8;letter-spacing:3px;text-align:center;margin-bottom:2px;">TODAY'S RESULT</div>
    <div style="font-size:64px;font-weight:900;color:#00dca8;text-align:center;line-height:1;text-shadow:0 0 30px #00dca880,0 0 60px #00dca840;letter-spacing:-2px;">{pct_str}</div>
    <div style="font-size:9px;color:#fff;letter-spacing:3px;text-align:center;margin:4px 0 2px;opacity:0.5;">· DAILY PROFIT ·</div>
    <div style="font-size:10px;color:#fff;text-align:center;opacity:0.4;">CONSISTENCY. STRATEGY. <span style="color:#00dca8;opacity:1;">SUCCESS.</span></div>
  </div>
  {extra}
  <div style="display:flex;width:100%;margin-bottom:8px;">
    {''.join(f'''<div style="flex:1;display:flex;flex-direction:column;align-items:center;padding:6px 2px;border-right:1px solid #1a2d4a;">
      <div style="font-size:16px;margin-bottom:2px;">{icon}</div>
      <div style="font-size:13px;font-weight:900;">100%</div>
      <div style="font-size:7px;color:#00dca8;letter-spacing:1px;text-align:center;">{lbl}</div>
      <div style="font-size:7px;color:#4a7090;text-align:center;">{sub}</div>
    </div>''' for icon,lbl,sub in [("🎯","FOCUS","ON YOUR GOALS"),("📊","SYSTEM","DRIVEN"),("🛡️","RISK","MANAGED"),("👥","TEAM","STRONG")])}
  </div>
  <div style="width:100%;display:flex;align-items:flex-end;gap:4px;height:60px;margin-bottom:6px;padding:0 4px;">
    {bar_html}
  </div>
  <div style="width:100%;background:#0a1525;border:1px solid #1a2d4a;border-radius:10px;padding:7px 12px;display:flex;align-items:center;gap:8px;margin-bottom:4px;">
    <div style="font-size:24px;color:#00dca8;line-height:1;font-family:Georgia,serif;flex-shrink:0;">"</div>
    <div style="font-size:9px;color:#fff;line-height:1.5;flex:1;">WE DON'T CHASE THE MARKET.<br/><strong style="color:#00dca8;">WE FOLLOW THE PLAN.</strong></div>
    <div style="font-size:8px;font-weight:900;color:#00dca8;letter-spacing:2px;flex-shrink:0;">ONE<br/>TRADE</div>
  </div>
  <div style="font-size:7px;color:#1a3050;letter-spacing:0.5px;text-align:center;">PAST PERFORMANCE IS NOT INDICATIVE OF FUTURE RESULTS.</div>
</div></body></html>"""

def render_poster_to_png(html_content):
    """Render HTML to PNG using playwright"""
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 600, "height": 600})
            page.set_content(html_content)
            page.wait_for_timeout(500)
            png_bytes = page.screenshot(clip={"x":0,"y":0,"width":600,"height":600})
            browser.close()
            return png_bytes
    except Exception as e:
        return None

def send_tg_text(text):
    base = f"https://api.telegram.org/bot{BOT_TOKEN}"
    r = requests.post(f"{base}/sendMessage", json={
        "chat_id": GROUP_ID, "text": text,
        "parse_mode": "Markdown", "disable_web_page_preview": True
    }, timeout=15)
    return r.json()

def send_tg_photo(png_bytes, caption):
    base = f"https://api.telegram.org/bot{BOT_TOKEN}"
    r = requests.post(f"{base}/sendPhoto",
        files={"photo": ("poster.png", png_bytes, "image/png")},
        data={"chat_id": GROUP_ID, "caption": caption, "parse_mode": "Markdown"},
        timeout=30
    )
    return r.json()

@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "OneTrade Daily Profit Bot"})

@app.route("/test", methods=["GET", "POST"])
def test():
    result = send_tg_text("🤖 *OneTrade Bot* – Verbindung erfolgreich! ✅")
    if result.get("ok"):
        return jsonify({"ok": True, "message": "Test-Nachricht gesendet!"})
    return jsonify({"ok": False, "error": result.get("description", "Fehler")}), 400

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
    date_en  = data.get("date_en", date_str)

    sign  = "+" if pct >= 0 else ""
    emoji = "📈" if pct >= 0 else "📉"

    caption = f"""{emoji} *OneTrade – Tägliche Ausschüttung*

📅 *Datum:* {date_str} | {time_str} Uhr
━━━━━━━━━━━━━━━━━
💰 *Tagesgewinn:* `{sign}{pct:.4f}%`
"""
    if gained > 0:
        caption += f"💵 *Ausgeschüttet:* `{gained:,.2f} USDT`\n"
    if kapital > 0:
        caption += f"🏦 *Eingesetztes Kapital:* `{kapital:,.2f} USDT`\n"
    if balance > 0:
        caption += f"📊 *Wallet-Stand:* `{balance:,.2f} USDT`\n"
    caption += "━━━━━━━━━━━━━━━━━\n"
    if note:
        caption += f"📝 {note}\n━━━━━━━━━━━━━━━━━\n"
    caption += "🤖 _Powered by OneTrade AI System_\n"
    caption += "⚠️ _Vergangene Ergebnisse sind keine Garantie für die Zukunft._"

    # Poster als PNG generieren und mit Bild senden
    html_content = build_poster_html(pct, gained, kapital, date_en)
    png_bytes = render_poster_to_png(html_content)

    if png_bytes:
        result = send_tg_photo(png_bytes, caption)
    else:
        # Fallback: nur Text wenn Playwright nicht verfügbar
        result = send_tg_text(caption)

    if result.get("ok"):
        return jsonify({"ok": True, "message": "Gesendet!", "with_image": png_bytes is not None})
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
        return jsonify({"ok": False, "error": d.get("message", "API Fehler")}), 400
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
