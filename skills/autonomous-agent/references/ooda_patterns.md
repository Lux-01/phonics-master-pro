# OODA Loop Patterns

## Observe

### Information Gathering Checklist
- [ ] Current context from conversation
- [ ] Relevant memories (search)
- [ ] Existing files in workspace
- [ ] External documentation if needed
- [ ] Past similar tasks
- [ ] User preferences

### Observation Patterns
```
Pattern: Quick Scan
- Read MEMORY.md
- List relevant files
- Check for existing code
- Time: < 1 minute

Pattern: Deep Dive
- Search all memories
- Read multiple files
- Research external sources
- Time: 2-5 minutes

Pattern: Incremental
- Start with minimal context
- Gather more as needed
- Adapt plan based on findings
```

## Orient

### Analysis Framework
1. **What do we know?** (Facts from observation)
2. **What do we need?** (Gaps to fill)
3. **What's the goal?** (Success criteria)
4. **What constraints exist?** (Limitations)
5. **What patterns apply?** (Past similar work)

### Orientation Questions
- Is this similar to something we've done before?
- What tools/libraries are available?
- What could go wrong?
- What's the minimum viable version?
- Are there user preferences to respect?

## Decide

### Decision Types

**Type 1: Technical Approach**
- Which language/framework?
- Which API/library?
- Which pattern/architecture?

**Type 2: Implementation Details**
- How to structure code?
- How to handle errors?
- What to name functions?

**Type 3: Process Decisions**
- Which mode to use? (autonomous/checkpoint)
- How many checkpoints?
- When to ask for confirmation?

### Decision Confidence Levels
- **>90%:** Obvious choice, auto-execute
- **70-90%:** Good choice, probably auto-execute, maybe log
- **50-70%:** Uncertain, checkpoint or ask
- **<50%:** Need more info or ask user

## Act

### Action Categories

**READ:**
- File content, documentation
- Low risk, always allowed

**WRITE:**
- New files: Low risk
- Temp files: Low risk  
- Modify existing: Medium-high risk
- Overwrite production: High risk

**EXEC:**
- Read-only commands: Low risk
- Test scripts: Medium risk
- Production commands: High risk

**EXTERNAL:**
- Web fetch: Low risk
- API calls: Medium risk
- Messages/emails: High risk

### Execution Templates

```python
# Template: Create new module
def create_module(name, purpose):
    """Create new Python module."""
    content = f'''"""
{purpose}
"""
# TODO: Implementation
'''
    write(f"{name}.py", content)
    log_action(f"Created {name}.py for {purpose}")

# Template: Modification with backup
def modify_file(filepath, changes):
    """Modify file with backup."""
    original = read(filepath)
    backup_path = f"{filepath}.bak"
    write(backup_path, original, overwrite=True)
    apply_changes(filepath, changes)
    log_action(f"Modified {filepath} (backup at {backup_path})")
```

## Full OODA Examples

### Example 1: "Build API client"

**Observe:**
- Check existing API clients
- Research target API docs
- Look for auth patterns

**Orient:**
- API uses REST with JSON
- Need auth headers
- Similar to existing Jupiter client
- User prefers async Python

**Decide:**
- Use aiohttp for async
- Create class-based client
- Match pattern of existing client
- Add retry logic

**Act:**
- Write client.py
- Add error handling
- Test basic request
- Document usage

### Example 2: "Debug slow code"

**Observe:**
- Read reported slow code
- Check memory logs for past issues
- Look for profiling data

**Orient:**
- Nested loops are culprit
- No caching implemented
- API calls in inner loop
- Pattern seen before (EVO-003)

**Decide:**
- Add caching layer
- Batch API calls
- Optimize loop structure
- Log as evolution

**Act:**
- Implement fixes
- Run comparison test
- Document improvement
- Update EVO log
