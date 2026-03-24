#!/usr/bin/env python3
"""
Genetic Trading System - LIVE MODE Runner
Uses real DexScreener data with token diversity
"""

import asyncio
import sys
import os
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import copy

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from strategies import get_all_strategies, Strategy, Trade, create_random_strategy, mutate_dna
from engine_fixed import GeneticEngine, DataFeed

DATA_DIR = Path("/home/skux/.openclaw/workspace/genetic_trader")
STATE_FILE = DATA_DIR / "system_state.json"
DASHBOARD_FILE = DATA_DIR / "current_dashboard.json"

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

def save_state(strategies, cycle_number):
    """Save current system state"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    state = {
        "cycle_number": cycle_number,
        "last_update": datetime.now().isoformat(),
        "strategies": [],
    }
    
    for s in strategies:
        state["strategies"].append({
            "id": s.id,
            "name": s.name,
            "pnl_sol": s.total_pnl_sol,
            "pnl_usd": s.total_pnl_usd,
            "current_sol": s.current_sol,
            "win_count": s.win_count,
            "loss_count": s.loss_count,
            "generation": s.generation,
            "trades": [
                {
                    "token": t.token,
                    "symbol": t.symbol,
                    "entry_price": t.entry_price,
                    "entry_time": t.entry_time.isoformat() if t.entry_time else None,
                    "exit_price": t.exit_price,
                    "exit_time": t.exit_time.isoformat() if t.exit_time else None,
                    "pnl_sol": t.pnl_sol,
                    "pnl_pct": t.pnl_pct,
                    "amount_sol": t.amount_sol,
                    "status": t.status,
                }
                for t in s.trades
            ]
        })
    
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)
    
    print(f"💾 Saved state to {STATE_FILE}")

def save_dashboard(strategies, cycle_number, tokens_available, recent_actions):
    """Save dashboard data"""
    current_sol_totals = [s.current_sol for s in strategies]
    total_sol = sum(current_sol_totals)
    initial_sol = len(strategies) * 1.2
    
    # Build holdings
    holdings = {}
    for s in strategies:
        for t in s.trades:
            if t.status == 'open':
                if t.symbol not in holdings:
                    holdings[t.symbol] = {
                        "symbol": t.symbol,
                        "total_sol_invested": 0,
                        "strategies": [],
                        "entry_prices": []
                    }
                holdings[t.symbol]["strategies"].append(s.name)
                holdings[t.symbol]["total_sol_invested"] += t.amount_sol
                holdings[t.symbol]["entry_prices"].append(t.entry_price)
    
    # Calculate avg entry for each
    for sym, data in holdings.items():
        if data["entry_prices"]:
            data["avg_entry_price"] = sum(data["entry_prices"]) / len(data["entry_prices"])
    
    dashboard = {
        "timestamp": datetime.now().isoformat(),
        "cycle_number": cycle_number,
        "mode": "LIVE",
        "tokens_available": tokens_available,
        "summary": {
            "total_strategies": len(strategies),
            "total_capital_sol": round(total_sol, 3),
            "total_capital_usd": total_sol * 150,
            "initial_capital_sol": initial_sol,
            "total_pnl_sol": round(total_sol - initial_sol, 6),
            "total_pnl_usd": round((total_sol - initial_sol) * 150, 2),
            "pnl_percentage": round((total_sol - initial_sol) / initial_sol * 100, 2),
            "total_trades": sum(len(s.trades) for s in strategies),
            "open_positions": sum(1 for s in strategies for t in s.trades if t.status == 'open'),
            "closed_trades": sum(1 for s in strategies for t in s.trades if t.status == 'closed'),
            "win_rate": sum(s.win_count for s in strategies) / max(1, sum(s.win_count + s.loss_count for s in strategies)) * 100,
            "active_strategies": len([s for s in strategies if s.active]),
            "evolution_generation": max(s.generation for s in strategies)
        },
        "strategies": [
            {
                "id": s.id,
                "name": s.name,
                "description": s.description,
                "timeframe": s.timeframe,
                "risk_level": s.risk_level,
                "generation": s.generation,
                "initial_sol": 1.2,
                "current_sol": round(s.current_sol, 5),
                "invested_sol": round(s.current_sol - 1.2 + sum(t.amount_sol for t in s.trades if t.status == 'open'), 5),
                "pnl_sol": round(s.total_pnl_sol, 6),
                "pnl_usd": round(s.total_pnl_usd, 2),
                "pnl_percentage": round(s.total_pnl_sol / 1.2 * 100, 2),
                "total_trades": len(s.trades),
                "open_positions": len([t for t in s.trades if t.status == 'open']),
                "win_count": s.win_count,
                "loss_count": s.loss_count,
                "win_rate": s.win_count / max(1, len(s.trades)) * 100,
            }
            for s in strategies
        ],
        "holdings": holdings,
        "recent_actions": recent_actions
    }
    
    with open(DASHBOARD_FILE, 'w') as f:
        json.dump(dashboard, f, indent=2)
    
    return dashboard

async def run_live_cycle():
    """Execute one live trading cycle with real tokens"""
    print("\n" + "="*70)
    print(f"🚀 GENETIC TRADING SYSTEM - LIVE CYCLE")
    print(f"   Using REAL DexScreener data")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Load previous state
    state = load_state()
    cycle_number = state.get('cycle_number', 0) + 1
    
    # Initialize strategies
    strategies = get_all_strategies()
    
    # Restore previous state
    if state.get('strategies'):
        for saved in state['strategies']:
            for s in strategies:
                if s.id == saved.get('id'):
                    s.total_pnl_sol = saved.get('pnl_sol', 0)
                    s.total_pnl_usd = saved.get('pnl_usd', 0)
                    s.current_sol = saved.get('current_sol', 1.2)
                    s.win_count = saved.get('win_count', 0)
                    s.loss_count = saved.get('loss_count', 0)
                    s.generation = saved.get('generation', 0)
                    
                    # Restore trades
                    for t_data in saved.get('trades', []):
                        trade = Trade(
                            token=t_data.get('token', ''),
                            symbol=t_data.get('symbol', ''),
                            entry_price=t_data.get('entry_price', 0),
                            entry_time=datetime.fromisoformat(t_data['entry_time']) if t_data.get('entry_time') else datetime.now(),
                            amount_sol=t_data.get('amount_sol', 0.1),
                            status=t_data.get('status', 'open')
                        )
                        if t_data.get('exit_time'):
                            trade.exit_time = datetime.fromisoformat(t_data['exit_time'])
                            trade.exit_price = t_data.get('exit_price')
                            trade.pnl_sol = t_data.get('pnl_sol', 0)
                            trade.pnl_pct = t_data.get('pnl_pct', 0)
                        s.trades.append(trade)
    
    print(f"\n📊 Configuration:")
    print(f"   Strategies: {len(strategies)}")
    print(f"   Capital per Strategy: 1.2 SOL (~$180 USD)")
    print(f"   Total Capital: {len(strategies) * 1.2:.2f} SOL (~${len(strategies) * 180} USD)")
    print(f"   Current Cycle: #{cycle_number}")
    
    # Initialize data feed
    data_feed = DataFeed()
    recent_actions = []
    tokens_available = 0
    
    try:
        await data_feed.__aenter__()
        
        print(f"\n📡 Fetching LIVE tokens from DexScreener...")
        tokens = await data_feed.get_trending_tokens(limit=100)
        tokens_available = len(tokens)
        
        if tokens_available < 10:
            print("   ⚠️  Insufficient tokens, aborting cycle")
            return
        
        print(f"\n🎯 TRADING ACTIONS")
        print("-" * 70)
        
        # Process each active strategy
        for strategy in strategies:
            if not strategy.active:
                continue
            
            # Close old positions (time-based exit)
            for trade in strategy.trades:
                if trade.status == 'open':
                    held_hours = (datetime.now() - trade.entry_time).total_seconds() / 3600
                    
                    # Time-stop after 6 hours
                    if held_hours >= 6:
                        print(f"   🟢 {strategy.name}: EXIT {trade.symbol} (Time stop: {held_hours:.1f}h)")
                        trade.status = 'closed'
                        trade.exit_time = datetime.now()
                        trade.exit_price = trade.entry_price  # Breakeven for now
                        trade.pnl_sol = 0
                        trade.pnl_pct = 0
                        strategy.current_sol += trade.amount_sol
                        recent_actions.append({
                            "strategy": strategy.name,
                            "symbol": trade.symbol,
                            "type": "EXIT",
                            "reason": f"Time stop: {held_hours:.1f}h",
                            "time": datetime.now().isoformat()
                        })
            
            # Check if strategy can enter new position
            open_count = len([t for t in strategy.trades if t.status == 'open'])
            if open_count >= 1:
                continue  # Already in position
            
            # Select token based on strategy type
            from engine_fixed import StrategyExecutor
            executor = StrategyExecutor(strategy, data_feed)
            selected_token = executor.select_token_for_strategy(tokens)
            
            if not selected_token:
                print(f"   ⏸️  {strategy.name}: No suitable token found")
                continue
            
            # Calculate indicators
            indicators = data_feed.calculate_indicators(selected_token)
            
            # Determine entry
            symbol = selected_token['symbol']
            should_enter = False
            reason = ""
            
            if strategy.id == 1:  # Momentum Surge
                if indicators['is_pumping'] and selected_token.get('volume_24h', 0) > 50000:
                    should_enter = True
                    reason = f"Momentum: +{indicators['price_momentum_1h']:.1f}%"
            
            elif strategy.id == 2:  # Mean Reversion Dip
                change = indicators['price_momentum_1h']
                if -15 < change < -8:
                    should_enter = True
                    reason = f"Dip: {change:.1f}%"
            
            elif strategy.id == 3:  # Whale Shadow
                if selected_token.get('volume_24h', 0) > 100000:
                    should_enter = True
                    reason = "High volume"
            
            elif strategy.id == 4:  # RSI Oversold
                if indicators['oversold']:
                    should_enter = True
                    reason = f"RSI: {indicators['rsi_14']:.0f}"
            
            elif strategy.id == 5:  # Breakout Hunter
                if 5 < indicators['price_momentum_1h'] < 20:
                    should_enter = True
                    reason = f"Breakout: +{indicators['price_momentum_1h']:.1f}%"
            
            elif strategy.id == 6:  # Social Sentiment
                if selected_token.get('is_new') or indicators['is_pumping']:
                    should_enter = True
                    reason = "New/Meme"
            
            elif strategy.id == 7:  # Liquidity Surfing
                if selected_token.get('volume_24h', 0) > 50000:
                    should_enter = True
                    reason = "Liquidity wave"
            
            elif strategy.id == 8:  # EMA Cross
                if indicators['is_established']:
                    should_enter = True
                    reason = "Established coin"
            
            elif strategy.id == 9:  # Range Trader
                if abs(indicators['price_momentum_1h']) < 5:
                    should_enter = True
                    reason = "Range bound"
            
            elif strategy.id == 10:  # News Arbitrage
                if selected_token.get('volume_24h', 0) > 100000:
                    should_enter = True
                    reason = "Volume spike"
            
            if should_enter:
                # Enter position
                position_size = 0.12  # 10% of capital per trade
                
                if strategy.current_sol >= position_size:
                    trade = Trade(
                        token=selected_token['address'],
                        symbol=symbol,
                        entry_price=selected_token['price'],
                        entry_time=datetime.now(),
                        amount_sol=position_size,
                        status='open'
                    )
                    strategy.trades.append(trade)
                    strategy.current_sol -= position_size
                    
                    age_days = selected_token.get('age_days', 'unknown')
                    categories = selected_token.get('category_str', 'N/A')
                    
                    print(f"   🔴 {strategy.name}: ENTRY {symbol}")
                    print(f"      Price: ${selected_token['price']:.8f}")
                    print(f"      MCap: ${selected_token['market_cap']:,.0f}")
                    print(f"      Age: {age_days} days")
                    print(f"      Volume 24h: ${selected_token['volume_24h']:,.0f}")
                    print(f"      Categories: {categories}")
                    print(f"      Reason: {reason}")
                    print()
                    
                    recent_actions.append({
                        "strategy": strategy.name,
                        "symbol": symbol,
                        "type": "ENTRY",
                        "amount_sol": position_size,
                        "time": datetime.now().isoformat()
                    })
                else:
                    print(f"   ⚠️  {strategy.name}: Insufficient capital")
            else:
                print(f"   ⏸️  {strategy.name}: No signal")
    
    finally:
        await data_feed.__aexit__(None, None, None)
    
    # Save state and dashboard
    save_state(strategies, cycle_number)
    dashboard = save_dashboard(strategies, cycle_number, tokens_available, recent_actions)
    
    # Print summary
    print("=" * 70)
    print("📊 CYCLE SUMMARY")
    print("=" * 70)
    print(f"\n💰 Financial:")
    print(f"   Total P&L: {dashboard['summary']['total_pnl_sol']:+.4f} SOL")
    print(f"   Win Rate: {dashboard['summary']['win_rate']:.1f}%")
    print(f"   Total Trades: {dashboard['summary']['total_trades']}")
    print(f"   Open Positions: {dashboard['summary']['open_positions']}")
    print(f"   Tokens Available: {tokens_available}")
    
    if recent_actions:
        print(f"\n🔄 Actions This Cycle:")
        for action in recent_actions[:10]:
            emoji = "🔴" if action['type'] == 'ENTRY' else "🟢"
            print(f"   {emoji} {action['strategy']}: {action['type']} {action['symbol']}")
    
    print(f"\n" + "=" * 70)
    print(f"⏭️  Next cycle: Run again for new data")
    print(f"📊 Dashboard: {DASHBOARD_FILE}")
    print("=" * 70)

def print_status():
    """Print current system status"""
    print("\n" + "=" * 70)
    print("🧬 GENETIC TRADING SYSTEM - LIVE Status")
    print("=" * 70)
    
    state = load_state()
    
    print(f"\n📊 System State:")
    print(f"   Current Cycle: #{state.get('cycle_number', 0)}")
    print(f"   Started: {state.get('start_date', 'N/A')}")
    print(f"   Last Update: {state.get('last_update', 'Never')}")
    print(f"   Mode: LIVE (DexScreener real data)")
    
    if state.get('strategies'):
        print(f"\n📈 Strategies (sorted by P&L):")
        strategies = sorted(state['strategies'], key=lambda x: x.get('pnl_sol', 0), reverse=True)
        total_pnl = sum(s.get('pnl_sol', 0) for s in strategies)
        
        for i, s in enumerate(strategies, 1):
            status = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            pnl = s.get('pnl_sol', 0)
            open_pos = len([t for t in s.get('trades', []) if t.get('status') == 'open'])
            print(f"   {status} {s['name']}: {pnl:+.4f} SOL ({open_pos} open)")
        
        print(f"\n💰 Total P&L: {total_pnl:+.4f} SOL")
    else:
        print("\n⚠️  No trading data yet. Run a cycle first.")
    
    if DASHBOARD_FILE.exists():
        print(f"\n📊 Dashboard: {DASHBOARD_FILE}")
    
    print("\n" + "=" * 70)

async def main():
    parser = argparse.ArgumentParser(description="Genetic Trading System - LIVE MODE")
    parser.add_argument('command', choices=['run', 'status', 'reset'],
                       help='Command to execute')
    
    args = parser.parse_args()
    
    if args.command == 'run':
        await run_live_cycle()
    elif args.command == 'status':
        print_status()
    elif args.command == 'reset':
        print("⚠️  Resetting system...")
        if STATE_FILE.exists():
            STATE_FILE.unlink()
        if DASHBOARD_FILE.exists():
            DASHBOARD_FILE.unlink()
        print("✅ System reset. Ready for new LIVE cycles.")

if __name__ == "__main__":
    asyncio.run(main())
