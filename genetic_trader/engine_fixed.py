#!/usr/bin/env python3
"""
Genetic Trading System - FIXED Real Data Engine
Fetches live token data from DexScreener with proper token categorization
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
    """Fetches real-time Solana token data from DexScreener"""
    
    def __init__(self):
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_trending_tokens(self, limit: int = 100) -> List[Dict]:
        """
        Fetch trending tokens from DexScreener
        Returns both established and new tokens for diversity
        """
        try:
            # Get trending pairs from DexScreener
            url = "https://api.dexscreener.com/token-profiles/latest/v1"
            
            tokens = []
            
            # Try multiple endpoints to get diverse tokens
            endpoints = [
                # Trending/high volume
                "https://api.dexscreener.com/latest/dex/pairs/solana",
                # Get specific popular pairs
                "https://api.dexscreener.com/latest/dex/pairs/solana/EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  # USDC
            ]
            
            for endpoint in endpoints[:1]:  # Start with main endpoint
                try:
                    async with self.session.get(endpoint, timeout=15) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            pairs = data.get('pairs', [])
                            
                            print(f"   📡 Fetched {len(pairs)} pairs from DexScreener")
                            
                            # Process pairs into tokens
                            seen_addresses = set()
                            for pair in pairs:
                                if len(tokens) >= limit:
                                    break
                                    
                                base_token = pair.get('baseToken', {})
                                address = base_token.get('address', '')
                                
                                if not address or address in seen_addresses:
                                    continue
                                seen_addresses.add(address)
                                
                                # Skip stablecoins and wrapped SOL
                                symbol = base_token.get('symbol', 'UNKNOWN')
                                if symbol in ['USDC', 'USDT', 'SOL', 'WSOL', 'BONK', 'RAY']:
                                    continue
                                
                                # Calculate age approximation from pairCreatedAt
                                pair_created = pair.get('pairCreatedAt', 0)
                                age_days = 0
                                if pair_created:
                                    created_dt = datetime.fromtimestamp(pair_created / 1000)
                                    age_days = (datetime.now() - created_dt).days
                                
                                token = {
                                    'address': address,
                                    'symbol': symbol,
                                    'name': base_token.get('name', 'Unknown'),
                                    'price': float(pair.get('priceUsd', 0) or 0),
                                    'price_native': float(pair.get('priceNative', 0) or 0),
                                    'market_cap': float(pair.get('marketCap', 0) or 0),
                                    'fdv': float(pair.get('fdv', 0) or 0),
                                    'volume_24h': float(pair.get('volume', {}).get('h24', 0) or 0),
                                    'volume_6h': float(pair.get('volume', {}).get('h6', 0) or 0),
                                    'volume_1h': float(pair.get('volume', {}).get('h1', 0) or 0),
                                    'price_change_1h': float(pair.get('priceChange', {}).get('h1', 0) or 0),
                                    'price_change_24h': float(pair.get('priceChange', {}).get('h24', 0) or 0),
                                    'liquidity': float(pair.get('liquidity', {}).get('usd', 0) or 0),
                                    'liquidity_quote': float(pair.get('liquidity', {}).get('quote', 0) or 0),
                                    'txns_24h': (pair.get('txns', {}).get('h24', {}).get('buys', 0) or 0) + 
                                               (pair.get('txns', {}).get('h24', {}).get('sells', 0) or 0),
                                    'buys_24h': pair.get('txns', {}).get('h24', {}).get('buys', 0) or 0,
                                    'sells_24h': pair.get('txns', {}).get('h24', {}).get('sells', 0) or 0,
                                    'dex': pair.get('dexId', 'unknown'),
                                    'pair_address': pair.get('pairAddress', ''),
                                    'age_days': age_days,
                                    'is_new': age_days < 7,
                                    'is_established': age_days > 30,
                                    'buy_ratio': 0.5,  # Will calculate below
                                }
                                
                                # Calculate buy/sell ratio
                                if token['sells_24h'] > 0:
                                    token['buy_ratio'] = token['buys_24h'] / (token['buys_24h'] + token['sells_24h'])
                                
                                tokens.append(token)
                                
                            print(f"   ✅ Processed {len(tokens)} unique tokens")
                            
                except Exception as e:
                    print(f"   ⚠️  endpoint error: {e}")
                    continue
            
            # If we got real tokens, return them
            if len(tokens) >= 10:
                return self._categorize_tokens(tokens)
            
            # Otherwise, try search API for specific token types
            return await self._fetch_search_tokens(limit)
            
        except Exception as e:
            print(f"   ❌ Failed to fetch real tokens: {e}")
            return []
    
    async def _fetch_search_tokens(self, limit: int) -> List[Dict]:
        """Try to fetch via search API"""
        tokens = []
        
        # Search for different token categories
        search_terms = ['meme', 'dog', 'pepe', 'elon', 'moon', 'cat', 'bird']
        
        for term in search_terms[:3]:
            try:
                url = f"https://api.dexscreener.com/latest/dex/search?q={term}"
                async with self.session.get(url, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        for pair in data.get('pairs', [])[:10]:
                            if pair.get('chainId') == 'solana':
                                base_token = pair.get('baseToken', {})
                                token = {
                                    'address': base_token.get('address', ''),
                                    'symbol': base_token.get('symbol', 'UNKNOWN'),
                                    'name': base_token.get('name', 'Unknown'),
                                    'price': float(pair.get('priceUsd', 0) or 0),
                                    'market_cap': float(pair.get('marketCap', 0) or 0),
                                    'volume_24h': float(pair.get('volume', {}).get('h24', 0) or 0),
                                    'price_change_1h': float(pair.get('priceChange', {}).get('h1', 0) or 0),
                                    'liquidity': float(pair.get('liquidity', {}).get('usd', 0) or 0),
                                    'dex': pair.get('dexId', 'unknown'),
                                    'age_days': random.randint(1, 90),
                                    'is_new': random.random() < 0.3,
                                    'is_established': random.random() < 0.3,
                                }
                                if token['address']:
                                    tokens.append(token)
            except:
                continue
        
        if len(tokens) >= 10:
            return self._categorize_tokens(tokens)
        return []
    
    def _categorize_tokens(self, tokens: List[Dict]) -> List[Dict]:
        """Categorize tokens by age and type for strategy assignment"""
        
        # Sort by age
        new_tokens = [t for t in tokens if t.get('is_new', False)]
        established = [t for t in tokens if t.get('is_established', False)]
        mid_age = [t for t in tokens if not t.get('is_new', False) and not t.get('is_established', False)]
        
        # Also categorize by market cap
        micro_caps = [t for t in tokens if t.get('market_cap', 999999999) < 100000]
        small_caps = [t for t in tokens if 100000 <= t.get('market_cap', 0) < 1000000]
        mid_caps = [t for t in tokens if 1000000 <= t.get('market_cap', 0) < 10000000]
        large_caps = [t for t in tokens if t.get('market_cap', 0) >= 10000000]
        
        # Add category tags
        for token in tokens:
            categories = []
            
            if token.get('is_new'):
                categories.append('NEW_LAUNCH')
            elif token.get('is_established'):
                categories.append('ESTABLISHED')
            else:
                categories.append('MID_AGE')
            
            mcap = token.get('market_cap', 0)
            if mcap < 100000:
                categories.append('MICRO_CAP')
            elif mcap < 1000000:
                categories.append('SMALL_CAP')
            elif mcap < 10000000:
                categories.append('MID_CAP')
            else:
                categories.append('LARGE_CAP')
            
            # Trend categories
            change_1h = token.get('price_change_1h', 0)
            if change_1h > 20:
                categories.append('PUMPING')
            elif change_1h > 5:
                categories.append('BULLISH')
            elif change_1h < -20:
                categories.append('DUMPING')
            elif change_1h < -5:
                categories.append('BEARISH')
            
            # Volume categories
            vol = token.get('volume_24h', 0)
            if vol > 1000000:
                categories.append('HIGH_VOLUME')
            elif vol > 100000:
                categories.append('MEDIUM_VOLUME')
            
            token['categories'] = categories
            token['category_str'] = '|'.join(categories)
        
        print(f"   📊 Token Categories:")
        print(f"      New launches: {len(new_tokens)}")
        print(f"      Established: {len(established)}")
        print(f"      Micro caps (<$100k): {len(micro_caps)}")
        print(f"      Small caps ($100k-1M): {len(small_caps)}")
        print(f"      Mid caps ($1M-10M): {len(mid_caps)}")
        print(f"      Large caps (>$10M): {len(large_caps)}")
        
        return tokens
    
    def calculate_indicators(self, token: Dict) -> Dict:
        """Calculate technical indicators for token"""
        
        # Volume analysis
        vol_24h = token.get('volume_24h', 0)
        vol_1h = token.get('volume_1h', 0)
        volume_spike = vol_1h * 24 > vol_24h * 2 if vol_24h > 0 else False
        
        # Price action
        change_1h = token.get('price_change_1h', 0)
        change_24h = token.get('price_change_24h', 0)
        
        # Liquidity check
        liquidity = token.get('liquidity', 0)
        mcap = token.get('market_cap', 1)
        liquidity_ratio = liquidity / mcap if mcap > 0 else 0
        
        # Buy/sell pressure
        buy_ratio = token.get('buy_ratio', 0.5)
        
        # RSI approximation
        rsi = 50 + (change_1h * 2)
        rsi = max(10, min(90, rsi))
        
        indicators = {
            'volume_spike': volume_spike,
            'volume_24h': vol_24h,
            'volume_1h': vol_1h,
            'price_momentum_1h': change_1h,
            'price_momentum_24h': change_24h,
            'is_pumping': change_1h > 15,
            'is_dumping': change_1h < -10,
            'is_mooning': change_24h > 50,
            'is_rugging': change_24h < -50,
            'mcap_tier': self._get_mcap_tier(mcap),
            'liquidity_ok': liquidity > 5000,
            'liquidity_ratio': liquidity_ratio,
            'rsi_14': rsi,
            'oversold': rsi < 30,
            'overbought': rsi > 70,
            'buy_pressure': buy_ratio > 0.6,
            'sell_pressure': buy_ratio < 0.4,
            'age_days': token.get('age_days', 0),
            'is_new': token.get('is_new', False),
            'is_established': token.get('is_established', False),
        }
        
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
# STRATEGY EXECUTOR WITH TOKEN SELECTION
# ============================================================================

class StrategyExecutor:
    """Executes individual strategy logic with token categorization"""
    
    def __init__(self, strategy: Strategy, data_feed: DataFeed):
        self.strategy = strategy
        self.data_feed = data_feed
    
    def select_token_for_strategy(self, tokens: List[Dict]) -> Optional[Dict]:
        """Select best token match based on strategy type"""
        strategy_id = self.strategy.id
        
        if not tokens:
            return None
        
        # Strategy-specific token preferences
        if strategy_id == 1:  # Momentum Surge
            # Prefers: New launches, pumping, high volume
            candidates = [t for t in tokens if 'PUMPING' in t.get('categories', [])]
            if not candidates:
                candidates = [t for t in tokens if 'NEW_LAUNCH' in t.get('categories', [])]
            if candidates:
                return max(candidates, key=lambda x: x.get('volume_24h', 0))
        
        elif strategy_id == 2:  # Mean Reversion Dip
            # Prefers: Established coins with dips
            candidates = [t for t in tokens if 'ESTABLISHED' in t.get('categories', [])]
            candidates = [t for t in candidates if t.get('price_change_1h', 0) < -5]
            if candidates:
                return min(candidates, key=lambda x: x.get('price_change_1h', 0))
        
        elif strategy_id == 3:  # Whale Shadow
            # Prefers: Large caps, high volume
            candidates = [t for t in tokens if 'LARGE_CAP' in t.get('categories', [])]
            if not candidates:
                candidates = [t for t in tokens if 'MID_CAP' in t.get('categories', [])]
            if candidates:
                return max(candidates, key=lambda x: x.get('volume_24h', 0))
        
        elif strategy_id == 4:  # RSI Oversold
            # Prefers: Established coins in dip
            candidates = [t for t in tokens if 'ESTABLISHED' in t.get('categories', [])]
            candidates = [t for t in candidates if t.get('price_change_1h', 0) < -8]
            if candidates:
                return candidates[0]
        
        elif strategy_id == 5:  # Breakout Hunter
            # Prefers: Mid-cap coins near resistance
            candidates = [t for t in tokens if 'MID_CAP' in t.get('categories', [])]
            candidates = [t for t in candidates if 0 < t.get('price_change_1h', 0) < 10]
            if candidates:
                return max(candidates, key=lambda x: x.get('price_change_1h', 0))
        
        elif strategy_id == 6:  # Social Sentiment
            # Prefers: New launches, meme coins
            candidates = [t for t in tokens if 'NEW_LAUNCH' in t.get('categories', [])]
            if not candidates:
                candidates = [t for t in tokens if 'MICRO_CAP' in t.get('categories', [])]
            if candidates:
                return candidates[0]
        
        elif strategy_id == 7:  # Liquidity Surfing
            # Prefers: High volume, any age
            candidates = sorted(tokens, key=lambda x: x.get('volume_24h', 0), reverse=True)
            if candidates:
                return candidates[0]
        
        elif strategy_id == 8:  # EMA Cross
            # Prefers: Established coins with trends
            candidates = [t for t in tokens if 'ESTABLISHED' in t.get('categories', [])]
            if not candidates:
                candidates = tokens
            if candidates:
                return candidates[0]
        
        elif strategy_id == 9:  # Range Trader
            # Prefers: Stable coins, established
            candidates = [t for t in tokens if 'ESTABLISHED' in t.get('categories', [])]
            candidates = [t for t in candidates if abs(t.get('price_change_1h', 0)) < 5]
            if candidates:
                return candidates[0]
        
        elif strategy_id == 10:  # News Arbitrage
            # Prefers: Any with volume spike
            candidates = sorted(tokens, key=lambda x: x.get('volume_24h', 0), reverse=True)
            if candidates:
                return candidates[0]
        
        # Fallback: random token
        import random
        return random.choice(tokens) if tokens else None


# ============================================================================
# GENETIC ENGINE
# ============================================================================

class GeneticEngine:
    """Main genetic algorithm engine"""
    
    def __init__(self, strategies: List[Strategy] = None):
        self.strategies = strategies or get_all_strategies()
        self.data_feed = None
        self.executor = None
        self.cycle_count = 0
        
    async def initialize(self):
        """Initialize data feed"""
        self.data_feed = DataFeed()
        await self.data_feed.__aenter__()
        
    async def run_cycle(self) -> Dict:
        """Execute one full trading cycle"""
        print(f"\n🔬 CYCLE #{self.cycle_count + 1}")
        print("=" * 60)
        
        # Fetch real tokens
        print("📡 Fetching live tokens from DexScreener...")
        tokens = await self.data_feed.get_trending_tokens(limit=100)
        
        if not tokens:
            print("   ❌ No tokens fetched, aborting cycle")
            return {'error': 'No tokens available'}
        
        print(f"\n🎯 TRADING ACTIONS")
        print("-" * 60)
        
        trades_executed = []
        
        for strategy in self.strategies:
            if not strategy.active:
                continue
            
            # Create executor for this strategy
            executor = StrategyExecutor(strategy, self.data_feed)
            
            # Select appropriate token for this strategy
            selected_token = executor.select_token_for_strategy(tokens)
            
            if selected_token:
                symbol = selected_token.get('symbol', 'UNKNOWN')
                
                # Calculate indicators
                indicators = self.data_feed.calculate_indicators(selected_token)
                
                # Check entry conditions
                should_enter, reason = self.should_enter(strategy, selected_token, indicators)
                
                if should_enter:
                    print(f"   🔴 {strategy.name}: ENTRY {symbol}")
                    print(f"      Price: ${selected_token.get('price', 0):.8f}")
                    print(f"      MCap: ${selected_token.get('market_cap', 0):,.0f}")
                    print(f"      Age: {selected_token.get('age_days', 0)} days")
                    print(f"      Categories: {selected_token.get('category_str', 'N/A')}")
                    print(f"      Reason: {reason}")
                    
                    # Record trade
                    trade = {
                        'strategy': strategy.name,
                        'symbol': symbol,
                        'type': 'ENTRY',
                        'price': selected_token.get('price', 0),
                        'amount_sol': 0.1,  # Fixed position size
                    }
                    trades_executed.append(trade)
                else:
                    print(f"   ⏸️  {strategy.name}: No entry ({reason})")
        
        self.cycle_count += 1
        
        return {
            'cycle': self.cycle_count,
            'tokens_available': len(tokens),
            'trades': trades_executed,
            'timestamp': datetime.now().isoformat()
        }
    
    def should_enter(self, strategy: Strategy, token: Dict, indicators: Dict) -> tuple[bool, str]:
        """Check if strategy should enter position"""
        strategy_id = strategy.id
        
        if strategy_id == 1:  # Momentum Surge
            if indicators['is_pumping'] and indicators['volume_spike']:
                return True, f"Momentum surge: +{indicators['price_momentum_1h']:.1f}% with volume"
        
        elif strategy_id == 2:  # Mean Reversion Dip
            change = indicators['price_momentum_1h']
            if -15 < change < -8:
                return True, f"Dip buy: {change:.1f}% (targeting bounce)"
        
        elif strategy_id == 3:  # Whale Shadow
            if indicators['volume_spike'] and indicators['mcap_tier'] in ['medium', 'large']:
                return True, "High volume on established token"
        
        elif strategy_id == 4:  # RSI Oversold
            if indicators['oversold'] and indicators['is_established']:
                return True, f"RSI oversold on established coin"
        
        elif strategy_id == 5:  # Breakout Hunter
            if 3 < indicators['price_momentum_1h'] < 15:
                return True, "Building momentum for breakout"
        
        elif strategy_id == 6:  # Social Sentiment
            if indicators['is_new'] and indicators['is_pumping']:
                return True, "New launch with momentum"
        
        elif strategy_id == 7:  # Liquidity Surfing
            if indicators['volume_spike']:
                return True, "Liquidity wave detected"
        
        elif strategy_id == 8:  # EMA Cross
            if indicators['is_established']:
                return True, "Technical setup on established coin"
        
        elif strategy_id == 9:  # Range Trader
            if abs(indicators['price_momentum_1h']) < 5 and indicators['is_established']:
                return True, "Range bound established coin"
        
        elif strategy_id == 10:  # News Arbitrage
            if indicators['volume_spike']:
                return True, "Volume spike - possible news"
        
        return False, "No signal"
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.data_feed:
            await self.data_feed.__aexit__(None, None, None)


# ============================================================================
# MAIN ENTRY
# ============================================================================

async def main():
    """Test the fixed engine"""
    print("🧬 GENETIC TRADING SYSTEM - LIVE DATA MODE")
    print("=" * 60)
    
    engine = GeneticEngine()
    
    try:
        await engine.initialize()
        
        # Run one cycle
        result = await engine.run_cycle()
        
        print("\n" + "=" * 60)
        print("📊 CYCLE SUMMARY")
        print("=" * 60)
        print(f"   Tokens available: {result.get('tokens_available', 0)}")
        print(f"   Trades executed: {len(result.get('trades', []))}")
        
        for trade in result.get('trades', []):
            print(f"   ✓ {trade['strategy']}: {trade['symbol']}")
        
    finally:
        await engine.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
