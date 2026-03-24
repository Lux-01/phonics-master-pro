#!/usr/bin/env python3
"""
ALOE Reflection Agent
Spawns after each task to analyze and learn.
"""

import sys
import json
from datetime import datetime
from pathlib import Path

sys.path.insert(0, "/home/skux/.openclaw/workspace/skills/aloe")
from reflection_system import run_full_reflection


def reflect_on_task(task_json: str) -> str:
    """
    Analyze a completed task and update ALOE knowledge.
    
    Args:
        task_json: JSON string with task data
        
    Returns:
        Summary of learnings
    """
    task_data = json.loads(task_json)
    
    print("🧠 ALOE Reflection Agent Starting...")
    print(f"   Task: {task_data.get('description', 'Unknown')[:50]}...")
    
    result = run_full_reflection(task_data)
    
    # Generate summary
    outcome = result['outcome']
    
    summary = f"""
📊 REFLECTION COMPLETE
━━━━━━━━━━━━━━━━━━━━━━
Task: {outcome['task_summary'][:60]}
Outcome: {outcome['outcome'].upper()} (confidence: {outcome['confidence']:.0f}%)
Duration: {outcome['duration_seconds']:.1f}s

🔍 Learnings:
{chr(10).join('  • ' + l for l in outcome['learnings'])}

📈 Patterns Extracted: {result['patterns_extracted']}

💡 Proactive Suggestions for similar tasks:
"""
    
    for s in result['suggestions'][:3]:
        summary += f"  • [{s['confidence']:.0f}% conf] {s['suggestion'][:80]}\n"
    
    return summary


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(reflect_on_task(sys.argv[1]))
    else:
        print("Usage: python3 aloe_reflection_agent.py '{task_json}'")
