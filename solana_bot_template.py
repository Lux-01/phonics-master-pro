#!/usr/bin/env python3
"""
Solana Meme Coin Trading Bot - Starter Template
Complete working code for scanning, analyzing, and trading
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

# API Keys (replace with your own)
HELIUS_API_KEY = 'your_helius_key'
BIRDEYE_API_KEY = 'your_birdeye_key'

# Trading Parameters
MAX_POSITION_SIZE = 0.5  # SOL
STOP_LOSS_PERCENT = -7
TAKE_PROFIT_PERCENT = 30
MAX_HOLD_TIME_HOURS = 4
MIN_LIQUIDITY_USD = 10000
MIN_VOLUME_24H = 5000

# Solana addresses
SOL_MINT = 'So11111111111111111111111111111111111111112'
USDC_MINT = 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'

# ============================================================================
# API CLIENTS
# ============================================================================

class BirdeyeClient:
    """Birdeye API Client for price and token data"""
    
    BASE_URL = 'https://public-api.birdeye.so'
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {'X-API-KEY': api_key}
    
    def get_price(self, token_address: str) -> Optional[float]:
        """Get current token price"""
        try:
            url = f'{self.BASE_URL}/public/price'
            params = {'address': token_address}
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', {}).get('value')
            return None
        except Exception as e:
            logger.error(f"Birdeye price error: {e}")
            return None
    
    def get_token_list(self, sort_by: str = 'v24hUSD', limit: int = 50) -> List[Dict]:
        """Get list of tokens sorted by criteria"""
        try:
            url = f'{self.BASE_URL}/public/tokenlist'
            params = {
                'sort_by': sort_by,
                'sort_type': 'desc',
                'offset': 0,
                'limit': limit
            }
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json().get('data', {}).get('tokens', [])
            return []
        except Exception as e:
            logger.error(f"Birdeye token list error: {e}")
            return []
    
    def get_historical_price(self, token_address: str, timeframe: str = '1m') -> List[Dict]:
        """Get OHLCV data for technical analysis"""
        try:
            url = f'{self.BASE_URL}/public/history_price'
            params = {
                'address': token_address,
                'type': timeframe,
                'time_from': int((datetime.now() - timedelta(hours=24)).timestamp()),
                'time_to': int(datetime.now().timestamp())
            }
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json().get('data', {}).get('items', [])
            return []
        except Exception as e:
            logger.error(f"Birdeye history error: {e}")
            return []


class JupiterClient:
    """Jupiter API Client for swaps"""
    
    BASE_URL = 'https://quote-api.jup.ag/v6'
    
    def get_quote(self, input_mint: str, output_mint: str, 
                  amount: int, slippage_bps: int = 100) -> Optional[Dict]:
        """Get swap quote"""
        try:
            url = f'{self.BASE_URL}/quote'
            params = {
                'inputMint': input_mint,
                'outputMint': output_mint,
                'amount': amount,
                'slippageBps': slippage_bps,
                'onlyDirectRoutes': 'false',
                'asLegacyTransaction': 'false'
            }
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Jupiter quote error: {e}")
            return None
    
    def get_swap_transaction(self, quote_response: Dict, user_public_key: str) -> Optional[Dict]:
        """Get swap transaction from quote"""
        try:
            url = f'{self.BASE_URL}/swap'
            payload = {
                'quoteResponse': quote_response,
                'userPublicKey': user_public_key,
                'wrapAndUnwrapSOL': True,
                'prioritizationFeeLamports': 10000  # 0.00001 SOL priority fee
            }
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Jupiter swap error: {e}")
            return None


class DexScreenerClient:
    """DexScreener API Client for trending tokens"""
    
    BASE_URL = 'https://api.dexscreener.com'
    
    def get_token_profiles(self) -> List[Dict]:
        """Get latest token profiles"""
        try:
            url = f'{self.BASE_URL}/token-profiles/latest/v1'
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                profiles = response.json()
                # Filter for Solana only
                return [p for p in profiles if p.get('chainId') == 'solana']
            return []
        except Exception as e:
            logger.error(f"DexScreener error: {e}")
            return []
    
    def search_pairs(self, query: str) -> List[Dict]:
        """Search for trading pairs"""
        try:
            url = f'{self.BASE_URL}/latest/dex/search'
            params = {'q': query}
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json().get('pairs', [])
            return []
        except Exception as e:
            logger.error(f"DexScreener search error: {e}")
            return []


# ============================================================================
# SCANNING STRATEGIES
# ============================================================================

class TokenScanner:
    """Multi-source token scanner"""
    
    def __init__(self, birdeye_key: str):
        self.birdeye = BirdeyeClient(birdeye_key)
        self.dexscreener = DexScreenerClient()
    
    def scan_volume_spikes(self, min_volume_change: float = 300.0) -> List[Dict]:
        """
        Scan for tokens with significant volume spikes
        
        Args:
            min_volume_change: Minimum volume change % (default 300%)
        
        Returns:
            List of tokens with volume spikes
        """
        tokens = self.birdeye.get_token_list(sort_by='v24hUSD', limit=100)
        
        spikes = []
        for token in tokens:
            # Check filters
            if token.get('liquidity', 0) < MIN_LIQUIDITY_USD:
                continue
            if token.get('v24hUSD', 0) < MIN_VOLUME_24H:
                continue
            
            # Check volume change (if available)
            volume_change = token.get('v24hChangePercent', 0)
            if volume_change >= min_volume_change:
                spikes.append({
                    'address': token['address'],
                    'symbol': token.get('symbol', 'UNKNOWN'),
                    'name': token.get('name', 'Unknown'),
                    'price': token.get('price', 0),
                    'volume_24h': token.get('v24hUSD', 0),
                    'volume_change': volume_change,
                    'liquidity': token.get('liquidity', 0),
                    'market_cap': token.get('marketCap', 0)
                })
        
        return sorted(spikes, key=lambda x: x['volume_change'], reverse=True)
    
    def scan_new_tokens(self, max_age_hours: int = 24) -> List[Dict]:
        """
        Scan for recently created tokens
        
        Note: This is a simplified version. For production, use Helius webhooks
        to detect new token mints in real-time.
        """
        tokens = self.birdeye.get_token_list(sort_by='mcap', limit=200)
        
        new_tokens = []
        for token in tokens:
            # Filter for low market cap (new tokens)
            if token.get('marketCap', 0) < 100000:  # < $100K
                if token.get('liquidity', 0) > 5000:  # Min $5K liquidity
                    new_tokens.append({
                        'address': token['address'],
                        'symbol': token.get('symbol', 'UNKNOWN'),
                        'market_cap': token.get('marketCap', 0),
                        'liquidity': token.get('liquidity', 0),
                        'volume_24h': token.get('v24hUSD', 0)
                    })
        
        return new_tokens
    
    def scan_trending(self) -> List[Dict]:
        """Get trending tokens from DexScreener"""
        profiles = self.dexsccreener.get_token_profiles()
        
        trending = []
        for profile in profiles[:20]:
            trending.append({
                'address': profile.get('tokenAddress'),
                'symbol': profile.get('symbol', 'UNKNOWN'),
                'description': profile.get('description', '')
            })
        
        return trending


# ============================================================================
# TECHNICAL ANALYSIS
# ============================================================================

class TechnicalAnalyzer:
    """Technical analysis for meme coins"""
    
    def __init__(self, birdeye_key: str):
        self.birdeye = BirdeyeClient(birdeye_key)
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calculate Relative Strength Index"""
        if len(prices) < period + 1:
            return 50.0  # Neutral
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas[-period:]]
        losses = [-d if d < 0 else 0 for d in deltas[-period:]]
        
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_ema(self, prices: List[float], period: int) -> float:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return prices[-1] if prices else 0
        
        multiplier = 2 / (period + 1)
        ema = sum(prices[:period]) / period
        
        for price in prices[period:]:
            ema = (price - ema) * multiplier + ema
        
        return ema
    
    def analyze_token(self, token_address: str) -> Dict:
        """
        Complete technical analysis of a token
        
        Returns:
            Dict with analysis results
        """
        # Get historical data
        history = self.birdeye.get_historical_price(token_address, '1m')
        
        if not history or len(history) < 20:
            return {'error': 'Insufficient data'}
        
        prices = [item['price'] for item in history]
        volumes = [item.get('volume', 0) for item in history]
        
        # Calculate indicators
        rsi = self.calculate_rsi(prices)
        ema_9 = self.calculate_ema(prices, 9)
        ema_21 = self.calculate_ema(prices, 21)
        
        current_price = prices[-1]
        
        # Determine trend
        trend = 'BULLISH' if ema_9 > ema_21 else 'BEARISH'
        
        # Support/Resistance (simplified)
        support = min(prices[-20:])
        resistance = max(prices[-20:])
        
        # Volume analysis
        avg_volume = sum(volumes[-20:]) / 20
        current_volume = volumes[-1] if volumes else 0
        volume_spike = current_volume > avg_volume * 3
        
        return {
            'price': current_price,
            'rsi': rsi,
            'ema_9': ema_9,
            'ema_21': ema_21,
            'trend': trend,
            'support': support,
            'resistance': resistance,
            'volume_spike': volume_spike,
            'recommendation': self._generate_recommendation(rsi, trend, volume_spike)
        }
    
    def _generate_recommendation(self, rsi: float, trend: str, volume_spike: bool) -> str:
        """Generate trading recommendation"""
        if trend == 'BULLISH' and rsi < 70 and volume_spike:
            return 'BUY'
        elif trend == 'BEARISH' or rsi > 80:
            return 'SELL'
        else:
            return 'HOLD'


# ============================================================================
# TRADING BOT
# ============================================================================

class TradingBot:
    """Main trading bot class"""
    
    def __init__(self, birdeye_key: str, wallet_private_key: Optional[str] = None):
        self.scanner = TokenScanner(birdeye_key)
        self.analyzer = TechnicalAnalyzer(birdeye_key)
        self.jupiter = JupiterClient()
        self.birdeye = BirdeyeClient(birdeye_key)
        
        self.wallet_key = wallet_private_key
        self.positions = {}  # Track open positions
        self.trade_history = []
    
    def scan_and_analyze(self) -> List[Dict]:
        """
        Scan for opportunities and analyze them
        
        Returns:
            List of trading opportunities with analysis
        """
        logger.info("Scanning for opportunities...")
        
        # Scan for volume spikes
        candidates = self.scanner.scan_volume_spikes(min_volume_change=200)
        
        opportunities = []
        for token in candidates[:10]:  # Analyze top 10
            logger.info(f"Analyzing {token['symbol']}...")
            
            analysis = self.analyzer.analyze_token(token['address'])
            
            if analysis.get('recommendation') == 'BUY':
                opportunities.append({
                    **token,
                    **analysis
                })
        
        return opportunities
    
    def execute_paper_trade(self, token_address: str, amount_sol: float = 0.1) -> Dict:
        """
        Execute a paper trade (simulated)
        
        Args:
            token_address: Token to buy
            amount_sol: Amount of SOL to spend
        
        Returns:
            Trade details
        """
        entry_price = self.birdeye.get_price(token_address)
        
        if not entry_price:
            return {'error': 'Could not get price'}
        
        trade = {
            'id': len(self.trade_history) + 1,
            'token': token_address,
            'entry_price': entry_price,
            'amount_sol': amount_sol,
            'entry_time': datetime.now(),
            'status': 'OPEN',
            'stop_loss': entry_price * (1 + STOP_LOSS_PERCENT / 100),
            'take_profit': entry_price * (1 + TAKE_PROFIT_PERCENT / 100)
        }
        
        self.positions[token_address] = trade
        self.trade_history.append(trade)
        
        logger.info(f"Paper trade opened: {token_address} at {entry_price}")
        
        return trade
    
    def check_positions(self):
        """Check all open positions and close if needed"""
        for token_address, position in list(self.positions.items()):
            current_price = self.birdeye.get_price(token_address)
            
            if not current_price:
                continue
            
            pnl_percent = (current_price - position['entry_price']) / position['entry_price'] * 100
            
            # Check stop loss
            if current_price <= position['stop_loss']:
                self.close_position(token_address, current_price, 'STOP_LOSS')
            
            # Check take profit
            elif current_price >= position['take_profit']:
                self.close_position(token_address, current_price, 'TAKE_PROFIT')
            
            # Check time stop
            elif datetime.now() - position['entry_time'] > timedelta(hours=MAX_HOLD_TIME_HOURS):
                self.close_position(token_address, current_price, 'TIME_STOP')
            
            else:
                logger.info(f"Position {token_address}: {pnl_percent:+.2f}%")
    
    def close_position(self, token_address: str, exit_price: float, reason: str):
        """Close a position"""
        position = self.positions.pop(token_address, None)
        
        if position:
            pnl = (exit_price - position['entry_price']) / position['entry_price'] * 100
            position['exit_price'] = exit_price
            position['exit_time'] = datetime.now()
            position['pnl_percent'] = pnl
            position['exit_reason'] = reason
            position['status'] = 'CLOSED'
            
            logger.info(f"Position closed: {token_address} | PnL: {pnl:+.2f}% | Reason: {reason}")
    
    def get_performance_report(self) -> Dict:
        """Generate performance report"""
        closed_trades = [t for t in self.trade_history if t['status'] == 'CLOSED']
        
        if not closed_trades:
            return {'message': 'No completed trades yet'}
        
        wins = [t for t in closed_trades if t['pnl_percent'] > 0]
        losses = [t for t in closed_trades if t['pnl_percent'] <= 0]
        
        total_pnl = sum(t['pnl_percent'] for t in closed_trades)
        avg_win = sum(t['pnl_percent'] for t in wins) / len(wins) if wins else 0
        avg_loss = sum(t['pnl_percent'] for t in losses) / len(losses) if losses else 0
        
        return {
            'total_trades': len(closed_trades),
            'winning_trades': len(wins),
            'losing_trades': len(losses),
            'win_rate': len(wins) / len(closed_trades) * 100,
            'total_pnl_percent': total_pnl,
            'avg_win_percent': avg_win,
            'avg_loss_percent': avg_loss,
            'profit_factor': abs(sum(t['pnl_percent'] for t in wins) / sum(t['pnl_percent'] for t in losses)) if losses else float('inf')
        }


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main bot execution"""
    
    print("=" * 60)
    print("Solana Meme Coin Trading Bot")
    print("=" * 60)
    
    # Initialize bot
    bot = TradingBot(
        birdeye_key=BIRDEYE_API_KEY,
        wallet_private_key=None  # Paper trading mode
    )
    
    # Run scanning loop
    try:
        while True:
            print("\n" + "-" * 60)
            print(f"Scanning cycle: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("-" * 60)
            
            # Scan for opportunities
            opportunities = bot.scan_and_analyze()
            
            if opportunities:
                print(f"\n🎯 Found {len(opportunities)} opportunities:")
                for opp in opportunities:
                    print(f"\n  Token: {opp['symbol']}")
                    print(f"  Price: ${opp['price']:.6f}")
                    print(f"  RSI: {opp['rsi']:.1f}")
                    print(f"  Trend: {opp['trend']}")
                    print(f"  Volume Spike: {'Yes' if opp['volume_spike'] else 'No'}")
                    print(f"  Recommendation: {opp['recommendation']}")
                    
                    # Execute paper trade
                    if opp['recommendation'] == 'BUY':
                        trade = bot.execute_paper_trade(opp['address'])
                        print(f"  ✓ Paper trade executed: ID {trade['id']}")
            else:
                print("\n❌ No opportunities found this cycle")
            
            # Check existing positions
            bot.check_positions()
            
            # Show performance
            report = bot.get_performance_report()
            if 'total_trades' in report:
                print(f"\n📊 Performance:")
                print(f"  Total Trades: {report['total_trades']}")
                print(f"  Win Rate: {report['win_rate']:.1f}%")
                print(f"  Total PnL: {report['total_pnl_percent']:+.2f}%")
            
            # Wait before next scan
            print("\n⏳ Waiting 60 seconds...")
            time.sleep(60)
    
    except KeyboardInterrupt:
        print("\n\n👋 Bot stopped by user")
        
        # Final report
        report = bot.get_performance_report()
        print("\n" + "=" * 60)
        print("FINAL PERFORMANCE REPORT")
        print("=" * 60)
        for key, value in report.items():
            print(f"  {key}: {value}")


if __name__ == '__main__':
    main()
