---
name: skill-activation-manager
description: Intelligent skill activation system that wakes up dormant skills, tracks utilization patterns, and creates contextual prompts to use under-utilized capabilities. Maximizes the value of all 17+ skills by ensuring they're actively used.
---

# Skill Activation Manager (SAM)

**Wake up sleeping skills. Maximize your investment.**

SAM monitors skill utilization across the entire ALOE ecosystem, identifies dormant skills, and creates contextual prompts to re-engage them at the right moments.

## Philosophy

**Skills you built but don't use = wasted potential.**

SAM transforms the skill ecosystem from a static set of capabilities into an actively engaged, continuously utilized intelligence network.

## Core Workflow

```
MONITOR (Track usage)
     ↓
IDENTIFY (Find dormant skills)
     ↓
ANALYZE (Why dormant?)
     ↓
PROMPT (Contextual activation)
     ↓
ENGAGE (User interaction)
     ↓
LEARN (via ALOE)
```

## Skill Utilization Tracking

### What SAM Monitors

```yaml
tracking_metrics:
  frequency:
    - last_used: datetime
    - times_used_this_week: int
    - times_used_this_month: int
    - average_uses_per_week: float
    
  recency:
    - days_since_last_use: int
    - user_requests_without_use: int  # User asked for something this skill could do
    
  value:
    - successful_outcomes: int
    - user_satisfaction: score
    - time_saved: minutes
    - value_generated: optional
```

### Dormancy Thresholds

| Status | Criteria | Action |
|--------|----------|--------|
| **Active** | Used in last 7 days | Continue monitoring |
| **Under-utilized** | Last use 7-21 days | Gentle prompting |
| **Dormant** | Last use 21-45 days | Active activation |
| **Forgotten** | No use for 45+ days | Re-onboarding |
| **Candidate for Archive** | No use for 90+ days | Consider removal |

## Contextual Prompts

### How SAM Prompts

**Not:** "Use this skill."
**Instead:** "For this task, [skill] could help by..."

### Prompt Examples

#### Example 1: Context-Optimizer Dormant
```
User: "I've been working on this for 2 hours, getting confused."

SAM Triggers: context-optimizer (dormant 18 days)
Message: 
"Your session is 47 messages long. Want me to summarize what 
we've done so far? The context-optimizer can clarify where 
we are and what's next."

[Summarize] [Continue without]
```

#### Example 2: Decision-Log Dormant
```
User: "Should we use Python or Go for the trading bot?"

SAM Triggers: decision-log (dormant 12 days)
Message:
"This is a significant architectural choice. Want to document 
the trade-offs in the decision-log? It'll help track the 
rationale for future reference."

[Log Decision] [Decide without logging]
```

#### Example 3: LPM Dormant
```
User: "I want to build a crypto scanner. Here's what I need..."

SAM Triggers: long-term-project-manager (dormant 25 days)
Message:
"This sounds like a multi-day project. Want me to create a 
project in LPM to track tasks, deadlines, and progress?"

[Create Project] [Track mentally]
```

#### Example 4: Multiple Skills Dormant
```
User: "Research Solana DEXs for me."

SAM Analyzes: User hasn't used research-synthesizer (15 days), 
              memory-manager (22 days), or ATS (28 days)
Message:
"I can use multiple skills for this:
• research-synthesizer: Multi-source analysis with contradiction detection
• ATS: Trading-specific analysis with risk scoring
• memory-manager: Reference past research

Want the full integrated approach?"

[Full Analysis] [Quick Summary]
```

## Dormancy Analysis

### Why Skills Go Dormant

```yaml
common_reasons:
  forgotten_capability:
    symptom: "User doesn't know skill exists"
    solution: "Skill awareness campaign"
    
  wrong_trigger_pattern:
    symptom: "User says what they want, not the skill name"
    solution: "Semantic trigger expansion"
    
  low_perceived_value:
    symptom: "User used skill once, didn't continue"
    solution: "Demonstrate value with specific examples"
    
  complexity_barrier:
    symptom: "User avoids multi-step skill"
    solution: "Simplified one-click triggers"
    
  satisfied_by_alternative:
    symptom: "User achieves goal through different path"
    solution: "Show skill does it better/faster"
```

### Analysis Report Example

```markdown
## SAM Weekly Analysis: Skills at Risk

### Forgotten Skills (>21 days dormant)
| Skill | Last Used | Dormancy Reason | Activation Strategy |
|-------|-----------|-----------------|---------------------|
| autonomous-workflow-builder | 28 days | Complex invocation | Create one-click template |
| knowledge-graph-engine | 24 days | Low awareness | Demo in next research task |
| tool-orchestrator | 31 days | Alternative patterns | Show parallel execution value |

### Under-utilized Skills (7-21 days)
| Skill | Activations This Week | Potential Increase |
|-------|----------------------|-------------------|
| decision-log | 2 | +300% if added to major choices |
| code-evolution-tracker | 1 | +500% if auto-triggered on edits |
| workspace-organizer | 0 | +∞ if weekly cleanup prompt added |

### Re-engagement Opportunities
- Next crypto research → Suggest research-synthesizer
- Next code refactor → Suggest code-evolution-tracker  
- Next "should I..." → Suggest decision-log
- Next cluttered workspace → Suggest workspace-organizer
```

## Smart Activation Strategies

### Strategy 1: Value-First Prompts

```
❌ Weak: "Want to use the long-term-project-manager?"
✅ Strong: "Want me to track this multi-day project with deadlines and next actions?"
```

### Strategy 2: Comparison Prompts

```
User: "Organize this folder"

SAM Response:
"I can organize this two ways:

A) Basic: Quick file cleanup (30 seconds)
B) Smart: Full analysis + duplicate detection + automatic archiving (2 minutes)

The workspace-organizer skill does option B. Which do you prefer?"
```

### Strategy 3: Outcome-Based Triggers

```python
outcome_triggers = {
    "user seems confused": "context-optimizer",
    "user mentions deadline": "long-term-project-manager",
    "user comparing options": "decision-log",
    "user searching for something": "memory-manager",
    "user writing code": "code-evolution-tracker",
    "user making recurring request": "autonomous-workflow-builder"
}
```

### Strategy 4: Success Story Prompts

```
"By the way, last time you used KGE for research, you said 
'incredibly useful for seeing connections.' Want me to activate 
it for this token analysis too?"
```

## Weekly Skill Audit

### Cron Job: Every Monday 9 AM

```python
def weekly_audit():
    # Generate utilization report
    report = generate_usage_report()
    
    # Identify dormant skills
    dormant = find_skills_not_used(days=14)
    
    # Create activation plan
    action_plan = create_activation_strategy(dormant)
    
    # Deliver to user
    return format_audit_report(report, action_plan)
```

### Audit Report Format

```markdown
# SAM Weekly Skill Audit 📊

## Utilization Summary
| Skill | This Week | Last Month | Trend |
|-------|-----------|------------|-------|
| ATS | 12x | 45x | ↑ 8% |
| AOE | 8x | 32x | ↑ 12% |
| decision-log | 1x | 3x | ↓ 45% ❗ |
| LPM | 2x | 8x | ↓ 30% ⚠️ |
| workspace-organizer | 0x | 1x | ↓ 80% 🔴 |

## Dormant Skills Requiring Attention

### 🔴 Critical (21+ days)
1. **workspace-organizer** (34 days dormant)
   - Value: Could save 5-10 min/week in file management
   - Action: Prompt next time clutter detected

2. **code-evolution-tracker** (27 days dormant)
   - Value: Track improvements across codebase
   - Action: Auto-trigger on file edits

### ⚠️ Warning (14-21 days)
3. **tool-orchestrator** (19 days dormant)
   - Suggest for multi-tool tasks

## Proposed Improvements
- Add auto-trigger: code-evolution-tracker on >5 file edits
- Add contextual trigger: workspace-organizer when folder >50 files
- Create skill shortcuts: Most-used skills get single-word triggers
```

## Integration with Other Skills

```
SAM + ALOE
  → SAM learns which prompts succeed
  → ALOE identifies activation patterns
  → Both improve over time

SAM + SEE
  → SEE identifies underperforming skills
  → SAM activates them contextually
  → Combined = skill optimization

SAM + MAC
  → Complex tasks = multiple dormant skills
  → MAC coordinates activation
  → SAM tracks which multi-skill combos work

SAM + KGE
  → Know what skills relate to what topics
  → "Skills for crypto research" → ATS, AOE, research-synthesizer
```

## Skill-Specific Activation Triggers

```yaml
activation_triggers:
  context-optimizer:
    - session_length > 30 messages
    - user says: "what were we doing?", "remind me", "where are we?"
    - user re-reads file 2+ times
    
  decision-log:
    - user asks: "should we", "what's better", "compare X and Y"
    - multiple options presented to user
    - user says: "let's go with X" (capture the decision)
    
  workspace-organizer:
    - directory > 50 files
    - user says: "cluttered", "disorganized", "clean up"
    - weekly cron
    
  research-synthesizer:
    - user asks for research on topic
    - multiple sources mentioned
    - user needs "comparison" or "analysis"
    
  tool-orchestrator:
    - 3+ tools needed for task
    - dependent operations
    - complex multi-step workflow
    
  code-evolution-tracker:
    - user edits file > 3 times
    - refactoring detected
    - user says: "improved", "optimized", "better version"
    
  memory-manager:
    - user asks: "what did I say about...", "remember...", "last time we..."
    - writing to MEMORY.md
    - searching past context
    
  long-term-project-manager:
    - user mentions deadline, milestone, multi-day
    - project-like language detected
    - "track progress", "what's next"
    
  autonomous-workflow-builder:
    - repetitive tasks detected
    - user says: "every time", "always", " automate"
    - pattern detected in 3+ similar requests
    
  knowledge-graph-engine:
    - research tasks
    - "what's related", "connections", "ecosystem"
    - complex relationships
```

## Commands

| Command | Action |
|---------|--------|
| "Show skill usage" | Utilization dashboard |
| "What skills am I not using?" | Dormant skills list |
| "Wake up [skill]" | Activate specific skill |
| "Skill audit" | Run weekly audit now |
| "Why isn't [skill] being used?" | Dormancy analysis |
| "Suggest skills for [task]" | Contextual recommendations |
| "Skill stats" | Detailed metrics |
| "Optimize my skill usage" | SAM action plan |

## Storage

```
memory/sam/
├── utilization/
│   ├── skill_usage.json        # Tracks all skill usage
│   ├── weekly_reports.json     # Audit reports
│   └── activation_history.json
├── dormancy/
│   ├── dormant_skills.json   # Currently dormant
│   └── dormancy_analysis.json  # Why analysis
├── prompts/
│   ├── prompt_templates.json # Contextual prompts
│   └── prompt_success.json     # What worked
├── config.json
└── strategies/
    └── activation_strategies.json
```

## Implementation

### Skill Usage Tracker
```python
# In each skill execution
def track_skill_usage(skill_name, outcome):
    sam.record_usage(
        skill=skill_name,
        timestamp=now(),
        outcome=outcome,
        context=get_current_context()
    )
```

### Dormancy Checker
```python
def check_dormancy(skill_name):
    last_used = sam.get_last_used(skill_name)
    days_dormant = (now() - last_used).days
    
    if days_dormant > 21:
        sam.flag_for_activation(skill_name)
        sam.analyze_dormancy_reason(skill_name)
```

### Contextual Prompt Generator
```python
def generate_prompt(skill_name, context):
    prompt_template = sam.get_template(skill_name)
    return prompt_template.fill(
        task=context.current_task,
        value=skill_name.value_proposition
    )
```

## Success Metrics

- **Skill Activation Rate:** % of dormant skills successfully re-engaged
- **Utilization Increase:** % increase in under-utilized skills
- **Time to Reactivation:** Avg days from dormant to active
- **Value Realized:** Est. time saved by using dormant skills
- **User Satisfaction:** Feedback on activation prompts

---

**SAM: Every skill you built deserves to be used.** 🧬
