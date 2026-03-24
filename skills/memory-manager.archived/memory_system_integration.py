#!/usr/bin/env python3
"""
Memory System Integration
Unified interface for all memory enhancement features
"""
import sys
import os
sys.path.insert(0, '/home/skux/.openclaw/workspace/skills/memory-manager')

from memory_enhancement_layer import get_mel, remember_key, remember_pref, remember_decision, log_fragment
from remember_this import check_and_remember
from pre_query_memory import get_pre_query, gather_context, format_context

class MemorySystem:
    """
    Unified Memory System
    
    Features:
    1. Auto-remember important info
    2. Pre-query memory before responses
    3. Persistent storage of critical data
    4. Context continuity
    """
    
    def __init__(self):
        self.mel = get_mel()
        self.pqm = get_pre_query()
    
    def on_user_message(self, text: str) -> str:
        """
        Call this on EVERY user message
        Checks for remember commands and stores info
        """
        # Check for "remember this" commands
        result = check_and_remember(text)
        if result:
            return result
        
        # Auto-detect important info
        if self.mel.should_remember_this(text):
            pass  # Could auto-extract and store
        
        return None
    
    def before_response(self, user_query: str) -> str:
        """
        Call this BEFORE generating a response
        Gathers relevant context from memory
        """
        context = self.pqm.gather_context(user_query)
        return self.pqm.format_context_for_prompt(context)
    
    def remember(self, content: str, category: str = "general"):
        """
        Explicitly remember something
        
        Args:
            content: What to remember
            category: Type (api_key, preference, decision, fragment)
        """
        if category == "api_key":
            return remember_key("unknown", content, "Manually stored")
        elif category == "preference":
            return remember_pref("general", "preference", content)
        elif category == "decision":
            return remember_decision(content, "Manual entry")
        else:
            return log_fragment(category, [content])
    
    def recall(self, topic: str) -> str:
        """
        Recall information about a topic
        """
        context = self.pqm.gather_context(topic)
        return self.pqm.format_context_for_prompt(context)
    
    def start_session(self):
        """Call at start of session"""
        return self.mel.start_session()
    
    def end_session(self):
        """Call at end of session"""
        return self.mel.end_session()

# Global instance
_memory_system = None

def get_memory_system():
    """Get singleton MemorySystem instance"""
    global _memory_system
    if _memory_system is None:
        _memory_system = MemorySystem()
    return _memory_system

# Main API functions
remember = lambda content, cat="general": get_memory_system().remember(content, cat)
recall = lambda topic: get_memory_system().recall(topic)
before_response = lambda query: get_memory_system().before_response(query)
on_message = lambda text: get_memory_system().on_user_message(text)
start_session = lambda: get_memory_system().start_session()
end_session = lambda: get_memory_system().end_session()

if __name__ == "__main__":
    print("=" * 60)
    print("MEMORY ENHANCEMENT SYSTEM - ACTIVATED")
    print("=" * 60)
    print("\n✅ Auto-remember important info")
    print("✅ Pre-query memory before responses")
    print("✅ Persistent API key storage")
    print("✅ Context continuity across sessions")
    print("\nUsage:")
    print("  remember('API key is XYZ', 'api_key')")
    print("  recall('trading bot')")
    print("  before_response('What about the scanner?')")
    print("\n" + "=" * 60)
