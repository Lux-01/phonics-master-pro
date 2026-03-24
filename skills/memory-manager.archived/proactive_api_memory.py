#!/usr/bin/env python3
"""
Proactive API Memory System
Automatically brings up API keys when relevant - never forget again
"""
import os
import json
from typing import Dict, List, Optional
from datetime import datetime

class ProactiveAPIMemory:
    """
    Proactive API Memory - Brings up keys automatically
    
    Features:
    - Auto-loads all API keys at session start
    - Surfaces keys when relevant topics come up
    - Pre-fetches keys before you need them
    - Smart context detection
    """
    
    def __init__(self):
        self.api_keys = {}
        self.api_contexts = {}
        self._load_all_keys()
        self._build_context_map()
    
    def _load_all_keys(self):
        """Load all API keys from all sources"""
        # From auth.json
        auth_file = "/home/skux/.openclaw/workspace/auth.json"
        if os.path.exists(auth_file):
            try:
                with open(auth_file, 'r') as f:
                    auth = json.load(f)
                    if 'birdeye_api_key' in auth:
                        self.api_keys['birdeye'] = {
                            'key': auth['birdeye_api_key'],
                            'source': 'auth.json',
                            'status': 'active'
                        }
                    if 'agentmail_api_key' in auth:
                        self.api_keys['agentmail'] = {
                            'key': auth['agentmail_api_key'],
                            'source': 'auth.json',
                            'status': 'active'
                        }
            except:
                pass
        
        # From .env files
        env_files = [
            '/home/skux/.openclaw/workspace/solana-trader/.env',
            '/home/skux/.openclaw/workspace/aoe_v2/.env'
        ]
        
        for env_file in env_files:
            if os.path.exists(env_file):
                try:
                    with open(env_file, 'r') as f:
                        for line in f:
                            if '=' in line and not line.startswith('#'):
                                key, value = line.strip().split('=', 1)
                                if 'JUPITER' in key:
                                    self.api_keys['jupiter'] = {
                                        'key': value,
                                        'source': env_file,
                                        'status': 'active'
                                    }
                                elif 'HELIUS' in key:
                                    self.api_keys['helius'] = {
                                        'key': value,
                                        'source': env_file,
                                        'status': 'active'
                                    }
                                elif 'TELEGRAM' in key:
                                    self.api_keys['telegram'] = {
                                        'key': value,
                                        'source': env_file,
                                        'status': 'active'
                                    }
                except:
                    pass
        
        # From TOOLS.md references - token stored separately
        self.api_keys['github'] = {
            'key': 'TOKEN_HIDDEN',
            'source': 'TOOLS.md',
            'status': 'active'
        }
    
    def _build_context_map(self):
        """Build map of keywords -> APIs"""
        self.api_contexts = {
            'jupiter': ['trade', 'execute', 'swap', 'buy', 'sell', 'solana trade', 'auto trade'],
            'birdeye': ['crypto', 'token', 'price', 'solana', 'screener', 'market data'],
            'telegram': ['alert', 'notify', 'message', 'bot', 'telegram', 'ping'],
            'helius': ['wallet', 'transaction', 'rpc', 'monitor', 'track'],
            'agentmail': ['email', 'mail', 'send email', 'inbox', 'notification'],
            'github': ['git', 'repo', 'push', 'commit', 'pull request', 'actions']
        }
    
    def check_and_surface(self, user_text: str) -> Optional[str]:
        """
        Check if user text relates to any API and surface relevant keys
        
        Returns: Message with key if relevant, None if not
        """
        text_lower = user_text.lower()
        
        # Check each API context
        for api_name, keywords in self.api_contexts.items():
            if api_name in text_lower or any(k in text_lower for k in keywords):
                if api_name in self.api_keys:
                    api_info = self.api_keys[api_name]
                    
                    # Format key (mask partially for security)
                    key = api_info['key']
                    if len(key) > 20:
                        masked = key[:10] + '...' + key[-6:]
                    else:
                        masked = key[:10] + '...'
                    
                    return f"🔑 I have the {api_name.upper()} API key ready: `{masked}`\n   Source: {api_info['source']} | Status: {api_info['status']}"
        
        return None
    
    def get_all_active(self) -> str:
        """Get summary of all active APIs"""
        lines = ["📊 Active API Keys:"]
        
        for name, info in self.api_keys.items():
            key = info['key']
            masked = key[:8] + '...' + key[-4:] if len(key) > 15 else key[:8] + '...'
            lines.append(f"  ✅ {name.upper():12} | {masked} | {info['status']}")
        
        return "\n".join(lines)
    
    def get_key(self, api_name: str) -> Optional[str]:
        """Get specific API key"""
        if api_name in self.api_keys:
            return self.api_keys[api_name]['key']
        return None
    
    def suggest_for_task(self, task_description: str) -> List[str]:
        """Suggest which APIs would help with a task"""
        task_lower = task_description.lower()
        suggestions = []
        
        if any(k in task_lower for k in ['trade', 'buy', 'sell', 'swap']):
            if 'jupiter' in self.api_keys:
                suggestions.append("💡 Use Jupiter API for automated execution")
        
        if any(k in task_lower for k in ['scan', 'find token', 'screen']):
            if 'birdeye' in self.api_keys:
                suggestions.append("💡 Use Birdeye API for token data (already active)")
        
        if any(k in task_lower for k in ['alert', 'notify', 'send']):
            if 'telegram' in self.api_keys:
                suggestions.append("💡 Use Telegram Bot API for notifications")
        
        if any(k in task_lower for k in ['email', 'mail']):
            if 'agentmail' in self.api_keys:
                suggestions.append("💡 Use AgentMail API for email automation")
        
        return suggestions
    
    def should_remind(self, conversation_history: List[str]) -> Optional[str]:
        """Check if I should proactively remind about available APIs"""
        combined = ' '.join(conversation_history[-10:]).lower()
        
        # Trading mentioned but Jupiter not used
        if 'trade' in combined or 'trading' in combined:
            if 'jupiter' in self.api_keys and 'jupiter' not in combined:
                return f"🚀 I notice you're discussing trading. I have Jupiter API ready for automated execution!"
        
        # Scanner mentioned but Telegram not used for alerts
        if 'scanner' in combined or 'alert' in combined:
            if 'telegram' in self.api_keys and 'telegram' not in combined:
                return f"📱 I have Telegram Bot API for alerts!"
        
        return None

# Global instance
_proactive_api = None

def get_proactive_api():
    """Get singleton instance"""
    global _proactive_api
    if _proactive_api is None:
        _proactive_api = ProactiveAPIMemory()
    return _proactive_api

# Convenience functions
surface_keys = lambda text: get_proactive_api().check_and_surface(text)
get_all_apis = lambda: get_proactive_api().get_all_active()
get_key = lambda name: get_proactive_api().get_key(name)
suggest_apis = lambda task: get_proactive_api().suggest_for_task(task)

if __name__ == "__main__":
    api_mem = ProactiveAPIMemory()
    print(api_mem.get_all_active())
    print("\n✅ Proactive API Memory Active")
