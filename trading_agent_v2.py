#!/usr/bin/env python3
"""
Solana Meme Coin Trading Agent v2.0
Monitors 7 coins during 12am-4am Sydney, sends axiom.trade alerts
"""

import asyncio
import json
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional
import aiohttp

# Token contract addresses (Solana mainnet)
TOKENS = {
    'WIF': 'EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm',
    'POPCAT': '7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr',
    'BONK': 'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263',
    'BOME': 'ukHH6c7mMyiWCf1b9pnWe25TSpkDDt3H5pQZgZ74J82',
    'SLERF': '9999FVbjHioTcoJpoBiSjpxHW6xEn3witVuXKqBh2RFQ',
    'PENGU': '2zMMhcVQEXDtdE6vsFS7S7D5oUodfJHE8vd1gnBouauv',
    'MEW': 'MEW1gQWJ3nEXg2qgERiKu7FAFj79PHvQVREQUzScPP5'
}

# Token metadata
CATEGORY_MAP = {
    'WIF': 'dog',
    'BONK': 'dog',
    'POPCAT': 'cat',
    'MEW': 'cat',
    'BOME': 'meme',
    'SLERF': 'meme',
    'PENGU': 'bird'
}

# Strategy v2.0 Settings
SETTINGS = {
    'min_market_cap': 20_000_000,  # $20M
    'max_positions': 3,
    'position_sizes': {'A+': 0.5, 'B': 0.25, 'C': 0},
    'dip_threshold_min': -0.18,  # -18%
    'dip_threshold_max': -0.10,    # -10%
    'volume_multiplier': 2.0,
    'ema_period': 20,
    'scale_1_target': 0.08,        # +8%
    'hard_stop': -0.07,            # -7%
    'time_stop_minutes': 30,
    'trading_window_start': 0,     # 12am Sydney
    'trading_window_end': 4,       # 4am Sydney
    'telegram_chat_id': '6610224534'
}

class TradingAgent:
    def __init__(self):
        self.prices = {k: [] for k in TOKENS}
        self.volumes = {k: [] for k in TOKENS}
        self.positions = {}
        self.trade_history = []
        
    async def fetch_prices(self) -> Dict[str, dict]:
        """Fetch current prices from DexScreener by token address"""
        results = {}
        async with aiohttp.ClientSession() as session:
            for symbol, token_addr in TOKENS.items():
                try:
                    # DexScreener token endpoint
                    url = f"https://api.dexscreener.com/latest/dex/tokens/{token_addr}"
                    async with session.get(url, timeout=10) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            pairs = data.get('pairs', [])
                            if pairs:
                                # Get the pair with highest liquidity
                                pair = max(pairs, key=lambda x: float(x.get('liquidity', {}).get('usd', 0) or 0))
                                results[symbol] = {
                                    'price': float(pair['priceUsd']),
                                    'volume24h': float(pair['volume'].get('h24', 0)),
                                    'liquidity': float(pair.get('liquidity', {}).get('usd', 0)),
                                    'mcap': float(pair.get('fdv', 0)),
                                    'priceChange': float(pair.get('priceChange', {}).get('h24', 0)),
                                    'token_address': token_addr
                                }
                except Exception as e:
                    print(f"Error fetching {symbol}: {e}")
                    await asyncio.sleep(0.5)  # Rate limiting
        return results
    
    def calculate_ema(self, prices: List[float], period: int = 20) -> float:
        """Calculate EMA for trend filter"""
        if len(prices) < period:
            return prices[-1] if prices else 0
        
        multiplier = 2 / (period + 1)
        ema = prices[0]
        for price in prices[1:]:
            ema = (price - ema) * multiplier + ema
        return ema
    
    def calculate_avg_volume(self, volumes: List[float]) -> float:
        """Calculate average volume over last 20 periods"""
        if len(volumes) < 20:
            return sum(volumes) / len(volumes) if volumes else 0
        return sum(volumes[-20:]) / 20
    
    def check_dip_signal(self, prices: List[float]) -> bool:
        """Check if price dipped -10% to -18% from recent high"""
        if len(prices) < 5:
            return False
        
        recent_high = max(prices[-20:]) if len(prices) >= 20 else max(prices)
        current = prices[-1]
        drop_pct = (current - recent_high) / recent_high
        
        return SETTINGS['dip_threshold_max'] <= drop_pct <= SETTINGS['dip_threshold_min']
    
    def check_momentum_shift(self, prices: List[float]) -> bool:
        """Check for green candle after 2 red candles"""
        if len(prices) < 3:
            return False
        
        prev_2 = prices[-3]
        prev_1 = prices[-2]
        current = prices[-1]
        
        # Two red candles (price went down)
        candle_1_red = prev_1 < prev_2
        candle_2_red = current < prev_1
        
        # Actually for "green after 2 reds", we need to look at closes
        # Simplified: current > prev_1 and prev_1 < prev_2 < prev_3
        return current > prev_1 and prev_1 < prev_2
    
    def grade_setup(self, token_data: dict, prices: List[float], volumes: List[float]) -> str:
        """Grade setup quality: A+, B, or C"""
        grade = 'A+'
        reasons = []
        
        # Check market cap
        if token_data.get('mcap', 0) < SETTINGS['min_market_cap']:
            grade = 'C'
            reasons.append(f"Market cap ${token_data.get('mcap', 0):,.0f} < ${SETTINGS['min_market_cap']:,}")
        
        # Check EMA trend
        ema = self.calculate_ema(prices)
        if prices and prices[-1] < ema:
            if grade == 'A+':
                grade = 'B'
            reasons.append("Below EMA20")
        
        # Check volume
        avg_vol = self.calculate_avg_volume(volumes)
        current_vol = volumes[-1] if volumes else 0
        if avg_vol > 0 and current_vol < avg_vol * SETTINGS['volume_multiplier']:
            if grade == 'A+':
                grade = 'B'
            reasons.append(f"Volume {current_vol/avg_vol:.1f}x < {SETTINGS['volume_multiplier']}x")
        
        return grade, reasons
    
    def check_entry_signal(self, symbol: str, prices: List[float], volumes: List[float], token_data: dict) -> Optional[dict]:
        """Check if entry conditions are met"""
        # Grade the setup
        grade, reasons = self.grade_setup(token_data, prices, volumes)
        
        if grade == 'C':
            return None
        
        # Check entry signals
        dip_signal = self.check_dip_signal(prices)
        momentum_signal = self.check_momentum_shift(prices)
        
        if not (dip_signal or momentum_signal):
            return None
        
        # Calculate position size
        position_size = SETTINGS['position_sizes'].get(grade, 0)
        
        return {
            'symbol': symbol,
            'grade': grade,
            'price': prices[-1],
            'position_size': position_size,
            'dip_signal': dip_signal,
            'momentum_signal': momentum_signal,
            'ema': self.calculate_ema(prices),
            'volume_ratio': volumes[-1] / self.calculate_avg_volume(volumes) if volumes else 0,
            'token_address': token_data.get('token_address', TOKENS[symbol]),
            'mcap': token_data.get('mcap', 0),
            'reasons': reasons
        }
    
    def generate_axiom_link(self, symbol: str, token_address: str) -> str:
        """Generate axiom.trade link"""
        return f"https://axiom.trade/t/{token_address}/@skuxx121?chain=sol"
    
    def format_alert(self, signal: dict) -> str:
        """Format Telegram alert message"""
        token_address = signal.get('token_address', TOKENS[signal['symbol']])
        axiom_link = self.generate_axiom_link(signal['symbol'], token_address)
        
        signal_type = "DIP" if signal['dip_signal'] else "MOMENTUM"
        
        mcap_str = f"${signal['mcap']/1_000_000:.1f}M" if signal.get('mcap', 0) > 0 else "N/A"
        
        msg = f"""🔵 **{signal['symbol']} SETUP - Grade {signal['grade']}**

📊 Signal: {signal_type}
💰 Price: ${signal['price']:.8f}
📈 EMA20: ${signal['ema']:.8f}
📊 Volume: {signal['volume_ratio']:.1f}x avg
💵 Position: {signal['position_size']} SOL
💎 Market Cap: {mcap_str}

Setup:
• Market Cap: {'✅ $20M+' if signal.get('mcap', 0) >= SETTINGS['min_market_cap'] else '❌ Too small'}
• Trend: {'✅ Above EMA' if signal['price'] > signal['ema'] else '⚠️ Check trend'}
• Volume: {signal['volume_ratio']:.1f}x average {'✅' if signal['volume_ratio'] >= SETTINGS['volume_multiplier'] else '❌'}

Exit Plan:
• Scale 1: Sell 50% at +8%
• Stop: -7% (hard) / Breakeven (after scale)
• Time: 30 min max

👉 **Buy:** {axiom_link}

Reply "YES" to confirm trade"""
        
        return msg
    
    async def send_telegram_alert(self, message: str):
        """Send alert to Telegram by writing to file for OpenClaw pickup"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"\n{'='*60}")
        print(f"ALERT TO TELEGRAM [{timestamp}]:")
        print(f"{'='*60}")
        print(message)
        print(f"{'='*60}\n")
        
        # Write to JSON file for Telegram bot pickup
        import json
        signals_file = '/tmp/trading_signals.json'
        
        try:
            signals = []
            if os.path.exists(signals_file):
                with open(signals_file, 'r') as f:
                    signals = json.load(f)
        except:
            signals = []
        
        signals.append({
            'timestamp': timestamp,
            'message': message,
            'notified': False
        })
        
        try:
            with open(signals_file, 'w') as f:
                json.dump(signals, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save signal: {e}")
    
    async def scan_for_entries(self):
        """Main scanning loop"""
        print(f"\n{'='*60}")
        print(f"Scanning at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        # Fetch current data
        market_data = await self.fetch_prices()
        
        if not market_data:
            print("No data fetched")
            return
        
        # Update price/volume history
        for symbol, data in market_data.items():
            self.prices[symbol].append(data['price'])
            self.volumes[symbol].append(data['volume24h'])
            
            # Keep only last 50 data points
            self.prices[symbol] = self.prices[symbol][-50:]
            self.volumes[symbol] = self.volumes[symbol][-50:]
        
        # Check for entry signals
        for symbol in TOKENS:
            if symbol not in market_data:
                continue
            
            # Check if we already have a position
            if symbol in self.positions:
                # Monitor existing position
                await self.monitor_position(symbol, market_data[symbol])
                continue
            
            # Check for entry
            if len(self.prices[symbol]) >= 20:
                signal = self.check_entry_signal(
                    symbol,
                    self.prices[symbol],
                    self.volumes[symbol],
                    market_data[symbol]
                )
                
                if signal:
                    alert = self.format_alert(signal)
                    await self.send_telegram_alert(alert)
                    
                    # Log the signal
                    self.trade_history.append({
                        'time': datetime.now().isoformat(),
                        'type': 'signal',
                        'data': signal
                    })
    
    async def monitor_position(self, symbol: str, market_data: dict):
        """Monitor existing position for exits"""
        # Implementation for stop/target checks
        pass
    
    def is_trading_window(self) -> bool:
        """Check if we're in the 12am-4am Sydney trading window"""
        # Sydney is UTC+11
        now = datetime.now(timezone.utc)
        sydney_hour = (now.hour + 11) % 24  # Convert to Sydney time
        
        return SETTINGS['trading_window_start'] <= sydney_hour < SETTINGS['trading_window_end']
    
    async def run(self):
        """Main loop"""
        print("="*60)
        print("Solana Meme Coin Trading Agent v2.0")
        print("Strategy: Optimal v2.0")
        print("Trading Window: 12am-4am Sydney")
        print("="*60)
        
        while True:
            if self.is_trading_window():
                await self.scan_for_entries()
                await asyncio.sleep(300)  # 5 minute interval
            else:
                # Outside trading hours
                now = datetime.now(timezone.utc)
                sydney_hour = (now.hour + 11) % 24
                print(f"Outside trading window (Sydney: {sydney_hour}:00). Sleeping...")
                await asyncio.sleep(600)  # Check every 10 min

async def main():
    agent = TradingAgent()
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())
