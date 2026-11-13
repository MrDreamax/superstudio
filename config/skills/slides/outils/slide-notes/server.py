#!/usr/bin/env python3
"""Slide Notes : sert la page + enregistre les retours dans notes.json.
Usage : python3 server.py <dossier> <port>"""
import http.server, json, os, sys, time

D = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 8823
os.chdir(D)

class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass

    def do_GET(self):
        if self.path.startswith("/api/notes"):
            body = open("notes.json", "rb").read() if os.path.exists("notes.json") else b"{}"
            self.send_response(200); self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store"); self.end_headers(); self.wfile.write(body); return
        return super().do_GET()

    def do_POST(self):
        if not self.path.startswith("/api/notes"):
            self.send_error(404); return
        n = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(n) or b"{}")
        data["saved_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        tmp = "notes.json.tmp"
        json.dump(data, open(tmp, "w"), ensure_ascii=False, indent=1)
        os.replace(tmp, "notes.json")
        self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers()
        self.wfile.write(b'{"ok":true}')

http.server.ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
