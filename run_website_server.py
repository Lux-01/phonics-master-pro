#!/usr/bin/env python3
"""Simple HTTP server for Restored Right website - runs on all interfaces"""

import http.server
import socketserver
import os

PORT = 8888
DIRECTORY = "/home/skux/.openclaw/workspace/restored_right_redesign"

os.chdir(DIRECTORY)

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    print(f"Server running at http://172.26.93.172:{PORT}")
    print(f"Local access: http://127.0.0.1:{PORT}")
    print("\nAll pages:")
    print(f"  http://172.26.93.172:{PORT}/index.html")
    print(f"  http://172.26.93.172:{PORT}/services.html")
    print(f"  http://172.26.93.172:{PORT}/about.html")
    print(f"  http://172.26.93.172:{PORT}/emergency.html")
    print(f"  http://172.26.93.172:{PORT}/areas.html")
    print(f"  http://172.26.93.172:{PORT}/contact.html")
    print("\nCtrl+C to stop")
    httpd.serve_forever()
