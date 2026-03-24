#!/usr/bin/env python3
"""
Universal Memory System - Core Long-Term Memory Module
Cold memory for persistent storage (disk-backed, durable)
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


MEMORY_DIR = Path("/home/skux/.openclaw/workspace/memory")
KNOWLEDGE_DIR = MEMORY_DIR / "knowledge"


@dataclass
class LongTermEntry:
    """Persistent long-term memory entry"""
    id: str
    content: str
    category: str
    timestamp: str
    source: str
    tags: List[str]
    importance: int
    access_count: int = 0
    last_accessed: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> "LongTermEntry":
        return cls(**{k: v for k, v in data.items() if k in [f.name for f in cls.__dataclass_fields__.values()]})


class LongTermMemory:
    """
    Long-term memory (cold memory) - persistent storage.
    
    Features:
    - Disk-backed persistence (JSONL files)
    - Categorization by memory type
    - Importance-based retention
    - Index for fast lookup
    """
    
    def __init__(self, memory_dir: Path = MEMORY_DIR):
        self.memory_dir = memory_dir
        self.knowledge_dir = memory_dir / "knowledge"
        self.raw_dir = memory_dir / "raw_capture"
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create directory structure"""
        dirs = [
            self.memory_dir,
            self.knowledge_dir,
            self.knowledge_dir / "research",
            self.knowledge_dir / "decisions",
            self.knowledge_dir / "projects",
            self.knowledge_dir / "people",
            self.raw_dir
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
    
    def _generate_id(self, content: str) -> str:
        """Generate unique ID"""
        ts = datetime.now().isoformat()
        return hashlib.sha256(f"{content}{ts}".encode()).hexdigest()[:16]
    
    def _get_filepath(self, category: str, date: str) -> Path:
        """Get appropriate file path for category"""
        category_map = {
            "research": self.knowledge_dir / "research",
            "decision": self.knowledge_dir / "decisions",
            "project": self.knowledge_dir / "projects",
            "preference": self.knowledge_dir / "people",
            "api_key": self.knowledge_dir / "people",
        }
        
        base_dir = category_map.get(category, self.raw_dir)
        return base_dir / f"{date}.jsonl"
    
    def store(self, content: str, category: str = "general",
              tags: List[str] = None, importance: int = 5,
              source: str = "unknown") -> str:
        """
        Store a memory entry.
        
        Args:
            content: Content to store
            category: Memory category
            tags: List of tags
            importance: Importance (1-10)
            source: Source identifier
            
        Returns:
            Entry ID
        """
        date_str = datetime.now().strftime("%Y-%m-%d")
        entry_id = self._generate_id(content)
        
        entry = LongTermEntry(
            id=entry_id,
            content=content,
            category=category,
            timestamp=datetime.now().isoformat(),
            source=source,
            tags=tags or [],
            importance=importance
        )
        
        filepath = self._get_filepath(category, date_str)
        
        # Append to file
        with open(filepath, 'a') as f:
            f.write(json.dumps(entry.to_dict()) + '\n')
        
        return entry_id
    
    def search(self, query: str, limit: int = 10, 
               category: Optional[str] = None) -> List[LongTermEntry]:
        """
        Search long-term memory.
        
        Args:
            query: Search query
            limit: Max results
            category: Optional category filter
            
        Returns:
            List of matching entries
        """
        query_lower = query.lower()
        results = []
        
        # Determine search directories
        if category:
            if category == "research":
                dirs = [self.knowledge_dir / "research"]
            elif category == "decision":
                dirs = [self.knowledge_dir / "decisions"]
            elif category in ["preference", "api_key"]:
                dirs = [self.knowledge_dir / "people"]
            else:
                dirs = [self.raw_dir]
        else:
            dirs = [
                self.knowledge_dir / "research",
                self.knowledge_dir / "decisions",
                self.knowledge_dir / "projects",
                self.knowledge_dir / "people",
                self.raw_dir
            ]
        
        # Search files
        for directory in dirs:
            if not directory.exists():
                continue
                
            for filepath in sorted(directory.glob("*.jsonl"), reverse=True):
                try:
                    with open(filepath) as f:
                        for line in f:
                            data = json.loads(line.strip())
                            if query_lower in data.get("content", "").lower():
                                results.append(LongTermEntry.from_dict(data))
                                if len(results) >= limit * 2:
                                    break
                except:
                    continue
                
                if len(results) >= limit * 2:
                    break
        
        # Sort by importance and recency
        results.sort(key=lambda e: (e.importance, e.timestamp), reverse=True)
        return results[:limit]
    
    def get_by_category(self, category: str, limit: int = 20) -> List[LongTermEntry]:
        """Get recent entries by category"""
        results = []
        
        filepath = self._get_filepath(category, datetime.now().strftime("%Y-%m-%d"))
        if not filepath.parent.exists():
            return results
        
        for jsonl_file in filepath.parent.glob("*.jsonl"):
            try:
                with open(jsonl_file) as f:
                    for line in f:
                        data = json.loads(line.strip())
                        if data.get("category") == category:
                            results.append(LongTermEntry.from_dict(data))
            except:
                continue
        
        return sorted(results, key=lambda e: e.timestamp, reverse=True)[:limit]


# Global instance
_ltm = None

def get_ltm() -> LongTermMemory:
    """Get singleton long-term memory instance"""
    global _ltm
    if _ltm is None:
        _ltm = LongTermMemory()
    return _ltm


if __name__ == "__main__":
    ltm = LongTermMemory()
    
    print("Store test entry...")
    entry_id = ltm.store("Test memory", category="test", tags=["test"])
    print(f"Stored: {entry_id}")
    
    print("\nSearch...")
    results = ltm.search("test")
    print(f"Found {len(results)} results")
    for r in results:
        print(f"  - {r.content}")