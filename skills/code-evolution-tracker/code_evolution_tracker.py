#!/usr/bin/env python3
"""
Code Evolution Tracker v1.0
Tracks code changes over time, documents improvements

## ACA Plan:
1. Requirements: Monitor code files → track changes → document improvements
2. Architecture: GitWatcher → ChangeDetector → PatternExtractor → Reporter
3. Data Flow: Check git → Detect changes → Extract patterns → Save history
4. Edge Cases: No git, huge diffs, binary files, merge conflicts
5. Tool Constraints: Git commands, file read, JSON write
6. Error Handling: Git errors, file access, parse errors
7. Testing: Test with real git repo

Author: Autonomous Code Architect (ACA)
"""

import argparse
import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

WORKSPACE_DIR = Path("/home/skux/.openclaw/workspace")
MEMORY_DIR = WORKSPACE_DIR / "memory"


@dataclass
class CodeChange:
    file: str
    lines_added: int
    lines_removed: int
    timestamp: str
    message: str
    author: str
    patterns: List[str]


class CodeEvolutionTracker:
    def __init__(self):
        self.changes: List[CodeChange] = []
        self.history_file = MEMORY_DIR / "code_evolution" / "history.json"
    
    def get_git_commits(self) -> List[Dict]:
        """Get recent git commits"""
        try:
            result = subprocess.run(
                ["git", "log", "--pretty=format:%H|%ci|%s|%an", "-20"],
                cwd=WORKSPACE_DIR,
                capture_output=True, text=True
            )
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if '|' in line:
                    parts = line.split('|')
                    commits.append({
                        "hash": parts[0],
                        "date": parts[1],
                        "message": parts[2],
                        "author": parts[3]
                    })
            
            return commits
        except Exception as e:
            print(f"Git error: {e}")
            return []
    
    def get_file_changes(self, commit_hash: str) -> List[Dict]:
        """Get file changes for a commit"""
        try:
            result = subprocess.run(
                ["git", "show", "--stat", commit_hash],
                cwd=WORKSPACE_DIR,
                capture_output=True, text=True
            )
            
            changes = []
            for line in result.stdout.split('\n'):
                # Match: file | 10 +++---
                match = re.match(r'^(.*?)\s+\|\s+(\d+)\s+([+-]+)', line)
                if match:
                    changes.append({
                        "file": match.group(1).strip(),
                        "lines": int(match.group(2)),
                        "change": match.group(3)
                    })
            
            return changes
        except:
            return []
    
    def extract_patterns(self, message: str, files: List[str]) -> List[str]:
        """Extract improvement patterns from commit"""
        patterns = []
        
        msg_lower = message.lower()
        
        # Detect patterns
        if "refactor" in msg_lower:
            patterns.append("refactoring")
        if "fix" in msg_lower or "bug" in msg_lower:
            patterns.append("bugfix")
        if "add" in msg_lower or "implement" in msg_lower:
            patterns.append("new_feature")
        if "test" in msg_lower:
            patterns.append("testing")
        if "doc" in msg_lower:
            patterns.append("documentation")
        if "optimize" in msg_lower or "improve" in msg_lower:
            patterns.append("optimization")
        if "upgrade" in msg_lower or "evolve" in msg_lower:
            patterns.append("evolution")
        
        if not patterns:
            patterns.append("miscellaneous")
        
        return patterns
    
    def track_changes(self) -> List[CodeChange]:
        """Track code evolution"""
        commits = self.get_git_commits()
        
        for commit in commits:
            files = self.get_file_changes(commit["hash"])
            patterns = self.extract_patterns(commit["message"], [f["file"] for f in files])
            
            for f in files:
                change = CodeChange(
                    file=f["file"],
                    lines_added=f["change"].count('+'),
                    lines_removed=f["change"].count('-'),
                    timestamp=commit["date"],
                    message=commit["message"],
                    author=commit["author"],
                    patterns=patterns
                )
                self.changes.append(change)
        
        return self.changes
    
    def generate_report(self) -> str:
        """Generate evolution report"""
        if not self.changes:
            return "No changes tracked."
        
        report = []
        report.append("# Code Evolution Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append("")
        
        # Stats
        total_changes = len(self.changes)
        total_additions = sum(c.lines_added for c in self.changes)
        total_removals = sum(c.lines_removed for c in self.changes)
        
        report.append("## Statistics")
        report.append(f"- Total changes tracked: {total_changes}")
        report.append(f"- Lines added: {total_additions}")
        report.append(f"- Lines removed: {total_removals}")
        report.append(f"- Net change: {total_additions - total_removals:+d}")
        report.append("")
        
        # Pattern breakdown
        all_patterns = [p for c in self.changes for p in c.patterns]
        pattern_counts = {}
        for p in all_patterns:
            pattern_counts[p] = pattern_counts.get(p, 0) + 1
        
        report.append("## Pattern Breakdown")
        for pattern, count in sorted(pattern_counts.items(), key=lambda x: -x[1]):
            report.append(f"- {pattern}: {count} occurrences")
        report.append("")
        
        # Recent changes
        report.append("## Recent Changes")
        for change in sorted(self.changes, key=lambda x: x.timestamp, reverse=True)[:10]:
            report.append(f"\n### {change.file}")
            report.append(f"- Lines: +{change.lines_added}/-{change.lines_removed}")
            report.append(f"- Patterns: {', '.join(change.patterns)}")
            report.append(f"- Message: {change.message[:50]}...")
        
        return "\n".join(report)
    
    def run(self) -> Dict:
        """Main execution"""
        # Ensure directories
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Track changes
        changes = self.track_changes()
        
        # Save history
        history = {
            "last_run": datetime.now().isoformat(),
            "total_changes": len(changes),
            "changes": [{"file": c.file, "patterns": c.patterns} for c in changes]
        }
        
        with open(self.history_file, "w") as f:
            json.dump(history, f, indent=2)
        
        # Generate report
        report = self.generate_report()
        report_file = MEMORY_DIR / "code_evolution" / "report.md"
        with open(report_file, "w") as f:
            f.write(report)
        
        return {
            "success": True,
            "changes_tracked": len(changes),
            "history_file": str(self.history_file),
            "report": str(report_file)
        }


def main():
    parser = argparse.ArgumentParser(description="Code Evolution Tracker")
    args = parser.parse_args()
    
    tracker = CodeEvolutionTracker()
    result = tracker.run()
    
    if result.get("success"):
        print(f"✓ Evolution tracking complete")
        print(f"  Changes tracked: {result['changes_tracked']}")
    else:
        print(f"✗ Error")


if __name__ == "__main__":
    main()
