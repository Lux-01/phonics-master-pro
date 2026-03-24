#!/usr/bin/env python3
"""
Context Optimizer Auto-Trigger System
Automatically triggers context optimization based on session conditions
"""
import json
import os
from datetime import datetime

MEMORY_DIR = "/home/skux/.openclaw/workspace/memory"
CONTEXT_STATE_FILE = os.path.join(MEMORY_DIR, "context_state.json")

class ContextAutoTrigger:
    """Auto-trigger context optimization"""
    
    def __init__(self):
        self.state = self._load_state()
        self.triggers = {
            'message_threshold': 30,  # Trigger after 30 messages
            'file_reread_threshold': 2,  # Trigger after reading same file 2x
            'time_threshold': 30,  # Trigger after 30 minutes
            'stale_context_threshold': 15  # Trigger if no file read in 15 messages
        }
    
    def _load_state(self):
        """Load context state"""
        if os.path.exists(CONTEXT_STATE_FILE):
            try:
                with open(CONTEXT_STATE_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            'session_start': datetime.now().isoformat(),
            'message_count': 0,
            'files_read': [],
            'last_file_read': None,
            'checkpoints': [],
            'triggers_fired': []
        }
    
    def _save_state(self):
        """Save context state"""
        os.makedirs(MEMORY_DIR, exist_ok=True)
        with open(CONTEXT_STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def record_message(self):
        """Record a new message"""
        self.state['message_count'] += 1
        self._save_state()
        return self.check_triggers()
    
    def record_file_read(self, filepath, summary=""):
        """Record a file read"""
        # Check if file was already read
        existing = [f for f in self.state['files_read'] if f['path'] == filepath]
        
        file_record = {
            'path': filepath,
            'read_at': f"msg-{self.state['message_count']}",
            'summary': summary,
            'times_read': len(existing) + 1
        }
        
        if existing:
            existing[0]['times_read'] += 1
            existing[0]['read_at'] = f"msg-{self.state['message_count']}"
        else:
            self.state['files_read'].append(file_record)
        
        self.state['last_file_read'] = self.state['message_count']
        self._save_state()
        
        # Check if file was read multiple times
        if file_record['times_read'] >= self.triggers['file_reread_threshold']:
            return self._create_trigger('file_reread', {
                'file': filepath,
                'times': file_record['times_read'],
                'suggestion': f"You've read {filepath} {file_record['times_read']} times. Summary: {summary[:100]}..."
            })
        
        return None
    
    def check_triggers(self):
        """Check if any triggers should fire"""
        triggers_fired = []
        
        # Check message threshold
        if self.state['message_count'] % self.triggers['message_threshold'] == 0:
            triggers_fired.append(self._create_trigger('message_milestone', {
                'count': self.state['message_count'],
                'suggestion': f'Session checkpoint at {self.state["message_count"]} messages. Consider summarizing progress.'
            }))
        
        # Check stale context
        if self.state['last_file_read']:
            messages_since_file = self.state['message_count'] - self.state['last_file_read']
            if messages_since_file >= self.triggers['stale_context_threshold']:
                triggers_fired.append(self._create_trigger('stale_context', {
                    'messages_since_file': messages_since_file,
                    'suggestion': f'No file read in {messages_since_file} messages. Context may be stale.'
                }))
        
        return triggers_fired if triggers_fired else None
    
    def _create_trigger(self, trigger_type, data):
        """Create a trigger record"""
        trigger = {
            'type': trigger_type,
            'fired_at': datetime.now().isoformat(),
            'message_count': self.state['message_count'],
            'data': data
        }
        self.state['triggers_fired'].append(trigger)
        self._save_state()
        return trigger
    
    def create_checkpoint(self, summary, key_decisions=None):
        """Create a session checkpoint"""
        checkpoint = {
            'at': f"msg-{self.state['message_count']}",
            'timestamp': datetime.now().isoformat(),
            'summary': summary,
            'key_decisions': key_decisions or [],
            'files_active': [f['path'] for f in self.state['files_read'][-5:]]
        }
        self.state['checkpoints'].append(checkpoint)
        self._save_state()
        return checkpoint
    
    def get_session_summary(self):
        """Get current session summary"""
        return {
            'messages': self.state['message_count'],
            'files_read': len(self.state['files_read']),
            'checkpoints': len(self.state['checkpoints']),
            'session_duration': self._calculate_duration(),
            'recent_files': [f['path'] for f in self.state['files_read'][-5:]]
        }
    
    def _calculate_duration(self):
        """Calculate session duration"""
        try:
            start = datetime.fromisoformat(self.state['session_start'])
            return (datetime.now() - start).total_seconds() / 60  # minutes
        except:
            return 0
    
    def should_suggest_summary(self):
        """Check if we should suggest a summary"""
        return self.state['message_count'] >= self.triggers['message_threshold'] and \
               len(self.state['checkpoints']) == 0
    
    def reset_session(self):
        """Reset session state"""
        self.state = {
            'session_start': datetime.now().isoformat(),
            'message_count': 0,
            'files_read': [],
            'last_file_read': None,
            'checkpoints': [],
            'triggers_fired': []
        }
        self._save_state()

# Global instance
_auto_trigger = None

def get_auto_trigger():
    """Get singleton auto-trigger instance"""
    global _auto_trigger
    if _auto_trigger is None:
        _auto_trigger = ContextAutoTrigger()
    return _auto_trigger

# Convenience functions
record_message = lambda: get_auto_trigger().record_message()
record_file = lambda path, summary="": get_auto_trigger().record_file_read(path, summary)
checkpoint = lambda summary, decisions=None: get_auto_trigger().create_checkpoint(summary, decisions)
get_summary = lambda: get_auto_trigger().get_session_summary()
should_summarize = lambda: get_auto_trigger().should_suggest_summary()

if __name__ == "__main__":
    # Test auto-trigger
    print("=== Context Optimizer Auto-Trigger Test ===")
    trigger = ContextAutoTrigger()
    
    # Simulate messages
    for i in range(35):
        result = trigger.record_message()
        if result:
            print(f"\nTrigger fired at message {i+1}:")
            for t in (result if isinstance(result, list) else [result]):
                print(f"  - {t['type']}: {t['data'].get('suggestion', '')[:80]}...")
    
    # Simulate file reads
    print("\n=== Simulating file reads ===")
    trigger.record_file_read("/workspace/config.json", "API configuration with endpoints")
    trigger.record_file_read("/workspace/config.json", "API configuration with endpoints")
    trigger.record_file_read("/workspace/config.json", "API configuration with endpoints")
    
    print(f"\nSession summary: {trigger.get_session_summary()}")
    print("\nAuto-trigger system ACTIVE ✅")
