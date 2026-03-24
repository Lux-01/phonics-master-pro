#!/usr/bin/env python3
"""
Lux Status Dashboard - Quick overview of all systems
"""
import json
import os
from pathlib import Path
from datetime import datetime

def get_crypto_status():
    """Check crypto scanner status"""
    alpha_files = list(Path("/home/skux/.openclaw/workspace").glob("alpha_results_v*.json"))
    if alpha_files:
        latest = max(alpha_files, key=lambda p: p.stat().st_mtime)
        mtime = datetime.fromtimestamp(latest.stat().st_mtime)
        return f"{len(alpha_files)} versions | Latest: {latest.name} ({mtime.strftime('%Y-%m-%d')})"
    return "No data"

def get_skills_status():
    """Check skills health"""
    skills_dir = Path("/home/skux/.openclaw/workspace/skills")
    if skills_dir.exists():
        skill_count = len([d for d in skills_dir.iterdir() if d.is_dir()])
        return f"{skill_count} skills active"
    return "Unknown"

def get_website_status():
    """Check website projects"""
    demo_dir = Path("/home/skux/.openclaw/workspace/demo-site")
    if demo_dir.exists():
        return f"demo-site ready"
    return "No sites"

def get_moltbook_status():
    """Check moltbook activity"""
    state_file = Path("/home/skux/.openclaw/workspace/memory/moltbook_state.json")
    if state_file.exists():
        with open(state_file) as f:
            data = json.load(f)
        last_check = data.get("lastCheckISO", "unknown")
        return f"Last check: {last_check[:10]}"
    return "Not configured"

def get_subagents_status():
    """Check running sub-agents"""
    # Check process list for sub-agents
    import subprocess
    try:
        result = subprocess.run(["pgrep", "-c", "openclaw"], capture_output=True, text=True)
        count = int(result.stdout.strip()) if result.returncode == 0 else 0
        return f"{count} worker(s) running"
    except:
        return "Unable to check"

def main():
    print("╔═══════════════════════════════════════════════════╗")
    print("║           LUX SYSTEM STATUS DASHBOARD            ║")
    print("╠═══════════════════════════════════════════════════╣")
    print(f"║  Time: {datetime.now().strftime('%Y-%m-%d %H:%M'):<42}║")
    print("╠═══════════════════════════════════════════════════╣")
    print(f"║  🪙 Crypto Scans    │ {get_crypto_status():<32} ║")
    print(f"║  🧠 Skills          │ {get_skills_status():<32} ║")
    print(f"║  🎨 Websites        │ {get_website_status():<32} ║")
    print(f"║  🦞 Moltbook        │ {get_moltbook_status():<32} ║")
    print(f"║  ⚙️  Workers         │ {get_subagents_status():<32} ║")
    print("╚═══════════════════════════════════════════════════╝")

if __name__ == "__main__":
    main()
