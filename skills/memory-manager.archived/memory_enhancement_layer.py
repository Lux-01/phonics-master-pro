#!/usr/bin/env python3
"""
Memory Enhancement Layer (MEL)
Solves the "I forget everything each session" problem
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

MEMORY_DIR = "/home/skux/.openclaw/workspace/memory"
CRITICAL_INFO_FILE = os.path.join(MEMORY_DIR, "critical_info.json")
CONTEXT_STATE_FILE = os.path.join(MEMORY_DIR, "context_state.json")
CONVERSATION_LOG = os.path.join(MEMORY_DIR, "conversation_fragments.json")

class MemoryEnhancementLayer:
    """
    Memory Enhancement Layer - Never forget the important stuff again
    
    Features:
    1. Auto-save critical info (API keys, decisions, preferences)
    2. Context continuity across sessions
    3. Pre-query memory before responses
    4. Conversation fragment logging
    5. Smart reminders
    """
    
    def __init__(self):
        self.critical_info = self._load_critical_info()
        self.context_state = self._load_context_state()
        self.session_start = datetime.now()
        
    def _load_critical_info(self) -> Dict:
        """Load critical information that must never be forgotten"""
        if os.path.exists(CRITICAL_INFO_FILE):
            try:
                with open(CRITICAL_INFO_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            'api_keys': {},
            'preferences': {},
            'decisions': [],
            'important_contacts': {},
            'active_projects': {},
            'credentials': {}
        }
    
    def _save_critical_info(self):
        """Save critical information"""
        os.makedirs(MEMORY_DIR, exist_ok=True)
        with open(CRITICAL_INFO_FILE, 'w') as f:
            json.dump(self.critical_info, f, indent=2)
    
    def _load_context_state(self) -> Dict:
        """Load context state for continuity"""
        if os.path.exists(CONTEXT_STATE_FILE):
            try:
                with open(CONTEXT_STATE_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            'last_session_end': None,
            'open_questions': [],
            'in_progress_tasks': [],
            'recent_topics': [],
            'message_count_this_topic': 0
        }
    
    def _save_context_state(self):
        """Save context state"""
        with open(CONTEXT_STATE_FILE, 'w') as f:
            json.dump(self.context_state, f, indent=2)
    
    # ========== CRITICAL INFO STORAGE ==========
    
    def remember_api_key(self, service: str, key: str, notes: str = ""):
        """Store an API key permanently"""
        self.critical_info['api_keys'][service] = {
            'key': key,
            'notes': notes,
            'added': datetime.now().isoformat()
        }
        self._save_critical_info()
        print(f"✅ API key for {service} stored in critical memory")
    
    def get_api_key(self, service: str) -> Optional[str]:
        """Retrieve an API key"""
        info = self.critical_info['api_keys'].get(service)
        return info['key'] if info else None
    
    def remember_preference(self, category: str, key: str, value: Any):
        """Store a user preference"""
        if category not in self.critical_info['preferences']:
            self.critical_info['preferences'][category] = {}
        self.critical_info['preferences'][category][key] = {
            'value': value,
            'set_at': datetime.now().isoformat()
        }
        self._save_critical_info()
    
    def get_preference(self, category: str, key: str) -> Any:
        """Get a stored preference"""
        pref = self.critical_info['preferences'].get(category, {}).get(key)
        return pref['value'] if pref else None
    
    def remember_decision(self, decision: str, context: str, reversible: bool = True):
        """Store an important decision with context"""
        self.critical_info['decisions'].append({
            'decision': decision,
            'context': context,
            'timestamp': datetime.now().isoformat(),
            'reversible': reversible
        })
        self._save_critical_info()
    
    def remember_credential(self, service: str, username: str, password: str, notes: str = ""):
        """Store login credentials"""
        self.critical_info['credentials'][service] = {
            'username': username,
            'password': password,
            'notes': notes,
            'added': datetime.now().isoformat()
        }
        self._save_critical_info()
    
    # ========== CONTEXT TRACKING ==========
    
    def start_session(self):
        """Call at the start of each session to restore context"""
        print(f"🧠 Memory Enhancement Layer Active")
        print(f"   Last session: {self.context_state.get('last_session_end', 'Unknown')}")
        print(f"   Open tasks: {len(self.context_state.get('in_progress_tasks', []))}")
        
        # Show reminders
        reminders = self._get_session_reminders()
        if reminders:
            print(f"\n📌 Reminders:")
            for r in reminders:
                print(f"   - {r}")
        
        return self.context_state
    
    def end_session(self):
        """Call at the end of each session to save state"""
        self.context_state['last_session_end'] = datetime.now().isoformat()
        self._save_context_state()
    
    def _get_session_reminders(self) -> List[str]:
        """Get reminders for this session"""
        reminders = []
        
        # Check for open tasks
        for task in self.context_state.get('in_progress_tasks', [])[-3:]:
            reminders.append(f"Task in progress: {task}")
        
        # Check for recent decisions
        recent_decisions = [d for d in self.critical_info.get('decisions', [])[-3:]]
        for d in recent_decisions:
            reminders.append(f"Decision: {d['decision'][:50]}...")
        
        return reminders
    
    # ========== CONVERSATION FRAGMENTS ==========
    
    def log_conversation_fragment(self, topic: str, key_points: List[str], 
                                   decisions: List[str] = None):
        """Log important conversation fragments"""
        fragment = {
            'topic': topic,
            'key_points': key_points,
            'decisions': decisions or [],
            'timestamp': datetime.now().isoformat()
        }
        
        fragments = []
        if os.path.exists(CONVERSATION_LOG):
            try:
                with open(CONVERSATION_LOG, 'r') as f:
                    fragments = json.load(f)
            except:
                pass
        
        fragments.append(fragment)
        
        # Keep only last 50 fragments
        fragments = fragments[-50:]
        
        with open(CONVERSATION_LOG, 'w') as f:
            json.dump(fragments, f, indent=2)
        
        # Update recent topics in context
        if topic not in self.context_state.get('recent_topics', []):
            self.context_state.setdefault('recent_topics', []).insert(0, topic)
            self.context_state['recent_topics'] = self.context_state['recent_topics'][:10]
            self._save_context_state()
    
    def get_recent_fragments(self, topic: str = None, n: int = 5) -> List[Dict]:
        """Get recent conversation fragments"""
        if not os.path.exists(CONVERSATION_LOG):
            return []
        
        try:
            with open(CONVERSATION_LOG, 'r') as f:
                fragments = json.load(f)
        except:
            return []
        
        if topic:
            fragments = [f for f in fragments if topic.lower() in f['topic'].lower()]
        
        return fragments[-n:]
    
    # ========== INTELLIGENT QUERY ==========
    
    def should_remember_this(self, text: str) -> bool:
        """Determine if this text contains something worth remembering"""
        critical_patterns = [
            'api key', 'apikey', 'password', 'credential', 'login',
            'token', 'secret', 'auth',
            'decided to', 'we decided', 'lets decide',
            'my preference', 'i prefer', 'always use',
            'important', 'remember this', 'don\'t forget',
            '@', 'email', 'phone'
        ]
        
        text_lower = text.lower()
        return any(pattern in text_lower for pattern in critical_patterns)
    
    def extract_and_remember(self, text: str):
        """Extract and remember important info from text"""
        # This is a simple version - could be enhanced with NLP
        if 'api key' in text.lower() or 'apikey' in text.lower():
            # Try to extract service and key
            # Format: "Service API key: xxx" or similar
            pass
        
        if 'decided to' in text.lower() or 'we decided' in text.lower():
            # Extract decision
            pass
    
    def get_memory_summary(self) -> str:
        """Get a summary of what's in memory"""
        lines = []
        lines.append("# Memory Summary")
        lines.append(f"\n## API Keys Stored: {len(self.critical_info.get('api_keys', {}))}")
        for service in self.critical_info.get('api_keys', {}).keys():
            lines.append(f"  - {service}")
        
        lines.append(f"\n## Preferences: {len(self.critical_info.get('preferences', {}))}")
        for cat in self.critical_info.get('preferences', {}).keys():
            lines.append(f"  - {cat}: {list(self.critical_info['preferences'][cat].keys())}")
        
        lines.append(f"\n## Decisions: {len(self.critical_info.get('decisions', []))}")
        for d in self.critical_info.get('decisions', [])[-3:]:
            lines.append(f"  - {d['decision'][:60]}...")
        
        lines.append(f"\n## In-Progress Tasks: {len(self.context_state.get('in_progress_tasks', []))}")
        for t in self.context_state.get('in_progress_tasks', [])[-3:]:
            lines.append(f"  - {t}")
        
        return "\n".join(lines)

# Global instance
_mel = None

def get_mel():
    """Get singleton MEL instance"""
    global _mel
    if _mel is None:
        _mel = MemoryEnhancementLayer()
    return _mel

# Convenience functions
remember_key = lambda s, k, n="": get_mel().remember_api_key(s, k, n)
get_key = lambda s: get_mel().get_api_key(s)
remember_pref = lambda c, k, v: get_mel().remember_preference(c, k, v)
get_pref = lambda c, k: get_mel().get_preference(c, k)
remember_decision = lambda d, c, r=True: get_mel().remember_decision(d, c, r)
log_fragment = lambda t, p, d=None: get_mel().log_conversation_fragment(t, p, d)
start_session = lambda: get_mel().start_session()
end_session = lambda: get_mel().end_session()
memory_summary = lambda: get_mel().get_memory_summary()

if __name__ == "__main__":
    mel = MemoryEnhancementLayer()
    print(mel.get_memory_summary())
    print("\n✅ Memory Enhancement Layer READY")
