# Decision Patterns Reference

## When to Log Decisions

Log a decision when any of these trigger:

### Explicit Triggers
- "Let's go with X"
- "I choose Y"
- "We should do Z"
- "Decision: ..."

### Implicit Triggers
- Multiple alternatives discussed and one selected
- Trade-offs explicitly weighed
- "Why" explanation follows a choice
- User asks to "remember this choice"

## Decision Entry Template

```markdown
## DEC-XXX: [Concise Title]

**Date:** YYYY-MM-DD  
**Context:** [What were we working on]  
**Decision:** [What was decided]

### Options Considered
| Option | Pros | Cons | Chosen? |
|--------|------|------|---------|
| A | ... | ... | Yes |
| B | ... | ... | No |
| C | ... | ... | No |

### Rationale
- Reason 1
- Reason 2
- Constraint that drove the choice

### Consequences
**Positive:**
- Outcome 1
- Outcome 2

**Negative:**
- Trade-off made
- Risk accepted

### Reversibility
- **Can change:** Yes/No
- **Effort to change:** High/Medium/Low
- **Revisit by:** Date or trigger condition

### Related Decisions
- Related to DEC-XXX (depends on)
- Supersedes DEC-XXX (replaces)
```

## Decision Categories

| Category | Prefix | Example |
|----------|--------|---------|
| Technical | DEC | DEC-001: Use Python 3.11 |
| Architecture | ARC | ARC-003: Microservices |
| Process | PRO | PRO-005: Daily standups |
| Tool | TOOL | TOOL-007: Use Docker |
| Design | DES | DES-012: Dark mode default |

## Decision Status Flow

```
Proposed → Active → [Deprecated | Superseded | Validated]
```

- **Active:** Current, being followed
- **Deprecated:** No longer relevant
- **Superseded:** Replaced by newer decision (link to DEC-YYY)
- **Validated:** Confirmed to work well

## Anti-Patterns

❌ DON'T log:
- Obvious choices ("use the file system")
- Implementation details ("variable named X")
- Temporary workarounds not discussed
- Personal preferences without trade-offs

✅ DO log:
- Non-obvious choices
- Alternatives seriously considered
- High-impact decisions
- Decisions user might ask about later
