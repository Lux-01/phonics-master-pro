"""
Universal Memory System (UMS) v2.0
Comprehensive memory solution with merged features from memory-manager

Quick Start:
    from skills.universal_memory_system import remember, recall, context_for
    
    remember("Important information")
    results = recall("topic")
    context = context_for("query")

Full API:
    from skills.universal_memory_system import MemoryAPI
    api = MemoryAPI()
    api.remember("content", category="decision")
    context = api.before_response("user query")

Core Components:
    - core/short_term.py: Hot session memory (in-memory)
    - core/long_term.py: Cold persistent storage (disk-backed)
    - core/semantic_search.py: Cross-tier search
    - core/auto_tagging.py: Pattern detection & categorization
    - remember.py: Command parsing
    - pre_query.py: Context surfacing
    - unified_api.py: Single entry point
    - aca_memory_system.py: Original UMS base
    - memory_bridge.py: Auto-capture integration
    - memory_cli.py: Command line interface
"""

__version__ = "2.0.0"
__author__ = "OpenClaw"
__license__ = "MIT"

# Core components (import lazily to avoid circular deps)
def ShortTermMemory():
    from .core.short_term import ShortTermMemory
    return ShortTermMemory

def LongTermMemory():
    from .core.long_term import LongTermMemory
    return LongTermMemory

def SemanticSearch():
    from .core.semantic_search import SemanticSearch
    return SemanticSearch

def AutoTagging():
    from .core.auto_tagging import AutoTagging
    return AutoTagging

# Main API
from .unified_api import (
    UnifiedMemoryAPI,
    MemoryAPI,
    get_memory_api,
    remember,
    recall,
    context_for,
    on_message,
    before_response,
    start_session,
    end_session,
    # Legacy compatibility
    get_memory_system,
    remember_key,
    remember_pref,
    log_fragment
)

# Original UMS
from .aca_memory_system import (
    UniversalMemorySystem,
    get_ums,
    remember as ums_remember,
    recall as ums_recall,
    get_context as ums_context_for,
    MemoryEntry,
    ResearchEntry,
    DecisionEntry,
    MemoryCategory
)

# Remember module
from .remember import (
    RememberCommand,
    check_and_remember,
    remember_api_key,
    remember_preference,
    remember_decision,
    log_fragment
)

# Pre-query module
from .pre_query import (
    PreQueryMemory,
    get_pre_query,
    gather_context,
    format_context,
    context_for as prequery_context
)

# Memory bridge
from .memory_bridge import (
    MemoryBridge,
    remember as bridge_remember,
    recall as bridge_recall,
    context_for as bridge_context,
    save_research,
    save_decision
)

# CLI
from .memory_cli import main as cli_main

__all__ = [
    # Version
    '__version__',
    
    # Main API (recommended)
    'UnifiedMemoryAPI',
    'MemoryAPI',
    'get_memory_api',
    'remember',
    'recall',
    'context_for',
    'on_message',
    'before_response',
    'start_session',
    'end_session',
    
    # Original UMS
    'UniversalMemorySystem',
    'get_ums',
    'ums_remember',
    'ums_recall',
    'ums_context_for',
    'MemoryEntry',
    'ResearchEntry',
    'DecisionEntry',
    'MemoryCategory',
    
    # Remember
    'RememberCommand',
    'check_and_remember',
    'remember_api_key',
    'remember_preference',
    'remember_decision',
    'log_fragment',
    
    # Pre-query
    'PreQueryMemory',
    'get_pre_query',
    'gather_context',
    'format_context',
    'prequery_context',
    
    # Bridge
    'MemoryBridge',
    'bridge_remember',
    'bridge_recall',
    'bridge_context',
    'save_research',
    'save_decision',
    
    # Legacy compatibility
    'get_memory_system',
    'remember_key',
    'remember_pref',
]