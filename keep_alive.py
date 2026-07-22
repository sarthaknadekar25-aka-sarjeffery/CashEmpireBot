from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
import os

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(b"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CashEmpireBot</title><style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:system-ui,sans-serif;background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);min-height:100vh;display:flex;align-items:center;justify-content:center;color:#fff}
.card{background:rgba(255,255,255,.06);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,.1);border-radius:24px;padding:40px;text-align:center;max-width:400px}
.coin{font-size:60px;margin-bottom:8px;animation:bounce 2s infinite}
@keyframes bounce{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}
h1{font-size:26px;font-weight:700;background:linear-gradient(90deg,#f7971e,#ffd200);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.status{display:inline-flex;align-items:center;gap:6px;background:rgba(46,204,113,.15);color:#2ecc71;padding:8px 18px;border-radius:40px;font-size:13px;font-weight:600;margin:16px 0}
.dot{width:8px;height:8px;border-radius:50%;background:#2ecc71;animation:pulse 1.5s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
.footer{font-size:11px;color:rgba(255,255,255,.2);margin-top:20px}
</style></head><body><div class="card"><div class="coin">🪙</div><h1>CashEmpireBot</h1><div class="status"><span class="dot"></span> ONLINE</div><p style="font-size:13px;color:rgba(255,255,255,.35)">Empire Tycoon Discord Bot</p><div class="footer">Always running</div></div></body></html>""")
    def log_message(self, *a): pass

def run():
    try:
        HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
    except: pass

Thread(target=run, daemon=True).start()
