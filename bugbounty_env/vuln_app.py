#!/usr/bin/env python3
"""
DVWA-Style Vulnerable Web App for Practice
Local bug bounty training environment

Run: python3 vuln_app.py
Access: http://localhost:8080
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import sqlite3
import os
import json

# Database setup
def init_db():
    conn = sqlite3.connect('vuln_app.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT, password TEXT, email TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS comments
                 (id INTEGER PRIMARY KEY, name TEXT, comment TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Insert test data
    c.execute("INSERT OR IGNORE INTO users VALUES (1, 'admin', 'password123', 'admin@vulnapp.local')")
    c.execute("INSERT OR IGNORE INTO users VALUES (2, 'user', 'userpass', 'user@vulnapp.local')")
    c.execute("INSERT OR IGNORE INTO users VALUES (3, 'guest', 'guestpass', 'guest@vulnapp.local')")
    conn.commit()
    conn.close()

class VulnHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        query = urllib.parse.parse_qs(parsed_path.query)
        
        if path == '/':
            self.show_home()
        elif path == '/sqli':
            self.show_sqli(query)
        elif path == '/xss':
            self.show_xss(query)
        elif path == '/idor':
            self.show_idor(query)
        elif path == '/ssrf':
            self.show_ssrf(query)
        elif path == '/api/users':
            self.api_users(query)
        else:
            self.send_error(404)
    
    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        params = urllib.parse.parse_qs(post_data)
        
        if path == '/xss':
            self.post_xss(params)
        elif path == '/sqli':
            self.post_sqli(params)
        else:
            self.send_error(404)
    
    def show_home(self):
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>VulnApp - Practice Target</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
                h1 { color: #d9534f; }
                .vuln-box { border: 2px solid #d9534f; padding: 15px; margin: 20px 0; border-radius: 5px; }
                .vuln-box h3 { margin-top: 0; color: #d9534f; }
                a { color: #337ab7; text-decoration: none; }
                a:hover { text-decoration: underline; }
                code { background: #f5f5f5; padding: 2px 5px; border-radius: 3px; }
            </style>
        </head>
        <body>
            <h1>🔴 VulnApp - Practice Target</h1>
            <p><strong>Warning:</strong> This application is intentionally vulnerable. Use only for learning!</p>
            
            <div class="vuln-box">
                <h3>1. SQL Injection (SQLi)</h3>
                <p>Test SQL injection in the user search:</p>
                <ul>
                    <li><a href="/sqli?id=1">Normal query (id=1)</a></li>
                    <li><a href="/sqli?id=1' OR '1'='1">SQLi test (' OR '1'='1)</a></li>
                    <li><a href="/sqli?id=1' UNION SELECT username,password,email FROM users--">Union-based SQLi</a></li>
                </ul>
                <p><code>GET /sqli?id=[payload]</code></p>
            </div>
            
            <div class="vuln-box">
                <h3>2. Cross-Site Scripting (XSS)</h3>
                <p>Test reflected and stored XSS:</p>
                <ul>
                    <li><a href="/xss?name=test">Normal (name=test)</a></li>
                    <li><a href="/xss?name=<script>alert('XSS')</script>">Reflected XSS</a></li>
                    <li><a href="/xss?name=<img src=x onerror=alert('XSS')>">Image onerror XSS</a></li>
                </ul>
                <p><code>GET /xss?name=[payload]</code></p>
                <p>Or POST to <code>/xss</code> with <code>name</code> and <code>comment</code> parameters</p>
            </div>
            
            <div class="vuln-box">
                <h3>3. Insecure Direct Object Reference (IDOR)</h3>
                <p>Access other users' data by changing IDs:</p>
                <ul>
                    <li><a href="/idor?user_id=1">User 1 (admin)</a></li>
                    <li><a href="/idor?user_id=2">User 2</a></li>
                    <li><a href="/idor?user_id=3">User 3</a></li>
                    <li><a href="/idor?user_id=999">Non-existent user</a></li>
                </ul>
                <p><code>GET /idor?user_id=[id]</code></p>
            </div>
            
            <div class="vuln-box">
                <h3>4. Server-Side Request Forgery (SSRF)</h3>
                <p>Make the server request internal resources:</p>
                <ul>
                    <li><a href="/ssrf?url=https://example.com">External URL</a></li>
                    <li><a href="/ssrf?url=http://localhost:8080">Localhost</a></li>
                    <li><a href="/ssrf?url=file:///etc/passwd">File read attempt</a></li>
                </ul>
                <p><code>GET /ssrf?url=[target]</code></p>
            </div>
            
            <div class="vuln-box">
                <h3>5. API Endpoints</h3>
                <p>Test API vulnerabilities:</p>
                <ul>
                    <li><a href="/api/users">List all users (JSON)</a></li>
                    <li><a href="/api/users?id=1">Get user by ID</a></li>
                </ul>
            </div>
            
            <hr>
            <p><small>Practice responsibly. Report generation: <code>python3 report_gen.py --template [type]</code></small></p>
        </body>
        </html>
        """
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def show_sqli(self, query):
        """SQL Injection vulnerability"""
        user_id = query.get('id', ['1'])[0]
        
        conn = sqlite3.connect('vuln_app.db')
        c = conn.cursor()
        
        # VULNERABLE: Direct string concatenation
        try:
            c.execute(f"SELECT * FROM users WHERE id = '{user_id}'")
            users = c.fetchall()
        except Exception as e:
            users = []
            error = str(e)
        conn.close()
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>SQL Injection Test</title></head>
        <body>
            <h1>SQL Injection Practice</h1>
            <p>Query executed: <code>SELECT * FROM users WHERE id = '{user_id}'</code></p>
            <form method="GET" action="/sqli">
                <input type="text" name="id" value="{user_id}" placeholder="Enter user ID">
                <button type="submit">Search</button>
            </form>
            <h3>Results:</h3>
            <table border="1">
                <tr><th>ID</th><th>Username</th><th>Password</th><th>Email</th></tr>
        """
        
        for user in users:
            html += f"<tr><td>{user[0]}</td><td>{user[1]}</td><td>{user[2]}</td><td>{user[3]}</td></tr>"
        
        html += """
            </table>
            <p><a href="/">← Back to home</a></p>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def post_sqli(self, params):
        """POST-based SQL Injection"""
        username = params.get('username', [''])[0]
        password = params.get('password', [''])[0]
        
        conn = sqlite3.connect('vuln_app.db')
        c = conn.cursor()
        
        # VULNERABLE: Direct string concatenation
        try:
            c.execute(f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'")
            user = c.fetchone()
        except Exception as e:
            user = None
            error = str(e)
        conn.close()
        
        if user:
            html = f"<h1>Welcome {user[1]}!</h1><p>Login successful.</p>"
        else:
            html = "<h1>Login Failed</h1><p>Invalid credentials.</p>"
        
        html += '<p><a href="/">← Back to home</a></p>'
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def show_xss(self, query):
        """XSS vulnerability"""
        name = query.get('name', ['Guest'])[0]
        
        # VULNERABLE: No sanitization
        html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>XSS Test</title></head>
        <body>
            <h1>XSS Practice</h1>
            <p>Hello, {name}!</p>
            <form method="GET" action="/xss">
                <input type="text" name="name" placeholder="Enter your name">
                <button type="submit">Submit</button>
            </form>
            <h3>Try these payloads:</h3>
            <ul>
                <li><code>&lt;script&gt;alert('XSS')&lt;/script&gt;</code></li>
                <li><code>&lt;img src=x onerror=alert('XSS')&gt;</code></li>
                <li><code>&lt;svg onload=alert('XSS')&gt;</code></li>
            </ul>
            <p><a href="/">← Back to home</a></p>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def post_xss(self, params):
        """Stored XSS via comments"""
        name = params.get('name', ['Anonymous'])[0]
        comment = params.get('comment', [''])[0]
        
        conn = sqlite3.connect('vuln_app.db')
        c = conn.cursor()
        # VULNERABLE: No sanitization before storing
        c.execute("INSERT INTO comments (name, comment) VALUES (?, ?)", (name, comment))
        conn.commit()
        
        # Retrieve all comments
        c.execute("SELECT * FROM comments ORDER BY created_at DESC")
        comments = c.fetchall()
        conn.close()
        
        html = """
        <!DOCTYPE html>
        <html>
        <head><title>Stored XSS - Comments</title></head>
        <body>
            <h1>Comments (Stored XSS)</h1>
            <form method="POST" action="/xss">
                <input type="text" name="name" placeholder="Your name"><br><br>
                <textarea name="comment" placeholder="Your comment"></textarea><br><br>
                <button type="submit">Post Comment</button>
            </form>
            <h3>All Comments:</h3>
        """
        
        for c in comments:
            # VULNERABLE: No output encoding
            html += f"<div style='border:1px solid #ccc; padding:10px; margin:10px 0;'>"
            html += f"<strong>{c[1]}</strong> <small>({c[3]})</small><br>"
            html += f"{c[2]}"
            html += f"</div>"
        
        html += '<p><a href="/">← Back to home</a></p></body></html>'
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def show_idor(self, query):
        """IDOR vulnerability"""
        user_id = query.get('user_id', ['1'])[0]
        
        conn = sqlite3.connect('vuln_app.db')
        c = conn.cursor()
        
        # VULNERABLE: No authorization check
        c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = c.fetchone()
        conn.close()
        
        if user:
            html = f"""
            <h1>User Profile</h1>
            <table border="1">
                <tr><td>ID</td><td>{user[0]}</td></tr>
                <tr><td>Username</td><td>{user[1]}</td></tr>
                <tr><td>Password</td><td>{user[2]}</td></tr>
                <tr><td>Email</td><td>{user[3]}</td></tr>
            </table>
            """
        else:
            html = "<h1>User Not Found</h1><p>No user with that ID.</p>"
        
        html += """
        <form method="GET" action="/idor">
            <input type="text" name="user_id" placeholder="Enter user ID">
            <button type="submit">View User</button>
        </form>
        <p>Try changing the user_id parameter!</p>
        <p><a href="/">← Back to home</a></p>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def show_ssrf(self, query):
        """SSRF vulnerability"""
        import urllib.request
        
        url = query.get('url', ['https://example.com'])[0]
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>SSRF Test</title></head>
        <body>
            <h1>SSRF Practice</h1>
            <p>Fetching: {url}</p>
            <form method="GET" action="/ssrf">
                <input type="text" name="url" value="{url}" placeholder="Enter URL to fetch">
                <button type="submit">Fetch</button>
            </form>
        """
        
        try:
            # VULNERABLE: No URL validation
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                content = response.read().decode('utf-8', errors='ignore')[:2000]
                html += f"<h3>Response (first 2000 chars):</h3><pre>{content}</pre>"
        except Exception as e:
            html += f"<h3>Error:</h3><pre>{str(e)}</pre>"
        
        html += """
            <h3>Try these:</h3>
            <ul>
                <li><code>http://localhost:8080</code> - Local service</li>
                <li><code>http://127.0.0.1:22</code> - SSH banner</li>
                <li><code>file:///etc/passwd</code> - File read</li>
            </ul>
            <p><a href="/">← Back to home</a></p>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def api_users(self, query):
        """API endpoint with potential IDOR"""
        conn = sqlite3.connect('vuln_app.db')
        c = conn.cursor()
        
        if 'id' in query:
            user_id = query['id'][0]
            c.execute("SELECT id, username, email FROM users WHERE id = ?", (user_id,))
            user = c.fetchone()
            data = {'user': user} if user else {'error': 'Not found'}
        else:
            c.execute("SELECT id, username, email FROM users")
            users = c.fetchall()
            data = {'users': users}
        
        conn.close()
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode())
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass

def run_server(port=8080):
    init_db()
    server = HTTPServer(('localhost', port), VulnHandler)
    print(f"[*] VulnApp running at http://localhost:{port}")
    print(f"[*] Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Shutting down...")
        server.shutdown()

if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8888
    run_server(port)
