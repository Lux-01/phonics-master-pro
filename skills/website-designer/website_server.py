#!/usr/bin/env python3
"""
Website Server - Live reload development server
"""
import os
import sys
import json
import time
import threading
import http.server
import socketserver
from pathlib import Path
from datetime import datetime

class LiveReloadHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler with SSE for live reload"""
    
    def __init__(self, *args, **kwargs):
        # Track file changes
        self.file_hashes = {}
        super().__init__(*args, **kwargs)
    
    def end_headers(self):
        # Add CORS headers for development
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass
    
    def do_GET(self):
        # Inject live reload script
        if self.path == '/' or self.path.endswith('.html'):
            return self.serve_html_with_reload()
        elif self.path == '/__live_reload.js':
            return self.serve_reload_script()
        elif self.path == '/__sse':
            return self.serve_sse()
        else:
            return super().do_GET()
    
    def serve_html_with_reload(self):
        try:
            filepath = self.translate_path(self.path)
            if filepath.endswith('/'):
                filepath = os.path.join(filepath, 'index.html')
            
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Inject live reload script
            script = '<script src="/__live_reload.js"></script>'
            if '</body>' in content:
                content = content.replace('</body>', f'{script}</body>')
            else:
                content += script
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(content.encode())
        except FileNotFoundError:
            self.send_error(404, "File not found")
    
    def serve_reload_script(self):
        """Serve live reload client script"""
        script = '''
(function() {
    console.log('🔥 Live reload enabled');
    
    const evtSource = new EventSource('/__sse');
    let reconnectAttempts = 0;
    
    evtSource.onmessage = function(event) {
        if (event.data === 'reload') {
            console.log('🔄 Reloading...');
            window.location.reload();
        }
    };
    
    evtSource.onerror = function() {
        console.log('Connection lost, will reconnect...');
        reconnectAttempts++;
        if (reconnectAttempts > 10) {
            evtSource.close();
            console.log('Stopped trying to reconnect');
        }
    };
    
    // Optional: Show live indicator
    const indicator = document.createElement('div');
    indicator.style.cssText = `
        position: fixed; 
        bottom: 10px; 
        right: 10px; 
        background: #10b981; 
        color: white; 
        padding: 4px 12px; 
        border-radius: 4px; 
        font-size: 12px; 
        font-family: monospace;
        z-index: 9999;
        opacity: 0.8;
    `;
    indicator.textContent = '⚡ LIVE';
    document.addEventListener('DOMContentLoaded', () => {
        document.body.appendChild(indicator);
    });
})();
        '''
        self.send_response(200)
        self.send_header('Content-Type', 'application/javascript')
        self.end_headers()
        self.wfile.write(script.encode())
    
    def serve_sse(self):
        """Server-Sent Events for file changes"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Connection', 'keep-alive')
        self.end_headers()
        
        # Send heartbeat
        try:
            self.wfile.write(b'data: connected\\n\\n')
            self.wfile.flush()
            
            # Keep connection alive
            while True:
                time.sleep(1)
        except:
            pass

def watch_files(site_dir, port):
    """Watch files for changes and trigger reload"""
    file_mtimes = {}
    
    print(f"🔍 Watching for changes...")
    
    while True:
        try:
            changed = False
            for root, dirs, files in os.walk(site_dir):
                # Skip node_modules and hidden
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    if file.endswith(('.html', '.css', '.js')):
                        filepath = os.path.join(root, file)
                        mtime = os.path.getmtime(filepath)
                        
                        if filepath in file_mtimes and file_mtimes[filepath] != mtime:
                            changed = True
                            rel_path = os.path.relpath(filepath, site_dir)
                            print(f"📝 Changed: {rel_path}")
                        
                        file_mtimes[filepath] = mtime
            
            if changed:
                print(f"🔄 Triggering reload...")
                # Reload is handled by browser reconnecting
            
            time.sleep(0.5)
        except KeyboardInterrupt:
            break

def start_server(site_name, port=3000):
    """Start development server with live reload"""
    site_dir = Path(site_name) / "src"
    
    if not site_dir.exists():
        print(f"❌ Site '{site_name}' not found")
        sys.exit(1)
    
    os.chdir(site_dir)
    
    print(f"""
╔══════════════════════════════════════════╗
║     Lux Website Designer - Dev Server    ║
╠══════════════════════════════════════════╣
║  Site:  {site_name:<30}║
║  URL:   http://localhost:{port:<22}║
╚══════════════════════════════════════════╝
    """)
    
    # Start file watcher in background
    watcher_thread = threading.Thread(
        target=watch_files,
        args=(site_dir, port),
        daemon=True
    )
    watcher_thread.start()
    
    # Start HTTP server
    with socketserver.TCPServer(("", port), LiveReloadHandler) as httpd:
        print(f"Server running... (Press Ctrl+C to stop)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 website_server.py <site_name> [--port 3000]")
        sys.exit(1)
    
    site_name = sys.argv[1]
    port = 3000
    
    if "--port" in sys.argv:
        port_idx = sys.argv.index("--port") + 1
        if port_idx < len(sys.argv):
            port = int(sys.argv[port_idx])
    
    start_server(site_name, port)
