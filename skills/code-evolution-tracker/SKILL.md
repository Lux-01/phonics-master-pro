---
name: code-evolution-tracker
description: Track code changes over time, document improvements, performance gains, and successful patterns. Use when refactoring code, after code reviews, or to build a knowledge base of what works.
---

# Code Evolution Tracker

Track how code improves over time and document what patterns work best.

## When to Use

- After refactoring code
- Following code review
- Comparing before/after
- "How did we improve this?"
- Building pattern library
- Documenting performance gains

## Core Concepts

### Evolution Entry

Each significant change:

```markdown
## EVO-001: Trading Strategy Optimization

**File:** strategy.py  
**Date:** 2026-03-08  
**Author:** User + Lux

### Before
```python
# V1: Simple loop
for token in tokens:
    if token.price > threshold:
        buy(token)
```
**Issues:** 
- API rate limit exceeded
- No error handling
- Slow sequential execution

### After
```python
# V2: Batch with concurrency
batches = chunk(tokens, 10)
async with aiohttp.ClientSession() as session:
    results = await asyncio.gather(*[
        process_batch(b, session) for b in batches
    ])
```
**Improvements:**
- 5x faster (10min → 2min)
- Rate limiting handled
- Proper error recovery

### Pattern Established
**"API Batch Processing"**
- Chunk large lists
- Use asyncio for I/O bound
- Always handle rate limits
- Add exponential backoff

### Metrics
| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Runtime | 10min | 2min | -80% |
| API calls | 100 | 100 | - |
| Errors | 12 | 0 | -100% |
| Lines | 25 | 40 | +60% |
```

## Evolution Log Structure

Store in `memory/code_evolution/README.md` with entries in `memory/code_evolution/entries/`:

```
memory/code_evolution/
├── README.md           # Index and patterns
└── entries/
    ├── EVO-001.md      # Individual evolution entries
    ├── EVO-002.md
    └── ...
```

### Index Format

```markdown
# Code Evolution Log

## Pattern Library
| Pattern | First Used | Times Applied | Success Rate |
|-----------|------------|---------------|--------------|
| API Batching | EVO-001 | 5 | 100% |
| Error Wrapping | EVO-003 | 3 | 100% |
| Config Injection | EVO-005 | 2 | 100% |

## Recent Evolutions
| ID | Date | File | Improvement |
|----|------|------|-------------|
| EVO-007 | 2026-03-08 | api_client.py | Added retry logic |
| EVO-006 | 2026-03-07 | strategy.py | Parallel processing |

## By File
- strategy.py: EVO-001, EVO-006
- api_client.py: EVO-007
```

## Automatic Capture Triggers

Record evolution when:
- Refactoring reduces complexity
- Performance improves significantly
- Bug fixed with pattern change
- New error handling added
- User says "that's much better"

## Metrics to Track

| Category | Metrics |
|----------|---------|
| Performance | Runtime, memory, throughput |
| Reliability | Error rate, crash frequency |
| Maintainability | Lines, complexity, test coverage |
| Efficiency | API calls, tokens used |

## Query Patterns

### "How did we improve strategy.py?"
→ Show all EVO entries for strategy.py

### "What patterns work for API calls?"
→ Filter patterns, show success rates

### "Show me recent improvements"
→ Last 5 evolution entries

### "What's our success rate with batching?"
→ Aggregate pattern usage stats

## Integration

Update evolution log:
1. After significant refactors
2. Post code review improvements
3. On explicit "track this change"
4. Weekly summary of changes

## Evolution Entry Template

```markdown
## EVO-XXX: [Brief Description]

**File:** filename  
**Date:** YYYY-MM-DD  
**Context:** [Why change was needed]

### Problem
[What was wrong with before]

### Solution
[What changed]

### Code
**Before:**
```
...
```

**After:**
```
...
```

### Results
| Metric | Before | After |
|--------|--------|-------|
| ... | ... | ... |

### Pattern
[Reusable pattern if applicable]
```
