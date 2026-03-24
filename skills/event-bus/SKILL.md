---
name: event-bus
tier: 5
type: integration-layer
status: active
---

# Event Bus Skill

Tier 5 Integration Layer - connects all skill tiers through centralized event routing.

## API

### EventBus (Central Router)

```python
from skills.event_bus import EventBus, get_event_bus, Event, EventPriority

# Create or get global instance
bus = get_event_bus()

# Start the bus
bus.start()

# Subscribe to events
bus.subscribe(
    subscriber_id='my_skill',
    handler=lambda event: print(event.payload),
    event_types=['skill.completed'],
    priority_min=EventPriority.NORMAL
)

# Publish events
bus.publish(
    event_type='skill.completed',
    source='my_skill',
    payload={'result': 'success'}
)

# Stop gracefully
bus.stop()
```

### EventEmitter (Publishing)

```python
from skills.event_bus import EventEmitter

emitter = EventEmitter(bus, source='my_skill')
emitter.emit('task.started', {'task_id': 123})
```

### EventSubscriber (Subscribing)

```python
from skills.event_bus import EventSubscriber

sub = EventSubscriber(bus, subscriber_id='my_skill')
sub.on(['skill.completed'], handler_fn)
sub.on_all(log_all_events)
```

## Event Priority

- `CRITICAL` - Process immediately
- `HIGH` - Process before normal
- `NORMAL` - Standard processing
- `LOW` - Process when idle
- `BACKGROUND` - Lowest priority

## Features

- Thread-safe operations
- Persistent event logging
- Retry mechanism with dead letter queue
- Event filtering by type/source/priority
- Async/sync event emission
- Infinite loop protection
- Queue size limits
