#!/usr/bin/env python3
"""
Decision Log - ACA Built v1.0
Log decisions with rationale, dates, context. Store in memory/decisions/
"""

import json
import os
import sys
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import argparse


class DecisionLog:
    """Tracks decisions with full context and rationale."""
    
    def __init__(self, memory_dir: str = None):
        self.memory_dir = memory_dir or os.path.expanduser("~/.openclaw/workspace/memory/decisions")
        self.decisions_file = os.path.join(self.memory_dir, "decisions.json")
        self.index_file = os.path.join(self.memory_dir, "index.json")
        self.logs_dir = os.path.join(self.memory_dir, "logs")
        self._ensure_dirs()
        self.decisions = self._load_decisions()
        self.index = self._load_index()
    
    def _ensure_dirs(self):
        Path(self.memory_dir).mkdir(parents=True, exist_ok=True)
        Path(self.logs_dir).mkdir(parents=True, exist_ok=True)
    
    def _load_decisions(self) -> List[Dict]:
        try:
            if os.path.exists(self.decisions_file):
                with open(self.decisions_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self._log_error(f"Decisions load failed: {e}")
        return []
    
    def _load_index(self) -> Dict:
        defaults = {"total_decisions": 0, "tags": {}, "last_updated": datetime.now().isoformat()}
        try:
            if os.path.exists(self.index_file):
                with open(self.index_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self._log_error(f"Index load failed: {e}")
        return defaults
    
    def _save(self):
        try:
            with open(self.decisions_file, 'w') as f:
                json.dump(self.decisions, f, indent=2)
            with open(self.index_file, 'w') as f:
                json.dump(self.index, f, indent=2)
        except Exception as e:
            self._log_error(f"Save failed: {e}")
    
    def _log_error(self, message: str):
        log_file = os.path.join(self.logs_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log")
        with open(log_file, 'a') as f:
            f.write(f"{datetime.now().isoformat()} | ERROR | {message}\n")
    
    def log_decision(self, decision: str, rationale: str, context: str = "", 
                     tags: List[str] = None, alternatives: List[str] = None) -> str:
        """Log a new decision."""
        
        decision_id = hashlib.md5(f"{decision}{datetime.now().isoformat()}".encode()).hexdigest()[:12]
        
        entry = {
            "id": decision_id,
            "timestamp": datetime.now().isoformat(),
            "decision": decision,
            "rationale": rationale,
            "context": context,
            "tags": tags or [],
            "alternatives": alternatives or [],
            "outcome": None,
            "outcome_recorded": None
        }
        
        self.decisions.append(entry)
        self.index["total_decisions"] = len(self.decisions)
        self.index["last_updated"] = datetime.now().isoformat()
        
        # Update tag index
        for tag in entry["tags"]:
            if tag not in self.index["tags"]:
                self.index["tags"][tag] = []
            self.index["tags"][tag].append(decision_id)
        
        self._save()
        return decision_id
    
    def record_outcome(self, decision_id: str, outcome: str, notes: str = "") -> bool:
        """Record the outcome of a decision."""
        for d in self.decisions:
            if d["id"] == decision_id:
                d["outcome"] = outcome
                d["outcome_recorded"] = datetime.now().isoformat()
                d["outcome_notes"] = notes
                self._save()
                return True
        return False
    
    def search_by_tag(self, tag: str) -> List[Dict]:
        """Find decisions by tag."""
        decision_ids = self.index.get("tags", {}).get(tag, [])
        return [d for d in self.decisions if d["id"] in decision_ids]
    
    def search(self, query: str) -> List[Dict]:
        """Search decisions by text."""
        query = query.lower()
        results = []
        for d in self.decisions:
            if (query in d["decision"].lower() or 
                query in d["rationale"].lower() or
                query in d.get("context", "").lower()):
                results.append(d)
        return results
    
    def get_recent(self, limit: int = 10) -> List[Dict]:
        """Get recent decisions."""
        return sorted(self.decisions, key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    def get_by_id(self, decision_id: str) -> Optional[Dict]:
        """Get decision by ID."""
        for d in self.decisions:
            if d["id"] == decision_id:
                return d
        return None
    
    def generate_report(self, days: int = 30) -> str:
        """Generate decision report."""
        cutoff = (datetime.now() - __import__('datetime').timedelta(days=days)).isoformat()
        recent = [d for d in self.decisions if d["timestamp"] > cutoff]
        
        lines = [
            f"Decision Report (Last {days} days)",
            f"Total decisions: {len(recent)}",
            f"Without outcomes: {len([d for d in recent if not d.get('outcome')])}",
            "",
            "Recent decisions:",
        ]
        
        for d in sorted(recent, key=lambda x: x["timestamp"], reverse=True)[:5]:
            outcome = f"[Outcome: {d.get('outcome', 'pending')}]" if d.get('outcome') else "[pending]"
            lines.append(f"  {d['timestamp'][:10]} | {d['id'][:8]} | {d['decision'][:50]}... {outcome}")
        
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Decision Log - Track decisions with rationale")
    parser.add_argument("--mode", choices=["log", "outcome", "search", "recent", "report", "test"], default="recent")
    parser.add_argument("--decision", "-d", help="Decision description")
    parser.add_argument("--rationale", "-r", help="Decision rationale")
    parser.add_argument("--context", "-c", help="Additional context")
    parser.add_argument("--tags", "-t", help="Comma-separated tags")
    parser.add_argument("--id", help="Decision ID")
    parser.add_argument("--outcome", help="Outcome status")
    parser.add_argument("--query", "-q", help="Search query")
    
    args = parser.parse_args()
    
    log = DecisionLog()
    
    if args.mode == "log":
        if not args.decision or not args.rationale:
            print("Error: --decision and --rationale required")
            sys.exit(1)
        tags = [t.strip() for t in args.tags.split(",")] if args.tags else []
        decision_id = log.log_decision(args.decision, args.rationale, args.context or "", tags)
        print(f"✓ Logged decision: {decision_id}")
    
    elif args.mode == "outcome":
        if not args.id or not args.outcome:
            print("Error: --id and --outcome required")
            sys.exit(1)
        if log.record_outcome(args.id, args.outcome):
            print(f"✓ Recorded outcome for {args.id}")
        else:
            print(f"✗ Decision {args.id} not found")
    
    elif args.mode == "search":
        if not args.query:
            print("Error: --query required")
            sys.exit(1)
        results = log.search(args.query)
        print(f"Found {len(results)} decisions:")
        for d in results[:5]:
            print(f"  {d['id'][:8]} | {d['decision'][:50]}...")
    
    elif args.mode == "recent":
        recent = log.get_recent(10)
        print(f"Last {len(recent)} decisions:")
        for d in recent:
            print(f"  {d['timestamp'][:10]} | {d['id'][:8]} | {d['decision'][:50]}...")
    
    elif args.mode == "report":
        print(log.generate_report(30))
    
    elif args.mode == "test":
        print("🧪 Running tests...")
        # Test logging
        test_id = log.log_decision("Test decision", "Test rationale", tags=["test", "aca"])
        print(f"✓ Logged: {test_id}")
        # Test outcome
        log.record_outcome(test_id, "success")
        print("✓ Outcome recorded")
        # Test search
        results = log.search("test")
        print(f"✓ Search found {len(results)} results")
        print("✓ All tests passed")


if __name__ == "__main__":
    main()
