#!/usr/bin/env python3
"""
LuxTrader Immediate Run - Lower threshold for learning
Trades on tokens ≥60 for immediate market exposure
"""

import sys
import json
import glob
import re
from pathlib import Path
from datetime import datetime

sys.path.insert(0, '/home/skux/.openclaw/workspace/agents/lux_trader')

from lux_trader import LuxTrader
from learning_engine import LearningEngine

class ImmediateRunner:
    """Runner that trades immediately on lower threshold for learning"""
    
    def __init__(self, min_score=60):  # Lowered from 75
        self.trader = LuxTrader()
        self.min_score = min_score
        self.data_dir = Path("/home/skux/.openclaw/workspace/agents/lux_trader")
    
    def run_immediate(self):
        """Run trading cycle immediately"""
        print("=" * 70)
        print("🔥 LUXTRADER IMMEDIATE RUN")
        print(f"Threshold: ≥{self.min_score} | Time: {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 70)
        
        # 1. Check existing positions
        print("\n📊 Step 1: Checking open positions...")
        self._check_exits()
        
        # 2. Get signals from latest AOE scan
        print(f"\n📡 Step 2: Scanning for tokens ≥{self.min_score}...")
        signals = self._get_signals_from_latest_scan()
        
        # 3. Execute trades
        if signals:
            print(f"\n🎯 Found {len(signals)} tokens ≥{self.min_score}!")
            self._execute_trades(signals)
        else:
            print(f"\n⏭️  No tokens ≥{self.min_score} in latest scan")
        
        # 4. Learn
        print("\n🧠 Step 3: Running learning...")
        self._learn()
        
        # 5. Status
        print("\n📈 Final Status:")
        self.trader.print_status()
        
        print("=" * 70)
    
    def _get_signals_from_latest_scan(self):
        """Parse latest AOE scan log for high scores"""
        # Find latest scan log
        logs = sorted(glob.glob("/tmp/aoe_scan_*.log"), reverse=True)
        if not logs:
            print("  No AOE scan logs found")
            return []
        
        latest = logs[0]
        print(f"  Reading: {Path(latest).name}")
        
        signals = []
        try:
            with open(latest) as f:
                content = f.read()
            
            # Parse score breakdown section
            in_scores = False
            for line in content.split('\n'):
                if "DETAILED SCORE BREAKDOWN" in line:
                    in_scores = True
                    continue
                if "SCORE TRENDS" in line:
                    break
                
                if in_scores and len(line.strip()) > 10:
                    # Parse format: SYMBOL Score Pot Prob Speed Fit Alpha Risk Status MC
                    # Example: JOY        61     75    85    90    75    45    50    📊 MONITOR  $302K
                    parts = line.split()
                    if len(parts) >= 9 and parts[0].isupper():
                        try:
                            symbol = parts[0]
                            score = int(parts[1])
                            
                            if score >= self.min_score:
                                # Look for address in the log
                                address = self._find_address(symbol, content)
                                
                                signals.append({
                                    'symbol': symbol,
                                    'address': address or f"UNKNOWN_{symbol}",
                                    'score': score,
                                    'price': 0.0001  # Will fetch real price
                                })
                                print(f"  ✓ {symbol}: Score {score}")
                        except:
                            pass
        except Exception as e:
            print(f"  Error reading log: {e}")
        
        return signals
    
    def _find_address(self, symbol, content):
        """Try to find token address in log"""
        # Look for symbol mention near addresses
        return None  # Simplify for now
    
    def _check_exits(self):
        """Check positions for exits"""
        if not self.trader.portfolio:
            print("  No open positions")
            return
        
        # Simulate price movements
        price_data = {}
        for trade in self.trader.portfolio:
            # Random movement for paper trading
            import random
            move = random.uniform(0.9, 1.15)  # -10% to +15%
            price_data[trade.token_address] = trade.entry_price * move
        
        self.trader.check_exits(price_data)
    
    def _execute_trades(self, signals):
        """Execute paper trades"""
        executed = 0
        for signal in signals:
            if len(self.trader.portfolio) >= self.trader.strategy.max_positions:
                print(f"  Max positions reached")
                break
            
            # Check duplicate
            if any(t.token_address == signal['address'] for t in self.trader.portfolio):
                print(f"  Skipping {signal['symbol']} - already in portfolio")
                continue
            
            trade = self.trader.execute_paper_trade(signal)
            if trade:
                executed += 1
        
        print(f"\n✅ Executed {executed} paper trade(s)")
    
    def _learn(self):
        """Run learning engine"""
        if len([t for t in self.trader.trades if not t.is_open]) < 3:
            print(f"  Need 3+ completed trades, have {len(self.trader.trades)}")
            return
        
        engine = LearningEngine(self.data_dir)
        analysis = engine.analyze()
        
        if 'error' not in analysis:
            print(f"\n  📊 Win Rate: {analysis['stats']['win_rate']:.1f}%")
            print(f"  💰 Total P&L: {analysis['stats']['total_pnl']:+.1f}%")
            
            engine.evolve_strategy(analysis)


def main():
    print("\n" + "="*70)
    print("  LUXTRADER IMMEDIATE MODE")
    print("  Lower threshold for immediate learning")
    print("="*70 + "\n")
    
    runner = ImmediateRunner(min_score=60)  # Lower threshold
    runner.run_immediate()


if __name__ == "__main__":
    main()
