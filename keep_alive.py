from flask import Flask
from threading import Thread
import os

app = Flask(__name__)

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CashEmpireBot</title>
<style>
  *{margin:0;padding:0;box-sizing:border-box}
  body{font-family:system-ui,-apple-system,sans-serif;background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);min-height:100vh;display:flex;align-items:center;justify-content:center;color:#fff}
  .card{background:rgba(255,255,255,.06);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,.1);border-radius:24px;padding:48px 56px;text-align:center;max-width:480px;box-shadow:0 25px 50px rgba(0,0,0,.4)}
  .coin{font-size:64px;margin-bottom:12px}
  h1{font-size:28px;font-weight:700;margin-bottom:4px;background:linear-gradient(90deg,#f7971e,#ffd200);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
  .sub{color:rgba(255,255,255,.5);font-size:14px;margin-bottom:28px}
  .status{display:inline-flex;align-items:center;gap:8px;background:rgba(46,204,113,.15);color:#2ecc71;padding:10px 20px;border-radius:40px;font-size:14px;font-weight:600;margin-bottom:20px}
  .dot{width:10px;height:10px;border-radius:50%;background:#2ecc71;animation:pulse 1.5s infinite}
  @keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
  .stats{display:flex;gap:32px;justify-content:center;margin:24px 0 8px}
  .stat{text-align:center}
  .num{font-size:22px;font-weight:700;color:#ffd200}
  .lbl{font-size:11px;color:rgba(255,255,255,.4);text-transform:uppercase;letter-spacing:1px}
  .footer{font-size:12px;color:rgba(255,255,255,.25);margin-top:20px}
</style>
</head>
<body>
<div class="card">
  <div class="coin">🪙</div>
  <h1>CashEmpireBot</h1>
  <p class="sub">Empire Tycoon Discord Bot</p>
  <div class="status"><span class="dot"></span> Online</div>
  <div class="stats">
    <div class="stat"><div class="num">24/7</div><div class="lbl">Uptime</div></div>
    <div class="stat"><div class="num">0</div><div class="lbl">Ping</div></div>
  </div>
  <p style="font-size:13px;color:rgba(255,255,255,.35);margin-top:12px">Add me to your server and start earning!</p>
  <div class="footer">Powered by Replit &copy; 2026</div>
</div>
</body>
</html>"""

@app.route("/")
def home():
    return HTML

def run():
    port = int(os.getenv("PORT", 8080))
    try:
        app.run(host="0.0.0.0", port=port)
    except OSError:
        pass

def keep_alive():
    t = Thread(target=run, daemon=True)
    t.start()
