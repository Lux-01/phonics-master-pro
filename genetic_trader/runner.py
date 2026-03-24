#!/usr/bin/env python3
"""
Genetic Trading System - Main Runner
Executes trading cycles and manages evolution
"""

import asyncio
import sys
import os
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from strategies import get_all_strategies, Strategy, Trade
from engine_fixed import GeneticEngine, DataFeed, StrategyExecutor
from dashboard import TradingDashboard

DATA_DIR = Path("/home/skux/.openclaw/workspace/genetic_trader")
STATE_FILE = DATA_DIR / "system_state.json"

def load_state():
    """Load system state or initialize"""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            data = json.load(f)
            print(f"📂 Loaded system state (Cycle #{data.get('cycle_number', 0)})")
            return data
    return {
        "cycle_number": 0,
        "last_evolution": None,
        "strategies": [],
        "start_date": datetime.now().isoformat(),
    }

def save_state(engine: GeneticEngine, cycle_number: int):
    """Save current system state including trades"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    state = {
        "cycle_number": cycle_number,
        "last_evolution": None,
        "last_update": datetime.now().isoformat(),
        "strategies": [],
    }
    
    for s in engine.strategies:
        strategy_data = {
            "id": s.id,
            "name": s.name,
            "pnl_sol": s.total_pnl_sol,
            "pnl_usd": s.total_pnl_usd,
            "current_sol": s.current_sol,
            "win_count": s.win_count,
            "loss_count": s.loss_count,
            "generation": s.generation,
            "risk_level": s.risk_level,
            "open_positions": s.get_open_positions(),
            "total_trades": s.get_total_trades(),
            "trades": [
                {
                    "symbol": t.symbol,
                    "token": t.token,
                    "entry_price": t.entry_price,
                    "entry_time": t.entry_time.isoformat() if t.entry_time else None,
                    "amount_sol": t.amount_sol,
                    "exit_price": t.exit_price,
                    "exit_time": t.exit_time.isoformat() if t.exit_time else None,
                    "pnl_sol": t.pnl_sol,
                    "pnl_pct": t.pnl_pct,
                    "status": t.status
                }
                for t in s.trades
            ]
        }
        state["strategies"].append(strategy_data)
    
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

async def run_daily_cycle():
    """Execute one daily trading cycle"""
    print("\n" + "="*70)
    print(f"🚀 GENETIC TRADING SYSTEM - Daily Cycle")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Load previous state
    state = load_state()
    cycle_number = state.get('cycle_number', 0) + 1
    
    # Initialize engine
    engine = GeneticEngine()
    dashboard = TradingDashboard()
    
    print(f"\n📊 Configuration:")
    print(f"   Strategies: {len(engine.strategies)}")
    print(f"   Capital per Strategy: 1.2 SOL (~$100 USD)")
    print(f"   Total Capital: {len(engine.strategies) * 1.2:.2f} SOL (~${len(engine.strategies) * 100} USD)")
    print(f"   Current Cycle: #{cycle_number}")
    
    # Restore previous PnL data and trades if exists
    if state.get('strategies'):
        for saved in state['strategies']:
            for s in engine.strategies:
                if s.id == saved.get('id'):
                    s.total_pnl_sol = saved.get('pnl_sol', 0)
                    s.total_pnl_usd = saved.get('pnl_usd', 0)
                    s.current_sol = saved.get('current_sol', 1.2)
                    s.win_count = saved.get('win_count', 0)
                    s.loss_count = saved.get('loss_count', 0)
                    s.generation = saved.get('generation', 0)
                    
                    # Restore trades
                    if saved.get('trades'):
                        s.trades = []
                        for t_data in saved['trades']:
                            trade = Trade(
                                token=t_data.get('token', ''),
                                symbol=t_data.get('symbol', ''),
                                entry_price=t_data.get('entry_price', 0),
                                entry_time=datetime.fromisoformat(t_data['entry_time']) if t_data.get('entry_time') else datetime.now(),
                                amount_sol=t_data.get('amount_sol', 0),
                                status=t_data.get('status', 'open')
                            )
                            trade.exit_price = t_data.get('exit_price')
                            trade.exit_time = datetime.fromisoformat(t_data['exit_time']) if t_data.get('exit_time') else None
                            trade.pnl_sol = t_data.get('pnl_sol')
                            trade.pnl_pct = t_data.get('pnl_pct')
                            s.trades.append(trade)
    
    # Run trading cycle
    await engine.run_cycle()
    
    # Update dashboard
    dashboard.update(engine.strategies, cycle_number)
    dashboard_path = dashboard.save_html()
    
    # Save state
    save_state(engine, cycle_number)
    
    # Print summary
    print(f"\n" + "="*70)
    print("📊 CYCLE SUMMARY")
    print("="*70)
    
    summary = dashboard._calculate_summary(engine.strategies)
    print(f"\n💰 Financial:")
    print(f"   Total P&L: {summary['total_pnl_sol']:+.4f} SOL (${summary['total_pnl_usd']:+.2f})")
    print(f"   Win Rate: {summary['win_rate']:.1f}%")
    print(f"   Total Trades: {summary['total_trades']}")
    print(f"   Open Positions: {summary['open_positions']}")
    
    print(f"\n📈 Top Performers:")
    leaderboard = dashboard._calculate_leaderboard(engine.strategies)
    for i, entry in enumerate(leaderboard[:3], 1):
        print(f"   {i}. {entry['name']}: {entry['pnl_sol']:+.4f} SOL")
    
    print(f"\n" + "="*70)
    print(f"⏭️  Next cycle tomorrow at same time")
    print(f"📊 Dashboard: {dashboard_path}")
    print("="*70)

def run_weekly_evolution():
    """Execute weekly evolution (eliminate bottom 4, breed top 3)"""
    print("\n" + "="*70)
    print(f"🧬 WEEKLY EVOLUTION")
    print(f"   {datetime.now().strftime('%Y-%m-%d')}")
    print("="*70)
    
    engine = GeneticEngine()
    
    # Load state
    state = load_state()
    if state.get('strategies'):
        # Restore previous PnL
        for saved in state['strategies']:
            for s in engine.strategies:
                if s.id == saved.get('id'):
                    s.total_pnl_sol = saved.get('pnl_sol', 0)
                    s.total_pnl_usd = saved.get('pnl_usd', 0)
    
    # Run evolution
    engine.weekly_evolution()
    
    # Save updated state
    save_state(engine, state.get('cycle_number', 0))
    
    print("\n✅ Evolution complete! Next evolution in 7 days.")
    print("="*70)

def print_status():
    """Print current system status"""
    print("\n" + "="*70)
    print("🧬 GENETIC TRADING SYSTEM - Status")
    print("="*70)
    
    state = load_state()
    
    print(f"\n📊 System State:")
    print(f"   Current Cycle: #{state.get('cycle_number', 0)}")
    print(f"   Started: {state.get('start_date', 'N/A')}")
    print(f"   Last Update: {state.get('last_update', 'Never')}")
    print(f"   Last Evolution: {state.get('last_evolution', 'Never')}")
    
    if state.get('strategies'):
        print(f"\n📈 Strategies:")
        strategies = sorted(state['strategies'], key=lambda x: x.get('pnl_sol', 0), reverse=True)
        total_pnl = sum(s.get('pnl_sol', 0) for s in strategies)
        
        for i, s in enumerate(strategies, 1):
            status = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            pnl = s.get('pnl_sol', 0)
            print(f"   {status} {s['name']}: {pnl:+.4f} SOL")
        
        print(f"\n💰 Total P&L: {total_pnl:+.4f} SOL")
    else:
        print("\n⚠️  No trading data yet. Run a cycle first.")
    
    # Check if dashboard exists
    dashboard_path = DATA_DIR / "dashboard.html"
    if dashboard_path.exists():
        print(f"\n📊 Dashboard: {dashboard_path}")
        print("   Open in browser to view real-time data")
    
    print("\n" + "="*70)

def reset_system():
    """Reset system to initial state"""
    print("⚠️  Resetting Genetic Trading System...")
    
    # Backup existing data
    if DATA_DIR.exists():
        backup_dir = DATA_DIR / "backup" / datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        for file in DATA_DIR.glob("*.json"):
            if file.is_file():
                import shutil
                shutil.copy(file, backup_dir / file.name)
        print(f"   📦 Backed up to: {backup_dir}")
    
    # Remove state file
    if STATE_FILE.exists():
        STATE_FILE.unlink()
    
    print("✅ System reset complete!")
    print("   Run 'python3 runner.py run' to start fresh")

def setup_cron():
    """Setup cron jobs for daily and weekly execution"""
    import subprocess
    
    script_path = Path(__file__).absolute()
    
    # Daily at 9 AM
    daily_cron = f"0 9 * * * cd /home/skux/.openclaw/workspace/genetic_trader && /usr/bin/python3 {script_path} run >> /home/skux/.openclaw/workspace/genetic_trader/cron.log 2>&1"
    
    # Weekly on Sunday at 10 AM (for evolution)
    weekly_cron = f"0 10 * * 0 cd /home/skux/.openclaw/workspace/genetic_trader && /usr/bin/python3 {script_path} evolve >> /home/skux/.openclaw/workspace/genetic_trader/cron_evolve.log 2>&1"
    
    print("📅 Proposed Cron Jobs:")
    print(f"   Daily: {daily_cron}")
    print(f"   Weekly: {weekly_cron}")
    print("\nTo install:")
    print(f"   crontab -e")
    print(f"   # Add these lines:")
    print(f"   {daily_cron}")
    print(f"   {weekly_cron}")

def main():
    parser = argparse.ArgumentParser(description="Genetic Trading System")
    parser.add_argument('command', choices=['run', 'evolve', 'status', 'reset', 'setup-cron', 'demo'],
                       help='Command to execute')
    
    args = parser.parse_args()
    
    if args.command == 'run':
        asyncio.run(run_daily_cycle())
    elif args.command == 'evolve':
        run_weekly_evolution()
    elif args.command == 'status':
        print_status()
    elif args.command == 'reset':
        reset_system()
    elif args.command == 'setup-cron':
        setup_cron()
    elif args.command == 'demo':
        from engine import demo
        asyncio.run(demo())

if __name__ == "__main__":
    main()
