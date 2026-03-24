---
name: suggestion-engine
description: Proactively offer hints, recommendations, and next steps based on context, patterns, and user goals. Learns from accept/reject rates to improve suggestions over time.
---

# Suggestion Engine

**The right hint at the right time.**

The Suggestion Engine analyzes context, user patterns, and current state to proactively offer helpful hints, recommendations, and next steps. It learns from user responses to improve over time.

## Core Philosophy

**Anticipate, don't interrupt.**

Good suggestions:
- Are relevant to current context
- Come at appropriate times
- Respect user focus and availability
- Improve with feedback

## Architecture

```
┌─────────────────────────────────────────┐
│         SUGGESTION ENGINE               │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────┐  ┌──────────────┐    │
│  │   CONTEXT    │  │   PATTERN    │    │
│  │   ANALYZER   │  │   MATCHER    │    │
│  └──────┬───────┘  └──────┬───────┘    │
│         │                 │             │
│         └────────┬────────┘             │
│                  │                      │
│         ┌────────▼────────┐             │
│         │  SUGGESTION     │             │
│         │   GENERATOR     │             │
│         └────────┬────────┘             │
│                  │                      │
│         ┌────────▼────────┐             │
│         │   DELIVERY      │             │
│         │   CONTROLLER    │             │
│         └────────┬────────┘             │
│                  │                      │
│         ┌────────▼────────┐             │
│         │   FEEDBACK    │             │
│         │   LEARNER       │             │
│         └─────────────────┘             │
│                                         │
└─────────────────────────────────────────┘
```

## Suggestion Types

### 1. Contextual Suggestions

**Based on current activity:**
```python
# User is coding
def suggest_while_coding():
    suggestions = [
        "Run tests before committing?",
        "Check git status?",
        "Update documentation?",
        "Take a break (been 2 hours)?"
    ]
    return filter_relevant(suggestions)

# User just finished a task
def suggest_after_completion():
    suggestions = [
        "Shall I log this in MEMORY.md?",
        "Update the project status?",
        "What's next on your list?",
        "Take a moment to celebrate the win?"
    ]
```

**Based on time:**
```python
def suggest_based_on_time():
    hour = datetime.now().hour
    
    if hour == 9:
        return "Morning routine: Check crypto, review calendar?"
    elif hour == 12:
        return "Lunch break soon. Want me to summarize morning progress?"
    elif hour == 17:
        return "End of day approaching. Shall I prepare daily summary?"
    elif hour == 21:
        return "Evening wind-down. Review tomorrow's priorities?"
```

### 2. Pattern-Based Suggestions

**From user behavior:**
```python
# Detected pattern: User always checks git status after coding
def suggest_from_pattern():
    if just_finished_coding() and not checked_git():
        return {
            "suggestion": "Check git status?",
            "confidence": 0.92,
            "reason": "You usually do this after coding sessions"
        }

# Detected pattern: User reviews trades at market close
def suggest_trading_pattern():
    if market_closing_soon() and not reviewed_today():
        return {
            "suggestion": "Review today's trades?",
            "confidence": 0.88,
            "reason": "Daily routine before market close"
        }
```

### 3. Goal-Based Suggestions

**Aligned with active goals:**
```python
def suggest_from_goals():
    active_goals = get_active_goals()
    
    for goal in active_goals:
        if goal.due_soon() and not goal.has_progress():
            return {
                "suggestion": f"Work on '{goal.name}'? Due in {goal.days_left} days",
                "confidence": 0.85,
                "reason": "Goal deadline approaching"
            }
        
        if goal.stalled():
            return {
                "suggestion": f"Resume '{goal.name}'? No progress in {goal.stalled_days} days",
                "confidence": 0.80,
                "reason": "Goal appears stalled"
            }
```

### 4. Skill-Based Suggestions

**Surface relevant skills:**
```python
def suggest_skills():
    context = get_current_context()
    
    # User is researching
    if context.activity == "research":
        return {
            "suggestion": "Use research-synthesizer skill for multi-source analysis?",
            "confidence": 0.90,
            "reason": "You're gathering information from multiple sources"
        }
    
    # User is coding
    if context.activity == "coding":
        return {
            "suggestion": "Use autonomous-code-architect for structured development?",
            "confidence": 0.85,
            "reason": "Complex coding task detected"
        }
```

## Suggestion Scoring

### Relevance Score

```python
def calculate_relevance(suggestion, context):
    score = 0
    
    # Context match
    if suggestion.matches_current_activity():
        score += 40
    
    # Time appropriateness
    if suggestion.is_good_time():
        score += 30
    
    # User preference
    if suggestion.similar_accepted_before():
        score += 20
    
    # Goal alignment
    if suggestion.aligns_with_goals():
        score += 10
    
    return score / 100
```

### Confidence Calculation

```python
def calculate_confidence(suggestion):
    confidence = 0.5  # Base
    
    # Boost if pattern detected
    if suggestion.has_strong_pattern():
        confidence += 0.3
    
    # Boost if similar suggestions accepted
    if suggestion.similar_accepted():
        confidence += 0.15
    
    # Reduce if user rejected similar recently
    if suggestion.similar_rejected_recently():
        confidence -= 0.2
    
    # Reduce if bad timing
    if suggestion.poor_timing():
        confidence -= 0.3
    
    return max(0, min(1, confidence))
```

## Delivery Control

### When to Suggest

```python
class DeliveryController:
    def should_suggest(self, suggestion) -> bool:
        """Decide if suggestion should be delivered now"""
        
        # Don't interrupt focused work
        if self.user_is_focused() and suggestion.priority != 'high':
            return False
        
        # Don't suggest during meetings
        if self.in_meeting():
            return False
        
        # Don't suggest during quiet hours
        if self.is_quiet_hours():
            return False
        
        # Rate limiting
        if self.recent_suggestion_count() > 3:
            return False
        
        # Check confidence threshold
        if suggestion.confidence < 0.6:
            return False
        
        return True
    
    def choose_timing(self, suggestion) -> datetime:
        """Choose optimal delivery time"""
        if suggestion.urgency == 'immediate':
            return datetime.now()
        elif suggestion.urgency == 'soon':
            return self.next_natural_break()
        else:
            return self.optimal_time_for_user()
```

### How to Present

```python
class SuggestionPresenter:
    def format_suggestion(self, suggestion) -> str:
        """Format suggestion for display"""
        
        if suggestion.confidence > 0.9:
            prefix = "💡"
        elif suggestion.confidence > 0.7:
            prefix = "🤔"
        else:
            prefix = "💭"
        
        return f"""
{prefix} {suggestion.text}

[Yes] [No] [Remind me later]

_Why: {suggestion.reason}_
"""
```

## Feedback Learning

### Track Outcomes

```python
class FeedbackLearner:
    def __init__(self):
        self.suggestion_history = []
    
    def record_accept(self, suggestion):
        """User accepted suggestion"""
        self.suggestion_history.append({
            'suggestion': suggestion,
            'outcome': 'accepted',
            'timestamp': datetime.now()
        })
        
        # Boost similar suggestions
        self.boost_pattern(suggestion.pattern)
    
    def record_reject(self, suggestion):
        """User rejected suggestion"""
        self.suggestion_history.append({
            'suggestion': suggestion,
            'outcome': 'rejected',
            'timestamp': datetime.now()
        })
        
        # Reduce similar suggestions
        self.reduce_pattern(suggestion.pattern)
    
    def record_ignore(self, suggestion):
        """User ignored suggestion"""
        self.suggestion_history.append({
            'suggestion': suggestion,
            'outcome': 'ignored',
            'timestamp': datetime.now()
        })
        
        # Slight reduction
        self.slightly_reduce_pattern(suggestion.pattern)
```

### Pattern Learning

```python
def learn_from_feedback():
    """Extract patterns from feedback"""
    
    # What types of suggestions are accepted?
    accepted_types = analyze_accepted()
    
    # What timing works best?
    best_times = analyze_timing()
    
    # What context leads to acceptance?
    good_contexts = analyze_contexts()
    
    # Update suggestion model
    update_model(
        accepted_types=accepted_types,
        best_times=best_times,
        good_contexts=good_contexts
    )
```

## Implementation

### Core Engine

```python
class SuggestionEngine:
    def __init__(self):
        self.context_analyzer = ContextAnalyzer()
        self.pattern_matcher = PatternMatcher()
        self.generator = SuggestionGenerator()
        self.delivery = DeliveryController()
        self.learner = FeedbackLearner()
    
    def generate_suggestions(self) -> List[Suggestion]:
        """Generate relevant suggestions"""
        context = self.context_analyzer.analyze()
        patterns = self.pattern_matcher.find_patterns(context)
        
        suggestions = []
        
        # Generate from patterns
        for pattern in patterns:
            suggestion = self.generator.from_pattern(pattern, context)
            if suggestion:
                suggestions.append(suggestion)
        
        # Generate from context
        context_suggestions = self.generator.from_context(context)
        suggestions.extend(context_suggestions)
        
        # Generate from goals
        goal_suggestions = self.generator.from_goals(context)
        suggestions.extend(goal_suggestions)
        
        # Score and filter
        for suggestion in suggestions:
            suggestion.relevance = self.calculate_relevance(suggestion, context)
            suggestion.confidence = self.calculate_confidence(suggestion)
        
        # Sort by score
        suggestions.sort(key=lambda s: s.relevance * s.confidence, reverse=True)
        
        return suggestions[:5]  # Top 5
    
    def offer_suggestion(self, suggestion):
        """Offer suggestion to user"""
        if self.delivery.should_suggest(suggestion):
            formatted = self.presenter.format(suggestion)
            send_to_user(formatted)
            return True
        return False
    
    def handle_response(self, suggestion, response):
        """Handle user response to suggestion"""
        if response == 'accept':
            self.learner.record_accept(suggestion)
            execute_suggestion(suggestion)
        elif response == 'reject':
            self.learner.record_reject(suggestion)
        elif response == 'snooze':
            self.reschedule_suggestion(suggestion)
```

## Usage Examples

### Example 1: Coding Session
```
User: [coding for 2 hours]

Suggestion Engine:
- Context: Coding session, no commits
- Pattern: Usually commits every hour
- Confidence: 85%

💡 Commit your changes?
You've been coding for 2 hours without committing.

[Commit now] [Remind in 30 min] [Dismiss]

_Why: You usually commit hourly_
```

### Example 2: End of Day
```
17:00 - User wrapping up

Suggestion Engine:
- Context: End of work day
- Pattern: Daily summary requested at 5pm
- Confidence: 90%

💡 Prepare daily summary?
Shall I summarize what you accomplished today?

[Yes] [No]

_Why: Daily routine at this time_
```

### Example 3: Stalled Project
```
Project "Trading Bot v2" - No activity for 5 days

Suggestion Engine:
- Context: Project stalled
- Pattern: Usually resumes stalled projects when reminded
- Confidence: 75%

🤔 Resume Trading Bot v2?
No progress in 5 days. Want to pick it back up?

[Yes] [View project] [Dismiss]

_Why: Project appears stalled_
```

### Example 4: Skill Suggestion
```
User: "Research Solana DEXs"

Suggestion Engine:
- Context: Multi-source research
- Pattern: Research tasks often benefit from synthesis
- Confidence: 88%

💡 Use research-synthesizer skill?
This will help you gather and synthesize information from multiple sources.

[Use skill] [No thanks]

_Why: You're gathering information from multiple sources_
```

## Configuration

```yaml
# suggestion_engine.yaml

suggestion_types:
  contextual: true
  pattern_based: true
  goal_based: true
  skill_based: true

delivery:
  max_per_hour: 5
  min_interval: 10_minutes
  quiet_hours:
    start: "22:00"
    end: "08:00"
  
  thresholds:
    high_confidence: 0.8
    medium_confidence: 0.6
    low_confidence: 0.4

learning:
  pattern_decay: 30_days
  feedback_weight: 0.1
  min_samples: 3

exclusions:
  - when_in_meeting
  - when_focus_mode
  - when_do_not_disturb
```

## Storage

```
memory/suggestion_engine/
├── patterns/
│   ├── user_patterns.json
│   ├── accepted_patterns.json
│   └── rejected_patterns.json
├── suggestions/
│   ├── suggestion_history.jsonl
│   └── active_suggestions.json
├── feedback/
│   ├── accept_log.jsonl
│   ├── reject_log.jsonl
│   └── ignore_log.jsonl
├── model/
│   ├── relevance_weights.json
│   └── timing_preferences.json
└── config.yaml
```

## Commands

| Command | Action |
|---------|--------|
| "Suggest something" | Generate suggestions now |
| "What should I do next?" | Context-aware suggestions |
| "Suggestion status" | Show active suggestions |
| "Pause suggestions" | Stop proactive suggestions |
| "Resume suggestions" | Re-enable |
| "Suggestion accuracy" | Show accept/reject rates |
| "Learn my preferences" | Analyze feedback |

## Integration

### With Predictive Engine
```python
# Get predictions
predictions = predictive_engine.predict()

# Convert to suggestions
for prediction in predictions:
    suggestion = convert_prediction_to_suggestion(prediction)
    suggestion_engine.offer(suggestion)
```

### With ALOE
```python
# Learn from outcomes
aloe.observe(
    action="suggestion_offered",
    outcome=user_response,
    context=suggestion.context
)
```

### With Event Bus
```python
# Listen for context changes
bus.subscribe('context.changed', on_context_change)

def on_context_change(event):
    suggestions = suggestion_engine.generate_suggestions()
    for suggestion in suggestions:
        suggestion_engine.offer_suggestion(suggestion)
```

---

**The Suggestion Engine: The right hint at the right time.** 💡
