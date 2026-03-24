#!/usr/bin/env python3
"""
Memory Bridge - Auto-Capture Module
Automatically captures memories from conversations and interactions.
Integrates with Universal Memory System.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, List

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from aca_memory_system import UniversalMemorySystem, MemoryCategory

class MemoryBridge:
    """
    Bridge between conversation flow and memory system.
    Auto-captures important information without explicit commands.
    """
    
    def __init__(self):
        self.ums = UniversalMemorySystem()
        self._important_keywords = [
            "remember", "important", "decided", "decision", "research",
            "found", "discovered", "api key", "token", "password",
            "preference", "usually", "always", "never", "build",
            "create", "project", "plan", "goal"
        ]
    
    def analyze_message(self, speaker: str, content: str) -> Optional[str]:
        """
        Analyze a message and decide if it should be remembered.
        Returns entry_id if captured, None if not important.
        """
        content_lower = content.lower()
        
        # Check for important keywords
        importance_score = 0
        for keyword in self._important_keywords:
            if keyword in content_lower:
                importance_score += 1
        
        # Length factor (substantial messages)
        if len(content) > 200:
            importance_score += 1
        
        # Decision keywords = automatic capture
        if any(k in content_lower for k in ["decided", "decision", "concluded"]):
            entry_id = self.ums.capture(
                content=content,
                source=f"conversation:{speaker}",
                category=MemoryCategory.DECISION.value,
                tags=["decision", "auto-captured"]
            )
            return entry_id
        
        # Research keywords = automatic capture
        if any(k in content_lower for k in ["research", "found", "discovered", "analysis"]):
            if len(content) > 100:  # Only substantial research
                entry_id = self.ums.capture(
                    content=content,
                    source=f"conversation:{speaker}",
                    category=MemoryCategory.RESEARCH.value,
                    tags=["research", "auto-captured"]
                )
                return entry_id
        
        # Build/code keywords = automatic capture
        if any(k in content_lower for k in ["build", "create", "develop", "implement"]):
            if len(content) > 100:
                entry_id = self.ums.capture(
                    content=content,
                    source=f"conversation:{speaker}",
                    category=MemoryCategory.CODE.value,
                    tags=["code", "build", "auto-captured"]
                )
                return entry_id
        
        # API keys / credentials = automatic capture (high importance)
        if any(k in content_lower for k in ["api key", "token", "credential", "secret"]):
            entry_id = self.ums.capture(
                content=content,
                source=f"conversation:{speaker}",
                category=MemoryCategory.API_KEY.value,
                tags=["api", "credential", "auto-captured"]
            )
            return entry_id
        
        # High importance score = capture
        if importance_score >= 2:
            entry_id = self.ums.capture(
                content=content,
                source=f"conversation:{speaker}",
                tags=["auto-captured"]
            )
            return entry_id
        
        return None
    
    def remember_research(self, topic: str, content: str,
                         sources: Optional[List[str]] = None) -> str:
        """Explicitly store research"""
        return self.ums.remember_research(
            topic=topic,
            findings=content,
            sources=sources or []
        )
    
    def remember_decision(self, decision: str, reasoning: str,
                         context: str = "") -> str:
        """Explicitly store decision"""
        return self.ums.remember_decision(
            decision=decision,
            context=context,
            reasoning=reasoning
        )
    
    def get_relevant_context(self, query: str, max_entries: int = 3) -> str:
        """Get context for current query"""
        return self.ums.get_context(query, max_entries=max_entries)
    
    def search(self, query: str, limit: int = 5) -> List:
        """Search memory"""
        return self.ums.search(query, limit=limit)


# Convenience functions for easy import
def remember(content: str, category: Optional[str] = None) -> str:
    """Quick remember function"""
    bridge = MemoryBridge()
    return bridge.ums.capture(content, category=category)

def recall(query: str, limit: int = 5) -> List:
    """Quick recall function"""
    bridge = MemoryBridge()
    return bridge.ums.search(query, limit=limit)

def context_for(query: str) -> str:
    """Get context for query"""
    bridge = MemoryBridge()
    return bridge.get_relevant_context(query)

def save_research(topic: str, findings: str, sources: Optional[List[str]] = None) -> str:
    """Save research findings"""
    bridge = MemoryBridge()
    return bridge.remember_research(topic, findings, sources)

def save_decision(decision: str, reasoning: str, context: str = "") -> str:
    """Save decision with reasoning"""
    bridge = MemoryBridge()
    return bridge.remember_decision(decision, reasoning, context)


if __name__ == "__main__":
    print("🧠 Memory Bridge - Testing auto-capture...")
    
    bridge = MemoryBridge()
    
    # Test messages
    test_messages = [
        ("user", "I decided to use Python for this project"),
        ("assistant", "Research shows that memory systems need multiple layers"),
        ("user", "Can you build a trading bot?"),
        ("user", "My API key is abc123"),
        ("user", "Just saying hi"),  # Should not capture
    ]
    
    for speaker, content in test_messages:
        entry_id = bridge.analyze_message(speaker, content)
        if entry_id:
            print(f"✅ Captured from {speaker}: {content[:50]}...")
        else:
            print(f"⏭️  Skipped: {content[:50]}...")
    
    print("\nTest complete!")
