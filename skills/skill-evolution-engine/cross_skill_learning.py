#!/usr/bin/env python3
"""
Cross-Skill Learning System
Enables skills to learn from each other and share knowledge
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Any

MEMORY_DIR = "/home/skux/.openclaw/workspace/memory"
CROSS_SKILL_DIR = os.path.join(MEMORY_DIR, "cross_skill_learning")
KNOWLEDGE_GRAPH_FILE = os.path.join(CROSS_SKILL_DIR, "knowledge_graph.json")
LEARNING_LOG_FILE = os.path.join(CROSS_SKILL_DIR, "learning_log.json")
PATTERNS_FILE = os.path.join(CROSS_SKILL_DIR, "shared_patterns.json")

class CrossSkillLearning:
    """
    Cross-Skill Learning System
    
    Enables:
    1. Skills teaching each other (pattern transfer)
    2. Shared knowledge base (common learnings)
    3. Skill composition (combining capabilities)
    4. Learning propagation (success spreads)
    """
    
    def __init__(self):
        self._ensure_dirs()
        self.knowledge_graph = self._load_json(KNOWLEDGE_GRAPH_FILE, {})
        self.learning_log = self._load_json(LEARNING_LOG_FILE, [])
        self.shared_patterns = self._load_json(PATTERNS_FILE, [])
    
    def _ensure_dirs(self):
        """Ensure directories exist"""
        os.makedirs(CROSS_SKILL_DIR, exist_ok=True)
    
    def _load_json(self, filepath, default):
        """Load JSON file"""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except:
                pass
        return default
    
    def _save_json(self, filepath, data):
        """Save JSON file"""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def record_learning(self, source_skill: str, target_skill: str, 
                       learning_type: str, content: Dict, success: bool = True):
        """
        Record that source_skill taught target_skill something
        
        Args:
            source_skill: Skill that provided the learning
            target_skill: Skill that received the learning
            learning_type: Type of learning (pattern, technique, insight)
            content: The actual learning content
            success: Whether the learning was successful
        """
        learning = {
            'timestamp': datetime.now().isoformat(),
            'source_skill': source_skill,
            'target_skill': target_skill,
            'type': learning_type,
            'content': content,
            'success': success,
            'id': f"{source_skill}_to_{target_skill}_{datetime.now().timestamp()}"
        }
        
        self.learning_log.append(learning)
        self._save_json(LEARNING_LOG_FILE, self.learning_log)
        
        # Update knowledge graph
        self._update_knowledge_graph(source_skill, target_skill, learning_type, success)
        
        return learning
    
    def _update_knowledge_graph(self, source: str, target: str, learning_type: str, success: bool):
        """Update the knowledge graph with new learning relationship"""
        if 'nodes' not in self.knowledge_graph:
            self.knowledge_graph['nodes'] = {}
        if 'edges' not in self.knowledge_graph:
            self.knowledge_graph['edges'] = []
        
        # Add nodes
        for skill in [source, target]:
            if skill not in self.knowledge_graph['nodes']:
                self.knowledge_graph['nodes'][skill] = {
                    'id': skill,
                    'type': 'skill',
                    'learnings_given': 0,
                    'learnings_received': 0,
                    'success_rate': 1.0
                }
        
        # Update node stats
        self.knowledge_graph['nodes'][source]['learnings_given'] += 1
        self.knowledge_graph['nodes'][target]['learnings_received'] += 1
        
        # Add edge
        edge = {
            'source': source,
            'target': target,
            'type': learning_type,
            'success': success,
            'timestamp': datetime.now().isoformat()
        }
        self.knowledge_graph['edges'].append(edge)
        
        self._save_json(KNOWLEDGE_GRAPH_FILE, self.knowledge_graph)
    
    def share_pattern(self, source_skill: str, pattern: Dict, 
                    applicable_skills: List[str] = None):
        """
        Share a pattern from source_skill to other skills
        
        Args:
            source_skill: Skill that discovered the pattern
            pattern: The pattern to share
            applicable_skills: List of skills that could use this pattern
        """
        shared_pattern = {
            'id': f"pattern_{datetime.now().timestamp()}",
            'source_skill': source_skill,
            'pattern': pattern,
            'applicable_skills': applicable_skills or [],
            'timestamp': datetime.now().isoformat(),
            'adoptions': []
        }
        
        self.shared_patterns.append(shared_pattern)
        self._save_json(PATTERNS_FILE, self.shared_patterns)
        
        return shared_pattern
    
    def adopt_pattern(self, target_skill: str, pattern_id: str, 
                     adaptation: Dict = None):
        """
        Have a skill adopt a shared pattern
        
        Args:
            target_skill: Skill adopting the pattern
            pattern_id: ID of the pattern to adopt
            adaptation: How the pattern was adapted for this skill
        """
        for pattern in self.shared_patterns:
            if pattern['id'] == pattern_id:
                adoption = {
                    'skill': target_skill,
                    'timestamp': datetime.now().isoformat(),
                    'adaptation': adaptation or {}
                }
                pattern['adoptions'].append(adoption)
                self._save_json(PATTERNS_FILE, self.shared_patterns)
                
                # Record the learning
                self.record_learning(
                    pattern['source_skill'],
                    target_skill,
                    'pattern_adoption',
                    {'pattern_id': pattern_id, 'adaptation': adaptation}
                )
                
                return adoption
        
        return None
    
    def get_learnings_for_skill(self, skill_name: str) -> List[Dict]:
        """Get all learnings received by a skill"""
        return [l for l in self.learning_log if l['target_skill'] == skill_name]
    
    def get_learnings_from_skill(self, skill_name: str) -> List[Dict]:
        """Get all learnings given by a skill"""
        return [l for l in self.learning_log if l['source_skill'] == skill_name]
    
    def get_applicable_patterns(self, skill_name: str) -> List[Dict]:
        """Get patterns applicable to a skill"""
        return [p for p in self.shared_patterns 
                if skill_name in p.get('applicable_skills', []) 
                and skill_name not in [a['skill'] for a in p.get('adoptions', [])]]
    
    def find_skill_connections(self, skill_name: str) -> Dict:
        """Find skills connected to this one through learning"""
        teaches = []
        learns_from = []
        
        for edge in self.knowledge_graph.get('edges', []):
            if edge['source'] == skill_name:
                teaches.append(edge['target'])
            if edge['target'] == skill_name:
                learns_from.append(edge['source'])
        
        return {
            'teaches': list(set(teaches)),
            'learns_from': list(set(learns_from)),
            'total_connections': len(set(teaches + learns_from))
        }
    
    def propagate_success(self, source_skill: str, technique: str, 
                         success_metric: float):
        """
        Propagate a successful technique to related skills
        
        Args:
            source_skill: Skill with successful technique
            technique: The technique that worked
            success_metric: How well it worked (0-1)
        """
        if success_metric < 0.7:  # Only propagate significant successes
            return []
        
        # Find skills that could benefit
        connections = self.find_skill_connections(source_skill)
        propagated = []
        
        for target_skill in connections['teaches']:
            learning = self.record_learning(
                source_skill,
                target_skill,
                'technique_propagation',
                {
                    'technique': technique,
                    'success_metric': success_metric,
                    'reason': f'{source_skill} found success with this technique'
                }
            )
            propagated.append(learning)
        
        return propagated
    
    def compose_skills(self, skill_names: List[str], task: str) -> Dict:
        """
        Compose multiple skills for a complex task
        
        Args:
            skill_names: Skills to compose
            task: The task to accomplish
        """
        composition = {
            'task': task,
            'skills': skill_names,
            'timestamp': datetime.now().isoformat(),
            'execution_order': self._determine_order(skill_names),
            'shared_learnings': self._find_shared_learnings(skill_names)
        }
        
        return composition
    
    def _determine_order(self, skill_names: List[str]) -> List[str]:
        """Determine optimal execution order based on dependencies"""
        # Simple topological sort based on learning relationships
        order = []
        remaining = set(skill_names)
        
        while remaining:
            # Find skill with no unmet dependencies
            for skill in list(remaining):
                connections = self.find_skill_connections(skill)
                deps = [s for s in connections['learns_from'] if s in remaining]
                if not deps:
                    order.append(skill)
                    remaining.remove(skill)
                    break
            else:
                # Circular dependency, just append remaining
                order.extend(remaining)
                break
        
        return order
    
    def _find_shared_learnings(self, skill_names: List[str]) -> List[Dict]:
        """Find learnings shared between these skills"""
        shared = []
        for learning in self.learning_log:
            if (learning['source_skill'] in skill_names and 
                learning['target_skill'] in skill_names):
                shared.append(learning)
        return shared
    
    def get_learning_stats(self) -> Dict:
        """Get statistics on cross-skill learning"""
        total = len(self.learning_log)
        successful = len([l for l in self.learning_log if l.get('success', True)])
        
        by_type = {}
        for learning in self.learning_log:
            t = learning['type']
            by_type[t] = by_type.get(t, 0) + 1
        
        top_teachers = {}
        top_learners = {}
        for learning in self.learning_log:
            source = learning['source_skill']
            target = learning['target_skill']
            top_teachers[source] = top_teachers.get(source, 0) + 1
            top_learners[target] = top_learners.get(target, 0) + 1
        
        return {
            'total_learnings': total,
            'successful_learnings': successful,
            'success_rate': successful / total if total > 0 else 0,
            'by_type': by_type,
            'top_teachers': sorted(top_teachers.items(), key=lambda x: x[1], reverse=True)[:5],
            'top_learners': sorted(top_learners.items(), key=lambda x: x[1], reverse=True)[:5],
            'shared_patterns': len(self.shared_patterns),
            'total_skills_in_graph': len(self.knowledge_graph.get('nodes', {}))
        }
    
    def generate_learning_report(self) -> str:
        """Generate a human-readable learning report"""
        stats = self.get_learning_stats()
        
        report = f"""# Cross-Skill Learning Report

## Overview
- Total Learnings: {stats['total_learnings']}
- Success Rate: {stats['success_rate']*100:.1f}%
- Shared Patterns: {stats['shared_patterns']}
- Skills in Network: {stats['total_skills_in_graph']}

## Learning Types
"""
        for learning_type, count in stats['by_type'].items():
            report += f"- {learning_type}: {count}\n"
        
        report += "\n## Top Teachers\n"
        for skill, count in stats['top_teachers']:
            report += f"- {skill}: {count} learnings shared\n"
        
        report += "\n## Top Learners\n"
        for skill, count in stats['top_learners']:
            report += f"- {skill}: {count} learnings received\n"
        
        report += "\n## Recent Learnings\n"
        for learning in self.learning_log[-5:]:
            report += f"- {learning['source_skill']} → {learning['target_skill']}: {learning['type']}\n"
        
        return report

# Global instance
_cross_skill = None

def get_cross_skill_learning():
    """Get singleton cross-skill learning instance"""
    global _cross_skill
    if _cross_skill is None:
        _cross_skill = CrossSkillLearning()
    return _cross_skill

# Convenience functions
teach = lambda source, target, type, content, success=True: get_cross_skill_learning().record_learning(source, target, type, content, success)
share_pattern = lambda source, pattern, skills=None: get_cross_skill_learning().share_pattern(source, pattern, skills)
adopt = lambda target, pattern_id, adaptation=None: get_cross_skill_learning().adopt_pattern(target, pattern_id, adaptation)
propagate = lambda source, technique, metric: get_cross_skill_learning().propagate_success(source, technique, metric)
compose = lambda skills, task: get_cross_skill_learning().compose_skills(skills, task)
stats = lambda: get_cross_skill_learning().get_learning_stats()
report = lambda: get_cross_skill_learning().generate_learning_report()

if __name__ == "__main__":
    # Test cross-skill learning
    print("=== Cross-Skill Learning System Test ===\n")
    
    csl = CrossSkillLearning()
    
    # Simulate some learnings
    csl.record_learning('pattern-extractor', 'autonomous-trading-strategist', 
                       'pattern_recognition', {'pattern': 'breakout_after_consolidation'})
    
    csl.record_learning('autonomous-trading-strategist', 'aoe', 
                       'risk_management', {'technique': 'position_sizing'})
    
    csl.share_pattern('pattern-extractor', 
                     {'name': 'volume_spike_entry', 'confidence': 0.85},
                     ['autonomous-trading-strategist', 'aoe'])
    
    print(csl.generate_learning_report())
    print("\nCross-Skill Learning System ACTIVE ✅")
