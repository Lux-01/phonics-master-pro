#!/usr/bin/env python3
"""
Remember This - Command system for persistent memory
Usage: "Remember this: [important info]" or "Store this: [info]"
"""
import re
from memory_enhancement_layer import get_mel, log_fragment, remember_key, remember_pref, remember_decision

class RememberThis:
    """
    Parse "remember this" commands and store information appropriately
    """
    
    @staticmethod
    def parse_command(text: str) -> dict:
        """
        Parse a "remember this" command
        
        Patterns:
        - "Remember this: My API key is XYZ"
        - "Store this: I prefer dark mode"
        - "Remember: Decision to use X"
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
    
    @staticmethod
    def categorize_and_store(content: str, original_text: str = ""):
        """
        Categorize the content and store it appropriately
        """
        content_lower = content.lower()
        
        # API Key pattern
        if any(x in content_lower for x in ['api key', 'apikey', 'api-key']) or re.search(r'[a-zA-Z0-9_]{20,}', content):
            # Try to extract service name and key
            service_match = re.search(r'(\w+)\s+(?:api\s+)?key', content_lower)
            service = service_match.group(1) if service_match else 'unknown'
            
            # Extract key (alphanumeric string of 20+ chars)
            key_match = re.search(r'([a-zA-Z0-9_-]{20,})', content)
            if key_match:
                remember_key(service, key_match.group(1), content)
                return f"✅ Stored API key for {service} in critical memory"
        
        # Preference pattern
        if any(x in content_lower for x in ['i prefer', 'my preference', 'i like', 'i want', 'default']):
            # Extract preference
            pref_match = re.search(r'(?:i prefer|my preference|i like|i want)\s+(.+)', content_lower)
            if pref_match:
                category = 'general'
                if any(x in content_lower for x in ['voice', 'speaker', 'tts']):
                    category = 'communication'
                elif any(x in content_lower for x in ['position', 'trade', 'size']):
                    category = 'trading'
                
                remember_pref(category, 'preference', content)
                return f"✅ Stored preference in category: {category}"
        
        # Decision pattern
        if any(x in content_lower for x in ['decided to', 'we decided', 'decision:', 'lets go with', 'choice:']):
            decision_match = re.search(r'(?:decided to|we decided|decision:|lets go with)\s+(.+)', content_lower)
            if decision_match:
                remember_decision(decision_match.group(1), original_text)
                return "✅ Stored decision in critical memory"
        
        # Contact/Email pattern
        if re.search(r'\S+@\S+\.\S+', content):
            email_match = re.search(r'(\S+@\S+\.\S+)', content)
            if email_match:
                remember_pref('contacts', email_match.group(1), content)
                return "✅ Stored contact in critical memory"
        
        # Generic - store as fragment
        log_fragment('remembered_item', [content])
        return "✅ Stored in conversation memory"
    
    @staticmethod
    def process_text(text: str) -> str:
        """
        Process text for remember commands
        Returns result message if command found, None otherwise
        """
        parsed = RememberThis.parse_command(text)
        if parsed:
            return RememberThis.categorize_and_store(parsed['content'], parsed['original'])
        return None

# Auto-trigger function - call on every user message
def check_and_remember(text: str) -> str:
    """
    Check if text contains a remember command and process it
    Call this on every user message
    """
    return RememberThis.process_text(text)

# Export convenience function
remember = check_and_remember

if __name__ == "__main__":
    # Test cases
    test_inputs = [
        "Remember this: My API key for Birdeye is 6335463fca7340f9a2c73eacd5a37f64",
        "I decided to use Python for all automation",
        "Remember: Contact john@example.com for consulting",
        "Store this: I prefer working at night"
    ]
    
    for text in test_inputs:
        result = check_and_remember(text)
        if result:
            print(f"Input: {text}")
            print(f"Result: {result}\n")
