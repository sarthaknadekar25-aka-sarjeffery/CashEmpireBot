from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CashEmpireBot</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Inter',system-ui,sans-serif;background:#0a0a12;color:#fff;min-height:100vh;overflow-x:hidden}
canvas{position:fixed;top:0;left:0;width:100%;height:100%;z-index:0;pointer-events:none}
.content{position:relative;z-index:1}

nav{display:flex;align-items:center;justify-content:space-between;padding:18px 48px;background:rgba(255,255,255,.02);border-bottom:1px solid rgba(255,255,255,.04)}
.logo{display:flex;align-items:center;gap:12px;font-weight:700;font-size:18px;letter-spacing:-.3px}
.logo img{width:36px;height:36px;border-radius:10px}
.logo span{background:linear-gradient(90deg,#f7971e,#ffd200);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.nav-links{display:flex;gap:24px;align-items:center}
.nav-links a{color:rgba(255,255,255,.5);text-decoration:none;font-size:14px;font-weight:500;transition:color .2s}
.nav-links a:hover{color:#fff}
.btn-gold{background:linear-gradient(90deg,#f7971e,#ffd200);color:#0a0a12!important;padding:10px 24px;border-radius:100px;font-weight:700!important;font-size:13px!important;transition:transform .2s,box-shadow .2s}
.btn-gold:hover{transform:translateY(-1px);box-shadow:0 8px 24px rgba(247,151,30,.3)}

.hero{display:flex;align-items:center;justify-content:space-between;max-width:1100px;margin:0 auto;padding:80px 48px;gap:60px}
.hero-left{flex:1.2}
.badges{display:flex;gap:10px;margin-bottom:20px;flex-wrap:wrap}
.badge{display:flex;align-items:center;gap:6px;padding:6px 14px;border-radius:100px;font-size:12px;font-weight:600}
.badge-green{background:rgba(46,204,113,.1);border:1px solid rgba(46,204,113,.2);color:#2ecc71}
.badge-green .dot{width:8px;height:8px;border-radius:50%;background:#2ecc71;display:inline-block;animation:pulse 1.5s infinite}
@keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(46,204,113,.6)}50%{box-shadow:0 0 0 8px rgba(46,204,113,0)}}
.badge-gold{background:rgba(247,151,30,.1);border:1px solid rgba(247,151,30,.2);color:#f7971e}
.badge-purple{background:rgba(155,89,182,.1);border:1px solid rgba(155,89,182,.2);color:#9b59b6}
.hero-left h1{font-size:52px;font-weight:800;line-height:1.1;letter-spacing:-1px;margin-bottom:16px}
.hero-left h1 span{background:linear-gradient(90deg,#f7971e,#ffd200);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.hero-left p{color:rgba(255,255,255,.45);font-size:16px;line-height:1.7;margin-bottom:28px;max-width:500px}
.hero-btns{display:flex;gap:14px;flex-wrap:wrap}
.btn-ghost{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);color:#fff!important;padding:12px 28px;border-radius:100px;font-weight:600;font-size:14px;text-decoration:none;transition:background .2s}
.btn-ghost:hover{background:rgba(255,255,255,.1)}
.hero-right{flex:.8;text-align:center}
.hero-right img{width:200px;height:200px;border-radius:50%;border:4px solid rgba(247,151,30,.15);box-shadow:0 24px 80px rgba(247,151,30,.1);transition:transform .3s}
.hero-right img:hover{transform:scale(1.03)}

.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:rgba(255,255,255,.04);border-top:1px solid rgba(255,255,255,.04);border-bottom:1px solid rgba(255,255,255,.04);max-width:900px;margin:0 auto;border-radius:16px;overflow:hidden}
.stat{background:#0a0a12;padding:28px 20px;text-align:center}
.stat .num{font-size:32px;font-weight:800;color:#ffd200}
.stat .lbl{font-size:13px;color:rgba(255,255,255,.35);margin-top:4px;font-weight:500}

.features{max-width:1000px;margin:0 auto;padding:80px 48px}
.features h2{text-align:center;font-size:32px;font-weight:800;margin-bottom:8px;letter-spacing:-.5px}
.features h2 span{background:linear-gradient(90deg,#f7971e,#ffd200);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.features .sub{text-align:center;color:rgba(255,255,255,.35);font-size:15px;margin-bottom:40px}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.card{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);border-radius:16px;padding:28px 24px;transition:border-color .2s,transform .2s}
.card:hover{border-color:rgba(247,151,30,.2);transform:translateY(-2px)}
.card .icon{font-size:36px;margin-bottom:12px;display:block}
.card h3{font-size:16px;font-weight:700;margin-bottom:6px}
.card p{font-size:13px;color:rgba(255,255,255,.4);line-height:1.5}

.cta{text-align:center;padding:60px 48px 80px}
.cta h2{font-size:32px;font-weight:800;margin-bottom:8px}
.cta p{color:rgba(255,255,255,.35);font-size:15px;margin-bottom:24px}
.cta .btn-gold{font-size:15px!important;padding:14px 36px!important;display:inline-block}

footer{text-align:center;padding:24px 48px;color:rgba(255,255,255,.1);font-size:13px;border-top:1px solid rgba(255,255,255,.04)}

@media(max-width:768px){
  nav{padding:14px 20px}
  .hero{flex-direction:column-reverse;padding:40px 20px;text-align:center}
  .hero-left h1{font-size:36px}
  .hero-btns{justify-content:center}
  .stats{grid-template-columns:repeat(2,1fr)}
  .grid{grid-template-columns:1fr}
  .features{padding:40px 20px}
}
</style>
</head>
<body>
<canvas id="stars"></canvas>
<div class="content">
<nav>
<div class="logo"><img src="/logo.png" alt=""><span>CashEmpireBot</span></div>
<div class="nav-links">
<a href="#features">Features</a>
<a href="#stats">Stats</a>
<a class="btn-gold" href="https://discord.gg/XAhXeJqAdw" target="_blank">Join Server</a>
</div>
</nav>

<div class="hero">
<div class="hero-left">
<div class="badges">
<div class="badge badge-green"><span class="dot"></span> Online</div>
<div class="badge badge-gold">32 Commands</div>
<div class="badge badge-purple">v2.0</div>
</div>
<h1>Build Your <span>Empire</span></h1>
<p>Earn coins, collect rare pets with multipliers, farm in voice channels, trade with friends, and climb the leaderboard. The ultimate Discord economy experience.</p>
<div class="hero-btns">
<a class="btn-gold" href="https://discord.gg/XAhXeJqAdw" target="_blank">Get Started</a>
<a class="btn-ghost" href="#features">Learn More</a>
</div>
</div>
<div class="hero-right"><img src="/logo.png" alt="CashEmpireBot"></div>
</div>

<div class="stats" id="stats">
<div class="stat"><div class="num">32</div><div class="lbl">Commands</div></div>
<div class="stat"><div class="num">24/7</div><div class="lbl">Uptime</div></div>
<div class="stat"><div class="num">3</div><div class="lbl">Crates</div></div>
<div class="stat"><div class="num">6</div><div class="lbl">Rarities</div></div>
</div>

<div class="features" id="features">
<h2>Everything You <span>Need</span></h2>
<p class="sub">Build your fortune with a complete economy ecosystem</p>
<div class="grid">
<div class="card"><span class="icon">💰</span><h3>Economy</h3><p>Work, collect daily rewards, gamble, and transfer coins to build your wealth</p></div>
<div class="card"><span class="icon">🐾</span><h3>Pet System</h3><p>Open crates, collect pets with unique multipliers, and equip your best ones</p></div>
<div class="card"><span class="icon">🎮</span><h3>Voice Farm</h3><p>Earn coins passively while in voice channels — active pets boost your gains</p></div>
<div class="card"><span class="icon">🏆</span><h3>Leaderboards</h3><p>Compete for the top spots and earn daily rewards with automatic posting</p></div>
<div class="card"><span class="icon">🔄</span><h3>Trading</h3><p>Sell pets you don't need and trade with other players in your server</p></div>
<div class="card"><span class="icon">⚡</span><h3>Boosters</h3><p>Activate 2x or 5x coin multipliers and unlock special bonuses</p></div>
</div>
</div>

<div class="cta">
<h2>Ready to Play?</h2>
<p>Join Cash Empire and start building your fortune today</p>
<a class="btn-gold" href="https://discord.gg/XAhXeJqAdw" target="_blank">Join the Server</a>
</div>

<footer>CashEmpireBot &copy; 2026 &bull; Running on Replit</footer>
</div>
<script>
const c=document.getElementById('stars'),ctx=c.getContext('2d');
c.width=window.innerWidth;c.height=window.innerHeight;
const stars=Array.from({length:150},()=>({x:Math.random()*c.width,y:Math.random()*c.height,r:Math.random()*1.5+0.5,a:Math.random(),s:Math.random()*.02+.005}));
function draw(){ctx.clearRect(0,0,c.width,c.height);stars.forEach(s=>{s.a+=s.s;const alpha=.3+Math.sin(s.a)*.4;ctx.beginPath();ctx.arc(s.x,s.y,s.r,0,Math.PI*2);ctx.fillStyle=`rgba(255,255,255,${alpha})`;ctx.fill()});requestAnimationFrame(draw)}
draw();
window.addEventListener('resize',()=>{c.width=window.innerWidth;c.height=window.innerHeight});
</script>
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
        HTTPServer(("0.0.0.0", 5000), Handler).serve_forever()
    except OSError:
        pass
Thread(target=run, daemon=True).start()
