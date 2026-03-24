#!/usr/bin/env python3
"""
Income Tracker Dashboard
Tracks all revenue streams and progress toward Gold Coast Master Plan
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

class IncomeTracker:
    def __init__(self, data_dir="/home/skux/.openclaw/workspace/memory/income"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.data_file = self.data_dir / "streams.json"
        self.daily_file = self.data_dir / "daily.json"
        
    def load_data(self):
        """Load income stream data"""
        if self.data_file.exists():
            with open(self.data_file) as f:
                return json.load(f)
        return {
            "streams": {},
            "goals": {
                "gold_coast_total": 4500000,  # $4.5M target
                "monthly_income_target": 5000,  # Phase 1 target
                "current_phase": 1
            },
            "last_updated": datetime.now().isoformat()
        }
    
    def save_data(self, data):
        """Save income stream data"""
        data["last_updated"] = datetime.now().isoformat()
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_stream(self, name, category, target_monthly=0, notes=""):
        """Add a new income stream"""
        data = self.load_data()
        data["streams"][name] = {
            "category": category,
            "status": "active",
            "target_monthly": target_monthly,
            "actual_monthly": 0,
            "total_earned": 0,
            "start_date": datetime.now().isoformat(),
            "notes": notes,
            "performance_score": 0
        }
        self.save_data(data)
        print(f"✅ Added income stream: {name}")
    
    def record_earnings(self, stream_name, amount, date=None):
        """Record earnings for a stream"""
        data = self.load_data()
        if stream_name not in data["streams"]:
            print(f"❌ Stream '{stream_name}' not found")
            return
        
        date = date or datetime.now().strftime("%Y-%m-%d")
        
        # Update daily records
        daily = self.load_daily()
        if date not in daily:
            daily[date] = {}
        if stream_name not in daily[date]:
            daily[date][stream_name] = 0
        daily[date][stream_name] += amount
        self.save_daily(daily)
        
        # Update stream totals
        stream = data["streams"][stream_name]
        stream["total_earned"] += amount
        
        # Calculate monthly average (last 30 days)
        monthly = self.calculate_monthly(stream_name, daily)
        stream["actual_monthly"] = monthly
        
        # Calculate performance score (0-100)
        if stream["target_monthly"] > 0:
            stream["performance_score"] = min(100, (monthly / stream["target_monthly"]) * 100)
        
        self.save_data(data)
        print(f"💰 Recorded ${amount:.2f} for {stream_name}")
    
    def load_daily(self):
        """Load daily earnings"""
        if self.daily_file.exists():
            with open(self.daily_file) as f:
                return json.load(f)
        return {}
    
    def save_daily(self, data):
        """Save daily earnings"""
        with open(self.daily_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def calculate_monthly(self, stream_name, daily_data=None):
        """Calculate monthly earnings for a stream"""
        if daily_data is None:
            daily_data = self.load_daily()
        
        cutoff = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        total = 0
        
        for date, streams in daily_data.items():
            if date >= cutoff and stream_name in streams:
                total += streams[stream_name]
        
        return total
    
    def get_dashboard(self):
        """Generate income dashboard"""
        data = self.load_data()
        daily = self.load_daily()
        
        # Calculate totals
        total_earned = sum(s["total_earned"] for s in data["streams"].values())
        total_monthly = sum(s["actual_monthly"] for s in data["streams"].values())
        target_monthly = sum(s["target_monthly"] for s in data["streams"].values())
        
        # Progress to Gold Coast
        goal = data["goals"]["gold_coast_total"]
        progress_pct = (total_earned / goal) * 100 if goal > 0 else 0
        
        # Today's earnings
        today = datetime.now().strftime("%Y-%m-%d")
        today_earnings = sum(daily.get(today, {}).values())
        
        # This week's earnings
        week_start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        week_earnings = 0
        for date, streams in daily.items():
            if date >= week_start:
                week_earnings += sum(streams.values())
        
        return {
            "summary": {
                "total_earned": total_earned,
                "monthly_income": total_monthly,
                "target_monthly": target_monthly,
                "progress_to_goal": progress_pct,
                "today_earnings": today_earnings,
                "week_earnings": week_earnings
            },
            "streams": data["streams"],
            "goals": data["goals"]
        }
    
    def print_dashboard(self):
        """Print formatted dashboard"""
        dash = self.get_dashboard()
        s = dash["summary"]
        
        print("\n" + "="*60)
        print("💰 INCOME TRACKER DASHBOARD")
        print("="*60)
        
        print(f"\n📊 SUMMARY")
        print(f"  Total Earned: ${s['total_earned']:,.2f}")
        print(f"  Monthly Income: ${s['monthly_income']:,.2f} / ${s['target_monthly']:,.2f}")
        print(f"  Today's Earnings: ${s['today_earnings']:.2f}")
        print(f"  This Week: ${s['week_earnings']:.2f}")
        
        print(f"\n🎯 GOLD COAST PROGRESS")
        goal = dash["goals"]["gold_coast_total"]
        print(f"  ${s['total_earned']:,.2f} / ${goal:,.2f}")
        print(f"  Progress: {s['progress_to_goal']:.4f}%")
        bar_len = 30
        filled = int((s['progress_to_goal'] / 100) * bar_len)
        bar = "█" * filled + "░" * (bar_len - filled)
        print(f"  [{bar}]")
        
        print(f"\n📈 INCOME STREAMS")
        for name, stream in dash["streams"].items():
            status = "🟢" if stream["status"] == "active" else "🔴"
            perf = stream["performance_score"]
            perf_emoji = "🚀" if perf >= 100 else "📈" if perf >= 50 else "📉" if perf > 0 else "⚪"
            print(f"  {status} {name}")
            print(f"     Monthly: ${stream['actual_monthly']:.2f} / ${stream['target_monthly']:.2f}")
            print(f"     Total: ${stream['total_earned']:,.2f} {perf_emoji}")
        
        print("\n" + "="*60)

# Default streams for Tem's setup
DEFAULT_STREAMS = [
    ("LuxTrader v3.0", "trading", 1000, "Automated Solana trading"),
    ("Holy Trinity", "trading", 1500, "Multi-strategy trading system"),
    ("Skylar Paper", "trading", 0, "Paper trading for strategy testing"),
    ("AOE Scanner", "crypto", 500, "Alpha opportunity alerts"),
    ("v54 Scanner", "crypto", 300, "Token lifecycle monitoring"),
]

def init_default_streams():
    """Initialize default income streams"""
    tracker = IncomeTracker()
    for name, category, target, notes in DEFAULT_STREAMS:
        if name not in tracker.load_data()["streams"]:
            tracker.add_stream(name, category, target, notes)
    print("\n✅ Default streams initialized!")

if __name__ == "__main__":
    import sys
    
    tracker = IncomeTracker()
    
    if len(sys.argv) < 2:
        tracker.print_dashboard()
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "init":
        init_default_streams()
    elif cmd == "add" and len(sys.argv) >= 4:
        tracker.add_stream(sys.argv[2], sys.argv[3], 
                          float(sys.argv[4]) if len(sys.argv) > 4 else 0,
                          sys.argv[5] if len(sys.argv) > 5 else "")
    elif cmd == "earn" and len(sys.argv) >= 4:
        tracker.record_earnings(sys.argv[2], float(sys.argv[3]))
    elif cmd == "dashboard":
        tracker.print_dashboard()
    else:
        print("Usage:")
        print("  python3 income_tracker.py init")
        print("  python3 income_tracker.py add <name> <category> [target] [notes]")
        print("  python3 income_tracker.py earn <stream> <amount>")
        print("  python3 income_tracker.py dashboard")
