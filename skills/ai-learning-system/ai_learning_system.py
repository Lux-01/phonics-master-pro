#!/usr/bin/env python3
"""
AI Learning System - Integrated Module
Connects universal-memory-system, decision-log, and outcome-tracker for continuous learning.

This module creates a unified learning pipeline:
1. Decisions are logged with context
2. Outcomes are tracked and measured
3. Memories are tagged and organized
4. Patterns are extracted and fed to ALOE

MIGRATED: Now uses universal-memory-system instead of memory-manager
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import hashlib

# Import the individual components
sys.path.insert(0, '/home/skux/.openclaw/workspace/skills/universal-memory-system')
sys.path.insert(0, '/home/skux/.openclaw/workspace/skills/decision-log')
sys.path.insert(0, '/home/skux/.openclaw/workspace/skills/outcome-tracker')

from unified_api import MemoryAPI as MemoryManager
from decision_log import DecisionLog


class AILearningSystem:
    """
    Integrated AI Learning System
    
    Combines:
    - Memory Manager: Auto-tagging and organization
    - Decision Log: Decision tracking with rationale
    - Outcome Tracker: Success/failure measurement
    - ALOE Integration: Pattern learning
    """
    
    def __init__(self, workspace_dir: str = None):
        self.workspace_dir = workspace_dir or os.path.expanduser("~/.openclaw/workspace")
        self.memory_dir = os.path.join(self.workspace_dir, "memory")
        self.ai_learning_dir = os.path.join(self.memory_dir, "ai_learning")
        self.patterns_file = os.path.join(self.ai_learning_dir, "learned_patterns.json")
        self.insights_file = os.path.join(self.ai_learning_dir, "insights.json")
        self.feed_log_file = os.path.join(self.ai_learning_dir, "aloe_feed_log.json")
        
        # Initialize components
        self.memory_manager = MemoryManager(self.memory_dir)
        self.decision_log = DecisionLog(os.path.join(self.memory_dir, "decisions"))
        
        self._ensure_dirs()
        self.patterns = self._load_patterns()
        self.insights = self._load_insights()
    
    def _ensure_dirs(self):
        """Create necessary directories"""
        Path(self.ai_learning_dir).mkdir(parents=True, exist_ok=True)
        Path(os.path.join(self.ai_learning_dir, "outcomes")).mkdir(parents=True, exist_ok=True)
    
    def _load_patterns(self) -> Dict:
        """Load learned patterns"""
        try:
            if os.path.exists(self.patterns_file):
                with open(self.patterns_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading patterns: {e}")
        return {
            "success_patterns": [],
            "failure_patterns": [],
            "decision_patterns": [],
            "tool_patterns": [],
            "last_updated": None
        }
    
    def _load_insights(self) -> Dict:
        """Load generated insights"""
        try:
            if os.path.exists(self.insights_file):
                with open(self.insights_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading insights: {e}")
        return {
            "total_insights": 0,
            "insights": [],
            "recommendations": []
        }
    
    def _save(self):
        """Save patterns and insights"""
        try:
            with open(self.patterns_file, 'w') as f:
                json.dump(self.patterns, f, indent=2)
            with open(self.insights_file, 'w') as f:
                json.dump(self.insights, f, indent=2)
        except Exception as e:
            print(f"Error saving AI learning data: {e}")
    
    # ============ DECISION-OUTCOME INTEGRATION ============
    
    def log_decision_with_outcome(self, decision: str, rationale: str, 
                                   expected_outcome: str, context: str = "",
                                   tags: List[str] = None) -> str:
        """
        Log a decision with expected outcome tracking
        
        Returns decision_id for later outcome recording
        """
        # Add AI learning tags
        ai_tags = tags or []
        ai_tags.extend(["ai_learning", "tracked"])
        
        # Log the decision
        decision_id = self.decision_log.log_decision(
            decision=decision,
            rationale=rationale,
            context=context,
            tags=ai_tags
        )
        
        # Create outcome expectation record
        expectation = {
            "decision_id": decision_id,
            "expected_outcome": expected_outcome,
            "logged_at": datetime.now().isoformat(),
            "status": "pending"
        }
        
        self._save_outcome_expectation(expectation)
        
        # Index in memory manager
        decision_file = os.path.join(self.memory_dir, "decisions", f"decision_{decision_id}.json")
        self.memory_manager.index_file(decision_file)
        
        return decision_id
    
    def record_decision_outcome(self, decision_id: str, actual_outcome: str, 
                                 impact_score: int = None, notes: str = "") -> Dict:
        """
        Record the actual outcome of a decision
        
        impact_score: -5 to +5 (negative = bad, positive = good)
        """
        # Record in decision log
        success = self.decision_log.record_outcome(decision_id, actual_outcome, notes)
        
        if not success:
            return {"error": "Decision not found"}
        
        # Get decision details
        decision = self.decision_log.get_by_id(decision_id)
        
        # Calculate outcome metrics
        outcome_record = {
            "decision_id": decision_id,
            "decision": decision["decision"],
            "rationale": decision["rationale"],
            "expected": self._get_expected_outcome(decision_id),
            "actual": actual_outcome,
            "impact_score": impact_score,
            "aligned": self._outcomes_aligned(decision.get("expected"), actual_outcome),
            "recorded_at": datetime.now().isoformat(),
            "notes": notes
        }
        
        # Save outcome record
        self._save_outcome_record(outcome_record)
        
        # Extract pattern
        self._extract_decision_pattern(decision, outcome_record)
        
        # Feed to ALOE
        self._feed_to_aloe("decision_outcome", outcome_record)
        
        return outcome_record
    
    # ============ MEMORY-DECISION INTEGRATION ============
    
    def get_contextual_decisions(self, context_query: str, limit: int = 10) -> List[Dict]:
        """
        Get decisions related to current context using memory manager
        """
        # Search memory for related files
        related_files = []
        for tag in self.memory_manager.tags_index:
            if context_query.lower() in tag.lower():
                related_files.extend(self.memory_manager.tags_index[tag])
        
        # Get decisions from related context
        decisions = self.decision_log.search(context_query)
        
        # Sort by recency
        decisions = sorted(decisions, key=lambda x: x["timestamp"], reverse=True)
        
        return decisions[:limit]
    
    def suggest_based_on_history(self, current_context: str) -> List[Dict]:
        """
        Suggest actions based on similar past decisions and their outcomes
        """
        # Find similar past decisions
        similar_decisions = self.get_contextual_decisions(current_context, limit=20)
        
        # Analyze outcomes
        successful = [d for d in similar_decisions if d.get("outcome") == "success"]
        failed = [d for d in similar_decisions if d.get("outcome") == "failure"]
        
        suggestions = []
        
        if successful:
            # Extract what worked
            common_rationales = self._find_common_elements([s["rationale"] for s in successful])
            suggestions.append({
                "type": "repeat_success",
                "message": f"Similar situations had success with: {common_rationales[:3]}",
                "confidence": len(successful) / len(similar_decisions) if similar_decisions else 0,
                "examples": successful[:3]
            })
        
        if failed:
            # Warn about pitfalls
            common_issues = self._find_common_elements([f.get("outcome_notes", "") for f in failed])
            suggestions.append({
                "type": "avoid_failure",
                "message": f"Watch out for: {common_issues[:3]}",
                "confidence": len(failed) / len(similar_decisions) if similar_decisions else 0,
                "examples": failed[:3]
            })
        
        return suggestions
    
    # ============ PATTERN EXTRACTION ============
    
    def _extract_decision_pattern(self, decision: Dict, outcome: Dict):
        """Extract patterns from decision-outcome pairs"""
        pattern = {
            "context": decision.get("context", ""),
            "decision_type": self._categorize_decision(decision["decision"]),
            "rationale_keywords": self._extract_keywords(decision["rationale"]),
            "outcome": outcome["actual"],
            "impact": outcome.get("impact_score", 0),
            "timestamp": datetime.now().isoformat()
        }
        
        if outcome.get("impact_score", 0) > 0:
            self.patterns["success_patterns"].append(pattern)
        elif outcome.get("impact_score", 0) < 0:
            self.patterns["failure_patterns"].append(pattern)
        else:
            self.patterns["decision_patterns"].append(pattern)
        
        self.patterns["last_updated"] = datetime.now().isoformat()
        self._save()
    
    def extract_all_patterns(self) -> Dict:
        """Extract patterns from all historical data"""
        # Get all decisions
        all_decisions = self.decision_log.get_recent(1000)
        
        # Categorize decisions
        categories = {}
        for d in all_decisions:
            cat = self._categorize_decision(d["decision"])
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(d)
        
        # Find patterns in each category
        patterns = {
            "by_category": {},
            "high_success_approaches": [],
            "common_failure_modes": [],
            "optimal_timing": {}
        }
        
        for cat, decisions in categories.items():
            successful = [d for d in decisions if d.get("outcome") == "success"]
            failed = [d for d in decisions if d.get("outcome") == "failure"]
            
            patterns["by_category"][cat] = {
                "total": len(decisions),
                "success_rate": len(successful) / len(decisions) if decisions else 0,
                "common_rationales": self._find_common_elements([d["rationale"] for d in successful]) if successful else []
            }
        
        self.patterns["extracted_patterns"] = patterns
        self._save()
        
        return patterns
    
    # ============ ALOE INTEGRATION ============
    
    def _feed_to_aloe(self, event_type: str, data: Dict):
        """Feed learning data to ALOE"""
        feed_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "data": data
        }
        
        # Append to feed log
        try:
            feed_log = []
            if os.path.exists(self.feed_log_file):
                with open(self.feed_log_file, 'r') as f:
                    feed_log = json.load(f)
            
            feed_log.append(feed_entry)
            
            # Keep only last 1000 entries
            feed_log = feed_log[-1000:]
            
            with open(self.feed_log_file, 'w') as f:
                json.dump(feed_log, f, indent=2)
        except Exception as e:
            print(f"Error feeding to ALOE: {e}")
    
    def sync_with_aloe(self) -> Dict:
        """Sync all patterns and insights with ALOE"""
        sync_data = {
            "patterns": self.patterns,
            "insights": self.insights,
            "synced_at": datetime.now().isoformat()
        }
        
        # Save to ALOE input file
        aloe_input_file = os.path.join(self.ai_learning_dir, "aloe_sync.json")
        with open(aloe_input_file, 'w') as f:
            json.dump(sync_data, f, indent=2)
        
        return sync_data
    
    # ============ INSIGHT GENERATION ============
    
    def generate_insights(self) -> List[Dict]:
        """Generate insights from all tracked data"""
        insights = []
        
        # Analyze decision patterns
        all_decisions = self.decision_log.get_recent(100)
        
        if all_decisions:
            with_outcomes = [d for d in all_decisions if d.get("outcome")]
            success_rate = len([d for d in with_outcomes if d["outcome"] == "success"]) / len(with_outcomes) if with_outcomes else 0
            
            insights.append({
                "type": "decision_success_rate",
                "value": success_rate,
                "message": f"Recent decision success rate: {success_rate:.1%}",
                "generated_at": datetime.now().isoformat()
            })
        
        # Analyze memory patterns
        top_tags = sorted(self.memory_manager.tags_index.items(), 
                         key=lambda x: -len(x[1]))[:5]
        
        insights.append({
            "type": "top_memory_tags",
            "value": top_tags,
            "message": f"Top memory categories: {', '.join([t[0] for t in top_tags])}",
            "generated_at": datetime.now().isoformat()
        })
        
        # Pattern-based insights
        if self.patterns["success_patterns"]:
            insights.append({
                "type": "success_pattern_count",
                "value": len(self.patterns["success_patterns"]),
                "message": f"Learned {len(self.patterns['success_patterns'])} success patterns",
                "generated_at": datetime.now().isoformat()
            })
        
        self.insights["insights"] = insights
        self.insights["total_insights"] = len(insights)
        self.insights["last_generated"] = datetime.now().isoformat()
        self._save()
        
        return insights
    
    def generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Check for unrecorded outcomes
        pending = self._get_pending_outcomes()
        if len(pending) > 5:
            recommendations.append(f"Record outcomes for {len(pending)} pending decisions")
        
        # Check memory consolidation needs
        suggestions = self.memory_manager.suggest_memory_refresh()
        recommendations.extend(suggestions)
        
        # Pattern-based recommendations
        if self.patterns["failure_patterns"]:
            recommendations.append("Review failure patterns to avoid repeating mistakes")
        
        self.insights["recommendations"] = recommendations
        self._save()
        
        return recommendations
    
    # ============ UTILITY METHODS ============
    
    def _save_outcome_expectation(self, expectation: Dict):
        """Save outcome expectation"""
        expectations_file = os.path.join(self.ai_learning_dir, "outcome_expectations.json")
        
        expectations = []
        if os.path.exists(expectations_file):
            with open(expectations_file, 'r') as f:
                expectations = json.load(f)
        
        expectations.append(expectation)
        
        with open(expectations_file, 'w') as f:
            json.dump(expectations, f, indent=2)
    
    def _save_outcome_record(self, record: Dict):
        """Save outcome record"""
        outcomes_file = os.path.join(self.ai_learning_dir, "outcomes", 
                                    f"{datetime.now().strftime('%Y-%m')}.json")
        
        outcomes = []
        if os.path.exists(outcomes_file):
            with open(outcomes_file, 'r') as f:
                outcomes = json.load(f)
        
        outcomes.append(record)
        
        with open(outcomes_file, 'w') as f:
            json.dump(outcomes, f, indent=2)
    
    def _get_expected_outcome(self, decision_id: str) -> Optional[str]:
        """Get expected outcome for a decision"""
        expectations_file = os.path.join(self.ai_learning_dir, "outcome_expectations.json")
        
        if os.path.exists(expectations_file):
            with open(expectations_file, 'r') as f:
                expectations = json.load(f)
                for e in expectations:
                    if e["decision_id"] == decision_id:
                        return e["expected_outcome"]
        
        return None
    
    def _get_pending_outcomes(self) -> List[Dict]:
        """Get decisions with pending outcomes"""
        expectations_file = os.path.join(self.ai_learning_dir, "outcome_expectations.json")
        
        if os.path.exists(expectations_file):
            with open(expectations_file, 'r') as f:
                expectations = json.load(f)
                return [e for e in expectations if e["status"] == "pending"]
        
        return []
    
    def _outcomes_aligned(self, expected: str, actual: str) -> bool:
        """Check if expected and actual outcomes align"""
        if not expected:
            return True
        
        # Simple string matching - could be enhanced with semantic similarity
        expected_lower = expected.lower()
        actual_lower = actual.lower()
        
        return expected_lower in actual_lower or actual_lower in expected_lower
    
    def _categorize_decision(self, decision: str) -> str:
        """Categorize a decision by type"""
        decision_lower = decision.lower()
        
        categories = {
            "trading": ["trade", "buy", "sell", "position", "portfolio"],
            "coding": ["code", "build", "create", "implement", "develop"],
            "research": ["research", "analyze", "investigate", "study"],
            "automation": ["automate", "schedule", "cron", "workflow"],
            "communication": ["email", "message", "contact", "notify"],
            "maintenance": ["fix", "repair", "update", "upgrade", "refactor"]
        }
        
        for cat, keywords in categories.items():
            if any(kw in decision_lower for kw in keywords):
                return cat
        
        return "general"
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        # Simple keyword extraction
        words = text.lower().split()
        # Filter out common words
        stop_words = {"the", "a", "an", "is", "are", "was", "were", "be", "been", 
                     "being", "have", "has", "had", "do", "does", "did", "will",
                     "would", "could", "should", "may", "might", "must", "shall",
                     "can", "need", "dare", "ought", "used", "to", "of", "in",
                     "for", "on", "with", "at", "by", "from", "as", "into",
                     "through", "during", "before", "after", "above", "below",
                     "between", "under", "and", "but", "or", "yet", "so"}
        
        keywords = [w.strip(".,!?;:'\"") for w in words if w.strip(".,!?;:'\"") not in stop_words and len(w) > 3]
        return list(set(keywords))[:10]  # Return unique keywords, max 10
    
    def _find_common_elements(self, texts: List[str]) -> List[str]:
        """Find common elements across texts"""
        if not texts:
            return []
        
        # Extract keywords from each text
        all_keywords = [self._extract_keywords(t) for t in texts if t]
        
        if not all_keywords:
            return []
        
        # Find common keywords
        common = set(all_keywords[0])
        for keywords in all_keywords[1:]:
            common &= set(keywords)
        
        return list(common)[:5]
    
    # ============ REPORTING ============
    
    def generate_report(self) -> str:
        """Generate comprehensive AI learning report"""
        lines = [
            "=" * 60,
            "🧠 AI LEARNING SYSTEM REPORT",
            "=" * 60,
            "",
            f"Generated: {datetime.now().isoformat()}",
            "",
            "📊 DECISION TRACKING",
            "-" * 40,
        ]
        
        # Decision stats
        recent_decisions = self.decision_log.get_recent(100)
        with_outcomes = [d for d in recent_decisions if d.get("outcome")]
        success_count = len([d for d in with_outcomes if d["outcome"] == "success"])
        
        lines.extend([
            f"Total decisions tracked: {len(recent_decisions)}",
            f"Decisions with outcomes: {len(with_outcomes)}",
            f"Success rate: {success_count / len(with_outcomes) * 100:.1f}%" if with_outcomes else "Success rate: N/A",
            "",
            "🧩 LEARNED PATTERNS",
            "-" * 40,
            f"Success patterns: {len(self.patterns.get('success_patterns', []))}",
            f"Failure patterns: {len(self.patterns.get('failure_patterns', []))}",
            f"Decision patterns: {len(self.patterns.get('decision_patterns', []))}",
            "",
            "📝 MEMORY INTEGRATION",
            "-" * 40,
            f"Files indexed: {self.memory_manager.state.get('total_files_indexed', 0)}",
            f"Tags created: {self.memory_manager.state.get('tags_created', 0)}",
            "",
            "💡 RECENT INSIGHTS",
            "-" * 40,
        ])
        
        for insight in self.insights.get("insights", [])[-5:]:
            lines.append(f"• {insight['message']}")
        
        lines.extend([
            "",
            "🎯 RECOMMENDATIONS",
            "-" * 40,
        ])
        
        for rec in self.insights.get("recommendations", [])[:5]:
            lines.append(f"• {rec}")
        
        lines.extend([
            "",
            "=" * 60,
        ])
        
        return "\n".join(lines)


# ============ COMMAND LINE INTERFACE ============

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Learning System - Integrated learning module")
    parser.add_argument("--mode", choices=["report", "sync", "insights", "patterns", "test"], 
                       default="report")
    parser.add_argument("--decision", help="Decision to log")
    parser.add_argument("--rationale", help="Decision rationale")
    parser.add_argument("--expected", help="Expected outcome")
    parser.add_argument("--decision-id", help="Decision ID for outcome recording")
    parser.add_argument("--outcome", help="Actual outcome")
    parser.add_argument("--impact", type=int, help="Impact score (-5 to +5)")
    
    args = parser.parse_args()
    
    ai = AILearningSystem()
    
    if args.mode == "report":
        print(ai.generate_report())
    
    elif args.mode == "sync":
        result = ai.sync_with_aloe()
        print(f"✓ Synced {len(result['patterns'])} patterns to ALOE")
    
    elif args.mode == "insights":
        insights = ai.generate_insights()
        print(f"Generated {len(insights)} insights:")
        for i in insights:
            print(f"  • {i['message']}")
        
        recommendations = ai.generate_recommendations()
        print(f"\nRecommendations:")
        for r in recommendations:
            print(f"  • {r}")
    
    elif args.mode == "patterns":
        patterns = ai.extract_all_patterns()
        print(f"Extracted patterns from {len(patterns['by_category'])} categories")
        for cat, data in patterns['by_category'].items():
            print(f"  {cat}: {data['success_rate']:.1%} success rate")
    
    elif args.mode == "test":
        print("🧪 Testing AI Learning System...")
        
        # Test decision logging
        test_id = ai.log_decision_with_outcome(
            decision="Test trading strategy",
            rationale="Based on historical pattern analysis",
            expected_outcome="Positive returns",
            context="SOL/USDC pair",
            tags=["trading", "test"]
        )
        print(f"✓ Logged decision: {test_id}")
        
        # Test outcome recording
        result = ai.record_decision_outcome(
            decision_id=test_id,
            actual_outcome="success",
            impact_score=4,
            notes="Strategy performed well"
        )
        print(f"✓ Recorded outcome: {result['actual']}")
        
        # Test insights
        insights = ai.generate_insights()
        print(f"✓ Generated {len(insights)} insights")
        
        # Test patterns
        patterns = ai.extract_all_patterns()
        print(f"✓ Extracted patterns from {len(patterns['by_category'])} categories")
        
        print("✓ All tests passed!")


if __name__ == "__main__":
    main()
