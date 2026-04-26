#!/usr/bin/env python3
"""
TileBench Wave Server
---------------------
Serves two things from a single origin (no CORS issues):
  /          →  Surfer WASM static files  (/opt/surfer-web/)
  /files/    →  workspace VCD files       (/workspace/)

VeriFlow opens the browser at:
  http://localhost:7681/?load_url=http://localhost:7681/files/<path-to-vcd>
"""

import http.server
import os
from pathlib import Path

SURFER_DIR  = Path("/opt/surfer-web")
WORKSPACE_DIR = Path("/workspace")
PORT = 7681


class WaveHandler(http.server.SimpleHTTPRequestHandler):

    def translate_path(self, path: str) -> str:
        # Strip query string
        path = path.split("?", 1)[0]

        if path.startswith("/files/"):
            rel = path[len("/files/"):]
            return str(WORKSPACE_DIR / rel.lstrip("/"))

        # Everything else → Surfer WASM
        rel = path.lstrip("/") or "index.html"
        return str(SURFER_DIR / rel)

    def end_headers(self):
        # Required for SharedArrayBuffer used by WASM threading
        self.send_header("Cross-Origin-Opener-Policy",   "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
        self.send_header("Access-Control-Allow-Origin",  "*")
        super().end_headers()

    def log_message(self, fmt, *args):
        pass  # Keep container output clean


if __name__ == "__main__":
    os.chdir(str(SURFER_DIR))  # Default working dir for SimpleHTTPRequestHandler
    with http.server.HTTPServer(("0.0.0.0", PORT), WaveHandler) as httpd:
        print(f"[wave_server] Surfer ready at http://localhost:{PORT}")
        httpd.serve_forever()
