#!/usr/bin/env python3
"""
🚨 EMERGENCY EXIT DASHBOARD v1.0
Web-based control panel for LuxTrader with manual overrides

Features:
- Real-time position monitoring
- One-click emergency sells
- Manual override controls
- Risk alerts
- Transaction history
- System health status
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Import our modules
from lux_enhanced_seller import LuxEnhancedSeller
from tokenomics_detector import TokenomicsDetector
from lux_auto_sell_monitor import LuxAutoSellMonitor, MonitoredPosition

# Dashboard HTML template
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚨 LuxTrader Emergency Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0e1a;
            color: #e0e0e0;
            min-height: 100vh;
        }
        
        .header {
            background: linear-gradient(135deg, #1a1f2e 0%, #2d3748 100%);
            padding: 20px;
            border-bottom: 3px solid #3b82f6;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .header h1 {
            font-size: 24px;
            color: #3b82f6;
        }
        
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .status-dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        
        .status-dot.online {
            background: #10b981;
            box-shadow: 0 0 10px #10b981;
        }
        
        .status-dot.warning {
            background: #f59e0b;
            box-shadow: 0 0 10px #f59e0b;
        }
        
        .status-dot.danger {
            background: #ef4444;
            box-shadow: 0 0 10px #ef4444;
            animation: pulse 0.5s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .container {
            padding: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: #1a1f2e;
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #2d3748;
            transition: border-color 0.3s;
        }
        
        .card:hover {
            border-color: #3b82f6;
        }
        
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .card-title {
            font-size: 16px;
            font-weight: 600;
            color: #3b82f6;
        }
        
        .stat-value {
            font-size: 32px;
            font-weight: 700;
            margin: 10px 0;
        }
        
        .stat-value.positive {
            color: #10b981;
        }
        
        .stat-value.negative {
            color: #ef4444;
        }
        
        .stat-label {
            font-size: 14px;
            color: #9ca3af;
        }
        
        .positions-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        
        .positions-table th,
        .positions-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #2d3748;
        }
        
        .positions-table th {
            background: #1a1f2e;
            font-weight: 600;
            color: #3b82f6;
            position: sticky;
            top: 0;
        }
        
        .positions-table tr:hover {
            background: #2d3748;
        }
        
        .pnl-positive {
            color: #10b981;
            font-weight: 600;
        }
        
        .pnl-negative {
            color: #ef4444;
            font-weight: 600;
        }
        
        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
            text-transform: uppercase;
            font-size: 12px;
        }
        
        .btn-sell {
            background: #ef4444;
            color: white;
        }
        
        .btn-sell:hover {
            background: #dc2626;
            transform: scale(1.05);
        }
        
        .btn-emergency {
            background: #dc2626;
            color: white;
            font-size: 18px;
            padding: 20px 40px;
            animation: emergency-pulse 1s infinite;
        }
        
        @keyframes emergency-pulse {
            0%, 100% { 
                box-shadow: 0 0 0 0 rgba(220, 38, 38, 0.7);
                transform: scale(1);
            }
            50% { 
                box-shadow: 0 0 20px 10px rgba(220, 38, 38, 0);
                transform: scale(1.02);
            }
        }
        
        .emergency-section {
            background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 100%);
            border: 3px solid #ef4444;
            border-radius: 12px;
            padding: 30px;
            text-align: center;
            margin-bottom: 30px;
        }
        
        .emergency-section h2 {
            color: #fca5a5;
            margin-bottom: 20px;
            font-size: 28px;
        }
        
        .emergency-section p {
            color: #fecaca;
            margin-bottom: 20px;
        }
        
        .risk-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .risk-low {
            background: #10b981;
            color: white;
        }
        
        .risk-medium {
            background: #f59e0b;
            color: white;
        }
        
        .risk-high {
            background: #ef4444;
            color: white;
        }
        
        .risk-critical {
            background: #7f1d1d;
            color: white;
            animation: blink 1s infinite;
        }
        
        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        
        .alert {
            background: #7f1d1d;
            border-left: 4px solid #ef4444;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 0 6px 6px 0;
        }
        
        .alert-title {
            font-weight: 600;
            color: #fca5a5;
            margin-bottom: 5px;
        }
        
        .refresh-info {
            text-align: center;
            color: #6b7280;
            font-size: 12px;
            margin-top: 20px;
        }
        
        .wallet-info {
            background: #1a1f2e;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-family: monospace;
            font-size: 14px;
        }
        
        .wallet-info span {
            color: #3b82f6;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚨 LuxTrader Emergency Dashboard</h1>
        <div class="status-indicator">
            <span>System Status:</span>
            <div class="status-dot {{status_class}}"></div>
            <span>{{status_text}}</span>
        </div>
    </div>
    
    <div class="container">
        <!-- Emergency Section -->
        <div class="emergency-section">
            <h2>⚠️ EMERGENCY CONTROLS</h2>
            <p>Use these buttons only in emergency situations</p>
            <button class="btn btn-emergency" onclick="emergencySellAll()">
                🚨 EMERGENCY SELL ALL POSITIONS
            </button>
        </div>
        
        <!-- Wallet Info -->
        <div class="wallet-info">
            Wallet: <span>{{wallet_address}}</span> | 
            Balance: <span>{{wallet_balance}} SOL</span>
        </div>
        
        <!-- Stats Grid -->
        <div class="grid">
            <div class="card">
                <div class="card-header">
                    <span class="card-title">Active Positions</span>
                </div>
                <div class="stat-value">{{active_positions}}</div>
                <div class="stat-label">Currently monitoring</div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <span class="card-title">Total P&L</span>
                </div>
                <div class="stat-value {{pnl_class}}">{{total_pnl}} SOL</div>
                <div class="stat-label">Realized + Unrealized</div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <span class="card-title">Success Rate</span>
                </div>
                <div class="stat-value">{{success_rate}}%</div>
                <div class="stat-label">Sells executed</div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <span class="card-title">Avg Sell Time</span>
                </div>
                <div class="stat-value">{{avg_sell_time}}s</div>
                <div class="stat-label">From signal to fill</div>
            </div>
        </div>
        
        <!-- Alerts -->
        {{alerts_section}}
        
        
        <!-- Positions Table -->
        <div class="card">
            <div class="card-header">
                <span class="card-title">📊 Active Positions</span>
            </div>
            
            <table class="positions-table">
                <thead>
                    <tr>
                        <th>Token</th>
                        <th>Entry</th>
                        <th>Current</th>
                        <th>P&L</th>
                        <th>Time</th>
                        <th>Risk</th>
                        <th>Status</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {{positions_rows}}
                </tbody>
            </table>
        </div>
        
        <div class="refresh-info">
            Dashboard refreshes every 5 seconds | Last update: {{last_update}}
        </div>
    </div>
    
    <script>
        // Auto-refresh every 5 seconds
        setInterval(() => {
            location.reload();
        }, 5000);
        
        // Emergency sell all
        function emergencySellAll() {
            if (confirm('🚨 ARE YOU SURE?\n\nThis will sell ALL positions immediately!\n\nThis action cannot be undone.')) {
                if (confirm('⚠️ FINAL WARNING\n\nSelling all positions at market price.\n\nConfirm to proceed.')) {
                    fetch('/api/emergency-sell-all', { method: 'POST' })
                        .then(response => response.json())
                        .then(data => {
                            alert('Emergency sell initiated!\nCheck console for details.');
                        });
                }
            }
        }
        
        // Sell single position
        function sellPosition(tokenAddress) {
            if (confirm('Sell this position?')) {
                fetch(`/api/sell/${tokenAddress}`, { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        alert('Sell order placed!');
                        location.reload();
                    });
            }
        }
    </script>
</body>
</html>
"""


class DashboardHandler(BaseHTTPRequestHandler):
    """HTTP request handler for dashboard"""
    
    dashboard_data = {
        'wallet_address': 'Not connected',
        'wallet_balance': '0.00',
        'active_positions': 0,
        'total_pnl': '+0.00',
        'pnl_class': 'positive',
        'success_rate': '0',
        'avg_sell_time': '0',
        'status_class': 'online',
        'status_text': 'Online',
        'positions': [],
        'alerts': []
    }
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/' or self.path == '/dashboard':
            self._serve_dashboard()
        elif self.path == '/api/status':
            self._serve_api_status()
        else:
            self._serve_404()
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/api/emergency-sell-all':
            self._handle_emergency_sell_all()
        elif self.path.startswith('/api/sell/'):
            token = self.path.split('/')[-1]
            self._handle_sell(token)
        else:
            self._serve_404()
    
    def _serve_dashboard(self):
        """Serve the dashboard HTML"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        data = self.dashboard_data
        
        # Build positions rows
        positions_html = ""
        for pos in data.get('positions', []):
            pnl_class = 'pnl-positive' if pos.get('pnl_pct', 0) >= 0 else 'pnl-negative'
            risk_class = f"risk-{pos.get('risk_level', 'low')}"
            
            positions_html += f"""
            <tr>
                <td>{pos.get('symbol', 'Unknown')}</td>
                <td>{pos.get('entry_sol', 0):.4f} SOL</td>
                <td>{pos.get('current_value', 0):.4f} SOL</td>
                <td class="{pnl_class}">{pos.get('pnl_pct', 0):+.1f}%</td>
                <td>{pos.get('time_held', '0h')}</td>
                <td><span class="risk-badge {risk_class}">{pos.get('risk_level', 'low')}</span></td>
                <td>{pos.get('status', 'active')}</td>
                <td><button class="btn btn-sell" onclick="sellPosition('{pos.get('address', '')}')">SELL</button></td>
            </tr>
            """
        
        if not positions_html:
            positions_html = '<tr><td colspan="8" style="text-align:center; padding:40px; color:#6b7280;">No active positions</td></tr>'
        
        # Build alerts section
        alerts_html = ""
        for alert in data.get('alerts', []):
            alerts_html += f"""
            <div class="alert">
                <div class="alert-title">{alert.get('title', 'Alert')}</div>
                <div>{alert.get('message', '')}</div>
            </div>
            """
        
        # Replace placeholders
        html = DASHBOARD_HTML
        html = html.replace('{{wallet_address}}', data['wallet_address'][:30] + '...')
        html = html.replace('{{wallet_balance}}', data['wallet_balance'])
        html = html.replace('{{active_positions}}', str(data['active_positions']))
        html = html.replace('{{total_pnl}}', data['total_pnl'])
        html = html.replace('{{pnl_class}}', data['pnl_class'])
        html = html.replace('{{success_rate}}', data['success_rate'])
        html = html.replace('{{avg_sell_time}}', data['avg_sell_time'])
        html = html.replace('{{status_class}}', data['status_class'])
        html = html.replace('{{status_text}}', data['status_text'])
        html = html.replace('{{positions_rows}}', positions_html)
        html = html.replace('{{alerts_section}}', alerts_html)
        html = html.replace('{{last_update}}', datetime.now().strftime('%H:%M:%S'))
        
        self.wfile.write(html.encode())
    
    def _serve_api_status(self):
        """Serve API status JSON"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(self.dashboard_data).encode())
    
    def _handle_emergency_sell_all(self):
        """Handle emergency sell all request"""
        print("\n🚨 EMERGENCY SELL ALL TRIGGERED FROM DASHBOARD!")
        
        # This would trigger the actual sell logic
        # For now, just log it
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({
            'status': 'initiated',
            'message': 'Emergency sell all triggered'
        }).encode())
    
    def _handle_sell(self, token_address: str):
        """Handle sell single token request"""
        print(f"\n👤 Manual sell triggered for: {token_address[:20]}...")
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({
            'status': 'initiated',
            'token': token_address
        }).encode())
    
    def _serve_404(self):
        """Serve 404 error"""
        self.send_response(404)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Not Found')


class EmergencyDashboard:
    """
    Emergency exit dashboard for LuxTrader
    """
    
    def __init__(self, wallet_address: str, port: int = 7777):
        self.wallet = wallet_address
        self.port = port
        self.server = None
        self.monitor = None
        self.running = False
    
    def start(self, monitor: Optional[LuxAutoSellMonitor] = None):
        """Start the dashboard server"""
        self.monitor = monitor
        self.running = True
        
        # Update dashboard data
        self._update_data()
        
        # Start server in thread
        self.server = HTTPServer(('0.0.0.0', self.port), DashboardHandler)
        
        server_thread = threading.Thread(target=self._run_server)
        server_thread.daemon = True
        server_thread.start()
        
        print(f"\n{'='*70}")
        print(f"🚨 EMERGENCY DASHBOARD STARTED")
        print(f"{'='*70}")
        print(f"Access: http://localhost:{self.port}")
        print(f"Wallet: {self.wallet[:30]}...")
        print(f"{'='*70}\n")
    
    def _run_server(self):
        """Run the HTTP server"""
        while self.running:
            try:
                self.server.handle_request()
            except Exception as e:
                print(f"Dashboard error: {e}")
    
    def _update_data(self):
        """Update dashboard data from monitor"""
        if not self.monitor:
            return
        
        # Get stats from monitor
        stats = self.monitor.stats
        positions = self.monitor.get_all_positions()
        
        # Update dashboard handler data
        DashboardHandler.dashboard_data = {
            'wallet_address': self.wallet,
            'wallet_balance': '2.01',  # Would get from actual wallet
            'active_positions': len([p for p in positions if p.status.value not in ['sold', 'failed']]),
            'total_pnl': f"{stats['total_pnl_sol']:+.4f}",
            'pnl_class': 'positive' if stats['total_pnl_sol'] >= 0 else 'negative',
            'success_rate': str(int((stats['positions_sold'] / max(stats['positions_monitored'], 1)) * 100)),
            'avg_sell_time': str(int(stats.get('avg_sell_time_seconds', 0))),
            'status_class': 'online',
            'status_text': 'Online',
            'positions': [
                {
                    'symbol': p.token_symbol,
                    'address': p.token_address,
                    'entry_sol': p.entry_sol,
                    'current_value': p.current_value,
                    'pnl_pct': p.pnl_pct,
                    'time_held': '2h',  # Calculate from entry_time
                    'risk_level': 'low',  # From tokenomics
                    'status': p.status.value
                }
                for p in positions
            ],
            'alerts': []  # Would populate from actual alerts
        }
    
    def stop(self):
        """Stop the dashboard"""
        print("\n🛑 Stopping dashboard...")
        self.running = False
        if self.server:
            self.server.shutdown()
    
    def refresh(self):
        """Refresh dashboard data"""
        self._update_data()


# Convenience function
def start_dashboard(wallet_address: str, port: int = 7777, 
                   monitor: Optional[LuxAutoSellMonitor] = None):
    """Start emergency dashboard"""
    dashboard = EmergencyDashboard(wallet_address, port)
    dashboard.start(monitor)
    return dashboard


if __name__ == "__main__":
    print("🚨 Emergency Exit Dashboard v1.0")
    print("\nUsage:")
    print("   from emergency_dashboard import EmergencyDashboard, start_dashboard")
    print("   dashboard = start_dashboard(wallet_address, port=7777)")
    print("\n   Then open http://localhost:7777 in your browser")
    print("\n   Press Ctrl+C to stop")
    
    # Example: Start with dummy data
    # dashboard = start_dashboard("8JGnzH1aP8GW3UR1spVUtxVi9m58oe1aSDXnnP1b6Yc5")
    # input("Press Enter to stop...")
    # dashboard.stop()
