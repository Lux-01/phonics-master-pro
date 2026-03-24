#!/usr/bin/env python3
"""
Memory Bridge
Integrates proactive API memory into every interaction
"""
import sys
sys.path.insert(0, '/home/skux/.openclaw/workspace/skills/memory-manager')

from auto_memory_system import auto_memory, process_message

def check_message_for_apis(text: str) -> str:
    """
    Check if message relates to APIs and return context
    
    This is the function to call on EVERY user message
    before processing the request.
    
    Returns: API context to prepend, or empty string
    """
    result = process_message(text)
    return result if result else ""

# Example usage
if __name__ == "__main__":
    print("=== Memory Bridge Test ===")
    
    # Simulate conversation
    messages = [
        "Hello",
        "I want to trade some tokens",
        "Setup alerts for me",
        "Send an email",
        "Check the scanner"
    ]
    
    for msg in messages:
        context = check_message_for_apis(msg)
        if context:
            print(f"\nUser: {msg}")
            print(f"System: {context}")
        
    print("\n✅ Memory Bridge Active")
