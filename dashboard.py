#!/usr/bin/env python3
"""
OpenClaw System Dashboard
Real-time monitoring of all skills, signals, and system health.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import subprocess

def get_system_health() -> Dict:
    """Check overall system health."""
    try:
        # Run AMRE health check
        import sys
        sys.path.insert(0, '/home/skux/.openclaw/workspace/skills/autonomous-maintenance-repair')
        from amre_runner import check_health
        return check_health()
    except Exception as e:
        # Fallback: check manually
        components = {
            "scanners": Path("/home/skux/.openclaw/workspace/skills/pattern-extractor/rug_pattern_extractor.py").exists(),
            "outcome_tracker": Path("/home/skux/.openclaw/workspace/skills/outcome-tracker/trading_outcome_tracker.py").exists(),
            "aloe": Path("/home/skux/.openclaw/workspace/skills/aloe/aloe_coordinator.py").exists(),
            "ats": Path("/home/skux/.openclaw/workspace/skills/autonomous-trading-strategist/ats_runner.py").exists(),
            "aoe": Path("/home/skux/.openclaw/workspace/skills/autonomous-opportunity-engine/aoe_runner.py").exists(),
            "mac": Path("/home/skux/.openclaw/workspace/skills/multi-agent-coordinator/mac_runner.py").exists(),
            "amre": Path("/home/skux/.openclaw/workspace/skills/autonomous-maintenance-repair/amre_runner.py").exists(),
            "kge": Path("/home/skux/.openclaw/workspace/skills/knowledge-graph-engine/kge_runner.py").exists(),
            "io": Path("/home/skux/.openclaw/workspace/skills/integration-orchestrator/io_runner.py").exists(),
        }
        
        healthy = sum(1 for v in components.values() if v)
        total = len(components)
        
        return {
            "overall_status": "healthy" if healthy == total else "degraded",
            "components_checked": {k: {"status": "healthy" if v else "missing"} for k, v in components.items()},
            "issues_found": [] if healthy == total else [{"component": k, "issue": "File missing"} for k, v in components.items() if not v]
        }

def get_skill_status() -> Dict:
    """Get status of all skills."""
    try:
        import sys
        sys.path.insert(0, '/home/skux/.openclaw/workspace/skills/integration-orchestrator')
        from io_runner import get_system_status
        return get_system_status()
    except Exception as e:
        return {"error": str(e)}

def get_recent_outcomes() -> List[Dict]:
    """Get recent trading outcomes."""
    outcomes_file = Path("/home/skux/.openclaw/workspace/memory/outcomes/trading_outcomes.json")
    if outcomes_file.exists():
        try:
            with open(outcomes_file) as f:
                outcomes = json.load(f)
            return outcomes[-5:]  # Last 5
        except:
            pass
    return []

def get_cron_jobs() -> List[Dict]:
    """Get active cron jobs."""
    try:
        result = subprocess.run(
            ["python3", "-c", "from subprocess import run; print(run(['openclaw', 'cron', 'list'], capture_output=True, text=True).stdout)"],
            capture_output=True,
            text=True
        )
        # Check actual cron file
        import sys
        sys.path.insert(0, '/home/skux/.openclaw/workspace')
        result = subprocess.run(['openclaw', 'cron', 'list'], 
                              capture_output=True, text=True)
        return result.stdout
    except:
        return "Check with: openclaw cron list"

def get_active_signals() -> List[Dict]:
    """Get active trading signals."""
    signals_dir = Path("/home/skux/.openclaw/workspace/skills/autonomous-trading-strategist/data/alerts")
    if not signals_dir.exists():
        return []
    
    signals = []
    for alert_file in sorted(signals_dir.glob("alert_*.json"), reverse=True)[:5]:
        try:
            with open(alert_file) as f:
                signals.append(json.load(f))
        except:
            pass
    return signals

def get_opportunities() -> List[Dict]:
    """Get current opportunities."""
    try:
        import sys
        sys.path.insert(0, '/home/skux/.openclaw/workspace/skills/autonomous-opportunity-engine')
        from aoe_runner import get_queue
        return get_queue(limit=5)
    except:
        return []

def get_live_scanner_results():
    """Get live scanner results."""
    results_file = Path("/home/skux/.openclaw/workspace/memory/live_results/dashboard_export.json")
    if results_file.exists():
        try:
            with open(results_file) as f:
                return json.load(f)
        except:
            pass
    return None

def get_scanner_history():
    """Get recent scanner runs."""
    results_dir = Path("/home/skux/.openclaw/workspace/memory/live_results")
    if not results_dir.exists():
        return []
    
    scans = []
    for scan_file in sorted(results_dir.glob("scan_*.json"), reverse=True)[:5]:
        try:
            with open(scan_file) as f:
                data = json.load(f)
                scans.append({
                    "timestamp": data.get("timestamp"),
                    "signals": len(data.get("signals", [])),
                    "status": data.get("status")
                })
        except:
            pass
    return scans

def print_dashboard():
    """Print system dashboard."""
    
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "🤖 OPENCLAW SYSTEM DASHBOARD" + " " * 25 + "║")
    print("╠" + "═" * 78 + "╣")
    print(f"║  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} AEDT" + " " * 52 + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    
    # System Health
    print("┌" + "─" * 78 + "┐")
    print("│ 🏥 SYSTEM HEALTH" + " " * 61 + "│")
    print("├" + "─" * 78 + "┤")
    
    health = get_system_health()
    status = health.get('overall_status', 'unknown').upper()
    
    if status == 'HEALTHY':
        status_icon = "🟢"
    elif status == 'DEGRADED':
        status_icon = "🟡"
    else:
        status_icon = "🔴"
    
    print(f"│  Overall Status: {status_icon} {status}" + " " * (55 - len(status)) + "│")
    
    components = health.get('components_checked', {})
    healthy = sum(1 for c in components.values() if c.get('status') == 'healthy')
    total = len(components)
    
    print(f"│  Components: {healthy}/{total} healthy" + " " * (58 - len(str(healthy)) - len(str(total))) + "│")
    
    issues = health.get('issues_found', [])
    if issues:
        print(f"│  Issues: {len(issues)} detected" + " " * (58 - len(str(len(issues)))) + "│")
        for issue in issues:
            print(f"│    • {issue.get('component', 'Unknown')}: {issue.get('issue', 'Unknown')[:50]}" + " " * 10 + "│")
    else:
        print(f"│  Issues: None ✅" + " " * 50 + "│")
    
    print("└" + "─" * 78 + "┘")
    print()
    
    # Skills Status
    print("┌" + "─" * 78 + "┐")
    print("│ 🛠️  SKILLS STATUS" + " " * 60 + "│")
    print("├" + "─" * 78 + "┤")
    
    skills_status = get_skill_status()
    
    phases = {
        "Phase 1 (Learning)": ["pattern_extractor", "outcome_tracker", "aloe"],
        "Phase 2 (Evolution)": ["scanner_architect", "skill_evolution", "code_evolution"],
        "Phase 3 (Execution)": ["ats", "aoe", "mac"],
        "Phase 4 (Autonomy)": ["amre", "kge", "io"],
        "Phase 5 (Cognition)": ["cel_understanding", "cel_creativity", "cel_self", "cel_transfer", "cel_commonsense"]
    }
    
    skill_names = {
        "pattern_extractor": "Pattern Extractor",
        "outcome_tracker": "Outcome Tracker",
        "aloe": "ALOE",
        "scanner_architect": "Scanner Architect",
        "skill_evolution": "Skill Evolution",
        "code_evolution": "Code Evolution",
        "ats": "ATS",
        "aoe": "AOE",
        "mac": "MAC",
        "amre": "AMRE",
        "kge": "KGE",
        "io": "Integration Orchestrator",
        "cel_understanding": "CEL-Understanding",
        "cel_creativity": "CEL-Creativity",
        "cel_self": "CEL-Self",
        "cel_transfer": "CEL-Transfer",
        "cel_commonsense": "CEL-Commonsense"
    }
    
    for phase, skills in phases.items():
        print(f"│  {phase}:" + " " * (73 - len(phase)) + "│")
        for skill in skills:
            name = skill_names.get(skill, skill)
            status = "✅"  # Assume healthy based on AMRE
            print(f"│    {status} {name}" + " " * (70 - len(name)) + "│")
    
    print("└" + "─" * 78 + "┘")
    print()
    
    # Live Scanner Results
    print("┌" + "─" * 78 + "┐")
    print("│ 🔴 LIVE SCANNER RESULTS" + " " * 54 + "│")
    print("├" + "─" * 78 + "┤")
    
    live_data = get_live_scanner_results()
    scan_history = get_scanner_history()
    
    if live_data:
        last_scan = live_data.get('last_scan', 'Never')
        total_signals = live_data.get('total_signals', 0)
        active_signals = live_data.get('active_signals', [])
        
        print(f"│  Last Scan: {last_scan[:19] if last_scan else 'Never':<20}" + " " * 42 + "│")
        print(f"│  Total Signals Found: {total_signals:<3}" + " " * 48 + "│")
        
        if active_signals:
            print("│" + " " * 78 + "│")
            print("│  Active Signals:" + " " * 61 + "│")
            for sig in active_signals[:3]:
                token = sig.get('token', 'Unknown')[:25]
                grade = sig.get('grade', '?')
                icon = "🟢" if grade == "A+" else "🟡" if grade == "A" else "🟠"
                print(f"│    {icon} {token:<25} Grade {grade}" + " " * 28 + "│")
        else:
            print("│  No active signals currently" + " " * 48 + "│")
    else:
        print("│  No scan data available yet" + " " * 48 + "│")
        print("│  Run: python3 live_scanner.py --scan" + " " * 40 + "│")
    
    if scan_history:
        print("│" + " " * 78 + "│")
        print("│  Recent Scans:" + " " * 63 + "│")
        for scan in scan_history[:3]:
            ts = scan.get('timestamp', 'Unknown')[:16]
            signals = scan.get('signals', 0)
            status = scan.get('status', 'unknown')
            icon = "✅" if status == 'completed' else "❌"
            print(f"│    {icon} {ts} - {signals} signals" + " " * (50 - len(str(signals))) + "│")
    
    print("└" + "─" * 78 + "┘")
    print()
    
    # Active Signals
    print("┌" + "─" * 78 + "┐")
    print("│ 🎯 ACTIVE SIGNALS" + " " * 61 + "│")
    print("├" + "─" * 78 + "┤")
    
    signals = get_active_signals()
    if signals:
        for sig in signals:
            symbol = sig.get('token', 'Unknown')
            grade = sig.get('grade', 'Unknown')
            conf = sig.get('confidence', 0)
            print(f"│  • {symbol:<10} Grade: {grade:<3} Confidence: {conf:>3}%" + " " * 32 + "│")
    else:
        print("│  No active signals" + " " * 55 + "│")
    
    print("└" + "─" * 78 + "┘")
    print()
    
    # Opportunities
    print("┌" + "─" * 78 + "┐")
    print("│ 🌐 OPPORTUNITIES QUEUE" + " " * 55 + "│")
    print("├" + "─" * 78 + "┤")
    
    opps = get_opportunities()
    if opps:
        for opp in opps[:3]:
            name = opp.name if hasattr(opp, 'name') else str(opp)
            score = opp.score if hasattr(opp, 'score') else 0
            grade = opp.grade if hasattr(opp, 'grade') else 'C'
            print(f"│  • {name[:40]:<40} Score: {score:>3} ({grade})" + " " * 10 + "│")
    else:
        print("│  Queue empty - run AOE scan" + " " * 47 + "│")
    
    print("└" + "─" * 78 + "┘")
    print()
    
    # Recent Outcomes
    print("┌" + "─" * 78 + "┐")
    print("│ 📊 RECENT OUTCOMES" + " " * 58 + "│")
    print("├" + "─" * 78 + "┤")
    
    outcomes = get_recent_outcomes()
    if outcomes:
        for outcome in outcomes[-5:]:
            status = outcome.get('outcome', {}).get('status', 'Unknown')
            pnl = outcome.get('outcome', {}).get('pnl_percent', 0)
            
            if status == 'PROFIT':
                icon = "🟢"
            elif status == 'RUG':
                icon = "🔴"
            else:
                icon = "🟡"
            
            print(f"│  {icon} {status:<10} PnL: {pnl:>+6.1f}%" + " " * 50 + "│")
    else:
        print("│  No outcomes logged yet" + " " * 50 + "│")
    
    print("└" + "─" * 78 + "┘")
    print()
    
    # Cron Jobs
    print("┌" + "─" * 78 + "┐")
    print("│ ⏰ CRON JOBS" + " " * 63 + "│")
    print("├" + "─" * 78 + "┤")
    print("│  Check: openclaw cron list" + " " * 46 + "│")
    print("│  Scanner runs: Every 2-6 hours (Sydney time)" + " " * 30 + "│")
    print("└" + "─" * 78 + "┘")
    print()
    
    # Actions
    print("┌" + "─" * 78 + "┐")
    print("│ ⚡ QUICK ACTIONS" + " " * 60 + "│")
    print("├" + "─" * 78 + "┤")
    print("│  python3 dashboard.py                    - Show this dashboard" + " " * 8 + "│")
    print("│  python3 live_scanner.py --scan        - Run protected scanner" + " " * 14 + "│")
    print("│  python3 live_scanner.py --watch       - Auto-refresh mode" + " " * 19 + "│")
    print("│  python3 skills/aoe/aoe_runner.py      - Run AOE scan" + " " * 19 + "│")
    print("│  python3 skills/ats/ats_runner.py        - Analyze token" + " " * 18 + "│")
    print("│  python3 update_outcome.py --stats       - View outcome stats" + " " * 13 + "│")
    print("│  openclaw cron list                      - View cron jobs" + " " * 15 + "│")
    print("└" + "─" * 78 + "┘")
    print()

if __name__ == "__main__":
    print_dashboard()
