---
name: long-term-project-manager
description: Track multi-day projects, deadlines, progress, dependencies, and next steps. Gives OpenClaw continuity - doesn't just answer questions, it builds. Use when managing ongoing work, resuming projects, or tracking what needs attention.
---

# Long-Term Project Manager (LPM)

Track multi-day projects with full continuity. OpenClaw doesn't just answer - it builds.

## Philosophy

**OpenClaw remembers your goals and pushes them forward.**

No more "what were we doing last week?" LPM maintains project context across sessions.

## Project Structure

Each project has:

```
Project
├── Metadata (name, status, dates)
├── Tasks (the work)
├── Timeline (milestones, deadlines)
├── Dependencies (what blocks what)
├── Resources (files, links)
├── Notes (decisions, context)
└── Progress (what's done/remaining)
```

## Project Status States

| Status | Meaning | Action |
|--------|---------|--------|
| 🔴 **Blocked** | Can't proceed | Needs unblocking |
| 🟡 **In Progress** | Active work | Continue |
| 🟢 **Active** | Next up | Ready to resume |
| ⚪ **Paused** | Not now | Can resume later |
| ✅ **Complete** | Done | Archive |
| ⏸️ **Pending** | Waiting for something | Await dependency |

## Project Definition

### Project Manifest

```yaml
project:
  id: "PROJ-001"
  name: "Avatar 3D Integration"
  description: "Integrate Mixamo 3D avatar into web app"
  status: "in_progress"
  priority: "high"
  
  created: "2026-03-01T10:00:00"
  target_completion: "2026-03-15"
  last_active: "2026-03-08T22:00:00"
  
  # Progress tracking
  progress:
    total_tasks: 10
    completed: 4
    remaining: 6
    percent: 40%
  
  # Tasks (todo items)
  tasks:
    - id: T1
      title: "Download Mixamo Y Bot"
      status: complete
      completed_at: "2026-03-01"
      
    - id: T2
      title: "Export animations"
      status: complete
      completed_at: "2026-03-02"
      
    - id: T3
      title: "Convert FBX to GLB"
      status: blocked
      blocked_by: ["Need Blender"]
      
    - id: T4
      title: "Update HTML viewer"
      status: in_progress
      priority: high
      
    - id: T5
      title: "Test on mobile"
      status: pending
      depends_on: [T4]
  
  # Deadlines
  milestones:
    - name: "Model Ready"
      date: "2026-03-10"
      status: on_track
      
    - name: "Integration Complete"
      date: "2026-03-15"
      status: at_risk
  
  # Blockers
  blockers:
    - id: B1
      description: "Need Blender installed"
      blocking: [T3]
      priority: "remove"
      
    - id: B2
      description: "Waiting for 3D asset files"
      blocking: [T4]
      priority: "medium"
  
  # What needs user input?
  needs_decision:
    - question: "Which animation set to use?"
      options: ["Professional", "Casual"]
      blocking: T4
```

## Project Actions

### Daily Check-In

```
LPM: Checking projects...

Project: Avatar 3D Integration
├── Status: 4/10 tasks (40% complete)
├── Current: Working on T4 - Update HTML viewer
├── Blocked: T3 - Need Blender (B1)
├── Due: Integration Complete in 7 days (at risk)
└── Needs Input: Which animation set?

Next Actions:
1. Work on T4 (in progress)
2. Resolve B1 (install Blender)
3. Decide on animation set
```

### Resume Project

```
User: "Continue my avatar project"

LPM: Resuming "Avatar 3D Integration"

Last worked on: 2 days ago
Status: 4/10 tasks complete

Current focus: T4 - Update HTML viewer
Blocked by: Need to decide animation set first

What's your decision on the animation set?
Options:
1. Professional set (12 animations, 450KB)
2. Casual set (8 animations, 280KB)
3. Both (switchable)
```

### Auto-Prompt on Blockers

```
LPM: Blockers detected in Active projects:

🔴 B1: Need Blender installed
   └─ Blocking: Convert FBX to GLB
   └─ Suggested action: apt install blender

🟡 B2: Waiting for asset files
   └─ Blocking: Update HTML viewer
   └─ User needs to provide files
```

## Dependency Management

### Dependency Graph

```
T1 (Download) ────┐
T2 (Animations) ──┼──→ T3 (Convert) ────→ T5 (Test)
                   │                         ↑
T4 (HTML) ─────────┴───────────────────────┘
```

When T3 is blocked, T5 is blocked.
When T3 completes, T5 becomes unblocked.

### Auto-Dependency Resolution

```python
# When T3 completes
def on_task_complete(task_id):
    dependents = find_dependents(task_id)
    for dep in dependents:
        if all_dependencies_complete(dep):
            unblock_task(dep)
            notify(f"Task {dep} unblocked!")
```

## Timeline View

### Gantt-Style View

```
Week 1 (Mar 1-7)   Week 2 (Mar 8-14)  Week 3 (Mar 15)
┌────────────────┬──────────────────┬──────────────┐
│ ▓▓▓▓ Download  │ ░░░ Integrate    │              │
│ ▓▓▓▓ Export    │ ░░░░ Test        │              │
│ ░░░░ Convert   │                  │              │
└────────────────┴──────────────────┴──────────────┘

▓▓▓ Complete  ░░░ In Progress  ... Planned
```

## Integrations

### Calendar Integration

```yaml
# Events synced to calendar
events:
  - title: "Avatar Project - Milestone: Model Ready"
    date: "2026-03-10"
    reminder: 1 day before
    
  - title: "Avatar Project - Deadline"
    date: "2026-03-15"
    reminder: 3 days before
```

### Decision Log Integration

```
Project: Avatar 3D Integration
Decision: "Use GLB format" (DEC-007)
└─ Links to decision in memory/decisions/
```

### Code Evolution Integration

```
When code changes tracked:
Project: Avatar 3D Integration
└─ EVO-012: Improved HTML viewer loading
```

## Commands

| Command | Action |
|---------|--------|
| "My projects" | List all projects |
| "Status of [project]" | Project summary |
| "Continue [project]" | Resume work |
| "New project: X" | Create project |
| "Block [project]" | Mark as blocked |
| "Complete [task]" | Mark task done |
| "What should I work on?" | Priority queue |
| "Blockers?" | Show what's blocked |
| "Overdue" | Past due items |
| "Due this week" | Time-sensitive |

## Storage

```
memory/lpm/
├── projects/
│   ├── PROJ-001_avatar_3d.json
│   ├── PROJ-002_trading_bot.json
│   └── ...
├── index.json                  # All projects list
├── backlog.md                  # Ideas not started
├── archived/                   # Completed projects
└── templates/                # Project templates
    ├── software_project.json
    ├── research_project.json
    └── trading_project.json
```

## Notifications

### Daily Digest

```
📅 Project Update - 2026-03-08

Active Projects: 3
Overdue: 0
Due Today: 1
Blocked: 1

🔴 Needs Attention:
└─ Avatar 3D: Waiting on Blender install

🟡 In Progress:
├─ Avatar 3D: Update HTML viewer
└─ Trading Bot: Implement strategy

⚪ Due Soon (3 days):
└─ Avatar 3D: Milestone due
```

### Context on Startup

```
Welcome back! Your projects:

🎯 Continue: Avatar 3D (4/10 tasks, due in 7 days)
🌙 Continue: Trading Bot (testing phase)
⏸️ Paused: Research Paper (paused 5 days ago)

What would you like to work on?
```

## Example Projects

### Software Project
```yaml
name: "Trading Bot v3"
type: "software"
workflow: ["design", "code", "test", "deploy"]
tasks:
  - design_strategy
  - code_connector
  - code_logic
  - test_paper
  - test_live
  - deploy
```

### Research Project
```yaml
name: "Solana DEX Comparison"
type: "research"
workflow: ["gather", "analyze", "write", "present"]
tasks:
  - gather_data
  - compare_metrics
  - write_report
  - create_summary
```

### Trading Project
```yaml
name: "Microcap Strategy"
type: "trading"
workflow: ["research", "paper_trade", "live_test", "scale"]
tasks:
  - backtest
  - risk_assessment
  - paper_trade_1week
  - live_deploy
  - monitor
```

## LPM Workflow

### On Daily Heartbeat
```
1. Load all active projects
2. Check for overdue items
3. Check for blockers
4. Notify if attention needed
5. Update progress percentages
```

### On User Login
```
1. Show project summary
2. Highlight next actions
3. Suggest what to work on
4. Surface blockers
5. Remind of deadlines
```

### On Task Completion
```
1. Update task status
2. Recalculate progress
3. Check for unblocked dependents
4. Suggest next task
5. Update project state
```

## Success Metrics

Track LPM effectiveness:
- Projects completed on time
- Blockers resolved speed
- Time to resume dropped projects
- User satisfaction with suggestions

LPM learns from this via ALOE.
