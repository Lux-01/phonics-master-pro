---
name: proactive-ai-integration
description: Central integration layer that wires together all 6 proactive AI components (Predictive Engine, Proactive Monitor, Suggestion Engine, Outcome Tracker, Pattern Extractor, User Behavior Model) into a unified proactive AI system.
---

# Proactive AI Integration Layer

**The brain that connects all the pieces.**

This integration layer wires together all 6 proactive AI components into a unified system that anticipates, monitors, suggests, learns, and adapts.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              PROACTIVE AI INTEGRATION LAYER                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  PREDICTIVE │  │  PROACTIVE  │  │ SUGGESTION  │         │
│  │   ENGINE    │  │   MONITOR   │  │   ENGINE    │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         │                │                │                 │
│         └────────────────┼────────────────┘                 │
│                          │                                  │
│              ┌───────────▼───────────┐                      │
│              │   CENTRAL ORCHESTRATOR │                      │
│              │   (Event Bus + Router) │                      │
│              └───────────┬───────────┘                      │
│                          │                                  │
│         ┌────────────────┼────────────────┐                  │
│         │                │                │                  │
│  ┌──────┴──────┐  ┌──────┴──────┐  ┌──────┴──────┐        │
│  │   OUTCOME   │  │   PATTERN   │  │    USER     │        │
│  │   TRACKER   │  │  EXTRACTOR  │  │   MODEL     │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │                    ALOE LEARNING                      │  │
│  │         (Continuous Improvement Loop)               │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

```
User Interaction → Event Bus → Skills Process → Outcome Tracked → Patterns Extracted → ALOE Learns → Model Updates → Better Predictions
```

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | Full documentation and architecture |
| `scripts/proactive_ai_orchestrator.py` | Main orchestrator implementation |
| `scripts/test_integration.py` | Integration tests (6/6 passing) |
| `scripts/quickstart.sh` | Easy start/stop/status script |
| `references/config.yaml` | Configuration for all components |

## Core Components

### 1. Central Orchestrator

```python
class ProactiveAIOrchestrator:
    """Central hub that coordinates all proactive AI components"""
    
    def __init__(self):
        # Initialize all components
        self.predictive_engine = PredictiveEngine()
        self.proactive_monitor = ProactiveMonitor()
        self.suggestion_engine = SuggestionEngine()
        self.outcome_tracker = OutcomeTracker()
        self.pattern_extractor = PatternExtractor()
        self.user_model = UserBehaviorModel()
        
        # Event bus for communication
        self.event_bus = EventBus()
        
        # Register event handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register event handlers for cross-component communication"""
        
        # User interaction events
        self.event_bus.subscribe('user.message', self._on_user_message)
        self.event_bus.subscribe('user.command', self._on_user_command)
        self.event_bus.subscribe('user.idle', self._on_user_idle)
        
        # Monitor events
        self.event_bus.subscribe('monitor.alert', self._on_monitor_alert)
        self.event_bus.subscribe('monitor.condition_met', self._on_condition_met)
        
        # Prediction events
        self.event_bus.subscribe('prediction.made', self._on_prediction_made)
        self.event_bus.subscribe('prediction.confirmed', self._on_prediction_confirmed)
        
        # Suggestion events
        self.event_bus.subscribe('suggestion.offered', self._on_suggestion_offered)
        self.event_bus.subscribe('suggestion.accepted', self._on_suggestion_accepted)
        self.event_bus.subscribe('suggestion.rejected', self._on_suggestion_rejected)
        
        # Outcome events
        self.event_bus.subscribe('task.completed', self._on_task_completed)
        self.event_bus.subscribe('task.failed', self._on_task_failed)
    
    def start(self):
        """Start the proactive AI system"""
        logger.info("Starting Proactive AI Integration Layer...")
        
        # Start all components
        self.proactive_monitor.start()
        self.predictive_engine.start()
        
        # Load user model
        self.user_model.load()
        
        logger.info("Proactive AI system ready")
    
    def stop(self):
        """Stop the proactive AI system"""
        self.proactive_monitor.stop()
        self.predictive_engine.stop()
        self.user_model.save()
```

### 2. Event Handlers

```python
    def _on_user_message(self, event):
        """Handle user message - predict needs, update model"""
        
        # Update user model
        self.user_model.update_from_interaction(event)
        
        # Generate predictions
        predictions = self.predictive_engine.predict_needs(
            context=event.context
        )
        
        # Filter high-confidence predictions
        for prediction in predictions:
            if prediction.confidence >= 0.9:
                # Auto-prepare
                self._auto_prepare(prediction)
            elif prediction.confidence >= 0.7:
                # Offer suggestion
                self.suggestion_engine.offer_prediction(prediction)
    
    def _on_monitor_alert(self, event):
        """Handle monitor alert - prioritize and route"""
        
        # Check user context
        context = self.user_model.get_current_context()
        
        # Decide delivery
        if self._should_deliver_now(event, context):
            # Send immediately
            self._send_alert(event)
        else:
            # Batch for later
            self.proactive_monitor.batch_alert(event)
        
        # Track outcome
        self.outcome_tracker.track_alert(event)
    
    def _on_suggestion_accepted(self, event):
        """Handle accepted suggestion - learn and execute"""
        
        # Execute the suggestion
        result = self._execute_suggestion(event.suggestion)
        
        # Track outcome
        self.outcome_tracker.track_suggestion_outcome(
            suggestion=event.suggestion,
            response='accept',
            result=result
        )
        
        # Update user model
        self.user_model.learn_from_feedback(
            suggestion=event.suggestion,
            response='accept'
        )
        
        # Feed to ALOE
        aloe.observe(
            action='suggestion_accepted',
            outcome='success',
            context=event.context
        )
    
    def _on_task_completed(self, event):
        """Handle completed task - extract patterns, learn"""
        
        # Track outcome
        self.outcome_tracker.track_task_outcome(
            task=event.task,
            status='success'
        )
        
        # Extract patterns
        patterns = self.pattern_extractor.extract_from_outcome(event)
        
        # Update user model
        self.user_model.update_from_outcome(event)
        
        # Feed to ALOE
        aloe.learn_from_outcome(event)
        
        # Generate proactive suggestions for next steps
        suggestions = self.suggestion_engine.suggest_next_steps(event)
        for suggestion in suggestions:
            if suggestion.confidence >= 0.7:
                self.suggestion_engine.offer_suggestion(suggestion)
```

### 3. Integration Points

```python
    def _auto_prepare(self, prediction):
        """Silently prepare for predicted need"""
        
        if prediction.type == 'crypto_check':
            # Pre-fetch portfolio data
            data = self._fetch_portfolio_data()
            self.cache.set('prepared_portfolio', data)
            
        elif prediction.type == 'meeting_prep':
            # Prepare meeting context
            context = self._gather_meeting_context(prediction.meeting_id)
            self.cache.set('prepared_meeting', context)
            
        elif prediction.type == 'code_session':
            # Prepare development environment
            self._prepare_dev_environment()
    
    def _should_deliver_now(self, alert, context):
        """Decide if alert should be delivered immediately"""
        
        # Critical alerts always immediate
        if alert.priority == 'critical':
            return True
        
        # Check user focus
        if context.is_focused and alert.priority != 'high':
            return False
        
        # Check quiet hours
        if context.is_quiet_hours:
            return False
        
        # Check recent alert frequency
        if context.recent_alerts > 3:
            return False
        
        return True
    
    def _execute_suggestion(self, suggestion):
        """Execute an accepted suggestion"""
        
        if suggestion.action == 'run_scanner':
            return self._run_scanner(suggestion.params)
        elif suggestion.action == 'commit_changes':
            return self._commit_changes()
        elif suggestion.action == 'prepare_summary':
            return self._prepare_summary()
        else:
            return {'status': 'unknown_action'}
```

## Configuration

```yaml
# proactive_ai_config.yaml

orchestrator:
  auto_start: true
  event_bus: enabled
  learning: enabled

components:
  predictive_engine:
    enabled: true
    auto_prepare_threshold: 0.9
    suggest_threshold: 0.7
    
  proactive_monitor:
    enabled: true
    batch_window: 300  # 5 minutes
    max_alerts_per_hour: 10
    
  suggestion_engine:
    enabled: true
    max_per_hour: 5
    min_interval: 600  # 10 minutes
    
  outcome_tracker:
    enabled: true
    auto_track: true
    
  pattern_extractor:
    enabled: true
    min_support: 0.1
    min_confidence: 0.7
    
  user_model:
    enabled: true
    update_frequency: real_time
    personalization_level: high

integration:
  aloe_feeding: true
  event_bus_persistence: true
  cross_component_cache: true

learning_loop:
  extract_patterns_daily: true
  update_user_model_daily: true
  generate_weekly_report: true
```

## Usage Examples

### Example 1: Start the System
```python
from proactive_ai_integration import ProactiveAIOrchestrator

# Initialize and start
orchestrator = ProactiveAIOrchestrator()
orchestrator.start()

# System is now running:
# - Monitoring data sources
# - Predicting needs
# - Offering suggestions
# - Learning from outcomes
```

### Example 2: Handle User Message
```python
# When user sends a message
event = {
    'type': 'user.message',
    'content': 'Check my crypto portfolio',
    'timestamp': datetime.now(),
    'context': get_current_context()
}

# Publish to event bus
orchestrator.event_bus.publish(event)

# System automatically:
# 1. Updates user model
# 2. Generates predictions for next needs
# 3. May offer suggestions
# 4. Tracks the interaction
```

### Example 3: Monitor Alert Flow
```python
# Price spike detected
alert_event = {
    'type': 'monitor.alert',
    'alert_type': 'price_spike',
    'symbol': 'SOL',
    'change': 25,
    'priority': 'high'
}

orchestrator.event_bus.publish(alert_event)

# System automatically:
# 1. Checks user context (in meeting? focused?)
# 2. Decides delivery timing
# 3. May batch or send immediately
# 4. Tracks user response
# 5. Learns from outcome
```

### Example 4: Complete Learning Loop
```python
# User accepts suggestion to commit code
suggestion_event = {
    'type': 'suggestion.accepted',
    'suggestion': {
        'id': 'sug-001',
        'text': 'Commit your changes?',
        'action': 'commit_changes'
    }
}

orchestrator.event_bus.publish(suggestion_event)

# System automatically:
# 1. Executes the commit
# 2. Tracks successful outcome
# 3. Extracts pattern (user commits after coding)
# 4. Updates user model
# 5. Feeds to ALOE
# 6. Future suggestions improve
```

## Event Bus

```python
class EventBus:
    """Central event bus for component communication"""
    
    def __init__(self):
        self.subscribers = defaultdict(list)
        self.history = []
    
    def subscribe(self, event_type, handler):
        """Subscribe to event type"""
        self.subscribers[event_type].append(handler)
    
    def publish(self, event):
        """Publish event to all subscribers"""
        event['id'] = generate_id()
        event['timestamp'] = datetime.now().isoformat()
        
        # Store in history
        self.history.append(event)
        
        # Notify subscribers
        event_type = event.get('type')
        for handler in self.subscribers.get(event_type, []):
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Handler error: {e}")
        
        # Also notify wildcard subscribers
        for handler in self.subscribers.get('*', []):
            handler(event)
```

## Storage Structure

```
memory/proactive_ai/
├── orchestrator/
│   ├── state.json
│   └── config.yaml
├── event_bus/
│   └── event_history.jsonl
├── cache/
│   └── prepared_data/
├── cross_component/
│   ├── shared_context.json
│   └── component_states.json
└── learning/
    ├── daily_insights.json
    └── weekly_reports.json
```

## Commands

| Command | Action |
|---------|--------|
| "Start proactive AI" | Initialize and start all components |
| "Stop proactive AI" | Gracefully stop all components |
| "Proactive AI status" | Show component health and status |
| "Force prediction" | Manually trigger prediction cycle |
| "Flush learning" | Push all pending data to ALOE |
| "Reset user model" | Clear and rebuild user model |

## Integration with Existing Skills

```python
# Integration with existing skills
class SkillIntegration:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
    
    def integrate_autonomous_agent(self):
        """Wire autonomous-agent skill"""
        self.orchestrator.event_bus.subscribe(
            'task.complex',
            self._delegate_to_autonomous_agent
        )
    
    def integrate_multi_agent_coordinator(self):
        """Wire multi-agent-coordinator skill"""
        self.orchestrator.event_bus.subscribe(
            'task.parallel',
            self._delegate_to_multi_agent
        )
    
    def integrate_knowledge_graph(self):
        """Wire knowledge-graph-engine"""
        # Feed patterns to knowledge graph
        self.orchestrator.event_bus.subscribe(
            'pattern.extracted',
            self._add_to_knowledge_graph
        )
```

## Benefits

1. **Unified System:** All 6 components work as one
2. **Continuous Learning:** Every interaction improves the system
3. **Smart Coordination:** Components communicate via events
4. **Adaptive:** Learns user patterns and preferences
5. **Proactive:** Anticipates needs before user asks
6. **Self-Improving:** ALOE integration ensures continuous improvement

---

**The Proactive AI Integration Layer: All components, one brain.** 🧠⚡
