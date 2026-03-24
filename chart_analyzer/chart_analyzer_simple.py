#!/usr/bin/env python3
"""
Chart Pattern Analyzer Simple v3.0
No drag selection - uses preset regions or manual coordinates
"""

import sys
import numpy as np
import cv2
from PIL import Image, ImageGrab
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QComboBox,
                             QSpinBox, QTextEdit, QGroupBox, QRadioButton,
                             QButtonGroup, QLineEdit, QMessageBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QPixmap, QImage
import json
import time
from datetime import datetime
from scipy.signal import argrelextrema
from scipy.ndimage import gaussian_filter1d
from scipy.stats import linregress
from collections import deque


class SimplePatternDetector:
    """Simplified pattern detection"""
    
    def __init__(self):
        self.price_history = deque(maxlen=500)
        
    def extract_price_from_image(self, image):
        """Extract price data from chart image"""
        try:
            img_array = np.array(image)
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # Edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return None
                
            # Get main price line
            main_contour = max(contours, key=cv2.contourArea)
            points = main_contour.reshape(-1, 2)
            
            # Extract price levels
            x_coords = np.unique(points[:, 0])
            prices = []
            
            for x in x_coords:
                y_vals = points[points[:, 0] == x, 1]
                if len(y_vals) > 0:
                    prices.append(np.median(y_vals))
                    
            return np.array(prices) if len(prices) > 20 else None
        except:
            return None
    
    def detect_double_bottom(self, prices):
        """Detect Double Bottom pattern"""
        if prices is None or len(prices) < 30:
            return None
            
        minima = argrelextrema(prices, np.less, order=10)[0]
        
        if len(minima) < 2:
            return None
            
        for i in range(len(minima) - 1):
            first = prices[minima[i]]
            second = prices[minima[i+1]]
            
            price_range = np.max(prices) - np.min(prices)
            if price_range == 0:
                continue
                
            diff = abs(first - second) / price_range
            
            if diff < 0.05:  # 5% tolerance
                middle = prices[minima[i]:minima[i+1]]
                if len(middle) == 0:
                    continue
                    
                peak = np.max(middle)
                depth = (peak - first) / price_range
                
                if depth > 0.1:
                    return {
                        'type': 'Double Bottom',
                        'confidence': 1 - diff,
                        'entry': float(peak * 1.01),
                        'target': float(peak + (peak - first)),
                        'description': 'W pattern - bullish reversal'
                    }
        return None
    
    def detect_support_resistance(self, prices):
        """Find support and resistance levels"""
        if prices is None or len(prices) < 20:
            return None
            
        highs = argrelextrema(prices, np.greater, order=10)[0]
        lows = argrelextrema(prices, np.less, order=10)[0]
        
        resistance = [float(prices[h]) for h in highs[:3]] if len(highs) > 0 else []
        support = [float(prices[l]) for l in lows[:3]] if len(lows) > 0 else []
        
        return {'support': support, 'resistance': resistance}
    
    def calculate_rsi(self, prices, period=14):
        """Calculate RSI"""
        if len(prices) < period + 1:
            return None
            
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100
            
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    
    def analyze_trend(self, prices):
        """Simple trend analysis"""
        if prices is None or len(prices) < 20:
            return {'direction': 'neutral', 'strength': 0}
            
        first_half = np.mean(prices[:len(prices)//2])
        second_half = np.mean(prices[len(prices)//2:])
        
        diff = (second_half - first_half) / first_half
        
        if diff > 0.02:
            return {'direction': 'bullish', 'strength': min(1.0, diff * 10)}
        elif diff < -0.02:
            return {'direction': 'bearish', 'strength': min(1.0, abs(diff) * 10)}
        else:
            return {'direction': 'neutral', 'strength': 0}


class ChartCaptureThread(QThread):
    """Capture and analyze thread"""
    analysis_complete = pyqtSignal(dict)
    screenshot_captured = pyqtSignal(np.ndarray)
    
    def __init__(self, region=None):
        super().__init__()
        self.region = region
        self.running = True
        self.timeframe = '1H'
        self.detector = SimplePatternDetector()
        self.capture_interval = 3
        
    def set_region(self, region):
        self.region = region
        
    def set_timeframe(self, tf):
        self.timeframe = tf
        intervals = {'1M': 1, '5M': 2, '15M': 3, '1H': 5, '4H': 10, '1D': 30}
        self.capture_interval = intervals.get(tf, 3)
        
    def stop(self):
        self.running = False
        
    def run(self):
        while self.running:
            try:
                if self.region:
                    screenshot = ImageGrab.grab(bbox=self.region)
                    img_array = np.array(screenshot)
                    
                    self.screenshot_captured.emit(img_array)
                    
                    analysis = self.analyze_chart(img_array)
                    if analysis:
                        self.analysis_complete.emit(analysis)
                        
                time.sleep(self.capture_interval)
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(1)
                
    def analyze_chart(self, img_array):
        """Analyze chart"""
        try:
            prices = self.detector.extract_price_from_image(Image.fromarray(img_array))
            
            if prices is None:
                return None
                
            analysis = {
                'timestamp': datetime.now().strftime('%H:%M:%S'),
                'timeframe': self.timeframe,
                'price': {
                    'current': float(prices[-1]),
                    'high': float(np.max(prices)),
                    'low': float(np.min(prices))
                }
            }
            
            # Patterns
            patterns = []
            db = self.detector.detect_double_bottom(prices)
            if db:
                patterns.append(db)
            analysis['patterns'] = patterns
            
            # S/R
            sr = self.detector.detect_support_resistance(prices)
            if sr:
                analysis['sr'] = sr
                
            # Indicators
            analysis['rsi'] = self.detector.calculate_rsi(prices)
            analysis['trend'] = self.detector.analyze_trend(prices)
            
            return analysis
            
        except Exception as e:
            print(f"Analysis error: {e}")
            return None


class ChartAnalyzerSimple(QMainWindow):
    """Simple main window"""
    
    PRESETS = {
        'Top Left': (0, 0, 800, 600),
        'Top Right': (800, 0, 800, 600),
        'Bottom Left': (0, 500, 800, 600),
        'Bottom Right': (800, 500, 800, 600),
        'Center': (400, 200, 800, 600),
        'Full Screen': (0, 0, 1920, 1080)
    }
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chart Pattern Analyzer Simple v3.0")
        self.setGeometry(100, 100, 900, 700)
        
        self.capture_thread = None
        self.chart_region = None
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Title
        title = QLabel("📊 Chart Pattern Analyzer Simple")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #667eea;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Region Selection
        region_group = QGroupBox("Select Chart Region")
        region_layout = QVBoxLayout()
        
        # Preset buttons
        preset_layout = QHBoxLayout()
        self.preset_group = QButtonGroup(self)
        
        for i, (name, coords) in enumerate(self.PRESETS.items()):
            radio = QRadioButton(name)
            self.preset_group.addButton(radio, i)
            preset_layout.addWidget(radio)
            
        self.preset_group.buttonClicked.connect(self.on_preset_selected)
        region_layout.addLayout(preset_layout)
        
        # Manual coordinates
        manual_layout = QHBoxLayout()
        manual_layout.addWidget(QLabel("Or enter coordinates (x, y, w, h):"))
        
        self.coord_input = QLineEdit()
        self.coord_input.setPlaceholderText("100, 100, 800, 600")
        manual_layout.addWidget(self.coord_input)
        
        self.set_manual_btn = QPushButton("Set")
        self.set_manual_btn.clicked.connect(self.set_manual_region)
        manual_layout.addWidget(self.set_manual_btn)
        
        region_layout.addLayout(manual_layout)
        
        # Current region display
        self.region_label = QLabel("No region selected")
        self.region_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")
        region_layout.addWidget(self.region_label)
        
        region_group.setLayout(region_layout)
        layout.addWidget(region_group)
        
        # Controls
        control_group = QGroupBox("Analysis Controls")
        control_layout = QHBoxLayout()
        
        control_layout.addWidget(QLabel("Timeframe:"))
        self.timeframe_combo = QComboBox()
        self.timeframe_combo.addItems(['1M', '5M', '15M', '1H', '4H', '1D'])
        self.timeframe_combo.setCurrentText('1H')
        control_layout.addWidget(self.timeframe_combo)
        
        control_layout.addWidget(QLabel("Interval (sec):"))
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 60)
        self.interval_spin.setValue(3)
        control_layout.addWidget(self.interval_spin)
        
        self.start_btn = QPushButton("▶️ Start")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #48bb78;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
            }
        """)
        self.start_btn.clicked.connect(self.toggle_analysis)
        control_layout.addWidget(self.start_btn)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # Results
        results_group = QGroupBox("Analysis Results")
        results_layout = QVBoxLayout()
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a2e;
                color: #00ff88;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
        """)
        results_layout.addWidget(self.results_text)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        # Status
        self.status_label = QLabel("Ready - Select a region and click Start")
        self.status_label.setStyleSheet("color: #888; padding: 5px;")
        layout.addWidget(self.status_label)
        
    def on_preset_selected(self, button):
        """Handle preset selection"""
        preset_name = button.text()
        self.chart_region = self.PRESETS[preset_name]
        self.region_label.setText(f"Region: {preset_name} {self.chart_region}")
        self.region_label.setStyleSheet("color: #48bb78; font-weight: bold;")
        
    def set_manual_region(self):
        """Set manual region from input"""
        try:
            coords = [int(x.strip()) for x in self.coord_input.text().split(',')]
            if len(coords) == 4:
                self.chart_region = tuple(coords)
                self.region_label.setText(f"Region: Manual {self.chart_region}")
                self.region_label.setStyleSheet("color: #48bb78; font-weight: bold;")
            else:
                QMessageBox.warning(self, "Error", "Enter 4 numbers: x, y, width, height")
        except:
            QMessageBox.warning(self, "Error", "Invalid format. Use: 100, 100, 800, 600")
            
    def toggle_analysis(self):
        """Start or stop"""
        if self.capture_thread and self.capture_thread.isRunning():
            self.stop_analysis()
        else:
            self.start_analysis()
            
    def start_analysis(self):
        """Start analysis"""
        if not self.chart_region:
            QMessageBox.warning(self, "No Region", "Please select a region first!")
            return
            
        self.capture_thread = ChartCaptureThread(self.chart_region)
        self.capture_thread.analysis_complete.connect(self.on_analysis)
        self.capture_thread.set_timeframe(self.timeframe_combo.currentText())
        self.capture_thread.start()
        
        self.start_btn.setText("⏹️ Stop")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff6b6b;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
            }
        """)
        self.status_label.setText("🔴 Analyzing...")
        
    def stop_analysis(self):
        """Stop analysis"""
        if self.capture_thread:
            self.capture_thread.stop()
            self.capture_thread.wait()
            
        self.start_btn.setText("▶️ Start")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #48bb78;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
            }
        """)
        self.status_label.setText("Analysis stopped")
        
    def on_analysis(self, analysis):
        """Display results"""
        text = f"""
[{analysis['timestamp']}] {analysis['timeframe']}

📈 Price: {analysis['price']['current']:.2f} (H: {analysis['price']['high']:.2f}, L: {analysis['price']['low']:.2f})

"""
        
        if analysis['patterns']:
            text += "🔍 PATTERNS:\n"
            for p in analysis['patterns']:
                text += f"  • {p['type']} - {p['confidence']*100:.0f}%\n"
                text += f"    Entry: {p['entry']:.2f}, Target: {p['target']:.2f}\n"
        else:
            text += "🔍 No patterns detected\n"
            
        if analysis.get('sr'):
            text += "\n📊 Support/Resistance:\n"
            for s in analysis['sr'].get('support', []):
                text += f"  Support: {s:.2f}\n"
            for r in analysis['sr'].get('resistance', []):
                text += f"  Resistance: {r:.2f}\n"
                
        if analysis.get('rsi'):
            text += f"\n📉 RSI: {analysis['rsi']:.1f}\n"
            
        if analysis.get('trend'):
            t = analysis['trend']
            text += f"📊 Trend: {t['direction'].upper()} ({t['strength']*100:.0f}%)\n"
            
        text += "\n" + "="*50 + "\n"
        
        self.results_text.append(text)
        
    def closeEvent(self, event):
        """Cleanup"""
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
            margin-top: 10px;
            padding-top: 10px;
            font-weight: bold;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
            color: #667eea;
        }
        QPushButton {
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
        }
        QRadioButton {
            spacing: 5px;
        }
        QLineEdit {
            background-color: #1a1a2e;
            border: 1px solid #667eea;
            padding: 5px;
            color: white;
        }
    """)
    
    window = ChartAnalyzerSimple()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
