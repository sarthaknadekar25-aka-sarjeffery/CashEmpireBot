from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
import os, sys

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(b"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CashEmpireBot</title><style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:system-ui,sans-serif;background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);min-height:100vh;display:flex;align-items:center;justify-content:center;color:#fff}
.card{background:rgba(255,255,255,.06);backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,.1);border-radius:24px;padding:40px;text-align:center;max-width:400px;width:90%}
.coin{font-size:60px;margin-bottom:8px;animation:bounce 2s infinite}
@keyframes bounce{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}
h1{font-size:26px;font-weight:700;background:linear-gradient(90deg,#f7971e,#ffd200);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:4px}
.sub{color:rgba(255,255,255,.4);font-size:13px;margin-bottom:16px}
.status{display:inline-flex;align-items:center;gap:6px;background:rgba(46,204,113,.15);color:#2ecc71;padding:8px 18px;border-radius:40px;font-size:13px;font-weight:600;margin-bottom:16px}
.dot{width:8px;height:8px;border-radius:50%;background:#2ecc71;animation:pulse 1.5s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
.cmds{display:flex;gap:8px;flex-wrap:wrap;justify-content:center;margin:12px 0}
.tag{background:rgba(255,255,255,.06);padding:4px 12px;border-radius:12px;font-size:11px;color:rgba(255,255,255,.4)}
.footer{font-size:11px;color:rgba(255,255,255,.18);margin-top:20px}
</style></head><body><div class="card"><div class="coin">🪙</div><h1>CashEmpireBot</h1><p class="sub">Empire Tycoon Discord Bot</p><div class="status"><span class="dot"></span> ONLINE</div><div class="cmds"><span class="tag">/work</span><span class="tag">/daily</span><span class="tag">/petshop</span><span class="tag">/mypets</span><span class="tag">/balance</span><span class="tag">/lb</span></div><div class="footer">Replit &bull; 2026</div></div></body></html>""")
    def log_message(self, *a): pass

try:
    server = HTTPServer(("0.0.0.0", 8080), Handler)
    print("[Web] Preview server running on port 8080", flush=True)
    Thread(target=server.serve_forever, daemon=True).start()
except OSError as e:
    print(f"[Web] Port 8080 busy - preview unavailable", flush=True)
