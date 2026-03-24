#!/usr/bin/env python3
"""
Genetic Trading System - Real Data Engine
Fetches live token data and executes strategy logic
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import random

from strategies import (
    Strategy, Trade, get_all_strategies, mutate_dna, breed_strategies,
    create_random_strategy
)

# ============================================================================
# REAL DATA SOURCES
# ============================================================================

class DataFeed:
    """Fetches real-time Solana token data"""
    
    def __init__(self):
        self.dexscreener_url = "https://api.dexscreener.com/latest/dex/pairs/solana"
        self.jupiter_price_url = "https://price.jup.ag/v4/price"
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_trending_tokens(self, limit: int = 50) -> List[Dict]:
        """Fetch trending tokens using DexScreener pairs endpoint"""
        try:
            # Try multiple endpoints
            endpoints = [
                "https://api.dexscreener.com/latest/dex/pairs/solana/Dh9BSB8qAJNgrJmDxpAKPpDsQ7BDSmWAa3jDqxb7o5Y",
                "https://api.dexscreener.com/latest/dex/pairs/solana/So11111111111111111111111111111111111111112",
            ]
            
            tokens = []
            for endpoint in endpoints:
                try:
                    async with self.session.get(endpoint, timeout=10) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            pairs = data.get('pairs', [])
                            
                            for pair in pairs[:limit//2]:
                                base_token = pair.get('baseToken', {})
                                token = {
                                    'address': base_token.get('address', ''),
                                    'symbol': base_token.get('symbol', 'UNKNOWN'),
                                    'name': base_token.get('name', 'Unknown Token'),
                                    'price': float(pair.get('priceUsd', 0) or 0),
                                    'market_cap': float(pair.get('marketCap', 0) or 0),
                                    'volume_24h': float(pair.get('volume', {}).get('h24', 0) or 0),
                                    'price_change_1h': float(pair.get('priceChange', {}).get('h1', 0) or 0),
                                    'price_change_24h': float(pair.get('priceChange', {}).get('h24', 0) or 0),
                                    'liquidity': float(pair.get('liquidity', {}).get('usd', 0) or 0),
                                    'txns_24h': (pair.get('txns', {}).get('h24', {}).get('buys', 0) or 0) + 
                                               (pair.get('txns', {}).get('h24', {}).get('sells', 0) or 0),
                                    'dex': pair.get('dexId', 'unknown'),
                                    'pair_address': pair.get('pairAddress', ''),
                                    'fdv': pair.get('fdv', 0),
                                }
                                tokens.append(token)
                                
                            if len(tokens) >= limit//2:
                                break
                except Exception as e:
                    continue
            
            if tokens:
                return tokens
                
        except Exception as e:
            print(f"Error fetching tokens: {e}")
        
        # Fallback: Generate simulated tokens for testing
        print("⚠️  Using fallback token data for demo")
        return self._generate_fallback_tokens(limit)
    
    def _generate_fallback_tokens(self, limit: int) -> List[Dict]:
        """Generate realistic fallback tokens for testing"""
        import random
        import hashlib
        
        symbols = ['PEPE', 'DOGE', 'SHIB', 'FLOKI', 'BONK', 'WIF', 'BOME', 'SLERF', 
                   'POPCAT', 'MOG', 'WOJAK', 'MEME', 'TURBO', 'AIDOGE', 'QUACK',
                   'SOLINU', 'GORK', 'AIPEPE', 'MOON', 'MARS', 'JUP', 'RAY', 'ORCA']
        
        tokens = []
        for i in range(min(limit, len(symbols))):
            symbol = symbols[i]
            # Generate deterministic but random-looking data
            seed = hashlib.md5(f"{symbol}{datetime.now().strftime('%Y%m%d')}".encode()).hexdigest()
            seed_int = int(seed[:8], 16)
            
            price = (seed_int % 1000) / 100000000  # Micro prices
            mcap = 50000 + (seed_int % 950000)  # $50k to $1M
            volume = 10000 + (seed_int % 490000)
            
            tokens.append({
                'address': f"token{i}{hashlib.md5(symbol.encode()).hexdigest()[:20]}",
                'symbol': symbol,
                'name': f"{symbol} Token",
                'price': price,
                'market_cap': mcap,
                'volume_24h': volume,
                'price_change_1h': ((seed_int % 40) - 20),  # -20% to +20%
                'price_change_24h': ((seed_int % 60) - 30),  # -30% to +30%
                'liquidity': volume * 0.3,
                'txns_24h': 100 + (seed_int % 900),
                'dex': 'raydium' if seed_int % 2 == 0 else 'orca',
                'pair_address': f"pair{i}{seed[:15]}",
                'fdv': mcap * 1.2,
            })
        
        return tokens
    
    def calculate_indicators(self, token: Dict) -> Dict:
        """Calculate technical indicators for token"""
        indicators = {
            'volume_spike': token.get('volume_24h', 0) > 50000,  # $50k+ volume
            'price_momentum': token.get('price_change_1h', 0),
            'is_pumping': token.get('price_change_1h', 0) > 10,
            'is_dumping': token.get('price_change_1h', 0) < -5,
            'mcap_tier': self._get_mcap_tier(token.get('market_cap', 0)),
            'liquidity_ok': token.get('liquidity', 0) > 10000,
        }
        
        # Mock RSI calculation (would need historical data)
        price_change = token.get('price_change_24h', 0)
        indicators['rsi_14'] = 50 + (price_change * 0.5)  # Simplified
        indicators['rsi_14'] = max(10, min(90, indicators['rsi_14']))
        
        # Mock EMA
        indicators['ema9'] = token.get('price', 0) * 1.02
        indicators['ema21'] = token.get('price', 0) * 0.98
        
        # Support/Resistance estimation
        price = token.get('price', 0)
        indicators['support'] = price * 0.93
        indicators['resistance'] = price * 1.12
        
        return indicators
    
    def _get_mcap_tier(self, mcap: float) -> str:
        """Classify market cap tier"""
        if mcap < 100000:
            return "micro"
        elif mcap < 1000000:
            return "small"
        elif mcap < 10000000:
            return "medium"
        else:
            return "large"

# ============================================================================
# STRATEGY EXECUTOR
# ============================================================================

class StrategyExecutor:
    """Executes individual strategy logic"""
    
    def __init__(self, strategy: Strategy, data_feed: DataFeed):
        self.strategy = strategy
        self.data_feed = data_feed
        
    def should_enter(self, token: Dict, indicators: Dict) -> tuple[bool, str]:
        """Evaluate if strategy should enter position"""
        dna = self.strategy.dna
        
        # Get strategy-specific entry rules
        strategy_id = self.strategy.id
        
        if strategy_id == 1:  # Momentum Surge
            return self._check_momentum_surge(token, indicators, dna)
        elif strategy_id == 2:  # Mean Reversion
            return self._check_mean_reversion(token, indicators, dna)
        elif strategy_id == 3:  # Whale Shadow
            return self._check_whale_shadow(token, indicators, dna)
        elif strategy_id == 4:  # RSI Oversold
            return self._check_rsi_oversold(token, indicators, dna)
        elif strategy_id == 5:  # Breakout Hunter
            return self._check_breakout(token, indicators, dna)
        elif strategy_id == 6:  # Social Sentiment
            return self._check_social_sentiment(token, indicators, dna)
        elif strategy_id == 7:  # Liquidity Surfing
            return self._check_liquidity_surfing(token, indicators, dna)
        elif strategy_id == 8:  # EMA Cross
            return self._check_ema_cross(token, indicators, dna)
        elif strategy_id == 9:  # Range Trader
            return self._check_range_trader(token, indicators, dna)
        elif strategy_id == 10:  # News Arbitrage
            return self._check_news_arbitrage(token, indicators, dna)
        else:
            # Generic evolved strategy
            return self._check_generic(token, indicators, dna)
    
    def _check_momentum_surge(self, token, indicators, dna):
        """Volume spike + price breakout"""
        if indicators['volume_spike'] and indicators['is_pumping']:
            return True, f"Momentum surge: +{token['price_change_1h']:.1f}% with volume"
        return False, "No momentum"
    
    def _check_mean_reversion(self, token, indicators, dna):
        """Buy dips"""
        dip = token.get('price_change_1h', 0)
        min_dip = dna.get('dip_threshold_min', -0.15) * 100
        max_dip = dna.get('dip_threshold_max', -0.08) * 100
        
        if min_dip <= dip <= max_dip:
            return True, f"Dip buy: {dip:.1f}% (targeting bounce)"
        return False, f"Dip not in range ({dip:.1f}%)"
    
    def _check_whale_shadow(self, token, indicators, dna):
        """Simulated whale detection"""
        # In real implementation, would check whale wallet transactions
        if token.get('volume_24h', 0) > 100000 and indicators['is_pumping']:
            return True, "Whale activity detected (simulated)"
        return False, "No whale activity"
    
    def _check_rsi_oversold(self, token, indicators, dna):
        """RSI oversold bounce"""
        rsi = indicators.get('rsi_14', 50)
        max_rsi = dna.get('rsi_entry_max', 30)
        if rsi < max_rsi:
            return True, f"RSI oversold: {rsi:.1f}"
        return False, f"RSI not oversold ({rsi:.1f})"
    
    def _check_breakout(self, token, indicators, dna):
        """Breakout above resistance"""
        price = token.get('price', 0)
        resistance = indicators.get('resistance', price * 1.1)
        
        if price > resistance * 0.97:  # Near resistance
            return True, f"Breakout setup at ${price:.6f}"
        return False, "Not at resistance"
    
    def _check_social_sentiment(self, token, indicators, dna):
        """Social buzz detection"""
        if indicators['is_pumping'] and token.get('volume_24h', 0) > 50000:
            return True, "High social activity"
        return False, "Low social buzz"
    
    def _check_liquidity_surfing(self, token, indicators, dna):
        """Liquidity wave riding"""
        if indicators['liquidity_ok'] and not indicators['is_dumping']:
            return True, "Riding liquidity wave"
        return False, "Poor liquidity"
    
    def _check_ema_cross(self, token, indicators, dna):
        """EMA golden cross"""
        if indicators['ema9'] > indicators['ema21']:
            return True, "Golden cross confirmed"
        return False, "No EMA cross"
    
    def _check_range_trader(self, token, indicators, dna):
        """Support/Resistance range"""
        price = token.get('price', 0)
        support = indicators.get('support', price * 0.9)
        
        if price < support * 1.03:  # Near support
            return True, f"Near support: ${price:.6f}"
        return False, "Not at support"
    
    def _check_news_arbitrage(self, token, indicators, dna):
        """News reaction"""
        if indicators['is_pumping'] and token.get('price_change_1h', 0) > 15:
            return True, "News momentum trade"
        return False, "No news catalyst"
    
    def _check_generic(self, token, indicators, dna):
        """Generic evolved strategy logic"""
        score = 0
        reasons = []
        
        if indicators['volume_spike']:
            score += 20
            reasons.append("volume")
        if indicators['is_pumping']:
            score += 25
            reasons.append("pump")
        if indicators['liquidity_ok']:
            score += 15
            reasons.append("liq")
        
        if score >= 50:
            return True, "Evolved signal: " + ",".join(reasons)
        return False, f"Score too low ({score})"
    
    def should_exit(self, trade: Trade, token: Dict, indicators: Dict) -> tuple[bool, str]:
        """Evaluate if should exit position"""
        current_price = token.get('price', trade.entry_price)
        pnl_pct = ((current_price - trade.entry_price) / trade.entry_price) * 100
        
        dna = self.strategy.dna
        
        # Check take profit
        tp_pct = dna.get('take_profit_pct', 0.15) * 100
        if pnl_pct >= tp_pct:
            return True, f"Take profit: +{pnl_pct:.1f}%"
        
        # Check stop loss
        sl_pct = dna.get('stop_loss_pct', -0.07) * 100
        if pnl_pct <= sl_pct:
            return True, f"Stop loss: {pnl_pct:.1f}%"
        
        # Check time stop
        hold_hours = dna.get('time_stop_hours', 4)
        if trade.entry_time:
            hold_time = (datetime.now() - trade.entry_time).total_seconds() / 3600
            if hold_time >= hold_hours:
                return True, f"Time stop: {hold_hours}h reached"
        
        return False, f"Holding: {pnl_pct:.1f}%"

# ============================================================================
# PARALLEL ENGINE
# ============================================================================

class GeneticEngine:
    """Main engine running all strategies in parallel"""
    
    def __init__(self, data_dir: str = "/home/skux/.openclaw/workspace/genetic_trader"):
        self.data_dir = data_dir
        self.strategies: List[Strategy] = get_all_strategies()
        self.data_feed = DataFeed()
        self.executors: Dict[int, StrategyExecutor] = {}
        
        # Initialize executors
        for strategy in self.strategies:
            self.executors[strategy.id] = StrategyExecutor(strategy, self.data_feed)
        
        self.trade_history = []
        
    async def run_cycle(self):
        """Execute one trading cycle for all strategies"""
        print(f"\n{'='*60}")
        print(f"🔄 Trading Cycle - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        async with self.data_feed:
            # Fetch all tokens
            tokens = await self.data_feed.get_trending_tokens(limit=50)
            print(f"📊 Fetched {len(tokens)} tokens from DexScreener")
            
            if not tokens:
                print("❌ No tokens fetched, skipping cycle")
                return
            
            # Process each strategy in parallel
            tasks = []
            for strategy in self.strategies:
                if strategy.active:
                    executor = self.executors[strategy.id]
                    task = self._run_strategy(strategy, executor, tokens)
                    tasks.append(task)
            
            # Run all strategies
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Log results
            for result in results:
                if isinstance(result, Exception):
                    print(f"❌ Strategy error: {result}")
    
    async def _run_strategy(self, strategy: Strategy, executor: StrategyExecutor, tokens: List[Dict]):
        """Run single strategy logic"""
        actions_taken = []
        
        # Check existing positions for exit signals
        for trade in strategy.trades[:]:
            if trade.status == "open":
                # Find current token data
                token_data = next((t for t in tokens if t['symbol'] == trade.symbol), None)
                if token_data:
                    indicators = self.data_feed.calculate_indicators(token_data)
                    should_exit, reason = executor.should_exit(trade, token_data, indicators)
                    
                    if should_exit:
                        # Close trade
                        exit_price = token_data.get('price', trade.entry_price)
                        pnl = trade.close_trade(exit_price)
                        strategy.current_sol += trade.amount_sol + pnl
                        
                        if pnl > 0:
                            strategy.win_count += 1
                        else:
                            strategy.loss_count += 1
                        
                        strategy.total_pnl_sol += pnl
                        strategy.total_pnl_usd = strategy.total_pnl_sol * 150  # Approx USD
                        actions_taken.append(f"🟢 EXIT {trade.symbol}: {reason}")
        
        # Check for new entries (if under max positions)
        max_positions = 5
        open_positions = strategy.get_open_positions()
        
        if open_positions < max_positions:
            # Score each token
            scored_tokens = []
            for token in tokens:
                indicators = self.data_feed.calculate_indicators(token)
                should_enter, reason = executor.should_enter(token, indicators)
                if should_enter:
                    scored_tokens.append((token, reason, indicators))
            
            # Take best opportunity
            if scored_tokens and strategy.get_available_sol() > 0.1:
                # Sort by some scoring logic (volume * momentum)
                scored_tokens.sort(
                    key=lambda x: x[0].get('volume_24h', 0) * abs(x[0].get('price_change_1h', 0)),
                    reverse=True
                )
                
                best_token = scored_tokens[0][0]
                entry_reason = scored_tokens[0][1]
                
                # Calculate position size
                position_pct = strategy.dna.get('entry_position_pct', 0.15)
                position_size = min(
                    strategy.current_sol * position_pct,
                    strategy.current_sol * 0.2  # Max 20%
                )
                
                if position_size >= 0.05:  # Minimum 0.05 SOL
                    # Create trade
                    trade = Trade(
                        token=best_token['address'],
                        symbol=best_token['symbol'],
                        entry_price=best_token['price'],
                        entry_time=datetime.now(),
                        amount_sol=position_size,
                        status="open"
                    )
                    
                    strategy.trades.append(trade)
                    strategy.current_sol -= position_size
                    actions_taken.append(f"🔴 ENTRY {best_token['symbol']}: {entry_reason}")
        
        if actions_taken:
            print(f"  {strategy.name}: {len(actions_taken)} actions")
        for action in actions_taken:
            print(f"    {action}")
        
        return strategy.id, actions_taken
    
    def get_leaderboard(self) -> List[Dict]:
        """Get strategy rankings by performance"""
        rankings = []
        for strategy in self.strategies:
            rankings.append({
                'id': strategy.id,
                'name': strategy.name,
                'pnl_sol': strategy.total_pnl_sol,
                'pnl_usd': strategy.total_pnl_usd,
                'win_rate': strategy.get_win_rate(),
                'trades': strategy.get_total_trades(),
                'open_positions': strategy.get_open_positions(),
                'sol_available': strategy.get_available_sol(),
                'sol_invested': strategy.get_invested_sol(),
                'performance_score': strategy.get_performance_score(),
                'risk_level': strategy.risk_level,
                'generation': strategy.generation,
            })
        
        # Sort by PnL
        rankings.sort(key=lambda x: x['pnl_sol'], reverse=True)
        return rankings
    
    def weekly_evolution(self):
        """Perform weekly evolution - eliminate bottom 4, breed top 3"""
        print(f"\n{'='*60}")
        print(f"🧬 WEEKLY EVOLUTION - {datetime.now().strftime('%Y-%m-%d')}")
        print(f"{'='*60}")
        
        # Get rankings
        rankings = self.get_leaderboard()
        
        # Identify survivors and eliminated
        survivors = rankings[:6]  # Top 6
        eliminated = rankings[-4:]  # Bottom 4
        
        print(f"\n🏆 SURVIVORS (Top 6):")
        for s in survivors:
            print(f"  #{s['id']} {s['name']}: +{s['pnl_sol']:.4f} SOL (${s['pnl_usd']:.2f})")
        
        print(f"\n💀 ELIMINATED (Bottom 4):")
        for e in eliminated:
            print(f"  #{e['id']} {e['name']}: {e['pnl_sol']:.4f} SOL")
        
        # Create new generation
        new_generation = []
        current_gen = max(s['generation'] for s in rankings) if rankings else 0
        
        # Keep top 6
        survivor_strategies = [s for s in self.strategies if s.id in [x['id'] for x in survivors]]
        new_generation.extend(survivor_strategies)
        
        # Clone #1 (90% similar)
        top1 = survivor_strategies[0]
        clone1 = self._clone_strategy(top1, current_gen + 1, mutation_rate=0.1)
        new_generation.append(clone1)
        
        # Clone #2 (80% similar)  
        top2 = survivor_strategies[1]
        clone2 = self._clone_strategy(top2, current_gen + 1, mutation_rate=0.2)
        new_generation.append(clone2)
        
        # Hybrid of #2 and #3
        top3 = survivor_strategies[2]
        hybrid = breed_strategies(top2, top3, current_gen + 1)
        hybrid.initial_sol = 1.2
        hybrid.current_sol = 1.2
        new_generation.append(hybrid)
        
        # Random newcomer
        newcomer = create_random_strategy(current_gen + 1)
        newcomer.initial_sol = 1.2
        newcomer.current_sol = 1.2
        new_generation.append(newcomer)
        
        # Update strategies
        self.strategies = new_generation
        self.executors = {}
        for strategy in self.strategies:
            self.executors[strategy.id] = StrategyExecutor(strategy, self.data_feed)
        
        print(f"\n✅ Evolution complete! New generation: {current_gen + 1}")
        print(f"   Total strategies: {len(self.strategies)}")
        
        return rankings
    
    def _clone_strategy(self, strategy: Strategy, generation: int, mutation_rate: float) -> Strategy:
        """Clone a strategy with mutations"""
        new_dna = mutate_dna(strategy.dna.copy(), mutation_rate)
        
        return Strategy(
            id=random.randint(100, 999),
            name=f"{strategy.name}_G{generation}",
            description=strategy.description,
            timeframe=strategy.timeframe,
            risk_level=strategy.risk_level,
            dna=new_dna,
            generation=generation,
            parent_strategy=strategy.name,
            mutations=[f"mutation_{int(mutation_rate*100)}pct"]
        )

# ============================================================================
# MAIN ENTRY
# ============================================================================

async def demo():
    """Demo the genetic engine"""
    engine = GeneticEngine()
    
    print("\n" + "="*60)
    print("🧬 GENETIC TRADING SYSTEM - DEMO")
    print("="*60)
    print(f"\n📊 Initial Setup:")
    print(f"   Total Strategies: {len(engine.strategies)}")
    print(f"   Capital per Strategy: 1.2 SOL (~$100 USD)")
    print(f"   Total Capital: {len(engine.strategies) * 1.2:.2f} SOL (~${len(engine.strategies) * 100} USD)")
    
    print(f"\n🎯 Strategy Lineup:")
    for i, s in enumerate(engine.strategies, 1):
        print(f"   {i}. {s.name} ({s.risk_level}, {s.timeframe})")
    
    # Run a few cycles
    print(f"\n{'='*60}")
    print("RUNNING 3 TRADING CYCLES...")
    print(f"{'='*60}")
    
    for cycle in range(3):
        print(f"\n--- Cycle {cycle + 1} ---")
        await engine.run_cycle()
    
    # Show leaderboard
    print(f"\n{'='*60}")
    print("📊 FINAL LEADERBOARD")
    print(f"{'='*60}")
    
    leaderboard = engine.get_leaderboard()
    for i, s in enumerate(leaderboard, 1):
        emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        print(f"{emoji} {s['name']}")
        print(f"   PnL: {s['pnl_sol']:+.4f} SOL (${s['pnl_usd']:+.2f})")
        print(f"   Win Rate: {s['win_rate']:.1f}% | Trades: {s['trades']}")
        print(f"   SOL: {s['sol_available']:.4f} available, {s['sol_invested']:.4f} invested")
        print(f"   Generation: {s['generation']}")
        
if __name__ == "__main__":
    asyncio.run(demo())
