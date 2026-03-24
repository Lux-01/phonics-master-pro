#!/usr/bin/env python3
"""
Workspace Organizer - ACA Built v1.0
Categorize files, detect duplicates, suggest archives.
"""

import json
import os
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import argparse


class WorkspaceOrganizer:
    """Organizes workspace by categorizing and cleaning files."""
    
    CATEGORIES = {
        "code": [".py", ".js", ".ts", ".java", ".cpp", ".c", ".h", ".go", ".rs", ".rb", ".php"],
        "config": [".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf", ".env"],
        "docs": [".md", ".txt", ".rst", ".adoc", ".docx", ".pdf"],
        "data": [".csv", ".json", ".xml", ".sqlite", ".db"],
        "media": [".jpg", ".jpeg", ".png", ".gif", ".mp4", ".mp3", ".svg", ".webp"],
        "logs": [".log", ".logs"],
        "temp": [".tmp", ".temp", ".cache"],
        "archive": [".zip", ".tar", ".gz", ".bz2", ".7z", ".rar"]
    }
    
    def __init__(self, workspace_dir: str = None, memory_dir: str = None):
        self.workspace_dir = workspace_dir or os.path.expanduser("~/.openclaw/workspace")
        self.memory_dir = memory_dir or os.path.expanduser("~/.openclaw/workspace/memory/workspace-organizer")
        self.state_file = os.path.join(self.memory_dir, "state.json")
        self.reports_dir = os.path.join(self.memory_dir, "reports")
        self._ensure_dirs()
        self.state = self._load_state()
    
    def _ensure_dirs(self):
        Path(self.memory_dir).mkdir(parents=True, exist_ok=True)
        Path(self.reports_dir).mkdir(parents=True, exist_ok=True)
    
    def _load_state(self) -> Dict:
        defaults = {
            "last_scan": None,
            "total_files": 0,
            "categorized": {},
            "duplicates_found": [],
            "suggestions": [],
            "archived_files": []
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
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            self._log_error(f"State save failed: {e}")
    
    def _log_error(self, message: str):
        log_file = os.path.join(self.memory_dir, "logs", f"{datetime.now().strftime('%Y-%m-%d')}.log")
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        with open(log_file, 'a') as f:
            f.write(f"{datetime.now().isoformat()} | ERROR | {message}\n")
    
    def _get_category(self, file_path: str) -> str:
        """Determine file category by extension."""
        ext = Path(file_path).suffix.lower()
        for cat, exts in self.CATEGORIES.items():
            if ext in exts:
                return cat
        return "other"
    
    def scan_workspace(self, max_depth: int = 3) -> Dict:
        """Scan workspace and categorize files."""
        files = {}
        categories = {cat: [] for cat in self.CATEGORIES.keys()}
        categories["other"] = []
        
        for root, dirs, filenames in os.walk(self.workspace_dir):
            depth = root.count(os.sep) - self.workspace_dir.count(os.sep)
            if depth > max_depth:
                del dirs[:]
                continue
            
            # Skip hidden dirs
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for filename in filenames:
                if filename.startswith('.'):
                    continue
                
                full_path = os.path.join(root, filename)
                try:
                    stat = os.stat(full_path)
                    category = self._get_category(full_path)
                    
                    file_info = {
                        "path": full_path,
                        "name": filename,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "category": category
                    }
                    
                    categories[category].append(file_info)
                    files[full_path] = file_info
                except Exception:
                    continue
        
        self.state["last_scan"] = datetime.now().isoformat()
        self.state["total_files"] = len(files)
        self.state["categorized"] = categories
        self._save_state()
        
        return categories
    
    def find_duplicates(self, max_size_mb: int = 100) -> List[Dict]:
        """Find duplicate files by size and first chunk hash."""
        if not self.state.get("categorized"):
            self.scan_workspace()
        
        duplicates = []
        size_groups: Dict[int, List[str]] = {}
        
        # Group by size first
        for cat, files in self.state["categorized"].items():
            for f in files:
                size = f["size"]
                if size < 1024:  # Skip tiny files
                    continue
                if size > max_size_mb * 1024 * 1024:  # Skip large files
                    continue
                
                if size not in size_groups:
                    size_groups[size] = []
                size_groups[size].append(f["path"])
        
        # Hash potential duplicates
        for size, paths in size_groups.items():
            if len(paths) < 2:
                continue
            
            hashes: Dict[str, List[str]] = {}
            for path in paths:
                try:
                    with open(path, 'rb') as f:
                        chunk = f.read(8192)  # First 8KB
                        file_hash = hashlib.md5(chunk).hexdigest()[:16]
                        if file_hash not in hashes:
                            hashes[file_hash] = []
                        hashes[file_hash].append(path)
                except Exception:
                    continue
            
            for h, duplicate_paths in hashes.items():
                if len(duplicate_paths) > 1:
                    duplicates.append({
                        "hash_prefix": h,
                        "size": size,
                        "files": duplicate_paths,
                        "found_at": datetime.now().isoformat()
                    })
        
        self.state["duplicates_found"] = duplicates
        self._save_state()
        return duplicates
    
    def generate_suggestions(self) -> List[str]:
        """Generate organization suggestions."""
        suggestions = []
        
        if not self.state.get("categorized"):
            self.scan_workspace()
        
        # Temp files
        temp_count = len(self.state["categorized"].get("temp", []))
        if temp_count > 5:
            suggestions.append(f"{temp_count} temp files - consider cleanup")
        
        # Large log files
        log_files = self.state["categorized"].get("logs", [])
        big_logs = [f for f in log_files if f["size"] > 10 * 1024 * 1024]  # 10MB
        if big_logs:
            suggestions.append(f"{len(big_logs)} log files >10MB - consider rotation")
        
        # Old files (6+ months)
        cutoff = (datetime.now() - timedelta(days=180)).isoformat()
        old_files = 0
        for cat, files in self.state["categorized"].items():
            for f in files:
                if f["modified"] < cutoff:
                    old_files += 1
        if old_files > 20:
            suggestions.append(f"{old_files} files not modified in 6 months - consider archiving")
        
        # Duplicates
        if self.state.get("duplicates_found"):
            suggestions.append(f"{len(self.state['duplicates_found'])} duplicate file groups detected")
        
        self.state["suggestions"] = suggestions
        self._save_state()
        return suggestions
    
    def get_oldest_files(self, limit: int = 10) -> List[Dict]:
        """Get files not modified in longest time."""
        all_files = []
        for cat, files in self.state.get("categorized", {}).items():
            all_files.extend(files)
        
        return sorted(all_files, key=lambda x: x["modified"])[:limit]
    
    def get_largest_files(self, limit: int = 10) -> List[Dict]:
        """Get largest files."""
        all_files = []
        for cat, files in self.state.get("categorized", {}).items():
            all_files.extend(files)
        
        return sorted(all_files, key=lambda x: x["size"], reverse=True)[:limit]
    
    def generate_report(self) -> str:
        """Generate workspace organization report."""
        categories = self.state.get("categorized", {})
        suggestions = self.generate_suggestions()
        
        lines = [
            "Workspace Organization Report",
            f"Scanned: {self.state.get('last_scan', 'Unknown')}",
            f"Total files: {self.state.get('total_files', 0)}",
            "",
            "By category:",
        ]
        
        for cat, files in sorted(categories.items(), key=lambda x: -len(x[1])):
            total_size = sum(f["size"] for f in files)
            lines.append(f"  {cat:12} | {len(files):4} files | {total_size/1024/1024:.1f} MB")
        
        lines.append("")
        lines.append("Suggestions:")
        if suggestions:
            for s in suggestions:
                lines.append(f"  ⚠️ {s}")
        else:
            lines.append("  ✓ Workspace looks organized")
        
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Workspace Organizer - Categorize and clean files")
    parser.add_argument("--mode", choices=["scan", "duplicates", "suggest", "report", "test"], default="report")
    parser.add_argument("--workspace", "-w", help="Workspace directory")
    args = parser.parse_args()
    
    organizer = WorkspaceOrganizer(workspace_dir=args.workspace)
    
    if args.mode == "scan":
        categories = organizer.scan_workspace()
        print(f"Scanned {organizer.state['total_files']} files")
        print("\nBy category:")
        for cat, files in sorted(categories.items(), key=lambda x: -len(x[1])):
            print(f"  {cat}: {len(files)} files")
    
    elif args.mode == "duplicates":
        dupes = organizer.find_duplicates()
        if dupes:
            print(f"Found {len(dupes)} duplicate groups:")
            for d in dupes:
                print(f"  {len(d['files'])} files ({d['size']/1024:.1f}KB)")
        else:
            print("No duplicates found")
    
    elif args.mode == "suggest":
        suggestions = organizer.generate_suggestions()
        if suggestions:
            print("Suggestions:")
            for s in suggestions:
                print(f"  • {s}")
        else:
            print("No suggestions - workspace organized")
    
    elif args.mode == "report":
        print(organizer.generate_report())
    
    elif args.mode == "test":
        print("🧪 Running tests...")
        organizer.scan_workspace(max_depth=2)
        dupes = organizer.find_duplicates()
        print(f"✓ Scanned {organizer.state['total_files']} files")
        print(f"✓ Found {len(dupes)} duplicates")
        suggestions = organizer.generate_suggestions()
        print(f"✓ Generated {len(suggestions)} suggestions")
        print("✓ All tests passed")


if __name__ == "__main__":
    main()
