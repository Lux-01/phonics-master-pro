# Error Recovery Guide

## Error Classification

### Temporary Errors (Retry)
- Network timeout
- Rate limiting
- File locked (temporarily)
- API temporarily unavailable

**Recovery:** Retry with exponential backoff

### Logic Errors (Fix)
- Syntax errors
- Logic bugs
- Wrong parameters
- Invalid assumptions

**Recovery:** Fix and retry

### Environmental Errors (Adapt)
- Missing dependencies
- Wrong file paths
- Invalid configuration
- Tool unavailable

**Recovery:** Adapt approach

### User Errors (Escalate)
- Unclear requirements
- Contradictory instructions
- Impossible constraints
- Missing information

**Recovery:** Ask for clarification

## Recovery Patterns

### Pattern: Retry with Backoff
```python
import time

def retry_with_backoff(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except TransientError as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt  # 1s, 2s, 4s
            time.sleep(wait_time)
```

### Pattern: Circuit Breaker
```python
class CircuitBreaker:
    def __init__(self, threshold=3):
        self.failures = 0
        self.threshold = threshold
        self.state = "closed"  # closed, open, half-open
    
    def call(self, func):
        if self.state == "open":
            raise Exception("Circuit open - try alternative")
        try:
            result = func()
            self.failures = 0
            return result
        except:
            self.failures += 1
            if self.failures >= self.threshold:
                self.state = "open"
            raise
```

### Pattern: Fallback
```python
def with_fallback(primary_func, fallback_func):
    try:
        return primary_func()
    except Exception as e:
        log(f"Primary failed: {e}, trying fallback")
        return fallback_func()
```

## Common Error Scenarios

| Error | First Try | Retry | Fallback | Escalate |
|-------|-----------|-------|----------|----------|
| API timeout | Retry | 3x, then | Use cached | Ask user |
| File not found | Search alt | - | Create new | Ask user |
| Syntax error | Fix error | Retry | - | If can't fix |
| Permission denied | Check perms | Retry | - | Ask user |
| Out of memory | Reduce data | Retry | Chunk data | Ask user |
| Rate limited | Wait | Exponential | Queue task | If blocked |

## Error Reporting Template

```markdown
## Error Report
**Task:** [Task ID]  
**Step:** [Which step failed]  
**Error:** [What went wrong]

### Context
- What was being attempted
- What worked before
- Recent changes

### Diagnosis
[Root cause analysis]

### Recovery Attempted
1. [What was tried]
2. [If retry, describe]
3. [Result of attempt]

### Options
- Option A: [Recovery path]
- Option B: [Alternative]
- Option C: [Ask user]

**Recommendation:** [Which option to pursue]
```
