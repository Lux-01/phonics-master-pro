#!/usr/bin/env python3
"""
Memory Manager - ACA Built v1.0
Auto-tagging, proactive surfacing, smart consolidation.
"""

import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
import argparse


class MemoryManager:
    """Manages memory with auto-tagging and smart consolidation."""
    
    def __init__(self, memory_dir: str = None):
        self.workspace_dir = os.path.expanduser("~/.openclaw/workspace")
        self.memory_dir = memory_dir or os.path.join(self.workspace_dir, "memory")
        self.state_file = os.path.join(self.memory_dir, "memory_manager_state.json")
        self.tags_index_file = os.path.join(self.memory_dir, "tags_index.json")
        self._ensure_dirs()
        self.state = self._load_state()
        self.tags_index = self._load_tags_index()
    
    def _ensure_dirs(self):
        Path(self.memory_dir).mkdir(parents=True, exist_ok=True)
    
    def _load_state(self) -> Dict:
        defaults = {
            "total_files_indexed": 0,
            "tags_created": 0,
            "last_consolidation": None,
            "files_by_tag": {}
        }
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    defaults.update(json.load(f))
        except Exception:
            pass
        return defaults
    
    def _load_tags_index(self) -> Dict:
        try:
            if os.path.exists(self.tags_index_file):
                with open(self.tags_index_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def _save(self):
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
            with open(self.tags_index_file, 'w') as f:
                json.dump(self.tags_index, f, indent=2)
        except Exception as e:
            self._log_error(f"Save failed: {e}")
    
    def _log_error(self, message: str):
        log_file = os.path.join(self.memory_dir, "logs", f"{datetime.now().strftime('%Y-%m-%d')}.log")
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        with open(log_file, 'a') as f:
            f.write(f"{datetime.now().isoformat()} | ERROR | {message}\n")
    
    def _extract_tags(self, content: str, file_path: str) -> Set[str]:
        """Auto-extract tags from content and path."""
        tags = set()
        
        # From filename
        filename = Path(file_path).stem.lower()
        if "strategy" in filename:
            tags.add("strategy")
        if "crypto" in filename or "token" in filename:
            tags.add("crypto")
        if "skill" in filename:
            tags.add("skill")
        if "trade" in filename:
            tags.add("trading")
        if "income" in filename:
            tags.add("income")
        if "cron" in filename:
            tags.add("automation")
        
        # From content
        content_lower = content.lower()
        keywords = {
            "solana": "crypto",
            "trading": "trading",
            "skill": "skill",
            "memory": "memory",
            "optimization": "performance",
            "todo": "task",
            "decision": "decision",
            "strategy": "strategy",
            "money": "finance",
            "revenue": "income",
            "pattern": "pattern",
            "error": "error",
            "fix": "maintenance",
            "alert": "alert"
        }
        
        for keyword, tag in keywords.items():
            if keyword in content_lower:
                tags.add(tag)
        
        return tags
    
    def index_file(self, file_path: str) -> List[str]:
        """Index a file and extract tags."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(10000)  # First 10KB
        except Exception:
            return []
        
        tags = self._extract_tags(content, file_path)
        
        for tag in tags:
            if tag not in self.tags_index:
                self.tags_index[tag] = []
            if file_path not in self.tags_index[tag]:
                self.tags_index[tag].append(file_path)
            
            if tag not in self.state["files_by_tag"]:
                self.state["files_by_tag"][tag] = []
            if file_path not in self.state["files_by_tag"][tag]:
                self.state["files_by_tag"][tag].append(file_path)
        
        self.state["total_files_indexed"] += 1
        self.state["tags_created"] = len(self.tags_index)
        self._save()
        
        return list(tags)
    
    def index_directory(self, root_dir: str, extensions: List[str] = None):
        """Index all files in directory."""
        extensions = extensions or [".md", ".json", ".py", ".txt"]
        indexed = 0
        
        for root, dirs, files in os.walk(root_dir):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    full_path = os.path.join(root, file)
                    self.index_file(full_path)
                    indexed += 1
        
        return indexed
    
    def search_by_tag(self, tag: str) -> List[str]:
        """Find files by tag."""
        return self.tags_index.get(tag, [])
    
    def get_related_files(self, file_path: str) -> List[str]:
        """Find files related by tags."""
        related = set()
        
        for tag, files in self.tags_index.items():
            if file_path in files:
                related.update(files)
        
        related.discard(file_path)
        return list(related)[:10]
    
    def suggest_memory_refresh(self) -> List[str]:
        """Suggest what to remember or consolidate."""
        suggestions = []
        
        # Old files
        cutoff = (datetime.now() - timedelta(days=30)).isoformat()
        old_count = 0
        for tag, files in self.state.get("files_by_tag", {}).items():
            for f in files:
                try:
                    mtime = datetime.fromtimestamp(os.path.getmtime(f)).isoformat()
                    if mtime < cutoff:
                        old_count += 1
                except:
                    pass
        
        if old_count > 20:
            suggestions.append(f"{old_count} files not accessed in 30 days - review old memories")
        
        # Large tag groups
        for tag, files in self.tags_index.items():
            if len(files) > 50:
                suggestions.append(f"Tag '{tag}' has {len(files)} files - may need subcategorization")
        
        if not suggestions:
            suggestions.append("Memory organization healthy")
        
        return suggestions
    
    def consolidate_tag(self, tag: str) -> str:
        """Consolidate large tag groups."""
        files = self.tags_index.get(tag, [])
        
        if len(files) < 20:
            return f"Tag '{tag}' has only {len(files)} files - no consolidation needed"
        
        # Create sub-tags based on modification time
        recent = []
        old = []
        
        cutoff = (datetime.now() - timedelta(days=90)).isoformat()
        
        for f in files:
            try:
                mtime = datetime.fromtimestamp(os.path.getmtime(f)).isoformat()
                if mtime > cutoff:
                    recent.append(f)
                else:
                    old.append(f)
            except:
                recent.append(f)
        
        # Update index
        self.tags_index[f"{tag}_recent"] = recent
        self.tags_index[f"{tag}_archived"] = old
        self.tags_index[tag] = recent[:10]  # Keep top 10 in main tag
        
        self.state["last_consolidation"] = datetime.now().isoformat()
        self._save()
        
        return f"Consolidated '{tag}': {len(recent)} recent, {len(old)} archived"
    
    def generate_report(self) -> str:
        """Generate memory management report."""
        lines = [
            "Memory Management Report",
            f"Files indexed: {self.state['total_files_indexed']}",
            f"Tags created: {self.state['tags_created']}",
            f"Last consolidation: {self.state.get('last_consolidation', 'Never')}",
            "",
            "Top tags:",
        ]
        
        top_tags = sorted(self.tags_index.items(), key=lambda x: -len(x[1]))[:10]
        for tag, files in top_tags:
            lines.append(f"  {tag}: {len(files)} files")
        
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Memory Manager - Auto-tag and organize memories")
    parser.add_argument("--mode", choices=["index", "search", "suggest", "consolidate", "report", "test"], default="report")
    parser.add_argument("--file", "-f", help="File to index")
    parser.add_argument("--tag", "-t", help="Tag to search/consolidate")
    parser.add_argument("--directory", "-d", help="Directory to index")
    
    args = parser.parse_args()
    
    mm = MemoryManager()
    
    if args.mode == "index":
        if args.file:
            tags = mm.index_file(args.file)
            print(f"✓ Indexed {args.file} with tags: {tags}")
        elif args.directory:
            count = mm.index_directory(args.directory)
            print(f"✓ Indexed {count} files")
        else:
            print("Error: --file or --directory required")
    
    elif args.mode == "search":
        if not args.tag:
            print("Error: --tag required")
            return
        files = mm.search_by_tag(args.tag)
        print(f"Tagged '{args.tag}': {len(files)} files")
        for f in files[:5]:
            print(f"  - {f}")
    
    elif args.mode == "suggest":
        suggestions = mm.suggest_memory_refresh()
        print("Suggestions:")
        for s in suggestions:
            print(f"  • {s}")
    
    elif args.mode == "consolidate":
        if not args.tag:
            print("Error: --tag required")
            return
        result = mm.consolidate_tag(args.tag)
        print(result)
    
    elif args.mode == "report":
        print(mm.generate_report())
    
    elif args.mode == "test":
        print("🧪 Running tests...")
        test_file = "/home/skux/.openclaw/workspace/test_memory.json"
        with open(test_file, 'w') as f:
            f.write('{"strategy": "test", "trading": true}')
        tags = mm.index_file(test_file)
        print(f"✓ Extracted tags: {tags}")
        related = mm.get_related_files(test_file)
        print(f"✓ Found {len(related)} related files")
        os.remove(test_file)
        print("✓ All tests passed")


if __name__ == "__main__":
    main()
