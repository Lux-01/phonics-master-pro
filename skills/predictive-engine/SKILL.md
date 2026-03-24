---
name: predictive-engine
description: Anticipate user needs before they ask. Analyzes patterns from memory, calendar, and behavior to predict what the user will need next and proactively prepare or suggest actions.
---

# Predictive Engine

**Know what the user needs before they ask.**

The Predictive Engine analyzes temporal patterns, user behavior, and contextual signals to anticipate needs and proactively prepare solutions.

## Core Philosophy

**From reactive to anticipatory.**

Instead of waiting for commands, the Predictive Engine:
- Learns user routines and preferences
- Detects patterns in behavior
- Predicts upcoming needs
- Prepares solutions in advance
- Offers proactive suggestions

## Architecture

```
┌─────────────────────────────────────────┐
│         PREDICTIVE ENGINE               │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────┐  ┌──────────────┐    │
│  │   PATTERN    │  │   CONTEXT    │    │
│  │   ANALYZER   │  │   GATHERER   │    │
│  └──────┬───────┘  └──────┬───────┘    │
│         │                 │             │
│         └────────┬────────┘             │
│                  │                      │
│         ┌────────▼────────┐             │
│         │  PREDICTION     │             │
│         │   GENERATOR     │             │
│         └────────┬────────┘             │
│                  │                      │
│         ┌────────▼────────┐             │
│         │   SUGGESTION    │             │
│         │    EMITTER      │             │
│         └─────────────────┘             │
│                                         │
└─────────────────────────────────────────┘
```

## Pattern Types

### 1. Temporal Patterns

**Daily Routines:**
```python
# Detected from memory logs
morning_routine = {
    "time": "08:00-09:00",
    "actions": ["check_crypto", "review_calendar", "check_emails"],
    "confidence": 0.85
}
```

**Weekly Patterns:**
```python
weekly_patterns = {
    "monday": ["week_planning", "income_review"],
    "friday": ["week_summary", "next_week_prep"],
    "sunday": ["strategy_review"]
}
```

**Project-Based:**
```python
project_patterns = {
    "trading_bot": {
        "after_market_hours": "review_trades",
        "before_market": "check_signals",
        "weekend": "backtest_strategies"
    }
}
```

### 2. Contextual Patterns

**Location-Based:**
```python
location_patterns = {
    "home": ["deep_work", "coding", "trading"],
    "commute": ["quick_checks", "messaging"],
    "office": ["meetings", "collaboration"]
}
```

**Device-Based:**
```python
device_patterns = {
    "desktop": ["heavy_coding", "research", "multi_task"],
    "mobile": ["quick_responses", "alerts", "monitoring"],
    "tablet": ["reading", "review", "light_work"]
}
```

**Time-Based:**
```python
time_context = {
    "early_morning": "focus_work",
    "midday": "collaboration",
    "evening": "review_planning",
    "late_night": "monitoring_only"
}
```

### 3. Event-Driven Patterns

**Calendar Triggers:**
```python
calendar_patterns = {
    "15_min_before_meeting": "send_reminder_prep",
    "meeting_ended": "capture_action_items",
    "end_of_day": "daily_summary"
}
```

**System Events:**
```python
system_patterns = {
    "high_cpu_usage": "suggest_optimization",
    "low_disk_space": "cleanup_suggestion",
    "new_email_urgent": "immediate_alert"
}
```

## Prediction Generation

### Confidence Scoring

```python
class Prediction:
    def __init__(self, need, confidence, timeframe, context):
        self.need = need              # What user will need
        self.confidence = confidence  # 0.0 - 1.0
        self.timeframe = timeframe    # When (minutes/hours)
        self.context = context        # Why this prediction
        self.prepared = False         # Have we prepared?

# Example predictions
predictions = [
    Prediction(
        need="crypto_portfolio_check",
        confidence=0.92,
        timeframe="5_minutes",
        context="Daily 8:30 AM routine, market just opened"
    ),
    Prediction(
        need="meeting_prep",
        confidence=0.78,
        timeframe="10_minutes", 
        context="Calendar event in 15 min, usually reviews docs before"
    )
]
```

### Prediction Sources

| Source | Weight | Example |
|--------|--------|---------|
| Historical patterns | 40% | "User checks crypto at 8:30 daily" |
| Calendar events | 25% | "Meeting in 15 min" |
| Current context | 20% | "Just finished task X" |
| Time of day | 10% | "Morning = planning time" |
| Recent activity | 5% | "Been coding for 2 hours" |

## Proactive Actions

### Action Types

**1. Prepare Information**
```python
def prepare_portfolio_summary():
    """Before user asks, fetch and format data"""
    data = {
        "prices": fetch_crypto_prices(),
        "changes_24h": calculate_changes(),
        "alerts": check_thresholds(),
        "news": get_relevant_news()
    }
    return format_summary(data)
```

**2. Suggest Next Action**
```python
def suggest_next_action():
    """Based on current state, suggest what to do"""
    if time_for_daily_review():
        return "Shall I prepare your daily review?"
    elif project_due_soon():
        return "Project X is due tomorrow. Want to review progress?"
```

**3. Auto-Execute (Low Risk)**
```python
def auto_execute_safe():
    """Actions that are safe to do without asking"""
    if should_refresh_data():
        refresh_cache()  # Safe, no side effects
    if should_compact_memory():
        compact_old_sessions()  # Maintenance
```

**4. Alert on Anomaly**
```python
def alert_on_anomaly():
    """Detect unusual patterns and alert"""
    if missed_daily_routine():
        return "You usually check crypto by now. Market is volatile today."
    if unusual_activity():
        return "Unusual pattern detected: [explanation]"
```

## Implementation

### Core Classes

```python
class PredictiveEngine:
    def __init__(self):
        self.pattern_db = PatternDatabase()
        self.user_model = UserBehaviorModel()
        self.context_gatherer = ContextGatherer()
        self.prediction_queue = []
    
    def analyze_patterns(self):
        """Mine patterns from memory and logs"""
        return self.pattern_db.extract_patterns()
    
    def generate_predictions(self) -> List[Prediction]:
        """Generate predictions based on patterns + context"""
        patterns = self.analyze_patterns()
        context = self.context_gatherer.gather()
        
        predictions = []
        for pattern in patterns:
            if pattern.matches(context):
                pred = Prediction(
                    need=pattern.predicted_need,
                    confidence=pattern.confidence * context.relevance,
                    timeframe=pattern.typical_timing,
                    context=pattern.explanation
                )
                predictions.append(pred)
        
        return sorted(predictions, key=lambda p: p.confidence, reverse=True)
    
    def act_on_predictions(self, predictions: List[Prediction]):
        """Decide what to do with predictions"""
        for pred in predictions:
            if pred.confidence > 0.9:
                # High confidence - prepare silently
                self.prepare_solution(pred)
            elif pred.confidence > 0.7:
                # Medium confidence - suggest proactively
                self.proactive_suggestion(pred)
            elif pred.confidence > 0.5:
                # Low confidence - just log
                self.log_prediction(pred)
```

### Pattern Database

```python
class PatternDatabase:
    def __init__(self):
        self.patterns = []
        self.load_from_memory()
    
    def extract_patterns(self):
        """Mine patterns from historical data"""
        patterns = []
        
        # Temporal patterns
        patterns.extend(self.mine_temporal_patterns())
        
        # Sequential patterns
        patterns.extend(self.mine_sequential_patterns())
        
        # Contextual patterns
        patterns.extend(self.mine_contextual_patterns())
        
        return patterns
    
    def mine_temporal_patterns(self):
        """Find time-based patterns"""
        # Example: "User checks email at 9am daily"
        pass
    
    def mine_sequential_patterns(self):
        """Find action sequences"""
        # Example: "After coding session, user reviews git status"
        pass
    
    def mine_contextual_patterns(self):
        """Find context-based patterns"""
        # Example: "When market volatile, user checks prices hourly"
        pass
```

## Usage Examples

### Example 1: Morning Routine
```
08:25 AM - Prediction Engine detects:
- Pattern: "Daily crypto check at 08:30"
- Confidence: 92%
- Context: Market just opened, volatile night

Action:
1. Silently fetch portfolio data
2. Check for alerts
3. Prepare summary

08:30 AM - User opens Telegram:
[Proactive message]
"Good morning! Market update ready:
• SOL: +5.2% overnight
• Your positions: +2.1%
• 2 new A-grade signals detected

[View Full Report] [Dismiss]"
```

### Example 2: Meeting Preparation
```
09:45 AM - Calendar event at 10:00 AM

Prediction Engine:
- Pattern: "Usually reviews docs 10 min before"
- Confidence: 78%
- Context: Meeting with external client

Action:
09:45 AM - Proactive message:
"Meeting with Client X in 15 minutes.

Prepared:
• Last conversation summary
• Their current project status
• Open action items (3)

[View Prep] [Dismiss]"
```

### Example 3: Anomaly Detection
```
Pattern: "Check crypto every 2 hours during market hours"

Current: 6 hours since last check
Market: High volatility (+15% BTC)

Prediction Engine:
- Anomaly: Missed routine during volatile market
- Confidence: 85%
- Urgency: High

Action:
"⚠️ Market Alert: BTC +15% in last 6 hours
You usually check during volatile periods.

[View Market] [Dismiss]"
```

## Integration

### With MEMORY.md
```python
# Read user patterns
patterns = memory_search("daily routine")
patterns += memory_search("usual schedule")
```

### With Calendar
```python
# Check upcoming events
events = get_calendar_events(hours=2)
for event in events:
    if event.starts_soon():
        predict_meeting_prep(event)
```

### With ALOE
```python
# Learn from predictions
aloe.observe(
    action="proactive_suggestion",
    outcome=user_response,
    context=prediction.context
)
```

## Configuration

```yaml
# predictive_engine.yaml

prediction_thresholds:
  auto_prepare: 0.9    # Prepare silently
  proactive_suggest: 0.7  # Suggest to user
  log_only: 0.5        # Just track

learning:
  pattern_decay: 30_days  # Forget old patterns
  min_occurrences: 3      # Need 3+ to form pattern
  confidence_boost: 0.1   # Increase on success

limits:
  max_predictions_per_hour: 5
  min_time_between_suggestions: 30_minutes
  quiet_hours: ["23:00", "07:00"]
```

## Storage

```
memory/predictive_engine/
├── patterns/
│   ├── temporal_patterns.json
│   ├── sequential_patterns.json
│   └── contextual_patterns.json
├── predictions/
│   ├── active_predictions.json
│   └── prediction_history.jsonl
├── user_model/
│   ├── behavior_profile.json
│   └── preference_weights.json
└── config.yaml
```

## Commands

| Command | Action |
|---------|--------|
| "Predict my needs" | Generate predictions now |
| "Learn my patterns" | Analyze and store patterns |
| "Prediction status" | Show active predictions |
| "Pause predictions" | Stop proactive suggestions |
| "Resume predictions" | Re-enable |
| "Prediction accuracy" | Show hit/miss rate |

## Success Metrics

- **Prediction accuracy:** % of predictions that were correct
- **User acceptance:** % of suggestions that were accepted
- **Time saved:** Estimated minutes saved per day
- **Proactive actions:** Number of actions taken without asking
- **Pattern confidence:** Average confidence of predictions

---

**The Predictive Engine: Making OpenClaw truly proactive.** 🔮
