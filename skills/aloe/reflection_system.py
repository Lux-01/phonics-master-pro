#!/usr/bin/env python3
"""
ALOE Reflection System v1.0
Self-reflecting agent framework using ACA methodology.
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# Paths
WORKSPACE = Path("/home/skux/.openclaw/workspace")
MEMORY_DIR = WORKSPACE / "memory"
ALOE_DIR = MEMORY_DIR / "aloe"
PATTERNS_DIR = ALOE_DIR / "patterns"
KNOWLEDGE_DIR = ALOE_DIR / "knowledge"
LOGS_DIR = ALOE_DIR / "logs"

for d in [PATTERNS_DIR, KNOWLEDGE_DIR, LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)


@dataclass
class TaskOutcome:
    """Structured task outcome for learning."""
    task_id: str
    timestamp: str
    task_summary: str
    approach: str
    tools_used: List[str]
    duration_seconds: float
    outcome: str  # "success", "partial", "failure"
    errors: List[str]
    learnings: List[str]
    confidence: float  # 0-100
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, d: Dict) -> 'TaskOutcome':
        return cls(**d)


@dataclass
class Pattern:
    """Extracted pattern from task outcomes."""
    pattern_id: str
    name: str
    trigger: str
    solution: str
    first_seen: str
    uses: int
    success_rate: float
    avg_time: float
    confidence: float
    tags: List[str]
    
    def to_dict(self) -> Dict:
        return asdict(self)


class ReflectionEngine:
    """Analyzes task outcomes and extracts learnings."""
    
    def __init__(self):
        self.patterns_file = PATTERNS_DIR / "extracted_patterns.json"
        self.outcomes_file = LOGS_DIR / "task_outcomes.json"
        
    def analyze_task(self, 
                    task_description: str,
                    approach: str,
                    tools_used: List[str],
                    start_time: datetime,
                    end_time: datetime,
                    errors: List[str],
                    user_feedback: Optional[str] = None) -> TaskOutcome:
        """Analyze a completed task and create outcome record."""
        
        duration = (end_time - start_time).total_seconds()
        
        # Determine outcome
        if not errors:
            outcome = "success"
            confidence = 95.0
        elif len(errors) <= 2:
            outcome = "partial"
            confidence = 70.0
        else:
            outcome = "failure"
            confidence = 40.0
        
        # Generate learnings
        learnings = self._extract_learnings(errors, tools_used, duration)
        
        # Create outcome
        outcome_obj = TaskOutcome(
            task_id=self._generate_id(task_description + str(start_time)),
            timestamp=end_time.isoformat(),
            task_summary=task_description[:200],
            approach=approach,
            tools_used=tools_used,
            duration_seconds=duration,
            outcome=outcome,
            errors=errors,
            learnings=learnings,
            confidence=confidence
        )
        
        # Save
        self._save_outcome(outcome_obj)
        
        return outcome_obj
    
    def _extract_learnings(self, errors: List[str], tools: List[str], duration: float) -> List[str]:
        """Extract learnings from task execution."""
        learnings = []
        
        # Tool-specific learnings
        if "process" in tools and errors:
            learnings.append("Process management requires explicit session ID tracking")
        
        if "exec" in tools and any("timed out" in e.lower() for e in errors):
            learnings.append("Long-running commands need background mode with polling")
        
        if "browser" in tools and any("timeout" in e.lower() for e in errors):
            learnings.append("Browser operations need the gateway running first")
        
        if duration > 60:
            learnings.append(f"Task took {duration:.0f}s - consider parallelization")
        
        if "read" in tools and "edit" in tools:
            learnings.append("File modification workflow: read -> plan -> edit")
        
        if not learnings:
            learnings.append("Smooth execution - approach validated")
        
        return learnings
    
    def extract_patterns(self) -> List[Pattern]:
        """Mine patterns from historical outcomes."""
        if not self.outcomes_file.exists():
            return []
        
        with open(self.outcomes_file) as f:
            outcomes = json.load(f)
        
        # Pattern mining
        patterns = []
        
        # Tool combination patterns
        tool_combos = {}
        for oc in outcomes:
            tools = tuple(sorted(oc.get('tools_used', [])))
            if tools not in tool_combos:
                tool_combos[tools] = []
            tool_combos[tools].append(oc)
        
        for tools, ocs in tool_combos.items():
            if len(ocs) >= 2:
                success = [o for o in ocs if o['outcome'] == 'success']
                if success:
                    pattern = Pattern(
                        pattern_id=self._generate_id(str(tools)),
                        name=f"Tool combo: {', '.join(tools)}",
                        trigger=f"Task requires {', '.join(tools[:2])}...",
                        solution=f"Use tools in sequence: {' -> '.join(tools)}",
                        first_seen=success[0]['timestamp'],
                        uses=len(ocs),
                        success_rate=len(success)/len(ocs)*100,
                        avg_time=sum(o['duration_seconds'] for o in ocs)/len(ocs),
                        confidence=min(95, len(ocs) * 20),
                        tags=list(tools)
                    )
                    patterns.append(pattern)
        
        # Error -> Fix patterns
        error_fixes = {}
        for oc in outcomes:
            for error in oc.get('errors', []):
                key = error[:50]  # Truncated error
                if key not in error_fixes:
                    error_fixes[key] = {}
                for learning in oc.get('learnings', []):
                    error_fixes[key][learning] = error_fixes[key].get(learning, 0) + 1
        
        for error, fixes in error_fixes.items():
            if fixes:
                best_fix = max(fixes.items(), key=lambda x: x[1])
                pattern = Pattern(
                    pattern_id=self._generate_id(error),
                    name=f"Fix for: {error[:30]}...",
                    trigger=error,
                    solution=best_fix[0],
                    first_seen=outcomes[0]['timestamp'] if outcomes else datetime.now().isoformat(),
                    uses=sum(fixes.values()),
                    success_rate=85.0,
                    avg_time=30.0,
                    confidence=min(90, best_fix[1] * 30),
                    tags=["error_fix"]
                )
                patterns.append(pattern)
        
        # Save patterns
        self._save_patterns(patterns)
        
        return patterns
    
    def get_suggestions(self, current_task: str) -> List[Dict]:
        """Get proactive suggestions based on patterns."""
        suggestions = []
        
        # Load patterns
        if not self.patterns_file.exists():
            return suggestions
        
        with open(self.patterns_file) as f:
            patterns = json.load(f)
        
        # Match current task to patterns
        task_lower = current_task.lower()
        
        for p in patterns:
            # Check if pattern applies
            if any(tag in task_lower for tag in p.get('tags', [])):
                suggestions.append({
                    "pattern": p['name'],
                    "confidence": p['confidence'],
                    "suggestion": p['solution'],
                    "success_rate": p['success_rate'],
                    "uses": p['uses']
                })
        
        # Sort by confidence
        suggestions.sort(key=lambda x: x['confidence'], reverse=True)
        return suggestions[:5]
    
    def _generate_id(self, content: str) -> str:
        """Generate unique ID from content."""
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _save_outcome(self, outcome: TaskOutcome):
        """Save outcome to history."""
        outcomes = []
        if self.outcomes_file.exists():
            with open(self.outcomes_file) as f:
                outcomes = json.load(f)
        
        outcomes.append(outcome.to_dict())
        
        # Keep last 100
        outcomes = outcomes[-100:]
        
        with open(self.outcomes_file, 'w') as f:
            json.dump(outcomes, f, indent=2)
    
    def _save_patterns(self, patterns: List[Pattern]):
        """Save extracted patterns."""
        existing = []
        if self.patterns_file.exists():
            with open(self.patterns_file) as f:
                existing = json.load(f)
        
        # Merge with existing
        existing_ids = {p['pattern_id'] for p in existing}
        new_patterns = [p.to_dict() for p in patterns if p.pattern_id not in existing_ids]
        
        existing.extend(new_patterns)
        
        with open(self.patterns_file, 'w') as f:
            json.dump(existing, f, indent=2)


class KnowledgeGraph:
    """Simple knowledge graph for storing relationships."""
    
    def __init__(self):
        self.graph_file = KNOWLEDGE_DIR / "knowledge_graph.json"
    
    def add_node(self, node_type: str, node_id: str, properties: Dict):
        """Add node to knowledge graph."""
        graph = self._load()
        
        if node_type not in graph['nodes']:
            graph['nodes'][node_type] = {}
        
        graph['nodes'][node_type][node_id] = {
            "properties": properties,
            "created": datetime.now().isoformat(),
            "connections": []
        }
        
        self._save(graph)
    
    def add_edge(self, from_type: str, from_id: str, to_type: str, to_id: str, relation: str):
        """Add relationship between nodes."""
        graph = self._load()
        
        edge = {
            "from": f"{from_type}:{from_id}",
            "to": f"{to_type}:{to_id}",
            "relation": relation,
            "timestamp": datetime.now().isoformat()
        }
        
        graph['edges'].append(edge)
        
        # Update node connections
        if from_type in graph['nodes'] and from_id in graph['nodes'][from_type]:
            graph['nodes'][from_type][from_id]['connections'].append(edge)
        
        self._save(graph)
    
    def query(self, node_type: Optional[str] = None, properties: Optional[Dict] = None) -> List[Dict]:
        """Query knowledge graph."""
        graph = self._load()
        
        results = []
        types_to_search = [node_type] if node_type else graph['nodes'].keys()
        
        for nt in types_to_search:
            if nt not in graph['nodes']:
                continue
            for nid, node in graph['nodes'][nt].items():
                props = node.get('properties', {})
                
                # Check property matches
                if properties:
                    match = all(props.get(k) == v for k, v in properties.items())
                    if not match:
                        continue
                
                results.append({
                    "type": nt,
                    "id": nid,
                    **props
                })
        
        return results
    
    def _load(self) -> Dict:
        """Load graph from disk."""
        if self.graph_file.exists():
            with open(self.graph_file) as f:
                return json.load(f)
        return {"nodes": {}, "edges": [], "version": "1.0"}
    
    def _save(self, graph: Dict):
        """Save graph to disk."""
        with open(self.graph_file, 'w') as f:
            json.dump(graph, f, indent=2)


def run_full_reflection(task_data: Dict) -> Dict[str, Any]:
    """Run complete ALOE reflection pipeline."""
    
    engine = ReflectionEngine()
    kg = KnowledgeGraph()
    
    # 1. Analyze task
    outcome = engine.analyze_task(
        task_description=task_data.get('description', ''),
        approach=task_data.get('approach', ''),
        tools_used=task_data.get('tools', []),
        start_time=datetime.fromisoformat(task_data.get('start_time')),
        end_time=datetime.fromisoformat(task_data.get('end_time')),
        errors=task_data.get('errors', []),
        user_feedback=task_data.get('feedback')
    )
    
    # 2. Extract patterns
    patterns = engine.extract_patterns()
    
    # 3. Update knowledge graph
    kg.add_node("task", outcome.task_id, {
        "summary": outcome.task_summary,
        "outcome": outcome.outcome,
        "confidence": outcome.confidence
    })
    
    for tool in outcome.tools_used:
        kg.add_node("tool", tool, {"name": tool})
        kg.add_edge("task", outcome.task_id, "tool", tool, "used")
    
    # 4. Get suggestions for next time
    suggestions = engine.get_suggestions(outcome.task_summary)
    
    return {
        "outcome": outcome.to_dict(),
        "patterns_extracted": len(patterns),
        "patterns": [p.to_dict() for p in patterns[-5:]],  # Last 5
        "suggestions": suggestions
    }


if __name__ == "__main__":
    # Test
    print("🧠 ALOE Reflection System v1.0")
    print("=" * 50)
    
    engine = ReflectionEngine()
    patterns = engine.extract_patterns()
    
    print(f"\n📊 Found {len(patterns)} patterns")
    
    for p in patterns[:3]:
        print(f"\n  {p.name}")
        print(f"    Success rate: {p.success_rate:.0f}%")
        print(f"    Uses: {p.uses}")
