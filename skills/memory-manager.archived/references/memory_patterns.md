# Memory Patterns Reference

## Memory Types

| Type | Location | Lifespan | Example |
|------|----------|----------|---------|
| Long-term | MEMORY.md | Permanent | Projects, decisions |
| Daily | YYYY-MM-DD.md | 30+ days | Daily activities |
| Temporary | memory/temp/ | 7 days | Scratch notes |
| State | memory/*.json | Session | Current state |

## Tag Taxonomy

### Project Tags
- #project-[name] for specific projects
- #active, #paused, #complete for status
- #priority-high, #priority-medium, #priority-low

### Technical Tags
- #language-python, #language-javascript
- #framework-[name]
- #api-[service]
- #database-[type]

### Domain Tags
- #trading, #crypto, #automation
- #research, #analysis
- #integration-[service]

### Process Tags
- #decision, #lesson-learned
- #work-in-progress, #blocked
- #question, #todo

## Memory Entry Structure

```markdown
## Entry Title
**Tags:** #tag1 #tag2  
**Created:** YYYY-MM-DD  
**Modified:** YYYY-MM-DD  
**Related:** [Links to other memories]

### Summary
One paragraph summary

### Details
[Full content]

### Actions Taken
- [x] Done
- [ ] TODO

### Notes
Additional context
```

## Proactive Memory Surfacing

### Before Responding, Check:

1. **Similar queries:** Have we done this before?
2. **Related projects:** Any existing work?
3. **Known preferences:** User's stated preferences
4. **Prior decisions:** DEC entries that apply
5. **Recent changes:** What's new since last session

### Surface When:

| Trigger | Action |
|---------|--------|
| User mentions "again" | Find previous occurrence |
| Starting new project | Check for similar projects |
| Technical question | Check if documented |
| "Remember when..." | Find and surface |

## Memory Consistency Rules

1. **Single source of truth:** Projects live in MEMORY.md, not duplicated across files
2. **Cross-reference:** Link between related memories
3. **Update in place:** Don't append, update existing entries
4. **Date everything:** Created and modified timestamps
5. **Tag liberally:** More tags = better discoverability

## Memory Consolidation Checklist

Run weekly:
- [ ] Merge duplicate entries about same topic
- [ ] Archive entries > 90 days old to memory/archive/
- [ ] Update INDEX.md
- [ ] Check for orphaned references
- [ ] Verify tags are still relevant
