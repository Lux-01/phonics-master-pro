---
name: outcome-tracker
description: Track outcomes of all tasks, actions, and suggestions. Connects to ALOE for continuous learning. Measures success, failure, and impact to improve future performance.
---

# Outcome Tracker

**Track everything. Learn from everything.**

The Outcome Tracker logs results from every task, action, and suggestion, creating a rich dataset for continuous improvement through ALOE.

## Core Philosophy

**You can't improve what you don't measure.**

Every action has an outcome. Track it, learn from it, get better.

## Architecture

```
┌─────────────────────────────────────────┐
│         OUTCOME TRACKER                 │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────┐  ┌──────────────┐    │
│  │   ACTION     │  │   OUTCOME    │    │
│  │   LOGGER     │  │   ANALYZER   │    │
│  └──────┬───────┘  └──────┬───────┘    │
│         │                 │             │
│         └────────┬────────┘             │
│                  │                      │
│         ┌────────▼────────┐             │
│         │   METRICS      │             │
│         │   CALCULATOR   │             │
│         └────────┬────────┘             │
│                  │                      │
│         ┌────────▼────────┐             │
│         │   ALOE         │             │
│         │   FEEDER       │             │
│         └─────────────────┘             │
│                                         │
└─────────────────────────────────────────┘
```

## What to Track

### 1. Task Outcomes

```python
class TaskOutcome:
    def __init__(self):
        self.task_id = generate_id()
        self.description = ""
        self.start_time = None
        self.end_time = None
        self.status = None  # success, failure, partial
        self.tools_used = []
        self.errors = []
        self.user_satisfaction = None
        self.time_saved = None
```

**Example:**
```json
{
  "task_id": "TASK-2026-001",
  "description": "Build Solana trading bot",
  "start_time": "2026-03-08T22:00:00",
  "end_time": "2026-03-09T00:30:00",
  "status": "success",
  "tools_used": ["write", "edit", "exec", "web_fetch"],
  "files_created": ["trading_bot.py", "config.json"],
  "errors": [],
  "user_satisfaction": 5,
  "time_saved_estimate": 120
}
```

### 2. Suggestion Outcomes

```python
class SuggestionOutcome:
    def __init__(self):
        self.suggestion_id = ""
        self.suggestion_text = ""
        self.context = {}
        self.user_response = None  # accept, reject, ignore
        self.outcome = None  # what happened after
```

**Example:**
```json
{
  "suggestion_id": "SUG-2026-045",
  "suggestion_text": "Commit your changes?",
  "context": {
    "activity": "coding",
    "duration": "2 hours",
    "uncommitted_changes": 5
  },
  "user_response": "accept",
  "outcome": "changes_committed_successfully",
  "time_to_response": 30
}
```

### 3. Prediction Outcomes

```python
class PredictionOutcome:
    def __init__(self):
        self.prediction_id = ""
        self.predicted_need = ""
        self.confidence = 0.0
        self.actual_outcome = None  # correct, incorrect, unclear
        self.user_feedback = None
```

**Example:**
```json
{
  "prediction_id": "PRED-2026-089",
  "predicted_need": "crypto_portfolio_check",
  "confidence": 0.92,
  "timeframe": "5_minutes",
  "actual_outcome": "correct",
  "user_action": "checked_portfolio",
  "time_to_action": 180
}
```

### 4. Alert Outcomes

```python
class AlertOutcome:
    def __init__(self):
        self.alert_id = ""
        self.alert_type = ""
        self.priority = ""
        self.user_response_time = None
        self.action_taken = None
        self.was_useful = None
```

**Example:**
```json
{
  "alert_id": "ALERT-2026-234",
  "alert_type": "price_spike",
  "priority": "high",
  "user_response_time": 45,
  "action_taken": "reviewed_and_traded",
  "was_useful": true,
  "profit_loss": 150
}
```

### 5. Skill Usage Outcomes

```python
class SkillOutcome:
    def __init__(self):
        self.skill_name = ""
        self.task_complexity = 0
        self.execution_time = 0
        self.success_rate = 0.0
        self.user_rating = None
```

**Example:**
```json
{
  "skill_name": "autonomous-code-architect",
  "task_complexity": 8,
  "execution_time": 1800,
  "success_rate": 1.0,
  "user_rating": 5,
  "bugs_found": 0,
  "refactors_needed": 0
}
```

## Outcome Analysis

### Success Metrics

```python
class MetricsCalculator:
    def calculate_task_success_rate(self, timeframe='30d'):
        """Calculate success rate for tasks"""
        tasks = self.get_tasks(timeframe)
        
        total = len(tasks)
        successful = len([t for t in tasks if t.status == 'success'])
        
        return successful / total if total > 0 else 0
    
    def calculate_suggestion_acceptance_rate(self):
        """Calculate how often suggestions are accepted"""
        suggestions = self.get_suggestions()
        
        total = len(suggestions)
        accepted = len([s for s in suggestions if s.user_response == 'accept'])
        
        return accepted / total if total > 0 else 0
    
    def calculate_prediction_accuracy(self):
        """Calculate prediction accuracy"""
        predictions = self.get_predictions()
        
        total = len(predictions)
        correct = len([p for p in predictions if p.actual_outcome == 'correct'])
        
        return correct / total if total > 0 else 0
    
    def calculate_time_saved(self):
        """Calculate total time saved"""
        outcomes = self.get_all_outcomes()
        
        return sum(o.time_saved for o in outcomes if o.time_saved)
```

### Pattern Extraction

```python
class PatternExtractor:
    def extract_success_patterns(self):
        """Find patterns in successful outcomes"""
        successful = self.get_successful_outcomes()
        
        patterns = {
            'tools_used': self.find_common_tools(successful),
            'approaches': self.find_common_approaches(successful),
            'conditions': self.find_common_conditions(successful),
            'timing': self.find_optimal_timing(successful)
        }
        
        return patterns
    
    def extract_failure_patterns(self):
        """Find patterns in failed outcomes"""
        failed = self.get_failed_outcomes()
        
        patterns = {
            'common_errors': self.find_common_errors(failed),
            'risk_factors': self.find_risk_factors(failed),
            'warning_signs': self.find_warning_signs(failed)
        }
        
        return patterns
    
    def find_correlations(self):
        """Find correlations between inputs and outcomes"""
        # Example: Does task complexity correlate with success?
        # Example: Do certain tools lead to better outcomes?
        pass
```

## ALOE Integration

### Feed Outcomes to ALOE

```python
class ALOEFeeder:
    def feed_outcome(self, outcome):
        """Send outcome to ALOE for learning"""
        
        # Convert outcome to observation
        observation = {
            'action': outcome.action,
            'context': outcome.context,
            'outcome': outcome.status,
            'metrics': {
                'time_taken': outcome.duration,
                'tools_used': outcome.tools_used,
                'errors': outcome.errors
            }
        }
        
        # Send to ALOE
        aloe.observe(**observation)
    
    def feed_batch(self, outcomes):
        """Send batch of outcomes"""
        for outcome in outcomes:
            self.feed_outcome(outcome)
```

### Learn from Patterns

```python
def update_aloe_patterns():
    """Extract patterns and feed to ALOE"""
    
    # Success patterns
    success_patterns = pattern_extractor.extract_success_patterns()
    for pattern in success_patterns:
        aloe.learn_pattern(
            pattern_type='success',
            pattern=pattern,
            confidence=pattern.confidence
        )
    
    # Failure patterns
    failure_patterns = pattern_extractor.extract_failure_patterns()
    for pattern in failure_patterns:
        aloe.learn_pattern(
            pattern_type='failure',
            pattern=pattern,
            confidence=pattern.confidence
        )
```

## Implementation

### Core Tracker

```python
class OutcomeTracker:
    def __init__(self):
        self.storage = OutcomeStorage()
        self.analyzer = OutcomeAnalyzer()
        self.aloe_feeder = ALOEFeeder()
    
    def start_tracking(self, task_description):
        """Start tracking a new task"""
        outcome = TaskOutcome()
        outcome.task_id = generate_id()
        outcome.description = task_description
        outcome.start_time = datetime.now()
        
        self.storage.store(outcome)
        return outcome.task_id
    
    def end_tracking(self, task_id, status, **kwargs):
        """End tracking a task"""
        outcome = self.storage.get(task_id)
        outcome.end_time = datetime.now()
        outcome.status = status
        
        for key, value in kwargs.items():
            setattr(outcome, key, value)
        
        self.storage.update(outcome)
        
        # Feed to ALOE
        self.aloe_feeder.feed_outcome(outcome)
        
        return outcome
    
    def track_suggestion(self, suggestion, response):
        """Track suggestion outcome"""
        outcome = SuggestionOutcome()
        outcome.suggestion_id = suggestion.id
        outcome.suggestion_text = suggestion.text
        outcome.user_response = response
        outcome.timestamp = datetime.now()
        
        self.storage.store(outcome)
        self.aloe_feeder.feed_outcome(outcome)
    
    def track_prediction(self, prediction, actual):
        """Track prediction accuracy"""
        outcome = PredictionOutcome()
        outcome.prediction_id = prediction.id
        outcome.predicted_need = prediction.need
        outcome.confidence = prediction.confidence
        outcome.actual_outcome = actual
        
        self.storage.store(outcome)
        self.aloe_feeder.feed_outcome(outcome)
    
    def get_metrics(self, timeframe='30d'):
        """Get outcome metrics"""
        return self.analyzer.calculate_metrics(timeframe)
```

## Usage Examples

### Example 1: Task Tracking
```python
# Start tracking
task_id = outcome_tracker.start_tracking("Build trading bot")

try:
    # Do the work
    build_trading_bot()
    
    # Success
    outcome_tracker.end_tracking(
        task_id=task_id,
        status='success',
        files_created=['bot.py', 'config.json'],
        user_satisfaction=5
    )
except Exception as e:
    # Failure
    outcome_tracker.end_tracking(
        task_id=task_id,
        status='failure',
        errors=[str(e)]
    )
```

### Example 2: Automatic Tracking
```python
@track_outcomes
def autonomous_task(task_description):
    """Decorator automatically tracks outcomes"""
    # Task execution
    pass

# Usage
result = autonomous_task("Research Solana DEXs")
# Outcome automatically logged
```

### Example 3: Metrics Dashboard
```python
# Get metrics
metrics = outcome_tracker.get_metrics(timeframe='7d')

print(f"""
📊 Outcome Metrics (Last 7 Days)

Task Success Rate: {metrics.task_success_rate:.1%}
Suggestion Acceptance: {metrics.suggestion_acceptance:.1%}
Prediction Accuracy: {metrics.prediction_accuracy:.1%}
Time Saved: {metrics.time_saved} minutes

Top Success Patterns:
{metrics.top_patterns}

Areas for Improvement:
{metrics.improvement_areas}
""")
```

## Configuration

```yaml
# outcome_tracker.yaml

tracking:
  auto_track_tasks: true
  auto_track_suggestions: true
  auto_track_predictions: true
  
storage:
  format: jsonl
  retention: 90_days
  compression: true

aloe_integration:
  enabled: true
  batch_size: 10
  flush_interval: 300  # 5 minutes

metrics:
  calculate_daily: true
  report_weekly: true
  
privacy:
  anonymize: false
  exclude_sensitive: true
```

## Storage

```
memory/outcome_tracker/
├── outcomes/
│   ├── tasks/
│   │   └── tasks.jsonl
│   ├── suggestions/
│   │   └── suggestions.jsonl
│   ├── predictions/
│   │   └── predictions.jsonl
│   └── alerts/
│       └── alerts.jsonl
├── metrics/
│   ├── daily_metrics.json
│   └── weekly_reports.json
├── patterns/
│   ├── success_patterns.json
│   └── failure_patterns.json
└── config.yaml
```

## Commands

| Command | Action |
|---------|--------|
| "Track this task" | Start tracking current task |
| "Task complete" | Mark task as complete |
| "Show outcomes" | Display outcome summary |
| "Outcome metrics" | Show detailed metrics |
| "Learn from outcomes" | Feed patterns to ALOE |
| "Export outcomes" | Export data for analysis |

## Integration

### With All Skills
```python
# Every skill reports outcomes
skill.execute()
outcome_tracker.track_skill_usage(skill, result)
```

### With ALOE
```python
# Continuous learning
outcome_tracker.feed_to_aloe()
aloe.learn_from_outcomes()
```

### With Event Bus
```python
# Listen for events
bus.subscribe('task.completed', on_task_complete)
bus.subscribe('suggestion.responded', on_suggestion_response)
```

---

**The Outcome Tracker: Measure everything, learn everything.** 📊
