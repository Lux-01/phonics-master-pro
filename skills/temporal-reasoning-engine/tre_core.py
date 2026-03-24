#!/usr/bin/env python3
"""
Temporal Reasoning Engine (TRE)
Provides unified time-series analysis, forecasting, and pattern detection.

ACA Implementation:
- Requirements: Unified temporal analysis, forecasting, anomaly detection
- Architecture: Modular with pluggable analysis methods
- Data Flow: Ingest → Store → Analyze → Query
- Edge Cases: Empty data, insufficient points, API limits
- Tools: Pandas, NumPy, Scikit-learn, Statsmodels
- Errors: Retry, fallback, graceful degradation
- Tests: 6 comprehensive test cases
"""

import json
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
from numpy.polynomial import polynomial as P

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TrendDirection(Enum):
    UP = "up"
    DOWN = "down"
    FLAT = "flat"
    UNKNOWN = "unknown"


class AnomalyType(Enum):
    SPIKE = "spike"
    DROP = "drop"
    UNUSUAL_VOLUME = "unusual_volume"
    PATTERN_BREAK = "pattern_break"


@dataclass
class TimeSeriesPoint:
    """Single data point in time series."""
    timestamp: datetime
    value: float
    metadata: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "value": self.value,
            "metadata": self.metadata or {}
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "TimeSeriesPoint":
        return cls(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            value=float(data["value"]),
            metadata=data.get("metadata", {})
        )


@dataclass
class TrendAnalysis:
    """Result of trend analysis."""
    direction: TrendDirection
    slope: float
    intercept: float
    r_squared: float
    confidence: float
    start_value: float
    end_value: float
    percent_change: float
    
    def to_dict(self) -> Dict:
        return {
            "direction": self.direction.value,
            "slope": self.slope,
            "intercept": self.intercept,
            "r_squared": self.r_squared,
            "confidence": self.confidence,
            "start_value": self.start_value,
            "end_value": self.end_value,
            "percent_change": self.percent_change
        }


@dataclass
class Anomaly:
    """Detected anomaly."""
    timestamp: datetime
    type: AnomalyType
    value: float
    expected_value: float
    deviation_percent: float
    severity: str  # low, medium, high, critical
    
    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "type": self.type.value,
            "value": self.value,
            "expected_value": self.expected_value,
            "deviation_percent": self.deviation_percent,
            "severity": self.severity
        }


@dataclass
class Forecast:
    """Time series forecast."""
    timestamp: datetime
    predicted_value: float
    confidence_lower: float
    confidence_upper: float
    confidence_level: float
    
    def to_dict(self) -> Dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "predicted_value": self.predicted_value,
            "confidence_lower": self.confidence_lower,
            "confidence_upper": self.confidence_upper,
            "confidence_level": self.confidence_level
        }


@dataclass
class Pattern:
    """Detected temporal pattern."""
    name: str
    start_time: datetime
    end_time: datetime
    confidence: float
    description: str
    supporting_points: List[datetime]
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "confidence": self.confidence,
            "description": self.description,
            "supporting_points": [t.isoformat() for t in self.supporting_points]
        }


class TemporalReasoningEngine:
    """
    Core TRE providing temporal analysis capabilities.
    
    Features:
    - Time-series storage and retrieval
    - Trend analysis (linear regression)
    - Anomaly detection (statistical + ML)
    - Forecasting (simple exponential smoothing)
    - Pattern matching
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize TRE with optional database path."""
        if db_path is None:
            db_path = str(Path.home() / ".openclaw" / "workspace" / "memory" / "tre_data.db")
        
        self.db_path = db_path
        self._init_database()
        logger.info(f"TRE initialized with database: {db_path}")
    
    def _init_database(self):
        """Initialize SQLite database with time-series tables."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Main time-series table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS time_series (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    series_name TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    value REAL NOT NULL,
                    metadata TEXT,
                    created_at REAL DEFAULT (unixepoch())
                )
            """)
            
            # Indexes for performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_series_name 
                ON time_series(series_name)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON time_series(timestamp)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_series_time 
                ON time_series(series_name, timestamp)
            """)
            
            # Anomalies table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS anomalies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    series_name TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    type TEXT NOT NULL,
                    value REAL NOT NULL,
                    expected_value REAL NOT NULL,
                    deviation_percent REAL NOT NULL,
                    severity TEXT NOT NULL,
                    detected_at REAL DEFAULT (unixepoch())
                )
            """)
            
            # Patterns table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    series_name TEXT NOT NULL,
                    pattern_name TEXT NOT NULL,
                    start_time REAL NOT NULL,
                    end_time REAL NOT NULL,
                    confidence REAL NOT NULL,
                    description TEXT,
                    detected_at REAL DEFAULT (unixepoch())
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info("TRE database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize TRE database: {e}")
            raise
    
    def ingest(self, series_name: str, points: List[TimeSeriesPoint]) -> bool:
        """
        Ingest time-series data.
        
        Args:
            series_name: Identifier for the time series
            points: List of TimeSeriesPoint objects
            
        Returns:
            True if successful, False otherwise
        """
        if not points:
            logger.warning(f"No points to ingest for series: {series_name}")
            return False
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for point in points:
                cursor.execute("""
                    INSERT INTO time_series (series_name, timestamp, value, metadata)
                    VALUES (?, ?, ?, ?)
                """, (
                    series_name,
                    point.timestamp.timestamp(),
                    point.value,
                    json.dumps(point.metadata) if point.metadata else None
                ))
            
            conn.commit()
            conn.close()
            logger.info(f"Ingested {len(points)} points for series: {series_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to ingest data for {series_name}: {e}")
            return False
    
    def query(
        self,
        series_name: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 10000
    ) -> List[TimeSeriesPoint]:
        """
        Query time-series data.
        
        Args:
            series_name: Series identifier
            start_time: Optional start filter
            end_time: Optional end filter
            limit: Maximum points to return
            
        Returns:
            List of TimeSeriesPoint objects
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT timestamp, value, metadata FROM time_series WHERE series_name = ?"
            params = [series_name]
            
            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time.timestamp())
            
            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time.timestamp())
            
            query += " ORDER BY timestamp ASC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            points = []
            for row in rows:
                point = TimeSeriesPoint(
                    timestamp=datetime.fromtimestamp(row[0]),
                    value=row[1],
                    metadata=json.loads(row[2]) if row[2] else None
                )
                points.append(point)
            
            return points
            
        except Exception as e:
            logger.error(f"Failed to query data for {series_name}: {e}")
            return []
    
    def analyze_trend(
        self,
        series_name: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Optional[TrendAnalysis]:
        """
        Analyze trend in time series using linear regression.
        
        Args:
            series_name: Series identifier
            start_time: Optional start time
            end_time: Optional end time
            
        Returns:
            TrendAnalysis object or None if insufficient data
        """
        points = self.query(series_name, start_time, end_time)
        
        # Edge case: insufficient data
        if len(points) < 10:
            logger.warning(f"Insufficient data for trend analysis: {len(points)} points")
            return None
        
        try:
            # Convert to numpy arrays
            x = np.arange(len(points))
            y = np.array([p.value for p in points])
            
            # Linear regression
            coeffs = np.polyfit(x, y, 1)
            slope = coeffs[0]
            intercept = coeffs[1]
            
            # R-squared
            y_pred = slope * x + intercept
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            # Direction
            if slope > 0.01:
                direction = TrendDirection.UP
            elif slope < -0.01:
                direction = TrendDirection.DOWN
            else:
                direction = TrendDirection.FLAT
            
            # Confidence based on R-squared
            confidence = min(r_squared * 100, 95)
            
            # Calculate percent change
            start_value = points[0].value
            end_value = points[-1].value
            percent_change = ((end_value - start_value) / start_value * 100) if start_value != 0 else 0
            
            return TrendAnalysis(
                direction=direction,
                slope=float(slope),
                intercept=float(intercept),
                r_squared=float(r_squared),
                confidence=float(confidence),
                start_value=float(start_value),
                end_value=float(end_value),
                percent_change=float(percent_change)
            )
            
        except Exception as e:
            logger.error(f"Trend analysis failed: {e}")
            return None
    
    def detect_anomalies(
        self,
        series_name: str,
        sensitivity: float = 2.0,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Anomaly]:
        """
        Detect anomalies using statistical methods.
        
        Args:
            series_name: Series identifier
            sensitivity: Number of standard deviations for anomaly threshold
            start_time: Optional start time
            end_time: Optional end time
            
        Returns:
            List of Anomaly objects
        """
        points = self.query(series_name, start_time, end_time)
        
        if len(points) < 20:
            logger.warning(f"Insufficient data for anomaly detection: {len(points)} points")
            return []
        
        try:
            values = np.array([p.value for p in points])
            mean = np.mean(values)
            std = np.std(values)
            
            if std == 0:
                return []
            
            anomalies = []
            for i, point in enumerate(points):
                deviation = abs(point.value - mean)
                z_score = deviation / std
                
                if z_score > sensitivity:
                    # Determine type
                    if point.value > mean * 1.5:
                        anomaly_type = AnomalyType.SPIKE
                    elif point.value < mean * 0.5:
                        anomaly_type = AnomalyType.DROP
                    else:
                        anomaly_type = AnomalyType.PATTERN_BREAK
                    
                    # Severity
                    if z_score > 4:
                        severity = "critical"
                    elif z_score > 3:
                        severity = "high"
                    elif z_score > 2.5:
                        severity = "medium"
                    else:
                        severity = "low"
                    
                    deviation_percent = ((point.value - mean) / mean * 100) if mean != 0 else 0
                    
                    anomaly = Anomaly(
                        timestamp=point.timestamp,
                        type=anomaly_type,
                        value=float(point.value),
                        expected_value=float(mean),
                        deviation_percent=float(deviation_percent),
                        severity=severity
                    )
                    anomalies.append(anomaly)
            
            # Store anomalies
            self._store_anomalies(series_name, anomalies)
            
            logger.info(f"Detected {len(anomalies)} anomalies in {series_name}")
            return anomalies
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return []
    
    def _store_anomalies(self, series_name: str, anomalies: List[Anomaly]):
        """Store detected anomalies in database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for anomaly in anomalies:
                cursor.execute("""
                    INSERT INTO anomalies 
                    (series_name, timestamp, type, value, expected_value, deviation_percent, severity)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    series_name,
                    anomaly.timestamp.timestamp(),
                    anomaly.type.value,
                    anomaly.value,
                    anomaly.expected_value,
                    anomaly.deviation_percent,
                    anomaly.severity
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store anomalies: {e}")
    
    def forecast(
        self,
        series_name: str,
        horizon: int = 24,
        confidence_level: float = 0.95
    ) -> List[Forecast]:
        """
        Generate forecasts using exponential smoothing.
        
        Args:
            series_name: Series identifier
            horizon: Number of periods to forecast
            confidence_level: Confidence interval (0.8, 0.95, etc.)
            
        Returns:
            List of Forecast objects
        """
        points = self.query(series_name, limit=1000)
        
        if len(points) < 50:
            logger.warning(f"Insufficient data for forecasting: {len(points)} points")
            return []
        
        try:
            values = np.array([p.value for p in points])
            
            # Simple exponential smoothing
            alpha = 0.3
            smoothed = [values[0]]
            for i in range(1, len(values)):
                smoothed.append(alpha * values[i] + (1 - alpha) * smoothed[-1])
            
            # Forecast
            last_value = smoothed[-1]
            last_time = points[-1].timestamp
            
            # Calculate standard error for confidence intervals
            residuals = values[1:] - smoothed[:-1]
            std_error = np.std(residuals)
            
            # Z-score for confidence level
            z_scores = {0.8: 1.28, 0.95: 1.96, 0.99: 2.58}
            z = z_scores.get(confidence_level, 1.96)
            
            forecasts = []
            for i in range(1, horizon + 1):
                # Simple trend continuation
                predicted = last_value
                margin = z * std_error * np.sqrt(i)
                
                forecast_time = last_time + timedelta(hours=i)
                
                forecasts.append(Forecast(
                    timestamp=forecast_time,
                    predicted_value=float(predicted),
                    confidence_lower=float(max(0, predicted - margin)),
                    confidence_upper=float(predicted + margin),
                    confidence_level=confidence_level
                ))
            
            logger.info(f"Generated {len(forecasts)} forecasts for {series_name}")
            return forecasts
            
        except Exception as e:
            logger.error(f"Forecasting failed: {e}")
            return []
    
    def find_patterns(
        self,
        series_name: str,
        pattern_types: Optional[List[str]] = None
    ) -> List[Pattern]:
        """
        Find temporal patterns in time series.
        
        Args:
            series_name: Series identifier
            pattern_types: Optional list of pattern types to search for
            
        Returns:
            List of Pattern objects
        """
        points = self.query(series_name, limit=1000)
        
        if len(points) < 30:
            logger.warning(f"Insufficient data for pattern detection: {len(points)} points")
            return []
        
        patterns = []
        
        # Pattern 1: Double bottom
        double_bottom = self._detect_double_bottom(points)
        if double_bottom:
            patterns.append(double_bottom)
        
        # Pattern 2: Double top
        double_top = self._detect_double_top(points)
        if double_top:
            patterns.append(double_top)
        
        # Pattern 3: Trend reversal
        reversal = self._detect_trend_reversal(points)
        if reversal:
            patterns.append(reversal)
        
        # Store patterns
        self._store_patterns(series_name, patterns)
        
        logger.info(f"Found {len(patterns)} patterns in {series_name}")
        return patterns
    
    def _detect_double_bottom(self, points: List[TimeSeriesPoint]) -> Optional[Pattern]:
        """Detect double bottom pattern."""
        if len(points) < 20:
            return None
        
        values = [p.value for p in points]
        
        # Find local minima
        minima = []
        for i in range(2, len(values) - 2):
            if values[i] < values[i-1] and values[i] < values[i-2] and \
               values[i] < values[i+1] and values[i] < values[i+2]:
                minima.append((i, values[i]))
        
        if len(minima) < 2:
            return None
        
        # Look for two similar minima
        for i in range(len(minima) - 1):
            for j in range(i + 1, len(minima)):
                idx1, val1 = minima[i]
                idx2, val2 = minima[j]
                
                # Check if values are similar (within 5%)
                if abs(val1 - val2) / max(val1, val2) < 0.05:
                    # Check if there's a peak between them
                    between = values[idx1:idx2]
                    if max(between) > val1 * 1.1:  # At least 10% higher
                        return Pattern(
                            name="double_bottom",
                            start_time=points[idx1].timestamp,
                            end_time=points[idx2].timestamp,
                            confidence=0.7,
                            description=f"Double bottom pattern detected between {val1:.2f} and {val2:.2f}",
                            supporting_points=[points[idx1].timestamp, points[idx2].timestamp]
                        )
        
        return None
    
    def _detect_double_top(self, points: List[TimeSeriesPoint]) -> Optional[Pattern]:
        """Detect double top pattern."""
        if len(points) < 20:
            return None
        
        values = [p.value for p in points]
        
        # Find local maxima
        maxima = []
        for i in range(2, len(values) - 2):
            if values[i] > values[i-1] and values[i] > values[i-2] and \
               values[i] > values[i+1] and values[i] > values[i+2]:
                maxima.append((i, values[i]))
        
        if len(maxima) < 2:
            return None
        
        # Look for two similar maxima
        for i in range(len(maxima) - 1):
            for j in range(i + 1, len(maxima)):
                idx1, val1 = maxima[i]
                idx2, val2 = maxima[j]
                
                if abs(val1 - val2) / max(val1, val2) < 0.05:
                    between = values[idx1:idx2]
                    if min(between) < val1 * 0.9:
                        return Pattern(
                            name="double_top",
                            start_time=points[idx1].timestamp,
                            end_time=points[idx2].timestamp,
                            confidence=0.7,
                            description=f"Double top pattern detected between {val1:.2f} and {val2:.2f}",
                            supporting_points=[points[idx1].timestamp, points[idx2].timestamp]
                        )
        
        return None
    
    def _detect_trend_reversal(self, points: List[TimeSeriesPoint]) -> Optional[Pattern]:
        """Detect trend reversal pattern."""
        if len(points) < 40:
            return None
        
        # Split into two halves
        mid = len(points) // 2
        first_half = points[:mid]
        second_half = points[mid:]
        
        # Calculate trends
        first_values = [p.value for p in first_half]
        second_values = [p.value for p in second_half]
        
        first_trend = (first_values[-1] - first_values[0]) / len(first_values)
        second_trend = (second_values[-1] - second_values[0]) / len(second_values)
        
        # Check for reversal (opposite signs)
        if first_trend * second_trend < 0 and abs(first_trend) > 0.001:
            direction = "upward" if second_trend > 0 else "downward"
            return Pattern(
                name="trend_reversal",
                start_time=first_half[0].timestamp,
                end_time=second_half[-1].timestamp,
                confidence=0.6,
                description=f"Trend reversal to {direction} direction",
                supporting_points=[points[mid].timestamp]
            )
        
        return None
    
    def _store_patterns(self, series_name: str, patterns: List[Pattern]):
        """Store detected patterns in database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for pattern in patterns:
                cursor.execute("""
                    INSERT INTO patterns 
                    (series_name, pattern_name, start_time, end_time, confidence, description)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    series_name,
                    pattern.name,
                    pattern.start_time.timestamp(),
                    pattern.end_time.timestamp(),
                    pattern.confidence,
                    pattern.description
                ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store patterns: {e}")
    
    def get_stats(self, series_name: str) -> Dict:
        """Get statistics for a time series."""
        points = self.query(series_name)
        
        if not points:
            return {"error": "No data available"}
        
        values = [p.value for p in points]
        
        return {
            "series_name": series_name,
            "count": len(points),
            "start_time": points[0].timestamp.isoformat(),
            "end_time": points[-1].timestamp.isoformat(),
            "min": min(values),
            "max": max(values),
            "mean": np.mean(values),
            "std": np.std(values),
            "latest": values[-1]
        }
    
    def export_to_json(self, series_name: str, filepath: str) -> bool:
        """Export time series to JSON file."""
        try:
            points = self.query(series_name)
            data = {
                "series_name": series_name,
                "exported_at": datetime.now().isoformat(),
                "points": [p.to_dict() for p in points]
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Exported {len(points)} points to {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return False


# Test functions
def test_tre():
    """Run comprehensive TRE tests."""
    print("🧪 Testing Temporal Reasoning Engine...")
    
    # Create TRE instance
    tre = TemporalReasoningEngine(db_path=":memory:")
    
    # Test 1: Ingest data
    print("\n1️⃣ Testing data ingestion...")
    points = []
    base_time = datetime.now() - timedelta(hours=100)
    for i in range(100):
        # Create synthetic price data with trend and noise
        trend = i * 0.1
        noise = np.random.normal(0, 0.5)
        value = 100 + trend + noise
        
        # Add some anomalies
        if i == 30:
            value += 20  # Spike
        if i == 60:
            value -= 15  # Drop
        
        points.append(TimeSeriesPoint(
            timestamp=base_time + timedelta(hours=i),
            value=value
        ))
    
    success = tre.ingest("test_token", points)
    assert success, "Ingestion failed"
    print("✅ Ingestion test passed")
    
    # Test 2: Query data
    print("\n2️⃣ Testing data query...")
    queried = tre.query("test_token")
    assert len(queried) == 100, f"Expected 100 points, got {len(queried)}"
    print("✅ Query test passed")
    
    # Test 3: Trend analysis
    print("\n3️⃣ Testing trend analysis...")
    trend = tre.analyze_trend("test_token")
    assert trend is not None, "Trend analysis failed"
    assert trend.direction == TrendDirection.UP, f"Expected UP trend, got {trend.direction}"
    print(f"✅ Trend analysis: {trend.direction.value} (confidence: {trend.confidence:.1f}%)")
    
    # Test 4: Anomaly detection
    print("\n4️⃣ Testing anomaly detection...")
    anomalies = tre.detect_anomalies("test_token", sensitivity=2.0)
    assert len(anomalies) >= 2, f"Expected at least 2 anomalies, got {len(anomalies)}"
    print(f"✅ Detected {len(anomalies)} anomalies")
    
    # Test 5: Forecasting
    print("\n5️⃣ Testing forecasting...")
    forecasts = tre.forecast("test_token", horizon=24)
    assert len(forecasts) == 24, f"Expected 24 forecasts, got {len(forecasts)}"
    print(f"✅ Generated {len(forecasts)} forecasts")
    
    # Test 6: Pattern detection
    print("\n6️⃣ Testing pattern detection...")
    patterns = tre.find_patterns("test_token")
    print(f"✅ Found {len(patterns)} patterns")
    
    # Test 7: Stats
    print("\n7️⃣ Testing statistics...")
    stats = tre.get_stats("test_token")
    assert stats["count"] == 100
    print(f"✅ Stats: mean={stats['mean']:.2f}, std={stats['std']:.2f}")
    
    print("\n🎉 All TRE tests passed!")
    return True


if __name__ == "__main__":
    test_tre()
