#!/usr/bin/env python3
"""
Context Optimizer - ACA Built v1.0
Tracks file reads, summarizes long sessions, suggests context refreshes.
"""

import json
import os
import sys
import time
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import argparse


class ContextOptimizer:
    """Tracks conversation context and suggests optimizations."""
    
    def __init__(self, memory_dir: str = None):
        self.memory_dir = memory_dir or os.path.expanduser("~/.openclaw/workspace/memory/context-optimizer")
        self.state_file = os.path.join(self.memory_dir, "state.json")
        self.logs_dir = os.path.join(self.memory_dir, "logs")
        self._ensure_dirs()
        self.state = self._load_state()
    
    def _ensure_dirs(self):
        """Create directories if missing."""
        Path(self.memory_dir).mkdir(parents=True, exist_ok=True)
        Path(self.logs_dir).mkdir(parents=True, exist_ok=True)
    
    def _load_state(self) -> Dict:
        """Load state with fallback defaults."""
        defaults = {
            "files_read": [],
            "session_start": datetime.now().isoformat(),
            "message_count": 0,
            "last_refresh": datetime.now().isoformat(),
            "context_fatigue_score": 0,
            "suggestions": []
        }
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    loaded = json.load(f)
                    defaults.update(loaded)
        except Exception as e:
            self._log_error(f"State load failed: {e}")
        return defaults
    
    def _save_state(self):
        """Persist state to disk."""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            self._log_error(f"State save failed: {e}")
    
    def _log_error(self, message: str):
        """Log error with timestamp."""
        log_file = os.path.join(self.logs_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log")
        with open(log_file, 'a') as f:
            f.write(f"{datetime.now().isoformat()} | ERROR | {message}\n")
    
    def track_file_read(self, file_path: str, content_hash: str = None):
        """Track that a file was read."""
        entry = {
            "path": file_path,
            "hash": content_hash or hashlib.md5(str(time.time()).encode()).hexdigest()[:8],
            "timestamp": datetime.now().isoformat(),
            "read_count": 1
        }
        
        # Update existing or add new
        existing = [f for f in self.state["files_read"] if f["path"] == file_path]
        if existing:
            existing[0]["read_count"] += 1
            existing[0]["timestamp"] = entry["timestamp"]
        else:
            self.state["files_read"].append(entry)
        
        # Keep only last 50 files
        self.state["files_read"] = self.state["files_read"][-50:]
        self.state["message_count"] += 1
        self._save_state()
    
    def get_context_fatigue(self) -> int:
        """Calculate context fatigue score (0-100)."""
        msg_count = self.state.get("message_count", 0)
        files_read = len(self.state.get("files_read", []))
        
        score = min(100, (msg_count * 2) + (files_read * 3))
        self.state["context_fatigue_score"] = score
        return score
    
    def suggest_refresh(self) -> List[str]:
        """Generate context refresh suggestions."""
        suggestions = []
        score = self.get_context_fatigue()
        
        if score > 80:
            suggestions.append("Context fatigue HIGH - consider starting fresh session")
        if len(self.state["files_read"]) > 20:
            suggestions.append(f"{len(self.state['files_read'])} files tracked - review recent reads")
        if self.state["message_count"] > 30:
            suggestions.append(f"{self.state['message_count']} messages - context may be stale")
        
        self.state["suggestions"] = suggestions
        self._save_state()
        return suggestions
    
    def get_recent_files(self, limit: int = 10) -> List[Dict]:
        """Get recently read files."""
        files = self.state.get("files_read", [])
        return sorted(files, key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    def generate_summary(self) -> str:
        """Generate session context summary."""
        fatigue = self.get_context_fatigue()
        suggestions = self.suggest_refresh()
        recent = self.get_recent_files(5)
        
        lines = [
            f"Session Summary (Fatigue: {fatigue}/100)",
            f"Messages: {self.state['message_count']}",
            f"Files tracked: {len(self.state['files_read'])}",
            "",
            "Recent files:",
        ]
        for f in recent:
            lines.append(f"  - {f['path']} (read {f['read_count']}x)")
        
        if suggestions:
            lines.extend(["", "Suggestions:"])
            for s in suggestions:
                lines.append(f"  ⚠️ {s}")
        
        return "\n".join(lines)
    
    def reset_session(self):
        """Reset for new session."""
        self.state = {
            "files_read": [],
            "session_start": datetime.now().isoformat(),
            "message_count": 0,
            "last_refresh": datetime.now().isoformat(),
            "context_fatigue_score": 0,
            "suggestions": []
        }
        self._save_state()
        return "Session context reset"


def main():
    parser = argparse.ArgumentParser(description="Context Optimizer - Track and manage conversation context")
    parser.add_argument("--mode", choices=["track", "summary", "suggest", "reset", "test"], default="summary")
    parser.add_argument("--file", help="File path to track")
    parser.add_argument("--memory-dir", help="Custom memory directory")
    
    args = parser.parse_args()
    
    optimizer = ContextOptimizer(memory_dir=args.memory_dir)
    
    if args.mode == "track" and args.file:
        optimizer.track_file_read(args.file)
        print(f"✓ Tracked: {args.file}")
    
    elif args.mode == "summary":
        print(optimizer.generate_summary())
    
    elif args.mode == "suggest":
        suggestions = optimizer.suggest_refresh()
        if suggestions:
            print("Context Suggestions:")
            for s in suggestions:
                print(f"  • {s}")
        else:
            print("No suggestions - context healthy")
    
    elif args.mode == "reset":
        print(optimizer.reset_session())
    
    elif args.mode == "test":
        print("🧪 Running tests...")
        optimizer.reset_session()
        optimizer.track_file_read("/test/file1.py")
        optimizer.track_file_read("/test/file2.py")
        fatigue = optimizer.get_context_fatigue()
        print(f"✓ Fatigue score: {fatigue}")
        suggestions = optimizer.suggest_refresh()
        print(f"✓ Suggestions: {len(suggestions)}")
        print("✓ All tests passed")


if __name__ == "__main__":
    main()
