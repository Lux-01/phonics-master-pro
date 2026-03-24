"""
Hot Memory - Current session context.
Fast, in-memory storage for active context.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import uuid
import threading

class HotMemory:
    """
    In-memory storage for session context.
    Fast access, volatile (lost on restart).
    """
    
    def __init__(self, max_items: int = 1000):
        self.storage = {}
        self.access_log = {}
        self.max_items = max_items
        self._lock = threading.Lock()
    
    def store(self, content: str, tags: Optional[List[str]] = None,
              ttl_hours: int = 24) -> str:
        """
        Store information in hot memory.
        
        Args:
            content: Information to store
            tags: Optional tags
            ttl_hours: Time to live in hours
            
        Returns:
            Memory ID
        """
        mem_id = f"hot_{uuid.uuid4().hex[:8]}"
        
        with self._lock:
            # Evict oldest if at capacity
            if len(self.storage) >= self.max_items:
                self._evict_oldest()
            
            self.storage[mem_id] = {
                "id": mem_id,
                "content": content,
                "tags": tags or [],
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(hours=ttl_hours)).isoformat(),
                "access_count": 0,
                "tier": "hot"
            }
            self.access_log[mem_id] = []
        
        return mem_id
    
    def get(self, mem_id: str) -> Optional[Dict]:
        """
        Retrieve single item by ID.
        
        Args:
            mem_id: Memory ID
            
        Returns:
            Memory item or None
        """
        with self._lock:
            item = self.storage.get(mem_id)
            if item:
                if self._is_expired(item):
                    del self.storage[mem_id]
                    return None
                
                item["access_count"] += 1
                self.access_log[mem_id].append(datetime.now().isoformat())
                return item.copy()
        
        return None
    
    def search(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search hot memory by content.
        
        Args:
            query: Search query
            max_results: Maximum results to return
            
        Returns:
            List of matching memories
        """
        results = []
        query_lower = query.lower()
        
        with self._lock:
            # Remove expired items first
            expired = [k for k, v in self.storage.items() if self._is_expired(v)]
            for k in expired:
                del self.storage[k]
                if k in self.access_log:
                    del self.access_log[k]
            
            for mem_id, item in self.storage.items():
                score = 0
                
                # Content match
                if query_lower in item["content"].lower():
                    score += 10
                
                # Tag match
                for tag in item["tags"]:
                    if query_lower in tag.lower():
                        score += 5
                
                if score > 0:
                    result = item.copy()
                    result["relevance"] = score
                    result["relevance_boost"] = "Access recency"
                    results.append(result)
                    
                    # Update access
                    item["access_count"] += 1
                    self.access_log[mem_id].append(datetime.now().isoformat())
        
        # Sort by relevance and recency
        results.sort(key=lambda x: (x["relevance"], x["created_at"]), reverse=True)
        return results[:max_results]
    
    def get_all(self) -> List[Dict]:
        """Get all hot memory items."""
        with self._lock:
            return [item.copy() for item in self.storage.values()]
    
    def clear(self):
        """Clear all hot memory."""
        with self._lock:
            self.storage.clear()
            self.access_log.clear()
    
    def cleanup_expired(self) -> int:
        """
        Remove expired items.
        
        Returns:
            Number of items removed
        """
        with self._lock:
            expired = [k for k, v in self.storage.items() if self._is_expired(v)]
            for k in expired:
                del self.storage[k]
                if k in self.access_log:
                    del self.access_log[k]
            return len(expired)
    
    def _is_expired(self, item: Dict) -> bool:
        """Check if an item has expired."""
        expires_at = datetime.fromisoformat(item["expires_at"])
        return datetime.now() > expires_at
    
    def _evict_oldest(self):
        """Remove oldest items when at capacity."""
        if not self.storage:
            return
        
        # Sort by last access time
        sorted_items = sorted(
            self.storage.items(),
            key=lambda x: x[1].get("access_count", 0)
        )
        
        # Remove bottom 10%
        to_remove = sorted_items[:max(1, len(sorted_items) // 10)]
        for mem_id, _ in to_remove:
            del self.storage[mem_id]
            if mem_id in self.access_log:
                del self.access_log[mem_id]
    
    def get_stats(self) -> Dict:
        """Get hot memory statistics."""
        with self._lock:
            return {
                "total_items": len(self.storage),
                "max_capacity": self.max_items,
                "utilization": f"{len(self.storage) / self.max_items * 100:.1f}%",
                "tier": "hot (in-memory)"
            }