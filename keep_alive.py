from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"CashEmpireBot is running")
    def log_message(self, *a): pass

def run():
    try:
        HTTPServer(("0.0.0.0", 8080), H).serve_forever()
    except: pass
Thread(target=run, daemon=True).start()
