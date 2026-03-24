#!/usr/bin/env python3
"""
Genetic Trading System - LIVE CYCLE v2 with Real P&L Tracking
Fetches current prices on exit to calculate actual P&L
"""

import asyncio
import sys
import os
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import aiohttp
import copy

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from strategies import get_all_strategies, Strategy, Trade

try:
    from engine_fixed import GeneticEngine, DataFeed
except ImportError:
    from engine import GeneticEngine
    print("Warning: Using old engine, no real token categorization")

class PriceTracker:
    """Fetches current token prices for P&L calculation"""
    
    def __init__(self):
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_current_price(self, token_address: str, symbol: str) -> float:
        """Fetch current price for a token from DexScreener"""
        try:
            # Search for the token
            url = f"https://api.dexscreener.com/latest/dex/tokens/{token_address}"
            async with self.session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    pairs = data.get('pairs', [])
                    if pairs:
                        # Get best pair (highest liquidity)
                        best_pair = max(pairs, key=lambda p: p.get('liquidity', {}).get('usd', 0) or 0)
                        price = float(best_pair.get('priceUsd', 0))
                        if price > 0:
                            return price
            
            # Fallback: search by symbol
            url = f"https://api.dexscreener.com/latest/dex/search?q={symbol}"
            async with self.session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    for pair in data.get('pairs', []):
                        if pair.get('baseToken', {}).get('address') == token_address:
                            price = float(pair.get('priceUsd', 0))
                            if price > 0:
                                return price
                        # Or match symbol
                        if pair.get('baseToken', {}).get('symbol', '').upper() == symbol.upper():
                            price = float(pair.get('priceUsd', 0))
                            if price > 0:
                                return price
        except Exception as e:
            print(f"      ⚠️  Price fetch failed for {symbol}: {e}")
        
        # Return 0 if couldn't fetch
        return 0.0
    
    async def calculate_exit_pnl(self, trade: Trade) -> tuple[float, float]:
        """Calculate P&L for an open trade"""
        current_price = await self.get_current_price(trade.token, trade.symbol)
        
        if current_price == 0:
            # Can't fetch price - exit at breakeven
            print(f"      ⚠️  No current price for {trade.symbol}, exiting at breakeven")
            return 0.0, 0.0
        
        # Calculate P&L percentage
        pnl_pct = ((current_price - trade.entry_price) / trade.entry_price) * 100
        
        # Calculate P&L in SOL
        # Simplified: assume USD terms, but we'll display as SOL for consistency
        # Real system would use SOL/USD conversion
        pnl_sol = trade.amount_sol * (pnl_pct / 100)
        
        return pnl_sol, pnl_pct


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
    
    # Calculate actual P&L
    total_pnl = sum(s.total_pnl_sol for s in strategies)
    
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
    
    # Build closed trades list
    closed_trades = []
    for s in strategies:
        for t in s.trades:
            if t.status == 'closed' and t.exit_time:
                closed_trades.append({
                    "strategy": s.name,
                    "symbol": t.symbol,
                    "entry_price": t.entry_price,
                    "exit_price": t.exit_price,
                    "pnl_sol": t.pnl_sol,
                    "pnl_pct": t.pnl_pct,
                    "held_hours": (t.exit_time - t.entry_time).total_seconds() / 3600
                })
    
    # Sort by exit time (most recent first)
    closed_trades.sort(key=lambda x: x.get("exit_time", datetime.min), reverse=True)
    
    dashboard = {
        "timestamp": datetime.now().isoformat(),
        "cycle_number": cycle_number,
        "mode": "LIVE_v2",
        "tokens_available": tokens_available,
        "summary": {
            "total_strategies": len(strategies),
            "total_capital_sol": round(total_sol, 3),
            "total_capital_usd": round(total_sol * 150, 2),
            "initial_capital_sol": initial_sol,
            "total_pnl_sol": round(total_pnl, 6),
            "total_pnl_usd": round(total_pnl * 150, 2),
            "pnl_percentage": round(total_pnl / initial_sol * 100, 2),
            "total_trades": sum(len(s.trades) for s in strategies),
            "open_positions": sum(1 for s in strategies for t in s.trades if t.status == 'open'),
            "closed_trades": sum(1 for s in strategies for t in s.trades if t.status == 'closed'),
            "win_rate": sum(s.win_count for s in strategies) / max(1, sum(s.win_count + s.loss_count for s in strategies)) * 100,
            "active_strategies": len([s for s in strategies if s.active]),
            "evolution_generation": max((s.generation for s in strategies), default=0)
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
                "invested_sol": round(sum(t.amount_sol for t in s.trades if t.status == 'open'), 5),
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
        "closed_trade_history": closed_trades[:20],  # Last 20 trades
        "recent_actions": recent_actions
    }
    
    with open(DASHBOARD_FILE, 'w') as f:
        json.dump(dashboard, f, indent=2)
    
    return dashboard

async def run_live_cycle_v2():
    """Execute one live trading cycle with REAL P&L tracking"""
    print("\n" + "="*70)
    print(f"🚀 GENETIC TRADING SYSTEM - LIVE CYCLE v2 (Real P&L)")
    print(f"   Using REAL DexScreener data + Live price tracking")
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
    
    # Initialize data feed and price tracker
    data_feed = DataFeed()
    price_tracker = PriceTracker()
    recent_actions = []
    tokens_available = 0
    
    try:
        await data_feed.__aenter__()
        await price_tracker.__aenter__()
        
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
            
            # EXITS: Check for time stops and calculate REAL P&L
            for trade in strategy.trades:
                if trade.status == 'open':
                    held_hours = (datetime.now() - trade.entry_time).total_seconds() / 3600
                    
                    # Time-stop after 6 hours
                    if held_hours >= 6:
                        print(f"\n   🟢 {strategy.name}: EXIT {trade.symbol} (Time stop: {held_hours:.1f}h)")
                        
                        # Fetch current price and calculate REAL P&L
                        pnl_sol, pnl_pct = await price_tracker.calculate_exit_pnl(trade)
                        
                        trade.status = 'closed'
                        trade.exit_time = datetime.now()
                        
                        if pnl_sol != 0:
                            # Real price fetched
                            current_price = trade.entry_price * (1 + pnl_pct / 100)
                            trade.exit_price = current_price
                            trade.pnl_sol = pnl_sol
                            trade.pnl_pct = pnl_pct
                            strategy.current_sol += trade.amount_sol + pnl_sol
                            
                            pnl_emoji = "📈" if pnl_sol > 0 else "📉"
                            print(f"      {pnl_emoji} P&L: {pnl_sol:+.6f} SOL ({pnl_pct:+.2f}%)")
                            print(f"      Entry: ${trade.entry_price:.8f} → Current: ${current_price:.8f}")
                            
                            if pnl_sol > 0:
                                strategy.win_count += 1
                            else:
                                strategy.loss_count += 1
                        else:
                            # No price data - breakeven
                            trade.exit_price = trade.entry_price
                            trade.pnl_sol = 0
                            trade.pnl_pct = 0
                            strategy.current_sol += trade.amount_sol
                            print(f"      ➡️  P&L: $0 (breakeven - no price data)")
                        
                        strategy.total_pnl_sol += trade.pnl_sol
                        strategy.total_pnl_usd += trade.pnl_sol * 150  # Approx $150/SOL
                        
                        recent_actions.append({
                            "strategy": strategy.name,
                            "symbol": trade.symbol,
                            "type": "EXIT",
                            "pnl_sol": trade.pnl_sol,
                            "pnl_pct": trade.pnl_pct,
                            "reason": f"Time stop: {held_hours:.1f}h",
                            "time": datetime.now().isoformat()
                        })
            
            # Check if strategy can enter new position
            open_count = len([t for t in strategy.trades if t.status == 'open'])
            if open_count >= 1:
                continue  # Already in position
            
            # ENTRY logic (same as before)
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
                    
                    print(f"\n   🔴 {strategy.name}: ENTRY {symbol}")
                    print(f"      Price: ${selected_token['price']:.8f}")
                    print(f"      MCap: ${selected_token['market_cap']:,.0f}")
                    print(f"      Age: {age_days} days")
                    print(f"      Volume 24h: ${selected_token['volume_24h']:,.0f}")
                    print(f"      Categories: {categories}")
                    print(f"      Reason: {reason}")
                    
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
        await price_tracker.__aexit__(None, None, None)
        await data_feed.__aexit__(None, None, None)
    
    # Save state and dashboard
    save_state(strategies, cycle_number)
    dashboard = save_dashboard(strategies, cycle_number, tokens_available, recent_actions)
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 CYCLE SUMMARY (v2 - Real P&L)")
    print("=" * 70)
    print(f"\n💰 Financial:")
    print(f"   Total P&L: {dashboard['summary']['total_pnl_sol']:+.6f} SOL")
    print(f"   P&L %: {dashboard['summary']['pnl_percentage']:+.2f}%")
    print(f"   Win Rate: {dashboard['summary']['win_rate']:.1f}%")
    print(f"   Total Trades: {dashboard['summary']['total_trades']}")
    print(f"   Open Positions: {dashboard['summary']['open_positions']}")
    print(f"   Closed Trades: {dashboard['summary']['closed_trades']}")
    print(f"   Tokens Available: {tokens_available}")
    
    # Show strategy rankings
    print(f"\n🏆 Strategy Rankings (by P&L):")
    sorted_strategies = sorted(strategies, key=lambda x: x.total_pnl_sol, reverse=True)
    for i, s in enumerate(sorted_strategies[:5], 1):
        pnl_str = f"{s.total_pnl_sol:+.4f}"
        emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "  "
        print(f"   {emoji} {s.name}: {pnl_str} SOL")
    
    if recent_actions:
        print(f"\n🔄 Actions This Cycle:")
        for action in recent_actions[:15]:
            if action['type'] == 'EXIT' and 'pnl_sol' in action:
                emoji = "🟢" if action['pnl_sol'] >= 0 else "🔴"
                pnl_str = f" ({action['pnl_sol']:+.4f} SOL)"
                print(f"   {emoji} {action['strategy']}: EXIT {action['symbol']}{pnl_str}")
            elif action['type'] == 'ENTRY':
                print(f"   🔴 {action['strategy']}: ENTRY {action['symbol']}")
    
    print(f"\n" + "=" * 70)
    print(f"⏭️  Next cycle: Run again for new data")
    print(f"📊 Dashboard: {DASHBOARD_FILE}")
    print("=" * 70)

def print_status():
    """Print current system status"""
    print("\n" + "=" * 70)
    print("🧬 GENETIC TRADING SYSTEM - LIVE Status v2 (Real P&L)")
    print("=" * 70)
    
    state = load_state()
    
    print(f"\n📊 System State:")
    print(f"   Current Cycle: #{state.get('cycle_number', 0)}")
    print(f"   Started: {state.get('start_date', 'N/A')}")
    print(f"   Last Update: {state.get('last_update', 'Never')}")
    print(f"   Mode: LIVE v2 (Real P&L tracking)")
    
    if state.get('strategies'):
        print(f"\n📈 Strategy Leaderboard:")
        strategies = sorted(state['strategies'], key=lambda x: x.get('pnl_sol', 0), reverse=True)
        total_pnl = sum(s.get('pnl_sol', 0) for s in strategies)
        total_trades = sum(len(s.get('trades', [])) for s in strategies)
        total_wins = sum(s.get('win_count', 0) for s in strategies)
        total_losses = sum(s.get('loss_count', 0) for s in strategies)
        win_rate = total_wins / max(1, total_wins + total_losses) * 100
        
        print(f"\n💰 Total P&L: {total_pnl:+.4f} SOL")
        print(f"📈 Win Rate: {win_rate:.1f}% ({total_wins}/{total_wins + total_losses})")
        print(f"🔄 Total Trades: {total_trades}")
        print()
        
        for i, s in enumerate(strategies, 1):
            status = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            pnl = s.get('pnl_sol', 0)
            open_pos = len([t for t in s.get('trades', []) if t.get('status') == 'open'])
            print(f"   {status} {s['name']}: {pnl:+.4f} SOL ({open_pos} open)")
    else:
        print("\n⚠️  No trading data yet. Run a cycle first.")
    
    if DASHBOARD_FILE.exists():
        print(f"\n📊 Dashboard: {DASHBOARD_FILE}")
    
    print("\n" + "=" * 70)

async def main():
    parser = argparse.ArgumentParser(description="Genetic Trading System - LIVE v2 (Real P&L)")
    parser.add_argument('command', choices=['run', 'status', 'reset'],
                       help='Command to execute')
    
    args = parser.parse_args()
    
    if args.command == 'run':
        await run_live_cycle_v2()
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
