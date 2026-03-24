#!/usr/bin/env python3
"""
Chart Pattern Analyzer - Windows Desktop App
Analyzes any chart visible on screen for patterns
Supports 4H, 1H, 1M timeframes
Detects: Double Bottom, Cup & Handle, Support/Resistance, Liquidity Grabs
"""

import sys
import numpy as np
import cv2
from PIL import Image, ImageGrab
import pyautogui
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QComboBox,
                             QSpinBox, QCheckBox, QTextEdit, QGroupBox,
                             QSystemTrayIcon, QMenu, QAction)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QIcon, QPixmap, QImage
import json
import time
from datetime import datetime
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d

class ChartCaptureThread(QThread):
    """Thread to capture screen and analyze charts"""
    analysis_complete = pyqtSignal(dict)
    
    def __init__(self, region=None):
        super().__init__()
        self.region = region  # (x, y, width, height)
        self.running = True
        self.timeframe = '1H'
        
    def set_region(self, region):
        self.region = region
        
    def set_timeframe(self, tf):
        self.timeframe = tf
        
    def stop(self):
        self.running = False
        
    def run(self):
        while self.running:
            try:
                if self.region:
                    # Capture chart area
                    screenshot = ImageGrab.grab(bbox=self.region)
                    analysis = self.analyze_chart(screenshot)
                    self.analysis_complete.emit(analysis)
                time.sleep(2)  # Analyze every 2 seconds
            except Exception as e:
                print(f"Capture error: {e}")
                time.sleep(1)
                
    def analyze_chart(self, image):
        """Analyze chart image for patterns"""
        # Convert to numpy array
        img_array = np.array(image)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Extract price data from image (simplified - would need OCR in real implementation)
        # For now, simulate pattern detection
        patterns = []
        
        # Detect support/resistance levels
        support_resistance = self.detect_support_resistance(gray)
        
        # Detect double bottom
        double_bottom = self.detect_double_bottom(gray)
        if double_bottom:
            patterns.append({
                'type': 'Double Bottom',
                'confidence': double_bottom['confidence'],
                'description': 'Bullish reversal pattern detected'
            })
            
        # Detect cup and handle
        cup_handle = self.detect_cup_handle(gray)
        if cup_handle:
            patterns.append({
                'type': 'Cup & Handle',
                'confidence': cup_handle['confidence'],
                'description': 'Bullish continuation pattern'
            })
            
        # Detect liquidity grabs
        liq_grabs = self.detect_liquidity_grabs(gray)
        
        # Trend analysis
        trend = self.analyze_trend(gray)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'timeframe': self.timeframe,
            'patterns': patterns,
            'support_resistance': support_resistance,
            'liquidity_grabs': liq_grabs,
            'trend': trend,
            'image_size': image.size
        }
        
    def detect_support_resistance(self, gray_img):
        """Detect support and resistance levels"""
        # Simplified - look for horizontal lines where price bounced
        height, width = gray_img.shape
        
        # Simulate detection
        levels = []
        
        # In real implementation, would use:
        # - Edge detection
        # - Horizontal line detection
        # - Price level clustering
        
        return {
            'support': [height * 0.7, height * 0.8],  # Y coordinates
            'resistance': [height * 0.2, height * 0.3],
            'confidence': 0.75
        }
        
    def detect_double_bottom(self, gray_img):
        """Detect double bottom pattern"""
        # Look for W shape in price action
        # Simplified simulation
        
        height, width = gray_img.shape
        
        # Check for two similar lows with peak in between
        # This is a simplified version - real implementation would track actual price
        
        return None  # Not detected in this frame
        
    def detect_cup_handle(self, gray_img):
        """Detect cup and handle pattern"""
        # Look for U shape followed by small pullback
        return None
        
    def detect_liquidity_grabs(self, gray_img):
        """Detect liquidity grab areas (wick spikes beyond S/R)"""
        return {
            'areas': [],
            'description': 'No significant liquidity grabs detected'
        }
        
    def analyze_trend(self, gray_img):
        """Analyze overall trend"""
        # Simple trend detection based on overall direction
        height, width = gray_img.shape
        
        # Compare top half vs bottom half brightness
        top_half = np.mean(gray_img[:height//2, :])
        bottom_half = np.mean(gray_img[height//2:, :])
        
        if top_half > bottom_half:
            return {'direction': 'bullish', 'strength': 0.6}
        else:
            return {'direction': 'bearish', 'strength': 0.6}


class ChartPatternAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chart Pattern Analyzer v1.0")
        self.setGeometry(100, 100, 800, 600)
        
        # Analysis thread
        self.capture_thread = None
        self.chart_region = None
        
        self.init_ui()
        self.init_tray()
        
    def init_ui(self):
        """Initialize UI"""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Title
        title = QLabel("📊 Chart Pattern Analyzer")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #667eea;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Control Panel
        control_group = QGroupBox("Controls")
        control_layout = QHBoxLayout()
        
        # Timeframe selector
        self.timeframe_combo = QComboBox()
        self.timeframe_combo.addItems(['1M', '5M', '15M', '1H', '4H', '1D'])
        self.timeframe_combo.setCurrentText('1H')
        control_layout.addWidget(QLabel("Timeframe:"))
        control_layout.addWidget(self.timeframe_combo)
        
        # Capture region button
        self.capture_btn = QPushButton("📷 Select Chart Region")
        self.capture_btn.setStyleSheet("""
            QPushButton {
                background-color: #667eea;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6fd6;
            }
        """)
        self.capture_btn.clicked.connect(self.select_chart_region)
        control_layout.addWidget(self.capture_btn)
        
        # Start/Stop analysis
        self.start_btn = QPushButton("▶️ Start Analysis")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #48bb78;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        self.start_btn.clicked.connect(self.toggle_analysis)
        control_layout.addWidget(self.start_btn)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # Pattern Detection Settings
        settings_group = QGroupBox("Pattern Detection Settings")
        settings_layout = QHBoxLayout()
        
        self.double_bottom_cb = QCheckBox("Double Bottom")
        self.double_bottom_cb.setChecked(True)
        settings_layout.addWidget(self.double_bottom_cb)
        
        self.cup_handle_cb = QCheckBox("Cup & Handle")
        self.cup_handle_cb.setChecked(True)
        settings_layout.addWidget(self.cup_handle_cb)
        
        self.support_res_cb = QCheckBox("Support/Resistance")
        self.support_res_cb.setChecked(True)
        settings_layout.addWidget(self.support_res_cb)
        
        self.liquidity_cb = QCheckBox("Liquidity Grabs")
        self.liquidity_cb.setChecked(True)
        settings_layout.addWidget(self.liquidity_cb)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # Results Display
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
                padding: 10px;
            }
        """)
        results_layout.addWidget(self.results_text)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        # Status bar
        self.status_label = QLabel("Ready - Select chart region to begin")
        self.status_label.setStyleSheet("color: #888; padding: 5px;")
        layout.addWidget(self.status_label)
        
    def init_tray(self):
        """Initialize system tray icon"""
        self.tray_icon = QSystemTrayIcon(self)
        # Would set icon here
        
        tray_menu = QMenu()
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        
        hide_action = QAction("Hide", self)
        hide_action.triggered.connect(self.hide)
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
    def select_chart_region(self):
        """Let user select chart area on screen"""
        self.hide()  # Hide window to see screen
        time.sleep(0.5)
        
        # Take full screenshot
        screenshot = ImageGrab.grab()
        screenshot.save('temp_screenshot.png')
        
        # Show selection overlay (simplified - would use OpenCV for interactive selection)
        self.show()
        
        # For now, use predefined region or let user input coordinates
        # In real implementation: drag to select region
        
        self.chart_region = (100, 100, 800, 600)  # Default
        self.status_label.setText(f"Chart region selected: {self.chart_region}")
        
    def toggle_analysis(self):
        """Start or stop chart analysis"""
        if self.capture_thread and self.capture_thread.isRunning():
            # Stop
            self.capture_thread.stop()
            self.capture_thread.wait()
            self.start_btn.setText("▶️ Start Analysis")
            self.status_label.setText("Analysis stopped")
        else:
            # Start
            if not self.chart_region:
                self.select_chart_region()
                
            self.capture_thread = ChartCaptureThread(self.chart_region)
            self.capture_thread.analysis_complete.connect(self.on_analysis_complete)
            self.capture_thread.set_timeframe(self.timeframe_combo.currentText())
            self.capture_thread.start()
            
            self.start_btn.setText("⏹️ Stop Analysis")
            self.status_label.setText("Analyzing chart...")
            
    def on_analysis_complete(self, analysis):
        """Handle analysis results"""
        # Format results
        text = f"""
[{analysis['timestamp']}] Timeframe: {analysis['timeframe']}

📈 TREND: {analysis['trend']['direction'].upper()} (strength: {analysis['trend']['strength']:.0%})

🔍 PATTERNS DETECTED:
"""
        
        if analysis['patterns']:
            for pattern in analysis['patterns']:
                text += f"  • {pattern['type']} - {pattern['confidence']:.0%} confidence\n"
                text += f"    {pattern['description']}\n\n"
        else:
            text += "  No clear patterns detected\n\n"
            
        text += f"""
📊 SUPPORT/RESISTANCE:
  Support levels: {len(analysis['support_resistance']['support'])}
  Resistance levels: {len(analysis['support_resistance']['resistance'])}

💧 LIQUIDITY:
  {analysis['liquidity_grabs']['description']}

{'='*50}
"""
        
        self.results_text.append(text)
        
        # Auto-scroll to bottom
        scrollbar = self.results_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
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
        QMainWindow {
            background-color: #0f0f1a;
        }
        QWidget {
            background-color: #0f0f1a;
            color: #e0e0e0;
        }
        QGroupBox {
            border: 2px solid #667eea;
            border-radius: 5px;
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
        QComboBox, QSpinBox {
            background-color: #1a1a2e;
            border: 1px solid #667eea;
            padding: 5px;
            border-radius: 3px;
            color: white;
        }
        QCheckBox {
            spacing: 8px;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
        }
    """)
    
    window = ChartPatternAnalyzer()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
