from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CashEmpireBot — Empire Tycoon</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:system-ui,-apple-system,sans-serif;background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);color:#fff;min-height:100vh}
nav{display:flex;align-items:center;justify-content:space-between;padding:16px 40px;background:rgba(255,255,255,.03);border-bottom:1px solid rgba(255,255,255,.06)}
.nav-logo{display:flex;align-items:center;gap:10px;font-weight:700;font-size:16px}
.nav-logo img{width:32px;height:32px;border-radius:8px}
.nav-links{display:flex;gap:20px;align-items:center}
.nav-links a{color:rgba(255,255,255,.6);text-decoration:none;font-size:13px;transition:color .2s}
.nav-links a:hover{color:#fff}
.btn{background:linear-gradient(90deg,#f7971e,#ffd200);color:#0f0c29!important;padding:8px 20px;border-radius:20px;font-weight:600;font-size:13px}
.hero{display:flex;align-items:center;justify-content:center;gap:60px;padding:60px 40px;max-width:1000px;margin:0 auto;min-height:70vh}
.hero-left{flex:1}
.hero-left h1{font-size:42px;font-weight:800;line-height:1.2;background:linear-gradient(90deg,#f7971e,#ffd200);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.hero-left p{color:rgba(255,255,255,.5);font-size:15px;margin:16px 0 24px;line-height:1.6}
.hero-right{flex:1;text-align:center}
.hero-right img{width:180px;height:180px;border-radius:50%;border:4px solid rgba(255,215,0,.2);box-shadow:0 20px 60px rgba(0,0,0,.4)}
.btns{display:flex;gap:12px;flex-wrap:wrap}
.btns .btn{font-size:14px;padding:10px 24px}
.btn-outline{background:transparent!important;border:1px solid rgba(255,255,255,.2);color:#fff!important;padding:10px 24px;border-radius:20px;font-size:14px;font-weight:600;text-decoration:none}
.badge-row{display:flex;gap:12px;margin-bottom:16px}
.badge{display:inline-flex;align-items:center;gap:6px;background:rgba(46,204,113,.12);border:1px solid rgba(46,204,113,.25);color:#2ecc71;padding:6px 14px;border-radius:20px;font-size:12px;font-weight:600}
.dot{width:8px;height:8px;border-radius:50%;background:#2ecc71;animation:pulse 1.5s infinite;display:inline-block}
@keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(46,204,113,.6)}50%{box-shadow:0 0 0 6px rgba(46,204,113,0)}}
.stats-section{background:rgba(255,255,255,.03);border-top:1px solid rgba(255,255,255,.06);border-bottom:1px solid rgba(255,255,255,.06);padding:40px}
.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:24px;max-width:800px;margin:0 auto;text-align:center}
.stat-box{padding:16px;background:rgba(255,255,255,.04);border-radius:16px;border:1px solid rgba(255,255,255,.06)}
.stat-box .num{font-size:28px;font-weight:800;color:#ffd200}
.stat-box .lbl{font-size:12px;color:rgba(255,255,255,.4);margin-top:4px}
.features{max-width:900px;margin:0 auto;padding:50px 40px}
.features h2{text-align:center;font-size:28px;font-weight:700;margin-bottom:32px;background:linear-gradient(90deg,#f7971e,#ffd200);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.feature-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px}
.feat{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.06);border-radius:16px;padding:20px;text-align:center}
.feat emoji{font-size:32px;display:block;margin-bottom:8px}
.feat h3{font-size:15px;font-weight:600;margin-bottom:4px}
.feat p{font-size:12px;color:rgba(255,255,255,.4)}
footer{text-align:center;padding:24px;color:rgba(255,255,255,.15);font-size:12px}
</style>
</head>
<body>
<nav>
<div class="nav-logo"><img src="/logo.png" alt="">CashEmpireBot</div>
<div class="nav-links">
<a href="#features">Features</a>
<a href="#stats">Stats</a>
<a class="btn" href="https://discord.gg/XAhXeJqAdw" target="_blank">Join Server</a>
</div>
</nav>

<div class="hero">
<div class="hero-left">
<div class="badge-row">
<div class="badge"><span class="dot"></span> Online</div>
<div class="badge">32 Commands</div>
</div>
<h1>Build Your Empire</h1>
<p>CashEmpireBot is a powerful Discord economy bot with pets, crates, leaderboards, voice farming, trading and more. Grow your wealth, collect rare pets, and dominate the leaderboard.</p>
<div class="btns">
<a class="btn" href="https://discord.gg/XAhXeJqAdw" target="_blank">Join the Server</a>
<a class="btn-outline" href="#features">Explore Features</a>
</div>
</div>
<div class="hero-right"><img src="/logo.png" alt="CashEmpireBot"></div>
</div>

<div class="stats-section" id="stats">
<div class="stats-grid">
<div class="stat-box"><div class="num">32</div><div class="lbl">Slash Commands</div></div>
<div class="stat-box"><div class="num">24/7</div><div class="lbl">Uptime</div></div>
<div class="stat-box"><div class="num">6+</div><div class="lbl">Pet Rarities</div></div>
<div class="stat-box"><div class="num">3</div><div class="lbl">Crate Types</div></div>
</div>
</div>

<div class="features" id="features">
<h2>Game Features</h2>
<div class="feature-grid">
<div class="feat"><div class="emoji">💰</div><h3>Economy</h3><p>Work, daily, gamble and earn coins to build your fortune</p></div>
<div class="feat"><div class="emoji">🐾</div><h3>Pet System</h3><p>Open crates, collect pets with multipliers, equip the best ones</p></div>
<div class="feat"><div class="emoji">🎮</div><h3>Voice Farm</h3><p>Earn coins passively while in voice channels</p></div>
<div class="feat"><div class="emoji">🏆</div><h3>Leaderboards</h3><p>Compete for top spots and earn daily rewards</p></div>
<div class="feat"><div class="emoji">🔄</div><h3>Trading</h3><p>Trade pets and items with other players</p></div>
<div class="feat"><div class="emoji">⚡</div><h3>Boosters</h3><p>Use multipliers to boost your earnings</p></div>
</div>
</div>

<footer>CashEmpireBot &copy; 2026 &bull; Powered by Replit</footer>
</body></html>"""


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
        self.wfile.write(HTML.encode())
    def log_message(self, *a): pass

def run():
    try:
        HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
    except OSError:
        pass
Thread(target=run, daemon=True).start()
