#!/usr/bin/env python3
"""
ALOE Self-Reflection Coordinator
Integrates with OpenClaw to enable self-improving behavior.

Usage: Import and call after task completion:
    from aloe_coordinator import reflect_after_task
    reflect_after_task(task_data)
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Paths
ALOE_DIR = Path("/home/skux/.openclaw/workspace/skills/aloe")
MEMORY_DIR = Path("/home/skux/.openclaw/workspace/memory/aloe")


class AloeCoordinator:
    """
    Coordinates ALOE reflection across multiple agents.
    """
    
    def __init__(self):
        self.reflection_agent = Path("/home/skux/.openclaw/workspace/agents/aloe_reflection_agent.py")
        self.patterns_file = MEMORY_DIR / "patterns" / "extracted_patterns.json"
        self.suggestions_file = MEMORY_DIR / "suggestions.json"
        
    def reflect(self, 
                task_description: str,
                tools_used: list,
                start_time: datetime,
                errors: list = None,
                approach: str = "") -> Dict[str, Any]:
        """
        Run full reflection pipeline using multiple agents.
        
        Spawns:
        1. Reflection Agent - Analyzes outcome
        2. Pattern Agent - Extracts patterns
        3. Knowledge Agent - Updates knowledge graph
        4. Suggestion Agent - Prepares proactive suggestions
        """
        
        end_time = datetime.now()
        errors = errors or []
        
        task_data = {
            "description": task_description,
            "approach": approach or "standard workflow",
            "tools": tools_used,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "errors": errors,
            "feedback": None
        }
        
        # Spawn reflection agent
        result = self._spawn_reflection_agent(task_data)
        
        return result
    
    def _spawn_reflection_agent(self, task_data: Dict) -> Dict:
        """Spawn the reflection agent subprocess."""
        try:
            result = subprocess.run(
                [
                    "python3",
                    str(self.reflection_agent),
                    json.dumps(task_data)
                ],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "errors": result.stderr if result.stderr else None
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_patterns(self) -> list:
        """Get all learned patterns."""
        if not self.patterns_file.exists():
            return []
        
        try:
            with open(self.patterns_file) as f:
                return json.load(f)
        except:
            return []
    
    def get_suggestions(self, task_hint: str) -> list:
        """Get proactive suggestions for a task type."""
        # Import and use reflection engine directly for speed
        import sys
        sys.path.insert(0, str(ALOE_DIR))
        from reflection_system import ReflectionEngine
        
        engine = ReflectionEngine()
        return engine.get_suggestions(task_hint)
    
    def show_learning_summary(self) -> str:
        """Generate summary of what ALOE has learned."""
        patterns = self.get_patterns()
        
        if not patterns:
            return "🌱 ALOE is still learning. Complete some tasks to build patterns!"
        
        # Group by tags
        by_tag = {}
        for p in patterns:
            for tag in p.get('tags', []):
                if tag not in by_tag:
                    by_tag[tag] = []
                by_tag[tag].append(p)
        
        summary = f"""
📚 ALOE Learning Summary
━━━━━━━━━━━━━━━━━━━━━━━
Total Patterns Learned: {len(patterns)}

By Category:
"""
        
        for tag, ps in sorted(by_tag.items(), key=lambda x: -len(x[1]))[:5]:
            avg_success = sum(p.get('success_rate', 0) for p in ps) / len(ps)
            summary += f"  • {tag}: {len(ps)} patterns (avg {avg_success:.0f}% success)\n"
        
        # Top patterns
        top_patterns = sorted(patterns, key=lambda x: x.get('uses', 0), reverse=True)[:3]
        
        summary += "\n🏆 Most Used Patterns:\n"
        for p in top_patterns:
            summary += f"  • {p['name'][:40]}... ({p['uses']} uses, {p['success_rate']:.0f}% success)\n"
        
        return summary


# Global coordinator instance
_aloe = None

def get_coordinator() -> AloeCoordinator:
    """Get or create singleton coordinator."""
    global _aloe
    if _aloe is None:
        _aloe = AloeCoordinator()
    return _aloe


def reflect_after_task(task_description: str,
                       tools_used: list,
                       start_time: datetime,
                       errors: list = None,
                       approach: str = "") -> str:
    """
    Convenience function to trigger reflection after task.
    
    Example:
        start = datetime.now()
        # ... do task ...
        result = reflect_after_task(
            "Upgraded AOE scanner",
            ["read", "edit", "exec"],
            start,
            errors=[]
        )
    """
    coordinator = get_coordinator()
    result = coordinator.reflect(task_description, tools_used, start_time, errors, approach)
    
    if result.get('success'):
        return result['output']
    else:
        return f"⚠️ Reflection failed: {result.get('error', 'Unknown error')}"


def show_what_ive_learned() -> str:
    """Show user what ALOE has learned so far."""
    coordinator = get_coordinator()
    return coordinator.show_learning_summary()


def get_proactive_suggestions(task: str) -> list:
    """Get suggestions before starting a task."""
    coordinator = get_coordinator()
    return coordinator.get_suggestions(task)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "summary":
        print(show_what_ive_learned())
    else:
        print("ALOE Coordinator Ready")
        print("Use: reflect_after_task() after completing tasks")
        print("Use: show_what_ive_learned() to see patterns")
