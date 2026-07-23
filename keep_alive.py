from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

PAGE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>CashEmpireBot</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:system-ui,sans-serif;background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);min-height:100vh;display:flex;align-items:center;justify-content:center;color:#fff}
.card{background:rgba(255,255,255,.06);border-radius:24px;padding:40px;text-align:center;max-width:420px;width:90%;backdrop-filter:blur(12px);border:1px solid rgba(255,255,255,.08)}
.logo{width:100px;height:100px;border-radius:50%;border:3px solid rgba(255,215,0,.2);margin-bottom:14px}
h1{font-size:26px;background:linear-gradient(90deg,#f7971e,#ffd200);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:4px}
.sub{color:rgba(255,255,255,.4);font-size:13px;margin-bottom:18px}
.badge{display:inline-flex;align-items:center;gap:6px;background:rgba(46,204,113,.12);color:#2ecc71;padding:8px 18px;border-radius:40px;font-size:13px;font-weight:600;margin-bottom:18px}
.dot{width:8px;height:8px;border-radius:50%;background:#2ecc71;display:inline-block;animation:pulse 1.5s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
.stats{display:flex;gap:24px;justify-content:center;margin:16px 0}
.stat .n{font-size:22px;font-weight:700;color:#ffd200}
.stat .l{font-size:11px;color:rgba(255,255,255,.35);text-transform:uppercase;letter-spacing:1px;margin-top:2px}
.tags{display:flex;gap:6px;flex-wrap:wrap;justify-content:center;margin:16px 0 20px}
.tag{background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.08);padding:4px 12px;border-radius:14px;font-size:11px;color:rgba(255,255,255,.4)}
a{display:inline-block;padding:10px 24px;background:linear-gradient(90deg,#f7971e,#ffd200);color:#0a0a12;border-radius:100px;text-decoration:none;font-weight:700;font-size:14px}
.ft{color:rgba(255,255,255,.15);font-size:11px;margin-top:20px}
</style>
</head>
<body>
<div class="card">
<img class="logo" src="/logo.png" alt="logo">
<h1>CashEmpireBot</h1>
<p class="sub">Empire Tycoon Discord Bot</p>
<div class="badge"><span class="dot"></span> ONLINE</div>
<div class="stats">
<div class="stat"><div class="n">32</div><div class="l">Commands</div></div>
<div class="stat"><div class="n">24/7</div><div class="l">Uptime</div></div>
<div class="stat"><div class="n">6</div><div class="l">Rarities</div></div>
</div>
<div class="tags">
<span class="tag">/work</span><span class="tag">/daily</span><span class="tag">/balance</span>
<span class="tag">/petshop</span><span class="tag">/mypets</span><span class="tag">/lb</span>
</div>
<a href="https://discord.gg/XAhXeJqAdw" target="_blank">Join Server</a>
<div class="ft">Running on Replit</div>
</div>
</body>
</html>
"""

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/logo.png":
            try:
                with open("logo.png","rb") as f:
                    self.send_response(200)
                    self.send_header("Content-Type","image/png")
                    self.end_headers()
                    self.wfile.write(f.read())
            except: pass
            return
        self.send_response(200)
        self.send_header("Content-Type","text/html")
        self.end_headers()
        self.wfile.write(PAGE.encode())
    def log_message(self,*a): pass

def run():
    try: HTTPServer(("0.0.0.0",8080),H).serve_forever()
    except: pass
Thread(target=run,daemon=True).start()
