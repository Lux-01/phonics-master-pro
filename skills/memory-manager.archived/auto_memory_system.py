#!/usr/bin/env python3
"""
Auto Memory System
Never forget API keys - bring them up proactively
"""
import sys
import os
sys.path.insert(0, '/home/skux/.openclaw/workspace/skills/memory-manager')

from proactive_api_memory import ProactiveAPIMemory, get_proactive_api
from datetime import datetime

class AutoMemorySystem:
    """
    Automatic Memory System
    
    This is the main interface that:
    - Loads at session start
    - Brings up API keys automatically
    - Never requires "do you have..." questions
    """
    
    def __init__(self):
        self.api_memory = get_proactive_api()
        self.session_start = datetime.now()
        self.conversation_count = 0
        self.keys_surfaced = set()
    
    def get_session_greeting(self):
        """Call at the beginning of every session"""
        greeting = []
        greeting.append("🧠 Auto Memory System Active")
        greeting.append("📝 Ready to recall API keys automatically")
        greeting.append("")
        greeting.append("Available APIs:")
        
        for name in self.api_memory.api_keys.keys():
            greeting.append(f"  ✅ {name.upper()}")
        
        greeting.append("")
        greeting.append("Just mention trading, alerts, email - and I'll bring up the key!")
        
        return "\n".join(greeting)
    
    def on_user_message(self, text: str) -> str:
        """
        Process every user message
        Returns: API key info if relevant, empty string if not
        """
        self.conversation_count += 1
        
        # Check if this message relates to any API
        result = self.api_memory.check_and_surface(text)
        
        if result:
            # Track that we surfaced this key so we don't spam
            api_name = result.split()[1].lower() if len(result.split()) > 1 else ""
            if api_name not in self.keys_surfaced:
                self.keys_surfaced.add(api_name)
                return f"\n{result}\n"
        
        # Check if we should proactively suggest
        if self.conversation_count % 20 == 0:  # Every 20 messages
            reminder = self.api_memory.should_remind([text])
            if reminder:
                return f"\n{reminder}\n"
        
        return ""
    
    def get_key(self, api_name: str) -> str:
        """Get specific key when explicitly asked"""
        key = self.api_memory.get_key(api_name)
        if key:
            # Mask for display
            if len(key) > 20:
                return f"{key[:10]}...{key[-6:]}"
        return "Key not found"
    
    def get_all_keys(self) -> str:
        """Get all keys formatted"""
        return self.api_memory.get_all_active()
    
    def suggest_for_current_task(self, task: str = "") -> str:
        """Suggest which APIs to use"""
        if not task:
            return "\n💡 Available APIs:\n" + self.get_all_keys()
        
        suggestions = self.api_memory.suggest_for_task(task)
        if suggestions:
            return "\n".join([""] + suggestions + [""])
        return ""

# Initialize on import
auto_memory = AutoMemorySystem()

# Session starter - call this at beginning of each session
def session_start_message():
    return auto_memory.get_session_greeting()

# Message processor - call this on every user message
def process_message(text: str):
    return auto_memory.on_user_message(text)

# Get specific key
def recall_key(api_name: str):
    return auto_memory.get_key(api_name)

# Get all keys
def recall_all():
    return auto_memory.get_all_keys()

# Suggest APIs for task
def suggest(task: str = ""):
    return auto_memory.suggest_for_current_task(task)

if __name__ == "__main__":
    print(session_start_message())
    print("\n" + "=" * 60)
    print("\nDemo: Message about trading...")
    result = process_message("I want to execute some trades")
    if result:
        print(result)
    
    print("\nDemo: Message about alerts...")
    result = process_message("Setup some alerts")
    if result:
        print(result)
    
    print("\n" + "=" * 60)
    print("\n✅ Auto Memory System Ready")
