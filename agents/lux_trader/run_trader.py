#!/usr/bin/env python3
"""
LuxTrader Runner v1.0
Main entry point - runs paper trades from AOE signals.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add paths
sys.path.insert(0, '/home/skux/.openclaw/workspace/aoe_v2')
sys.path.insert(0, '/home/skux/.openclaw/workspace/agents/lux_trader')

from lux_trader import LuxTrader
from learning_engine import LearningEngine

# Import AOE scanner for price data
try:
    from scanner_birdeye import BirdeyeScanner
    HAS_BIRDEYE = True
except:
    HAS_BIRDEYE = False


class LuxTraderRunner:
    """Runner that connects AOE signals to LuxTrader"""
    
    def __init__(self):
        self.trader = LuxTrader()
        self.data_dir = Path("/home/skux/.openclaw/workspace/agents/lux_trader")
        self.aoe_queue_file = Path("/home/skux/.openclaw/workspace/memory/aoe_queue.json")
        
        if HAS_BIRDEYE:
            self.scanner = BirdeyeScanner()
        else:
            self.scanner = None
    
    def run_cycle(self):
        """Run one complete trading cycle"""
        print("=" * 70)
        print("🔥 LUXTRADER PAPER TRADING CYCLE")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # 1. Check and close existing positions
        print("\n📊 Step 1: Checking open positions...")
        self._check_exits()
        
        # 2. Look for new signals
        print("\n📡 Step 2: Scanning for new opportunities...")
        signals = self._get_signals()
        
        # 3. Execute paper trades
        if signals:
            print(f"\n🎯 Step 3: Found {len(signals)} signals ≥75")
            self._execute_trades(signals)
        else:
            print("\n⏭️  Step 3: No signals ≥75, skipping")
        
        # 4. Learn and evolve
        print("\n🧠 Step 4: Running learning engine...")
        self._learn()
        
        # 5. Show status
        print("\n📈 Final Status:")
        self.trader.print_status()
        
        print("=" * 70)
        print("✅ Cycle Complete")
        print("=" * 70)
    
    def _check_exits(self):
        """Check all positions for exit conditions"""
        if not self.trader.portfolio:
            print("  No open positions")
            return
        
        # Get current prices (mock for now - would use real API)
        print(f"  Checking {len(self.trader.portfolio)} positions...")
        
        # TODO: Get real prices from Birdeye
        price_data = {}
        for trade in self.trader.portfolio:
            # Mock price data for demo
            price_data[trade.token_address] = trade.entry_price * 1.05  # +5%
        
        self.trader.check_exits(price_data)
    
    def _get_signals(self) -> list:
        """Get high-score tokens from AOE queue"""
        if not self.aoe_queue_file.exists():
            return []
        
        try:
            with open(self.aoe_queue_file) as f:
                queue = json.load(f)
            
            opportunities = queue.get('opportunities', [])
            
            # Filter to score ≥75 and not already in portfolio
            in_portfolio = {t.token_address for t in self.trader.portfolio}
            
            signals = [
                {
                    'symbol': o['symbol'],
                    'address': o['address'],
                    'score': o['score'],
                    # Would fetch real price here
                    'price': 0.0001  # Placeholder
                }
                for o in opportunities
                if o.get('score', 0) >= 75 and o['address'] not in in_portfolio
            ]
            
            return signals
        except Exception as e:
            print(f"  Error reading queue: {e}")
            return []
    
    def _execute_trades(self, signals: list):
        """Execute paper trades for signals"""
        executed = 0
        
        for signal in signals:
            if len(self.trader.portfolio) >= self.trader.strategy.max_positions:
                print(f"  Max positions reached, skipping {signal['symbol']}")
                break
            
            trade = self.trader.execute_paper_trade(signal)
            if trade:
                executed += 1
        
        print(f"  Executed {executed} paper trade(s)")
    
    def _learn(self):
        """Run learning and evolution"""
        if len(self.trader.trades) < 3:
            print(f"  Need 3+ trades for learning, have {len(self.trader.trades)}")
            return
        
        engine = LearningEngine(self.data_dir)
        analysis = engine.analyze()
        
        if 'error' not in analysis:
            engine.evolve_strategy(analysis)


def quick_test():
    """Test the system with mock trades"""
    print("\n🧪 LUXTRADER QUICK TEST\n")
    
    trader = LuxTrader()
    
    # Simulate trades
    test_tokens = [
        {'symbol': 'MOON', 'address': 'ADDR1', 'price': 0.001, 'score': 82},
        {'symbol': 'PUMP', 'address': 'ADDR2', 'price': 0.0005, 'score': 78},
    ]
    
    for token in test_tokens:
        trade = trader.execute_paper_trade(token)
        if trade:
            print(f"✅ Paper trade #{trade.id} created for {token['symbol']}")
    
    print("\n📊 Current Performance:")
    trader.print_status()
    
    print("\n💾 Data saved to:")
    print(f"  {trader.data_dir}")


def main():
    """Main entry"""
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        quick_test()
    else:
        runner = LuxTraderRunner()
        runner.run_cycle()


if __name__ == "__main__":
    main()
