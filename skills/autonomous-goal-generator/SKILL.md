---
name: autonomous-goal-generator
tier: 6
type: ceo-layer
status: active
---

# Autonomous Goal Generator (AGG)

## Overview
**Tier:** 6 (CEO Layer)  
**Purpose:** Creates goals based on opportunities, performance metrics, market conditions, and long-term objectives  
**Architecture:** GoalPool → GoalScorer → GoalPrioritizer → GoalEmitter

## Usage

### CLI Commands

```bash
# Generate template goals (daily/weekly/monthly)
python3 autonomous_goal_generator.py --mode generate

# Prioritize and emit top goals
python3 autonomous_goal_generator.py --mode prioritize

# Generate comprehensive report
python3 autonomous_goal_generator.py --mode report

# Run test suite
python3 autonomous_goal_generator.py --mode test

# Show configuration
python3 autonomous_goal_generator.py --mode config
```

### Programmatic API

```python
from autonomous_goal_generator import AutonomousGoalGenerator, GoalType

# Initialize
agg = AutonomousGoalGenerator()

# Generate from opportunity
opportunity = {
    "title": "New Market",
    "description": "Emerging crypto opportunity",
    "potential_revenue": 1000,
    "estimated_cost": 100,
    "deadline": "2024-12-31T23:59:59"
}
goal = agg.generate_from_opportunity(opportunity)

# Activate goal
agg.activate_goal(goal.id)

# Complete goal
agg.complete_goal(goal.id)

# Get priority report
report = agg.get_report()
```

## Goal Scoring

Goals are scored across 5 dimensions (weights):

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Urgency | 25% | Time sensitivity, deadlines |
| Impact | 25% | Potential benefit/value |
| Feasibility | 20% | Likelihood of success |
| Alignment | 20% | Strategic fit |
| ROI | 10% | Return on investment |

## Event Bus

Events emitted:
- `goal.created` - New goal created
- `goal.priority` - Priority goal identified
- `goal.completed` - Goal marked complete

Events stored in: `memory/autonomous-goal-generator/events.jsonl`

## State Management

- **State file:** `memory/autonomous-goal-generator/state.json`
- **Max active goals:** 10
- **Retention:** 90 days for completed/failed goals
- **Auto-cleanup:** Expired goals purged on each run

## Goal Types

- **Daily:** Routine tasks, health checks
- **Weekly:** Strategy reviews, income analysis
- **Monthly:** Performance audits, expansion planning
- **Quarterly:** Major milestones, strategic pivots
- **Opportunity:** Market-driven goals
- **Maintenance:** System upkeep
- **Strategic:** Long-term objectives

## Configuration

See `--mode config` for current settings. Edit `state.json` to customize templates.