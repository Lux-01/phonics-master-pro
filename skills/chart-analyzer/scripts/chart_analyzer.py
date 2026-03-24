#!/usr/bin/env python3
"""
Chart Analyzer - Technical Analysis for Chart Images
Analyzes trading charts for patterns, indicators, and signals
"""

import numpy as np
import cv2
from PIL import Image
from scipy.signal import argrelextrema
from scipy.ndimage import gaussian_filter1d
from scipy.stats import linregress
from typing import Dict, List, Optional, Tuple
import json


class ChartAnalyzer:
    """Main chart analysis class"""
    
    def __init__(self):
        self.patterns_found = []
        self.signals = []
        
    def analyze_image(self, image_path: str) -> Dict:
        """
        Analyze a chart image and return comprehensive results
        
        Args:
            image_path: Path to chart image file
            
        Returns:
            Dictionary with patterns, indicators, and signals
        """
        # Load image
        image = Image.open(image_path)
        img_array = np.array(image)
        
        # Extract price data
        prices = self._extract_price_data(img_array)
        
        if prices is None or len(prices) < 20:
            return {
                'error': 'Could not extract price data from image',
                'patterns': [],
                'indicators': {},
                'signals': []
            }
        
        # Run analysis
        results = {
            'patterns': self._detect_patterns(prices),
            'support_resistance': self._calculate_support_resistance(prices),
            'indicators': self._calculate_indicators(prices),
            'fibonacci': self._calculate_fibonacci(prices),
            'price_data': {
                'current': float(prices[-1]),
                'high': float(np.max(prices)),
                'low': float(np.min(prices)),
                'range': float(np.max(prices) - np.min(prices))
            }
        }
        
        # Generate trading signals
        results['signals'] = self._generate_signals(results)
        
        return results
    
    def _extract_price_data(self, img_array: np.ndarray) -> Optional[np.ndarray]:
        """Extract price line from chart image"""
        try:
            # Convert to grayscale
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # Enhance contrast
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(gray)
            
            # Edge detection
            edges = cv2.Canny(enhanced, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return None
            
            # Get main price line (largest contour)
            main_contour = max(contours, key=cv2.contourArea)
            points = main_contour.reshape(-1, 2)
            
            # Extract price levels
            x_coords = np.unique(points[:, 0])
            prices = []
            
            for x in x_coords:
                y_vals = points[points[:, 0] == x, 1]
                if len(y_vals) > 0:
                    # Use median to reduce noise
                    prices.append(np.median(y_vals))
            
            return np.array(prices) if len(prices) > 20 else None
            
        except Exception as e:
            print(f"Error extracting price data: {e}")
            return None
    
    def _detect_patterns(self, prices: np.ndarray) -> List[Dict]:
        """Detect chart patterns"""
        patterns = []
        
        # Double Bottom
        db = self._detect_double_bottom(prices)
        if db:
            patterns.append(db)
        
        # Cup and Handle
        cah = self._detect_cup_and_handle(prices)
        if cah:
            patterns.append(cah)
        
        # Head and Shoulders
        hs = self._detect_head_and_shoulders(prices)
        if hs:
            patterns.append(hs)
        
        # Triangles
        tri = self._detect_triangles(prices)
        if tri:
            patterns.append(tri)
        
        return patterns
    
    def _detect_double_bottom(self, prices: np.ndarray) -> Optional[Dict]:
        """Detect Double Bottom (W) pattern"""
        if len(prices) < 30:
            return None
        
        minima = argrelextrema(prices, np.less, order=10)[0]
        
        if len(minima) < 2:
            return None
        
        for i in range(len(minima) - 1):
            first_bottom = prices[minima[i]]
            second_bottom = prices[minima[i+1]]
            
            price_range = np.max(prices) - np.min(prices)
            if price_range == 0:
                continue
            
            diff = abs(first_bottom - second_bottom) / price_range
            
            if diff < 0.05:  # 5% tolerance
                middle = prices[minima[i]:minima[i+1]]
                if len(middle) == 0:
                    continue
                
                peak = np.max(middle)
                depth = (peak - first_bottom) / price_range
                
                if depth > 0.1:
                    pattern_height = peak - first_bottom
                    
                    return {
                        'type': 'Double Bottom',
                        'confidence': float(1 - diff),
                        'description': 'Bullish reversal pattern - W shape',
                        'entry': float(peak * 1.01),
                        'stop_loss': float(min(first_bottom, second_bottom) * 0.99),
                        'target': float(peak + pattern_height),
                        'risk_reward': float(pattern_height / (peak - min(first_bottom, second_bottom)))
                    }
        
        return None
    
    def _detect_cup_and_handle(self, prices: np.ndarray) -> Optional[Dict]:
        """Detect Cup and Handle pattern"""
        if len(prices) < 50:
            return None
        
        smoothed = gaussian_filter1d(prices, sigma=3)
        
        for i in range(30, len(smoothed) - 15):
            cup = smoothed[i-30:i]
            handle = smoothed[i:i+15]
            
            if len(cup) < 20 or len(handle) < 8:
                continue
            
            # Check for U shape
            left = cup[:len(cup)//2]
            right = cup[len(cup)//2:]
            
            if len(left) < 5 or len(right) < 5:
                continue
            
            left_slope = linregress(range(len(left)), left)[0]
            right_slope = linregress(range(len(right)), right)[0]
            
            if left_slope < -0.1 and right_slope > 0.1:
                cup_high = np.max(cup)
                cup_low = np.min(cup)
                handle_low = np.min(handle)
                
                if handle_low > cup_low + (cup_high - cup_low) * 0.3:
                    handle_depth = (np.max(handle) - handle_low) / (cup_high - cup_low)
                    
                    if handle_depth < 0.5:
                        return {
                            'type': 'Cup & Handle',
                            'confidence': float(0.7 + 0.3 * (1 - handle_depth)),
                            'description': 'Bullish continuation pattern',
                            'entry': float(cup_high * 1.02),
                            'stop_loss': float(handle_low * 0.98),
                            'target': float(cup_high + (cup_high - cup_low))
                        }
        
        return None
    
    def _detect_head_and_shoulders(self, prices: np.ndarray) -> Optional[Dict]:
        """Detect Head and Shoulders pattern"""
        if len(prices) < 60:
            return None
        
        peaks = argrelextrema(prices, np.greater, order=15)[0]
        
        if len(peaks) < 3:
            return None
        
        for i in range(len(peaks) - 2):
            left = prices[peaks[i]]
            head = prices[peaks[i+1]]
            right = prices[peaks[i+2]]
            
            if head > left and head > right:
                shoulder_diff = abs(left - right) / head
                
                if shoulder_diff < 0.1:
                    neckline = np.min(prices[peaks[i]:peaks[i+2]])
                    pattern_height = head - neckline
                    
                    return {
                        'type': 'Head & Shoulders',
                        'confidence': float(1 - shoulder_diff),
                        'description': 'Bearish reversal pattern',
                        'entry': float(neckline * 0.99),
                        'stop_loss': float(head * 1.01),
                        'target': float(neckline - pattern_height)
                    }
        
        return None
    
    def _detect_triangles(self, prices: np.ndarray) -> Optional[Dict]:
        """Detect triangle patterns"""
        if len(prices) < 40:
            return None
        
        recent = prices[-40:]
        highs = argrelextrema(recent, np.greater, order=5)[0]
        lows = argrelextrema(recent, np.less, order=5)[0]
        
        if len(highs) < 2 or len(lows) < 2:
            return None
        
        high_slope, _, _, _, _ = linregress(highs, recent[highs])
        low_slope, _, _, _, _ = linregress(lows, recent[lows])
        
        if abs(high_slope - low_slope) < 0.01:
            if high_slope < 0 and low_slope > 0:
                return {
                    'type': 'Symmetrical Triangle',
                    'confidence': 0.75,
                    'description': 'Consolidation - wait for breakout',
                    'breakout_up': float(recent[-1] * 1.05),
                    'breakout_down': float(recent[-1] * 0.95)
                }
            elif high_slope < 0.01 and low_slope > 0.01:
                return {
                    'type': 'Ascending Triangle',
                    'confidence': 0.8,
                    'description': 'Bullish - buy on resistance break',
                    'entry': float(np.max(recent[highs]) * 1.01),
                    'target': float(np.max(recent[highs]) + (np.max(recent[highs]) - np.min(recent[lows])))
                }
            elif high_slope < -0.01 and low_slope < 0.01:
                return {
                    'type': 'Descending Triangle',
                    'confidence': 0.8,
                    'description': 'Bearish - sell on support break',
                    'entry': float(np.min(recent[lows]) * 0.99),
                    'target': float(np.min(recent[lows]) - (np.max(recent[highs]) - np.min(recent[lows])))
                }
        
        return None
    
    def _calculate_support_resistance(self, prices: np.ndarray) -> Dict:
        """Calculate support and resistance levels"""
        if len(prices) < 20:
            return {'support': [], 'resistance': []}
        
        highs = argrelextrema(prices, np.greater, order=10)[0]
        lows = argrelextrema(prices, np.less, order=10)[0]
        
        support = []
        resistance = []
        
        # Group nearby levels
        if len(lows) > 0:
            low_prices = prices[lows]
            for price in np.unique(low_prices.round(0)):
                touches = np.sum(np.abs(low_prices - price) < 2)
                if touches >= 1:
                    support.append({
                        'price': float(price),
                        'touches': int(touches),
                        'strength': min(1.0, touches / 3)
                    })
        
        if len(highs) > 0:
            high_prices = prices[highs]
            for price in np.unique(high_prices.round(0)):
                touches = np.sum(np.abs(high_prices - price) < 2)
                if touches >= 1:
                    resistance.append({
                        'price': float(price),
                        'touches': int(touches),
                        'strength': min(1.0, touches / 3)
                    })
        
        return {
            'support': sorted(support, key=lambda x: x['strength'], reverse=True)[:3],
            'resistance': sorted(resistance, key=lambda x: x['strength'], reverse=True)[:3]
        }
    
    def _calculate_indicators(self, prices: np.ndarray) -> Dict:
        """Calculate technical indicators"""
        indicators = {}
        
        # RSI
        if len(prices) > 14:
            deltas = np.diff(prices)
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)
            avg_gain = np.mean(gains[-14:])
            avg_loss = np.mean(losses[-14:])
            
            if avg_loss > 0:
                rs = avg_gain / avg_loss
                indicators['rsi'] = float(100 - (100 / (1 + rs)))
            else:
                indicators['rsi'] = 100
        
        # Trend
        if len(prices) > 20:
            first = np.mean(prices[:len(prices)//2])
            second = np.mean(prices[len(prices)//2:])
            diff = (second - first) / first
            
            if diff > 0.02:
                indicators['trend'] = {'direction': 'bullish', 'strength': min(1.0, diff * 10)}
            elif diff < -0.02:
                indicators['trend'] = {'direction': 'bearish', 'strength': min(1.0, abs(diff) * 10)}
            else:
                indicators['trend'] = {'direction': 'neutral', 'strength': 0}
        
        return indicators
    
    def _calculate_fibonacci(self, prices: np.ndarray) -> Dict:
        """Calculate Fibonacci retracement levels"""
        high = np.max(prices)
        low = np.min(prices)
        diff = high - low
        
        return {
            '0.0': float(high),
            '0.236': float(high - 0.236 * diff),
            '0.382': float(high - 0.382 * diff),
            '0.5': float(high - 0.5 * diff),
            '0.618': float(high - 0.618 * diff),
            '0.786': float(high - 0.786 * diff),
            '1.0': float(low)
        }
    
    def _generate_signals(self, analysis: Dict) -> List[Dict]:
        """Generate trading signals"""
        signals = []
        
        # Pattern-based signals
        for pattern in analysis.get('patterns', []):
            if pattern['confidence'] > 0.7:
                action = 'buy' if pattern['type'] in ['Double Bottom', 'Cup & Handle', 'Ascending Triangle'] else 'sell'
                
                signals.append({
                    'type': pattern['type'],
                    'action': action,
                    'confidence': pattern['confidence'],
                    'entry': pattern.get('entry'),
                    'stop_loss': pattern.get('stop_loss'),
                    'target': pattern.get('target'),
                    'description': pattern.get('description', '')
                })
        
        # RSI signals
        rsi = analysis.get('indicators', {}).get('rsi')
        if rsi:
            if rsi < 30:
                signals.append({
                    'type': 'RSI Oversold',
                    'action': 'buy',
                    'confidence': 0.6,
                    'description': f'RSI at {rsi:.1f}'
                })
            elif rsi > 70:
                signals.append({
                    'type': 'RSI Overbought',
                    'action': 'sell',
                    'confidence': 0.6,
                    'description': f'RSI at {rsi:.1f}'
                })
        
        return signals


def format_results(results: Dict) -> str:
    """Format analysis results as readable text"""
    text = "📊 CHART ANALYSIS RESULTS\n"
    text += "=" * 50 + "\n\n"
    
    # Price info
    if 'price_data' in results:
        pd = results['price_data']
        text += f"💰 Price: {pd['current']:.2f}\n"
        text += f"   High: {pd['high']:.2f} | Low: {pd['low']:.2f}\n"
        text += f"   Range: {pd['range']:.2f}\n\n"
    
    # Patterns
    if results.get('patterns'):
        text += "🔍 PATTERNS DETECTED:\n"
        for p in results['patterns']:
            text += f"\n  • {p['type']} ({p['confidence']*100:.0f}% confidence)\n"
            text += f"    {p['description']}\n"
            if 'entry' in p:
                text += f"    Entry: {p['entry']:.2f}\n"
            if 'stop_loss' in p:
                text += f"    Stop: {p['stop_loss']:.2f}\n"
            if 'target' in p:
                text += f"    Target: {p['target']:.2f}\n"
            if 'risk_reward' in p:
                text += f"    R:R = 1:{p['risk_reward']:.1f}\n"
    else:
        text += "🔍 No clear patterns detected\n"
    
    text += "\n"
    
    # Support/Resistance
    sr = results.get('support_resistance', {})
    if sr.get('support') or sr.get('resistance'):
        text += "📊 SUPPORT/RESISTANCE:\n"
        for s in sr.get('support', []):
            text += f"  S: {s['price']:.2f} ({s['touches']} touches)\n"
        for r in sr.get('resistance', []):
            text += f"  R: {r['price']:.2f} ({r['touches']} touches)\n"
        text += "\n"
    
    # Indicators
    ind = results.get('indicators', {})
    if ind:
        text += "📈 INDICATORS:\n"
        if 'rsi' in ind:
            rsi = ind['rsi']
            status = "oversold" if rsi < 30 else "overbought" if rsi > 70 else "neutral"
            text += f"  RSI: {rsi:.1f} ({status})\n"
        if 'trend' in ind:
            t = ind['trend']
            text += f"  Trend: {t['direction'].upper()} ({t['strength']*100:.0f}% strength)\n"
        text += "\n"
    
    # Signals
    if results.get('signals'):
        text += "💡 TRADING SIGNALS:\n"
        for s in results['signals']:
            emoji = "🟢" if s['action'] == 'buy' else "🔴"
            text += f"\n  {emoji} {s['type']}\n"
            text += f"     Action: {s['action'].upper()}\n"
            text += f"     Confidence: {s['confidence']*100:.0f}%\n"
            if 'entry' in s and s['entry']:
                text += f"     Entry: {s['entry']:.2f}\n"
            if 'stop_loss' in s and s['stop_loss']:
                text += f"     Stop: {s['stop_loss']:.2f}\n"
            if 'target' in s and s['target']:
                text += f"     Target: {s['target']:.2f}\n"
    
    text += "\n" + "=" * 50 + "\n"
    text += "⚠️ Not financial advice - DYOR\n"
    
    return text


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python chart_analyzer.py <image_path>")
        sys.exit(1)
    
    analyzer = ChartAnalyzer()
    results = analyzer.analyze_image(sys.argv[1])
    
    if 'error' in results:
        print(f"Error: {results['error']}")
    else:
        print(format_results(results))
        
        # Also save as JSON
        output_file = sys.argv[1].rsplit('.', 1)[0] + '_analysis.json'
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nDetailed results saved to: {output_file}")
