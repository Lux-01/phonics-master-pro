---
name: memory-manager
description: Advanced memory management with auto-tagging, proactive surfacing, and smart consolidation. Use when writing to MEMORY.md, searching past context, or when relevant prior knowledge exists but isn't in current context.
---

# Memory Manager

Advanced memory management for better context retrieval and organization.

## When to Use

- Writing new memories to MEMORY.md
- Searching for relevant past context
- Memory feels cluttered or disorganized
- Need to find specific information
- Consolidating duplicate memories
- "What do we know about X?"

## Core Functions

### Auto-Tagging

Automatically tag memories with categories:

```markdown
## Crypto Scanner v5.5

**Tags:** #project #solana #trading #automation  
**Related:** #solana-alpha-hunter #trading-strategy  
**Created:** 2026-02-18

...
```

Tags are auto-generated based on content:
- Project names → #project
- Technologies → #python #javascript #solana
- Categories → #trading #research #automation
- People → #user

### Proactive Surfacing

Before responding, check for relevant memories:

```markdown
User: "Work on the trading bot"
→ Search memory for "trading bot"
→ Find: Crypto Scanner (v5.5)
→ Find: Skylar Strategy (v2.0)
→ Surface: "We have 2 trading bot projects. Which one?"
```

### Memory Consolidation

Detect and merge duplicate or related memories:

```markdown
## CONSOLIDATION CANDIDATE

**Topic:** Solana Alpha Hunter
**Locations:**
- MEMORY.md line 45-50
- memory/2026-02-18.md line 12-20
- memory/2026-02-19.md line 5-8

**Action:** Consolidate into single entry in MEMORY.md
```

### Smart Search

Multi-strategy memory search:

| Strategy | When to Use |
|----------|-------------|
| Semantic | Find conceptually related |
| Keyword | Find exact terms |
| Date | Find by time period |
| Tag | Find by category |
| File | Search specific file |

## Memory Index

Maintain auto-generated index in `memory/INDEX.md`:

```markdown
# Memory Index

## By Tag
| Tag | Count | Files |
|-----|-------|-------|
| #project | 12 | MEMORY.md, 2026-02-* |
| #solana | 8 | MEMORY.md, 2026-03-* |

## By Date
| Week | Entries | Key Topics |
|------|---------|------------|
| 2026-W10 | 5 | Moltbook, Whale Tracker |

## By File
| File | Purpose |
|------|---------|
| MEMORY.md | Long-lived projects, decisions |
| YYYY-MM-DD.md | Daily logs, conversations |

## Hot Topics
| Topic | Last Mentioned | Frequency |
|-------|----------------|-----------|
| Trading bots | 2026-03-07 | High |
| Moltbook | 2026-03-08 | High |
```

## Writing Guidelines

### When Writing to MEMORY.md

1. **Tag it:** Add relevant #tags
2. **Link it:** Reference related memories
3. **Date it:** Include creation/modified date
4. **Organize it:** Put in right section

### Memory Structure

```markdown
# Category Name

## Project Name
**Status:** [Active/Complete/Paused]  
**Started:** Date  
**Tags:** #tag1 #tag2

Brief description...
```

## Proactive Memory Queries

Auto-check before:
- Starting new project → "Similar projects exist?"
- Making decision → "Was this decided before?"
- Answering question → "Do we already know this?"
- Technical implementation → "What pattern worked before?"

## Commands

| Action | Do |
|--------|-----|
| Store memory | Write to MEMORY.md with tags |
| Find memory | Search index + full text |
| Consolidate | Merge duplicates, update single source |
| Surface | Proactively suggest relevant memories |
| Archive | Move old to memory/archive/ |

## Integration

Update memory system:
1. After major decisions → Store in MEMORY.md
2. Daily logs → Write to memory/YYYY-MM-DD.md
3. Project completion → Update status
4. New skill created → Add to skills section

## State Tracking

Store in `memory/memory_state.json`:

```json
{
  "lastConsolidation": "2026-03-08",
  "entryCount": 45,
  "tags": ["project", "solana", "trading"],
  "hotTopics": ["trading bots", "moltbook"],
  "needsConsolidation": false
}
```
