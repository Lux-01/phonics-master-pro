#!/usr/bin/env python3
"""
Workspace Organizer - Keep files tidy
"""
import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta

class WorkspaceOrganizer:
    def __init__(self, workspace="/home/skux/.openclaw/workspace"):
        self.workspace = Path(workspace)
        self.stats = {"moved": 0, "archived": 0, "cleaned": 0}
    
    def organize_by_type(self):
        """Move files into appropriate folders"""
        print("📁 Organizing files by type...")
        
        # Define mappings
        patterns = {
            "tools/": ["*_calculator*.py", "*_check*.py", "dashboard*.py"],
            "scripts/": ["run_*.sh", "check_*.sh", "start_*.sh"],
            "docs/": ["*.md", "*.txt"],
        }
        
        for folder, globs in patterns.items():
            target = self.workspace / folder
            target.mkdir(exist_ok=True)
            
            for pattern in globs:
                for file in self.workspace.glob(pattern):
                    if file.parent == self.workspace:
                        dest = target / file.name
                        if not dest.exists():
                            shutil.move(str(file), str(dest))
                            print(f"  → Moved {file.name} → {folder}")
                            self.stats["moved"] += 1
    
    def archive_old_logs(self, days=30):
        """Archive log files older than N days"""
        print("\n🗄️ Archiving old logs...")
        
        archive_dir = self.workspace / "archive" / "logs"
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        cutoff = datetime.now() - timedelta(days=days)
        
        for log_file in self.workspace.glob("*.log"):
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            if mtime < cutoff:
                dest = archive_dir / log_file.name
                shutil.move(str(log_file), str(dest))
                print(f"  → Archived {log_file.name}")
                self.stats["archived"] += 1
    
    def summary(self):
        print("\n" + "=" * 50)
        print("  ORGANIZATION COMPLETE")
        print("=" * 50)
        print(f"  Files moved: {self.stats['moved']}")
        print(f"  Files archived: {self.stats['archived']}")
        print(f"  Space cleaned: {self.stats['cleaned']} MB")
        print("=" * 50)

if __name__ == "__main__":
    organizer = WorkspaceOrganizer()
    organizer.organize_by_type()
    organizer.archive_old_logs(days=7)  # Archive logs older than a week
    organizer.summary()
