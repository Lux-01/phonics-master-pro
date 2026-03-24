"""
Context verification engine.
Verifies current state against stored knowledge.
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Tuple, Any, Optional
from pathlib import Path

class ContextVerifier:
    """
    Verifies context and detects stale information.
    """
    
    # Context staleness thresholds (hours)
    DEFAULT_THRESHOLDS = {
        "api_docs": 24,
        "ui_changes": 168,  # 1 week
        "library_releases": 72,  # 3 days
        "market_data": 1,
        "news": 24,
        "general": 168
    }
    
    def __init__(self, stale_threshold: int = 24, cache_dir: Optional[Path] = None):
        self.stale_threshold = stale_threshold
        self.cache_dir = cache_dir or Path("/tmp/omnibot_context")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.logger = None  # Set when integrated
    
    def verify(self, context_type: str, data: Dict) -> Dict:
        """
        Verify context against stored knowledge.
        
        Args:
            context_type: Type of context
            data: Current context data
            
        Returns:
            Verification result
        """
        stored = self._get_stored_context(context_type)
        is_stale = self._is_context_stale(context_type)
        has_changed = self._has_data_changed(context_type, data)
        
        result = {
            "context_type": context_type,
            "verified_at": datetime.now().isoformat(),
            "is_stale": is_stale,
            "has_changed": has_changed,
            "last_updated": stored.get("timestamp") if stored else None,
            "warnings": []
        }
        
        # Generate warnings
        if is_stale:
            threshold = self._get_threshold(context_type)
            result["warnings"].append(
                f"Context may be stale (threshold: {threshold}h). "
                f"Consider refreshing."
            )
        
        if has_changed:
            result["warnings"].append(
                "Data has changed since last verification. "
                "Stored context may be outdated."
            )
        
        # Store new context
        self._store_context(context_type, data)
        
        return result
    
    def check_staleness(self, context_type: str) -> Tuple[bool, Any]:
        """
        Check if a context type is stale.
        
        Args:
            context_type: Type to check
            
        Returns:
            (is_stale, fresh_data or None)
        """
        is_stale = self._is_context_stale(context_type)
        
        if is_stale:
            fresh_data = self._fetch_fresh_data(context_type)
            if fresh_data:
                self._store_context(context_type, fresh_data)
            return True, fresh_data
        
        return False, None
    
    def _get_stored_context(self, context_type: str) -> Optional[Dict]:
        """Get stored context for a type."""
        cache_file = self.cache_dir / f"{context_type}.json"
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                return json.load(f)
        return None
    
    def _store_context(self, context_type: str, data: Any):
        """Store context with timestamp."""
        cache_file = self.cache_dir / f"{context_type}.json"
        stored = {
            "timestamp": datetime.now().isoformat(),
            "data": data,
            "hash": self._compute_hash(data)
        }
        with open(cache_file, 'w') as f:
            json.dump(stored, f)
    
    def _is_context_stale(self, context_type: str) -> bool:
        """Check if stored context is stale."""
        stored = self._get_stored_context(context_type)
        if not stored:
            return True  # No stored data = considered stale
        
        threshold = self._get_threshold(context_type)
        stored_time = datetime.fromisoformat(stored["timestamp"])
        age = datetime.now() - stored_time
        
        return age.total_seconds() > (threshold * 3600)
    
    def _has_data_changed(self, context_type: str, data: Dict) -> bool:
        """Check if data has changed from stored version."""
        stored = self._get_stored_context(context_type)
        if not stored:
            return False
        
        current_hash = self._compute_hash(data)
        return current_hash != stored.get("hash")
    
    def _get_threshold(self, context_type: str) -> int:
        """Get staleness threshold for context type."""
        for pattern, threshold in self.DEFAULT_THRESHOLDS.items():
            if pattern in context_type.lower():
                return threshold
        return self.stale_threshold
    
    def _compute_hash(self, data: Any) -> str:
        """Compute hash of data for change detection."""
        json_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.md5(json_str.encode()).hexdigest()
    
    def _fetch_fresh_data(self, context_type: str) -> Any:
        """
        Fetch fresh data for a context type.
        Override this to implement auto-refresh logic.
        """
        # This is a placeholder - would be customized for each context type
        # In a real implementation, this would:
        # - Fetch API docs for api contexts
        # - Check npm/pypi for library versions
        # - Scrape websites for UI changes
        # - etc.
        
        refresh_strategies = {
            "api_docs": self._fetch_api_docs,
            "ui_changes": self._fetch_ui_changes,
            "library_releases": self._fetch_library_info,
            "market_data": self._fetch_market_data
        }
        
        for pattern, strategy in refresh_strategies.items():
            if pattern in context_type.lower():
                try:
                    return strategy(context_type)
                except Exception as e:
                    if self.logger:
                        self.logger.warning(f"Failed to refresh {context_type}: {e}")
        
        return None
    
    def _fetch_api_docs(self, context_type: str) -> Dict:
        """Fetch latest API documentation."""
        # Would integrate with API discovery
        return {"_note": f"Auto-fetched {context_type} docs", "timestamp": datetime.now().isoformat()}
    
    def _fetch_ui_changes(self, context_type: str) -> Dict:
        """Check for UI changes."""
        return {"_note": "UI check placeholder", "timestamp": datetime.now().isoformat()}
    
    def _fetch_library_info(self, context_type: str) -> Dict:
        """Fetch latest library releases."""
        return {"_note": "Library info placeholder", "timestamp": datetime.now().isoformat()}
    
    def _fetch_market_data(self, context_type: str) -> Dict:
        """Fetch fresh market data."""
        return {"_note": "Market data placeholder", "timestamp": datetime.now().isoformat()}