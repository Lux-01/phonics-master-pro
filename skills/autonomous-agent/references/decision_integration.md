# Decision Logging Integration

## Auto-Log Decisions

The autonomous agent automatically logs decisions when:

### Technical Decisions
- Choice of library/framework
- Architecture pattern selected
- API vs local implementation
- Synchronous vs asynchronous

### Process Decisions
- Checkpoint placement
- Tool selection
- Parallel vs sequential execution
- Retry strategy

### User-Preference Decisions
- Code style choices
- Naming conventions
- Documentation approach
- Error handling approach

## Decision Format

```markdown
## DEC-[TaskID]-[Num]: [Short Description]
**Task:** [Task ID]  
**Step:** [Step number]  
**Date:** [ISO timestamp]

### Context
[What was happening when decision was made]

### Options Considered
| Option | Pros | Cons | Confidence |
|--------|------|------|------------|
| A | ... | ... | 80% |
| B | ... | ... | 60% |

### Decision
[What was chosen]

### Rationale
[Why this choice]

### Consequences
**Positive:**
- Outcome 1
- Outcome 2

**Negative:**
- Trade-off 1

### Reversibility
- **Can change:** Yes/No
- **Effort to reverse:** High/Med/Low

### Auto-Logged
Yes, by autonomous-agent skill
```

## Integration with decision-log Skill

When a significant decision is made:
1. Log to task-specific decision file
2. Also log to central decision log if major
3. Link between logs

```python
# In autonomous execution
def make_decision(task_id, options, chosen, rationale):
    decision_id = f"DEC-{task_id}-{decision_number}"
    
    # Log to task
    log_task_decision(task_id, decision_id, options, chosen, rationale)
    
    # If major decision, also log centrally
    if confidence < 0.8 or impact == "high":
        log_central_decision(decision_id, options, chosen, rationale)
```

## Decision Thresholds

**Auto-log (minor):**
- Tool selection (obvious choice)
- File naming
- Parameter values
- Confidence > 90%

**Task-log (medium):**
- Implementation approach
- Checkpoint placement
- Error handling strategy
- Confidence 70-90%

**Central-log (major):**
- Architecture choices
- External service selection
- Trade-off decisions
- Confidence < 70%
