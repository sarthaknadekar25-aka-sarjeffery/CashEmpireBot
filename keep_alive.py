from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
import os

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
        self.wfile.write(b"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CashEmpireBot</title><style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:system-ui,sans-serif;background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);min-height:100vh;display:flex;align-items:center;justify-content:center;color:#fff;overflow:hidden}
.particles{position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:0}
.p{position:absolute;width:6px;height:6px;background:rgba(255,215,0,.3);border-radius:50%;animation:float linear infinite}
@keyframes float{0%{transform:translateY(100vh) rotate(0deg);opacity:0}10%{opacity:1}90%{opacity:1}100%{transform:translateY(-10vh) rotate(720deg);opacity:0}}
.card{position:relative;z-index:1;background:rgba(255,255,255,.06);backdrop-filter:blur(16px);border:1px solid rgba(255,255,255,.1);border-radius:28px;padding:40px 48px;text-align:center;max-width:440px;width:90%;box-shadow:0 30px 60px rgba(0,0,0,.5)}
.avatar{width:100px;height:100px;border-radius:50%;border:3px solid rgba(255,215,0,.3);margin-bottom:12px;object-fit:cover}
h1{font-size:26px;font-weight:800;margin-bottom:2px;background:linear-gradient(90deg,#f7971e,#ffd200);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.sub{color:rgba(255,255,255,.4);font-size:12px;margin-bottom:20px;letter-spacing:.5px}
.badge{display:inline-flex;align-items:center;gap:8px;background:rgba(46,204,113,.12);border:1px solid rgba(46,204,113,.25);color:#2ecc71;padding:8px 20px;border-radius:40px;font-size:13px;font-weight:700;margin-bottom:20px}
.dot{width:10px;height:10px;border-radius:50%;background:#2ecc71;animation:pulse 1.5s infinite}
@keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(46,204,113,.6)}50%{box-shadow:0 0 0 8px rgba(46,204,113,0)}}
.stats{display:flex;gap:32px;justify-content:center;margin:16px 0 20px}
.stat{text-align:center}
.num{font-size:22px;font-weight:800;color:#ffd200}
.lbl{font-size:10px;color:rgba(255,255,255,.35);text-transform:uppercase;letter-spacing:1.5px;margin-top:2px}
.tags{display:flex;gap:6px;flex-wrap:wrap;justify-content:center;margin:8px 0}
.tag{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.08);padding:4px 12px;border-radius:14px;font-size:11px;color:rgba(255,255,255,.45)}
.footer{font-size:11px;color:rgba(255,255,255,.15);margin-top:20px}
</style></head><body>
<div class="particles" id="p"></div>
<div class="card">
<img class="avatar" src="/logo.png" alt="CashEmpireBot">
<h1>CashEmpireBot</h1>
<p class="sub">Empire Tycoon Discord Bot</p>
<div class="badge"><span class="dot"></span> ONLINE</div>
<div class="stats">
<div class="stat"><div class="num">32</div><div class="lbl">Commands</div></div>
<div class="stat"><div class="num">24/7</div><div class="lbl">Uptime</div></div>
<div class="stat"><div class="num">0</div><div class="lbl">Latency</div></div>
</div>
<div class="tags">
<span class="tag">/work</span><span class="tag">/daily</span><span class="tag">/balance</span>
<span class="tag">/petshop</span><span class="tag">/mypets</span><span class="tag">/lb</span>
<span class="tag">/boost</span><span class="tag">/shop</span><span class="tag">/gamble</span>
</div>
<div class="footer">Running on Replit</div>
</div>
<script>
for(let i=0;i<35;i++){let e=document.createElement('div');e.className='p';e.style.left=Math.random()*100+'%';e.style.animationDuration=(5+Math.random()*10)+'s';e.style.animationDelay=Math.random()*8+'s';e.style.width=e.style.height=(3+Math.random()*5)+'px';document.getElementById('p').appendChild(e)}
</script>
</body></html>""")
    def log_message(self, *a): pass

try:
    server = HTTPServer(("0.0.0.0", 8080), Handler)
    print("[Web] Preview server on port 8080", flush=True)
    Thread(target=server.serve_forever, daemon=True).start()
except OSError:
    print("[Web] Port 8080 busy", flush=True)
