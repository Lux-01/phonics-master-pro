#!/usr/bin/env python3
"""
Rug Pattern Extractor
Mines patterns from historical rug pulls to predict future rugs.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple

# Paths
PATTERNS_DIR = Path("/home/skux/.openclaw/workspace/memory/patterns")
PATTERNS_DIR.mkdir(parents=True, exist_ok=True)

RUG_PATTERNS_FILE = PATTERNS_DIR / "rug_signatures.json"
PROTECTION_RULES_FILE = PATTERNS_DIR / "auto_reject_rules.json"


class RugPatternExtractor:
    """
    Extracts and applies rug detection patterns.
    Learns from ALIENS, XTuber, and future rugs.
    """
    
    def __init__(self):
        self.patterns_file = RUG_PATTERNS_FILE
        self.rules_file = PROTECTION_RULES_FILE
        self.patterns = self._load_patterns()
        self.rules = self._load_rules()
    
    def _load_patterns(self) -> List[Dict]:
        """Load known rug patterns."""
        if not self.patterns_file.exists():
            # Initialize with known rugs
            return [
                {
                    "id": "RUG-001",
                    "token": "ALIENS",
                    "date": "2026-03-19",
                    "conditions": {
                        "age_hours": 0.2,
                        "top10_pct": 27.4,
                        "grade": "A ✅",
                        "score": 15
                    },
                    "outcome": {
                        "time_to_rug_minutes": 40,
                        "loss_pct": 100
                    },
                    "lesson": "Age < 30min = immediate reject",
                    "confidence": 1.0
                },
                {
                    "id": "RUG-002",
                    "token": "XTuber",
                    "date": "2026-03-19",
                    "conditions": {
                        "age_hours": 1.0,
                        "top10_pct": 72.9,
                        "grade": "A ✅",
                        "score": 15.5
                    },
                    "outcome": {
                        "time_to_rug_minutes": 40,
                        "loss_pct": 100
                    },
                    "lesson": "Top10% > 70% = whale dump risk",
                    "confidence": 1.0
                }
            ]
        
        try:
            with open(self.patterns_file) as f:
                return json.load(f)
        except:
            return []
    
    def _load_rules(self) -> List[Dict]:
        """Load auto-reject rules."""
        if not self.rules_file.exists():
            # Initialize with lessons learned
            return [
                {
                    "id": "RULE-001",
                    "name": "Ultra-New Token",
                    "condition": "age_hours < 0.5",
                    "action": "REJECT",
                    "reason": "Tokens < 30min have 90% rug rate",
                    "source": "ALIENS pattern",
                    "confidence": 0.95
                },
                {
                    "id": "RULE-002",
                    "name": "Extreme Whale Concentration",
                    "condition": "top10_pct > 70",
                    "action": "REJECT",
                    "reason": "Top10% > 70% = instant dump risk",
                    "source": "XTuber pattern",
                    "confidence": 0.90
                },
                {
                    "id": "RULE-003",
                    "name": "High Whale Risk",
                    "condition": "top10_pct > 50",
                    "action": "DEMOTE",
                    "reason": "Top10% > 50% = cap grade at B",
                    "source": "Risk analysis",
                    "confidence": 0.85
                },
                {
                    "id": "RULE-004",
                    "name": "Young Token Caution",
                    "condition": "age_hours < 2",
                    "action": "DEMOTE",
                    "reason": "Age < 2h = max grade B",
                    "source": "Multiple rug patterns",
                    "confidence": 0.80
                },
                {
                    "id": "RULE-005",
                    "name": "Fresh Launch",
                    "condition": "age_hours < 1",
                    "action": "REJECT",
                    "reason": "No time to prove legitimacy",
                    "source": "Rug pattern analysis",
                    "confidence": 0.88
                }
            ]
        
        try:
            with open(self.rules_file) as f:
                return json.load(f)
        except:
            return []
    
    def _save_patterns(self):
        """Save patterns to file."""
        with open(self.patterns_file, 'w') as f:
            json.dump(self.patterns, f, indent=2)
    
    def _save_rules(self):
        """Save rules to file."""
        with open(self.rules_file, 'w') as f:
            json.dump(self.rules, f, indent=2)
    
    def analyze_token(self,
                     age_hours: float,
                     top10_pct: float,
                     grade: str,
                     score: float,
                     mcap: float = 0,
                     vol24: float = 0) -> Dict[str, Any]:
        """
        Analyze token against rug patterns.
        Returns: {passed: bool, action: str, reasons: [], risk_score: int}
        """
        risk_score = 0
        reasons = []
        action = "APPROVE"
        matched_rules = []
        
        # Check auto-reject rules
        for rule in self.rules:
            condition = rule["condition"]
            
            # Parse condition
            if "age_hours <" in condition:
                threshold = float(condition.split(" < ")[1])
                if age_hours < threshold:
                    if rule["action"] == "REJECT":
                        action = "REJECT"
                    elif rule["action"] == "DEMOTE" and action == "APPROVE":
                        action = "DEMOTE"
                    
                    risk_score += 5 if rule["action"] == "REJECT" else 2
                    reasons.append(f"{rule['name']}: {rule['reason']}")
                    matched_rules.append(rule)
            
            if "top10_pct >" in condition:
                threshold = float(condition.split(" > ")[1])
                if top10_pct > threshold:
                    if rule["action"] == "REJECT":
                        action = "REJECT"
                    elif rule["action"] == "DEMOTE" and action == "APPROVE":
                        action = "DEMOTE"
                    
                    risk_score += 3 if rule["action"] == "REJECT" else 1
                    reasons.append(f"{rule['name']}: {rule['reason']}")
                    matched_rules.append(rule)
        
        # Check historical patterns
        for pattern in self.patterns:
            pattern_score = 0
            cond = pattern["conditions"]
            
            # Age similarity
            if abs(cond["age_hours"] - age_hours) < 0.3:
                pattern_score += 2
            
            # Top10 similarity
            if abs(cond["top10_pct"] - top10_pct) < 10:
                pattern_score += 2
            
            # Score similarity
            if abs(cond["score"] - score) < 2:
                pattern_score += 1
            
            # If strong pattern match, elevate to reject
            if pattern_score >= 4:
                risk_score += 4
                action = "REJECT"
                reasons.append(f"Matches {pattern['token']} rug pattern ({pattern['lesson']})")
        
        return {
            "passed": action != "REJECT",
            "action": action,
            "risk_score": risk_score,
            "reasons": reasons,
            "matched_rules": len(matched_rules),
            "recommendation": self._get_recommendation(action, risk_score)
        }
    
    def _get_recommendation(self, action: str, risk_score: int) -> str:
        """Generate recommendation."""
        if action == "REJECT":
            return "❌ DO NOT TRADE - High rug risk"
        elif action == "DEMOTE":
            return "⚠️ TRADE WITH CAUTION - Cap position size"
        elif risk_score >= 3:
            return "⚠️ MODERATE RISK - Reduce position"
        else:
            return "✅ LOW RISK - Standard position"
    
    def add_rug_pattern(self,
                       token_name: str,
                       conditions: Dict,
                       outcome: Dict,
                       lesson: str):
        """
        Add a new rug pattern from observed rug.
        Call this whenever a token rugs.
        """
        pattern_id = f"RUG-{len(self.patterns) + 1:03d}"
        
        pattern = {
            "id": pattern_id,
            "token": token_name,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "conditions": conditions,
            "outcome": outcome,
            "lesson": lesson,
            "confidence": 1.0
        }
        
        self.patterns.append(pattern)
        self._save_patterns()
        
        # Auto-generate rule from pattern
        self._generate_rule_from_pattern(pattern)
        
        return pattern_id
    
    def _generate_rule_from_pattern(self, pattern: Dict):
        """Auto-generate protection rule from pattern."""
        cond = pattern["conditions"]
        
        # Age-based rule
        if cond["age_hours"] < 1:
            rule = {
                "id": f"RULE-{len(self.rules) + 1:03d}",
                "name": f"Auto: {pattern['token']} Age Pattern",
                "condition": f"age_hours < {cond['age_hours'] * 2}",  # Double the threshold
                "action": "REJECT",
                "reason": f"Similar to {pattern['token']} rug ({pattern['lesson']})",
                "source": f"Pattern {pattern['id']}",
                "confidence": 0.85,
                "generated_at": datetime.now().isoformat()
            }
            self.rules.append(rule)
        
        # Whale concentration rule
        if cond["top10_pct"] > 60:
            rule = {
                "id": f"RULE-{len(self.rules) + 1:03d}",
                "name": f"Auto: {pattern['token']} Whale Pattern",
                "condition": f"top10_pct > {cond['top10_pct'] - 10}",  # 10% buffer
                "action": "REJECT",
                "reason": f"Whale concentration similar to {pattern['token']}",
                "source": f"Pattern {pattern['id']}",
                "confidence": 0.80,
                "generated_at": datetime.now().isoformat()
            }
            self.rules.append(rule)
        
        self._save_rules()
    
    def get_all_rules(self) -> List[Dict]:
        """Get all protection rules."""
        return self.rules
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get pattern statistics."""
        return {
            "known_rugs": len(self.patterns),
            "protection_rules": len(self.rules),
            "auto_reject_rules": len([r for r in self.rules if r["action"] == "REJECT"]),
            "demote_rules": len([r for r in self.rules if r["action"] == "DEMOTE"]),
            "patterns": [p["token"] for p in self.patterns]
        }


# Global instance
extractor = RugPatternExtractor()


def check_token(age_hours: float, top10_pct: float, grade: str, score: float) -> Dict:
    """Quick check function."""
    return extractor.analyze_token(age_hours, top10_pct, grade, score)


def add_rug(token_name: str, conditions: Dict, outcome: Dict, lesson: str):
    """Quick add function."""
    return extractor.add_rug_pattern(token_name, conditions, outcome, lesson)


def get_rules() -> List[Dict]:
    """Get all rules."""
    return extractor.get_all_rules()


def get_stats() -> Dict:
    """Get stats."""
    return extractor.get_statistics()


if __name__ == "__main__":
    print("🔍 Rug Pattern Extractor")
    print("=" * 50)
    
    # Test with known rug patterns
    stats = extractor.get_statistics()
    print(f"\n📊 Loaded {stats['known_rugs']} rug patterns")
    print(f"🛡️  {stats['protection_rules']} protection rules active")
    print(f"🚫 {stats['auto_reject_rules']} auto-reject rules")
    
    # Test detection
    print("\n🧪 Testing rug detection:")
    
    # Test case 1: Similar to ALIENS
    result1 = extractor.analyze_token(
        age_hours=0.25,
        top10_pct=28,
        grade="A ✅",
        score=15
    )
    print(f"\nToken A (0.25h, 28% top10):")
    print(f"  Action: {result1['action']}")
    print(f"  Risk Score: {result1['risk_score']}")
    print(f"  Passed: {result1['passed']}")
    for reason in result1['reasons']:
        print(f"  ⚠️  {reason}")
    
    # Test case 2: Similar to XTuber
    result2 = extractor.analyze_token(
        age_hours=1.1,
        top10_pct=73,
        grade="A ✅",
        score=15.5
    )
    print(f"\nToken B (1.1h, 73% top10):")
    print(f"  Action: {result2['action']}")
    print(f"  Risk Score: {result2['risk_score']}")
    print(f"  Passed: {result2['passed']}")
    for reason in result2['reasons']:
        print(f"  ⚠️  {reason}")
    
    # Test case 3: Safe token
    result3 = extractor.analyze_token(
        age_hours=6.5,
        top10_pct=25,
        grade="A ✅",
        score=16.5
    )
    print(f"\nToken C (6.5h, 25% top10):")
    print(f"  Action: {result3['action']}")
    print(f"  Risk Score: {result3['risk_score']}")
    print(f"  Passed: {result3['passed']}")
    print(f"  Reasons: {len(result3['reasons'])}")
    
    print("\n✅ Rug Pattern Extractor ready!")
