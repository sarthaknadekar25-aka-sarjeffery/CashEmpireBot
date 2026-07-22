from http.server import HTTPServer, SimpleHTTPRequestHandler
import os, threading

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.path = "/index.html"
        return super().do_GET()

    def log_message(self, *a):
        pass

def run():
    port = int(os.getenv("PORT", 8080))
    try:
        server = HTTPServer(("0.0.0.0", port), Handler)
        server.serve_forever()
    except OSError:
        pass

def keep_alive():
    t = threading.Thread(target=run, daemon=True)
    t.start()
