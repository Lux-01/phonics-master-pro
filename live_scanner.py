#!/usr/bin/env python3
"""
Live Scanner Results
Real-time scanner monitoring and display.
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Results storage
RESULTS_DIR = Path("/home/skux/.openclaw/workspace/memory/live_results")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

def run_protected_scan() -> Dict:
    """Run the protected scanner and capture results."""
    
    print("🔍 Running protected multi-scanner...")
    print("=" * 60)
    
    try:
        # Run the protected scanner
        result = subprocess.run(
            ["bash", "/home/skux/.openclaw/workspace/run_protected_scanners.sh"],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        # Parse results
        scan_result = {
            "timestamp": datetime.now().isoformat(),
            "status": "completed" if result.returncode == 0 else "error",
            "output": result.stdout,
            "errors": result.stderr if result.stderr else None,
            "signals": parse_scan_output(result.stdout)
        }
        
        # Save results
        save_results(scan_result)
        
        return scan_result
        
    except subprocess.TimeoutExpired:
        return {
            "timestamp": datetime.now().isoformat(),
            "status": "timeout",
            "signals": []
        }
    except Exception as e:
        return {
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "error": str(e),
            "signals": []
        }

def parse_scan_output(output: str) -> List[Dict]:
    """Parse scanner output for signals."""
    signals = []
    
    # Look for graded tokens in output
    lines = output.split('\n')
    current_signal = {}
    
    for line in lines:
        # Look for signal patterns
        if 'Grade A' in line or 'Grade A-' in line or 'Grade A+' in line:
            # Extract token info
            parts = line.split()
            for i, part in enumerate(parts):
                if part == 'Grade':
                    grade = parts[i+1] if i+1 < len(parts) else 'Unknown'
                    token = parts[0] if parts[0] != 'Grade' else 'Unknown'
                    
                    signals.append({
                        "token": token,
                        "grade": grade,
                        "status": "active",
                        "detected": datetime.now().isoformat()
                    })
    
    return signals

def save_results(result: Dict):
    """Save scan results to file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = RESULTS_DIR / f"scan_{timestamp}.json"
    
    with open(result_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    # Also update latest file
    latest_file = RESULTS_DIR / "latest_scan.json"
    with open(latest_file, 'w') as f:
        json.dump(result, f, indent=2)

def get_latest_results(limit: int = 5) -> List[Dict]:
    """Get most recent scan results."""
    
    results = []
    
    # Get all result files
    for result_file in sorted(RESULTS_DIR.glob("scan_*.json"), reverse=True)[:limit]:
        try:
            with open(result_file) as f:
                results.append(json.load(f))
        except:
            pass
    
    return results

def get_live_signals() -> List[Dict]:
    """Get current live signals."""
    
    latest = RESULTS_DIR / "latest_scan.json"
    if latest.exists():
        try:
            with open(latest) as f:
                data = json.load(f)
                return data.get("signals", [])
        except:
            pass
    
    return []

def display_dashboard():
    """Display live scanner dashboard."""
    
    print("\n" + "=" * 80)
    print("🔴 LIVE SCANNER DASHBOARD".center(80))
    print("=" * 80)
    print(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 80)
    
    # Get latest results
    results = get_latest_results(3)
    
    if not results:
        print("\n⚠️  No scan results available yet.")
        print("   Run: python3 live_scanner.py --scan")
        print()
        return
    
    # Show recent scans
    print("\n📊 RECENT SCANS:")
    for i, result in enumerate(results, 1):
        timestamp = result.get('timestamp', 'Unknown')
        status = result.get('status', 'Unknown')
        signal_count = len(result.get('signals', []))
        
        status_icon = "✅" if status == "completed" else "❌"
        print(f"   {i}. {timestamp} - {status_icon} {status.title()} ({signal_count} signals)")
    
    # Show current signals
    signals = get_live_signals()
    
    print("\n🎯 CURRENT SIGNALS:")
    if signals:
        for sig in signals:
            token = sig.get('token', 'Unknown')
            grade = sig.get('grade', 'Unknown')
            icon = "🟢" if grade == "A+" else "🟡" if grade == "A" else "🟠"
            print(f"   {icon} {token} - Grade {grade}")
    else:
        print("   No active signals")
    
    # Show next scan time
    print("\n⏰ NEXT SCAN:")
    print("   Check cron schedule: openclaw cron list")
    print()
    
    print("-" * 80)
    print("Commands:")
    print("   python3 live_scanner.py --scan    Run scanner now")
    print("   python3 live_scanner.py --watch   Auto-refresh every 5 min")
    print("   python3 live_scanner.py --export Export to dashboard")
    print("=" * 80)

def watch_mode():
    """Watch mode - auto refresh every 5 minutes."""
    import time
    
    print("\n🔴 WATCH MODE ENABLED")
    print("   Auto-refresh every 5 minutes")
    print("   Press Ctrl+C to stop\n")
    
    try:
        while True:
            run_protected_scan()
            display_dashboard()
            print("\n   Sleeping for 5 minutes...")
            time.sleep(300)  # 5 minutes
    except KeyboardInterrupt:
        print("\n   Watch mode stopped.")

def export_for_dashboard():
    """Export latest results for dashboard display."""
    
    signals = get_live_signals()
    results = get_latest_results(5)
    
    export_data = {
        "last_scan": results[0].get('timestamp') if results else None,
        "scan_count": len(results),
        "total_signals": sum(len(r.get('signals', [])) for r in results),
        "active_signals": signals,
        "recent_scans": [
            {
                "timestamp": r.get('timestamp'),
                "signal_count": len(r.get('signals', [])),
                "status": r.get('status')
            }
            for r in results[:5]
        ]
    }
    
    # Save for dashboard
    dashboard_data = RESULTS_DIR / "dashboard_export.json"
    with open(dashboard_data, 'w') as f:
        json.dump(export_data, f, indent=2)
    
    return export_data

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "--scan":
            result = run_protected_scan()
            print(f"\n✅ Scan complete: {result['status']}")
            print(f"   Signals found: {len(result.get('signals', []))}")
            export_for_dashboard()
        
        elif command == "--watch":
            watch_mode()
        
        elif command == "--export":
            data = export_for_dashboard()
            print("📊 Dashboard export updated")
            print(f"   Signals: {len(data['active_signals'])}")
            print(f"   Recent scans: {data['scan_count']}")
        
        else:
            print(f"Unknown command: {command}")
            print("Usage:")
            print("  python3 live_scanner.py           Show dashboard")
            print("  python3 live_scanner.py --scan    Run scanner now")
            print("  python3 live_scanner.py --watch   Auto-refresh mode")
            print("  python3 live_scanner.py --export  Export for dashboard")
    else:
        display_dashboard()
