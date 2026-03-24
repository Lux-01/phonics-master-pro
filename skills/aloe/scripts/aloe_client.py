#!/usr/bin/env python3
"""
ALOE - Adaptive Learning and Observation Environment
Core learning and pattern management system.
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

ALOE_DIR = Path("/home/skux/.openclaw/workspace/memory/aloe")

class ALOELearning:
    def __init__(self):
        self.ensure_directories()
        self.patterns = self.load_patterns()
        self.observations = []
        
    def ensure_directories(self):
        """Create ALOE directory structure."""
        directories = [
            "patterns",
            "observations",
            "adaptations",
            "metrics",
            "evolution"
        ]
        for d in directories:
            (ALOE_DIR / d).mkdir(parents=True, exist_ok=True)
    
    def load_patterns(self) -> Dict:
        """Load all learned patterns."""
        patterns = {
            "success": [],
            "failure": [],
            "efficiency": [],
            "preference": [],
            "risk": []
        }
        
        patterns_dir = ALOE_DIR / "patterns"
        for category in patterns.keys():
            file_path = patterns_dir / f"{category}_patterns.json"
            if file_path.exists():
                with open(file_path) as f:
                    patterns[category] = json.load(f)
        
        return patterns
    
    def save_patterns(self):
        """Save all patterns."""
        patterns_dir = ALOE_DIR / "patterns"
        for category, pattern_list in self.patterns.items():
            file_path = patterns_dir / f"{category}_patterns.json"
            with open(file_path, 'w') as f:
                json.dump(pattern_list, f, indent=2)
    
    def observe(self, action: str, outcome: str, context: dict):
        """Record an observation."""
        observation = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "outcome": outcome,
            "context": context
        }
        self.observations.append(observation)
        
        # Log to daily file
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = ALOE_DIR / "observations" / f"{today}.json"
        
        existing = []
        if log_file.exists():
            with open(log_file) as f:
                existing = json.load(f)
        
        existing.append(observation)
        with open(log_file, 'w') as f:
            json.dump(existing, f, indent=2)
        
        # Attempt pattern extraction
        self.extract_pattern(observation)
    
    def extract_pattern(self, observation: dict):
        """Extract patterns from observations."""
        # Simple pattern extraction logic
        action = observation["action"]
        outcome = observation["outcome"]
        
        if outcome == "success":
            self._update_success_pattern(action, observation)
        elif outcome == "failure":
            self._update_failure_pattern(action, observation)
    
    def _update_success_pattern(self, action: str, observation: dict):
        """Update or create success pattern."""
        # Check if pattern exists
        for pattern in self.patterns["success"]:
            if pattern["action"] == action:
                pattern["uses"] += 1
                pattern["confidence"] = min(0.99, pattern["confidence"] + 0.01)
                pattern["last_applied"] = datetime.now().isoformat()
                return
        
        # Create new pattern
        new_pattern = {
            "pattern_id": f"PAT-{len(self.patterns['success']) + 1:03d}",
            "category": "success",
            "action": action,
            "confidence": 0.80,
            "uses": 1,
            "created": datetime.now().isoformat(),
            "last_applied": datetime.now().isoformat()
        }
        self.patterns["success"].append(new_pattern)
    
    def _update_failure_pattern(self, action: str, observation: dict):
        """Update or create failure pattern."""
        for pattern in self.patterns["failure"]:
            if pattern["action"] == action:
                pattern["encountered"] += 1
                return
        
        new_pattern = {
            "pattern_id": f"FAIL-{len(self.patterns['failure']) + 1:03d}",
            "category": "failure",
            "action": action,
            "confidence": 0.70,
            "encountered": 1,
            "created": datetime.now().isoformat()
        }
        self.patterns["failure"].append(new_pattern)
    
    def get_recommendations(self, action_type: str) -> List[dict]:
        """Get pattern recommendations for action type."""
        recommendations = []
        
        # Check success patterns
        for pattern in self.patterns["success"]:
            if action_type in pattern.get("action", ""):
                recommendations.append(pattern)
        
        # Check failure patterns (to avoid)
        for pattern in self.patterns["failure"]:
            if action_type in pattern.get("action", ""):
                recommendations.append({
                    **pattern,
                    "recommendation": "avoid"
                })
        
        # Sort by confidence
        recommendations.sort(key=lambda x: x.get("confidence", 0), reverse=True)
        return recommendations[:5]
    
    def show_stats(self):
        """Show ALOE statistics."""
        total_patterns = sum(len(p) for p in self.patterns.values())
        
        stats = {
            "total_patterns": total_patterns,
            "success_patterns": len(self.patterns["success"]),
            "failure_patterns": len(self.patterns["failure"]),
            "efficiency_patterns": len(self.patterns["efficiency"]),
            "preferences": len(self.patterns["preference"]),
            "observations_today": len(self.observations)
        }
        
        return stats
    
    def export_insights(self) -> str:
        """Export learning insights."""
        stats = self.show_stats()
        
        insights = f"""# ALOE Insights

## Statistics
- Total Patterns: {stats['total_patterns']}
- Success Patterns: {stats['success_patterns']}
- Failure Patterns: {stats['failure_patterns']}
- Today's Observations: {stats['observations_today']}

## Top Success Patterns
"""
        
        top_success = sorted(
            self.patterns["success"], 
            key=lambda x: x.get("confidence", 0), 
            reverse=True
        )[:5]
        
        for pattern in top_success:
            insights += f"- {pattern['action']}: {pattern['confidence']:.0%} confidence\n"
        
        return insights

def main():
    """CLI interface for ALOE."""
    import sys
    
    aloe = ALOELearning()
    
    if len(sys.argv) < 2:
        print("Usage: aloe_client.py [observe|patterns|stats|insights]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "observe" and len(sys.argv) >= 4:
        action = sys.argv[2]
        outcome = sys.argv[3]
        aloe.observe(action, outcome, {})
        print(f"Observed: {action} -> {outcome}")
    
    elif cmd == "patterns":
        if len(sys.argv) >= 3:
            action_type = sys.argv[2]
            recs = aloe.get_recommendations(action_type)
            for rec in recs:
                print(f"- {rec['pattern_id']}: {rec.get('confidence', 0):.0%} confidence")
        else:
            print("Success patterns:", len(aloe.patterns["success"]))
            print("Failure patterns:", len(aloe.patterns["failure"]))
    
    elif cmd == "stats":
        stats = aloe.show_stats()
        for k, v in stats.items():
            print(f"{k}: {v}")
    
    elif cmd == "insights":
        print(aloe.export_insights())

if __name__ == "__main__":
    main()
