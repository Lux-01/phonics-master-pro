#!/usr/bin/env python3
"""
Pre-Query Memory System - Context surfacing module
Part of Universal Memory System v2.0

Migrated from memory-manager/pre_query_memory.py
Provides automatic context gathering before responses.
"""

import os
import json
import re
from typing import List, Dict, Optional
from .aca_memory_system import UniversalMemorySystem

MEMORY_DIR = "/home/skux/.openclaw/workspace/memory"
TOOLS_FILE = "/home/skux/.openclaw/workspace/TOOLS.md"
MEMORY_FILE = "/home/skux/.openclaw/workspace/MEMORY.md"


class PreQueryMemory:
    """
    Pre-query memory system - check relevant memory before responding.
    
    Usage:
        pqm = PreQueryMemory()
        context = pqm.gather_context("What about the trading bot?")
        # Returns relevant info from memory before generating response
    """
    
    def __init__(self, ums: Optional[UniversalMemorySystem] = None):
        self.ums = ums
        self.cache = {}
        self.last_query = None
    
    def gather_context(self, user_query: str, max_items: int = 5) -> Dict:
        """
        Gather relevant context from memory before responding.
        
        Args:
            user_query: The user's message
            max_items: Max number of context items to return
        
        Returns:
            Dict with relevant context from various sources
        """
        context = {
            'relevant_from_memory': [],
            'recent_decisions': [],
            'api_keys': [],
            'open_tasks': [],
            'suggestions': [],
            'ums_results': []
        }
        
        query_lower = user_query.lower()
        
        # Query UMS for semantic search
        if self.ums:
            try:
                context['ums_results'] = self.ums.search(user_query, limit=max_items)
            except Exception as e:
                pass
        
        # Check TOOLS.md for relevant API keys / credentials
        context['api_keys'] = self._check_tools_for_keywords(query_lower)
        
        # Check MEMORY.md for relevant projects / decisions
        context['relevant_from_memory'] = self._check_memory_for_keywords(query_lower, max_items)
        
        # Check for recent decisions
        context['recent_decisions'] = self._check_recent_decisions(query_lower)
        
        # Check for open tasks
        context['open_tasks'] = self._check_open_tasks()
        
        # Generate suggestions
        context['suggestions'] = self._generate_suggestions(query_lower, context)
        
        return context
    
    def _check_tools_for_keywords(self, query: str) -> List[Dict]:
        """Check TOOLS.md for relevant API keys or credentials"""
        results = []
        
        if not os.path.exists(TOOLS_FILE):
            return results
        
        try:
            with open(TOOLS_FILE, 'r') as f:
                content = f.read()
            
            # Keywords that might trigger API key lookup
            api_keywords = {
                'email': ['agentmail', 'email', 'mail'],
                'search': ['brave', 'search', 'google'],
                'crypto': ['birdeye', 'solana', 'dexscreener', 'helius', 'token'],
                'trading': ['birdeye', 'jupiter', 'helius'],
                'github': ['github', 'git', 'repo'],
                'moltbook': ['moltbook', 'social', 'content'],
                'telegram': ['telegram', 'bot', 'messaging'],
            }
            
            for category, keywords in api_keywords.items():
                if any(k in query for k in keywords):
                    if category == 'email' and 'agentmail' in content.lower():
                        results.append({
                            'type': 'api_key',
                            'service': 'AgentMail.to',
                            'available': True,
                            'note': 'Check TOOLS.md for full details'
                        })
                    elif category == 'crypto' and 'birdeye' in content.lower():
                        results.append({
                            'type': 'api_key',
                            'service': 'Birdeye',
                            'available': True,
                            'note': 'API key stored in TOOLS.md'
                        })
        except:
            pass
        
        return results
    
    def _check_memory_for_keywords(self, query: str, max_items: int) -> List[Dict]:
        """Check memory files for relevant information"""
        results = []
        
        topic_keywords = {
            'trading': ['trading', 'trade', 'scanner', 'solana', 'token', 'buy', 'sell'],
            'gold coast': ['gold coast', 'property', 'dream', 'master plan'],
            'moltbook': ['moltbook', 'social', 'post', 'content'],
            'phonics': ['phonics', 'app', 'flutter', 'apk'],
            'skills': ['skill', 'evolution', 'aloe', 'cel'],
            'github': ['github', 'repo', 'git', 'code'],
            'memory': ['memory', 'remember', 'ums', 'store'],
        }
        
        matched_topic = None
        for topic, keywords in topic_keywords.items():
            if any(k in query for k in keywords):
                matched_topic = topic
                break
        
        if not matched_topic:
            return results
        
        # Check MEMORY.md
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, 'r') as f:
                    lines = f.readlines()
                
                current_section = []
                section_title = ""
                
                for line in lines:
                    if line.startswith('#'):
                        if current_section and any(k in ' '.join(current_section).lower() for k in topic_keywords.get(matched_topic, [])):
                            results.append({
                                'source': 'MEMORY.md',
                                'topic': section_title.strip(),
                                'preview': ' '.join(current_section[:3]).strip()[:100]
                            })
                        current_section = []
                        section_title = line
                    else:
                        current_section.append(line)
                    
                    if len(results) >= max_items:
                        break
            except:
                pass
        
        # Check recent daily memory files
        try:
            memory_files = sorted([f for f in os.listdir(MEMORY_DIR) if f.endswith('.md') and f.startswith('2026')])
            for filename in memory_files[-5:]:
                filepath = os.path.join(MEMORY_DIR, filename)
                with open(filepath, 'r') as f:
                    content = f.read()
                
                if any(k in content.lower() for k in topic_keywords.get(matched_topic, [])):
                    results.append({
                        'source': filename,
                        'topic': matched_topic,
                        'preview': 'Mentioned in recent daily log'
                    })
                    break
        except:
            pass
        
        return results
    
    def _check_recent_decisions(self, query: str) -> List[str]:
        """Check for recent decisions related to query"""
        decisions = []
        
        decision_keywords = {
            'aca': 'Use ACA methodology for all code builds',
            'flutter': 'Use cloud CI (Codemagic/GitHub Actions) for APK builds',
            'trading': 'Grade A+ only for live trading',
            'gold coast': '48-month roadmap to waterfront property',
            'memory': 'Use Universal Memory System for all memory needs',
            'testing': 'Auto-test all skills before deployment'
        }
        
        for keyword, decision in decision_keywords.items():
            if keyword in query:
                decisions.append(decision)
        
        return decisions
    
    def _check_open_tasks(self) -> List[str]:
        """Check for open tasks from context state"""
        tasks = []
        context_state_file = os.path.join(MEMORY_DIR, "context_state.json")
        
        if os.path.exists(context_state_file):
            try:
                with open(context_state_file, 'r') as f:
                    state = json.load(f)
                    tasks = state.get('in_progress_tasks', [])[-3:]
            except:
                pass
        
        return tasks
    
    def _generate_suggestions(self, query: str, context: Dict) -> List[str]:
        """Generate helpful suggestions based on context"""
        suggestions = []
        
        if any(k in query for k in ['api', 'key', 'token', 'credential']):
            if not context['api_keys']:
                suggestions.append("Check TOOLS.md for API keys")
        
        if any(k in query for k in ['project', 'work', 'task', 'doing']):
            if not context['relevant_from_memory']:
                suggestions.append("Should check MEMORY.md for active projects")
        
        if any(k in query for k in ['remember', 'before', 'last time', 'previously']):
            suggestions.append("Check memory/YYYY-MM-DD.md files for recent conversations")
        
        # If UMS has results, suggest using them
        if context.get('ums_results'):
            suggestions.append(f"Found {len(context['ums_results'])} relevant items in UMS")
        
        return suggestions
    
    def format_context_for_prompt(self, context: Dict) -> str:
        """Format gathered context as a string to prepend to prompts"""
        sections = []
        
        # Add UMS results first if available
        if context.get('ums_results'):
            sections.append("## 📚 From Memory System")
            for entry in context['ums_results'][:3]:
                sections.append(f"- [{entry.category}] {entry.content[:80]}...")
        
        if context['relevant_from_memory']:
            sections.append("## Relevant History")
            for item in context['relevant_from_memory'][:3]:
                sections.append(f"- {item['topic']}: {item['preview']}")
        
        if context['recent_decisions']:
            sections.append("## Recent Decisions")
            for d in context['recent_decisions']:
                sections.append(f"- {d}")
        
        if context['api_keys']:
            sections.append("## Available API Keys")
            for key in context['api_keys']:
                sections.append(f"- {key['service']}: {key['note']}")
        
        if context['open_tasks']:
            sections.append("## In Progress")
            for task in context['open_tasks']:
                sections.append(f"- {task}")
        
        if context['suggestions']:
            sections.append("## Notes")
            for s in context['suggestions']:
                sections.append(f"- {s}")
        
        return "\n".join(sections) if sections else ""


# Global instance
_pqm = None

def get_pre_query(ums: Optional[UniversalMemorySystem] = None):
    """Get singleton PreQueryMemory instance"""
    global _pqm
    if _pqm is None:
        _pqm = PreQueryMemory(ums)
    return _pqm

# Convenience functions
gather_context = lambda query, ums=None: get_pre_query(ums).gather_context(query)
format_context = lambda ctx: get_pre_query().format_context_for_prompt(ctx)
context_for = lambda query, ums=None: get_pre_query(ums).format_context_for_prompt(
    get_pre_query(ums).gather_context(query)
)


if __name__ == "__main__":
    print("="*60)
    print("🔍 Pre-Query Memory - UMS v2.0")
    print("="*60)
    
    # Test
    pqm = PreQueryMemory()
    
    test_queries = [
        "What about the trading bot?",
        "Do I have API keys?",
        "What's the Gold Coast plan?",
        "What did we decide about memory?"
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        ctx = pqm.gather_context(query)
        formatted = pqm.format_context_for_prompt(ctx)
        if formatted:
            print(formatted)
        else:
            print("(No relevant context found)")
    
    print("\n" + "="*60)
    print("✅ Pre-Query tests complete!")