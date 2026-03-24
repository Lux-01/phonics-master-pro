---
name: user-behavior-model
description: Build and maintain a deep model of user behavior, preferences, routines, and patterns. Enables personalized predictions, proactive suggestions, and adaptive responses.
---

# User Behavior Model

**Know the user better than they know themselves.**

The User Behavior Model builds a comprehensive profile of the user including preferences, routines, communication style, and behavioral patterns. This enables deeply personalized and proactive assistance.

## Core Philosophy

**Personalization at scale.**

The more we understand the user, the better we can:
- Anticipate their needs
- Adapt to their style
- Respect their preferences
- Optimize their experience

## Architecture

```
┌─────────────────────────────────────────┐
│      USER BEHAVIOR MODEL                │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────┐  ┌──────────────┐    │
│  │   BEHAVIOR   │  │   PREFERENCE │    │
│  │   TRACKER    │  │   LEARNER    │    │
│  └──────┬───────┘  └──────┬───────┘    │
│         │                 │             │
│         └────────┬────────┘             │
│                  │                      │
│         ┌────────▼────────┐             │
│         │   USER          │             │
│         │   PROFILE       │             │
│         │   BUILDER       │             │
│         └────────┬────────┘             │
│                  │                      │
│         ┌────────▼────────┐             │
│         │   PERSONALIZED  │             │
│         │   RESPONSE      │             │
│         │   GENERATOR     │             │
│         └─────────────────┘             │
│                                         │
└─────────────────────────────────────────┘
```

## Model Components

### 1. Demographics

```python
demographics = {
    "name": "Tem",
    "timezone": "Australia/Sydney",
    "location": "Sydney",
    "language": "English",
    "communication_channels": ["Telegram", "Discord"],
    "primary_device": "desktop"
}
```

### 2. Preferences

```python
preferences = {
    "communication": {
        "style": "concise",  # concise, detailed, casual, formal
        "frequency": "as_needed",  # frequent, as_needed, minimal
        "tone": "direct",  # direct, friendly, professional
        "emoji_usage": "moderate"  # none, minimal, moderate, heavy
    },
    
    "notifications": {
        "urgent": "immediate",
        "important": "batched",
        "routine": "digest",
        "quiet_hours": ["23:00", "07:00"]
    },
    
    "work_style": {
        "focus_time": "09:00-12:00",
        "break_frequency": "hourly",
        "preferred_tasks": ["coding", "research", "trading"],
        "avoid_tasks": ["meetings", "admin"]
    },
    
    "decision_making": {
        "speed": "balanced",  # fast, balanced, deliberate
        "risk_tolerance": "moderate",  # conservative, moderate, aggressive
        "information_needed": "medium"  # minimal, medium, exhaustive
    }
}
```

### 3. Routines

```python
routines = {
    "daily": {
        "08:00": "check_crypto",
        "09:00": "start_deep_work",
        "12:00": "lunch_break",
        "17:00": "daily_summary",
        "21:00": "evening_wind_down"
    },
    
    "weekly": {
        "monday": "week_planning",
        "friday": "week_review",
        "sunday": "strategy_session"
    },
    
    "project_based": {
        "new_project": ["plan", "research", "prototype"],
        "ongoing": ["execute", "review", "iterate"],
        "completion": ["test", "document", "deploy"]
    }
}
```

### 4. Behavioral Patterns

```python
behavioral_patterns = {
    "response_times": {
        "telegram": "5_minutes",
        "urgent": "immediate",
        "non_urgent": "when_convenient"
    },
    
    "task_patterns": {
        "prefers_parallel": True,
        "batch_similar": True,
        "deep_focus_duration": "3_hours",
        "context_switch_tolerance": "medium"
    },
    
    "interaction_patterns": {
        "asks_for_confirmation": "sometimes",
        "prefers_examples": True,
        "likes_alternatives": True,
        "wants_explanations": "when_complex"
    },
    
    "stress_signals": {
        "short_responses": "busy",
        "delayed_responses": "overwhelmed",
        "requests_summary": "time_constrained"
    }
}
```

### 5. Goals and Priorities

```python
goals = {
    "short_term": [
        {"name": "Launch trading bot", "priority": "high", "deadline": "2026-03-30"},
        {"name": "Optimize scanner", "priority": "medium", "deadline": "2026-04-15"}
    ],
    
    "long_term": [
        {"name": "Financial independence", "priority": "high", "horizon": "2028"},
        {"name": "Gold Coast property", "priority": "high", "horizon": "2029"}
    ],
    
    "ongoing": [
        {"name": "Daily income tracking", "priority": "medium"},
        {"name": "Skill development", "priority": "medium"}
    ]
}
```

### 6. Knowledge and Skills

```python
user_knowledge = {
    "expertise": ["crypto_trading", "python", "solana", "automation"],
    "learning": ["rust", "ml", "defi_protocols"],
    "interests": ["ai", "trading", "automation", "research"],
    "avoid_topics": ["politics", "news_drama"]
}
```

## Learning Mechanisms

### Explicit Learning

```python
def learn_explicitly(user_input):
    """Learn from explicit user statements"""
    
    # "I prefer concise responses"
    if "prefer" in user_input:
        preference = extract_preference(user_input)
        update_profile(preference)
    
    # "Don't wake me after 10pm"
    if "don't" in user_input or "never" in user_input:
        constraint = extract_constraint(user_input)
        update_profile(constraint)
    
    # "I usually check crypto at 8am"
    if "usually" in user_input or "always" in user_input:
        routine = extract_routine(user_input)
        update_profile(routine)
```

### Implicit Learning

```python
def learn_implicitly(interaction):
    """Learn from observed behavior"""
    
    # Response time patterns
    if interaction.response_time < 60:
        update_profile("responds_quickly", True)
    
    # Task preferences
    if interaction.task_type in frequent_tasks:
        boost_preference(interaction.task_type)
    
    # Tool usage
    if interaction.tools_used:
        for tool in interaction.tools_used:
            record_tool_usage(tool)
    
    # Success patterns
    if interaction.outcome == "success":
        learn_success_factors(interaction)
```

### Feedback Learning

```python
def learn_from_feedback(suggestion, response):
    """Learn from user feedback on suggestions"""
    
    if response == "accept":
        # Boost similar suggestions
        boost_pattern(suggestion.pattern)
        record_positive_feedback(suggestion)
    
    elif response == "reject":
        # Reduce similar suggestions
        reduce_pattern(suggestion.pattern)
        record_negative_feedback(suggestion)
        
        # Learn why
        if response.has_reason():
            learn_rejection_reason(suggestion, response.reason)
    
    elif response == "ignore":
        # Slight reduction
        slightly_reduce_pattern(suggestion.pattern)
```

## Model Updates

### Real-Time Updates

```python
class UserModel:
    def __init__(self):
        self.profile = self.load_profile()
    
    def update_from_interaction(self, interaction):
        """Update model from single interaction"""
        
        # Update response time average
        self.profile.response_times.append(interaction.duration)
        
        # Update activity patterns
        self.profile.record_activity(interaction.type)
        
        # Update preferences if expressed
        if interaction.expressed_preference:
            self.profile.update_preference(interaction.expressed_preference)
    
    def update_from_outcome(self, outcome):
        """Update from task outcome"""
        
        # Learn what works
        if outcome.success:
            self.profile.success_patterns.append(outcome.pattern)
        else:
            self.profile.failure_patterns.append(outcome.pattern)
```

### Periodic Updates

```python
def periodic_model_update():
    """Run daily/weekly model updates"""
    
    # Analyze recent behavior
    recent = get_interactions(timeframe='7d')
    
    # Detect new patterns
    new_patterns = pattern_extractor.extract(recent)
    
    # Update routines
    routine_changes = detect_routine_changes(recent)
    
    # Update preferences
    preference_shifts = detect_preference_shifts(recent)
    
    # Save updated model
    save_profile()
```

## Personalization

### Response Personalization

```python
def personalize_response(response, user_profile):
    """Adapt response to user preferences"""
    
    # Adjust length
    if user_profile.preferences.communication.style == "concise":
        response = make_concise(response)
    elif user_profile.preferences.communication.style == "detailed":
        response = add_details(response)
    
    # Adjust tone
    if user_profile.preferences.communication.tone == "friendly":
        response = make_friendly(response)
    elif user_profile.preferences.communication.tone == "professional":
        response = make_professional(response)
    
    # Add/remove emojis
    if user_profile.preferences.communication.emoji_usage == "none":
        response = remove_emojis(response)
    
    return response
```

### Timing Personalization

```python
def personalize_timing(suggestion, user_profile):
    """Choose optimal timing for suggestion"""
    
    # Check user schedule
    if user_profile.in_focus_time():
        return "delay_until_break"
    
    if user_profile.in_meeting():
        return "delay_until_after"
    
    if user_profile.is_quiet_hours():
        return "delay_until_morning"
    
    # Check historical response times
    optimal_time = user_profile.get_optimal_response_time()
    
    return optimal_time
```

### Content Personalization

```python
def personalize_content(content, user_profile):
    """Adapt content to user knowledge and interests"""
    
    # Adjust technical depth
    if user_profile.knowledge_level == "expert":
        content = skip_basics(content)
    elif user_profile.knowledge_level == "beginner":
        content = add_explanations(content)
    
    # Filter by interests
    if not matches_interests(content, user_profile.interests):
        content = add_relevance(content)
    
    # Avoid disliked topics
    if contains_topics(content, user_profile.avoid_topics):
        content = filter_topics(content)
    
    return content
```

## Implementation

### Core Model

```python
class UserBehaviorModel:
    def __init__(self):
        self.demographics = {}
        self.preferences = {}
        self.routines = {}
        self.patterns = {}
        self.goals = {}
        self.knowledge = {}
    
    def load(self):
        """Load user model from storage"""
        data = load_json("memory/user_model/profile.json")
        self.__dict__.update(data)
    
    def save(self):
        """Save user model to storage"""
        save_json("memory/user_model/profile.json", self.__dict__)
    
    def update(self, observation):
        """Update model from observation"""
        
        # Route to appropriate updater
        if observation.type == "preference":
            self.update_preferences(observation)
        elif observation.type == "routine":
            self.update_routines(observation)
        elif observation.type == "behavior":
            self.update_patterns(observation)
        elif observation.type == "goal":
            self.update_goals(observation)
    
    def get_personalization_context(self):
        """Get context for personalizing responses"""
        return {
            "preferences": self.preferences,
            "current_routine": self.get_current_routine(),
            "active_goals": self.get_active_goals(),
            "communication_style": self.preferences.communication
        }
```

## Usage Examples

### Example 1: Personalize Response
```python
model = UserBehaviorModel()
model.load()

# Get personalization context
context = model.get_personalization_context()

# Generate response
response = generate_response(query)

# Personalize
personalized = personalize_response(response, context)

# Send
send_to_user(personalized)
```

### Example 2: Optimal Timing
```python
# User wants to send a non-urgent message
message = create_message()

# Check optimal timing
optimal_time = model.get_optimal_delivery_time(message)

if optimal_time == "now":
    send_now(message)
else:
    schedule_for(message, optimal_time)
```

### Example 3: Predict Needs
```python
# Current context
current = {
    "time": "08:30",
    "day": "monday",
    "location": "home"
}

# Predict needs
predicted_needs = model.predict_needs(current)

for need in predicted_needs:
    if need.confidence > 0.8:
        prepare_for(need)
```

## Configuration

```yaml
# user_behavior_model.yaml

learning:
  explicit_weight: 0.7
  implicit_weight: 0.3
  feedback_weight: 0.5
  
  update_frequency:
    real_time: true
    daily: true
    weekly: true

privacy:
  anonymize: false
  local_only: true
  retention: 365_days

personalization:
  enabled: true
  level: "high"  # minimal, medium, high
  
  aspects:
    communication: true
    timing: true
    content: true
    suggestions: true
```

## Storage

```
memory/user_model/
├── profile.json
├── preferences.json
├── routines.json
├── patterns.json
├── goals.json
├── knowledge.json
├── history/
│   └── interactions.jsonl
└── config.yaml
```

## Commands

| Command | Action |
|---------|--------|
| "Show my profile" | Display user model |
| "Update my preferences" | Modify preferences |
| "What are my routines?" | Show detected routines |
| "Learn from this" | Explicit learning |
| "Reset my model" | Clear and rebuild |
| "Export my data" | Export user model |

## Integration

### With Predictive Engine
```python
# Use user model for predictions
context = user_model.get_personalization_context()
predictions = predictive_engine.predict(context)
```

### With Suggestion Engine
```python
# Personalize suggestions
context = user_model.get_personalization_context()
suggestions = suggestion_engine.generate(context)
personalized = personalize_suggestions(suggestions, context)
```

### With ALOE
```python
# Feed user patterns to ALOE
patterns = user_model.get_behavioral_patterns()
aloe.learn_user_patterns(patterns)
```

---

**The User Behavior Model: Deep personalization for proactive AI.** 👤
