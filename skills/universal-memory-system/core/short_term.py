#!/usr/bin/env python3
"""
Universal Memory System - Core Short-Term Memory Module
Hot memory for current session context (in-memory, fast access)
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import deque


@dataclass
class ShortTermEntry:
    """A single short-term memory entry"""
    id: str
    content: str
    timestamp: datetime
    source: str
    importance: int = 5
    ttl_seconds: int = 3600  # Default 1 hour TTL
    
    def is_expired(self) -> bool:
        """Check if this entry has expired"""
        age = (datetime.now() - self.timestamp).total_seconds()
        return age > self.ttl_seconds


class ShortTermMemory:
    """
    Short-term memory (hot memory) - current session context.
    
    Features:
    - In-memory storage (fast access)
    - TTL-based expiration
    - Importance-based retention
    - Circular buffer for memory pressure
    
    Default capacity: 100 entries
    Default TTL: 1 hour (or session end)
    """
    
    def __init__(self, capacity: int = 100):
        self.capacity = capacity
        self._entries: deque = deque(maxlen=capacity)
        self._by_id: Dict[str, ShortTermEntry] = {}
    
    def add(self, content: str, source: str = "session",
            importance: int = 5, ttl_seconds: int = 3600) -> str:
        """
        Add an entry to short-term memory.
        
        Args:
            content: Content to store
            source: Source identifier
            importance: Importance (1-10, higher = keep longer)
            ttl_seconds: Time-to-live in seconds
            
        Returns:
            Entry ID
        """
        entry_id = f"stm_{datetime.now().timestamp()}"
        
        entry = ShortTermEntry(
            id=entry_id,
            content=content,
            timestamp=datetime.now(),
            source=source,
            importance=importance,
            ttl_seconds=ttl_seconds if importance < 9 else 86400
        )
        
        self._entries.append(entry)
        self._by_id[entry_id] = entry
        
        return entry_id
    
    def get(self, entry_id: str) -> Optional[ShortTermEntry]:
        """Get a specific entry by ID"""
        entry = self._by_id.get(entry_id)
        if entry and entry.is_expired():
            return None
        return entry
    
    def search(self, query: str, limit: int = 10) -> List[ShortTermEntry]:
        """
        Search short-term memory.
        
        Args:
            query: Search query
            limit: Max results
            
        Returns:
            List of matching entries
        """
        self._cleanup_expired()
        
        query_lower = query.lower()
        results = []
        
        for entry in self._entries:
            if query_lower in entry.content.lower():
                results.append(entry)
                if len(results) >= limit:
                    break
        
        return results
    
    def get_recent(self, n: int = 10, source: Optional[str] = None) -> List[ShortTermEntry]:
        """
        Get recent entries.
        
        Args:
            n: Number of entries
            source: Optional filter by source
            
        Returns:
            List of recent entries
        """
        self._cleanup_expired()
        
        entries = list(self._entries)
        if source:
            entries = [e for e in entries if e.source == source]
        
        return entries[-n:]
    
    def get_context_string(self, query: str, max_entries: int = 5) -> str:
        """Get formatted context for a query"""
        results = self.search(query, limit=max_entries)
        
        if not results:
            return ""
        
        lines = ["\n## Short-Term Memory"]
        for entry in results:
            time_str = entry.timestamp.strftime("%H:%M")
            lines.append(f"- [{time_str}] {entry.content[:100]}")
        
        return "\n".join(lines)
    
    def _cleanup_expired(self):
        """Remove expired entries"""
        # Remove expired from deque
        while self._entries and self._entries[0].is_expired():
            expired = self._entries.popleft()
            self._by_id.pop(expired.id, None)
    
    def clear(self):
        """Clear all short-term memory"""
        self._entries.clear()
        self._by_id.clear()
    
    def size(self) -> int:
        """Get current number of entries"""
        self._cleanup_expired()
        return len(self._entries)
    
    def summary(self) -> Dict[str, Any]:
        """Get memory summary"""
        self._cleanup_expired()
        
        return {
            'total_entries': len(self._entries),
            'max_capacity': self.capacity,
            'utilization_percent': (len(self._entries) / self.capacity) * 100,
            'oldest_entry': self._entries[0].timestamp.isoformat() if self._entries else None,
            'newest_entry': self._entries[-1].timestamp.isoformat() if self._entries else None
        }


# Global instance
_stm = None

def get_stm() -> ShortTermMemory:
    """Get singleton short-term memory instance"""
    global _stm
    if _stm is None:
        _stm = ShortTermMemory()
    return _stm


if __name__ == "__main__":
    stm = ShortTermMemory()
    
    # Test
    stm.add("This is a test memory", importance=8)
    stm.add("Another test", importance=5)
    
    print("Summary:", stm.summary())
    print("\nSearch 'test':", [e.content for e in stm.search("test")])
    print("\nContext string:", stm.get_context_string("memory"))