#!/usr/bin/env python3
"""
KPI Performance Tracker - Implementation
Track key performance indicators including trading metrics
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict


class KPIPerformanceTracker:
    """
    KPI Performance Tracker
    
    Tracks:
    - Skill performance metrics
    - Trading performance metrics (NEW)
    - Business KPIs
    - System health metrics
    """
    
    def __init__(self, memory_dir: str = None):
        self.memory_dir = memory_dir or os.path.expanduser("~/.openclaw/workspace/memory/kpi_tracker")
        self.metrics_file = os.path.join(self.memory_dir, "metrics.json")
        self.trading_metrics_file = os.path.join(self.memory_dir, "trading_metrics.json")
        self.reports_dir = os.path.join(self.memory_dir, "reports")
        self._ensure_dirs()
        self.metrics = self._load_metrics()
        self.trading_metrics = self._load_trading_metrics()
    
    def _ensure_dirs(self):
        Path(self.memory_dir).mkdir(parents=True, exist_ok=True)
        Path(self.reports_dir).mkdir(parents=True, exist_ok=True)
    
    def _load_metrics(self) -> Dict:
        try:
            if os.path.exists(self.metrics_file):
                with open(self.metrics_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {
            "skills": {},
            "business": {},
            "system": {},
            "last_updated": None
        }
    
    def _load_trading_metrics(self) -> Dict:
        try:
            if os.path.exists(self.trading_metrics_file):
                with open(self.trading_metrics_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {
            "daily_pnl": [],
            "trade_stats": {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0.0,
                "avg_win": 0.0,
                "avg_loss": 0.0,
                "profit_factor": 0.0,
                "sharpe_ratio": 0.0,
                "max_drawdown": 0.0
            },
            "strategy_performance": {},
            "monthly_summary": {},
            "last_updated": None
        }
    
    def _save(self):
        try:
            with open(self.metrics_file, 'w') as f:
                json.dump(self.metrics, f, indent=2)
            with open(self.trading_metrics_file, 'w') as f:
                json.dump(self.trading_metrics, f, indent=2)
        except Exception as e:
            print(f"Save error: {e}")
    
    # ============ TRADING METRICS ============
    
    def record_trade(self, trade: Dict):
        """
        Record a trade for metrics tracking
        
        trade: {
            "token": str,
            "entry_price": float,
            "exit_price": float,
            "size": float,
            "pnl": float,
            "pnl_percent": float,
            "entry_time": str (ISO format),
            "exit_time": str (ISO format),
            "strategy": str,
            "side": "long" | "short"
        }
        """
        # Update daily PnL
        trade_date = trade.get("exit_time", datetime.now().isoformat())[:10]
        
        daily_entry = next((d for d in self.trading_metrics["daily_pnl"] if d["date"] == trade_date), None)
        
        if daily_entry:
            daily_entry["pnl"] += trade.get("pnl", 0)
            daily_entry["trades"] += 1
        else:
            self.trading_metrics["daily_pnl"].append({
                "date": trade_date,
                "pnl": trade.get("pnl", 0),
                "trades": 1
            })
        
        # Update trade stats
        stats = self.trading_metrics["trade_stats"]
        stats["total_trades"] += 1
        
        pnl = trade.get("pnl", 0)
        if pnl > 0:
            stats["winning_trades"] += 1
        else:
            stats["losing_trades"] += 1
        
        # Recalculate derived metrics
        self._recalculate_trade_stats()
        
        # Update strategy performance
        strategy = trade.get("strategy", "unknown")
        if strategy not in self.trading_metrics["strategy_performance"]:
            self.trading_metrics["strategy_performance"][strategy] = {
                "trades": 0,
                "wins": 0,
                "losses": 0,
                "total_pnl": 0,
                "win_rate": 0.0,
                "avg_pnl": 0.0
            }
        
        strat_perf = self.trading_metrics["strategy_performance"][strategy]
        strat_perf["trades"] += 1
        strat_perf["total_pnl"] += pnl
        if pnl > 0:
            strat_perf["wins"] += 1
        else:
            strat_perf["losses"] += 1
        
        strat_perf["win_rate"] = strat_perf["wins"] / strat_perf["trades"] if strat_perf["trades"] > 0 else 0
        strat_perf["avg_pnl"] = strat_perf["total_pnl"] / strat_perf["trades"] if strat_perf["trades"] > 0 else 0
        
        self.trading_metrics["last_updated"] = datetime.now().isoformat()
        self._save()
    
    def _recalculate_trade_stats(self):
        """Recalculate derived trading statistics"""
        stats = self.trading_metrics["trade_stats"]
        
        if stats["total_trades"] > 0:
            stats["win_rate"] = stats["winning_trades"] / stats["total_trades"]
        
        # Calculate profit factor (gross wins / gross losses)
        daily_pnls = [d["pnl"] for d in self.trading_metrics["daily_pnl"]]
        if daily_pnls:
            gross_wins = sum(p for p in daily_pnls if p > 0)
            gross_losses = abs(sum(p for p in daily_pnls if p < 0))
            stats["profit_factor"] = gross_wins / gross_losses if gross_losses > 0 else gross_wins
        
        # Calculate Sharpe ratio (simplified)
        if len(daily_pnls) > 1:
            avg_return = sum(daily_pnls) / len(daily_pnls)
            variance = sum((p - avg_return) ** 2 for p in daily_pnls) / len(daily_pnls)
            std_dev = variance ** 0.5
            stats["sharpe_ratio"] = avg_return / std_dev if std_dev > 0 else 0
        
        # Calculate max drawdown
        if daily_pnls:
            cumulative = 0
            peak = 0
            max_dd = 0
            for pnl in daily_pnls:
                cumulative += pnl
                if cumulative > peak:
                    peak = cumulative
                drawdown = peak - cumulative
                if drawdown > max_dd:
                    max_dd = drawdown
            stats["max_drawdown"] = max_dd
    
    def get_trading_summary(self, days: int = 30) -> Dict:
        """Get trading summary for last N days"""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()[:10]
        
        recent_daily = [d for d in self.trading_metrics["daily_pnl"] if d["date"] >= cutoff]
        
        total_pnl = sum(d["pnl"] for d in recent_daily)
        total_trades = sum(d["trades"] for d in recent_daily)
        
        winning_days = len([d for d in recent_daily if d["pnl"] > 0])
        losing_days = len([d for d in recent_daily if d["pnl"] < 0])
        
        return {
            "period_days": days,
            "total_pnl": total_pnl,
            "total_trades": total_trades,
            "winning_days": winning_days,
            "losing_days": losing_days,
            "avg_daily_pnl": total_pnl / len(recent_daily) if recent_daily else 0,
            "best_day": max(recent_daily, key=lambda x: x["pnl"]) if recent_daily else None,
            "worst_day": min(recent_daily, key=lambda x: x["pnl"]) if recent_daily else None,
            "overall_stats": self.trading_metrics["trade_stats"],
            "strategy_performance": self.trading_metrics["strategy_performance"]
        }
    
    def generate_trading_report(self, days: int = 30) -> str:
        """Generate comprehensive trading report"""
        summary = self.get_trading_summary(days)
        stats = summary["overall_stats"]
        
        lines = [
            "📊 TRADING PERFORMANCE REPORT",
            "=" * 50,
            f"Period: Last {days} days",
            f"Generated: {datetime.now().isoformat()[:10]}",
            "",
            "💰 P&L SUMMARY",
            "-" * 30,
            f"Total P&L: ${summary['total_pnl']:.2f}",
            f"Avg Daily P&L: ${summary['avg_daily_pnl']:.2f}",
            f"Winning Days: {summary['winning_days']}",
            f"Losing Days: {summary['losing_days']}",
            "",
            "📈 TRADE STATISTICS",
            "-" * 30,
            f"Total Trades: {stats['total_trades']}",
            f"Win Rate: {stats['win_rate']:.1%}",
            f"Winning Trades: {stats['winning_trades']}",
            f"Losing Trades: {stats['losing_trades']}",
            f"Profit Factor: {stats['profit_factor']:.2f}",
            f"Sharpe Ratio: {stats['sharpe_ratio']:.2f}",
            f"Max Drawdown: ${stats['max_drawdown']:.2f}",
            "",
            "🎯 STRATEGY PERFORMANCE",
            "-" * 30,
        ]
        
        strategies = summary.get("strategy_performance", {})
        if strategies:
            for strategy, perf in sorted(strategies.items(), 
                                        key=lambda x: x[1].get("total_pnl", 0), 
                                        reverse=True):
                lines.append(f"{strategy}:")
                lines.append(f"  Trades: {perf['trades']}, Win Rate: {perf['win_rate']:.1%}")
                lines.append(f"  Total P&L: ${perf['total_pnl']:.2f}, Avg: ${perf['avg_pnl']:.2f}")
        else:
            lines.append("No strategy data recorded yet")
        
        if summary.get("best_day"):
            lines.extend([
                "",
                "🏆 BEST/WORST DAYS",
                "-" * 30,
                f"Best Day: {summary['best_day']['date']} (${summary['best_day']['pnl']:.2f})",
                f"Worst Day: {summary['worst_day']['date']} (${summary['worst_day']['pnl']:.2f})",
            ])
        
        lines.extend(["", "=" * 50])
        
        return "\n".join(lines)
    
    # ============ SKILL METRICS ============
    
    def record_skill_usage(self, skill_name: str, success: bool, duration: float, 
                          metadata: Dict = None):
        """Record skill usage metrics"""
        if skill_name not in self.metrics["skills"]:
            self.metrics["skills"][skill_name] = {
                "total_uses": 0,
                "successful_uses": 0,
                "failed_uses": 0,
                "total_duration": 0,
                "avg_duration": 0,
                "success_rate": 0.0,
                "last_used": None
            }
        
        skill = self.metrics["skills"][skill_name]
        skill["total_uses"] += 1
        skill["total_duration"] += duration
        
        if success:
            skill["successful_uses"] += 1
        else:
            skill["failed_uses"] += 1
        
        skill["success_rate"] = skill["successful_uses"] / skill["total_uses"]
        skill["avg_duration"] = skill["total_duration"] / skill["total_uses"]
        skill["last_used"] = datetime.now().isoformat()
        
        self.metrics["last_updated"] = datetime.now().isoformat()
        self._save()
    
    def get_skill_report(self) -> str:
        """Generate skill performance report"""
        lines = [
            "🔧 SKILL PERFORMANCE REPORT",
            "=" * 50,
        ]
        
        if not self.metrics["skills"]:
            lines.append("No skill usage recorded yet")
            return "\n".join(lines)
        
        # Sort by total uses
        sorted_skills = sorted(self.metrics["skills"].items(), 
                              key=lambda x: x[1]["total_uses"], 
                              reverse=True)
        
        for skill_name, stats in sorted_skills:
            lines.extend([
                f"\n{skill_name}:",
                f"  Uses: {stats['total_uses']}",
                f"  Success Rate: {stats['success_rate']:.1%}",
                f"  Avg Duration: {stats['avg_duration']:.1f}s",
                f"  Last Used: {stats['last_used'][:10] if stats['last_used'] else 'Never'}"
            ])
        
        return "\n".join(lines)
    
    # ============ ALERTING ============
    
    def check_alerts(self) -> List[str]:
        """Check for alert conditions"""
        alerts = []
        
        stats = self.trading_metrics["trade_stats"]
        
        # Check win rate
        if stats["total_trades"] >= 10 and stats["win_rate"] < 0.4:
            alerts.append(f"⚠️ Low win rate: {stats['win_rate']:.1%}. Review strategies.")
        
        # Check drawdown
        if stats["max_drawdown"] > 1000:
            alerts.append(f"⚠️ High drawdown: ${stats['max_drawdown']:.2f}. Consider risk reduction.")
        
        # Check daily PnL streak
        recent_days = self.trading_metrics["daily_pnl"][-5:]
        if len(recent_days) >= 3:
            losing_streak = all(d["pnl"] < 0 for d in recent_days[-3:])
            if losing_streak:
                alerts.append("⚠️ 3 consecutive losing days. Take a break and review.")
        
        return alerts


# ============ COMMAND LINE ============

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="KPI Performance Tracker")
    parser.add_argument("--mode", choices=["trading-report", "skill-report", "alerts", "record-trade", "test"], 
                       default="trading-report")
    parser.add_argument("--days", type=int, default=30, help="Number of days for report")
    parser.add_argument("--trade-file", help="JSON file with trade data to record")
    
    args = parser.parse_args()
    
    tracker = KPIPerformanceTracker()
    
    if args.mode == "trading-report":
        print(tracker.generate_trading_report(args.days))
    
    elif args.mode == "skill-report":
        print(tracker.get_skill_report())
    
    elif args.mode == "alerts":
        alerts = tracker.check_alerts()
        if alerts:
            print("🚨 ALERTS:")
            for alert in alerts:
                print(f"  {alert}")
        else:
            print("✅ No alerts - all metrics healthy")
    
    elif args.mode == "record-trade":
        if not args.trade_file:
            print("Error: --trade-file required")
            return
        
        with open(args.trade_file, 'r') as f:
            trade = json.load(f)
        
        tracker.record_trade(trade)
        print("✓ Trade recorded")
    
    elif args.mode == "test":
        print("🧪 Testing KPI Performance Tracker...")
        
        # Test trade recording
        test_trades = [
            {"token": "SOL", "pnl": 150, "pnl_percent": 0.15, "entry_time": "2026-03-01T09:00:00", 
             "exit_time": "2026-03-01T12:00:00", "strategy": "momentum", "size": 1000},
            {"token": "BONK", "pnl": -50, "pnl_percent": -0.05, "entry_time": "2026-03-01T14:00:00", 
             "exit_time": "2026-03-01T15:00:00", "strategy": "scalping", "size": 500},
            {"token": "SOL", "pnl": 200, "pnl_percent": 0.20, "entry_time": "2026-03-02T09:30:00", 
             "exit_time": "2026-03-02T14:00:00", "strategy": "momentum", "size": 1000},
        ]
        
        for trade in test_trades:
            tracker.record_trade(trade)
        
        print("✓ Trades recorded")
        
        # Test report generation
        report = tracker.generate_trading_report(days=30)
        print("✓ Trading report generated")
        
        # Test skill recording
        tracker.record_skill_usage("autonomous-trading-strategist", True, 5.5)
        tracker.record_skill_usage("autonomous-trading-strategist", True, 4.2)
        tracker.record_skill_usage("autonomous-trading-strategist", False, 3.0)
        print("✓ Skill metrics recorded")
        
        # Test alerts
        alerts = tracker.check_alerts()
        print(f"✓ Alerts checked: {len(alerts)} alerts found")
        
        print("\n✓ All tests passed")


if __name__ == "__main__":
    main()
