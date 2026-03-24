#!/usr/bin/env python3
"""
Liquidity Scalping Backtest v2 for Solana Meme Coins
Strategy: Range-trading/mean reversion based on liquidity sweeps
Extended to 7 established meme coins
"""

import requests
import math
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import json
import time
from statistics import mean, stdev

# Birdeye API Configuration
BIRDEYE_API_KEY = "6335463fca7340f9a2c73eacd5a37f64"
BIRDEYE_BASE_URL = "https://public-api.birdeye.so"

# Target coins (token addresses) - 7 established meme coins
MEME_COINS = {
    "WIF": "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm",
    "POPCAT": "7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr",
    "BONK": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
    "MEW": "MEW1gQWJ3nEXg2qgERiKu7FAFj79PHvQVREQUzScPP5",
    "PENGU": "2zMMhcVQEXDtdE6vsFS7S7D5oUodfJHE8vd1gnBouauv",  # Pudgy Penguins
    "BOME": "ukHH6c7mMyiWCf1b9pnWe25TSpkDDt3H5pQZgZ74J82",  # Book of Meme
    "SLERF": "9999FVbjHioTcoJpoBiSjpxHW6xEn3witVuXKqBh2RFQ",  # Slerf
}


class Candle:
    """Represents a single OHLCV candle"""
    def __init__(self, timestamp: int, open_price: float, high: float, low: float, close: float, volume: float):
        self.timestamp = timestamp
        self.datetime = datetime.fromtimestamp(timestamp)
        self.open = open_price
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        
        # Technical indicators
        self.sma = None
        self.ema = None
        self.std = None
        self.atr = None
        self.bb_width = None
        self.support_level = None
        self.resistance_level = None
        self.range_mid = None
        
        # Signals
        self.sweep_signal = False
        self.entry_price = None
        self.stop_loss = None
        self.take_profit_1 = None
        self.take_profit_2 = None


class LiquidityScalper:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "accept": "application/json",
            "x-api-key": api_key
        }
        
    def fetch_ohlcv(self, token_address: str, timeframe: str = "15m", 
                    days_back: int = 7) -> List[Candle]:
        """Fetch OHLCV data from Birdeye API"""
        
        end_time = int(datetime.now().timestamp())
        start_time = end_time - (days_back * 24 * 60 * 60)
        
        url = f"{BIRDEYE_BASE_URL}/defi/ohlcv"
        params = {
            "address": token_address,
            "type": timeframe,
            "time_from": start_time,
            "time_to": end_time
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("data", {}).get("items"):
                    items = data["data"]["items"]
                    candles = []
                    for item in items:
                        candle = Candle(
                            timestamp=item.get('unixTime', 0),
                            open_price=float(item.get('o', 0)),
                            high=float(item.get('h', 0)),
                            low=float(item.get('l', 0)),
                            close=float(item.get('c', 0)),
                            volume=float(item.get('v', 0))
                        )
                        candles.append(candle)
                    
                    candles.sort(key=lambda x: x.timestamp)
                    return candles
                else:
                    print(f"  ⚠️ No data returned")
                    return []
            else:
                print(f"  ⚠️ API error: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"  ⚠️ Error fetching data: {e}")
            return []
    
    def calculate_indicators(self, candles: List[Candle]) -> List[Candle]:
        """Calculate technical indicators"""
        
        # SMA 20
        for i in range(len(candles)):
            if i >= 19:
                closes = [c.close for c in candles[i-19:i+1]]
                candles[i].sma = mean(closes)
                if len(closes) > 1:
                    candles[i].std = stdev(closes)
        
        # ATR 14
        for i in range(len(candles)):
            if i >= 13:
                trs = []
                for j in range(i-13, i+1):
                    if j == 0:
                        trs.append(candles[j].high - candles[j].low)
                    else:
                        tr1 = candles[j].high - candles[j].low
                        tr2 = abs(candles[j].high - candles[j-1].close)
                        tr3 = abs(candles[j].low - candles[j-1].close)
                        trs.append(max(tr1, tr2, tr3))
                candles[i].atr = mean(trs)
        
        # BB Width
        for i in range(len(candles)):
            if candles[i].sma and candles[i].std:
                upper = candles[i].sma + 2 * candles[i].std
                lower = candles[i].sma - 2 * candles[i].std
                candles[i].bb_width = (upper - lower) / candles[i].sma if candles[i].sma > 0 else 0
        
        return candles
    
    def find_support_resistance(self, candles: List[Candle]) -> List[Candle]:
        """Find support and resistance levels using recent price action"""
        
        lookback = 16  # 4 hours on 15m candles
        
        for i in range(lookback, len(candles)):
            # Get recent candles
            recent = candles[i-lookback:i]
            
            # Support = lowest low of recent period
            # Resistance = highest high of recent period
            recent_lows = [c.low for c in recent]
            recent_highs = [c.high for c in recent]
            recent_closes = [c.close for c in recent]
            
            # Find local minima/maxima (swing points)
            swing_lows = []
            swing_highs = []
            
            for j in range(2, len(recent) - 2):
                # Swing low: lower than 2 candles before and after
                if recent[j].low < recent[j-1].low and recent[j].low < recent[j-2].low:
                    if recent[j].low < recent[j+1].low and recent[j].low < recent[j+2].low:
                        swing_lows.append(recent[j].low)
                
                # Swing high: higher than 2 candles before and after
                if recent[j].high > recent[j-1].high and recent[j].high > recent[j-2].high:
                    if recent[j].high > recent[j+1].high and recent[j].high > recent[j+2].high:
                        swing_highs.append(recent[j].high)
            
            # Set current support/resistance
            if swing_lows:
                candles[i].support_level = min(swing_lows[-3:]) if len(swing_lows) >= 3 else min(swing_lows)
            else:
                candles[i].support_level = min(recent_lows)
            
            if swing_highs:
                candles[i].resistance_level = max(swing_highs[-3:]) if len(swing_highs) >= 3 else max(swing_highs)
            else:
                candles[i].resistance_level = max(recent_highs)
            
            # Calculate range mid point
            if candles[i].support_level and candles[i].resistance_level:
                candles[i].range_mid = (candles[i].support_level + candles[i].resistance_level) / 2
        
        return candles
    
    def detect_sweep_signals(self, candles: List[Candle]) -> List[Candle]:
        """
        Detect liquidity sweep and reclaim pattern:
        1. Price wicks below support (1-6% fakeout)
        2. Closes back above support within 3 candles
        """
        
        for i in range(20, len(candles) - 5):
            if candles[i].support_level is None:
                continue
            
            support = candles[i].support_level
            current_low = candles[i].low
            current_close = candles[i].close
            sweep_low = candles[i].low
            
            # Calculate how much price dipped below support
            if current_low >= support:
                continue  # No sweep happened
            
            dip_pct = (support - current_low) / support
            
            # Valid sweep: 1-6% below support (wider range for meme coins)
            if 0.01 <= dip_pct <= 0.06:
                # Check if it reclaims within next 3 candles
                for j in range(1, 4):
                    if i + j < len(candles):
                        reclaim_candle = candles[i + j]
                        
                        # Reclaim: close above support
                        if reclaim_candle.close >= support:
                            candles[i + j].sweep_signal = True
                            candles[i + j].entry_price = reclaim_candle.close
                            candles[i + j].stop_loss = sweep_low * 0.992  # Tight stop below sweep low
                            
                            # Take profits
                            if candles[i].range_mid and reclaim_candle.close < candles[i].range_mid:
                                candles[i + j].take_profit_1 = candles[i].range_mid
                            else:
                                # If already above mid, target resistance
                                candles[i + j].take_profit_1 = candles[i].resistance_level * 0.95
                            
                            candles[i + j].take_profit_2 = candles[i].resistance_level
                            break
        
        return candles
    
    def backtest(self, candles: List[Candle], symbol: str) -> List[Dict]:
        """Execute backtest on candles"""
        trades = []
        in_position = False
        entry_price = 0
        stop_loss = 0
        take_profit_1 = 0
        take_profit_2 = 0
        entry_time = None
        entry_idx = 0
        lowest_low = float('inf')
        
        for i in range(len(candles)):
            if in_position:
                current_high = candles[i].high
                current_low = candles[i].low
                current_close = candles[i].close
                
                # Track lowest low for trailing stop
                if current_low < lowest_low:
                    lowest_low = current_low
                
                # Check stop loss
                if current_low <= stop_loss:
                    pnl = (stop_loss - entry_price) / entry_price
                    trades.append({
                        'symbol': symbol,
                        'entry_time': entry_time.isoformat(),
                        'exit_time': candles[i].datetime.isoformat(),
                        'entry_price': entry_price,
                        'exit_price': stop_loss,
                        'pnl_pct': pnl,
                        'result': 'loss',
                        'exit_reason': 'stop_loss'
                    })
                    in_position = False
                    continue
                
                # Check take profit 2 (resistance) - full position
                if take_profit_2 and current_high >= take_profit_2:
                    pnl = (take_profit_2 - entry_price) / entry_price
                    trades.append({
                        'symbol': symbol,
                        'entry_time': entry_time.isoformat(),
                        'exit_time': candles[i].datetime.isoformat(),
                        'entry_price': entry_price,
                        'exit_price': take_profit_2,
                        'pnl_pct': pnl,
                        'result': 'win',
                        'exit_reason': 'take_profit_2'
                    })
                    in_position = False
                    continue
                
                # Check take profit 1 (mid-range) - full position
                if take_profit_1 and current_high >= take_profit_1:
                    pnl = (take_profit_1 - entry_price) / entry_price
                    trades.append({
                        'symbol': symbol,
                        'entry_time': entry_time.isoformat(),
                        'exit_time': candles[i].datetime.isoformat(),
                        'entry_price': entry_price,
                        'exit_price': take_profit_1,
                        'pnl_pct': pnl,
                        'result': 'win',
                        'exit_reason': 'take_profit_1'
                    })
                    in_position = False
                    continue
                
                # Time-based exit (max 8 candles = 2 hours)
                if i - entry_idx >= 8:
                    pnl = (current_close - entry_price) / entry_price
                    trades.append({
                        'symbol': symbol,
                        'entry_time': entry_time.isoformat(),
                        'exit_time': candles[i].datetime.isoformat(),
                        'entry_price': entry_price,
                        'exit_price': current_close,
                        'pnl_pct': pnl,
                        'result': 'win' if pnl > 0 else 'loss',
                        'exit_reason': 'time_exit'
                    })
                    in_position = False
                    continue
            
            else:
                # Look for entry
                if candles[i].sweep_signal and candles[i].entry_price:
                    in_position = True
                    entry_price = candles[i].entry_price
                    stop_loss = candles[i].stop_loss
                    take_profit_1 = candles[i].take_profit_1
                    take_profit_2 = candles[i].take_profit_2
                    entry_time = candles[i].datetime
                    entry_idx = i
                    lowest_low = candles[i].low
        
        return trades
    
    def run_backtest(self, coins: Dict[str, str] = None, days_back: int = 14) -> Dict:
        """Run backtest on specified coins"""
        if coins is None:
            coins = MEME_COINS
        
        all_trades = []
        summary_by_coin = {}
        detailed_results = {}
        
        print("=" * 70)
        print("LIQUIDITY SCALPING BACKTEST v2 - 7 Solana Meme Coins")
        print("=" * 70)
        print(f"Timeframe: 15m | Lookback: {days_back} days")
        print(f"Strategy: Support Sweep + Reclaim")
        print("-" * 70)
        print(f"Entry: Price wicks 1-6% below support, reclaims within 3 candles")
        print(f"Stop Loss: 0.8% below sweep low")
        print(f"Take Profit 1: Range middle")
        print(f"Take Profit 2: Resistance level")
        print(f"Time Exit: 8 candles (2 hours)")
        print("=" * 70)
        
        for symbol, address in coins.items():
            print(f"\n🔍 Testing {symbol}...")
            
            candles = self.fetch_ohlcv(address, timeframe="15m", days_back=days_back)
            
            if not candles or len(candles) < 50:
                print(f"  ❌ Insufficient data")
                summary_by_coin[symbol] = {
                    'total_trades': 0, 'wins': 0, 'losses': 0,
                    'win_rate': 0, 'avg_profit_per_trade': 0, 'total_return_pct': 0,
                    'best_trade': 0, 'worst_trade': 0
                }
                continue
            
            print(f"  📊 Fetched {len(candles)} candles ({len(candles)/96:.1f} days)")
            
            # Calculate indicators
            candles = self.calculate_indicators(candles)
            candles = self.find_support_resistance(candles)
            candles = self.detect_sweep_signals(candles)
            
            # Stats
            consolidation_periods = sum(1 for c in candles if c.bb_width and c.bb_width < 0.05)
            signals = sum(1 for c in candles if c.sweep_signal)
            print(f"  📉 Consolidation periods: {consolidation_periods}")
            print(f"  🎯 Sweep signals found: {signals}")
            
            # Backtest
            trades = self.backtest(candles, symbol)
            all_trades.extend(trades)
            
            if trades:
                wins = len([t for t in trades if t['result'] == 'win'])
                losses = len([t for t in trades if t['result'] == 'loss'])
                win_rate = (wins / len(trades)) * 100
                profits = [t['pnl_pct'] for t in trades]
                avg_profit = mean(profits) * 100
                total_return = sum(profits) * 100
                best_trade = max(profits) * 100
                worst_trade = min(profits) * 100
                
                # Win/loss PnL
                win_pnl = [t['pnl_pct'] for t in trades if t['result'] == 'win']
                loss_pnl = [t['pnl_pct'] for t in trades if t['result'] == 'loss']
                avg_win = mean(win_pnl) * 100 if win_pnl else 0
                avg_loss = mean(loss_pnl) * 100 if loss_pnl else 0
                
                summary_by_coin[symbol] = {
                    'total_trades': len(trades),
                    'wins': wins,
                    'losses': losses,
                    'win_rate': round(win_rate, 2),
                    'avg_profit_per_trade': round(avg_profit, 4),
                    'total_return_pct': round(total_return, 4),
                    'best_trade': round(best_trade, 4),
                    'worst_trade': round(worst_trade, 4),
                    'avg_win_pct': round(avg_win, 4),
                    'avg_loss_pct': round(avg_loss, 4),
                    'risk_reward': round(abs(avg_win / avg_loss), 2) if avg_loss != 0 else 0
                }
                
                print(f"  ✅ Trades: {len(trades)} | Win Rate: {win_rate:.1f}% | Total Return: {total_return:.2f}%")
                print(f"     Best: {best_trade:.2f}% | Worst: {worst_trade:.2f}%")
            else:
                print(f"  ⚠️ No trades executed")
                summary_by_coin[symbol] = {
                    'total_trades': 0, 'wins': 0, 'losses': 0,
                    'win_rate': 0, 'avg_profit_per_trade': 0, 'total_return_pct': 0,
                    'best_trade': 0, 'worst_trade': 0, 'avg_win_pct': 0, 'avg_loss_pct': 0,
                    'risk_reward': 0
                }
            
            detailed_results[symbol] = trades
            time.sleep(0.5)
        
        # Overall metrics
        if all_trades:
            total_wins = len([t for t in all_trades if t['result'] == 'win'])
            total_losses = len([t for t in all_trades if t['result'] == 'loss'])
            win_rate = (total_wins / len(all_trades)) * 100
            
            profits = [t['pnl_pct'] for t in all_trades]
            avg_profit = mean(profits) * 100
            
            # Drawdown calculation
            cumulative = []
            running_sum = 0
            for p in profits:
                running_sum += p
                cumulative.append(running_sum)
            
            running_max = [max(cumulative[:i+1]) for i in range(len(cumulative))]
            drawdowns = [c - m for c, m in zip(cumulative, running_max)]
            max_drawdown = float(min(drawdowns)) * 100 if drawdowns else 0
            
            # Risk/Reward
            win_pnl = [t['pnl_pct'] for t in all_trades if t['result'] == 'win']
            loss_pnl = [t['pnl_pct'] for t in all_trades if t['result'] == 'loss']
            avg_win = mean(win_pnl) * 100 if win_pnl else 0
            avg_loss = mean(loss_pnl) * 100 if loss_pnl else 0
            rr = abs(avg_win / avg_loss) if avg_loss and avg_loss != 0 else 0
            
            best_trade = max(profits) * 100
            worst_trade = min(profits) * 100
        else:
            total_wins = total_losses = 0
            win_rate = avg_profit = max_drawdown = rr = 0
            best_trade = worst_trade = 0
        
        results = {
            'backtest_config': {
                'coins_tested': list(coins.keys()),
                'timeframe': '15m',
                'lookback_days': days_back,
                'sweep_threshold': '1-6% below support',
                'reclaim_window': '3 candles',
                'stop_loss': '0.8% below sweep low',
                'take_profit_1': 'Range mid',
                'take_profit_2': 'Resistance',
                'max_hold': '2 hours (8 candles)'
            },
            'overall_metrics': {
                'total_trades': len(all_trades),
                'wins': total_wins,
                'losses': total_losses,
                'win_rate': round(win_rate, 2),
                'avg_profit_per_trade': round(avg_profit, 4),
                'max_drawdown_pct': round(max_drawdown, 4),
                'risk_reward_ratio': round(rr, 2),
                'total_return_pct': round(sum([t['pnl_pct'] for t in all_trades]) * 100, 4) if all_trades else 0,
                'best_trade': round(best_trade, 4),
                'worst_trade': round(worst_trade, 4)
            },
            'per_coin_summary': summary_by_coin,
            'trades_by_coin': detailed_results,
            'all_trades': all_trades
        }
        
        print("\n" + "=" * 70)
        print("BACKTEST RESULTS SUMMARY - 7 COINS")
        print("=" * 70)
        print(f"Total Trades: {len(all_trades)}")
        print(f"Wins: {total_wins} | Losses: {total_losses}")
        print(f"Win Rate: {win_rate:.2f}%")
        print(f"Avg Profit/Trade: {avg_profit:.4f}%")
        print(f"Total Return: {sum([t['pnl_pct'] for t in all_trades]) * 100:.2f}%")
        print(f"Max Drawdown: {max_drawdown:.4f}%")
        print(f"Risk/Reward: {rr:.2f}")
        print(f"Best Trade: {best_trade:.2f}% | Worst Trade: {worst_trade:.2f}%")
        print("=" * 70)
        
        return results


def main():
    print("\n🚀 Liquidity Scalping Backtest v2 - 7 Meme Coins\n")
    
    scalper = LiquidityScalper(BIRDEYE_API_KEY)
    results = scalper.run_backtest(MEME_COINS, days_back=14)
    
    # Save results
    with open("liquidity_scalper_7coin_results.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n💾 Results saved to liquidity_scalper_7coin_results.json")
    
    return results


if __name__ == "__main__":
    main()
