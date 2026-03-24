---
name: context-optimizer
description: Optimize conversation context management by tracking file reads, summarizing long sessions, auto-suggesting context refreshes, and detecting stale context. Use when conversations get long (20+ messages), files are read multiple times, or context appears outdated.
---

# Context Optimizer

Manage conversation context efficiently to reduce token waste and improve coherence.

## When to Use

- Long conversations (20+ messages)
- Same files being read multiple times
- "What were we talking about?" moments
- Context feels stale or lost
- Need to summarize session progress

## Core Functions

### Track File Reads

Maintain awareness of what has been read:

```markdown
## Files Read This Session
| File | Read At | Times | Summary |
|------|---------|-------|---------|
| config.json | msg #5 | 1 | API keys and endpoints |
| main.py | msg #8, #15 | 2 | Entry point, needs refactor |
```

Auto-suggest: "You've read main.py twice. Summary: entry point with routing logic."

### Session Summarizer

Create milestone summaries:

```markdown
## Session Checkpoint (Message #25)
- **Started:** 2026-03-08 14:00
- **Topic:** Building Solana trading bot
- **Progress:**
  - ✅ Defined strategy rules
  - ✅ Set up Jupiter API integration
  - ⏳ Working on: Position sizing logic
- **Key Files:** strategy.py, jupiter_client.py
- **Decisions:** Use 0.3 SOL max position size
```

### Context Health Monitor

Detect stale context:

```markdown
⚠️ Context Alert
- Last file read: 15 messages ago
- Session length: 45 messages
- Suggested action: Create checkpoint summary
```

## Usage Patterns

### Pattern 1: Auto-Summarize on Milestone

After every 20 messages or significant decision:
1. Summarize key progress
2. List active files
3. Note open questions

### Pattern 2: File Read Deduplication

Before reading a file:
1. Check if already read this session
2. If yes, use summary instead of re-reading
3. Only re-read if explicitly requested or content changed

### Pattern 3: Context Refresh Suggestion

When context feels stale:
1. Offer session summary
2. Suggest re-reading key files
3. Confirm current objectives

## Workflow

```
User: [long conversation continues]
→ Count messages
→ Check if milestone (20/40/60...)
→ If yes: Create checkpoint summary

User: Read that file again
→ Check files_read log
→ If recently read: Show summary
→ Ask: "Full re-read or summary sufficient?"

User: What were we doing?
→ Show latest checkpoint
→ List recent decisions
→ Suggest next step
```

## Integration

Store context state in `memory/context_state.json`:

```json
{
  "sessionStart": "2026-03-08T14:00:00",
  "messageCount": 25,
  "filesRead": [
    {"path": "main.py", "readAt": "msg-5", "summary": "Entry point"}
  ],
  "checkpoints": [
    {"at": "msg-20", "summary": "...", "keyDecisions": []}
  ]
}
```
