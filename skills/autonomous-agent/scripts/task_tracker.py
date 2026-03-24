#!/usr/bin/env python3
"""
Track autonomous task execution state.
"""
import json
import os
from datetime import datetime
from pathlib import Path

STATE_DIR = Path("/home/skux/.openclaw/workspace/memory/autonomous_agent")

def init_state_dir():
    """Initialize state directories."""
    (STATE_DIR / "active_tasks").mkdir(parents=True, exist_ok=True)
    (STATE_DIR / "completed_tasks").mkdir(parents=True, exist_ok=True)
    (STATE_DIR / "decisions").mkdir(parents=True, exist_ok=True)

def create_task(task_id, description, steps):
    """Create new task entry."""
    init_state_dir()
    task = {
        "taskId": task_id,
        "description": description,
        "status": "in_progress",
        "startedAt": datetime.now().isoformat(),
        "currentStep": 0,
        "totalSteps": len(steps),
        "steps": steps,
        "decisions": [],
        "errors": [],
        "deliverables": []
    }
    with open(STATE_DIR / "active_tasks" / f"{task_id}.json", "w") as f:
        json.dump(task, f, indent=2)
    return task

def update_task(task_id, **updates):
    """Update task state."""
    task_path = STATE_DIR / "active_tasks" / f"{task_id}.json"
    if not task_path.exists():
        return None
    with open(task_path) as f:
        task = json.load(f)
    task.update(updates)
    task["lastUpdated"] = datetime.now().isoformat()
    with open(task_path, "w") as f:
        json.dump(task, f, indent=2)
    return task

def log_decision(task_id, decision_id, what, why, confidence):
    """Log a decision for task."""
    task_path = STATE_DIR / "active_tasks" / f"{task_id}.json"
    if not task_path.exists():
        return
    with open(task_path) as f:
        task = json.load(f)
    task["decisions"].append({
        "id": decision_id,
        "what": what,
        "why": why,
        "confidence": confidence,
        "timestamp": datetime.now().isoformat()
    })
    with open(task_path, "w") as f:
        json.dump(task, f, indent=2)

def complete_task(task_id):
    """Move task to completed."""
    active_path = STATE_DIR / "active_tasks" / f"{task_id}.json"
    if not active_path.exists():
        return
    with open(active_path) as f:
        task = json.load(f)
    task["status"] = "completed"
    task["completedAt"] = datetime.now().isoformat()
    completed_path = STATE_DIR / "completed_tasks" / f"{task_id}.json"
    with open(completed_path, "w") as f:
        json.dump(task, f, indent=2)
    active_path.unlink()

def get_progress(task_id):
    """Get task progress."""
    task_path = STATE_DIR / "active_tasks" / f"{task_id}.json"
    if not task_path.exists():
        return None
    with open(task_path) as f:
        task = json.load(f)
    pct = (task["currentStep"] / task["totalSteps"]) * 100
    return {
        "taskId": task_id,
        "description": task["description"],
        "progress": f"{pct:.0f}%",
        "step": f"{task['currentStep']}/{task['totalSteps']}",
        "status": task["status"]
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: task_tracker.py [create|update|complete|progress] [args...]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "create" and len(sys.argv) >= 4:
        task_id = sys.argv[2]
        description = sys.argv[3]
        steps = sys.argv[4:]
        create_task(task_id, description, steps)
        print(f"Created task {task_id}")
    
    elif cmd == "progress" and len(sys.argv) >= 3:
        task_id = sys.argv[2]
        progress = get_progress(task_id)
        if progress:
            print(f"{progress['description']}: {progress['progress']}")
        else:
            print("Task not found")
    
    elif cmd == "complete" and len(sys.argv) >= 3:
        task_id = sys.argv[2]
        complete_task(task_id)
        print(f"Completed task {task_id}")
