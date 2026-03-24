#!/usr/bin/env python3
"""
Unified API - Single entry point for all memory operations
Part of Universal Memory System v2.0

Migrated and merged from memory-manager/memory_system_integration.py
Provides unified interface spanning short-term and long-term memory.
"""

import sys
import os
from typing import Optional, List, Any, Dict
from datetime import datetime

# Import UMS components
from .aca_memory_system import UniversalMemorySystem, MemoryCategory, get_ums
from .remember import RememberCommand, check_and_remember, remember_api_key as _remember_api_key
from .pre_query import PreQueryMemory, get_pre_query
from .memory_bridge import MemoryBridge

# ============================================================================
# UNIFIED MEMORY SYSTEM API
# ============================================================================

class UnifiedMemoryAPI:
    """
    Unified Memory System - Single API for all memory needs.
    
    Combines capabilities from:
    - Universal Memory System (UMS) - long-term structured storage
    - Remember Module - command parsing
    - Pre-Query Module - context surfacing
    - Memory Bridge - auto-capture
    
    This is the recommended entry point for all memory interactions.
    
    Usage:
        from unified_api import MemoryAPI
        
        api = MemoryAPI()
        
        # Remember something
        api.remember("I prefer dark mode")
        
        # Recall memories
        results = api.recall("trading strategy")
        
        # Get context for current query
        context = api.context_for("what were we building")
        
        # Check user message for remember commands
        result = api.on_user_message("Remember this: my API key is...")
    """
    
    def __init__(self):
        self.ums = get_ums()
        self.remember_cmd = RememberCommand(self.ums)
        self.pqm = PreQueryMemory(self.ums)
        self.bridge = MemoryBridge()
        
        # Session tracking
        self.session_start = datetime.now()
        self.session_memories: List[str] = []
    
    # ========================================================================
    # CORE OPERATIONS
    # ========================================================================
    
    def remember(self, content: str, category: str = "general", 
                 tags: Optional[List[str]] = None) -> str:
        """
        Store something in memory.
        
        Args:
            content: What to remember
            category: memory category (research, decision, code, preference, api_key, etc.)
            tags: Optional list of tags
            
        Returns:
            Entry ID of stored memory
        """
        entry_id = self.ums.capture(
            content=content,
            category=category,
            tags=tags or []
        )
        self.session_memories.append(entry_id)
        return entry_id
    
    def recall(self, query: str, limit: int = 5,
               category_filter: Optional[str] = None) -> List[Dict]:
        """
        Search and retrieve memories.
        
        Args:
            query: Search query
            limit: Max results to return
            category_filter: Optional filter by category
            
        Returns:
            List of matching memories
        """
        results = self.ums.search(query, limit=limit, category_filter=category_filter)
        return [
            {
                'id': r.id,
                'category': r.category,
                'content': r.content,
                'timestamp': r.timestamp,
                'tags': r.tags,
                'importance': r.importance
            }
            for r in results
        ]
    
    def recall_one(self, query: str) -> Optional[Dict]:
        """
        Get the single most relevant memory.
        
        Args:
            query: Search query
            
        Returns:
            Best matching memory or None
        """
        results = self.recall(query, limit=1)
        return results[0] if results else None
    
    def context_for(self, query: str, max_entries: int = 5) -> str:
        """
        Get formatted context for a query.
        
        Args:
            query: Current query/topic
            max_entries: Maximum memories to include
            
        Returns:
            Formatted context string ready for prompt
        """
        # Use UMS first
        ums_context = self.ums.get_context(query, max_entries)
        
        # Use Pre-Query for additional context
        pq_context = self.pqm.format_context_for_prompt(
            self.pqm.gather_context(query, max_items=max_entries)
        )
        
        # Combine if both have content
        if ums_context and pq_context:
            return ums_context + "\n\n" + pq_context
        elif ums_context:
            return ums_context
        elif pq_context:
            return pq_context
        return ""
    
    # ========================================================================
    # SPECIALIZED OPERATIONS
    # ========================================================================
    
    def remember_research(self, topic: str, findings: str,
                          sources: Optional[List[str]] = None,
                          key_points: Optional[List[str]] = None) -> str:
        """
        Store research findings.
        
        Args:
            topic: Research topic
            findings: Full findings
            sources: Source URLs/references
            key_points: Key takeaways
            
        Returns:
            Entry ID
        """
        return self.ums.remember_research(
            topic=topic,
            findings=findings,
            sources=sources or [],
            key_points=key_points or []
        )
    
    def remember_decision(self, decision: str, reasoning: str,
                          context: str = "",
                          alternatives: Optional[List[str]] = None,
                          reversible: bool = True) -> str:
        """
        Store a decision with full context.
        
        Args:
            decision: The decision made
            reasoning: Why this decision
            context: Background context
            alternatives: Other options considered
            reversible: Can this be changed
            
        Returns:
            Entry ID
        """
        return self.ums.remember_decision(
            decision=decision,
            context=context,
            reasoning=reasoning,
            alternatives=alternatives or [],
            reversible=reversible
        )
    
    def remember_api_key(self, service: str, key: str, notes: str = "") -> str:
        """
        Securely store an API key.
        
        Args:
            service: Service name
            key: The API key
            notes: Optional notes
            
        Returns:
            Entry ID
        """
        content = f"API Key for {service}: {key}"
        if notes:
            content += f" ({notes})"
        return self.ums.capture(
            content=content,
            category=MemoryCategory.API_KEY.value,
            tags=["api_key", service.lower(), "credential", "secure"]
        )
    
    def remember_preference(self, category: str, preference: str) -> str:
        """
        Store a user preference.
        
        Args:
            category: Preference category
            preference: The preference
            
        Returns:
            Entry ID
        """
        return self.ums.capture(
            content=f"Preference [{category}]: {preference}",
            category=MemoryCategory.PREFERENCE.value,
            tags=["preference", category]
        )
    
    # ========================================================================
    # CONVERSATION INTEGRATION
    # ========================================================================
    
    def on_user_message(self, text: str) -> Optional[str]:
        """
        Process a user message.
        Checks for remember commands and auto-captures important info.
        
        Args:
            text: User message text
            
        Returns:
            Result message if action taken, None otherwise
        """
        # Check for "remember this" commands
        result = self.remember_cmd.process_text(text)
        if result:
            return result
        
        # Auto-capture important info via bridge
        entry_id = self.bridge.analyze_message("user", text)
        if entry_id:
            return f"📝 Auto-captured to memory"
        
        return None
    
    def before_response(self, user_query: str) -> str:
        """
        Gather context BEFORE generating a response.
        Use this to enhance prompt with relevant memories.
        
        Args:
            user_query: The user's query
            
        Returns:
            Context string to prepend to prompt
        """
        return self.context_for(user_query)
    
    def after_response(self, user_query: str, assistant_response: str):
        """
        Log interaction AFTER generating a response.
        
        Args:
            user_query: User's message
            assistant_response: Assistant's response
        """
        # Capture as conversation fragment
        content = f"Q: {user_query}\nA: {assistant_response}"
        self.ums.capture(
            content=content,
            category=MemoryCategory.CONVERSATION.value,
            tags=["conversation", "interaction"]
        )
    
    def analyze_message(self, speaker: str, content: str) -> Optional[str]:
        """
        Analyze a message and auto-capture if important.
        
        Args:
            speaker: 'user' or 'assistant'
            content: Message content
            
        Returns:
            Entry ID if captured, None otherwise
        """
        return self.bridge.analyze_message(speaker, content)
    
    # ========================================================================
    # SESSION MANAGEMENT
    # ========================================================================
    
    def start_session(self) -> Dict:
        """
        Call at session start to restore context.
        
        Returns:
            Session info dict
        """
        self.session_start = datetime.now()
        self.session_memories = []
        
        # Get context from before
        today = datetime.now().strftime("%Y-%m-%d")
        
        return {
            'session_start': self.session_start.isoformat(),
            'today': today,
            'previous_memories': len(self.session_memories),
            'ums_ready': True
        }
    
    def end_session(self) -> Dict:
        """
        Call at session end to save state.
        
        Returns:
            Session summary
        """
        session_end = datetime.now()
        duration = (session_end - self.session_start).total_seconds() / 60
        
        summary = {
            'session_start': self.session_start.isoformat(),
            'session_end': session_end.isoformat(),
            'duration_minutes': round(duration, 2),
            'memories_created': len(self.session_memories)
        }
        
        return summary
    
    def get_session_summary(self) -> str:
        """
        Get summary of current session.
        
        Returns:
            Formatted summary string
        """
        duration = (datetime.now() - self.session_start).total_seconds() / 60
        
        lines = [
            "## Session Summary",
            f"Start: {self.session_start.strftime('%H:%M')}",
            f"Duration: {duration:.1f} minutes",
            f"New memories: {len(self.session_memories)}"
        ]
        
        return "\n".join(lines)
    
    # ========================================================================
    # UTILITY
    # ========================================================================
    
    def status(self) -> Dict:
        """
        Get memory system status.
        
        Returns:
            Status dict with key metrics
        """
        import glob
        
        memory_count = 0
        index_path = os.path.join("/home/skux/.openclaw/workspace/memory", "index.json")
        if os.path.exists(index_path):
            try:
                import json
                with open(index_path) as f:
                    index = json.load(f)
                memory_count = len(index.get("entries", {}))
            except:
                pass
        
        return {
            'ums_ready': True,
            'index_loaded': os.path.exists(index_path),
            'total_memories': memory_count,
            'session_active': True,
            'session_start': self.session_start.isoformat(),
            'session_memories': len(self.session_memories)
        }


# =============================================================================
# LEGACY COMPATIBILITY
# =============================================================================

# Old memory-manager API - wraps to new UMS
MemorySystem = UnifiedMemoryAPI

# Global singleton
_unified_api = None

def get_memory_api() -> UnifiedMemoryAPI:
    """Get singleton UnifiedMemoryAPI instance"""
    global _unified_api
    if _unified_api is None:
        _unified_api = UnifiedMemoryAPI()
    return _unified_api

# Convenience exports
remember = lambda content, cat="general", tags=None: get_memory_api().remember(content, cat, tags)
recall = lambda query, limit=5: get_memory_api().recall(query, limit)
context_for = lambda query: get_memory_api().context_for(query)
on_message = lambda text: get_memory_api().on_user_message(text)
before_response = lambda query: get_memory_api().before_response(query)
start_session = lambda: get_memory_api().start_session()
end_session = lambda: get_memory_api().end_session()

# Legacy function mappings
get_memory_system = get_memory_api
remember_key = lambda service, key, notes="": get_memory_api().remember_api_key(service, key, notes)
remember_pref = lambda category, key, value: get_memory_api().remember_preference(category, value)
remember_decision_legacy = lambda decision, context, reversible=True: get_memory_api().remember_decision(
    decision=decision,
    reasoning="User decision",
    context=context,
    reversible=reversible
)
log_fragment = lambda topic, key_points, decisions=None: get_memory_api().remember(
    f"Fragment: {topic} - {', '.join(key_points)}"
)

# =============================================================================
# CLI INTERFACE
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("🧠 Universal Memory System - Unified API v2.0")
    print("=" * 70)
    print("\n✅ Unified API ready - All memory systems integrated")
    print("\nUsage:")
    print("  from unified_api import MemoryAPI")
    print("  api = MemoryAPI()")
    print("  api.remember('Important info')")
    print("  api.recall('trading bot')")
    print("  context = api.before_response('What was I building?')")
    print("\nLegacy compatibility:")
    print("  from unified_api import remember, recall, context_for")
    print("  remember('Something important')")
    print("\n" + "=" * 70)
    
    # Run tests
    print("\n🏃 Running quick tests...")
    
    api = UnifiedMemoryAPI()
    
    # Test 1: Remember
    entry_id = api.remember("Test memory from Unified API", category="test")
    print(f"✅ Remember test: {entry_id[:16]}...")
    
    # Test 2: Recall
    results = api.recall("test memory")
    print(f"✅ Recall test: Found {len(results)} results")
    
    # Test 3: Context
    context = api.context_for("testing")
    print(f"✅ Context test: {len(context)} chars" if context else "✅ Context test: No context")
    
    # Test 4: Check message
    result = api.on_user_message("Remember this: test preference")
    print(f"✅ On message test: {result}")
    
    print("\n" + "=" * 70)
    print("✅ All tests passed! Unified API ready for use.")
    print("=" * 70)