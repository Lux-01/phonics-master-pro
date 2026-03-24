# Universal Memory System (UMS)

**"Never forget anything again"**

A comprehensive, multi-layer memory system that captures, categorizes, and retrieves everything - research, conversations, decisions, code, and context.

---

## Overview

The Universal Memory System solves the "amnesia problem" - losing context between sessions, forgetting research, misplacing decisions. It provides structured, searchable, persistent memory across all interactions.

### What UMS Captures

- **Conversations** - What was discussed, decided, requested
- **Research** - Findings, sources, key points
- **Decisions** - What was decided, why, alternatives considered
- **Code** - What was built, fixed, refactored
- **Projects** - Status, progress, milestones
- **Preferences** - User preferences, patterns
- **API Keys** - Credentials (with security measures)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: RAW CAPTURE (Automatic)                           │
│  ├── Every message analyzed                                 │
│  ├── Auto-categorization                                    │
│  └── Real-time indexing                                     │
├─────────────────────────────────────────────────────────────┤
│  Layer 2: DAILY JOURNAL                                     │
│  └── memory/YYYY-MM-DD.md                                   │
│      ├── Auto-generated summaries                           │
│      ├── Key decisions                                      │
│      └── Links to detailed knowledge                        │
├─────────────────────────────────────────────────────────────┤
│  Layer 3: KNOWLEDGE BASE (Curated)                          │
│  └── memory/knowledge/                                       │
│      ├── research/     # Research with sources               │
│      ├── decisions/    # Decision logs                       │
│      ├── projects/     # Project tracking                   │
│      └── people/       # Preferences                         │
├─────────────────────────────────────────────────────────────┤
│  Layer 4: SEARCHABLE INDEX                                   │
│  └── memory/index.json                                      │
│      ├── Keywords                                           │
│      ├── Tags                                               │
│      └── Timestamps                                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Installation

No installation required. UMS is self-contained Python code.

```bash
# Files are automatically created in /memory directory
cd /home/skux/.openclaw/workspace/skills/universal-memory-system
python3 aca_memory_system.py  # Run self-test
```

---

## Usage

### Quick Functions

```python
from memory_bridge import remember, recall, context_for

# Remember something
remember("User prefers dark mode for all apps", category="preference")

# Recall memories
results = recall("trading strategy", limit=5)

# Get context for current query
context = context_for("what were we building")
```

### Advanced Usage

```python
from aca_memory_system import UniversalMemorySystem

ums = UniversalMemorySystem()

# Store research
ums.remember_research(
    topic="crypto mining",
    findings="Mining requires ~$0.10/kWh to be profitable...",
    sources=["https://example.com/mining-guide"],
    key_points=["Electricity is main cost", "ASICs required for BTC"]
)

# Store decision
ums.remember_decision(
    decision="Use Python for backend",
    context="Building trading automation system",
    reasoning="Python has best library support for trading APIs",
    alternatives=["Node.js", "Go"],
    reversible=True
)

# Search with filters
results = ums.search(
    query="trading",
    category_filter="research",
    limit=10
)

# Get formatted context
context = ums.get_context("build trading system")
```

---

## CLI Commands

```bash
# Remember something
python3 memory_cli.py remember "Important decision" --category decision

# Recall memories
python3 memory_cli.py recall "trading strategy" --limit 5

# Store research
python3 memory_cli.py research "crypto mining" \
    --findings "Mining requires cheap electricity..." \
    --sources "https://..."

# Store decision
python3 memory_cli.py decision "Use Python" \
    --reasoning "Best library support" \
    --context "Building trading system"

# Get context
python3 memory_cli.py context "what were we building"

# View today's memories
python3 memory_cli.py today

# Check status
python3 memory_cli.py status

# Interactive mode
python3 memory_cli.py interactive
```

---

## Auto-Capture

The Memory Bridge automatically captures based on content:

```python
from memory_bridge import MemoryBridge

bridge = MemoryBridge()

# These are auto-captured:
bridge.analyze_message("user", "I decided to use Python")
# → Captured as: decision

bridge.analyze_message("assistant", "Research shows...")
# → Captured as: research

bridge.analyze_message("user", "My API key is abc123")
# → Captured as: api_key (high importance)

# These are NOT captured (not important enough):
bridge.analyze_message("user", "Just saying hi")
# → Skipped
```

---

## Memory Categories

| Category | Auto-Trigger | Storage |
|----------|-------------|---------|
| research | "research", "found", "analysis" | knowledge/research/ |
| decision | "decided", "decision", "concluded" | knowledge/decisions/ |
| code | "build", "create", "develop" | knowledge/projects/ |
| conversation | General chat | raw_capture/ |
| api_key | "api key", "token", "credential" | knowledge/people/ (secure) |
| preference | "prefer", "usually", "always" | knowledge/people/ |

---

## Search Algorithm

UMS uses multi-factor ranking:

```python
score = (
    keyword_overlap * 10 +     # Direct word matches
    recency_bonus +          # Recent = more relevant
    importance * 2 +          # Important entries rank higher
    access_frequency * 0.5  # Popular entries rank higher
)
```

---

## Files Created

```
memory/
├── index.json                    # Searchable index
├── raw_capture/                  # Auto-captured memories
│   └── YYYY-MM-DD.jsonl
└── knowledge/
    ├── research/
    │   └── YYYY-MM-DD.jsonl     # Research with sources
    ├── decisions/
    │   └── YYYY-MM-DD.jsonl     # Decision logs
    ├── projects/
    │   └── YYYY-MM-DD.jsonl     # Project progress
    └── people/
        └── YYYY-MM-DD.jsonl     # Preferences, credentials
```

---

## Integration

### With OpenClaw

```python
# Before responding, check memory
from memory_bridge import context_for

def respond_to_user(query):
    # Get relevant context
    context = context_for(query)
    
    # Use context in response
    response = generate_response(query, context)
    
    # Remember this interaction
    remember(f"User asked: {query}")
    remember(f"I responded: {response}")
    
    return response
```

### With Skills

```python
# In any skill, auto-capture:
from memory_bridge import MemoryBridge

class MySkill:
    def __init__(self):
        self.memory = MemoryBridge()
    
    def run(self, task):
        # Auto-capture important actions
        self.memory.analyze_message("system", f"Executing: {task}")
        
        # Do work...
        result = do_work(task)
        
        # Remember result
        self.memory.remember_research(task, result)
```

---

## ACA Compliance

UMS was built using **Autonomous Code Architect** methodology:

1. **Requirements Analysis** - Defined the amnesia problem
2. **Architecture Design** - 5-layer memory system
3. **Data Flow Planning** - Multi-stage capture → index → retrieve
4. **Edge Cases** - Empty memory, corruption, deduplication
5. **Tool Constraints** - File system only, no external DB
6. **Error Handling** - Retries, fallbacks, validation
7. **Testing** - Self-test validates all components

---

## Security

- **Credentials**: API keys stored with high importance
- **Masking**: Keys shown as `555e1b58-...d96eb` in normal display
- **Access Control**: Full keys only retrieved when explicitly needed
- **Location**: All within workspace, no external services

---

## Performance

- **Search**: O(1) lookup via index
- **Storage**: Append-only JSONL (fast writes)
- **Compression**: Large memories auto-compressed
- **Eviction**: LRU for oldest, lowest-importance entries

---

## Benefits

| Problem | Solution |
|---------|----------|
| "What were we working on?" | Daily journal + project tracking |
| "What was that API key?" | Auto-captured, instantly searchable |
| "Why did we decide that?" | Decision log with reasoning |
| "What research did I do?" | Research database with sources |
| "What did user prefer?" | Preference tracking in people/ |

---

## Future Enhancements

- [ ] Semantic search with embeddings
- [ ] Memory summarization for long conversations
- [ ] Cross-reference detection (link related memories)
- [ ] Export to external knowledge bases
- [ ] Backup/restore functionality

---

## Files

- `aca_memory_system.py` - Core memory system (25KB)
- `memory_bridge.py` - Auto-capture module (6KB)
- `memory_cli.py` - Command line interface (6KB)
- `SKILL.md` - This documentation

**Total:** ~40KB of comprehensive memory infrastructure

---

Built with ❤️ using ACA methodology
