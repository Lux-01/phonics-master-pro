#!/usr/bin/env python3
"""
KPI Performance Tracker v1.0
Tracks Key Performance Indicators across all systems

## ACA Plan:
1. Requirements: Track KPIs (trading, skills, income, system health) → calculate trends
2. Architecture: DataCollector → MetricCalculator → TrendAnalyzer → Reporter
3. Data Flow: Collect data → Calculate metrics → Detect trends → Generate reports
4. Edge Cases: No data history, missing files, division by zero, stale data
5. Tool Constraints: File read, JSON parse, datetime, calculations
6. Error Handling: Missing files, corrupt data, calc errors
7. Testing: Test with mock KPIs, verify calculations

Author: Autonomous Code Architect (ACA)
"""

import argparse
import json
import os
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("KPI")

# Configuration
WORKSPACE_DIR = Path("/home/skux/.openclaw/workspace")
MEMORY_DIR = WORKSPACE_DIR / "memory"
KPI_DIR = MEMORY_DIR / "kpi"


class MetricType(Enum):
    TRADING = "trading"
    SKILLS = "skills"
    INCOME = "income"
    SYSTEM = "system"


@dataclass
class KPIMetric:
    """Single KPI measurement"""
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime
    unit: str = ""
    target: Optional[float] = None
    trend: str = "stable"  # up, down, stable
    vs_last_period: float = 0.0  # percentage change
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "value": self.value,
            "metric_type": self.metric_type.value,
            "timestamp": self.timestamp.isoformat(),
            "unit": self.unit,
            "target": self.target,
            "trend": self.trend,
            "vs_last_period": self.vs_last_period
        }


class DataCollector:
    """Collects KPI data from various sources"""
    
    def collect_trading_kpis(self) -> List[Dict]:
        """Extract trading metrics"""
        kpis = []
        
        try:
            # Check trader results
            results_file = WORKSPACE_DIR / "agents" / "lux_trader" / "trades_6month.json"
            if results_file.exists():
                with open(results_file) as f:
                    data = json.load(f)
                
                # Fix: Handle both list and dict formats
                if isinstance(data, list):
                    trades = data
                else:
                    trades = data.get("trades", [])
                
                if trades:
                    # Use pnl_pct (not pnl_percent) based on actual data format
                    wins = len([t for t in trades if t.get("pnl_pct", 0) > 0])
                    losses = len([t for t in trades if t.get("pnl_pct", 0) <= 0])
                    total_pnl = sum(t.get("pnl_pct", 0) for t in trades)
                    
                    kpis.append({
                        "name": "win_rate",
                        "value": (wins / len(trades) * 100) if trades else 0,
                        "type": "trading",
                        "unit": "%"
                    })
                    
                    kpis.append({
                        "name": "total_pnl",
                        "value": total_pnl,
                        "type": "trading",
                        "unit": "%"
                    })
                    
                    kpis.append({
                        "name": "total_trades",
                        "value": len(trades),
                        "type": "trading",
                        "unit": "count"
                    })
        
        except Exception as e:
            logger.error(f"Error collecting trading KPIs: {e}")
        
        return kpis
    
    def collect_skills_kpis(self) -> List[Dict]:
        """Extract skills health metrics"""
        kpis = []
        
        try:
            see_file = MEMORY_DIR / "see" / "skill_health" / "all_skills.json"
            if see_file.exists():
                with open(see_file) as f:
                    data = json.load(f)
                
                if data:
                    scores = [v.get("health_score", 100) for v in data.values() if isinstance(v, dict)]
                    avg_health = sum(scores) / len(scores) if scores else 100
                    low_health = len([s for s in scores if s < 80])
                    
                    kpis.append({
                        "name": "skills_health_avg",
                        "value": avg_health,
                        "type": "skills",
                        "target": 95.0,
                        "unit": "score"
                    })
                    
                    kpis.append({
                        "name": "skills_needing_attention",
                        "value": low_health,
                        "type": "skills",
                        "unit": "count"
                    })
        
        except Exception as e:
            logger.error(f"Error collecting skills KPIs: {e}")
        
        return kpis
    
    def collect_system_kpis(self) -> List[Dict]:
        """Extract system health metrics"""
        kpis = []
        
        try:
            # Count active cron jobs
            import subprocess
            result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
            cron_count = len([l for l in result.stdout.split('\n') if l.strip() and not l.startswith('#')])
            
            kpis.append({
                "name": "active_cron_jobs",
                "value": cron_count,
                "type": "system",
                "unit": "count"
            })
            
            # Count skills
            skills_dir = WORKSPACE_DIR / "skills"
            skill_count = len([d for d in skills_dir.iterdir() if d.is_dir() and d.name not in ['dist', 'archive']])
            
            kpis.append({
                "name": "total_skills",
                "value": skill_count,
                "type": "system",
                "unit": "count"
            })
            
        except Exception as e:
            logger.error(f"Error collecting system KPIs: {e}")
        
        return kpis


class TrendAnalyzer:
    """Analyzes metric trends over time"""
    
    def calculate_trend(self, current: float, previous: Optional[float]) -> Tuple[str, float]:
        """Calculate trend direction and percentage change"""
        if previous is None or previous == 0:
            return "stable", 0.0
        
        change = ((current - previous) / previous) * 100
        
        if change > 5:
            return "up", change
        elif change < -5:
            return "down", change
        else:
            return "stable", change
    
    def analyze_all(self, metrics: List[KPIMetric], history: Dict) -> List[KPIMetric]:
        """Add trend analysis to all metrics"""
        analyzed = []
        
        for metric in metrics:
            # Find previous value
            previous = None
            if metric.name in history:
                prev_metric = history[metric.name]
                if isinstance(prev_metric, dict):
                    previous = prev_metric.get("value")
            
            trend, change = self.calculate_trend(metric.value, previous)
            metric.trend = trend
            metric.vs_last_period = change
            analyzed.append(metric)
        
        return analyzed


class KPIPerformanceTracker:
    """Main tracker class"""
    
    def __init__(self):
        self.collector = DataCollector()
        self.analyzer = TrendAnalyzer()
        self.metrics: List[KPIMetric] = []
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure required directories exist"""
        KPI_DIR.mkdir(parents=True, exist_ok=True)
    
    def load_history(self) -> Dict:
        """Load previous KPI snapshot"""
        history_file = KPI_DIR / "history.json"
        if not history_file.exists():
            return {}
        
        try:
            with open(history_file) as f:
                return json.load(f)
        except:
            return {}
    
    def save_current(self, metrics: List[KPIMetric]):
        """Save current KPI snapshot"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "metrics": {m.name: m.to_dict() for m in metrics}
        }
        
        history_file = KPI_DIR / "history.json"
        with open(history_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def generate_report(self, metrics: List[KPIMetric]) -> str:
        """Generate human-readable report"""
        report = []
        report.append("# KPI Performance Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append("")
        
        # Group by type
        by_type: Dict[str, List[KPIMetric]] = {}
        for m in metrics:
            t = m.metric_type.value
            if t not in by_type:
                by_type[t] = []
            by_type[t].append(m)
        
        for metric_type, type_metrics in by_type.items():
            report.append(f"## {metric_type.upper()}")
            report.append("")
            report.append("| Metric | Value | Trend | Target |")
            report.append("|--------|-------|-------|--------|")
            
            for m in type_metrics:
                trend_icon = "📈" if m.trend == "up" else "📉" if m.trend == "down" else "➡️"
                target_str = f"{m.target:.1f}" if m.target else "-"
                report.append(f"| {m.name} | {m.value:.2f}{m.unit} | {trend_icon} {m.vs_last_period:+.1f}% | {target_str} |")
            
            report.append("")
        
        # Add summary
        report.append("## Summary")
        report.append("")
        improving = len([m for m in metrics if m.trend == "up"])
        declining = len([m for m in metrics if m.trend == "down"])
        report.append(f"- **Improving:** {improving} metrics")
        report.append(f"- **Declining:** {declining} metrics")
        report.append(f"- **Total Tracked:** {len(metrics)} metrics")
        
        return "\n".join(report)
    
    def run(self, mode: str = "track") -> Dict:
        """Main execution"""
        # Collect data
        all_kpis = []
        all_kpis.extend(self.collector.collect_trading_kpis())
        all_kpis.extend(self.collector.collect_skills_kpis())
        all_kpis.extend(self.collector.collect_system_kpis())
        
        # Convert to KPIMetric objects
        metrics = [
            KPIMetric(
                name=k["name"],
                value=k["value"],
                metric_type=MetricType(k["type"]),
                timestamp=datetime.now(),
                unit=k.get("unit", ""),
                target=k.get("target")
            )
            for k in all_kpis
        ]
        
        # Analyze trends
        history = self.load_history()
        metrics = self.analyzer.analyze_all(metrics, history.get("metrics", {}))
        
        # Save
        self.save_current(metrics)
        
        if mode == "track":
            return {
                "success": True,
                "metrics_tracked": len(metrics),
                "by_type": {t.value: len([m for m in metrics if m.metric_type == t]) for t in MetricType}
            }
        
        elif mode == "report":
            report = self.generate_report(metrics)
            report_file = KPI_DIR / "report.md"
            with open(report_file, "w") as f:
                f.write(report)
            
            return {
                "success": True,
                "metrics_included": len(metrics),
                "report_saved": str(report_file)
            }
        
        return {"success": False, "error": f"Unknown mode: {mode}"}


def main():
    parser = argparse.ArgumentParser(description="KPI Performance Tracker")
    parser.add_argument("--mode", choices=["track", "report"], default="track")
    args = parser.parse_args()
    
    tracker = KPIPerformanceTracker()
    result = tracker.run(args.mode)
    
    if result.get("success"):
        print(f"✓ {args.mode.capitalize()} complete")
        for key, value in result.items():
            if key != "success":
                print(f"  {key}: {value}")
    else:
        print(f"✗ Error: {result.get('error')}")


if __name__ == "__main__":
    main()
