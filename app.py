from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import requests
import os
import base64

HTML_PAGE = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>OneTrade · Daily Profit System</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { min-height:100vh; background:radial-gradient(ellipse at 20% 0%, #00dca808 0%, transparent 60%), #080e1a; color:#e2f0ff; font-family:'Inter','Segoe UI',sans-serif; font-size:14px; }
  a { color:#00dca8; }

  /* Header */
  .header { background:#0d1626; border-bottom:1px solid #1a2d4a; padding:16px 28px; display:flex; align-items:center; gap:14px; }
  .logo { width:38px; height:38px; background:linear-gradient(135deg,#00dca8,#0ea5e9); border-radius:9px; display:flex; align-items:center; justify-content:center; font-weight:900; font-size:15px; color:#000; flex-shrink:0; }
  .header-title { font-size:17px; font-weight:700; }
  .header-sub { font-size:12px; color:#4a6080; margin-top:1px; }
  .live-dot { width:8px; height:8px; border-radius:50%; background:#00dca8; box-shadow:0 0 8px #00dca8; margin-left:auto; }

  /* Nav */
  .nav { background:#0d1626; border-bottom:1px solid #1a2d4a; padding:10px 28px; display:flex; gap:4px; }
  .nav-btn { padding:7px 16px; border-radius:6px; border:none; cursor:pointer; font-size:13px; background:transparent; color:#4a6080; transition:all 0.15s; }
  .nav-btn.active { background:#00dca815; color:#00dca8; font-weight:600; }

  /* Main */
  .main { padding:24px 28px; max-width:980px; margin:0 auto; }
  .tab { display:none; }
  .tab.active { display:block; }

  /* Cards */
  .card { background:#0d1626; border:1px solid #1a2d4a; border-radius:12px; padding:20px; margin-bottom:16px; }
  .card-glow { background:#0d1626; border:1px solid #00dca840; border-radius:12px; padding:20px; margin-bottom:16px; box-shadow:0 0 28px #00dca812; }
  .grid2 { display:grid; grid-template-columns:1fr 1fr; gap:16px; }

  /* Labels */
  .lbl { font-size:11px; color:#4a6080; text-transform:uppercase; letter-spacing:0.08em; margin-bottom:6px; display:block; }

  /* Inputs */
  input, select { width:100%; background:#060d18; border:1px solid #1a2d4a; border-radius:8px; padding:10px 12px; color:#e2f0ff; font-size:14px; outline:none; box-sizing:border-box; margin-bottom:12px; }
  input:focus { border-color:#00dca840; }
  textarea { width:100%; background:#060d18; border:1px solid #1a2d4a; border-radius:8px; padding:10px 12px; color:#e2f0ff; font-size:12px; outline:none; resize:vertical; font-family:monospace; box-sizing:border-box; }

  /* Buttons */
  .btn-primary { width:100%; background:linear-gradient(135deg,#00dca8,#0ea5e9); border:none; border-radius:8px; padding:13px 24px; color:#000; font-weight:700; font-size:14px; cursor:pointer; margin-bottom:8px; }
  .btn-primary:disabled { background:#1a2d4a; color:#4a6080; cursor:not-allowed; }
  .btn-secondary { width:100%; background:#00dca815; border:1px solid #00dca840; border-radius:8px; padding:10px 20px; color:#00dca8; font-weight:600; font-size:13px; cursor:pointer; margin-bottom:8px; }
  .btn-ghost { background:transparent; border:1px solid #1a2d4a; border-radius:8px; padding:8px 14px; color:#4a6080; font-size:12px; cursor:pointer; }

  /* Mode buttons */
  .mode-row { display:flex; gap:6px; margin-bottom:16px; }
  .mode-btn { flex:1; padding:9px 6px; border-radius:8px; border:1px solid #1a2d4a; background:transparent; color:#4a6080; font-size:12px; cursor:pointer; transition:all 0.15s; }
  .mode-btn.active { border-color:#00dca840; background:#00dca815; color:#00dca8; font-weight:700; }

  /* Big number */
  .big-pct { font-size:36px; font-weight:900; letter-spacing:-1.5px; line-height:1; }
  .pos { color:#00dca8; } .neg { color:#f43f5e; }

  /* Result box */
  .result-box { background:#00dca812; border:1px solid #00dca840; border-radius:8px; padding:10px 14px; margin-bottom:12px; }

  /* Log box */
  .log-box { background:#060d18; border:1px solid #1a2d4a; border-radius:8px; padding:10px 14px; font-size:12px; font-family:monospace; margin-top:8px; word-break:break-word; min-height:36px; }
  .log-ok { border-color:#00dca840; color:#00dca8; }
  .log-err { border-color:#f43f5e40; color:#f43f5e; }
  .log-info { color:#4a6080; }

  /* Divider */
  .divider { border-top:1px solid #1a2d4a; margin:14px 0; }

  /* Badge */
  .badge-ok { display:inline-block; padding:2px 9px; border-radius:20px; font-size:11px; font-weight:600; background:#00dca820; color:#00dca8; border:1px solid #00dca840; }
  .badge-err { display:inline-block; padding:2px 9px; border-radius:20px; font-size:11px; font-weight:600; background:#f43f5e20; color:#f43f5e; border:1px solid #f43f5e40; }

  /* Info box */
  .info-box { background:#060d18; border:1px solid #1a2d4a; border-radius:8px; padding:14px; font-size:12px; color:#4a6080; line-height:1.9; }

  /* Poster iframe */
  .poster-wrap { border:1px solid #00dca840; border-radius:10px; overflow:hidden; background:#050d1a; margin-top:12px; }
  .poster-wrap iframe { width:100%; height:340px; border:none; display:block; }

  /* History row */
  .history-row { display:flex; justify-content:space-between; align-items:center; padding:10px 0; border-bottom:1px solid #1a2d4a; }
  .history-row:last-child { border-bottom:none; }

  /* Warning */
  .warn { background:#f43f5e10; border:1px solid #f43f5e30; border-radius:8px; padding:8px 12px; font-size:12px; color:#f43f5e; margin-top:6px; }
  .success { background:#00dca810; border:1px solid #00dca840; border-radius:8px; padding:8px 12px; font-size:12px; color:#00dca8; margin-top:6px; }

  /* Backend URL highlight */
  .backend-box { background:#00dca810; border:1px solid #00dca840; border-radius:10px; padding:12px 14px; margin-bottom:14px; }
</style>
</head>
<body>

<!-- Header -->
<div class="header">
  <div class="logo">OT</div>
  <div>
    <div class="header-title">OneTrade · Daily Profit System</div>
    <div class="header-sub">Automatisiertes Telegram-Posting · BSC Wallet Tracker</div>
  </div>
  <div class="live-dot"></div>
</div>

<!-- Nav -->
<div class="nav">
  <button class="nav-btn active" onclick="showTab('post')">✍️ Post erstellen</button>
  <button class="nav-btn" onclick="showTab('dashboard')">📊 Dashboard</button>
  <button class="nav-btn" onclick="showTab('history')">📋 Verlauf</button>
  <button class="nav-btn" onclick="showTab('settings')">⚙️ Einstellungen</button>
</div>

<div class="main">

  <!-- ── POST TAB ─────────────────────────────────────────────────────────── -->
  <div id="tab-post" class="tab active">
    <div class="grid2">
      <!-- Links -->
      <div>
        <div class="card">
          <span class="lbl">Berechnungsmethode</span>
          <div class="mode-row">
            <button class="mode-btn active" onclick="setMode('kapital',this)">💰 Kapital</button>
            <button class="mode-btn" onclick="setMode('balance',this)">📊 Differenz</button>
            <button class="mode-btn" onclick="setMode('manual',this)">✏️ Manuell</button>
          </div>

          <!-- Kapital Mode -->
          <div id="mode-kapital">
            <span class="lbl">Eingesetztes Kapital (USDT)</span>
            <input id="kapital" type="number" placeholder="z.B. 10000" oninput="calcPct()">
            <span class="lbl">Heute ausgeschüttet (USDT)</span>
            <input id="ausschuettung" type="number" placeholder="z.B. 182.00" oninput="calcPct()">
          </div>

          <!-- Balance Mode -->
          <div id="mode-balance" style="display:none">
            <span class="lbl">Wallet-Stand gestern (USDT)</span>
            <input id="prev-bal" type="number" placeholder="z.B. 10000.00" oninput="calcPct()">
            <span class="lbl">Wallet-Stand heute (USDT)</span>
            <input id="curr-bal" type="number" placeholder="z.B. 10182.00" oninput="calcPct()">
          </div>

          <!-- Manual Mode -->
          <div id="mode-manual" style="display:none">
            <span class="lbl">Prozentsatz eingeben</span>
            <input id="manual-pct" type="number" step="0.0001" placeholder="z.B. 1.82" oninput="calcPct()">
          </div>

          <div id="calc-result" style="display:none" class="result-box">
            <div style="font-size:11px;color:#4a6080;">Berechnet</div>
            <div id="calc-display" class="big-pct pos" style="font-size:24px;"></div>
            <div id="calc-formula" style="font-size:11px;color:#4a6080;"></div>
          </div>

          <span class="lbl">Optionale Notiz</span>
          <input id="note" type="text" placeholder="z.B. Starke Performance heute!">
        </div>

        <!-- Poster -->
        <div class="card">
          <span class="lbl">OneTrade Poster</span>
          <button class="btn-secondary" onclick="generatePoster()">🎨 Poster generieren</button>
          <div id="poster-container" style="display:none">
            <canvas id="poster-canvas" style="display:none;"></canvas>
            <div class="poster-wrap">
              <img id="poster-img" style="width:100%;display:none;border-radius:8px;" alt="Poster">
            </div>
            <div style="font-size:11px;color:#00dca8;margin-top:6px;">✅ Bild wird automatisch mit gesendet</div>
          </div>
        </div>
      </div>

      <!-- Rechts -->
      <div>
        <div class="card-glow">
          <span class="lbl">Telegram Caption Vorschau</span>
          <textarea id="caption-preview" rows="12" readonly></textarea>
        </div>

        <div class="card">
          <span class="lbl">Tagesgewinn</span>
          <div id="pct-display" class="big-pct pos" style="margin-bottom:4px;">0.0000%</div>
          <div id="gained-display" style="font-size:12px;color:#4a6080;margin-bottom:16px;"></div>

          <button class="btn-primary" id="send-btn" onclick="sendPost()">📤 Jetzt an Telegram senden</button>
          <button class="btn-ghost" style="width:100%" onclick="testBackend()">🔧 Backend & Bot testen</button>

          <div id="send-log" class="log-box log-info" style="display:none;"></div>

          <div class="divider"></div>
          <div style="font-size:12px;color:#4a6080;line-height:1.8;">
            <strong style="color:#e2f0ff;">Backend:</strong> <span id="backend-display">nicht eingetragen</span><br>
            <strong style="color:#e2f0ff;">Gruppe:</strong> <span id="group-display">-1003900515439</span><br>
            <div style="margin-top:6px;padding:6px 10px;background:#060d18;border-radius:6px;font-size:11px;">
              ⚠️ Bot muss <strong style="color:#00dca8;">Admin</strong> in der Gruppe sein
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- ── DASHBOARD TAB ───────────────────────────────────────────────────── -->
  <div id="tab-dashboard" class="tab">
    <div class="grid2" style="margin-bottom:16px;">
      <div class="card-glow">
        <span class="lbl">Wallet Balance (USDT)</span>
        <div id="wallet-balance" style="font-size:22px;font-weight:700;">–</div>
        <div style="font-size:12px;color:#4a6080;margin-top:4px;">
          <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:#00dca8;box-shadow:0 0 8px #00dca8;margin-right:6px;"></span>BSC Wallet
        </div>
        <button class="btn-ghost" style="margin-top:12px;" onclick="fetchWallet()">🔄 Aktualisieren</button>
      </div>
      <div class="card">
        <span class="lbl">Letzter Tagesgewinn</span>
        <div id="last-pct" style="font-size:28px;font-weight:800;color:#4a6080;">–</div>
        <div id="last-info" style="font-size:12px;color:#4a6080;margin-top:4px;"></div>
      </div>
    </div>
    <div class="card">
      <span class="lbl">Wallet-Adresse</span>
      <div style="font-family:monospace;font-size:12px;color:#00dca8;word-break:break-all;">0x17E384Fc02A4800e1cb8644CAB9daAeA9a2861A1</div>
    </div>
  </div>

  <!-- ── HISTORY TAB ─────────────────────────────────────────────────────── -->
  <div id="tab-history" class="tab">
    <div class="card">
      <span class="lbl">Gesendete Posts</span>
      <div id="history-list"><div style="color:#4a6080;font-size:13px;">Noch keine Posts gesendet.</div></div>
    </div>
  </div>

  <!-- ── SETTINGS TAB ────────────────────────────────────────────────────── -->
  <div id="tab-settings" class="tab">
    <div class="card">
      <span class="lbl">Konfiguration</span>

      <div class="backend-box" style="margin-bottom:14px;">
        <span class="lbl" style="color:#00dca8;">🔗 Backend URL (Render.com)</span>
        <input id="backend-url" type="text" placeholder="https://onetrade-bot.onrender.com" oninput="saveSettings()" style="margin-bottom:4px;">
        <div id="backend-status" style="font-size:11px;color:#4a6080;"></div>
      </div>

      <span class="lbl">Telegram Bot Token</span>
      <input id="tg-token" type="text" value="8601946674:AAGpvttyRBy7B81uU_frX8BQWk-N68lFTtQ" oninput="saveSettings()">

      <span class="lbl">Telegram Gruppen-ID</span>
      <input id="tg-group" type="text" value="-1003900515439" oninput="saveSettings()">

      <span class="lbl">BscScan API-Key (für Live-Wallet)</span>
      <input id="bsc-key" type="text" placeholder="Kostenlos auf bscscan.com → API Keys" oninput="saveSettings()">

      <button class="btn-secondary" onclick="testBackend()">🔧 Backend & Bot testen</button>
      <div id="settings-log" class="log-box log-info" style="display:none;margin-top:8px;"></div>
    </div>

    <div class="card">
      <span class="lbl">Täglicher Workflow</span>
      <div class="info-box">
        1️⃣ Tab <strong style="color:#e2f0ff;">"Post erstellen"</strong> öffnen<br>
        2️⃣ Kapital + heutige Ausschüttung eingeben<br>
        3️⃣ <strong style="color:#00dca8;">🎨 Poster generieren</strong> → Screenshot machen<br>
        4️⃣ <strong style="color:#00dca8;">📤 An Telegram senden</strong> (Text-Post automatisch)<br>
        5️⃣ Poster-Screenshot manuell als Bild in Telegram posten
      </div>
    </div>
  </div>

</div>

<script>
// ── State ─────────────────────────────────────────────────────────────────────
let calcMode = 'kapital';
let currentPct = 0;
let gainedAmount = 0;
let kapitalVal = 0;
let history = JSON.parse(localStorage.getItem('ot_history') || '[]');

// ── Settings ──────────────────────────────────────────────────────────────────
function loadSettings() {
  // Automatisch eigene URL erkennen wenn auf Render gehostet
  const selfUrl = window.location.origin !== 'null' && window.location.origin !== 'file://' ? window.location.origin : '';
  const bu = localStorage.getItem('ot_backend') || selfUrl || 'https://onetrade-bot.onrender.com';
  const tt = localStorage.getItem('ot_token') || '8601946674:AAGpvttyRBy7B81uU_frX8BQWk-N68lFTtQ';
  const tg = localStorage.getItem('ot_group') || '-1003900515439';
  const bk = localStorage.getItem('ot_bsckey') || '';
  document.getElementById('backend-url').value = bu;
  document.getElementById('tg-token').value = tt;
  document.getElementById('tg-group').value = tg;
  document.getElementById('bsc-key').value = bk;
  updateBackendDisplay();
}

function saveSettings() {
  localStorage.setItem('ot_backend', document.getElementById('backend-url').value);
  localStorage.setItem('ot_token', document.getElementById('tg-token').value);
  localStorage.setItem('ot_group', document.getElementById('tg-group').value);
  localStorage.setItem('ot_bsckey', document.getElementById('bsc-key').value);
  updateBackendDisplay();
}

function updateBackendDisplay() {
  const bu = document.getElementById('backend-url').value;
  document.getElementById('backend-display').textContent = bu || 'nicht eingetragen';
  document.getElementById('group-display').textContent = document.getElementById('tg-group').value;
  const bs = document.getElementById('backend-status');
  bs.textContent = bu ? '✅ URL gespeichert' : '⚠️ Pflichtfeld!';
  bs.style.color = bu ? '#00dca8' : '#f43f5e';
}

// ── Tabs ──────────────────────────────────────────────────────────────────────
function showTab(name) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + name).classList.add('active');
  event.target.classList.add('active');
  if (name === 'history') renderHistory();
  if (name === 'dashboard') fetchWallet();
}

// ── Calc Mode ─────────────────────────────────────────────────────────────────
function setMode(mode, btn) {
  calcMode = mode;
  document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  ['kapital','balance','manual'].forEach(m => {
    document.getElementById('mode-' + m).style.display = m === mode ? 'block' : 'none';
  });
  calcPct();
}

// ── Calculate % ───────────────────────────────────────────────────────────────
function calcPct() {
  const kap = parseFloat(document.getElementById('kapital').value) || 0;
  const aus = parseFloat(document.getElementById('ausschuettung').value) || 0;
  const prev = parseFloat(document.getElementById('prev-bal').value) || 0;
  const curr = parseFloat(document.getElementById('curr-bal').value) || 0;
  const man = parseFloat(document.getElementById('manual-pct').value) || 0;

  kapitalVal = kap;

  if (calcMode === 'kapital' && kap > 0 && aus > 0) {
    currentPct = (aus / kap) * 100;
    gainedAmount = aus;
    document.getElementById('calc-formula').textContent = fmt(aus) + ' ÷ ' + fmt(kap) + ' × 100';
  } else if (calcMode === 'balance' && prev > 0 && curr > 0) {
    currentPct = ((curr - prev) / prev) * 100;
    gainedAmount = curr - prev;
    document.getElementById('calc-formula').textContent = '(' + fmt(curr) + ' - ' + fmt(prev) + ') ÷ ' + fmt(prev) + ' × 100';
  } else if (calcMode === 'manual' && man !== 0) {
    currentPct = man;
    gainedAmount = 0;
    document.getElementById('calc-formula').textContent = 'Manuell eingegeben';
  } else {
    currentPct = 0;
    gainedAmount = 0;
    document.getElementById('calc-result').style.display = 'none';
    updateDisplays();
    return;
  }

  document.getElementById('calc-result').style.display = 'block';
  const sign = currentPct >= 0 ? '+' : '';
  document.getElementById('calc-display').textContent = sign + currentPct.toFixed(4) + '%';
  document.getElementById('calc-display').className = 'big-pct ' + (currentPct >= 0 ? 'pos' : 'neg');

  updateDisplays();
}

function fmt(n, d=2) { return Number(n).toLocaleString('de-DE', {minimumFractionDigits:d, maximumFractionDigits:d}); }

function updateDisplays() {
  const sign = currentPct >= 0 ? '+' : '';
  const pctEl = document.getElementById('pct-display');
  pctEl.textContent = sign + currentPct.toFixed(4) + '%';
  pctEl.className = 'big-pct ' + (currentPct >= 0 ? 'pos' : 'neg');
  document.getElementById('gained-display').textContent = gainedAmount > 0 ? '+' + fmt(gainedAmount) + ' USDT ausgeschüttet' : '';
  updateCaption();
}

// ── Caption ───────────────────────────────────────────────────────────────────
function updateCaption() {
  const sign = currentPct >= 0 ? '+' : '';
  const emoji = currentPct >= 0 ? '📈' : '📉';
  const note = document.getElementById('note').value;
  const kap = kapitalVal;
  let text = emoji + ' *OneTrade – Tägliche Ausschüttung*\\n\\n';
  text += '📅 *Datum:* ' + todayDE() + ' | ' + timeNow() + ' Uhr\\n';
  text += '━━━━━━━━━━━━━━━━━\\n';
  text += '💰 *Tagesgewinn:* `' + sign + currentPct.toFixed(4) + '%`\\n';
  if (gainedAmount > 0) text += '💵 *Ausgeschüttet:* `' + fmt(gainedAmount) + ' USDT`\\n';
  if (kap > 0) text += '🏦 *Eingesetztes Kapital:* `' + fmt(kap) + ' USDT`\\n';
  text += '━━━━━━━━━━━━━━━━━\\n';
  if (note) text += '📝 ' + note + '\\n━━━━━━━━━━━━━━━━━\\n';
  text += '🤖 _Powered by OneTrade AI System_\\n';
  text += '⚠️ _Vergangene Ergebnisse sind keine Garantie für die Zukunft._';
  document.getElementById('caption-preview').value = text;
}

function todayDE() { return new Date().toLocaleDateString('de-DE', {day:'2-digit',month:'2-digit',year:'numeric'}); }
function todayEN() { return new Date().toLocaleDateString('en-GB', {day:'2-digit',month:'long',year:'numeric'}).toUpperCase(); }
function timeNow() { return new Date().toLocaleTimeString('de-DE', {hour:'2-digit',minute:'2-digit'}); }

// ── Poster ────────────────────────────────────────────────────────────────────
function generatePoster() {
  if (currentPct === 0) { alert('Bitte erst Werte eingeben!'); return; }
  const sign = currentPct >= 0 ? '+' : '';
  const pctStr = sign + currentPct.toFixed(2) + '%';
  const dateStr = todayEN();
  const gainedStr = gainedAmount > 0 ? '+' + fmt(gainedAmount) + ' USDT' : '';
  const kapStr = kapitalVal > 0 ? fmt(kapitalVal) + ' USDT' : '';
  const bars = [18,22,20,28,30,40,52,68,80,95];

  // Canvas 600x600
  const canvas = document.getElementById('poster-canvas');
  canvas.width = 600;
  canvas.height = 600;
  const ctx = canvas.getContext('2d');

  // Hintergrund
  ctx.fillStyle = '#050d1a';
  ctx.fillRect(0, 0, 600, 600);

  // Dot grid
  ctx.fillStyle = 'rgba(0,220,168,0.07)';
  for(let x=14; x<600; x+=28) for(let y=14; y<600; y+=28) { ctx.beginPath(); ctx.arc(x,y,1.5,0,Math.PI*2); ctx.fill(); }

  // Logo T
  const grad1 = ctx.createLinearGradient(282,30,318,30);
  grad1.addColorStop(0,'#00dca8'); grad1.addColorStop(1,'#60efff');
  ctx.fillStyle = grad1;
  ctx.beginPath(); ctx.roundRect(282,30,36,6,3); ctx.fill();
  const grad2 = ctx.createLinearGradient(297,36,303,66);
  grad2.addColorStop(0,'#00dca8'); grad2.addColorStop(1,'#0ea5e9');
  ctx.fillStyle = grad2;
  ctx.beginPath(); ctx.roundRect(297,36,6,30,3); ctx.fill();

  // ONETRADE
  ctx.font = '900 13px Arial';
  ctx.textAlign = 'center';
  ctx.fillStyle = '#ffffff'; ctx.fillText('ONE', 279, 85);
  ctx.fillStyle = '#00dca8'; ctx.fillText('TRADE', 321, 85);

  // DAILY PERFORMANCE
  ctx.font = '900 20px Arial';
  ctx.letterSpacing = '5px';
  ctx.fillStyle = '#ffffff';
  ctx.fillText('DAILY PERFORMANCE', 300, 108);
  ctx.letterSpacing = '0px';

  // Datum
  ctx.font = '10px Arial';
  ctx.fillStyle = '#4a7090';
  ctx.fillText('📅 ' + dateStr, 300, 124);

  // Main Box
  const boxY = 132, boxH = 148;
  ctx.fillStyle = '#0a1a2e';
  ctx.strokeStyle = '#00dca8';
  ctx.lineWidth = 1.5;
  ctx.beginPath(); ctx.roundRect(24, boxY, 552, boxH, 14); ctx.fill(); ctx.stroke();

  // Glow hinter %
  const glow = ctx.createRadialGradient(300, boxY+boxH/2, 10, 300, boxY+boxH/2, 120);
  glow.addColorStop(0,'rgba(0,220,168,0.15)'); glow.addColorStop(1,'transparent');
  ctx.fillStyle = glow; ctx.fillRect(24, boxY, 552, boxH);

  // TODAY'S RESULT
  ctx.font = '9px Arial';
  ctx.fillStyle = '#00dca8';
  ctx.letterSpacing = '3px';
  ctx.fillText("TODAY'S RESULT", 300, boxY+22);
  ctx.letterSpacing = '0px';

  // % Zahl mit Glow
  ctx.font = '900 72px Arial';
  ctx.shadowColor = '#00dca8'; ctx.shadowBlur = 30;
  ctx.fillStyle = '#00dca8';
  ctx.fillText(pctStr, 300, boxY+90);
  ctx.shadowBlur = 0;

  // DAILY PROFIT
  ctx.font = '9px Arial';
  ctx.fillStyle = 'rgba(255,255,255,0.5)';
  ctx.letterSpacing = '3px';
  ctx.fillText('· DAILY PROFIT ·', 300, boxY+112);
  ctx.letterSpacing = '0px';

  // CONSISTENCY...
  ctx.font = '10px Arial';
  ctx.fillStyle = 'rgba(255,255,255,0.4)';
  ctx.fillText('CONSISTENCY. STRATEGY. ', 240, boxY+132);
  ctx.fillStyle = '#00dca8';
  ctx.fillText('SUCCESS.', 370, boxY+132);

  // Extra info
  let nextY = boxY + boxH + 14;
  if (gainedStr) {
    ctx.font = '11px Arial';
    ctx.fillStyle = 'rgba(0,220,168,0.6)';
    let extra = '💵 ' + gainedStr;
    if (kapStr) extra += '  |  🏦 ' + kapStr;
    ctx.fillText(extra, 300, nextY);
    nextY += 18;
  }

  // Stats
  const stats = [['🎯','FOCUS','ON YOUR GOALS'],['📊','SYSTEM','DRIVEN'],['🛡️','RISK','MANAGED'],['👥','TEAM','STRONG']];
  const statW = 552/4, statX0 = 24;
  nextY += 4;
  stats.forEach((s,i) => {
    const cx = statX0 + i*statW + statW/2;
    if(i>0) { ctx.strokeStyle='#1a2d4a'; ctx.lineWidth=1; ctx.beginPath(); ctx.moveTo(statX0+i*statW,nextY-4); ctx.lineTo(statX0+i*statW,nextY+52); ctx.stroke(); }
    ctx.font = '18px Arial'; ctx.fillStyle='#ffffff'; ctx.fillText(s[0], cx, nextY+18);
    ctx.font = '900 13px Arial'; ctx.fillStyle='#ffffff'; ctx.fillText('100%', cx, nextY+34);
    ctx.font = '700 8px Arial'; ctx.fillStyle='#00dca8'; ctx.fillText(s[1], cx, nextY+46);
    ctx.font = '8px Arial'; ctx.fillStyle='#4a7090'; ctx.fillText(s[2], cx, nextY+56);
  });
  nextY += 66;

  // Bars
  const barW = 44, barGap = 5, barX0 = 36, barMaxH = 70;
  bars.forEach((h,i) => {
    const bh = barMaxH * h/100;
    const alpha = 0.3 + i/bars.length*0.7;
    const bg = ctx.createLinearGradient(0,0,0,bh);
    bg.addColorStop(0,`rgba(0,220,168,${alpha})`);
    bg.addColorStop(1,`rgba(14,165,233,${alpha})`);
    ctx.fillStyle = bg;
    ctx.beginPath(); ctx.roundRect(barX0+i*(barW+barGap), nextY+barMaxH-bh, barW, bh, [3,3,0,0]); ctx.fill();
  });
  nextY += barMaxH + 10;

  // Quote box
  ctx.fillStyle = '#0a1525';
  ctx.strokeStyle = '#1a2d4a'; ctx.lineWidth=1;
  ctx.beginPath(); ctx.roundRect(24, nextY, 552, 46, 10); ctx.fill(); ctx.stroke();
  ctx.font = '900 26px Georgia'; ctx.fillStyle='#00dca8'; ctx.textAlign='left';
  ctx.fillText('"', 38, nextY+32);
  ctx.font = '9px Arial'; ctx.fillStyle='#ffffff';
  ctx.fillText("WE DON'T CHASE THE MARKET.", 62, nextY+18);
  ctx.font = '900 9px Arial'; ctx.fillStyle='#00dca8';
  ctx.fillText('WE FOLLOW THE PLAN.', 62, nextY+32);
  ctx.font = '900 8px Arial'; ctx.fillStyle='#00dca8'; ctx.textAlign='right';
  ctx.fillText('ONE', 568, nextY+18);
  ctx.fillText('TRADE', 568, nextY+30);
  nextY += 56;

  // Disclaimer
  ctx.font = '7px Arial'; ctx.fillStyle='#1a3050'; ctx.textAlign='center';
  ctx.fillText('PAST PERFORMANCE IS NOT INDICATIVE OF FUTURE RESULTS.', 300, nextY+10);

  // Anzeigen
  const img = document.getElementById('poster-img');
  img.src = canvas.toDataURL('image/png');
  img.style.display = 'block';
  document.getElementById('poster-container').style.display = 'block';
}


// ── Send Post ─────────────────────────────────────────────────────────────────
async function sendPost() {
  if (currentPct === 0) { showLog('send-log', '❌ Bitte erst Werte eingeben!', 'err'); return; }
  const backendUrl = document.getElementById('backend-url').value.trim().replace(/\\/$/, '');
  if (!backendUrl) { showLog('send-log', '❌ Backend URL fehlt! Bitte in Einstellungen eintragen.', 'err'); return; }

  const btn = document.getElementById('send-btn');
  btn.disabled = true;
  btn.textContent = '⏳ Sende...';
  showLog('send-log', '📤 Sende mit Bild via Backend...', 'info');

  try {
    // Poster immer frisch rendern vor dem Senden
  generatePoster();
  await new Promise(r => setTimeout(r, 100)); // kurz warten bis Canvas gerendert

  const canvas = document.getElementById('poster-canvas');
  const image_b64 = (canvas && canvas.width > 0) ? canvas.toDataURL('image/png').split(',')[1] : '';

  showLog('send-log', '📤 Sende' + (image_b64 ? ' mit Bild' : ' (kein Bild)') + '...', 'info');

  const res = await fetch(backendUrl + '/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        pct: currentPct,
        gained: gainedAmount,
        kapital: kapitalVal,
        balance: 0,
        note: document.getElementById('note').value,
        date: todayDE(),
        time: timeNow(),
        date_en: todayEN(),
        image_b64: image_b64,
      }),
    });
    const data = await res.json();
    if (data.ok) {
      showLog('send-log', '✅ Gesendet! ' + (data.with_image ? '📸 Mit Bild!' : '📝 Nur Text'), 'ok');
      btn.textContent = '✅ Gesendet!';
      addHistory({ date: todayDE(), time: timeNow(), pct: currentPct, gained: gainedAmount, kapital: kapitalVal });
      setTimeout(() => { btn.textContent = '📤 Jetzt an Telegram senden'; btn.disabled = false; }, 3000);
    } else {
      showLog('send-log', '❌ ' + (data.error || 'Fehler'), 'err');
      btn.textContent = '📤 Jetzt an Telegram senden';
      btn.disabled = false;
    }
  } catch(e) {
    showLog('send-log', '❌ Fetch Fehler: ' + e.message, 'err');
    btn.textContent = '📤 Jetzt an Telegram senden';
    btn.disabled = false;
  }
}

// ── Test Backend ───────────────────────────────────────────────────────────────
async function testBackend() {
  const backendUrl = document.getElementById('backend-url').value.trim().replace(/\\/$/, '');
  if (!backendUrl) { alert('Bitte Backend URL eintragen!'); return; }
  showLog('send-log', '🔧 Teste Backend...', 'info');
  showLog('settings-log', '🔧 Teste Backend...', 'info');
  try {
    const res = await fetch(backendUrl + '/test', { method: 'POST' });
    const data = await res.json();
    if (data.ok) {
      showLog('send-log', '✅ Backend & Bot funktionieren!', 'ok');
      showLog('settings-log', '✅ Backend & Bot funktionieren!', 'ok');
    } else {
      showLog('send-log', '❌ ' + (data.error || 'Fehler'), 'err');
      showLog('settings-log', '❌ ' + (data.error || 'Fehler'), 'err');
    }
  } catch(e) {
    showLog('send-log', '❌ ' + e.message, 'err');
    showLog('settings-log', '❌ ' + e.message, 'err');
  }
}

// ── Wallet ─────────────────────────────────────────────────────────────────────
async function fetchWallet() {
  const backendUrl = (document.getElementById('backend-url').value || 'https://onetrade-bot.onrender.com').trim().replace(/\\/$/, '');
  document.getElementById('wallet-balance').textContent = 'Lade...';
  try {
    const res = await fetch(backendUrl + '/wallet');
    const data = await res.json();
    if (data.ok) {
      document.getElementById('wallet-balance').textContent = Number(data.balance).toLocaleString('de-DE', {minimumFractionDigits:2, maximumFractionDigits:2}) + ' USDT';
    } else {
      document.getElementById('wallet-balance').textContent = 'API-Key fehlt';
    }
  } catch(e) {
    document.getElementById('wallet-balance').textContent = 'Nicht erreichbar';
  }
}

// ── History ────────────────────────────────────────────────────────────────────
function addHistory(entry) {
  history.unshift(entry);
  if (history.length > 30) history = history.slice(0, 30);
  localStorage.setItem('ot_history', JSON.stringify(history));
  const last = history[0];
  const sign = last.pct >= 0 ? '+' : '';
  document.getElementById('last-pct').textContent = sign + last.pct.toFixed(4) + '%';
  document.getElementById('last-pct').className = 'big-pct ' + (last.pct >= 0 ? 'pos' : 'neg');
  document.getElementById('last-info').textContent = last.date + ' · ' + last.time + ' Uhr · +' + fmt(last.gained) + ' USDT';
}

function renderHistory() {
  const el = document.getElementById('history-list');
  if (history.length === 0) { el.innerHTML = '<div style="color:#4a6080;font-size:13px;">Noch keine Posts gesendet.</div>'; return; }
  el.innerHTML = history.map(h => {
    const sign = h.pct >= 0 ? '+' : '';
    return `<div class="history-row">
      <div>
        <div style="font-weight:600;">${h.date} · ${h.time} Uhr</div>
        <div style="font-size:12px;color:#4a6080;">+${fmt(h.gained)} USDT${h.kapital > 0 ? ' · Kapital: ' + fmt(h.kapital) + ' USDT' : ''}</div>
      </div>
      <div class="big-pct ${h.pct >= 0 ? 'pos' : 'neg'}" style="font-size:20px;">${sign}${h.pct.toFixed(4)}%</div>
    </div>`;
  }).join('');
}

// ── Log helper ─────────────────────────────────────────────────────────────────
function showLog(id, msg, type) {
  const el = document.getElementById(id);
  el.style.display = 'block';
  el.textContent = msg;
  el.className = 'log-box log-' + type;
}

// ── Init ───────────────────────────────────────────────────────────────────────
loadSettings();
updateCaption();
document.getElementById('note').addEventListener('input', updateCaption);

if (history.length > 0) {
  const last = history[0];
  const sign = last.pct >= 0 ? '+' : '';
  document.getElementById('last-pct').textContent = sign + last.pct.toFixed(4) + '%';
  document.getElementById('last-pct').className = 'big-pct ' + (last.pct >= 0 ? 'pos' : 'neg');
  document.getElementById('last-info').textContent = last.date + ' · ' + last.time + ' Uhr';
}
</script>
</body>
</html>
"""

app = Flask(__name__)
CORS(app)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "8601946674:AAGpvttyRBy7B81uU_frX8BQWk-N68lFTtQ")
GROUP_ID  = os.environ.get("TG_GROUP_ID",  "-1003900515439")

def send_tg_text(text):
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": GROUP_ID, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": True},
            timeout=15
        )
        return r.json()
    except Exception as e:
        return {"ok": False, "description": str(e)}

def send_tg_photo_b64(png_b64, caption):
    try:
        png_bytes = base64.b64decode(png_b64)
        r = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
            files={"photo": ("poster.png", png_bytes, "image/png")},
            data={"chat_id": GROUP_ID, "caption": caption, "parse_mode": "Markdown"},
            timeout=30
        )
        return r.json()
    except Exception as e:
        return {"ok": False, "description": str(e)}

@app.route("/", methods=["GET"])
def index():
    return Response(HTML_PAGE, mimetype="text/html")

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/test", methods=["GET", "POST", "OPTIONS"])
def test():
    if request.method == "OPTIONS":
        return jsonify({}), 200
    result = send_tg_text("🤖 *OneTrade Bot* – Verbindung erfolgreich! ✅")
    if result.get("ok"):
        return jsonify({"ok": True, "message": "Test-Nachricht gesendet!"})
    return jsonify({"ok": False, "error": result.get("description", "Fehler")}), 400

@app.route("/send", methods=["POST", "OPTIONS"])
def send():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"ok": False, "error": "Kein JSON Body"}), 400

        pct      = float(data.get("pct", 0))
        gained   = float(data.get("gained", 0))
        kapital  = float(data.get("kapital", 0))
        note     = str(data.get("note", ""))
        date_str = str(data.get("date", ""))
        time_str = str(data.get("time", ""))
        png_b64  = str(data.get("image_b64", ""))

        sign  = "+" if pct >= 0 else ""
        emoji = "📈" if pct >= 0 else "📉"

        caption  = f"{emoji} *OneTrade – Tägliche Ausschüttung*\n\n"
        caption += f"📅 *Datum:* {date_str} | {time_str} Uhr\n"
        caption += "━━━━━━━━━━━━━━━━━\n"
        caption += f"💰 *Tagesgewinn:* `{sign}{pct:.4f}%`\n"
        if gained > 0: caption += f"💵 *Ausgeschüttet:* `{gained:,.2f} USDT`\n"
        if kapital > 0: caption += f"🏦 *Eingesetztes Kapital:* `{kapital:,.2f} USDT`\n"
        caption += "━━━━━━━━━━━━━━━━━\n"
        if note: caption += f"📝 {note}\n━━━━━━━━━━━━━━━━━\n"
        caption += "🤖 _Powered by OneTrade AI System_\n"
        caption += "⚠️ _Vergangene Ergebnisse sind keine Garantie für die Zukunft._"

        if png_b64 and len(png_b64) > 100:
            result = send_tg_photo_b64(png_b64, caption)
        else:
            result = send_tg_text(caption)

        if result.get("ok"):
            return jsonify({"ok": True, "with_image": bool(png_b64 and len(png_b64) > 100)})
        return jsonify({"ok": False, "error": result.get("description", "Telegram Fehler")}), 400

    except Exception as e:
        return jsonify({"ok": False, "error": f"Server Fehler: {str(e)}"}), 500

@app.route("/wallet", methods=["GET"])
def wallet():
    address  = request.args.get("address", "0x17E384Fc02A4800e1cb8644CAB9daAeA9a2861A1")
    api_key  = os.environ.get("BSCSCAN_API_KEY", "YourApiKeyToken")
    contract = "0x55d398326f99059fF775485246999027B3197955"
    try:
        r = requests.get(
            f"https://api.bscscan.com/api?module=account&action=tokenbalance"
            f"&contractaddress={contract}&address={address}&tag=latest&apikey={api_key}",
            timeout=10
        )
        d = r.json()
        if d.get("status") == "1":
            return jsonify({"ok": True, "balance": int(d["result"]) / 1e18})
        return jsonify({"ok": False, "error": d.get("message")}), 400
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
