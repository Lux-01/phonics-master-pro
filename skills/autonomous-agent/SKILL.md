---
name: autonomous-agent
description: All-in-one autonomous reasoning and action system for complex multi-step tasks. Self-directed planning, decision making, tool orchestration, error recovery, and progress tracking. Use when tasks require multiple steps, research, coding, file operations, or when user wants "handle this for me" with optional checkpoint reviews.
---

# Autonomous Agent

Complete autonomous reasoning and execution system. Handles complex tasks from planning through completion with minimal user intervention.

## Core Philosophy

**Autonomous but Accountable:**
- Self-directed task execution
- Automatic decision making with logging
- Progress tracking and transparency
- User checkpoints for high-stakes actions
- Full audit trail of actions taken

## Execution Modes

### Mode 1: Fully Autonomous (default)
```
User: "Research Solana DEX aggregators and implement a comparison script"
→ Plan task
→ Execute all steps
→ Deliver result
→ Log all decisions
```

### Mode 2: Checkpoint Review
```
User: "Build trading bot --checkpoint every 3 steps"
→ Plan task with checkpoints
→ Execute step 1-3
→ Pause: "Review progress? [continue/modify/stop]"
→ Continue based on feedback
```

### Mode 3: Shadow Mode
```
User: "Plan how you'd build this [dry run]"
→ Show complete execution plan
→ Get approval before any action
→ User approves/modifies
→ Execute approved plan
```

## The OODA Loop

All autonomous actions follow OODA:

**Observe:**
- Gather current context
- Read relevant files
- Check existing capabilities
- Assess environment state

**Orient:**
- Analyze gathered data
- Identify patterns from memory
- Evaluate constraints
- Form understanding

**Decide:**
- Generate action options
- Score options (risk, reward, feasibility)
- Select best path
- Log decision with rationale

**Act:**
- Execute chosen action
- Monitor results
- Handle errors
- Track progress

**Repeat** until task complete.

## Task Planning Framework

### Phase 1: Task Decomposition

Break complex tasks into atomic operations:

```markdown
## Task: Build Solana Trading Bot

### Decomposition
1. [RESEARCH] Understand Jupiter API
2. [CODE] Create connection module
3. [CODE] Build swap execution
4. [CODE] Add wallet management
5. [TEST] Validate with paper trading
6. [INTEGRATE] Connect to monitoring

Dependencies:
- 3 depends on 2
- 4 depends on 2, 3
- 5 depends on 1-4
```

### Phase 2: Resource Assessment

Before acting, answer:
- What tools needed? (web, read, write, exec, etc.)
- What files exist? (check workspace)
- What knowledge needed? (search memory)
- What could go wrong? (risk assessment)

### Phase 3: Execution Planning

Create execution graph:

```
Step 1 ──┬──→ Step 2 ──→ Step 4 ──┬──→ Step 6
         │                        │
         └──→ Step 3 ─────────────┘
```

- Parallelize where possible
- Mark checkpoints for review
- Identify rollback points

## Decision Making

### Decision Matrix

For each decision, log:

```markdown
## Decision: [What was decided]
**Context:** [Situation]  
**Options:**
| Option | Pros | Cons | Risk | Confidence |
|--------|------|------|------|------------|
| A | ... | ... | Low | 80% |
| B | ... | ... | Med | 60% |

**Chosen:** A  
**Rationale:** [Why]  
**Confidence:** 80%  
**Reversible:** Yes/No  
**Check needed:** Yes/No
```

### Auto-Decision Rules

**Auto-approve (no checkpoint):**
- Reading files
- Writing to temp/
- Web searches
- Testing in isolated environment

**Checkpoint required:**
- Writing to production code
- Sending messages
- Financial transactions (even test)
- Deleting files
- Modifying MEMORY.md
- Git commits/pushes

## Execution Patterns

### Pattern 1: Research → Plan → Code → Test

```
1. RESEARCH
   - Search web for best practices
   - Check existing code in workspace
   - Review similar past projects

2. PLAN
   - Design architecture
   - Choose libraries/tools
   - Break into functions/modules

3. CODE
   - Write implementation
   - Add comments explaining why
   - Include error handling

4. TEST
   - Run code if testable
   - Check for syntax errors
   - Validate logic (dry run if needed)

5. DELIVER
   - Present complete solution
   - Explain key decisions
   - Suggest next steps
```

### Pattern 2: Iterative Refinement

```
1. Build MVP version
2. Test with user
3. Gather feedback
4. Refine based on feedback
5. Repeat until complete
```

### Pattern 3: Divide and Conquer

```
For large tasks:
1. Split into independent sub-tasks
2. Execute sub-tasks in parallel
3. Integrate results
4. Test complete solution
```

## Error Recovery

### Error Handling Strategy

1. **Detect:** Catch error immediately
2. **Diagnose:** Understand what failed
3. **Options:** Generate recovery paths
4. **Decide:** Choose best recovery
5. **Execute:** Attempt recovery
6. **Escalate:** Ask user if recovery fails

### Common Error Patterns

| Error | Recovery Action |
|-------|-----------------|
| File not found | Search for file, suggest alternatives |
| Syntax error | Re-read file, identify issue, fix |
| API failure | Retry with backoff, try alternative |
| Tool unavailable | Use alternative tool/method |
| Timeout | Break task into smaller chunks |
| Rate limit | Pause, wait, resume |

## Progress Tracking

### Task State

Track in `memory/autonomous_tasks/TASK_ID.json`:

```json
{
  "taskId": "TASK-001",
  "description": "Build trading bot",
  "status": "in_progress",
  "startedAt": "2026-03-08T22:00:00",
  "currentStep": 3,
  "totalSteps": 6,
  "decisions": [
    {"id": "DEC-001", "what": "Used Jupiter V6", "why": "Better latency"}
  ],
  "checkpoints": [
    {"step": 3, "status": "awaiting_review", "timestamp": "..."}
  ],
  "errors": [],
  "deliverables": []
}
```

### Progress Reporting

```markdown
## Task Progress: [Name]
██████░░░░ 60% Complete

### Current: Step 3 of 5 - Building swap execution

### Recent Actions:
- ✅ Step 1: Researched Jupiter API
- ✅ Step 2: Created connection module
- ⏳ Step 3: Building swap execution
- 📋 Step 4: Wallet management (pending)
- 📋 Step 5: Testing (pending)

### Next Action: [Describe]
### ETA: [Time estimate]
### Blockers: [Any?]
```

## Tool Orchestration

### Automatic Tool Selection

Given a task, autonomously choose:
- **Information gathering:** `web_fetch`, `memory_search`
- **File operations:** `read`, `write`, `edit`
- **Code execution:** `exec` with proper timeout
- **Process management:** `process`
- **Complex tasks:** `sessions_spawn` for sub-agents

### Batch Optimization

When multiple independent calls needed:
```
Instead of:
  Read A → wait → Read B → wait → Read C

Do:
  Read A, Read B, Read C simultaneously
  → Process all results
```

### Parallel Execution

```python
# Pattern for parallel tasks
results = await asyncio.gather(
    task1(),
    task2(),
    task3()
)
```

## Memory Integration

### Automatic Memory Usage

Before acting:
1. **memory_search** - Have we done this before?
2. **Read MEMORY.md** - Any relevant projects?
3. **Check decisions** - Past choices that apply?
4. **Pattern library** - What worked before?

After acting:
1. **Log decision** if non-trivial choice made
2. **Update daily log** - What was accomplished
3. **Update MEMORY.md** if significant project

### Context Awareness

Maintain awareness of:
- Current project context
- User preferences (from USER.md)
- Technical constraints
- Time constraints
- Tool availability

## Safety Protocols

### Do Not Autonomously

Always ask first:
- Delete or overwrite critical files
- Send messages/emails
- Push to git repos
- Execute destructive commands
- Access external services with auth
- Modify system configuration

### Protected Paths

```
/memory/       - Can read/update, preserve structure
/temp/         - Can write freely
agents/        - Can read, edit with caution
config/        - Read only, ask to modify
```

### User Confirmation Triggers

Require explicit confirmation for:
- Actions affecting >3 files
- Changes to production code
- Financial implications
- External communications
- Irreversible operations

## Reporting

### Final Delivery

Always include:
1. **What was done** (summary)
2. **How it was done** (approach)
3. **Why choices were made** (decisions)
4. **What files changed** (deliverables)
5. **What's next** (recommendations)

### Decision Summary

```markdown
## Decisions Made (Auto-logged)
| ID | Decision | Rationale | Confidence |
|----|----------|-----------|------------|
| 1 | Used X over Y | Better performance | 85% |
| 2 | Implemented Z pattern | Follows best practices | 90% |
```

## Usage Examples

### Example 1: "Build me a trading bot"
```
1. Plan complete architecture
2. Research best practices
3. Code all modules
4. Add error handling
5. Create usage docs
6. Test basic flow
7. Deliver with explanation
```

### Example 2: "Debug why scanner is slow"
```
1. Read scanner code
2. Profile slow sections
3. Identify bottlenecks
4. Implement optimizations
5. Test improvements
6. Log as EVO entry
7. Deliver results
```

### Example 3: "Organize my projects"
```
1. Analyze all files
2. Categorize projects
3. Detect duplicates
4. Propose restructure
5. Get user approval
6. Execute reorg
7. Document new structure
```

## Integration

### With Other Skills

Auto-invoke other skills when needed:
- **decision-log** - For significant choices
- **tool-orchestrator** - For multi-tool sequences
- **research-synthesizer** - For multi-source research
- **code-evolution-tracker** - After significant code changes
- **workspace-organizer** - When restructuring

### With MEMORY.md

Log autonomous tasks:
```markdown
## Autonomous Tasks
| Task | Status | Started | Duration |
|------|--------|---------|----------|
| Trading bot build | Complete | 2026-03-08 | 2 hours |
```

## Commands

| Command | Action |
|---------|--------|
| "Handle this" | Full autonomous mode |
| "Plan this first" | Shadow mode - show plan |
| "Checkpoint every N steps" | Review at intervals |
| "Auto mode" | No confirmations unless critical |
| "Safe mode" | Confirm every significant action |

## State Files

```
memory/autonomous_agent/
├── active_tasks/
│   ├── TASK-001.json
│   └── TASK-002.json
├── completed_tasks/
│   └── [archived completed tasks]
├── decisions/
│   └── DECISION-[task]-[num].md
└── patterns/
    └── successful_workflows.json
```
