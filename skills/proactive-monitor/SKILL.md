---
name: proactive-monitor
description: Intelligent monitoring system that watches multiple data sources, detects anomalies and opportunities, batches alerts intelligently, and triggers actions based on conditions. Smarter than cron - context-aware and adaptive.
---

# Proactive Monitor

**Watch everything. Alert intelligently. Act automatically.**

The Proactive Monitor goes beyond simple cron jobs - it watches multiple data sources, understands context, batches alerts smartly, and takes actions based on conditions.

## Core Philosophy

**Smart watching, not just scheduled checking.**

Traditional monitoring: "Check every 30 minutes"
Proactive monitoring: "Watch continuously, alert when it matters"

## Architecture

```
┌─────────────────────────────────────────┐
│         PROACTIVE MONITOR               │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────┐  ┌──────────────┐    │
│  │   WATCHERS   │  │   ALERT      │    │
│  │   (Sources)  │  │   ENGINE     │    │
│  └──────┬───────┘  └──────┬───────┘    │
│         │                 │             │
│         └────────┬────────┘             │
│                  │                      │
│         ┌────────▼────────┐             │
│         │   CONDITION     │             │
│         │   EVALUATOR     │             │
│         └────────┬────────┘             │
│                  │                      │
│         ┌────────▼────────┐             │
│         │   ACTION        │             │
│         │   TRIGGER       │             │
│         └─────────────────┘             │
│                                         │
└─────────────────────────────────────────┘
```

## Watcher Types

### 1. Data Source Watchers

**Financial Watchers:**
```python
class CryptoPriceWatcher:
    def __init__(self):
        self.sources = ['birdeye', 'jupiter', 'dexscreener']
        self.symbols = ['SOL', 'BONK', 'JUP']
    
    def watch(self):
        for symbol in self.symbols:
            price = fetch_price(symbol)
            if price.changed_significantly():
                self.emit_event('price_spike', {
                    'symbol': symbol,
                    'change': price.change_percent,
                    'current': price.value
                })
```

**System Watchers:**
```python
class SystemHealthWatcher:
    def __init__(self):
        self.metrics = ['cpu', 'memory', 'disk', 'network']
    
    def watch(self):
        for metric in self.metrics:
            value = get_metric(metric)
            if value.above_threshold():
                self.emit_event('system_alert', {
                    'metric': metric,
                    'value': value.current,
                    'threshold': value.threshold
                })
```

**Communication Watchers:**
```python
class EmailWatcher:
    def __init__(self):
        self.filters = {
            'urgent': 'priority:high OR from:boss',
            'opportunities': 'subject:opportunity OR subject:partnership',
            'alerts': 'from:alerts@'
        }
    
    def watch(self):
        emails = fetch_new_emails()
        for email in emails:
            category = self.categorize(email)
            if category:
                self.emit_event(f'email_{category}', email)
```

### 2. Event-Based Watchers

**Webhook Watchers:**
```python
class WebhookWatcher:
    def __init__(self):
        self.endpoints = {
            '/new-token': self.handle_new_token,
            '/price-alert': self.handle_price_alert,
            '/system-event': self.handle_system_event
        }
    
    def handle_new_token(self, data):
        self.emit_event('new_token_launch', data)
    
    def handle_price_alert(self, data):
        self.emit_event('price_threshold_hit', data)
```

**Stream Watchers:**
```python
class WebSocketWatcher:
    def __init__(self):
        self.streams = ['helius', 'birdeye_ws']
    
    def on_transaction(self, tx):
        if self.is_whale_transaction(tx):
            self.emit_event('whale_activity', tx)
    
    def on_price_update(self, update):
        if update.volume_spike():
            self.emit_event('volume_spike', update)
```

## Smart Alerting

### Alert Batching

**Problem:** Too many alerts = alert fatigue
**Solution:** Intelligent batching

```python
class AlertBatcher:
    def __init__(self):
        self.batch_window = 300  # 5 minutes
        self.batches = {}
    
    def should_alert_now(self, alert) -> bool:
        """Decide if alert should be sent immediately or batched"""
        
        # Critical alerts always immediate
        if alert.priority == 'critical':
            return True
        
        # Check if user is busy
        if self.user_is_busy():
            self.batch_for_later(alert)
            return False
        
        # Check time of day
        if self.is_quiet_hours():
            self.batch_for_later(alert)
            return False
        
        # Check recent alert frequency
        if self.recent_alert_count() > 3:
            self.batch_for_later(alert)
            return False
        
        return True
    
    def send_batch(self):
        """Send batched alerts as digest"""
        if not self.batches:
            return
        
        digest = self.create_digest(self.batches)
        send_alert(digest)
        self.batches.clear()
```

### Alert Prioritization

```python
class AlertPrioritizer:
    def prioritize(self, alert) -> Priority:
        """Score alert importance"""
        score = 0
        
        # Urgency factors
        if alert.is_time_sensitive():
            score += 50
        if alert.requires_action():
            score += 30
        if alert.is_opportunity():
            score += 20
        
        # User context
        if alert.matches_user_interests():
            score += 15
        if alert.is_from_trusted_source():
            score += 10
        
        # Convert to priority
        if score >= 80:
            return Priority.CRITICAL
        elif score >= 60:
            return Priority.HIGH
        elif score >= 40:
            return Priority.MEDIUM
        else:
            return Priority.LOW
```

### Context-Aware Delivery

```python
class ContextAwareDelivery:
    def should_deliver(self, alert) -> bool:
        """Check if now is appropriate time to deliver"""
        
        # Don't wake user for non-critical
        if self.is_night() and alert.priority != 'critical':
            return False
        
        # Don't interrupt focused work
        if self.user_is_focused() and alert.priority != 'critical':
            return False
        
        # Don't spam during meetings
        if self.in_meeting():
            return False
        
        return True
    
    def choose_channel(self, alert) -> Channel:
        """Choose best channel for alert"""
        if alert.priority == 'critical':
            return Channel.TELEGRAM_URGENT
        elif alert.has_visual_component():
            return Channel.CANVAS
        elif alert.is_quick_read():
            return Channel.TELEGRAM
        else:
            return Channel.EMAIL_DIGEST
```

## Condition Evaluation

### Condition Types

**Threshold Conditions:**
```python
conditions = {
    "price_spike": {
        "type": "threshold",
        "metric": "price_change_24h",
        "operator": ">",
        "value": 20,  # 20%
        "duration": "5m"  # Sustained for 5 minutes
    },
    "volume_surge": {
        "type": "threshold",
        "metric": "volume_ratio",
        "operator": ">",
        "value": 3,  # 3x average
        "window": "1h"
    }
}
```

**Pattern Conditions:**
```python
conditions = {
    "whale_accumulation": {
        "type": "pattern",
        "pattern": "3+ large buys in 30 minutes",
        "from_same_wallet": False
    },
    "breakout_setup": {
        "type": "pattern",
        "pattern": "consolidation + volume build + resistance test"
    }
}
```

**Composite Conditions:**
```python
conditions = {
    "strong_buy_signal": {
        "type": "composite",
        "all_of": [
            {"condition": "price_above_ema"},
            {"condition": "volume_spike"},
            {"condition": "positive_sentiment"}
        ]
    }
}
```

### Condition Engine

```python
class ConditionEngine:
    def __init__(self):
        self.conditions = {}
        self.state = {}
    
    def evaluate(self, condition_id, data) -> bool:
        """Evaluate if condition is met"""
        condition = self.conditions[condition_id]
        
        if condition['type'] == 'threshold':
            return self.evaluate_threshold(condition, data)
        elif condition['type'] == 'pattern':
            return self.evaluate_pattern(condition, data)
        elif condition['type'] == 'composite':
            return self.evaluate_composite(condition, data)
        
        return False
    
    def evaluate_threshold(self, condition, data):
        value = data.get(condition['metric'])
        threshold = condition['value']
        operator = condition['operator']
        
        if operator == '>':
            return value > threshold
        elif operator == '<':
            return value < threshold
        elif operator == '==':
            return value == threshold
        elif operator == 'between':
            return threshold[0] <= value <= threshold[1]
        
        return False
```

## Action Triggers

### Action Types

**1. Notification Actions:**
```python
class NotifyAction:
    def execute(self, alert):
        message = self.format_message(alert)
        
        if alert.priority == 'critical':
            send_urgent_notification(message)
        else:
            send_standard_notification(message)
```

**2. Auto-Response Actions:**
```python
class AutoResponseAction:
    def execute(self, alert):
        if alert.type == 'urgent_email':
            # Auto-respond with acknowledgment
            send_auto_reply(alert.email, "Received, will respond shortly")
        elif alert.type == 'calendar_conflict':
            # Suggest resolution
            propose_reschedule(alert.conflict)
```

**3. Data Collection Actions:**
```python
class DataCollectionAction:
    def execute(self, alert):
        if alert.type == 'new_token':
            # Gather full data
            token_data = gather_token_data(alert.ca)
            store_for_analysis(token_data)
```

**4. Chain Actions:**
```python
class ChainAction:
    def __init__(self):
        self.actions = []
    
    def add(self, action):
        self.actions.append(action)
    
    def execute(self, alert):
        for action in self.actions:
            result = action.execute(alert)
            if not result.success:
                break
```

## Implementation

### Core Monitor Class

```python
class ProactiveMonitor:
    def __init__(self):
        self.watchers = []
        self.alert_engine = AlertEngine()
        self.condition_engine = ConditionEngine()
        self.action_engine = ActionEngine()
        self.running = False
    
    def add_watcher(self, watcher):
        """Register a new watcher"""
        self.watchers.append(watcher)
        watcher.on_event = self.handle_event
    
    def handle_event(self, event):
        """Process incoming event from watcher"""
        # Check conditions
        triggered_conditions = []
        for condition_id, condition in self.condition_engine.conditions.items():
            if self.condition_engine.evaluate(condition_id, event.data):
                triggered_conditions.append(condition_id)
        
        if triggered_conditions:
            # Create alert
            alert = Alert(
                event=event,
                conditions=triggered_conditions,
                timestamp=datetime.now()
            )
            
            # Process alert
            self.process_alert(alert)
    
    def process_alert(self, alert):
        """Process alert through pipeline"""
        # Prioritize
        priority = self.alert_engine.prioritize(alert)
        alert.priority = priority
        
        # Check if should deliver now
        if self.alert_engine.should_deliver_now(alert):
            # Execute actions
            self.action_engine.execute(alert)
        else:
            # Batch for later
            self.alert_engine.batch(alert)
    
    def start(self):
        """Start all watchers"""
        self.running = True
        for watcher in self.watchers:
            watcher.start()
    
    def stop(self):
        """Stop all watchers"""
        self.running = False
        for watcher in self.watchers:
            watcher.stop()
```

## Usage Examples

### Example 1: Crypto Monitoring
```python
# Setup crypto watcher
watcher = CryptoWatcher(
    symbols=['SOL', 'BONK', 'JUP'],
    conditions={
        'price_spike': {'change': 20, 'duration': '5m'},
        'volume_surge': {'ratio': 3, 'window': '1h'}
    }
)

monitor.add_watcher(watcher)
monitor.start()

# When SOL pumps 25%:
# 1. Watcher detects price change
# 2. Condition engine evaluates
# 3. Alert created with HIGH priority
# 4. Context check: User not in meeting
# 5. Action: Send Telegram alert immediately
```

### Example 2: Email Monitoring
```python
# Setup email watcher
watcher = EmailWatcher(
    filters={
        'urgent': 'priority:high',
        'opportunities': 'subject:partnership'
    }
)

# When urgent email arrives:
# 1. Watcher categorizes as 'urgent'
# 2. Alert created with CRITICAL priority
# 3. Context check: User in meeting
# 4. Action: Batch for immediate after-meeting delivery
```

### Example 3: System Monitoring
```python
# Setup system watcher
watcher = SystemWatcher(
    metrics=['disk', 'memory'],
    thresholds={
        'disk': {'warning': 80, 'critical': 90},
        'memory': {'warning': 85, 'critical': 95}
    }
)

# When disk hits 85%:
# 1. Watcher detects threshold breach
# 2. Alert created with MEDIUM priority
# 3. Context check: Quiet hours
# 4. Action: Queue for morning digest with cleanup suggestions
```

## Configuration

```yaml
# proactive_monitor.yaml

watchers:
  crypto:
    enabled: true
    symbols: ['SOL', 'BONK', 'JUP']
    check_interval: 60  # seconds
    
  email:
    enabled: true
    poll_interval: 300  # 5 minutes
    
  system:
    enabled: true
    metrics: ['cpu', 'memory', 'disk']
    check_interval: 60

alerting:
  batch_window: 300  # 5 minutes
  max_alerts_per_hour: 10
  quiet_hours:
    start: "23:00"
    end: "07:00"
  
  channels:
    critical: telegram_urgent
    high: telegram
    medium: digest
    low: dashboard_only

conditions:
  price_spike:
    type: threshold
    metric: price_change_24h
    operator: ">"
    value: 20
    
  volume_surge:
    type: threshold
    metric: volume_ratio
    operator: ">"
    value: 3
```

## Storage

```
memory/proactive_monitor/
├── watchers/
│   ├── crypto_watcher.json
│   ├── email_watcher.json
│   └── system_watcher.json
├── alerts/
│   ├── active_alerts.json
│   ├── alert_history.jsonl
│   └── batched_alerts.json
├── conditions/
│   ├── conditions.json
│   └── condition_history.json
├── actions/
│   └── action_log.jsonl
└── config.yaml
```

## Commands

| Command | Action |
|---------|--------|
| "Start monitoring" | Begin all watchers |
| "Stop monitoring" | Pause all watchers |
| "Add watcher" | Register new watcher |
| "Alert status" | Show active alerts |
| "Clear alerts" | Dismiss all alerts |
| "Configure alerts" | Update alert settings |
| "Test alert" | Send test notification |

## Integration

### With Event Bus
```python
# Publish events to bus
bus.publish('monitor.alert', alert.to_dict())
```

### With ALOE
```python
# Learn from alert outcomes
aloe.observe(
    action="alert_sent",
    outcome=user_response,
    context=alert.context
)
```

### With Predictive Engine
```python
# Predict when alerts likely
prediction = predictive_engine.predict('alert_likely')
if prediction.confidence > 0.8:
    prepare_for_alert()
```

---

**The Proactive Monitor: Smart watching for the proactive AI.** 👁️
