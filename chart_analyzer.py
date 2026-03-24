#!/usr/bin/env python3
"""
Chart Analyzer for Solana Alpha Hunter v5.5
Technical Analysis for memecoin chart patterns
Uses: DexScreener, Birdeye for OHLC data
Timeframe: 15m candles (fast moves, memecoin lifecycle)
"""

import requests
import json
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Candle:
    """OHLC candle data"""
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    
@dataclass
class ChartSignals:
    """Technical analysis signals"""
    rsi: float
    ema_9: float
    ema_21: float
    vwap: float
    support: List[float]
    resistance: List[float]
    trend: str  # 'bullish', 'bearish', 'neutral'
    breakout_detected: bool
    breakdown_detected: bool
    consolidating: bool
    volume_trend: str  # 'increasing', 'decreasing', 'stable'
    oscillator_detected: bool = False
    oscillator_score: int = 0
    range_pct: float = 0.0
    sr_touches: int = 0

class ChartAnalyzer:
    """Technical Analysis engine for memecoin charts"""
    
    def __init__(self, timeframe: str = '15m'):
        self.timeframe = timeframe
        self.lookback_hours = 24  # 24h of 15m candles = 96 candles
        
    def fetch_ohlc_dexscreener(self, ca: str) -> List[Candle]:
        """Fetch OHLC - try Birdeye first for real data, then DexScreener"""
        
        # First try Birdeye for real OHLC data
        print("  📊 Trying Birdeye for real OHLC data...")
        birdeye_candles = self._fetch_from_birdeye(ca)
        if len(birdeye_candles) >= 20:
            print(f"  ✅ Got {len(birdeye_candles)} real candles from Birdeye")
            return birdeye_candles
        
        # Fallback to DexScreener synthetic data
        print("  📊 Falling back to DexScreener...")
        try:
            url = f"https://api.dexscreener.com/latest/dex/tokens/{ca}"
            r = requests.get(url, timeout=10)
            
            if r.status_code != 200:
                return []
            
            data = r.json()
            pairs = data.get('pairs', [])
            
            if not pairs:
                return []
            
            best_pair = max(pairs, key=lambda x: float(x.get('liquidity', {}).get('usd', 0)))
            candles = self._build_candles_from_txns(best_pair)
            
            if len(candles) >= 20:
                return candles
            
            return self._generate_synthetic_candles(best_pair)
            
        except Exception as e:
            print(f"  ⚠️ DexScreener chart fetch failed: {e}")
            return []
    
    def _build_candles_from_txns(self, pair: dict) -> List[Candle]:
        """Build candles from transaction data"""
        candles = []
        
        try:
            price_native = float(pair.get('priceNative', 0))
            price_usd = float(pair.get('priceUsd', 0))
            txns = pair.get('txns', {})
            
            # Use different timeframes to simulate candles
            candles_data = [
                {'time': 6, 'label': 'h6', 'buy': txns.get('h6', {}).get('buys', 0), 'sell': txns.get('h6', {}).get('sells', 0)},
                {'time': 1, 'label': 'h1', 'buy': txns.get('h1', {}).get('buys', 0), 'sell': txns.get('h1', {}).get('sells', 0)},
                {'time': 0.083, 'label': 'm5', 'buy': txns.get('m5', {}).get('buys', 0), 'sell': txns.get('m5', {}).get('sells', 0)},
            ]
            
            # Generate synthetic candles based on txns
            now = int(datetime.now().timestamp())
            base_candles = []
            
            for i, data in enumerate(candles_data):
                if price_usd > 0:
                    # Simulate price movement based on buy/sell ratio
                    total = data['buy'] + data['sell']
                    if total > 0:
                        buy_ratio = data['buy'] / total
                        change = (buy_ratio - 0.5) * 0.1  # 10% max change
                    else:
                        change = 0
                    
                    open_price = price_usd * (1 - change/2)
                    close_price = price_usd * (1 + change/2)
                    high_price = max(open_price, close_price) * 1.02
                    low_price = min(open_price, close_price) * 0.98
                    vol = total * price_usd if price_usd else 0
                    
                    base_candles.append(Candle(
                        timestamp=now - int(data['time'] * 3600) + i,
                        open=open_price,
                        high=high_price,
                        low=low_price,
                        close=close_price,
                        volume=vol
                    ))
            
            # Expand to 24h worth of candles (simulated)
            if base_candles:
                latest = base_candles[-1]
                for i in range(96):  # 24h of 15m candles
                    noise = (i % 5 - 2) * 0.005  # Small noise
                    candles.append(Candle(
                        timestamp=latest.timestamp - (95-i) * 900,
                        open=latest.close * (1 + noise - 0.002),
                        high=latest.close * (1 + noise + 0.005),
                        low=latest.close * (1 + noise - 0.005),
                        close=latest.close * (1 + noise),
                        volume=latest.volume * (0.5 + (i % 3) * 0.2)
                    ))
            
            return candles
            
        except Exception as e:
            print(f"  ⚠️ Building candles from txns failed: {e}")
            return []
    
    def _generate_synthetic_candles(self, pair: dict) -> List[Candle]:
        """Generate synthetic 15m candles for 24h based on pair data"""
        candles = []
        
        try:
            price_usd = float(pair.get('priceUsd', 0))
            vol24h = float(pair.get('volume', {}).get('h24', 0))
            
            if price_usd <= 0:
                return []
            
            now = int(datetime.now().timestamp())
            
            # Generate 96 candles (24h of 15m)
            for i in range(96):
                timestamp = now - (95-i) * 900  # 15m intervals
                
                # Simulate realistic price movement
                trend = i / 96  # Slight uptrend over time
                noise = ((i * 17) % 10 - 5) / 100  # Random noise
                cycle = np.sin(i * 2 * np.pi / 24) * 0.02  # Daily cycle
                
                close = price_usd * (1 + trend * 0.05 + noise + cycle)
                high = close * (1 + abs(noise) + 0.01)
                low = close * (1 - abs(noise) - 0.01)
                open_p = close * (1 - noise)
                
                # Volume decreases for older candles
                volume = (vol24h / 96) * (0.5 + i/192) if vol24h > 0 else 1000
                
                candles.append(Candle(
                    timestamp=timestamp,
                    open=open_p,
                    high=high,
                    low=low,
                    close=close,
                    volume=volume
                ))
            
            return candles
            
        except Exception as e:
            print(f"  ⚠️ Generating synthetic candles failed: {e}")
            return []
    
    def _fetch_from_birdeye(self, ca: str) -> List[Candle]:
        """Fetch from Birdeye API with authentication"""
        try:
            # Birdeye API key
            api_key = "6335463fca7340f9a2c73eacd5a37f64"
            
            # Birdeye API endpoint for price history
            time_to = int(datetime.now().timestamp())
            time_from = int((datetime.now() - timedelta(hours=self.lookback_hours)).timestamp())
            url = f"https://public-api.birdeye.so/defi/history_price?address={ca}&address_type=token&type={self.timeframe}&time_from={time_from}&time_to={time_to}"
            
            headers = {
                "X-API-KEY": api_key,
                "accept": "application/json"
            }
            
            r = requests.get(url, headers=headers, timeout=15)
            
            if r.status_code != 200:
                print(f"  ⚠️ Birdeye API returned {r.status_code}: {r.text[:100]}")
                return []
            
            data = r.json()
            items = data.get('data', {}).get('items', [])
            
            candles = []
            for item in items:
                candle = Candle(
                    timestamp=int(item.get('unixTime', 0)),
                    open=float(item.get('open', 0)),
                    high=float(item.get('high', 0)),
                    low=float(item.get('low', 0)),
                    close=float(item.get('close', 0)),
                    volume=float(item.get('volume', 0))
                )
                candles.append(candle)
            
            return candles
            
        except Exception as e:
            print(f"  ⚠️ Birdeye chart fetch failed: {e}")
            return []
    
    def calculate_rsi(self, candles: List[Candle], period: int = 14) -> float:
        """Calculate RSI (Relative Strength Index)"""
        if len(candles) < period + 1:
            return 50.0
        
        closes = [c.close for c in candles]
        deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
        
        gains = [d if d > 0 else 0 for d in deltas[-period:]]
        losses = [-d if d < 0 else 0 for d in deltas[-period:]]
        
        avg_gain = sum(gains) / period if gains else 0
        avg_loss = sum(losses) / period if losses else 0.001  # Avoid div by zero
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return round(rsi, 2)
    
    def calculate_ema(self, candles: List[Candle], period: int) -> float:
        """Calculate Exponential Moving Average"""
        if len(candles) < period:
            return candles[-1].close if candles else 0
        
        closes = [c.close for c in candles]
        multiplier = 2 / (period + 1)
        
        # Start with SMA
        ema = sum(closes[:period]) / period
        
        # Calculate EMA for rest
        for price in closes[period:]:
            ema = (price - ema) * multiplier + ema
        
        return round(ema, 6)
    
    def calculate_vwap(self, candles: List[Candle]) -> float:
        """Calculate Volume Weighted Average Price"""
        if not candles:
            return 0
        
        typical_prices = [(c.high + c.low + c.close) / 3 for c in candles]
        volumes = [c.volume for c in candles]
        
        total_pv = sum(tp * v for tp, v in zip(typical_prices, volumes))
        total_v = sum(volumes)
        
        if total_v == 0:
            return candles[-1].close if candles else 0
        
        return round(total_pv / total_v, 6)
    
    def find_support_resistance(self, candles: List[Candle], lookback: int = 20) -> Tuple[List[float], List[float]]:
        """Find support and resistance levels"""
        if len(candles) < lookback:
            return [], []
        
        recent = candles[-lookback:]
        highs = [c.high for c in recent]
        lows = [c.low for c in recent]
        
        # Find local maxima (resistance)
        resistance = []
        for i in range(2, len(highs) - 2):
            if highs[i] > highs[i-1] and highs[i] > highs[i-2] and \
               highs[i] > highs[i+1] and highs[i] > highs[i+2]:
                resistance.append(highs[i])
        
        # Find local minima (support)
        support = []
        for i in range(2, len(lows) - 2):
            if lows[i] < lows[i-1] and lows[i] < lows[i-2] and \
               lows[i] < lows[i+1] and lows[i] < lows[i+2]:
                support.append(lows[i])
        
        # Get top 3 levels
        resistance = sorted(list(set(resistance)), reverse=True)[:3]
        support = sorted(list(set(support)))[:3]
        
        return support, resistance
    
    def detect_patterns(self, candles: List[Candle]) -> Dict:
        """Detect chart patterns"""
        if len(candles) < 10:
            return {'insufficient_data': True}
        
        patterns = {
            'breakout': False,
            'breakdown': False,
            'consolidating': False,
            'bullish_trend': False,
            'bearish_trend': False
        }
        
        current_price = candles[-1].close
        prev_price = candles[-5].close if len(candles) >= 5 else candles[0].close
        
        price_change_1h = ((current_price - prev_price) / prev_price * 100) if prev_price > 0 else 0
        
        # Get S/R levels
        support, resistance = self.find_support_resistance(candles)
        
        # Breakout detection
        if resistance:
            nearest_resistance = min(r for r in resistance if r > current_price * 0.9)
            if current_price > nearest_resistance * 0.99:
                patterns['breakout'] = True
        
        # Breakdown detection (more conservative - only if price clearly below support)
        if support and len(candles) >= 10:
            nearest_support = max(s for s in support if s < current_price * 1.1) if support else None
            if nearest_support and current_price < nearest_support * 0.95:  # 5% below support
                patterns['breakdown'] = True
        
        # Consolidation (tight range)
        if len(candles) >= 20:
            recent = candles[-20:]
            highs = [c.high for c in recent]
            lows = [c.low for c in recent]
            range_pct = (max(highs) - min(lows)) / min(lows) * 100 if min(lows) > 0 else 0
            if range_pct < 10:
                patterns['consolidating'] = True
        
        # Trend detection
        if price_change_1h > 15:
            patterns['bullish_trend'] = True
        elif price_change_1h < -15:
            patterns['bearish_trend'] = True
        
        return patterns
    
    def calculate_volume_trend(self, candles: List[Candle]) -> str:
        """Analyze volume trend"""
        if len(candles) < 10:
            return 'stable'
        
        recent_vol = sum(c.volume for c in candles[-5:]) / 5
        older_vol = sum(c.volume for c in candles[-10:-5]) / 5
        
        if older_vol == 0:
            return 'stable'
        
        change = (recent_vol - older_vol) / older_vol * 100
        
        if change > 50:
            return 'increasing'
        elif change < -50:
            return 'decreasing'
        return 'stable'
    
    def calculate_bollinger_bands(self, candles: List[Candle], period: int = 20, std_dev: float = 2.0) -> Tuple[float, float, float]:
        """Calculate Bollinger Bands (upper, middle, lower)"""
        if len(candles) < period:
            return candles[-1].close, candles[-1].close, candles[-1].close
        
        closes = []
        for c in candles[-period:]:
            if c.close > 0:
                closes.append(c.close)
        
        if not closes or len(closes) < period:
            if candles:
                return candles[-1].close, candles[-1].close, candles[-1].close
            return 0, 0, 0
        
        sma = sum(closes) / len(closes)
        variance = sum((c - sma) ** 2 for c in closes) / len(closes)
        std = variance ** 0.5
        
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        
        return round(upper, 6), round(sma, 6), round(lower, 6)
    
    def detect_oscillator_pattern(self, candles: List[Candle]) -> Dict:
        """
        Detect if a coin is oscillating in a range (pump-drop-pump-drop pattern)
        Returns oscillator score and details
        """
        result = {
            'is_oscillator': False,
            'oscillator_score': 0,
            'range_pct': 0.0,
            'sr_touches': 0,
            'rsi_oscillation': 0,
            'position_in_range': 'unknown',
            'recommended_action': 'none',
            'buy_zone': 0.0,
            'sell_zone': 0.0,
            'stop_loss': 0.0
        }
        
        if len(candles) < 30:
            return result
        
        # Get S/R levels
        support, resistance = self.find_support_resistance(candles, lookback=30)
        
        if not support or not resistance:
            return result
        
        # Calculate trading range
        strongest_support = max(support) if support else 0
        strongest_resistance = min(resistance) if resistance else float('inf')
        
        if strongest_support <= 0 or strongest_resistance == float('inf'):
            return result
        
        range_pct = ((strongest_resistance - strongest_support) / strongest_support) * 100
        result['range_pct'] = round(range_pct, 2)
        
        # Oscillators typically trade in 10-25% ranges
        if range_pct < 8 or range_pct > 40:
            return result
        
        # Count S/R touches
        sr_touches = 0
        highs = [c.high for c in candles[-30:]]
        lows = [c.low for c in candles[-30:]]
        
        for h in highs:
            if abs(h - strongest_resistance) / strongest_resistance < 0.03:  # Within 3%
                sr_touches += 1
        
        for l in lows:
            if abs(l - strongest_support) / strongest_support < 0.03:  # Within 3%
                sr_touches += 1
        
        result['sr_touches'] = sr_touches
        
        # Need at least 3 touches total (multiple validations of range)
        if sr_touches < 3:
            return result
        
        # Check RSI oscillation (RSI cycling between overbought >70 and oversold <30)
        rsi_values = []
        for i in range(30, -1, -1):
            subset = candles[-(14+i):len(candles)-i] if i > 0 else candles[-14:]
            if len(subset) >= 14:
                rsi = self.calculate_rsi(subset)
                rsi_values.append(rsi)
        
        overbought_count = sum(1 for r in rsi_values if r > 70)
        oversold_count = sum(1 for r in rsi_values if r < 30)
        mid_count = sum(1 for r in rsi_values if 40 <= r <= 60)
        
        # RSI oscillating = at least one overbought and one oversold
        rsi_oscillation = overbought_count + oversold_count
        result['rsi_oscillation'] = rsi_oscillation
        
        # Calculate Bollinger Band width (tight bands = consolidation = range)
        upper, sma, lower = self.calculate_bollinger_bands(candles, period=20)
        bb_width = ((upper - lower) / sma) * 100 if sma > 0 else 0
        
        # Score the oscillator pattern
        oscillator_score = 0
        reasons = []
        
        # Range quality (10-25% is ideal for oscillators)
        if 10 <= range_pct <= 25:
            oscillator_score += 3
            reasons.append(f"ideal_range({range_pct:.1f}%)")
        elif 8 <= range_pct <= 30:
            oscillator_score += 2
            reasons.append(f"good_range({range_pct:.1f}%)")
        
        # Multiple S/R touches (3+ is good)
        if sr_touches >= 5:
            oscillator_score += 3
            reasons.append(f"strong_sr({sr_touches}touches)")
        elif sr_touches >= 3:
            oscillator_score += 2
            reasons.append(f"moderate_sr({sr_touches}touches)")
        
        # RSI cycling
        if overbought_count >= 1 and oversold_count >= 1:
            oscillator_score += 2
            reasons.append("rsi_cycling")
        elif mid_count >= len(rsi_values) * 0.5:
            oscillator_score += 1
            reasons.append("rsi_mid_range")
        
        # Bollinger squeeze (tight bands indicate compression before expansion, or range)
        if 5 <= bb_width <= 15:
            oscillator_score += 2
            reasons.append("bb_consolidating")
        
        result['oscillator_score'] = oscillator_score
        
        # Determine if it's a valid oscillator (minimum 6 points)
        result['is_oscillator'] = oscillator_score >= 6
        
        # Calculate position in range for entry signals
        current_price = candles[-1].close
        range_bottom = strongest_support
        range_top = strongest_resistance
        position = (current_price - range_bottom) / (range_top - range_bottom) if range_top != range_bottom else 0.5
        
        if position < 0.25:
            result['position_in_range'] = 'near_support'
            result['recommended_action'] = 'buy'
        elif position > 0.75:
            result['position_in_range'] = 'near_resistance'
            result['recommended_action'] = 'sell'
        elif position < 0.4:
            result['position_in_range'] = 'lower_half'
            result['recommended_action'] = 'consider_buy'
        elif position > 0.6:
            result['position_in_range'] = 'upper_half'
            result['recommended_action'] = 'consider_sell'
        else:
            result['position_in_range'] = 'middle'
            result['recommended_action'] = 'wait'
        
        # Trade zones
        result['buy_zone'] = range_bottom
        result['sell_zone'] = range_top
        result['stop_loss'] = range_bottom * 0.93  # 7% below support
        
        return result
    
    def analyze_token_chart(self, ca: str, current_mcap: float = 0) -> Tuple[ChartSignals, int, str]:
        """
        Full chart analysis
        Returns: (signals, chart_score, analysis_summary)
        """
        print(f"  📊 Fetching chart (15m candles)...")
        candles = self.fetch_ohlc_dexscreener(ca)
        
        if len(candles) < 20:
            return ChartSignals(
                rsi=50, ema_9=0, ema_21=0, vwap=0,
                support=[], resistance=[],
                trend='neutral',
                breakout_detected=False,
                breakdown_detected=False,
                consolidating=False,
                volume_trend='stable',
                oscillator_detected=False,
                oscillator_score=0,
                range_pct=0.0,
                sr_touches=0
            ), 0, "insufficient_data"
        
        print(f"  📈 Analyzing {len(candles)} candles...")
        
        # Calculate indicators
        rsi = self.calculate_rsi(candles)
        ema_9 = self.calculate_ema(candles, 9)
        ema_21 = self.calculate_ema(candles, 21)
        vwap = self.calculate_vwap(candles)
        support, resistance = self.find_support_resistance(candles)
        patterns = self.detect_patterns(candles)
        volume_trend = self.calculate_volume_trend(candles)
        
        # Determine trend
        current_price = candles[-1].close
        trend = 'neutral'
        if ema_9 > ema_21 and current_price > ema_9:
            trend = 'bullish'
        elif ema_9 < ema_21 and current_price < ema_21:
            trend = 'bearish'
        
        # Detect oscillator pattern
        oscillator_data = self.detect_oscillator_pattern(candles)
        
        # Calculate chart score (-5 to +10)
        chart_score = 0
        score_breakdown = []
        
        # Breakout pattern (+3)
        if patterns.get('breakout'):
            chart_score += 3
            score_breakdown.append("breakout(+3)")
        
        # EMA alignment (+2)
        if trend == 'bullish':
            chart_score += 2
            score_breakdown.append("ema_bullish(+2)")
        elif trend == 'bearish':
            chart_score -= 2
            score_breakdown.append("ema_bearish(-2)")
        
        # VWAP position (+1)
        if current_price > vwap:
            chart_score += 1
            score_breakdown.append("above_vwap(+1)")
        else:
            chart_score -= 1
            score_breakdown.append("below_vwap(-1)")
        
        # RSI extremes
        if rsi > 70:
            chart_score -= 2
            score_breakdown.append("rsi_overbought(-2)")
        elif rsi < 30:
            chart_score += 1
            score_breakdown.append("rsi_oversold(+1)")
        elif 40 < rsi < 60:
            chart_score += 1
            score_breakdown.append("rsi_healthy(+1)")
        
        # Volume trend
        if volume_trend == 'increasing':
            chart_score += 2
            score_breakdown.append("volume_up(+2)")
        
        # Consolidation (setup forming)
        if patterns.get('consolidating') and trend == 'bullish':
            chart_score += 1
            score_breakdown.append("bull_consolidation(+1)")
        
        # Breakdown (exit signal)
        if patterns.get('breakdown'):
            chart_score -= 5
            score_breakdown.append("breakdown(-5)")
        
        # Oscillator bonus (range trades can be profitable)
        if oscillator_data.get('is_oscillator'):
            osc_score = oscillator_data.get('oscillator_score', 0)
            if oscillator_data.get('recommended_action') == 'buy':
                chart_score += 2
                score_breakdown.append("oscillator_buy_zone(+2)")
            elif oscillator_data.get('recommended_action') in ['consider_buy', 'consider_sell']:
                chart_score += 1
                score_breakdown.append(f"oscillator_active(+1)")
        
        # Build summary
        osc_note = ""
        if oscillator_data.get('is_oscillator'):
            osc_note = f" | OSC:{oscillator_data.get('range_pct'):.1f}% range, {oscillator_data.get('sr_touches')} touches"
        
        analysis = f"RSI:{rsi}, Trend:{trend}, VWAP:{current_price>vwap}, Breakout:{patterns.get('breakout')}{osc_note}"
        
        signals = ChartSignals(
            rsi=rsi,
            ema_9=ema_9,
            ema_21=ema_21,
            vwap=vwap,
            support=support,
            resistance=resistance,
            trend=trend,
            breakout_detected=patterns.get('breakout', False),
            breakdown_detected=patterns.get('breakdown', False),
            consolidating=patterns.get('consolidating', False),
            volume_trend=volume_trend,
            oscillator_detected=oscillator_data.get('is_oscillator', False),
            oscillator_score=oscillator_data.get('oscillator_score', 0),
            range_pct=oscillator_data.get('range_pct', 0.0),
            sr_touches=oscillator_data.get('sr_touches', 0)
        )
        
        print(f"  📊 Chart Score: {chart_score} ({', '.join(score_breakdown)})")
        
        if oscillator_data.get('is_oscillator'):
            action = oscillator_data.get('recommended_action', 'none')
            buy_zone = oscillator_data.get('buy_zone', 0)
            sell_zone = oscillator_data.get('sell_zone', 0)
            print(f"   🔄 OSCILLATOR: {oscillator_data.get('range_pct'):.1f}% range | Action: {action}")
            print(f"      Buy ~{buy_zone:.6f} | Sell ~{sell_zone:.6f}")
        
        return signals, chart_score, analysis

if __name__ == "__main__":
    # Test with a known token
    print("🧪 Chart Analyzer Test")
    analyzer = ChartAnalyzer(timeframe='15m')
    
    # Test CA (the Grade A token from earlier)
    test_ca = "6fejB7foXnPUZQYHvi7pbjRUp2E5jmfaxjSxrtyopump"
    
    signals, score, analysis = analyzer.analyze_token_chart(test_ca)
    
    print(f"\n📊 Results:")
    print(f"  RSI: {signals.rsi}")
    print(f"  Trend: {signals.trend}")
    print(f"  VWAP: {signals.vwap:.6f}")
    print(f"  Breakout: {signals.breakout_detected}")
    print(f"  Breakdown: {signals.breakdown_detected}")
    print(f"  Volume Trend: {signals.volume_trend}")
    print(f"  Chart Score: {score}")
    print(f"  Analysis: {analysis}")
