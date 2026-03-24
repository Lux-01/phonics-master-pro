---
name: decision-log
description: Track and retrieve decisions with reasoning, context, and dates. Use when someone asks "why did we choose X?", "when did we decide...", or to document important choices with full rationale for future reference.
---

# Decision Log

Track decisions with full context so they can be retrieved and understood later.

## When to Use

- "Why did we choose X?"
- "When did we decide...?"
- Documenting important choices
- Recording rationale before moving on
- Revisiting past decisions

## Decision Format

Each decision entry:

```markdown
## DEC-001: Solana over Ethereum for trading bot

**Date:** 2026-03-08  
**Context:** Building crypto trading bot  
**Decision:** Use Solana ecosystem for trading bot

**Why:**
- Lower transaction fees ($0.001 vs $5-50)
- Faster finality (400ms vs 12s)
- Better ecosystem for meme coins
- User preference for Solana

**Alternatives Considered:**
- Ethereum: Too expensive for frequent trades
- BSC: Centralized, less liquidity
- Base: Too new, fewer tools

**Consequences:**
- + Need to learn Rust/Anchor
- + Access to Jupiter aggregator
- - Less mature developer tooling

**Reversible:** Yes, can port strategy  
**Revisit By:** 2026-04-08
```

## Storage

Store decisions in `memory/decisions/DEC-XXX.md` or consolidated in `memory/DECISIONS.md`:

```markdown
# Decision Log

## Index
| ID | Date | Topic | Status |
|----|------|-------|--------|
| DEC-001 | 2026-03-08 | Solana vs ETH | Active |
| DEC-002 | 2026-03-08 | Position sizing | Active |

## Full Entries

### DEC-001: [title]
...
```

## Workflow

### Recording a Decision

```
User: Let's go with Solana
→ Create decision entry
→ Capture alternatives considered
→ Note rationale
→ Save with auto-generated ID
→ Confirm: "Documented as DEC-003"
```

### Retrieving Decisions

```
User: Why did we choose Solana?
→ Search decisions by topic/keyword
→ Find relevant entries
→ Present full rationale
→ Offer to revisit if needed
```

## Auto-Capture Triggers

Record a decision when:
- User says "let's go with X" or "decide on Y"
- Multiple alternatives discussed
- Significant trade-offs mentioned
- User asks to "remember this choice"

## Commands

| Action | What to do |
|--------|------------|
| Log decision | Create DEC-XXX entry with full context |
| Find decision | Search by topic/keyword/date |
| Revisit decision | Mark old as deprecated, create new |
| List decisions | Show index table |

## Example Query Responses

**"Why did we choose Solana?"**
→ Pull DEC-001, show full rationale

**"Have we decided on position sizing?"**
→ Search decisions for "position" or "sizing"
→ Show matching entries

**"What decisions have we made this session?"**
→ List all decisions from today's session
→ Show brief summary of each
