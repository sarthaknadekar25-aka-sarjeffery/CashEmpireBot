from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

PAGE = '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>CashEmpireBot</title><style>body{margin:0;background:#0a0a12;color:#fff;font-family:system-ui;display:flex;align-items:center;justify-content:center;min-height:100vh}.c{text-align:center;padding:40px}img{width:120px;height:120px;border-radius:50%;border:3px solid rgba(247,151,30,.2);margin-bottom:16px}h1{font-size:32px;background:linear-gradient(90deg,#f7971e,#ffd200);-webkit-background-clip:text;-webkit-text-fill-color:transparent}.g{color:#2ecc71;font-weight:600;display:flex;align-items:center;gap:6px;justify-content:center;margin:12px 0}.d{width:8px;height:8px;border-radius:50%;background:#2ecc71;animation:p 1.5s infinite;display:inline-block}@keyframes p{0%,100%{opacity:1}50%{opacity:.3}}a{display:inline-block;margin-top:16px;padding:10px 24px;background:linear-gradient(90deg,#f7971e,#ffd200);color:#0a0a12;border-radius:100px;text-decoration:none;font-weight:700;font-size:14px}.s{color:rgba(255,255,255,.25);font-size:13px;margin-top:20px}</style></head><body><div class="c"><img src="/logo.png" alt=""><h1>CashEmpireBot</h1><div class="g"><span class="d"></span> ONLINE</div><p style="color:rgba(255,255,255,.4);margin:4px 0 8px">Empire Tycoon Discord Bot</p><a href="https://discord.gg/XAhXeJqAdw" target="_blank">Join Server</a><div class="s">Replit &bull; 2026</div></div></body></html>'

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/logo.png":
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.end_headers()
            with open("logo.png", "rb") as f:
                self.wfile.write(f.read())
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(PAGE.encode())
    def log_message(self, *a): pass

def run():
    try:
        HTTPServer(("0.0.0.0", 5000), Handler).serve_forever()
    except: pass
Thread(target=run, daemon=True).start()
