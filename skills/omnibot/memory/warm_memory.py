"""
Warm Memory - Daily log files.
Persistent storage for session logs.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import json
import uuid
import re

class WarmMemory:
    """
    Daily log file storage.
    Persistent, searchable, time-bounded.
    """
    
    def __init__(self, memory_dir: Path):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
    
    def store(self, content: str, tags: Optional[List[str]] = None,
              ttl_hours: Optional[int] = None) -> str:
        """
        Store information in today's warm memory file.
        
        Args:
            content: Information to store
            tags: Optional tags
            ttl_hours: Optional TTL (defaults to 30 days)
            
        Returns:
            Memory ID
        """
        mem_id = f"warm_{uuid.uuid4().hex[:8]}"
        ttl_days = (ttl_hours or 720) // 24  # Default 30 days
        
        entry = {
            "id": mem_id,
            "content": content,
            "tags": tags or [],
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(days=ttl_days)).isoformat(),
            "tier": "warm"
        }
        
        # Write to today's file
        today_file = self._get_today_file()
        self._append_to_file(today_file, entry)
        
        return mem_id
    
    def search(self, query: str, max_results: int = 10,
               days_back: int = 7) -> List[Dict]:
        """
        Search warm memory files.
        
        Args:
            query: Search query
            max_results: Maximum results
            days_back: How many days back to search
            
        Returns:
            List of matching memories
        """
        results = []
        query_lower = query.lower()
        
        # Get relevant files
        files = self._get_files_for_range(days_back)
        
        for file_path in files:
            if not file_path.exists():
                continue
            
            try:
                entries = self._read_file(file_path)
                for entry in entries:
                    # Skip expired entries
                    if self._is_expired(entry):
                        continue
                    
                    score = 0
                    
                    # Content match
                    content = entry.get("content", "")
                    if query_lower in content.lower():
                        score += 10
                        # Bonus for exact matches
                        if query_lower == content.lower():
                            score += 5
                    
                    # Tag match
                    for tag in entry.get("tags", []):
                        if query_lower in tag.lower():
                            score += 5
                    
                    if score > 0:
                        entry["relevance"] = score
                        entry["source_file"] = file_path.name
                        results.append(entry)
            except Exception as e:
                # Log but continue
                print(f"Error reading {file_path}: {e}")
        
        # Sort by relevance
        results.sort(key=lambda x: x["relevance"], reverse=True)
        return results[:max_results]
    
    def get_by_id(self, mem_id: str) -> Optional[Dict]:
        """Find a specific memory by ID."""
        # Search across recent files
        for file_path in self._get_all_files():
            try:
                entries = self._read_file(file_path)
                for entry in entries:
                    if entry.get("id") == mem_id:
                        return entry
            except Exception:
                continue
        return None
    
    def get_recent(self, days: int = 7) -> List[Dict]:
        """Get recent memory entries."""
        entries = []
        for file_path in self._get_files_for_range(days):
            if file_path.exists():
                entries.extend([
                    e for e in self._read_file(file_path)
                    if not self._is_expired(e)
                ])
        
        # Sort by time
        entries.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return entries
    
    def cleanup_expired(self) -> int:
        """
        Remove expired entries from files.
        
        Returns:
            Number of entries removed
        """
        removed = 0
        for file_path in self._get_all_files():
            try:
                entries = self._read_file(file_path)
                original_count = len(entries)
                entries = [e for e in entries if not self._is_expired(e)]
                removed += original_count - len(entries)
                self._write_file(file_path, entries)
            except Exception:
                continue
        
        return removed
    
    def _get_today_file(self) -> Path:
        """Get today's memory file path."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        return self.memory_dir / f"{date_str}.jsonl"
    
    def _get_files_for_range(self, days: int) -> List[Path]:
        """Get memory files for a date range."""
        files = []
        for i in range(days):
            date_str = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            files.append(self.memory_dir / f"{date_str}.jsonl")
        return files
    
    def _get_all_files(self) -> List[Path]:
        """Get all memory files."""
        if self.memory_dir.exists():
            return sorted(self.memory_dir.glob("*.jsonl"), reverse=True)
        return []
    
    def _read_file(self, file_path: Path) -> List[Dict]:
        """Read a memory file."""
        entries = []
        if file_path.exists():
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            entries.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        return entries
    
    def _write_file(self, file_path: Path, entries: List[Dict]):
        """Write entries to memory file."""
        with open(file_path, 'w') as f:
            for entry in entries:
                f.write(json.dumps(entry) + "\n")
    
    def _append_to_file(self, file_path: Path, entry: Dict):
        """Append a single entry to file."""
        with open(file_path, 'a') as f:
            f.write(json.dumps(entry) + "\n")
    
    def _is_expired(self, entry: Dict) -> bool:
        """Check if an entry has expired."""
        expires_at = entry.get("expires_at")
        if not expires_at:
            return False
        try:
            return datetime.now() > datetime.fromisoformat(expires_at)
        except (ValueError, TypeError):
            return False
    
    def get_stats(self) -> Dict:
        """Get warm memory statistics."""
        files = self._get_all_files()
        total_entries = sum(
            len(self._read_file(f)) for f in files
        )
        
        return {
            "total_files": len(files),
            "total_entries": total_entries,
            "memory_dir": str(self.memory_dir),
            "tier": "warm (daily logs)"
        }