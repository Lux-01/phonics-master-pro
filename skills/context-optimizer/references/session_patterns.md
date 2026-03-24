# Session Patterns Reference

## When to Create Checkpoints

Create a checkpoint when:
- Session reaches 20 messages
- Major decision made
- Switching to new topic
- "Let me summarize where we are"
- Before complex multi-step task

## Checkpoint Template

```markdown
## Session Checkpoint (Message #N)
- **Started:** [datetime]
- **Duration:** [how long]
- **Topic:** [main topic]

### Progress
- ✅ Completed: [done items]
- ⏳ In Progress: [current item]
- 📋 TODO: [remaining items]

### Key Decisions
1. [DEC-XXX] Decision made
2. [DEC-XXX] Another decision

### Files Active
- file1.py - purpose
- file2.json - purpose

### Notes
[Context that might be lost, open questions]
```

## File Read Deduplication Logic

```python
files_read = {
    "main.py": {
        "read_at": "msg-5",
        "summary": "Entry point with routing",
        "lines_read": [1, 50]
    }
}

def should_read(filepath, offset=None):
    """Determine if file should be re-read."""
    if filepath not in files_read:
        return True
    
    last_read = files_read[filepath]
    
    # Re-read if explicit range requested different from last
    if offset and offset != last_read.get('offset'):
        return True
    
    # Re-read if file changed since last read
    if file_modified_since(filepath, last_read['read_at']):
        return True
    
    return False
```

## Context Health Signals

| Signal | Threshold | Action |
|--------|-----------|--------|
| Message count | 20+ | Offer checkpoint |
| File re-reads | 2x same file | Use summary |
| Time gap | 30+ min | Refresh context |
| Topic drift | New subject | Create new checkpoint |
