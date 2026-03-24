"""
Omnibot Memory Manager

3-tier memory system for context preservation:
- Hot Memory (RAM): Current session, active tasks, last 10 messages
- Warm Memory (Daily Files): Raw daily logs, append-only
- Cold Memory (Curated): Long-term knowledge, critical info, manual updates
"""

import json
import re
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from collections import OrderedDict
import logging

logger = logging.getLogger("omnibot.memory")


@dataclass
class MemoryEntry:
    """Single memory entry structure."""
    key: str
    value: Any
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    tier: str = "hot"  # hot, warm, cold
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "key": self.key,
            "value": self.value,
            "timestamp": self.timestamp,
            "tier": self.tier,
            "tags": self.tags
        }


class MemoryManager:
    """
    3-tier memory management system.
    
    Tiers:
    - Hot (RAM): Fast access, session-scoped, auto-cleared
    - Warm (Daily Files): Append-only logs, time-scoped  
    - Cold (Curated): Long-term storage, manually managed
    
    Example:
        memory = MemoryManager()
        memory.store_hot("context", {"user": "Alice"})
        memory.store_warm("User logged in")
        memory.store_cold("api_key", "secret123")
        result = memory.recall("Alice")
    """
    
    def __init__(self, 
                 base_path: Optional[Path] = None,
                 hot_limit: int = 100,
                 warm_retention_days: int = 30):
        """
        Initialize memory manager.
        
        Args:
            base_path: Root directory for memory storage
            hot_limit: Max entries in hot memory
            warm_retention_days: Days to keep warm memory files
        """
        # Use package memory directory if not specified
        if base_path is None:
            # Determine memory directory relative to this file
            base_path = Path(__file__).parent.parent / "memory_store"
            
        self.base_path = Path(base_path)
        self.memory_dir = self.base_path
        self.hot_limit = hot_limit
        self.warm_retention_days = warm_retention_days
        
        # Create directories
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # Hot memory (in-RAM dictionary with LRU eviction)
        self._hot_memory: OrderedDict[str, MemoryEntry] = OrderedDict()
        
        # Daily warm memory file path
        self._warm_file = self._get_warm_file_path()
        
        # Cold memory file paths
        self._cold_md_file = self.memory_dir.parent / "MEMORY.md"
        self._cold_json_file = self.memory_dir / "critical_info.json"
        
        # Initialize cold storage files if missing
        self._init_cold_storage()
        
        logger.info(f"MemoryManager initialized at {self.memory_dir}")
    
    def _get_warm_file_path(self) -> Path:
        """Get today's warm memory file path."""
        today = date.today().isoformat()  # e.g., "2026-03-23"
        return self.memory_dir / f"{today}.md"
    
    def _init_cold_storage(self):
        """Initialize cold storage files if they don't exist."""
        # Critical info JSON
        if not self._cold_json_file.exists():
            self._cold_json_file.write_text(json.dumps({
                "api_keys": {},
                "decisions": [],
                "important_facts": {}
            }, indent=2))
        
        # MEMORY.md template
        if not self._cold_md_file.exists():
            self._cold_md_file.write_text(f"""# Omnibot Long-Term Memory

Curated knowledge and important information.

## Critical Information
- Last updated: {datetime.now().isoformat()}

## Key Facts

## Decisions

## Learnings

""")
    
    # ========== HOT MEMORY ==========
    
    def store_hot(self, key: str, value: Any, tags: Optional[List[str]] = None):
        """
        Store in hot memory (RAM, fastest access).
        
        Args:
            key: Storage key
            value: Any JSON-serializable value
            tags: Optional tags for categorization
        """
        # Evict oldest if at limit
        while len(self._hot_memory) >= self.hot_limit:
            self._hot_memory.popitem(last=False)
        
        entry = MemoryEntry(
            key=key,
            value=value,
            timestamp=datetime.now().isoformat(),
            tier="hot",
            tags=tags or []
        )
        
        # Move to end (most recently used)
        self._hot_memory[key] = entry
        self._hot_memory.move_to_end(key)
        
        logger.debug(f"Stored hot memory: {key}")
    
    def get_hot(self, key: str) -> Optional[Any]:
        """
        Retrieve from hot memory.
        
        Args:
            key: Storage key
            
        Returns:
            Value if found, None otherwise
        """
        if key in self._hot_memory:
            # Move to end (mark as recently used)
            self._hot_memory.move_to_end(key)
            return self._hot_memory[key].value
        return None
    
    def clear_hot(self, pattern: Optional[str] = None):
        """
        Clear hot memory entries.
        
        Args:
            pattern: Optional regex pattern to match keys
        """
        if pattern is None:
            self._hot_memory.clear()
        else:
            keys_to_remove = [
                k for k in self._hot_memory.keys() 
                if re.match(pattern, k)
            ]
            for k in keys_to_remove:
                del self._hot_memory[k]
        
        logger.info(f"Cleared hot memory (pattern: {pattern})")
    
    def get_hot_keys(self) -> List[str]:
        """List all hot memory keys."""
        return list(self._hot_memory.keys())
    
    # ========== WARM MEMORY ==========
    
    def store_warm(self, entry: Union[str, Dict, MemoryEntry], category: str = "general"):
        """
        Store in warm memory (daily file, append-only).
        
        Args:
            entry: Content to log (string, dict, or MemoryEntry)
            category: Entry category
        """
        timestamp = datetime.now().isoformat()
        
        if isinstance(entry, MemoryEntry):
            content = f"[{timestamp}] [{category}] [{entry.key}] {json.dumps(entry.value)}"
        elif isinstance(entry, dict):
            content = f"[{timestamp}] [{category}] {json.dumps(entry)}"
        else:
            content = f"[{timestamp}] [{category}] {entry}"
        
        # Append to today's file
        with open(self._warm_file, 'a') as f:
            f.write(content + "\n")
        
        logger.debug(f"Stored warm memory: {category}")
    
    def get_warm(self, date_str: Optional[str] = None, 
                 category: Optional[str] = None,
                 limit: int = 100) -> List[str]:
        """
        Retrieve from warm memory.
        
        Args:
            date_str: Date to read (default: today, format: YYYY-MM-DD)
            category: Filter by category
            limit: Max entries to return
            
        Returns:
            List of log entries
        """
        if date_str is None:
            date_str = date.today().isoformat()
        
        file_path = self.memory_dir / f"{date_str}.md"
        
        if not file_path.exists():
            return []
        
        entries = []
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if category and f"[{category}]" not in line:
                    continue
                entries.append(line)
                if len(entries) >= limit:
                    break
        
        return entries
    
    def search_warm(self, query: str, days: int = 7) -> List[Dict]:
        """
        Search warm memory across recent days.
        
        Args:
            query: Search term
            days: Days to search back
            
        Returns:
            Matching entries with metadata
        """
        results = []
        query_lower = query.lower()
        
        from datetime import timedelta
        for i in range(days):
            day = date.today() - timedelta(days=i)
            file_path = self.memory_dir / f"{day.isoformat()}.md"
            
            if not file_path.exists():
                continue
            
            with open(file_path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    if query_lower in line.lower():
                        results.append({
                            "date": day.isoformat(),
                            "line": line_num,
                            "content": line.strip()
                        })
        
        return results
    
    # ========== COLD MEMORY ==========
    
    def store_cold(self, key: str, value: Any, section: str = "important_facts"):
        """
        Store in cold memory (curated, long-term).
        
        Args:
            key: Storage key
            value: Value to store
            section: Section in cold storage (api_keys, decisions, important_facts)
        """
        if self._cold_json_file.exists():
            data = json.loads(self._cold_json_file.read_text())
        else:
            data = {"api_keys": {}, "decisions": [], "important_facts": {}}
        
        if section not in data:
            data[section] = {}
        
        if isinstance(data[section], dict):
            data[section][key] = {
                "value": value,
                "updated": datetime.now().isoformat()
            }
        elif isinstance(data[section], list):
            data[section].append({
                "key": key,
                "value": value,
                "timestamp": datetime.now().isoformat()
            })
        
        self._cold_json_file.write_text(json.dumps(data, indent=2))
        logger.info(f"Stored cold memory: {key} in {section}")
    
    def get_cold(self, key: str, section: str = "important_facts") -> Optional[Any]:
        """
        Retrieve from cold memory.
        
        Args:
            key: Storage key
            section: Section to search
            
        Returns:
            Value if found
        """
        if not self._cold_json_file.exists():
            return None
        
        data = json.loads(self._cold_json_file.read_text())
        
        if section in data and isinstance(data[section], dict):
            entry = data[section].get(key)
            if entry:
                return entry.get("value")
        
        return None
    
    def update_memory_md(self, content: str, section: str = "Key Facts"):
        """
        Update MEMORY.md with new content.
        
        Args:
            content: Content to add
            section: Section to append to
        """
        if not self._cold_md_file.exists():
            self._init_cold_storage()
        
        md_content = self._cold_md_file.read_text()
        
        # Find section and append
        section_pattern = f"## {section}"
        if section_pattern in md_content:
            lines = md_content.split('\n')
            section_idx = None
            for i, line in enumerate(lines):
                if line.strip() == section_pattern:
                    section_idx = i
                    break
            
            if section_idx is not None:
                timestamp = datetime.now().strftime("%Y-%m-%d")
                new_entry = f"- [{timestamp}] {content}"
                lines.insert(section_idx + 1, new_entry)
                self._cold_md_file.write_text('\n'.join(lines))
                logger.info(f"Updated MEMORY.md section: {section}")
        else:
            # Append new section
            timestamp = datetime.now().strftime("%Y-%m-%d")
            new_section = f"\n## {section}\n- [{timestamp}] {content}\n"
            self._cold_md_file.write_text(md_content + new_section)
            logger.info(f"Created MEMORY.md section: {section}")
    
    # ========== CROSS-TIER OPERATIONS ==========
    
    def recall(self, query: str, 
               search_hot: bool = True,
               search_warm: bool = True,
               search_cold: bool = True) -> Dict[str, Any]:
        """
        Semantic search across all memory tiers.
        
        Args:
            query: Search query
            search_hot: Include hot memory
            search_warm: Include warm memory
            search_cold: Include cold memory
            
        Returns:
            Results from each tier
        """
        results = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "hot": [],
            "warm": [],
            "cold": []
        }
        
        query_lower = query.lower()
        
        # Search hot memory
        if search_hot:
            for entry in self._hot_memory.values():
                if (query_lower in entry.key.lower() or 
                    query_lower in json.dumps(entry.value).lower()):
                    results["hot"].append(entry.to_dict())
        
        # Search warm memory
        if search_warm:
            results["warm"] = self.search_warm(query, days=7)
        
        # Search cold memory (JSON)
        if search_cold and self._cold_json_file.exists():
            data = json.loads(self._cold_json_file.read_text())
            for section, items in data.items():
                if isinstance(items, dict):
                    for k, v in items.items():
                        if query_lower in k.lower():
                            results["cold"].append({
                                "section": section,
                                "key": k,
                                "value": v
                            })
        
        return results
    
    def consolidate(self, date_str: Optional[str] = None):
        """
        Move warm memory to cold storage.
        Review daily entries and extract important facts.
        
        Args:
            date_str: Date to consolidate (default: yesterday)
        """
        from datetime import timedelta
        
        if date_str is None:
            date_str = (date.today() - timedelta(days=1)).isoformat()
        
        warm_entries = self.get_warm(date_str)
        
        if not warm_entries:
            logger.info(f"No warm memory to consolidate for {date_str}")
            return
        
        # Extract important entries (heuristic: entries with "critical", "important", "decision")
        important = []
        for entry in warm_entries:
            if any(kw in entry.lower() for kw in ["critical", "important", "decision", "milestone", "key"]):
                important.append(entry)
        
        if important:
            summary = f"Consolidated {len(important)} important entries from {date_str}"
            self.update_memory_md(summary, "Learnings")
            logger.info(f"Consolidated warm -> cold memory for {date_str}")
        
        return {
            "date": date_str,
            "total_entries": len(warm_entries),
            "important_found": len(important)
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory usage statistics."""
        return {
            "hot_entries": len(self._hot_memory),
            "hot_limit": self.hot_limit,
            "warm_files": len(list(self.memory_dir.glob("*.md"))),
            "cold_file_exists": self._cold_json_file.exists(),
            "base_path": str(self.base_path)
        }