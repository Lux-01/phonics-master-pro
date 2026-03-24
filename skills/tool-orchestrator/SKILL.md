---
name: tool-orchestrator
description: Optimize multi-tool workflows by planning optimal sequences, parallelizing independent calls, and suggesting tool combinations for common tasks. Use when a task requires 3+ tools, has dependencies between steps, or follows common patterns.
---

# Tool Orchestrator

Optimize tool usage for complex multi-step tasks.

## When to Use

- Task requires 3+ tools
- Steps have dependencies (B needs A's result)
- Common workflow patterns
- "What's the best way to do X?"
- Want to parallelize independent calls

## Core Patterns

### Pattern: Sequential (Dependencies)

When step B needs output from step A:

```
1. Read config.json
   ↓ (needs content)
2. Parse config → extract API key
   ↓ (needs key)
3. Call API with key
   ↓ (needs response)
4. Write results to file
```

**Strategy:** Execute serially, pass outputs

### Pattern: Parallel (Independent)

When steps don't depend on each other:

```
1. Read file A ──┐
2. Read file B ──┼──→ All can run simultaneously
3. Read file C ──┘
```

**Strategy:** Batch calls where possible

### Pattern: Fan-Out Fan-In

Multiple parallel → single combine:

```
1. Query API A ──┐
2. Query API B ──┼──→ 3. Synthesize results
3. Query API C ──┘
```

**Strategy:** Execute queries in parallel, then synthesize

## Common Workflows

### File Analysis Pipeline

```
1. List files in directory
2. Read metadata from each
3. Filter by criteria
4. Process matches
5. Write report

Optimizations:
- Batch reads where independent
- Skip already-cached files
- Parallel process if no dependencies
```

### Research Pipeline

```
1. Search web for topic
2. Fetch top 3 results
3. Extract key findings
4. Compare sources
5. Synthesize conclusion

Optimizations:
- Fetch in parallel
- Stream synthesis as results arrive
- Early termination if consensus reached
```

### Code Review Pipeline

```
1. Read changed files
2. Check against style guide
3. Run linter
4. Generate diff summary
5. Post review comments

Optimizations:
- Lint files in parallel
- Cache style guide reference
- Batch review comments
```

## Dependency Tracking

Track dependencies in `memory/tool_workflows.json`:

```json
{
  "workflow_id": "research-jupiter-api",
  "steps": [
    {"id": 1, "tool": "web_fetch", "depends_on": [], "output": "docs"},
    {"id": 2, "tool": "web_fetch", "depends_on": [], "output": "github"},
    {"id": 3, "tool": "synthesize", "depends_on": [1, 2], "output": "summary"}
  ],
  "parallel_groups": [[1, 2], [3]]
}
```

## Optimization Strategies

### Strategy 1: Read Deduplication

Before reading:
- Check if file already read this session
- If yes: use cached content
- If modified since: re-read

### Strategy 2: Batch Independent Calls

```
Instead of:
  Read A → wait → Read B → wait → Read C

Do:
  Read A, B, C simultaneously → Process all results
```

### Strategy 3: Fail-Fast

If critical call fails:
- Stop dependent steps immediately
- Report error without wasting calls
- Suggest alternative approach

### Strategy 4: Progressive Loading

For large tasks:
- Load overview first (metadata)
- Load details on demand
- Keep context window efficient

## Commands

| Task | Do |
|------|-----|
| Plan workflow | Map dependencies, suggest optimal order |
| Optimize task | Suggest parallelization, caching strategies |
| Estimate cost | Predict token usage, call count |
| Execute plan | Follow orchestrated sequence |

## Workflow Planning Template

```markdown
## Task Analysis: "Research and implement X"

### Required Tools
- web_fetch (3x)
- read (2x)
- write (1x)

### Dependencies
- Write needs synthesis
- Synthesis needs all fetches
- Write needs template read

### Optimal Order
```
1. Fetch source A ──┐
2. Fetch source B ──┼→ 4. Synthesize → 5. Write
3. Fetch source C ──┘      ↑
                      6. Read template ──┘
```

### Cost Estimate
- API calls: 3
- File reads: 3
- File writes: 1
- Estimated tokens: ~5000
```
