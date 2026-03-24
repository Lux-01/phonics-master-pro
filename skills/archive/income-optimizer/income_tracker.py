#!/usr/bin/env python3
"""
Income Optimizer - Income Tracking System
Tracks all revenue streams, calculates MRR, and generates monthly reports.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
STATE_FILE = Path("/home/skux/.openclaw/workspace/memory/income_streams.json")
INCOME_HISTORY_FILE = Path("/home/skux/.openclaw/workspace/memory/income_history.json")

# Default income streams based on MEMORY.md analysis
DEFAULT_STREAMS = [
    {"name": "AOE Alpha Trading", "monthly_revenue": 0, "status": "active", "category": "crypto_trading"},
    {"name": "ATS Strategy Trading", "monthly_revenue": 0, "status": "active", "category": "crypto_trading"},
    {"name": "Skylar Strategy Live", "monthly_revenue": 0, "status": "active", "category": "crypto_trading"},
    {"name": "Whale Tracker Copy Trades", "monthly_revenue": 0, "status": "active", "category": "crypto_trading"},
    {"name": "SOL Staking Rewards", "monthly_revenue": 0, "status": "active", "category": "passive"},
    {"name": "DeFi Yield Farming", "monthly_revenue": 0, "status": "active", "category": "passive"},
    {"name": "Avatar Packs - Etsy", "monthly_revenue": 0, "status": "unknown", "category": "digital_products"},
    {"name": "Automation Scripts", "monthly_revenue": 0, "status": "unknown", "category": "digital_products"},
    {"name": "Research Services", "monthly_revenue": 0, "status": "planned", "category": "services"},
    {"name": "Trading Signal Subscription", "monthly_revenue": 0, "status": "planned", "category": "services"},
    {"name": "Consulting", "monthly_revenue": 0, "status": "unknown", "category": "services"},
    {"name": "Affiliate Revenue", "monthly_revenue": 0, "status": "planned", "category": "passive"},
    {"name": "Airdrops", "monthly_revenue": 0, "status": "opportunistic", "category": "opportunistic"},
]

def load_state():
    """Load or initialize the income streams state."""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    
    return {
        "streams": DEFAULT_STREAMS,
        "total_mrr": 0,
        "total_monthly": 0,
        "last_updated": datetime.now().isoformat(),
        "created_at": datetime.now().isoformat(),
        "monthly_history": []
    }

def save_state(state):
    """Save state to file."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    state["last_updated"] = datetime.now().isoformat()
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def calculate_mrr(state):
    """Calculate Monthly Recurring Revenue."""
    stable_recurring = 0
    variable_monthly = 0
    
    for stream in state["streams"]:
        if stream["status"] == "active" and stream["category"] in ["passive"]:
            stable_recurring += stream.get("monthly_revenue", 0)
        elif stream["status"] in ["active", "unknown"]:
            variable_monthly += stream.get("monthly_revenue", 0)
    
    return {
        "stable_recurring": stable_recurring,
        "variable_monthly": variable_monthly,
        "total_mrr": stable_recurring + variable_monthly
    }

def generate_monthly_report(state):
    """Generate monthly income report."""
    mrr = calculate_mrr(state)
    
    report = {
        "report_date": datetime.now().isoformat(),
        "report_period": (datetime.now() - timedelta(days=30)).strftime("%Y-%m") + " to " + datetime.now().strftime("%Y-%m"),
        "summary": {
            "total_mrr": mrr["total_mrr"],
            "stable_recurring": mrr["stable_recurring"],
            "variable_monthly": mrr["variable_monthly"],
            "stream_count": len(state["streams"]),
            "active_streams": len([s for s in state["streams"] if s["status"] == "active"])
        },
        "breakdown_by_category": {},
        "breakdown_by_status": {}
    }
    
    # Category breakdown
    categories = {}
    for stream in state["streams"]:
        cat = stream.get("category", "other")
        if cat not in categories:
            categories[cat] = {"streams": [], "total_revenue": 0}
        categories[cat]["streams"].append(stream)
        categories[cat]["total_revenue"] += stream.get("monthly_revenue", 0)
    report["breakdown_by_category"] = categories
    
    # Status breakdown
    statuses = {}
    for stream in state["streams"]:
        status = stream.get("status", "unknown")
        if status not in statuses:
            statuses[status] = {"count": 0, "total_revenue": 0}
        statuses[status]["count"] += 1
        statuses[status]["total_revenue"] += stream.get("monthly_revenue", 0)
    report["breakdown_by_status"] = statuses
    
    return report

def run_monthly_update():
    """Run the monthly income tracking update."""
    print("💰 Income Optimizer - Monthly Update")
    print("=" * 50)
    
    state = load_state()
    
    print(f"Tracking {len(state['streams'])} income streams")
    print()
    
    # Calculate MRR
    mrr = calculate_mrr(state)
    state["total_mrr"] = mrr["total_mrr"]
    state["total_monthly"] = mrr["total_mrr"]  # Simplified
    
    print("📊 Revenue Summary")
    print("-" * 40)
    print(f"  Stable Recurring:  ${mrr['stable_recurring']:,.2f}")
    print(f"  Variable Monthly:  ${mrr['variable_monthly']:,.2f}")
    print(f"  ─────────────────────────")
    print(f"  Total MRR:         ${mrr['total_mrr']:,.2f}")
    print()
    
    # Print streams by category
    categories = {}
    for stream in state["streams"]:
        cat = stream.get("category", "other")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(stream)
    
    print("📁 Revenue by Category")
    print("-" * 40)
    cat_emoji = {
        "crypto_trading": "📈",
        "digital_products": "🎨",
        "services": "🤝",
        "passive": "💤",
        "opportunistic": "🎁",
        "other": "📦"
    }
    for cat, streams in sorted(categories.items()):
        total = sum(s.get("monthly_revenue", 0) for s in streams)
        emoji = cat_emoji.get(cat, "📦")
        print(f"  {emoji} {cat.replace('_', ' ').title():<20} ${total:>10,.2f} ({len(streams)} streams)")
    print()
    
    # Print all streams
    print("📋 All Income Streams")
    print("-" * 40)
    status_emoji = {
        "active": "🟢",
        "planned": "📋",
        "unknown": "❓",
        "opportunistic": "🎁"
    }
    
    for stream in sorted(state["streams"], key=lambda x: x.get("monthly_revenue", 0), reverse=True):
        se = status_emoji.get(stream["status"], "⚪")
        print(f"  {se} {stream['name']:<35} ${stream.get('monthly_revenue', 0):>10,.2f}")
    print()
    
    # Growth opportunities
    print("💡 Growth Opportunities")
    print("-" * 40)
    planned = [s for s in state["streams"] if s["status"] == "planned"]
    if planned:
        for s in planned:
            print(f"  📋 {s['name']} - Activate for additional revenue")
    else:
        print("  ✨ All planned streams are active!")
    
    unknown = [s for s in state["streams"] if s["status"] == "unknown"]
    if unknown:
        print(f"\n  ⚠️  {len(unknown)} streams need status verification:")
        for s in unknown[:3]:
            print(f"     • {s['name']}")
    print()
    
    # Generate and store monthly report
    report = generate_monthly_report(state)
    state["monthly_history"].append({
        "month": datetime.now().strftime("%Y-%m"),
        "mrr": mrr["total_mrr"],
        "report": report
    })
    
    # Keep only last 12 months
    state["monthly_history"] = state["monthly_history"][-12:]
    
    save_state(state)
    
    print("✅ Monthly update complete. State saved.")
    print(f"📁 State file: {STATE_FILE}")
    print()

def update_stream_revenue(stream_name, revenue):
    """Update revenue for a specific stream."""
    state = load_state()
    
    for stream in state["streams"]:
        if stream["name"].lower() == stream_name.lower():
            stream["monthly_revenue"] = revenue
            stream["last_updated"] = datetime.now().isoformat()
            save_state(state)
            print(f"✅ Updated {stream_name}: ${revenue:,.2f}")
            return True
    
    print(f"⚠️ Stream '{stream_name}' not found")
    return False

def add_stream(name, category="other", status="planned", monthly_revenue=0):
    """Add a new income stream."""
    state = load_state()
    
    # Check if exists
    for stream in state["streams"]:
        if stream["name"].lower() == name.lower():
            print(f"⚠️ Stream '{name}' already exists")
            return False
    
    state["streams"].append({
        "name": name,
        "category": category,
        "status": status,
        "monthly_revenue": monthly_revenue,
        "created_at": datetime.now().isoformat()
    })
    
    save_state(state)
    print(f"✅ Added stream: {name}")
    return True

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "update" and len(sys.argv) == 4:
            update_stream_revenue(sys.argv[2], float(sys.argv[3]))
        elif command == "add" and len(sys.argv) >= 3:
            category = sys.argv[3] if len(sys.argv) > 3 else "other"
            status = sys.argv[4] if len(sys.argv) > 4 else "planned"
            revenue = float(sys.argv[5]) if len(sys.argv) > 5 else 0
            add_stream(sys.argv[2], category, status, revenue)
        else:
            print("Usage:")
            print("  python3 income_tracker.py              # Run monthly update")
            print("  python3 income_tracker.py update <stream> <amount>")
            print("  python3 income_tracker.py add <name> [category] [status] [revenue]")
    else:
        run_monthly_update()
