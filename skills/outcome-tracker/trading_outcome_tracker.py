#!/usr/bin/env python3
"""
Trading Outcome Tracker for ALOE
Tracks every scanner signal and its outcome to improve future predictions.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Paths
OUTCOMES_DIR = Path("/home/skux/.openclaw/workspace/memory/outcomes")
OUTCOMES_DIR.mkdir(parents=True, exist_ok=True)

OUTCOMES_FILE = OUTCOMES_DIR / "trading_outcomes.json"
PATTERNS_FILE = OUTCOMES_DIR / "rug_patterns.json"


class TradingOutcomeTracker:
    """
    Tracks outcomes of scanner signals to improve accuracy.
    Learns which Grade A tokens actually profit vs rug.
    """
    
    def __init__(self):
        self.outcomes_file = OUTCOMES_FILE
        self.patterns_file = PATTERNS_FILE
        self.outcomes = self._load_outcomes()
        self.patterns = self._load_patterns()
    
    def _load_outcomes(self) -> list:
        """Load existing outcomes."""
        if not self.outcomes_file.exists():
            return []
        try:
            with open(self.outcomes_file) as f:
                return json.load(f)
        except:
            return []
    
    def _load_patterns(self) -> dict:
        """Load existing patterns."""
        if not self.patterns_file.exists():
            return {
                "rug_signatures": [],
                "success_signatures": [],
                "false_positives": []
            }
        try:
            with open(self.patterns_file) as f:
                return json.load(f)
        except:
            return {
                "rug_signatures": [],
                "success_signatures": [],
                "false_positives": []
            }
    
    def _save_outcomes(self):
        """Save outcomes to file."""
        with open(self.outcomes_file, 'w') as f:
            json.dump(self.outcomes, f, indent=2, default=str)
    
    def _save_patterns(self):
        """Save patterns to file."""
        with open(self.patterns_file, 'w') as f:
            json.dump(self.patterns, f, indent=2)
    
    def log_signal(self, 
                     token_ca: str,
                     token_name: str,
                     scanner_version: str,
                     grade: str,
                     score: float,
                     age_hours: float,
                     top10_pct: float,
                     mcap: float,
                     liq: float,
                     vol24: float) -> str:
        """
        Log a new scanner signal.
        Returns signal_id for later outcome tracking.
        """
        signal_id = f"SIG-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{token_ca[:8]}"
        
        signal = {
            "signal_id": signal_id,
            "timestamp": datetime.now().isoformat(),
            "token": {
                "ca": token_ca,
                "name": token_name
            },
            "scanner": {
                "version": scanner_version,
                "grade": grade,
                "score": score
            },
            "metrics": {
                "age_hours": age_hours,
                "top10_pct": top10_pct,
                "mcap": mcap,
                "liq": liq,
                "vol24": vol24
            },
            "outcome": {
                "status": "PENDING",
                "profit_pct": None,
                "time_to_outcome_hours": None,
                "lesson": None
            }
        }
        
        self.outcomes.append(signal)
        self._save_outcomes()
        
        return signal_id
    
    def update_outcome(self,
                       signal_id: str,
                       outcome_status: str,  # "PROFIT", "LOSS", "RUG", "PENDING"
                       profit_pct: Optional[float] = None,
                       lesson: Optional[str] = None):
        """
        Update outcome for a signal.
        Call this after trade completes or token rugs.
        """
        for signal in self.outcomes:
            if signal["signal_id"] == signal_id:
                signal["outcome"]["status"] = outcome_status
                signal["outcome"]["profit_pct"] = profit_pct
                
                start_time = datetime.fromisoformat(signal["timestamp"])
                end_time = datetime.now()
                hours_elapsed = (end_time - start_time).total_seconds() / 3600
                signal["outcome"]["time_to_outcome_hours"] = hours_elapsed
                signal["outcome"]["lesson"] = lesson
                
                # Auto-extract pattern
                self._extract_pattern(signal)
                
                self._save_outcomes()
                return True
        
        return False
    
    def _extract_pattern(self, signal: Dict):
        """Auto-extract pattern from outcome."""
        if signal["outcome"]["status"] == "RUG":
            pattern = {
                "type": "rug_signature",
                "conditions": {
                    "age_hours": signal["metrics"]["age_hours"],
                    "top10_pct": signal["metrics"]["top10_pct"],
                    "grade": signal["scanner"]["grade"],
                    "score": signal["scanner"]["score"]
                },
                "outcome": "RUG",
                "confidence": 1.0,
                "lesson": signal["outcome"]["lesson"]
            }
            self.patterns["rug_signatures"].append(pattern)
            
        elif signal["outcome"]["status"] == "PROFIT":
            pattern = {
                "type": "success_signature",
                "conditions": {
                    "age_hours": signal["metrics"]["age_hours"],
                    "top10_pct": signal["metrics"]["top10_pct"],
                    "grade": signal["scanner"]["grade"],
                    "score": signal["scanner"]["score"]
                },
                "outcome": "PROFIT",
                "profit_pct": signal["outcome"]["profit_pct"],
                "confidence": 1.0
            }
            self.patterns["success_signatures"].append(pattern)
            
        elif signal["outcome"]["status"] == "LOSS":
            # Grade A but lost money = false positive
            if signal["scanner"]["grade"] in ["A", "A+", "A ✅"]:
                pattern = {
                    "type": "false_positive",
                    "conditions": {
                        "age_hours": signal["metrics"]["age_hours"],
                        "top10_pct": signal["metrics"]["top10_pct"],
                        "score": signal["scanner"]["score"]
                    },
                    "outcome": "LOSS",
                    "lesson": signal["outcome"]["lesson"]
                }
                self.patterns["false_positives"].append(pattern)
        
        self._save_patterns()
    
    def get_risk_assessment(self, 
                           age_hours: float,
                           top10_pct: float,
                           grade: str) -> Dict[str, Any]:
        """
        Get risk assessment based on historical patterns.
        Call this before sending signal to user.
        """
        risk_score = 0
        warnings = []
        
        # Check against rug patterns
        for pattern in self.patterns.get("rug_signatures", []):
            cond = pattern["conditions"]
            
            # Age similarity
            if abs(cond["age_hours"] - age_hours) < 0.5:
                risk_score += 3
                warnings.append(f"Age pattern matches known rug ({cond['age_hours']:.1f}h)")
            
            # Top10 similarity
            if abs(cond["top10_pct"] - top10_pct) < 5:
                risk_score += 2
                warnings.append(f"Top10% pattern matches known rug ({cond['top10_pct']:.1f}%)")
        
        # Check false positives
        fp_count = 0
        for pattern in self.patterns.get("false_positives", []):
            cond = pattern["conditions"]
            if abs(cond["age_hours"] - age_hours) < 1:
                fp_count += 1
        
        if fp_count >= 2:
            risk_score += 2
            warnings.append(f"Similar to {fp_count} previous Grade A losses")
        
        # Determine risk level
        if risk_score >= 5:
            risk_level = "HIGH"
        elif risk_score >= 3:
            risk_level = "MEDIUM"
        elif risk_score >= 1:
            risk_level = "LOW"
        else:
            risk_level = "MINIMAL"
        
        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "warnings": warnings,
            "recommendation": "AVOID" if risk_level == "HIGH" else "CAUTION" if risk_level == "MEDIUM" else "PROCEED"
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get outcome statistics."""
        total = len(self.outcomes)
        rugs = sum(1 for o in self.outcomes if o["outcome"]["status"] == "RUG")
        profits = sum(1 for o in self.outcomes if o["outcome"]["status"] == "PROFIT")
        losses = sum(1 for o in self.outcomes if o["outcome"]["status"] == "LOSS")
        pending = sum(1 for o in self.outcomes if o["outcome"]["status"] == "PENDING")
        
        # Calculate Grade A accuracy
        grade_a_signals = [o for o in self.outcomes if "A" in o["scanner"]["grade"]]
        grade_a_rugs = sum(1 for o in grade_a_signals if o["outcome"]["status"] == "RUG")
        grade_a_accuracy = 1.0 - (grade_a_rugs / len(grade_a_signals)) if grade_a_signals else 0
        
        return {
            "total_signals": total,
            "rugs": rugs,
            "profits": profits,
            "losses": losses,
            "pending": pending,
            "grade_a_signals": len(grade_a_signals),
            "grade_a_rugs": grade_a_rugs,
            "grade_a_accuracy": f"{grade_a_accuracy:.1%}",
            "patterns_learned": {
                "rug_signatures": len(self.patterns.get("rug_signatures", [])),
                "success_signatures": len(self.patterns.get("success_signatures", [])),
                "false_positives": len(self.patterns.get("false_positives", []))
            }
        }


# Convenience functions for quick usage
tracker = TradingOutcomeTracker()


def log_scanner_signal(token_data: Dict) -> str:
    """Quick function to log a scanner signal."""
    return tracker.log_signal(
        token_ca=token_data.get("ca", ""),
        token_name=token_data.get("name", "?"),
        scanner_version=token_data.get("scanner_version", "v5.4"),
        grade=token_data.get("grade", "F"),
        score=token_data.get("score", 0),
        age_hours=token_data.get("age_hours", 0),
        top10_pct=token_data.get("top10_pct", 100),
        mcap=token_data.get("mcap", 0),
        liq=token_data.get("liq", 0),
        vol24=token_data.get("vol24", 0)
    )


def update_trade_outcome(signal_id: str, status: str, profit_pct: float = None, lesson: str = None):
    """Quick function to update outcome."""
    return tracker.update_outcome(signal_id, status, profit_pct, lesson)


def check_risk(age_hours: float, top10_pct: float, grade: str) -> Dict:
    """Quick risk check before trading."""
    return tracker.get_risk_assessment(age_hours, top10_pct, grade)


def get_stats() -> Dict:
    """Get current statistics."""
    return tracker.get_statistics()


if __name__ == "__main__":
    # Test with ALIENS data
    print("🧪 Testing Trading Outcome Tracker")
    print("=" * 50)
    
    # Log ALIENS signal
    aliens_signal = tracker.log_signal(
        token_ca="EHiXCnYmqc2bb1gLKdpWV6kwA1um9uW1zSP5JkC7pump",
        token_name="ALIENS",
        scanner_version="v5.4",
        grade="A ✅",
        score=15,
        age_hours=0.2,
        top10_pct=27.4,
        mcap=71855,
        liq=21624,
        vol24=176085
    )
    print(f"✅ Logged ALIENS signal: {aliens_signal}")
    
    # Update as rug
    tracker.update_outcome(
        signal_id=aliens_signal,
        outcome_status="RUG",
        lesson="Age < 30min = high rug risk"
    )
    print("✅ Updated ALIENS outcome: RUG")
    
    # Check risk for similar token
    risk = tracker.get_risk_assessment(
        age_hours=0.3,
        top10_pct=28,
        grade="A ✅"
    )
    print(f"\n🔍 Risk check for similar token:")
    print(f"   Risk Level: {risk['risk_level']}")
    print(f"   Warnings: {risk['warnings']}")
    
    # Get stats
    stats = tracker.get_statistics()
    print(f"\n📊 Statistics:")
    print(f"   Total signals: {stats['total_signals']}")
    print(f"   Rugs detected: {stats['rugs']}")
    print(f"   Grade A accuracy: {stats['grade_a_accuracy']}")
    print(f"   Patterns learned: {stats['patterns_learned']}")
