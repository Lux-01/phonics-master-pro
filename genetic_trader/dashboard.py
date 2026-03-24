#!/usr/bin/env python3
"""
Genetic Trading System - Real-time Dashboard
Displays PnL, holdings, performance metrics
"""

import json
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict
import os

class TradingDashboard:
    """Real-time dashboard for genetic trading system"""
    
    def __init__(self, data_dir: str = "/home/skux/.openclaw/workspace/genetic_trader"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.data_dir / "history.json"
        self.trades_file = self.data_dir / "trades.json"
        self.performance_file = self.data_dir / "performance.json"
        
    def update(self, strategies: List, cycle_number: int):
        """Update dashboard with current strategy data"""
        timestamp = datetime.now().isoformat()
        
        dashboard_data = {
            "timestamp": timestamp,
            "cycle_number": cycle_number,
            "summary": self._calculate_summary(strategies),
            "strategies": [self._format_strategy(s) for s in strategies],
            "leaderboard": self._calculate_leaderboard(strategies),
            "trades_today": self._get_todays_trades(strategies),
            "holdings": self._get_all_holdings(strategies),
        }
        
        # Save to history
        self._append_history(dashboard_data)
        
        # Save current state
        with open(self.data_dir / "current_dashboard.json", 'w') as f:
            json.dump(dashboard_data, f, indent=2)
        
        return dashboard_data
    
    def _calculate_summary(self, strategies: List) -> Dict:
        """Calculate portfolio summary"""
        total_pnl_sol = sum(s.total_pnl_sol for s in strategies)
        total_pnl_usd = sum(s.total_pnl_usd for s in strategies)
        total_capital = sum(s.current_sol + s.get_invested_sol() for s in strategies)
        initial_capital = sum(s.initial_sol for s in strategies)
        
        total_trades = sum(s.get_total_trades() for s in strategies)
        open_positions = sum(s.get_open_positions() for s in strategies)
        
        total_wins = sum(s.win_count for s in strategies)
        total_losses = sum(s.loss_count for s in strategies)
        win_rate = (total_wins / (total_wins + total_losses) * 100) if (total_wins + total_losses) > 0 else 0
        
        return {
            "total_strategies": len(strategies),
            "total_capital_sol": total_capital,
            "total_capital_usd": total_capital * 150,  # Approx
            "initial_capital_sol": initial_capital,
            "total_pnl_sol": total_pnl_sol,
            "total_pnl_usd": total_pnl_usd,
            "pnl_percentage": (total_pnl_sol / initial_capital * 100) if initial_capital > 0 else 0,
            "total_trades": total_trades,
            "open_positions": open_positions,
            "closed_trades": total_trades - open_positions,
            "win_rate": win_rate,
            "active_strategies": sum(1 for s in strategies if s.active),
            "evolution_generation": max(s.generation for s in strategies) if strategies else 0,
        }
    
    def _format_strategy(self, strategy) -> Dict:
        """Format strategy data for dashboard"""
        return {
            "id": strategy.id,
            "name": strategy.name,
            "description": strategy.description,
            "timeframe": strategy.timeframe,
            "risk_level": strategy.risk_level,
            "generation": strategy.generation,
            "parent": strategy.parent_strategy,
            "dna_keys": list(strategy.dna.keys()),
            
            # Financial metrics
            "initial_sol": strategy.initial_sol,
            "current_sol": strategy.current_sol,
            "invested_sol": strategy.get_invested_sol(),
            "pnl_sol": strategy.total_pnl_sol,
            "pnl_usd": strategy.total_pnl_usd,
            "pnl_percentage": (strategy.total_pnl_sol / strategy.initial_sol * 100) if strategy.initial_sol > 0 else 0,
            
            # Performance metrics
            "total_trades": strategy.get_total_trades(),
            "open_positions": strategy.get_open_positions(),
            "win_count": strategy.win_count,
            "loss_count": strategy.loss_count,
            "win_rate": strategy.get_win_rate(),
            "performance_score": strategy.get_performance_score(),
            
            # Active positions
            "positions": [
                {
                    "symbol": t.symbol,
                    "entry_price": t.entry_price,
                    "amount_sol": t.amount_sol,
                    "entry_time": t.entry_time.isoformat() if t.entry_time else None,
                    "status": t.status
                }
                for t in strategy.trades if t.status == "open"
            ],
            
            # Recent closed trades
            "recent_trades": [
                {
                    "symbol": t.symbol,
                    "pnl_sol": t.pnl_sol,
                    "pnl_pct": t.pnl_pct,
                    "exit_time": t.exit_time.isoformat() if t.exit_time else None,
                }
                for t in strategy.trades 
                if t.status == "closed" 
                and t.exit_time 
                and (datetime.now() - t.exit_time).days < 1  # Last 24h
            ][-5:]  # Last 5 trades
        }
    
    def _calculate_leaderboard(self, strategies: List) -> List[Dict]:
        """Calculate strategy rankings"""
        ranked = sorted(strategies, key=lambda s: s.total_pnl_sol, reverse=True)
        
        return [
            {
                "rank": i + 1,
                "id": s.id,
                "name": s.name,
                "pnl_sol": s.total_pnl_sol,
                "pnl_usd": s.total_pnl_usd,
                "win_rate": s.get_win_rate(),
                "trades": s.get_total_trades(),
                "risk_level": s.risk_level,
                "status": "ACTIVE" if not any(s.generation > 0 for s in strategies) else ("SURVIVOR" if i < 6 else "ELIMINATED"),
                "generation": s.generation,
            }
            for i, s in enumerate(ranked)
        ]
    
    def _get_todays_trades(self, strategies: List) -> List[Dict]:
        """Get all trades from today"""
        today = datetime.now().date()
        today_trades = []
        
        for strategy in strategies:
            for trade in strategy.trades:
                if trade.entry_time and trade.entry_time.date() == today:
                    today_trades.append({
                        "strategy": strategy.name,
                        "symbol": trade.symbol,
                        "type": "ENTRY",
                        "amount_sol": trade.amount_sol,
                        "time": trade.entry_time.isoformat(),
                    })
                if trade.exit_time and trade.exit_time.date() == today:
                    today_trades.append({
                        "strategy": strategy.name,
                        "symbol": trade.symbol,
                        "type": "EXIT",
                        "pnl_sol": trade.pnl_sol,
                        "pnl_pct": trade.pnl_pct,
                        "time": trade.exit_time.isoformat(),
                    })
        
        # Sort by time
        today_trades.sort(key=lambda x: x.get("time", ""), reverse=True)
        return today_trades[:20]  # Last 20
    
    def _get_all_holdings(self, strategies: List) -> Dict:
        """Get aggregate holdings across all strategies"""
        holdings = {}
        
        for strategy in strategies:
            for trade in strategy.trades:
                if trade.status == "open":
                    if trade.symbol not in holdings:
                        holdings[trade.symbol] = {
                            "symbol": trade.symbol,
                            "total_sol_invested": 0,
                            "strategies": [],
                            "entry_prices": [],
                        }
                    holdings[trade.symbol]["total_sol_invested"] += trade.amount_sol
                    holdings[trade.symbol]["strategies"].append(strategy.name)
                    holdings[trade.symbol]["entry_prices"].append(trade.entry_price)
        
        # Add average entry price
        for symbol, data in holdings.items():
            data["avg_entry_price"] = sum(data["entry_prices"]) / len(data["entry_prices"])
        
        return holdings
    
    def _append_history(self, data: Dict):
        """Append to history file"""
        history = []
        if self.history_file.exists():
            with open(self.history_file) as f:
                try:
                    history = json.load(f)
                except:
                    history = []
        
        history.append(data)
        
        # Keep last 1000 entries
        history = history[-1000:]
        
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def generate_html_dashboard(self) -> str:
        """Generate HTML dashboard"""
        current_file = self.data_dir / "current_dashboard.json"
        if not current_file.exists():
            return "<h1>No data yet</h1>"
        
        with open(current_file) as f:
            data = json.load(f)
        
        summary = data.get('summary', {})
        strategies = data.get('strategies', [])
        leaderboard = data.get('leaderboard', [])
        holdings = data.get('holdings', {})
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Genetic Trading Dashboard</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #0a0a0f; color: #e0e0e0; padding: 20px; }}
        .header {{ text-align: center; margin-bottom: 30px; padding: 20px; background: linear-gradient(135deg, #1a1a2e, #16213e); border-radius: 10px; }}
        .header h1 {{ color: #00ff88; font-size: 2.5em; margin-bottom: 10px; }}
        .header .subtitle {{ color: #888; }}
        .header .timestamp {{ color: #66ccff; margin-top: 10px; }}
        
        .summary-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 30px; }}
        .summary-card {{ background: #151528; padding: 20px; border-radius: 10px; border-left: 4px solid #00ff88; }}
        .summary-card.warning {{ border-color: #ffaa00; }}
        .summary-card.danger {{ border-color: #ff4444; }}
        .summary-card h3 {{ color: #888; font-size: 0.9em; margin-bottom: 10px; text-transform: uppercase; }}
        .summary-card .value {{ font-size: 1.8em; font-weight: bold; }}
        .summary-card .value.positive {{ color: #00ff88; }}
        .summary-card .value.negative {{ color: #ff4444; }}
        
        .grid-2 {{ display: grid; grid-template-columns: 2fr 1fr; gap: 20px; margin-bottom: 30px; }}
        .panel {{ background: #151528; border-radius: 10px; padding: 20px; }}
        .panel h2 {{ color: #00ff88; margin-bottom: 15px; border-bottom: 1px solid #333; padding-bottom: 10px; }}
        
        table {{ width: 100%; border-collapse: collapse; }}
        th {{ text-align: left; padding: 12px; color: #888; font-size: 0.85em; text-transform: uppercase; }}
        td {{ padding: 12px; border-bottom: 1px solid #333; }}
        tr:hover {{ background: #1a1a35; }}
        .rank {{ font-weight: bold; color: #00ff88; }}
        .eliminated {{ opacity: 0.5; text-decoration: line-through; }}
        .rank-1 {{ color: gold; }}
        .rank-2 {{ color: silver; }}
        .rank-3 {{ color: #cd7f32; }}
        
        .strategy-card {{ background: #1a1a2e; padding: 15px; margin-bottom: 10px; border-radius: 8px; border-left: 3px solid #00ff88; }}
        .strategy-card.neutral {{ border-color: #888; }}
        .strategy-card.negative {{ border-color: #ff4444; }}
        .strategy-header {{ display: flex; justify-content: space-between; margin-bottom: 10px; }}
        .strategy-name {{ font-weight: bold; color: #fff; }}
        .strategy-stats {{ display: flex; gap: 20px; color: #888; font-size: 0.9em; }}
        
        .holdings-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 15px; }}
        .holding-card {{ background: #1a1a2e; padding: 15px; border-radius: 8px; }}
        .holding-card h4 {{ color: #00ff88; margin-bottom: 10px; }}
        .holding-detail {{ display: flex; justify-content: space-between; margin: 5px 0; color: #aaa; }}
        .holding-detail span:first-child {{ color: #888; }}
        
        .badge {{ display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 0.75em; text-transform: uppercase; }}
        .badge-buy {{ background: #00ff88; color: #000; }}
        .badge-sell {{ background: #ff4444; color: #fff; }}
        .badge-hold {{ background: #888; color: #fff; }}
        .badge-high {{ background: #ff4444; color: #fff; }}
        .badge-med {{ background: #ffaa00; color: #000; }}
        .badge-low {{ background: #00ff88; color: #000; }}
        
        .trade-list {{ max-height: 400px; overflow-y: auto; }}
        .trade-item {{ display: flex; justify-content: space-between; padding: 10px; 
                       border-bottom: 1px solid #333; font-size: 0.9em; }}
        .trade-profit {{ color: #00ff88; }}
        .trade-loss {{ color: #ff4444; }}
        
        ::-webkit-scrollbar {{ width: 8px; }}
        ::-webkit-scrollbar-track {{ background: #151528; }}
        ::-webkit-scrollbar-thumb {{ background: #333; border-radius: 4px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: #444; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🧬 Genetic Trading System</h1>
        <p class="subtitle">10 Strategies Competing • 4 Eliminated Weekly • Evolution Active</p>
        <p class="timestamp">Last Updated: {data.get('timestamp', 'N/A')}</p>
    </div>
    
    <div class="summary-grid">
        <div class="summary-card">
            <h3>Total P&L</h3>
            <div class="value {'positive' if summary.get('total_pnl_sol', 0) >= 0 else 'negative'}">
                {summary.get('total_pnl_sol', 0):+.4f} SOL
            </div>
        </div>
        <div class="summary-card">
            <h3>USD Value</h3>
            <div class="value {'positive' if summary.get('total_pnl_usd', 0) >= 0 else 'negative'}">
                ${summary.get('total_pnl_usd', 0):+.2f}
            </div>
        </div>
        <div class="summary-card">
            <h3>Win Rate</h3>
            <div class="value">{summary.get('win_rate', 0):.1f}%</div>
        </div>
        <div class="summary-card">
            <h3>Active/Total Trades</h3>
            <div class="value">{summary.get('open_positions', 0)} / {summary.get('total_trades', 0)}</div>
        </div>
        
        <div class="summary-card">
            <h3>Total Capital</h3>
            <div class="value">{summary.get('total_capital_sol', 0):.2f} SOL</div>
        </div>
        
        <div class="summary-card">
            <h3>Active Strategies</h3>
            <div class="value">{summary.get('active_strategies', 0)}</div>
        </div>
        
        <div class="summary-card">
            <h3>Evolution Gen</h3>
            <div class="value">{summary.get('evolution_generation', 0)}</div>
        </div>
        
        <div class="summary-card {'warning' if summary.get('pnl_percentage', 0) < 0 else ''}">
            <h3>Portfolio Return</h3>
            <div class="value {'positive' if summary.get('pnl_percentage', 0) >= 0 else 'negative'}">
                {summary.get('pnl_percentage', 0):+.2f}%
            </div>
        </div>
    </div>
    
    <div class="grid-2">
        <div class="panel">
            <h2>🏆 Tournament Leaderboard</h2>
            <table>
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Strategy</th>
                        <th>P&L (SOL)</th>
                        <th>Win Rate</th>
                        <th>Trades</th>
                        <th>Risk</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        for entry in leaderboard:
            rank_class = f"rank-{entry['rank']}" if entry['rank'] <= 3 else ""
            eliminated = "eliminated" if entry.get('status') == "ELIMINATED" else ""
            risk_badge = f"badge-{entry['risk_level'][:3]}" if entry.get('risk_level') else ""
            
            html += f"""
                    <tr class="{eliminated}">
                        <td class="rank {rank_class}">#{entry['rank']}</td>
                        <td>{entry['name']}</td>
                        <td class="{'positive' if entry['pnl_sol'] >= 0 else 'negative'}">
                            {entry['pnl_sol']:+.4f}
                        </td>
                        <td>{entry['win_rate']:.1f}%</td>
                        <td>{entry['trades']}</td>
                        <td><span class="badge {risk_badge}">{entry.get('risk_level', 'N/A')}</span></td>
                        <td>{entry.get('status', 'ACTIVE')}</td>
                    </tr>
"""
        
        html += """
                </tbody>
            </table>
        </div>
        
        <div class="panel">
            <h2>💰 Today's Activity</h2>
            <div class="trade-list">
"""
        
        trades_today = data.get('trades_today', [])
        if trades_today:
            for trade in trades_today[:10]:
                trade_class = "trade-profit" if trade.get('pnl_sol', 0) > 0 else "trade-loss" if trade.get('pnl_sol', 0) < 0 else ""
                pnl_str = f"{trade.get('pnl_sol', 0):+.4f} SOL" if 'pnl_sol' in trade else f"{trade.get('amount_sol', 0):.4f} SOL"
                html += f"""
                <div class="trade-item {trade_class}">
                    <span>{trade.get('strategy', 'Unknown')} - {trade.get('symbol', '?')} ({trade.get('type', '')})</span>
                    <span>{pnl_str}</span>
                </div>
"""
        else:
            html += "<p style='color: #888; text-align: center; padding: 20px;'>No trades today</p>"
        
        html += """
            </div>
        </div>
    </div>
    
    <div class="panel" style="margin-bottom: 30px;">
        <h2>📊 Strategy Details</h2>
        <div class="strategy-list">
"""
        
        for s in strategies:
            pnl_class = "positive" if s.get('pnl_sol', 0) >= 0 else "negative"
            card_class = "" if s.get('pnl_sol', 0) >= 0 else "negative"
            
            html += f"""
            <div class="strategy-card {card_class}">
                <div class="strategy-header">
                    <div>
                        <span class="strategy-name">#{s['id']} {s['name']}</span>
                        <span style="color: #888; margin-left: 10px;">{s.get('timeframe', '?')} | Gen {s.get('generation', 0)}</span>
                    </div>
                    <div style="color: {'#00ff88' if s.get('pnl_sol', 0) >= 0 else '#ff4444'}; font-weight: bold;">
                        {s.get('pnl_sol', 0):+.4f} SOL
                    </div>
                </div>
                
                <div class="strategy-stats">
                    <span>💵 Available: {s.get('current_sol', 0):.4f} SOL</span>
                    <span>💼 Invested: {s.get('invested_sol', 0):.4f} SOL</span>
                    <span>🎯 Win Rate: {s.get('win_rate', 0):.1f}%</span>
                    <span>📈 Trades: {s.get('total_trades', 0)} ({s.get('open_positions', 0)} open)</span>
                </div>
                
                {'<div style="margin-top: 10px; color: #66ccff;">🔬 DNA: ' + ', '.join(s.get('dna_keys', [])[:6]) + '</div>' if s.get('dna_keys') else ''}
                
                {'''
                <div style="margin-top: 10px;">
                    <strong style="color: #888;">Open Positions:</strong>
                    <div style="display: flex; gap: 15px; margin-top: 5px;">
                        ''' + ''.join([f'<span style="background: #252540; padding: 5px 10px; border-radius: 4px;">{pos["symbol"]} ({pos["amount_sol"]:.3f} SOL)</span>' for pos in s.get('positions', [])]) + '''
                    </div>
                </div>
                ''' if s.get('positions') else ''}
            </div>
"""
        
        html += f"""
        </div>
    </div>
    
    <div class="panel">
        <h2>💼 Current Holdings</h2>
        <div class="holdings-grid">
"""
        
        if holdings:
            for symbol, holding in holdings.items():
                html += f"""
            <div class="holding-card">
                <h4>{symbol}</h4>
                <div class="holding-detail">
                    <span>Total Invested:</span>
                    <span>{holding.get('total_sol_invested', 0):.4f} SOL</span>
                </div>
                <div class="holding-detail">
                    <span>Strategies:</span>
                    <span>{len(holding.get('strategies', []))}</span>
                </div>
                <div class="holding-detail">
                    <span>Avg Entry:</span>
                    <span>${holding.get('avg_entry_price', 0):.8f}</span>
                </div>
            </div>
"""
        else:
            html += "<p style='color: #888; grid-column: 1 / -1; text-align: center;'>No active positions</p>"
        
        html += """
        </div>
    </div>
    
    <script>
        // Auto-refresh every 60 seconds
        setTimeout(() => {
            location.reload();
        }, 60000);
    </script>
</body>
</html>
"""
        
        return html
    
    def save_html(self):
        """Generate and save HTML dashboard"""
        html = self.generate_html_dashboard()
        output_path = self.data_dir / "dashboard.html"
        with open(output_path, 'w') as f:
            f.write(html)
        return output_path

if __name__ == "__main__":
    # Test
    from strategies import get_all_strategies
    
    dashboard = TradingDashboard()
    strategies = get_all_strategies()
    
    # Simulate some activity
    dashboard.update(strategies, cycle_number=1)
    path = dashboard.save_html()
    print(f"Dashboard saved to: {path}")
