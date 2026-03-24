#!/usr/bin/env python3
"""Raphael Monitor - Clean ASCII version"""

import json
import http.server
import socketserver
import time
from datetime import datetime, timedelta

PORT = 3456

STATE = {
    "agent": "raphael",
    "mode": "LIVE_TEST",
    "status": "READY",
    "subagentStatus": "ACTIVE",
    "subagentLastSeen": "LIVE",
    "balance": 1.17,
    "startingBalance": 1.17,
    "targetBalance": 110.0,
    "tradesToday": 0,
    "totalTrades": 0,
    "wins": 0,
    "losses": 0,
    "skips": 0,
    "realizedPnl": 0.0,
    "unrealizedPnl": 0.0,
    "positions": [],
    "walletAddress": "8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5"
}

def load_state():
    try:
        with open('/tmp/raphael_live_state.json', 'r') as f:
            data = json.load(f)
            STATE['tradesToday'] = data.get('trades_today', 0)
            STATE['totalTrades'] = len(data.get('trade_history', []))
            STATE['balance'] = data.get('wallet_balance', 1.17)
            STATE['status'] = data.get('status', 'IDLE')
    except:
        pass

class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.path == '/':
            self.serve_html()
        elif self.path == '/api/status':
            self.serve_json()
        else:
            self.send_error(404)

    def serve_html(self):
        load_state()
        progress = (STATE['balance'] / STATE['targetBalance']) * 100
        win_rate = (STATE['wins'] / (STATE['wins'] + STATE['losses']) * 100) if (STATE['wins'] + STATE['losses']) > 0 else 0
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Raphael Monitor</title>
    <meta http-equiv="refresh" content="5">
    <style>
        body {{ font-family: monospace; background: #0a0a0a; color: #00ff88; margin: 0; padding: 20px; }}
        .header {{ text-align: center; padding: 20px; background: #111; border-bottom: 2px solid #00ff88; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px; margin: 30px 0; }}
        .panel {{ background: #111; border: 1px solid #333; border-radius: 8px; padding: 20px; }}
        .panel h2 {{ margin: 0 0 15px 0; color: #00ff88; font-size: 1.1em; border-bottom: 1px solid #333; padding-bottom: 10px; }}
        .stat-row {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #222; }}
        .stat-row:last-child {{ border: none; }}
        .stat-label {{ color: #888; }}
        .stat-value {{ color: #fff; font-weight: bold; }}
        .win {{ color: #00ff88; }}
        .loss {{ color: #ff4444; }}
        .progress-bar {{ width: 100%; height: 30px; background: #0a0a0a; border-radius: 15px; overflow: hidden; margin: 20px 0; border: 2px solid #00ff88; }}
        .progress-fill {{ height: 100%; background: linear-gradient(90deg, #00ff88, #00cc66); display: flex; align-items: center; justify-content: center; color: #000; font-weight: bold; }}
        .footer {{ text-align: center; padding: 20px; color: #666; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>[RAPHAEL]</h1>
        <p>LIVE TEST | 1.17 SOL --&gt; 110 SOL | Phase 1 (0.01 SOL trades)</p>
    </div>
    
    <div class="progress-bar">
        <div class="progress-fill" style="width: {progress:.1f}%">{progress:.2f}%</div>
    </div>
    
    <div class="grid">
        <div class="panel">
            <h2>[Stats] Portfolio</h2>
            <div class="stat-row">
                <span class="stat-label">Balance</span>
                <span class="stat-value">{STATE['balance']:.4f} SOL</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Realized PNL</span>
                <span class="stat-value {'win' if STATE['realizedPnl'] >= 0 else 'loss'}">{STATE['realizedPnl']:+.4f} SOL</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Total Trades</span>
                <span class="stat-value">{STATE['totalTrades']}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Win Rate</span>
                <span class="stat-value">{win_rate:.1f}%</span>
            </div>
        </div>
        
        <div class="panel">
            <h2>[Chart] Today's Stats</h2>
            <div class="stat-row">
                <span class="stat-label">Trades Today</span>
                <span class="stat-value">{STATE['tradesToday']}/5</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Wins</span>
                <span class="stat-value win">{STATE['wins']}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Losses</span>
                <span class="stat-value loss">{STATE['losses']}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Status</span>
                <span class="stat-value">{STATE['status']}</span>
            </div>
        </div>
    </div>
    
    <div class="panel">
        <h2>[Wallet] Info</h2>
        <div class="stat-row">
            <span class="stat-label">Address</span>
            <span class="stat-value">{STATE['walletAddress'][:20]}...</span>
        </div>
        <div class="stat-row">
            <span class="stat-label">Mode</span>
            <span class="stat-value">{STATE['mode']}</span>
        </div>
    </div>
    
    <div class="footer">
        <p>The Adaptive Edge | 40 Rules Active</p>
    </div>
</body>
</html>"""
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def serve_json(self):
        load_state()
        win_rate = (STATE['wins'] / (STATE['wins'] + STATE['losses']) * 100) if (STATE['wins'] + STATE['losses']) > 0 else 0
        
        response = {
            "agent": STATE['agent'],
            "mode": STATE['mode'],
            "status": STATE['status'],
            "balance": STATE['balance'],
            "wallet_balance": STATE['balance'],
            "target_trades": 5,
            "trades_today": STATE['tradesToday'],
            "total_trades": STATE['totalTrades'],
            "wins": STATE['wins'],
            "losses": STATE['losses'],
            "realized_pnl": STATE['realizedPnl'],
            "wallet_address": STATE['walletAddress'],
            "win_rate": win_rate,
            "subagent_status": STATE['subagentStatus'],
            "last_update": datetime.now().isoformat(),
            "progress_to_target": (STATE['balance'] / STATE['targetBalance']) * 100
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

class ReuseAddrTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

if __name__ == "__main__":
    with ReuseAddrTCPServer(("", PORT), Handler) as httpd:
        print(f"Raphael Monitor running on port {PORT}", flush=True)
        httpd.serve_forever()
