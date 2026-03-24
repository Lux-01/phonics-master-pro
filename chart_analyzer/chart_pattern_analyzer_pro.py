#!/usr/bin/env python3
"""
Chart Pattern Analyzer Pro v2.0 - Enhanced Edition
Advanced technical analysis for any on-screen chart
"""

import sys
import numpy as np
import cv2
from PIL import Image, ImageGrab, ImageDraw, ImageFont
import pyautogui
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QComboBox,
                             QSpinBox, QCheckBox, QTextEdit, QGroupBox,
                             QSystemTrayIcon, QMenu, QAction, QTabWidget,
                             QProgressBar, QSplitter, QListWidget, QFrame,
                             QFileDialog, QMessageBox, QSlider, QGridLayout,
                             QScrollArea, QDialog, QLineEdit)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, QPoint, QRect
from PyQt5.QtGui import QIcon, QPixmap, QImage, QPainter, QPen, QColor, QFont
import json
import time
from datetime import datetime, timedelta
from scipy.signal import find_peaks, argrelextrema
from scipy.ndimage import gaussian_filter1d, median_filter
from scipy.stats import linregress
from collections import deque
import warnings
warnings.filterwarnings('ignore')


class AdvancedPatternDetector:
    """Advanced pattern detection algorithms"""
    
    def __init__(self):
        self.price_history = deque(maxlen=1000)
        self.pattern_history = []
        
    def extract_price_from_image(self, image):
        """Extract price data from chart image using edge detection and OCR-like analysis"""
        img_array = np.array(image)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Enhance contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # Edge detection to find price line
        edges = cv2.Canny(enhanced, 50, 150)
        
        # Find contours (price line)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return None
            
        # Get the main price line (largest contour)
        main_contour = max(contours, key=cv2.contourArea)
        
        # Extract y-coordinates (price levels)
        points = main_contour.reshape(-1, 2)
        
        # Sort by x-coordinate and get unique x positions
        x_coords = np.unique(points[:, 0])
        prices = []
        
        for x in x_coords:
            # Get all y values at this x position
            y_vals = points[points[:, 0] == x, 1]
            if len(y_vals) > 0:
                # Use median to reduce noise
                prices.append(np.median(y_vals))
                
        return np.array(prices) if prices else None
        
    def detect_double_bottom(self, prices, min_separation=10, tolerance=0.05):
        """
        Detect Double Bottom pattern (W shape)
        Returns: dict with confidence, entry, stop_loss, target
        """
        if prices is None or len(prices) < 50:
            return None
            
        # Find local minima
        minima = argrelextrema(prices, np.less, order=min_separation)[0]
        
        if len(minima) < 2:
            return None
            
        patterns = []
        
        for i in range(len(minima) - 1):
            first_bottom = prices[minima[i]]
            second_bottom = prices[minima[i+1]]
            
            # Check if bottoms are at similar levels (within tolerance)
            price_range = np.max(prices) - np.min(prices)
            if price_range == 0:
                continue
                
            diff = abs(first_bottom - second_bottom) / price_range
            
            if diff < tolerance:
                # Check for peak between bottoms (neckline)
                middle_section = prices[minima[i]:minima[i+1]]
                if len(middle_section) == 0:
                    continue
                    
                peak = np.max(middle_section)
                
                # Calculate pattern quality
                bottom_depth = (peak - first_bottom) / price_range
                
                if bottom_depth > 0.1:  # Minimum 10% depth
                    # Find neckline (resistance level)
                    neckline = peak
                    
                    # Calculate targets
                    pattern_height = neckline - first_bottom
                    
                    patterns.append({
                        'type': 'Double Bottom',
                        'confidence': 1 - diff,
                        'first_bottom_idx': int(minima[i]),
                        'second_bottom_idx': int(minima[i+1]),
                        'neckline': float(neckline),
                        'entry': float(neckline * 1.01),  # Break above neckline
                        'stop_loss': float(min(first_bottom, second_bottom) * 0.99),
                        'target': float(neckline + pattern_height),
                        'risk_reward': (pattern_height) / (neckline - min(first_bottom, second_bottom)),
                        'description': f'W pattern detected. Entry on neckline break. R:R = {((pattern_height) / (neckline - min(first_bottom, second_bottom))):.2f}'
                    })
                    
        return patterns[0] if patterns else None
        
    def detect_cup_and_handle(self, prices, min_cup_width=30):
        """
        Detect Cup and Handle pattern
        U-shape followed by small consolidation/pullback
        """
        if prices is None or len(prices) < min_cup_width * 2:
            return None
            
        # Smooth prices
        smoothed = gaussian_filter1d(prices, sigma=3)
        
        # Find the cup (U shape)
        patterns = []
        
        for i in range(min_cup_width, len(smoothed) - min_cup_width):
            cup_section = smoothed[i-min_cup_width:i]
            handle_section = smoothed[i:i+min_cup_width//3]
            
            if len(cup_section) < 10 or len(handle_section) < 5:
                continue
                
            # Check for U shape in cup section
            left_side = cup_section[:len(cup_section)//2]
            right_side = cup_section[len(cup_section)//2:]
            
            if len(left_side) < 3 or len(right_side) < 3:
                continue
                
            # Cup should be curved (decreasing then increasing)
            left_trend = linregress(range(len(left_side)), left_side)[0]
            right_trend = linregress(range(len(right_side)), right_side)[0]
            
            if left_trend < -0.1 and right_trend > 0.1:
                # Check for handle (slight pullback/consolidation)
                handle_high = np.max(handle_section)
                handle_low = np.min(handle_section)
                cup_high = np.max(cup_section)
                cup_low = np.min(cup_section)
                
                # Handle should be in upper half of cup
                if handle_low > cup_low + (cup_high - cup_low) * 0.3:
                    # Handle depth should be shallow
                    handle_depth = (handle_high - handle_low) / (cup_high - cup_low)
                    
                    if handle_depth < 0.5:  # Handle less than 50% of cup depth
                        patterns.append({
                            'type': 'Cup & Handle',
                            'confidence': 0.7 + (0.3 * (1 - handle_depth)),
                            'cup_start': i - min_cup_width,
                            'cup_end': i,
                            'handle_end': i + len(handle_section),
                            'entry': float(cup_high * 1.02),
                            'stop_loss': float(handle_low * 0.98),
                            'target': float(cup_high + (cup_high - cup_low)),
                            'description': f'Cup depth: {((cup_high-cup_low)/cup_high)*100:.1f}%, Handle depth: {handle_depth*100:.1f}%'
                        })
                        
        return patterns[0] if patterns else None
        
    def detect_head_and_shoulders(self, prices, order=15):
        """
        Detect Head and Shoulders pattern (bearish reversal)
        """
        if prices is None or len(prices) < 60:
            return None
            
        # Find peaks (shoulders and head)
        peaks_idx = argrelextrema(prices, np.greater, order=order)[0]
        
        if len(peaks_idx) < 3:
            return None
            
        patterns = []
        
        for i in range(len(peaks_idx) - 2):
            left_shoulder = prices[peaks_idx[i]]
            head = prices[peaks_idx[i+1]]
            right_shoulder = prices[peaks_idx[i+2]]
            
            # Head should be higher than shoulders
            if head > left_shoulder and head > right_shoulder:
                # Shoulders should be at similar levels
                shoulder_diff = abs(left_shoulder - right_shoulder) / head
                
                if shoulder_diff < 0.1:  # Within 10%
                    # Find neckline (support between shoulders)
                    neckline_section = prices[peaks_idx[i]:peaks_idx[i+2]]
                    neckline = np.min(neckline_section)
                    
                    pattern_height = head - neckline
                    
                    patterns.append({
                        'type': 'Head & Shoulders',
                        'confidence': 1 - shoulder_diff,
                        'left_shoulder': int(peaks_idx[i]),
                        'head': int(peaks_idx[i+1]),
                        'right_shoulder': int(peaks_idx[i+2]),
                        'neckline': float(neckline),
                        'entry': float(neckline * 0.99),
                        'stop_loss': float(head * 1.01),
                        'target': float(neckline - pattern_height),
                        'description': f'Bearish reversal. Target: {((neckline - pattern_height)/neckline)*100:.1f}% below neckline'
                    })
                    
        return patterns[0] if patterns else None
        
    def detect_triangle_patterns(self, prices, lookback=50):
        """
        Detect Ascending, Descending, and Symmetrical Triangles
        """
        if prices is None or len(prices) < lookback:
            return None
            
        recent = prices[-lookback:]
        
        # Find highs and lows
        highs_idx = argrelextrema(recent, np.greater, order=5)[0]
        lows_idx = argrelextrema(recent, np.less, order=5)[0]
        
        if len(highs_idx) < 2 or len(lows_idx) < 2:
            return None
            
        # Fit trendlines
        high_slope, high_intercept, _, _, _ = linregress(highs_idx, recent[highs_idx])
        low_slope, low_intercept, _, _, _ = linregress(lows_idx, recent[lows_idx])
        
        patterns = []
        
        # Check convergence
        if abs(high_slope - low_slope) < 0.01:  # Nearly parallel
            if high_slope < 0 and low_slope > 0:
                patterns.append({
                    'type': 'Symmetrical Triangle',
                    'confidence': 0.75,
                    'description': 'Consolidation pattern. Breakout direction determines trade.',
                    'breakout_up_target': float(recent[-1] * 1.05),
                    'breakout_down_target': float(recent[-1] * 0.95)
                })
            elif high_slope < 0.01 and low_slope > 0.01:
                patterns.append({
                    'type': 'Ascending Triangle',
                    'confidence': 0.8,
                    'description': 'Bullish pattern. Buy on horizontal resistance break.',
                    'entry': float(np.max(recent[highs_idx]) * 1.01),
                    'target': float(np.max(recent[highs_idx]) + (np.max(recent[highs_idx]) - np.min(recent[lows_idx])))
                })
            elif high_slope < -0.01 and low_slope < 0.01:
                patterns.append({
                    'type': 'Descending Triangle',
                    'confidence': 0.8,
                    'description': 'Bearish pattern. Sell on horizontal support break.',
                    'entry': float(np.min(recent[lows_idx]) * 0.99),
                    'target': float(np.min(recent[lows_idx]) - (np.max(recent[highs_idx]) - np.min(recent[lows_idx])))
                })
                
        return patterns[0] if patterns else None
        
    def calculate_support_resistance(self, prices, window=20):
        """
        Calculate dynamic support and resistance levels
        """
        if prices is None or len(prices) < window * 2:
            return None
            
        # Find local extrema
        highs_idx = argrelextrema(prices, np.greater, order=window)[0]
        lows_idx = argrelextrema(prices, np.less, order=window)[0]
        
        if len(highs_idx) < 2 or len(lows_idx) < 2:
            return None
            
        highs = prices[highs_idx]
        lows = prices[lows_idx]
        
        # Cluster analysis for key levels
        from scipy.cluster.hierarchy import fclusterdata
        
        # Cluster resistance levels
        if len(highs) >= 2:
            high_clusters = fclusterdata(highs.reshape(-1, 1), t=0.02, criterion='distance')
            resistance_levels = []
            for cluster_id in np.unique(high_clusters):
                cluster_prices = highs[high_clusters == cluster_id]
                resistance_levels.append({
                    'price': float(np.mean(cluster_prices)),
                    'touches': int(np.sum(high_clusters == cluster_id)),
                    'strength': min(1.0, np.sum(high_clusters == cluster_id) / 3)
                })
        else:
            resistance_levels = []
            
        # Cluster support levels
        if len(lows) >= 2:
            low_clusters = fclusterdata(lows.reshape(-1, 1), t=0.02, criterion='distance')
            support_levels = []
            for cluster_id in np.unique(low_clusters):
                cluster_prices = lows[low_clusters == cluster_id]
                support_levels.append({
                    'price': float(np.mean(cluster_prices)),
                    'touches': int(np.sum(low_clusters == cluster_id)),
                    'strength': min(1.0, np.sum(low_clusters == cluster_id) / 3)
                })
        else:
            support_levels = []
            
        return {
            'support': sorted(support_levels, key=lambda x: x['strength'], reverse=True)[:3],
            'resistance': sorted(resistance_levels, key=lambda x: x['strength'], reverse=True)[:3]
        }
        
    def detect_liquidity_grabs(self, prices, wick_threshold=0.02):
        """
        Detect liquidity grab areas (wick spikes beyond S/R with quick reversal)
        """
        if prices is None or len(prices) < 20:
            return []
            
        grabs = []
        
        # Calculate volatility
        returns = np.diff(prices) / prices[:-1]
        volatility = np.std(returns)
        
        for i in range(5, len(prices) - 5):
            # Look for sharp moves followed by quick reversal
            local_range = prices[i-5:i+5]
            local_high = np.max(local_range)
            local_low = np.min(local_range)
            
            # Check for wick above/below with body reversal
            if prices[i] == local_high:
                # Potential liquidity grab above
                if prices[i+1] < prices[i] * (1 - wick_threshold):
                    grabs.append({
                        'type': 'liquidity_grab_high',
                        'index': i,
                        'price': float(prices[i]),
                        'description': 'Liquidity grab above resistance - bearish signal'
                    })
            elif prices[i] == local_low:
                # Potential liquidity grab below
                if prices[i+1] > prices[i] * (1 + wick_threshold):
                    grabs.append({
                        'type': 'liquidity_grab_low',
                        'index': i,
                        'price': float(prices[i]),
                        'description': 'Liquidity grab below support - bullish signal'
                    })
                    
        return grabs[-5:] if grabs else []  # Return last 5 grabs
        
    def calculate_fibonacci_levels(self, prices):
        """Calculate Fibonacci retracement levels"""
        if prices is None or len(prices) < 10:
            return None
            
        high = np.max(prices)
        low = np.min(prices)
        diff = high - low
        
        levels = {
            '0.0': float(high),
            '0.236': float(high - 0.236 * diff),
            '0.382': float(high - 0.382 * diff),
            '0.5': float(high - 0.5 * diff),
            '0.618': float(high - 0.618 * diff),
            '0.786': float(high - 0.786 * diff),
            '1.0': float(low)
        }
        
        return levels
        
    def calculate_rsi(self, prices, period=14):
        """Calculate RSI indicator"""
        if prices is None or len(prices) < period + 1:
            return None
            
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100
            
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return float(rsi)
        
    def calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """Calculate MACD indicator"""
        if prices is None or len(prices) < slow:
            return None
            
        # Calculate EMAs
        ema_fast = self.calculate_ema(prices, fast)
        ema_slow = self.calculate_ema(prices, slow)
        
        if ema_fast is None or ema_slow is None:
            return None
            
        macd_line = ema_fast - ema_slow
        signal_line = self.calculate_ema(macd_line, signal)
        
        if signal_line is None:
            return None
            
        histogram = macd_line - signal_line
        
        return {
            'macd': float(macd_line),
            'signal': float(signal_line),
            'histogram': float(histogram),
            'trend': 'bullish' if macd_line > signal_line else 'bearish'
        }
        
    def calculate_ema(self, prices, period):
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return None
        multiplier = 2 / (period + 1)
        ema = np.mean(prices[:period])
        for price in prices[period:]:
            ema = (price - ema) * multiplier + ema
        return ema
        
    def analyze_trend(self, prices, short_period=20, long_period=50):
        """Analyze trend using multiple timeframes"""
        if prices is None or len(prices) < long_period:
            return {'direction': 'neutral', 'strength': 0}
            
        ema_short = self.calculate_ema(prices, short_period)
        ema_long = self.calculate_ema(prices, long_period)
        
        if ema_short is None or ema_long is None:
            return {'direction': 'neutral', 'strength': 0}
            
        # Trend direction
        if ema_short > ema_long:
            direction = 'bullish'
            strength = min(1.0, (ema_short - ema_long) / ema_long * 10)
        elif ema_short < ema_long:
            direction = 'bearish'
            strength = min(1.0, (ema_long - ema_short) / ema_long * 10)
        else:
            direction = 'neutral'
            strength = 0
            
        return {
            'direction': direction,
            'strength': strength,
            'ema_short': float(ema_short),
            'ema_long': float(ema_long)
        }


class ChartCaptureThread(QThread):
    """Enhanced thread to capture screen and analyze charts"""
    analysis_complete = pyqtSignal(dict)
    screenshot_captured = pyqtSignal(np.ndarray)
    
    def __init__(self, region=None):
        super().__init__()
        self.region = region
        self.running = True
        self.timeframe = '1H'
        self.detector = AdvancedPatternDetector()
        self.capture_interval = 2.0
        self.pattern_history = deque(maxlen=100)
        
    def set_region(self, region):
        self.region = region
        
    def set_timeframe(self, tf):
        self.timeframe = tf
        # Adjust capture interval based on timeframe
        intervals = {'1M': 1, '5M': 2, '15M': 3, '1H': 5, '4H': 10, '1D': 30}
        self.capture_interval = intervals.get(tf, 2)
        
    def stop(self):
        self.running = False
        
    def run(self):
        while self.running:
            try:
                if self.region:
                    # Capture chart area
                    screenshot = ImageGrab.grab(bbox=self.region)
                    img_array = np.array(screenshot)
                    
                    self.screenshot_captured.emit(img_array)
                    
                    analysis = self.analyze_chart(img_array)
                    if analysis:
                        self.analysis_complete.emit(analysis)
                        
                time.sleep(self.capture_interval)
            except Exception as e:
                print(f"Capture error: {e}")
                time.sleep(1)
                
    def analyze_chart(self, img_array):
        """Comprehensive chart analysis"""
        try:
            # Extract price data
            prices = self.detector.extract_price_from_image(Image.fromarray(img_array))
            
            if prices is None:
                return None
                
            # Store price history
            self.detector.price_history.extend(prices)
            
            analysis = {
                'timestamp': datetime.now().isoformat(),
                'timeframe': self.timeframe,
                'price_data': {
                    'current': float(prices[-1]) if len(prices) > 0 else 0,
                    'high': float(np.max(prices)),
                    'low': float(np.min(prices)),
                    'range': float(np.max(prices) - np.min(prices))
                }
            }
            
            # Pattern detection
            patterns = []
            
            # Double Bottom
            db = self.detector.detect_double_bottom(prices)
            if db:
                patterns.append(db)
                
            # Cup and Handle
            cah = self.detector.detect_cup_and_handle(prices)
            if cah:
                patterns.append(cah)
                
            # Head and Shoulders
            hs = self.detector.detect_head_and_shoulders(prices)
            if hs:
                patterns.append(hs)
                
            # Triangles
            tri = self.detector.detect_triangle_patterns(prices)
            if tri:
                patterns.append(tri)
                
            analysis['patterns'] = patterns
            
            # Support/Resistance
            sr = self.detector.calculate_support_resistance(prices)
            if sr:
                analysis['support_resistance'] = sr
                
            # Liquidity grabs
            liq = self.detector.detect_liquidity_grabs(prices)
            if liq:
                analysis['liquidity_grabs'] = liq
                
            # Fibonacci levels
            fib = self.detector.calculate_fibonacci_levels(prices)
            if fib:
                analysis['fibonacci'] = fib
                
            # Indicators
            analysis['indicators'] = {
                'rsi': self.detector.calculate_rsi(prices),
                'macd': self.detector.calculate_macd(prices),
                'trend': self.detector.analyze_trend(prices)
            }
            
            # Trading signals
            signals = self.generate_signals(analysis)
            analysis['signals'] = signals
            
            return analysis
            
        except Exception as e:
            print(f"Analysis error: {e}")
            return None
            
    def generate_signals(self, analysis):
        """Generate trading signals based on analysis"""
        signals = []
        
        # Check patterns
        for pattern in analysis.get('patterns', []):
            if pattern['confidence'] > 0.7:
                signals.append({
                    'type': pattern['type'],
                    'action': 'buy' if pattern['type'] in ['Double Bottom', 'Cup & Handle', 'Ascending Triangle'] else 'sell',
                    'confidence': pattern['confidence'],
                    'entry': pattern.get('entry'),
                    'stop_loss': pattern.get('stop_loss'),
                    'target': pattern.get('target')
                })
                
        # Check indicators
        indicators = analysis.get('indicators', {})
        
        # RSI signals
        rsi = indicators.get('rsi')
        if rsi:
            if rsi < 30:
                signals.append({
                    'type': 'RSI Oversold',
                    'action': 'buy',
                    'confidence': 0.6,
                    'description': f'RSI at {rsi:.1f} - potential bounce'
                })
            elif rsi > 70:
                signals.append({
                    'type': 'RSI Overbought',
                    'action': 'sell',
                    'confidence': 0.6,
                    'description': f'RSI at {rsi:.1f} - potential pullback'
                })
                
        # MACD signals
        macd = indicators.get('macd')
        if macd and macd.get('trend'):
            signals.append({
                'type': f"MACD {macd['trend'].upper()}",
                'action': macd['trend'],
                'confidence': 0.65,
                'description': f"Histogram: {macd['histogram']:.4f}"
            })
            
        return signals


class RegionSelector(QWidget):
    """Overlay widget for selecting chart region"""
    region_selected = pyqtSignal(tuple)
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(0, 0, 1920, 1080)  # Full screen
        self.begin = QPoint()
        self.end = QPoint()
        self.drawing = False
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(QColor(102, 126, 234), 2, Qt.SolidLine))
        painter.setBrush(QColor(102, 126, 234, 50))
        
        if self.drawing:
            rect = QRect(self.begin, self.end)
            painter.drawRect(rect)
            
    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = event.pos()
        self.drawing = True
        self.update()
        
    def mouseMoveEvent(self, event):
        if self.drawing:
            self.end = event.pos()
            self.update()
            
    def mouseReleaseEvent(self, event):
        self.drawing = False
        rect = QRect(self.begin, self.end).normalized()
        self.region_selected.emit((rect.x(), rect.y(), rect.width(), rect.height()))
        self.close()


class ChartPatternAnalyzerPro(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chart Pattern Analyzer Pro v2.0")
        self.setGeometry(100, 100, 1200, 800)
        
        self.capture_thread = None
        self.chart_region = None
        self.analysis_history = []
        
        self.init_ui()
        self.init_tray()
        
    def init_ui(self):
        """Initialize enhanced UI"""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Header
        header = QLabel("📊 Chart Pattern Analyzer Pro v2.0")
        header.setStyleSheet("""
            font-size: 28px; 
            font-weight: bold; 
            color: #667eea;
            padding: 10px;
        """)
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Create tabs
        self.tabs = QTabWidget()
        
        # Tab 1: Controls
        self.tabs.addTab(self.create_control_tab(), "⚙️ Controls")
        
        # Tab 2: Live Analysis
        self.tabs.addTab(self.create_analysis_tab(), "📈 Live Analysis")
        
        # Tab 3: History
        self.tabs.addTab(self.create_history_tab(), "📜 History")
        
        # Tab 4: Settings
        self.tabs.addTab(self.create_settings_tab(), "🔧 Settings")
        
        layout.addWidget(self.tabs)
        
        # Status bar
        self.status_label = QLabel("Ready - Select chart region to begin analysis")
        self.status_label.setStyleSheet("color: #888; padding: 10px; font-size: 12px;")
        layout.addWidget(self.status_label)
        
    def create_control_tab(self):
        """Create control panel tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Region selection
        region_group = QGroupBox("Chart Region Selection")
        region_layout = QHBoxLayout()
        
        self.region_label = QLabel("No region selected")
        self.region_label.setStyleSheet("color: #ff6b6b;")
        region_layout.addWidget(self.region_label)
        
        self.select_region_btn = QPushButton("📷 Select Chart Region")
        self.select_region_btn.setStyleSheet("""
            QPushButton {
                background-color: #667eea;
                color: white;
                padding: 15px 30px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5a6fd6;
            }
        """)
        self.select_region_btn.clicked.connect(self.select_chart_region)
        region_layout.addWidget(self.select_region_btn)
        
        region_group.setLayout(region_layout)
        layout.addWidget(region_group)
        
        # Timeframe and controls
        control_group = QGroupBox("Analysis Controls")
        control_grid = QGridLayout()
        
        # Timeframe
        control_grid.addWidget(QLabel("Timeframe:"), 0, 0)
        self.timeframe_combo = QComboBox()
        self.timeframe_combo.addItems(['1M', '5M', '15M', '1H', '4H', '1D'])
        self.timeframe_combo.setCurrentText('1H')
        self.timeframe_combo.currentTextChanged.connect(self.on_timeframe_changed)
        control_grid.addWidget(self.timeframe_combo, 0, 1)
        
        # Start/Stop
        self.start_btn = QPushButton("▶️ Start Analysis")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #48bb78;
                color: white;
                padding: 15px 30px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
        """)
        self.start_btn.clicked.connect(self.toggle_analysis)
        control_grid.addWidget(self.start_btn, 0, 2)
        
        # Capture interval
        control_grid.addWidget(QLabel("Capture Interval (sec):"), 1, 0)
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 60)
        self.interval_spin.setValue(2)
        control_grid.addWidget(self.interval_spin, 1, 1)
        
        control_group.setLayout(control_grid)
        layout.addWidget(control_group)
        
        # Pattern toggles
        pattern_group = QGroupBox("Pattern Detection")
        pattern_layout = QGridLayout()
        
        self.patterns = {
            'double_bottom': QCheckBox("Double Bottom"),
            'cup_handle': QCheckBox("Cup & Handle"),
            'head_shoulders': QCheckBox("Head & Shoulders"),
            'triangles': QCheckBox("Triangles (Asc/Desc/Sym)"),
            'support_resistance': QCheckBox("Support/Resistance"),
            'liquidity_grabs': QCheckBox("Liquidity Grabs"),
            'fibonacci': QCheckBox("Fibonacci Levels"),
            'indicators': QCheckBox("RSI/MACD/Trend")
        }
        
        for i, (key, cb) in enumerate(self.patterns.items()):
            cb.setChecked(True)
            cb.setStyleSheet("padding: 5px;")
            pattern_layout.addWidget(cb, i // 2, i % 2)
            
        pattern_group.setLayout(pattern_layout)
        layout.addWidget(pattern_group)
        
        layout.addStretch()
        return widget
        
    def create_analysis_tab(self):
        """Create live analysis tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Splitter for chart view and results
        splitter = QSplitter(Qt.Horizontal)
        
        # Left: Chart preview
        chart_widget = QWidget()
        chart_layout = QVBoxLayout(chart_widget)
        
        self.chart_preview = QLabel("Chart preview will appear here")
        self.chart_preview.setAlignment(Qt.AlignCenter)
        self.chart_preview.setStyleSheet("""
            background-color: #1a1a2e;
            border: 2px solid #667eea;
            border-radius: 8px;
            min-height: 300px;
        """)
        self.chart_preview.setMinimumSize(400, 300)
        chart_layout.addWidget(self.chart_preview)
        
        splitter.addWidget(chart_widget)
        
        # Right: Analysis results
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)
        
        # Patterns detected
        patterns_group = QGroupBox("Detected Patterns")
        self.patterns_list = QListWidget()
        self.patterns_list.setStyleSheet("""
            QListWidget {
                background-color: #1a1a2e;
                color: #00ff88;
                font-family: 'Consolas', monospace;
                padding: 5px;
            }
        """)
        patterns_group.setLayout(QVBoxLayout())
        patterns_group.layout().addWidget(self.patterns_list)
        results_layout.addWidget(patterns_group)
        
        # Trading signals
        signals_group = QGroupBox("🎯 Trading Signals")
        self.signals_text = QTextEdit()
        self.signals_text.setReadOnly(True)
        self.signals_text.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a2e;
                color: #ffd700;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
        """)
        signals_group.setLayout(QVBoxLayout())
        signals_group.layout().addWidget(self.signals_text)
        results_layout.addWidget(signals_group)
        
        # Technical indicators
        indicators_group = QGroupBox("📊 Technical Indicators")
        self.indicators_text = QTextEdit()
        self.indicators_text.setReadOnly(True)
        self.indicators_text.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a2e;
                color: #00ffff;
                font-family: 'Consolas', monospace;
                font-size: 11px;
            }
        """)
        indicators_group.setLayout(QVBoxLayout())
        indicators_group.layout().addWidget(self.indicators_text)
        results_layout.addWidget(indicators_group)
        
        splitter.addWidget(results_widget)
        splitter.setSizes([400, 600])
        
        layout.addWidget(splitter)
        return widget
        
    def create_history_tab(self):
        """Create history tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.history_list = QListWidget()
        self.history_list.setStyleSheet("""
            QListWidget {
                background-color: #1a1a2e;
                color: #e0e0e0;
                font-family: 'Consolas', monospace;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #333;
            }
        """)
        layout.addWidget(self.history_list)
        
        # Export button
        export_btn = QPushButton("📁 Export History to JSON")
        export_btn.clicked.connect(self.export_history)
        layout.addWidget(export_btn)
        
        return widget
        
    def create_settings_tab(self):
        """Create settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Sensitivity settings
        sensitivity_group = QGroupBox("Detection Sensitivity")
        sens_layout = QGridLayout()
        
        sens_layout.addWidget(QLabel("Pattern Confidence Threshold:"), 0, 0)
        self.confidence_slider = QSlider(Qt.Horizontal)
        self.confidence_slider.setRange(50, 95)
        self.confidence_slider.setValue(70)
        sens_layout.addWidget(self.confidence_slider, 0, 1)
        self.confidence_label = QLabel("70%")
        sens_layout.addWidget(self.confidence_label, 0, 2)
        self.confidence_slider.valueChanged.connect(
            lambda v: self.confidence_label.setText(f"{v}%")
        )
        
        sensitivity_group.setLayout(sens_layout)
        layout.addWidget(sensitivity_group)
        
        # Alert settings
        alert_group = QGroupBox("Alerts")
        alert_layout = QVBoxLayout()
        
        self.alert_pattern_cb = QCheckBox("Alert on pattern detection")
        self.alert_pattern_cb.setChecked(True)
        alert_layout.addWidget(self.alert_pattern_cb)
        
        self.alert_signal_cb = QCheckBox("Alert on trading signal")
        self.alert_signal_cb.setChecked(True)
        alert_layout.addWidget(self.alert_signal_cb)
        
        alert_group.setLayout(alert_layout)
        layout.addWidget(alert_group)
        
        layout.addStretch()
        return widget
        
    def init_tray(self):
        """Initialize system tray"""
        self.tray_icon = QSystemTrayIcon(self)
        tray_menu = QMenu()
        
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        hide_action = QAction("Hide", self)
        hide_action.triggered.connect(self.hide)
        tray_menu.addAction(hide_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
    def select_chart_region(self):
        """Show region selector overlay"""
        self.hide()
        time.sleep(0.3)
        
        self.selector = RegionSelector()
        self.selector.region_selected.connect(self.on_region_selected)
        self.selector.show()
        
    def on_region_selected(self, region):
        """Handle region selection"""
        self.chart_region = region
        self.region_label.setText(f"Region: {region}")
        self.region_label.setStyleSheet("color: #48bb78;")
        self.show()
        self.status_label.setText(f"Chart region selected: {region}")
        
    def on_timeframe_changed(self, tf):
        """Handle timeframe change"""
        if self.capture_thread:
            self.capture_thread.set_timeframe(tf)
            
    def toggle_analysis(self):
        """Start or stop analysis"""
        if self.capture_thread and self.capture_thread.isRunning():
            self.stop_analysis()
        else:
            self.start_analysis()
            
    def start_analysis(self):
        """Start chart analysis"""
        if not self.chart_region:
            QMessageBox.warning(self, "No Region", "Please select a chart region first!")
            return
            
        self.capture_thread = ChartCaptureThread(self.chart_region)
        self.capture_thread.analysis_complete.connect(self.on_analysis_complete)
        self.capture_thread.screenshot_captured.connect(self.on_screenshot)
        self.capture_thread.set_timeframe(self.timeframe_combo.currentText())
        self.capture_thread.start()
        
        self.start_btn.setText("⏹️ Stop Analysis")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff6b6b;
                color: white;
                padding: 15px 30px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
        """)
        self.status_label.setText("🔴 Analysis running...")
        
    def stop_analysis(self):
        """Stop chart analysis"""
        if self.capture_thread:
            self.capture_thread.stop()
            self.capture_thread.wait()
            
        self.start_btn.setText("▶️ Start Analysis")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #48bb78;
                color: white;
                padding: 15px 30px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
        """)
        self.status_label.setText("Analysis stopped")
        
    def on_screenshot(self, img_array):
        """Update chart preview"""
        # Convert to QPixmap
        height, width, channels = img_array.shape
        bytes_per_line = channels * width
        q_image = QImage(img_array.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        
        # Scale to fit
        scaled = pixmap.scaled(self.chart_preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.chart_preview.setPixmap(scaled)
        
    def on_analysis_complete(self, analysis):
        """Handle analysis results"""
        # Store in history
        self.analysis_history.append(analysis)
        
        # Update patterns list
        self.patterns_list.clear()
        for pattern in analysis.get('patterns', []):
            item_text = f"{pattern['type']} - {pattern['confidence']*100:.0f}% confidence"
            self.patterns_list.addItem(item_text)
            
        # Update signals
        signals_text = ""
        for signal in analysis.get('signals', []):
            emoji = "🟢" if signal['action'] == 'buy' else "🔴"
            signals_text += f"{emoji} {signal['type']}\n"
            signals_text += f"   Action: {signal['action'].upper()}\n"
            signals_text += f"   Confidence: {signal['confidence']*100:.0f}%\n"
            if 'entry' in signal:
                signals_text += f"   Entry: {signal['entry']:.2f}\n"
            if 'stop_loss' in signal:
                signals_text += f"   Stop: {signal['stop_loss']:.2f}\n"
            if 'target' in signal:
                signals_text += f"   Target: {signal['target']:.2f}\n"
            signals_text += "\n"
            
        self.signals_text.setText(signals_text or "No signals detected")
        
        # Update indicators
        indicators = analysis.get('indicators', {})
        ind_text = ""
        
        if indicators.get('rsi'):
            ind_text += f"RSI: {indicators['rsi']:.1f}\n"
            
        if indicators.get('macd'):
            macd = indicators['macd']
            ind_text += f"MACD: {macd['macd']:.4f}\n"
            ind_text += f"Signal: {macd['signal']:.4f}\n"
            ind_text += f"Trend: {macd['trend'].upper()}\n"
            
        if indicators.get('trend'):
            trend = indicators['trend']
            ind_text += f"\nTrend: {trend['direction'].upper()}\n"
            ind_text += f"Strength: {trend['strength']*100:.0f}%\n"
            
        # Support/Resistance
        sr = analysis.get('support_resistance', {})
        if sr:
            ind_text += "\n📊 Support/Resistance:\n"
            for level in sr.get('support', []):
                ind_text += f"  S: {level['price']:.2f} (touches: {level['touches']})\n"
            for level in sr.get('resistance', []):
                ind_text += f"  R: {level['price']:.2f} (touches: {level['touches']})\n"
                
        self.indicators_text.setText(ind_text)
        
        # Add to history
        history_item = f"[{analysis['timestamp'][:19]}] {len(analysis.get('patterns', []))} patterns, {len(analysis.get('signals', []))} signals"
        self.history_list.addItem(history_item)
        
    def export_history(self):
        """Export analysis history to JSON"""
        filename, _ = QFileDialog.getSaveFileName(self, "Export History", "chart_analysis_history.json", "JSON Files (*.json)")
        if filename:
            with open(filename, 'w') as f:
                json.dump(self.analysis_history, f, indent=2)
            QMessageBox.information(self, "Export Complete", f"History exported to {filename}")
            
    def closeEvent(self, event):
        """Clean up on close"""
        if self.capture_thread:
            self.capture_thread.stop()
            self.capture_thread.wait()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Dark theme
    app.setStyleSheet("""
        QMainWindow, QWidget {
            background-color: #0f0f1a;
            color: #e0e0e0;
        }
        QGroupBox {
            border: 2px solid #667eea;
            border-radius: 8px;
            margin-top: 15px;
            padding-top: 15px;
            font-weight: bold;
            font-size: 13px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 15px;
            padding: 0 10px;
            color: #667eea;
        }
        QPushButton {
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            font-weight: bold;
        }
        QComboBox, QSpinBox {
            background-color: #1a1a2e;
            border: 2px solid #667eea;
            padding: 8px;
            border-radius: 5px;
            color: white;
            font-size: 13px;
        }
        QCheckBox {
            spacing: 10px;
            font-size: 12px;
        }
        QCheckBox::indicator {
            width: 20px;
            height: 20px;
        }
        QTabWidget::pane {
            border: 2px solid #667eea;
            background-color: #0f0f1a;
        }
        QTabBar::tab {
            background-color: #1a1a2e;
            padding: 12px 25px;
            margin-right: 5px;
            border-top-left-radius: 5px;
            border-top-right-radius: 5px;
        }
        QTabBar::tab:selected {
            background-color: #667eea;
            color: white;
        }
        QListWidget {
            background-color: #1a1a2e;
            border: 1px solid #333;
            border-radius: 5px;
        }
        QSlider::groove:horizontal {
            height: 8px;
            background: #1a1a2e;
            border-radius: 4px;
        }
        QSlider::handle:horizontal {
            background: #667eea;
            width: 18px;
            margin: -5px 0;
            border-radius: 9px;
        }
    """)
    
    window = ChartPatternAnalyzerPro()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
