#!/usr/bin/env python3
"""
Skylar & AOE Daily Dashboard v1.0
Generated: 2026-03-12 15:15 AEDT
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple
import glob
import os

class TradingDashboard:
    """Daily trading system health monitor"""
    
    def __init__(self):
        self.workspace = Path("/home/skux/.openclaw/workspace")
        self.report = []
        
    def generate(self) -> str:
        """Generate full dashboard report"""
        self.report.append("=" * 70)
        self.report.append("📊 SKYLAR & AOE TRADING DASHBOARD")
        self.report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M AEDT')}")
        self.report.append("=" * 70)
        
        # Section 1: Skylar Live Positions
        self._skylar_section()
        
        # Section 2: Skylar Performance Analysis
        self._skylar_performance()
        
        # Section 3: AOE Scan Analysis
        self._aoe_section()
        
        # Section 4: System Health
        self._system_health()
        
        # Section 5: Action Items
        self._action_items()
        
        return "\n".join(self.report)
    
    def _skylar_section(self):
        """Active positions analysis"""
        active_file = self.workspace / "agents/skylar/skylar_active.json"
        
        self.report.append("\n" + "─" * 70)
        self.report.append("🤖 SKYLAR LIVE POSITIONS")
        self.report.append("─" * 70)
        
        if not active_file.exists():
            self.report.append("❌ No active positions file found")
            return
        
        with open(active_file) as f:
            data = json.load(f)
        
        positions = data.get("positions", [])
        
        if not positions:
            self.report.append("✅ No active positions (all closed)")
            return
        
        self.report.append(f"\nActive Positions: {len(positions)}")
        self.report.append(f"Cycle: {data.get('cycle', 'N/A')}")
        self.report.append("")
        
        for pos in positions:
            entry_time = datetime.fromtimestamp(pos.get("entryTime", 0)/1000)
            age = datetime.now() - entry_time
            
            self.report.append(f"  Trade #{pos.get('tradeNum')}: {pos.get('token', 'UNKNOWN')}")
            self.report.append(f"    Status: {pos.get('status')}")
            self.report.append(f"    Entry: {entry_time.strftime('%Y-%m-%d %H:%M')} ({age.days}d {age.seconds//3600}h ago)")
            self.report.append(f"    Size: {pos.get('inputSol')} SOL")
            self.report.append(f"    Grade/Score: {pos.get('grade')}/{pos.get('score')}")
            self.report.append(f"    Address: {pos.get('tokenAddress')[:20]}...")
            self.report.append("")
        
        # Warning for old positions
        old_positions = [p for p in positions if 
            datetime.now() - datetime.fromtimestamp(p.get("entryTime", 0)/1000) > timedelta(days=10)]
        
        if old_positions:
            self.report.append("⚠️  WARNING: Positions older than 10 days")
            self.report.append("    Consider manual review/closing")
    
    def _skylar_performance(self):
        """Learning log analysis"""
        log_file = self.workspace / "agents/skylar/skylar_learning_log.json"
        
        self.report.append("\n" + "─" * 70)
        self.report.append("📈 SKYLAR PERFORMANCE ANALYSIS")
        self.report.append("─" * 70)
        
        if not log_file.exists():
            self.report.append("❌ No learning log found")
            return
        
        with open(log_file) as f:
            trades = json.load(f)
        
        if not trades:
            self.report.append("No trades recorded")
            return
        
        # Calculate stats
        wins = [t for t in trades if t.get("result") == "win"]
        losses = [t for t in trades if t.get("result") in ["stop_loss", "rug_or_bag"]]
        
        win_pnl = sum(t.get("pnl_pct", 0) for t in wins)
        loss_pnl = sum(t.get("pnl_pct", 0) for t in losses)
        
        avg_win = win_pnl / len(wins) if wins else 0
        avg_loss = loss_pnl / len(losses) if losses else 0
        win_rate = len(wins) / len(trades) * 100 if trades else 0
        
        self.report.append(f"\nTotal Trades: {len(trades)}")
        self.report.append(f"Wins: {len(wins)} | Losses: {len(losses)}")
        self.report.append(f"Win Rate: {win_rate:.1f}%")
        self.report.append(f"Avg Win: +{avg_win:.1f}% | Avg Loss: {avg_loss:.1f}%")
        self.report.append(f"Net P&L: {win_pnl + loss_pnl:+.1f}%")
        
        # Key learnings
        self.report.append("\n🎯 Top Rules Learned:")
        rules_seen = set()
        for t in sorted(trades, key=lambda x: x.get("pnl_pct", 0), reverse=True)[:5]:
            rule = t.get("rule", "")
            if rule and rule not in rules_seen:
                self.report.append(f"  • {rule}")
                rules_seen.add(rule)
        
        self.report.append("\n⚠️  Common Mistakes:")
        mistakes = {}
        for t in trades:
            m = t.get("mistake", "")
            if m:
                mistakes[m] = mistakes.get(m, 0) + 1
        
        for m, count in sorted(mistakes.items(), key=lambda x: x[1], reverse=True)[:3]:
            self.report.append(f"  • {m} ({count}x)")
    
    def _aoe_section(self):
        """AOE scan analysis"""
        history_file = self.workspace / "memory/aoe_history.json"
        
        self.report.append("\n" + "─" * 70)
        self.report.append("🔥 AOE SCAN ANALYSIS")
        self.report.append("─" * 70)
        
        # Count log files
        log_files = glob.glob("/tmp/aoe_scan_*.log")
        self.report.append(f"\nTotal Scans (All Time): {len(log_files)}")
        
        # Today's scans
        today_prefix = datetime.now().strftime("%Y%m%d")
        today_logs = [f for f in log_files if today_prefix in f]
        self.report.append(f"Scans Today: {len(today_logs)}")
        
        # Latest scan
        if today_logs:
            latest = max(today_logs)
            self.report.append(f"\nLatest Scan: {Path(latest).name}")
            
            # Parse latest for highlights
            try:
                with open(latest) as f:
                    content = f.read()
                    
                # Find scores
                if "Score" in content:
                    self.report.append("\n📊 Today's Best Tokens:")
                    # Extract from DETAILED SCORE BREAKDOWN section
                    lines = content.split("\n")
                    in_scores = False
                    for line in lines:
                        if "DETAILED SCORE BREAKDOWN" in line:
                            in_scores = True
                            continue
                        if in_scores and line.strip() and not line.startswith("=") and not line.startswith("-") and "Symbol" not in line:
                            self.report.append(f"  {line.strip()}")
                        if in_scores and "SCORE TRENDS" in line:
                            break
                
                # Find trends
                if "SCORE TRENDS" in content:
                    self.report.append("\n📈 Notable Trends:")
                    lines = content.split("\n")
                    for line in lines:
                        if "→" in line:
                            self.report.append(f"  {line.strip()}")
            except Exception as e:
                self.report.append(f"Error parsing: {e}")
        
        # History file stats
        if history_file.exists():
            try:
                with open(history_file) as f:
                    history = json.load(f)
                self.report.append(f"\nHistory Records: {len(history)}")
                
                if history:
                    last = history[-1]
                    self.report.append(f"Last Update: {last.get('timestamp', 'N/A')[:16]}")
                    self.report.append(f"Tokens: {last.get('raw_count', 0)} → {last.get('final_count', 0)}")
            except:
                pass
    
    def _system_health(self):
        """System health check"""
        self.report.append("\n" + "─" * 70)
        self.report.append("🔧 SYSTEM HEALTH")
        self.report.append("─" * 70)
        
        # Disk usage
        self.report.append("\n💾 Disk Usage:")
        
        # AOE logs
        aoe_logs = glob.glob("/tmp/aoe_scan_*.log")
        aoe_size = sum(os.path.getsize(f) for f in aoe_logs) / 1024 / 1024
        self.report.append(f"  AOE Logs: {len(aoe_logs)} files ({aoe_size:.1f} MB)")
        
        # Workspace files
        workspace_logs = list(self.workspace.rglob("*.log"))
        ws_size = sum(os.path.getsize(f) for f in workspace_logs if f.exists()) / 1024 / 1024
        self.report.append(f"  Workspace Logs: {len(workspace_logs)} files ({ws_size:.1f} MB)")
        
        # JSON files
        json_files = list(self.workspace.rglob("*.json"))
        self.report.append(f"  JSON Data Files: {len(json_files)}")
        
        # Memory files
        memory_dir = self.workspace / "memory"
        if memory_dir.exists():
            mem_files = list(memory_dir.iterdir())
            self.report.append(f"  Memory Files: {len(mem_files)}")
        
        # Backup files
        backups = list(self.workspace.rglob("*.backup"))
        if backups:
            self.report.append(f"\n⚠️  Backup Files: {len(backups)} (consider cleaning)")
        
        # Temp files
        tmp_files = glob.glob("/tmp/*claw*") + glob.glob("/tmp/*aoe*")
        if len(tmp_files) > 20:
            self.report.append(f"\n⚠️  Temp Files: {len(tmp_files)} (consider cleaning)")
    
    def _action_items(self):
        """Generate action items"""
        self.report.append("\n" + "─" * 70)
        self.report.append("✅ ACTION ITEMS")
        self.report.append("─" * 70)
        
        actions = []
        
        # Check old positions
        active_file = self.workspace / "agents/skylar/skylar_active.json"
        if active_file.exists():
            with open(active_file) as f:
                data = json.load(f)
            positions = data.get("positions", [])
            old = [p for p in positions if 
                datetime.now() - datetime.fromtimestamp(p.get("entryTime", 0)/1000) > timedelta(days=10)]
            if old:
                actions.append(f"🔴 Review {len(old)} old Skylar positions (10+ days)")
        
        # Check queue
        queue_file = self.workspace / "memory/aoe_queue.json"
        if queue_file.exists():
            with open(queue_file) as f:
                queue = json.load(f)
            if queue.get("opportunities"):
                actions.append(f"📋 Review {len(queue['opportunities'])} tokens in AOE queue")
        
        # Log cleanup
        aoe_logs = glob.glob("/tmp/aoe_scan_*.log")
        if len(aoe_logs) > 50:
            actions.append(f"🧹 Clean up {len(aoe_logs)} AOE log files")
        
        # Backup cleanup
        backups = list(self.workspace.rglob("*.backup"))
        if backups:
            actions.append(f"🗑️  Remove {len(backups)} backup files")
        
        if actions:
            for action in actions:
                self.report.append(f"  {action}")
        else:
            self.report.append("  ✅ No immediate action items")


def main():
    dashboard = TradingDashboard()
    report = dashboard.generate()
    print(report)
    
    # Save to file
    output = Path("/home/skux/.openclaw/workspace/memory/daily_dashboard.txt")
    with open(output, 'w') as f:
        f.write(report)
    print(f"\n📄 Dashboard saved to: {output}")


if __name__ == "__main__":
    main()
