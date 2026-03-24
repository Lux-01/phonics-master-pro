#!/usr/bin/env python3
"""
Skill Activation Manager (SAM)
Weekly auditor that checks skill health, wakes dormant skills, and suggests activations.
"""

import json
import os
import glob
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
SKILLS_DIR = Path("/home/skux/.openclaw/workspace/skills")
STATE_DIR = Path("/home/skux/.openclaw/workspace/memory")
STATE_FILE = STATE_DIR / "skill_activation_state.json"

# Dormancy thresholds (days)
THRESHOLDS = {
    "active": 7,
    "under_utilized": 21,
    "dormant": 45,
    "forgotten": 90
}

SKILL_EMOJIS = {
    "context-optimizer": "🧠",
    "decision-log": "📋",
    "workspace-organizer": "🗂️",
    "research-synthesizer": "🔬",
    "tool-orchestrator": "🛠️",
    "code-evolution-tracker": "📈",
    "memory-manager": "🧬",
    "autonomous-agent": "🤖",
    "aloe": "🌱",
    "sensory-input-layer": "👁️",
    "multi-agent-coordinator": "👥",
    "autonomous-trading-strategist": "📊",
    "long-term-project-manager": "📅",
    "autonomous-workflow-builder": "⚡",
    "knowledge-graph-engine": "🕸️",
    "autonomous-opportunity-engine": "🎯",
    "skill-evolution-engine": "🧬",
    "autonomous-code-architect": "🏗️",
    "skill-activation-manager": "⏰",
    "income-optimizer": "💰",
    "event-bus": "📡",
    "integration-orchestrator": "🔗"
}

def get_skill_list():
    """Get all skills from the skills directory."""
    skills = []
    if not SKILLS_DIR.exists():
        return skills
    
    for item in SKILLS_DIR.iterdir():
        if item.is_dir() and (item / "SKILL.md").exists():
            skills.append(item.name)
    return skills

def load_state():
    """Load or initialize the state file."""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    
    return {
        "last_audit": None,
        "skills": {},
        "audit_history": [],
        "activation_suggestions": [],
        "created_at": datetime.now().isoformat()
    }

def save_state(state):
    """Save state to file."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def get_last_modified(skill_name):
    """Get last modified time of skill files."""
    skill_dir = SKILLS_DIR / skill_name
    if not skill_dir.exists():
        return None
    
    # Check SKILL.md and scripts directory
    files_to_check = [skill_dir / "SKILL.md"]
    scripts_dir = skill_dir / "scripts"
    if scripts_dir.exists():
        files_to_check.extend(scripts_dir.glob("*.py"))
    
    latest = None
    for file_path in files_to_check:
        if file_path.exists():
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            if latest is None or mtime > latest:
                latest = mtime
    
    return latest

def check_memory_references(skill_name):
    """Check if skill is referenced in memory files."""
    memory_dir = Path("/home/skux/.openclaw/workspace/memory")
    if not memory_dir.exists():
        return 0
    
    mentions = 0
    for memory_file in memory_dir.glob("*.md"):
        try:
            content = memory_file.read_text()
            if skill_name.replace("-", " ") in content.lower() or skill_name in content:
                mentions += 1
        except:
            pass
    
    return mentions

def get_skill_health(skill_name, state):
    """Calculate health metrics for a skill."""
    skill_data = state["skills"].get(skill_name, {})
    last_used = skill_data.get("last_used")
    
    if last_used:
        last_used_dt = datetime.fromisoformat(last_used)
        days_dormant = (datetime.now() - last_used_dt).days
    else:
        # Check file modification as fallback
        last_modified = get_last_modified(skill_name)
        if last_modified:
            days_dormant = (datetime.now() - last_modified).days
            last_used = last_modified.isoformat()
        else:
            days_dormant = 999  # Unknown/extremely dormant
            last_used = None
    
    # Determine status
    if days_dormant < THRESHOLDS["active"]:
        status = "active"
    elif days_dormant < THRESHOLDS["under_utilized"]:
        status = "under-utilized"
    elif days_dormant < THRESHOLDS["dormant"]:
        status = "dormant"
    elif days_dormant < THRESHOLDS["forgotten"]:
        status = "forgotten"
    else:
        status = "candidate-for-archive"
    
    # Memory references
    memory_refs = check_memory_references(skill_name)
    
    return {
        "name": skill_name,
        "emoji": SKILL_EMOJIS.get(skill_name, "🔧"),
        "last_used": last_used,
        "days_dormant": days_dormant,
        "status": status,
        "memory_refs": memory_refs,
        "activation_count": skill_data.get("activation_count", 0)
    }

def generate_activation_suggestions(dormant_skills):
    """Generate contextual prompts for dormant skills."""
    suggestions = []
    
    templates = {
        "context-optimizer": "Your conversations are getting long. Ready to summarize and refocus?",
        "decision-log": "You made some key decisions this week. Want to log them for future reference?",
        "workspace-organizer": "Your workspace has {file_count} files. Time for a cleanup?",
        "research-synthesizer": "Planning any research? I can synthesize multiple sources with contradiction detection.",
        "tool-orchestrator": "Complex multi-step task ahead? I can orchestrate parallel tool execution.",
        "code-evolution-tracker": "Been coding this week? I can track your improvements and document patterns.",
        "memory-manager": "Want me to organize your memory files and surface relevant past insights?",
        "autonomous-agent": "Have a task that needs autonomous handling? I'm here.",
        "aloe": "Want me to learn from our sessions and optimize my responses?",
        "sensory-input-layer": "Need data gathered from external sources?",
        "multi-agent-coordinator": "Complex multi-domain task? I can spawn specialist agents.",
        "autonomous-trading-strategist": "Markets moving? I can analyze opportunities.",
        "long-term-project-manager": "Have projects that span multiple days? Let me track them.",
        "autonomous-workflow-builder": "Doing repetitive tasks? I can build automation.",
        "knowledge-graph-engine": "Want to map relationships in your data?",
        "autonomous-opportunity-engine": "Looking for alpha? I'm hunting 24/7.",
        "skill-evolution-engine": "Want me to analyze and improve my own capabilities?",
        "autonomous-code-architect": "Building something complex? I can plan and engineer it properly.",
        "skill-activation-manager": "Meta! I can audit myself too. I'm running now! ✅",
        "income-optimizer": "Want to review your revenue streams and find growth opportunities?",
        "event-bus": "Need events routed between skills for better coordination?",
        "integration-orchestrator": "Have multiple systems that need better integration?"
    }
    
    for skill in dormant_skills:
        if skill["name"] in templates:
            suggestions.append({
                "skill": skill["name"],
                "emoji": skill["emoji"],
                "status": skill["status"],
                "days_dormant": skill["days_dormant"],
                "prompt": templates.get(skill["name"], f"Time to wake up {skill['name']}!"),
                "priority": "high" if skill["status"] in ["dormant", "forgotten"] else "medium"
            })
    
    return suggestions

def run_weekly_audit():
    """Run the weekly skill activation audit."""
    print("🔍 Skill Activation Manager - Weekly Audit")
    print("=" * 50)
    
    state = load_state()
    skills = get_skill_list()
    
    if not skills:
        print("⚠️ No skills found in directory")
        return
    
    print(f"Found {len(skills)} skills")
    print()
    
    # Assess each skill
    health_data = []
    dormant_skills = []
    
    for skill_name in skills:
        health = get_skill_health(skill_name, state)
        health_data.append(health)
        
        # Update state
        state["skills"][skill_name] = {
            "last_used": health["last_used"],
            "status": health["status"],
            "activation_count": health["activation_count"]
        }
        
        if health["status"] not in ["active", "under-utilized"]:
            dormant_skills.append(health)
    
    # Sort by dormancy
    health_data.sort(key=lambda x: x["days_dormant"], reverse=True)
    dormant_skills.sort(key=lambda x: x["days_dormant"], reverse=True)
    
    # Print status summary
    print("📊 Skill Health Summary")
    print("-" * 40)
    
    status_counts = {}
    for h in health_data:
        status_counts[h["status"]] = status_counts.get(h["status"], 0) + 1
    
    print(f"  🟢 Active: {status_counts.get('active', 0)}")
    print(f"  🟡 Under-utilized: {status_counts.get('under-utilized', 0)}")
    print(f"  🟠 Dormant: {status_counts.get('dormant', 0)}")
    print(f"  🔴 Forgotten: {status_counts.get('forgotten', 0)}")
    print(f"  ⚫ Candidate for Archive: {status_counts.get('candidate-for-archive', 0)}")
    print()
    
    # Print dormant skills table
    if dormant_skills:
        print("⚠️ Skills Requiring Attention")
        print("-" * 40)
        for skill in dormant_skills[:10]:  # Top 10
            status_emoji = {"dormant": "🟠", "forgotten": "🔴", "candidate-for-archive": "⚫"}.get(skill["status"], "⚪")
            print(f"  {skill['emoji']} {skill['name']:<35} {status_emoji} {skill['days_dormant']:>3} days")
        print()
    
    # Generate suggestions
    suggestions = generate_activation_suggestions(dormant_skills)
    state["activation_suggestions"] = suggestions
    
    if suggestions:
        print("💡 Activation Suggestions")
        print("-" * 40)
        for s in suggestions[:5]:  # Top 5
            priority_emoji = "🔴" if s["priority"] == "high" else "🟡"
            print(f"  {priority_emoji} {s['emoji']} {s['skill']}")
            print(f"     └─ {s['prompt']}")
        print()
    
    # Record audit
    audit_record = {
        "timestamp": datetime.now().isoformat(),
        "total_skills": len(skills),
        "dormant_count": len(dormant_skills),
        "suggestions_generated": len(suggestions)
    }
    state["audit_history"].append(audit_record)
    state["last_audit"] = datetime.now().isoformat()
    
    # Keep only last 10 audits
    state["audit_history"] = state["audit_history"][-10:]
    
    save_state(state)
    
    print("✅ Audit complete. State saved.")
    print(f"📁 State file: {STATE_FILE}")
    print()
    
    return state

if __name__ == "__main__":
    run_weekly_audit()
