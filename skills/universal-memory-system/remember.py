#!/usr/bin/env python3
"""
Remember Module - Command system for persistent memory
Part of Universal Memory System v2.0

Migrated from memory-manager/remember_this.py
Provides command parsing and automatic categorization.
"""

import re
from typing import Optional, Dict
from .aca_memory_system import UniversalMemorySystem, MemoryCategory

class RememberCommand:
    """
    Parse "remember this" commands and store information appropriately.
    
    Usage:
        "Remember this: My API key is XYZ"
        "Store this: I prefer dark mode"
        "Remember: Decision to use Python"
    """
    
    def __init__(self, ums: Optional[UniversalMemorySystem] = None):
        self.ums = ums or UniversalMemorySystem()
    
    def parse_command(self, text: str) -> Optional[Dict]:
        """
        Parse a "remember this" command.
        
        Patterns:
        - "Remember this: My API key is XYZ"
        - "Store this: I prefer dark mode"
        - "Remember: Decision to use X"
        - "Remember that ..."
        - "[remember] ..."
        
        Args:
            text: Input text to parse
            
        Returns:
            Dict with command info if found, None otherwise
        """
        text_lower = text.lower()
        
        # Check if this is a remember command
        if not any(x in text_lower for x in ['remember this', 'store this', 'remember:', 'store:']):
            return None
        
        # Extract the content
        patterns = [
            r'remember this:\s*(.+)', r'store this:\s*(.+)',
            r'remember:\s*(.+)', r'store:\s*(.+)',
            r'remember that\s+(.+)', r'\[remember\]\s*(.+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return {
                    'command': 'remember',
                    'content': match.group(1).strip(),
                    'original': text
                }
        
        return None
    
    def categorize_and_store(self, content: str, original_text: str = "") -> str:
        """
        Categorize the content and store it appropriately in UMS.
        
        Args:
            content: The content to store
            original_text: The original full text
            
        Returns:
            Status message
        """
        content_lower = content.lower()
        
        # API Key pattern
        if any(x in content_lower for x in ['api key', 'apikey', 'api-key', 'token']):
            service_match = re.search(r'(\w+)\s+(?:api\s+)?key', content_lower)
            service = service_match.group(1) if service_match else 'unknown'
            
            # Extract key (alphanumeric string of 20+ chars)
            key_match = re.search(r'([a-zA-Z0-9_-]{20,})', content)
            if key_match:
                entry_id = self.ums.capture(
                    content=f"API Key for {service}: {key_match.group(1)[:10]}...",
                    category=MemoryCategory.API_KEY.value,
                    tags=["api_key", service.lower(), "credential"]
                )
                return f"✅ Stored API key for {service} (secure storage)"
        
        # Preference pattern
        if any(x in content_lower for x in ['i prefer', 'my preference', 'i like', 'i want', 'default']):
            category = 'general'
            if any(x in content_lower for x in ['voice', 'speaker', 'tts']):
                category = 'communication'
            elif any(x in content_lower for x in ['position', 'trade', 'size']):
                category = 'trading'
            
            entry_id = self.ums.capture(
                content=content,
                category=MemoryCategory.PREFERENCE.value,
                tags=["preference", category]
            )
            return f"✅ Stored preference in category: {category}"
        
        # Decision pattern
        if any(x in content_lower for x in ['decided to', 'we decided', 'decision:', 'lets go with', 'choice:']):
            decision_match = re.search(r'(?:decided to|we decided|decision:|lets go with)\s+(.+)', content_lower)
            if decision_match:
                entry_id = self.ums.remember_decision(
                    decision=decision_match.group(1),
                    context=original_text,
                    reasoning="User stated decision",
                    reversible=True
                )
                return "✅ Stored decision in critical memory"
        
        # Contact/Email pattern
        if re.search(r'\S+@\S+\.\S+', content):
            email_match = re.search(r'(\S+@\S+\.\S+)', content)
            if email_match:
                entry_id = self.ums.capture(
                    content=f"Contact: {email_match.group(1)} - {content}",
                    category=MemoryCategory.PREFERENCE.value,
                    tags=["contact", "email"]
                )
                return "✅ Stored contact in critical memory"
        
        # Generic - store as normal memory
        entry_id = self.ums.capture(content, tags=["user_request"])
        return f"✅ Stored in conversation memory (ID: {entry_id[:8]}...)"
    
    def process_text(self, text: str) -> Optional[str]:
        """
        Process text for remember commands.
        
        Args:
            text: Input text from user
            
        Returns:
            Result message if command found, None otherwise
        """
        parsed = self.parse_command(text)
        if parsed:
            return self.categorize_and_store(parsed['content'], parsed['original'])
        return None


# Backward compatibility aliases
RememberThis = RememberCommand

# Auto-trigger function - call on every user message
def check_and_remember(text: str, ums: Optional[UniversalMemorySystem] = None) -> Optional[str]:
    """
    Check if text contains a remember command and process it.
    Call this on every user message.
    
    Args:
        text: User message text
        ums: Optional UMS instance
        
    Returns:
        Result message if command found, None otherwise
    """
    remember = RememberCommand(ums)
    return remember.process_text(text)

# Export convenience function
remember = check_and_remember


def remember_api_key(service: str, key: str, notes: str = "") -> str:
    """
    Store an API key in memory.
    
    Args:
        service: Service name
        key: The API key
        notes: Optional notes
        
    Returns:
        Status message
    """
    ums = UniversalMemorySystem()
    entry_id = ums.capture(
        content=f"API Key for {service}: {key}",
        category=MemoryCategory.API_KEY.value,
        tags=["api_key", service.lower(), "credential"]
    )
    return f"✅ API key for {service} stored (ID: {entry_id[:8]}...)"


def remember_preference(category: str, key: str, value: str) -> str:
    """
    Store a user preference.
    
    Args:
        category: Preference category
        key: Preference key
        value: Preference value
        
    Returns:
        Status message
    """
    ums = UniversalMemorySystem()
    entry_id = ums.capture(
        content=f"Preference [{category}]: {key} = {value}",
        category=MemoryCategory.PREFERENCE.value,
        tags=["preference", category, key]
    )
    return f"✅ Preference stored (ID: {entry_id[:8]}...)"


def remember_decision(decision: str, context: str = "") -> str:
    """
    Store a decision in memory.
    
    Args:
        decision: The decision made
        context: Context for the decision
        
    Returns:
        Status message
    """
    ums = UniversalMemorySystem()
    entry_id = ums.remember_decision(
        decision=decision,
        context=context,
        reasoning="User decision",
        reversible=True
    )
    return f"✅ Decision stored (ID: {entry_id[:8]}...)"


def log_fragment(topic: str, key_points: list, decisions: list = None) -> str:
    """
    Log a conversation fragment.
    
    Args:
        topic: Topic of the fragment
        key_points: Key points from the fragment
        decisions: Decisions made
        
    Returns:
        Status message
    """
    ums = UniversalMemorySystem()
    content = f"Topic: {topic}\nKey points: {', '.join(key_points)}"
    if decisions:
        content += f"\nDecisions: {', '.join(decisions)}"
    
    entry_id = ums.capture(
        content=content,
        category=MemoryCategory.CONVERSATION.value,
        tags=["fragment", topic.lower().replace(' ', '_')]
    )
    return f"✅ Fragment logged (ID: {entry_id[:8]}...)"


if __name__ == "__main__":
    print("="*60)
    print("📝 Remember Module - UMS v2.0")
    print("="*60)
    
    # Test cases
    test_inputs = [
        "Remember this: My API key for Birdeye is 6335463fca7340f9a2c73eacd5a37f64",
        "I decided to use Python for all automation",
        "Remember: Contact john@example.com for consulting",
        "Store this: I prefer working at night",
        "Just a regular message without remember command"
    ]
    
    remember = RememberCommand()
    
    for text in test_inputs:
        result = remember.process_text(text)
        print(f"\n📝 Input: {text}")
        if result:
            print(f"✅ Result: {result}")
        else:
            print("⏭️ No remember command detected")
    
    print("\n" + "="*60)
    print("✅ Remember module tests complete!")