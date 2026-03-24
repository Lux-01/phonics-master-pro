#!/usr/bin/env python3
"""
Tier 5: Event Bus - Integration Layer
Connects all tiers through a centralized event routing system.

ACA 7-Step Implementation:
- Central router for events between skills
- Sync/async event emission
- Event filtering and subscriptions
- Persistent event log
- Retry mechanism with dead letter queue
"""

import json
import os
import time
import threading
import uuid
import hashlib
from pathlib import Path
from typing import Callable, Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict, field
from enum import Enum, auto
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventPriority(Enum):
    """Event priority levels for processing order."""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4


class EventStatus(Enum):
    """Event processing status."""
    PENDING = auto()
    PROCESSING = auto()
    COMPLETED = auto()
    FAILED = auto()
    DEAD_LETTER = auto()


@dataclass
class Event:
    """
    Core event data structure.
    
    Attributes:
        event_type: Type/category of the event
        source: Origin of the event (skill name)
        payload: Event data
        timestamp: When the event was created
        event_id: Unique identifier for the event
        priority: Processing priority
        correlation_id: Links related events together
        depth: Event chain depth (prevents infinite loops)
        metadata: Additional event metadata
    """
    event_type: str
    source: str
    payload: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    priority: EventPriority = EventPriority.NORMAL
    correlation_id: Optional[str] = None
    depth: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.correlation_id is None:
            self.correlation_id = self.event_id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            'event_type': self.event_type,
            'source': self.source,
            'payload': self.payload,
            'timestamp': self.timestamp,
            'event_id': self.event_id,
            'priority': self.priority.name,
            'correlation_id': self.correlation_id,
            'depth': self.depth,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Create event from dictionary."""
        data = data.copy()
        data['priority'] = EventPriority[data.get('priority', 'NORMAL')]
        return cls(**data)
    
    def is_system_event(self) -> bool:
        """Check if this is a system-level event."""
        return self.event_type.startswith('system.')
    
    def child(self, event_type: str, payload: Dict[str, Any], source: str) -> 'Event':
        """Create a child event with incremented depth."""
        return Event(
            event_type=event_type,
            source=source,
            payload=payload,
            priority=self.priority,
            correlation_id=self.correlation_id,
            depth=self.depth + 1
        )


@dataclass
class Subscription:
    """
    Event subscription definition.
    
    Attributes:
        subscriber_id: Unique identifier for subscriber
        event_types: Types to subscribe to (None = all)
        sources: Source filters (None = all)
        priority_min: Minimum priority to receive
        synchronous: Process synchronously or async
        handler: Callable to invoke on event
        filter_fn: Optional custom filter function
        max_retries: Maximum retry attempts
    """
    subscriber_id: str
    event_types: Optional[Set[str]] = None
    sources: Optional[Set[str]] = None
    priority_min: EventPriority = EventPriority.BACKGROUND
    synchronous: bool = False
    handler: Optional[Callable[[Event], None]] = None
    filter_fn: Optional[Callable[[Event], bool]] = None
    max_retries: int = 3
    
    def matches(self, event: Event) -> bool:
        """Check if event matches subscription criteria."""
        # Event type filter
        if self.event_types is not None and event.event_type not in self.event_types:
            return False
        
        # Source filter
        if self.sources is not None and event.source not in self.sources:
            return False
        
        # Priority filter
        if event.priority.value > self.priority_min.value:
            return False
        
        # Custom filter
        if self.filter_fn is not None and not self.filter_fn(event):
            return False
        
        return True


class EventStore:
    """
    Persistent event storage with rotation and cleanup.
    """
    
    def __init__(self, base_path: Path, max_events_per_file: int = 1000):
        self.base_path = base_path
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.max_events_per_file = max_events_per_file
        self._lock = threading.RLock()
        self._current_events: List[Dict] = []
        self._current_file_idx = self._get_next_file_idx()
        self._dead_letter_queue: List[Dict] = []
    
    def _get_next_file_idx(self) -> int:
        """Find the next available file index."""
        existing = list(self.base_path.glob('events_*.jsonl'))
        if not existing:
            return 0
        indices = [int(f.stem.split('_')[1]) for f in existing if f.stem.split('_')[1].isdigit()]
        return max(indices) if indices else 0
    
    def _current_file(self) -> Path:
        """Get current log file path."""
        return self.base_path / f'events_{self._current_file_idx:06d}.jsonl'
    
    def _rotate_if_needed(self):
        """Rotate log file if max size reached."""
        if len(self._current_events) >= self.max_events_per_file:
            self._persist_current()
            self._current_events = []
            self._current_file_idx += 1
    
    def _persist_current(self):
        """Persist current events to disk."""
        if not self._current_events:
            return
        
        file_path = self._current_file()
        with open(file_path, 'a', encoding='utf-8') as f:
            for event in self._current_events:
                f.write(json.dumps(event, ensure_ascii=False) + '\n')
    
    def log_event(self, event: Event, status: EventStatus = EventStatus.PENDING):
        """Log an event with its processing status."""
        with self._lock:
            entry = {
                'event': event.to_dict(),
                'status': status.name,
                'logged_at': time.time()
            }
            self._current_events.append(entry)
            self._rotate_if_needed()
    
    def update_status(self, event_id: str, status: EventStatus, error: Optional[str] = None):
        """Update event processing status."""
        with self._lock:
            for entry in self._current_events:
                if entry['event']['event_id'] == event_id:
                    entry['status'] = status.name
                    entry['updated_at'] = time.time()
                    if error:
                        entry['error'] = error
                    return True
        return False
    
    def add_to_dead_letter(self, event: Event, error: str, attempts: int):
        """Add event to dead letter queue."""
        with self._lock:
            entry = {
                'event': event.to_dict(),
                'error': error,
                'attempts': attempts,
                'dlq_at': time.time()
            }
            self._dead_letter_queue.append(entry)
            
            # Persist dead letter queue periodically
            dlq_path = self.base_path / 'dead_letter.jsonl'
            with open(dlq_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    def get_event_log(self, limit: int = 100, event_type: Optional[str] = None) -> List[Dict]:
        """Retrieve event log with optional filtering."""
        events = []
        
        # Read from current events first
        with self._lock:
            events = [e for e in self._current_events]
        
        # Read from files
        for idx in range(self._current_file_idx, -1, -1):
            file_path = self.base_path / f'events_{idx:06d}.jsonl'
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            events.append(json.loads(line.strip()))
                except Exception:
                    continue
            
            if len(events) >= limit:
                break
        
        # Filter by event type if specified
        if event_type:
            events = [e for e in events if e['event'].get('event_type') == event_type]
        
        # Sort by timestamp and limit
        events.sort(key=lambda x: x.get('logged_at', 0), reverse=True)
        return events[:limit]
    
    def flush(self):
        """Force persist all pending events."""
        with self._lock:
            self._persist_current()


class EventBus:
    """
    Central event bus - the heart of Tier 5 integration.
    
    Routes events between all skill tiers, providing:
    - Thread-safe publish/subscribe
    - Persistent event logging
    - Retry mechanism with dead letter queue
    - Event filtering and priority handling
    - Protection against infinite loops
    """
    
    def __init__(
        self,
        state_dir: Optional[Path] = None,
        max_queue_size: int = 10000,
        max_event_depth: int = 10,
        handler_timeout: float = 30.0,
        worker_threads: int = 4
    ):
        self.state_dir = state_dir or Path('/home/skux/.openclaw/workspace/memory/event-bus')
        self.max_queue_size = max_queue_size
        self.max_event_depth = max_event_depth
        self.handler_timeout = handler_timeout
        
        # Core components
        self._store = EventStore(self.state_dir)
        self._subscriptions: Dict[str, Subscription] = {}
        self._lock = threading.RLock()
        self._running = False
        
        # Async processing
        self._queue: Queue[Event] = Queue(maxsize=max_queue_size)
        self._executor = ThreadPoolExecutor(max_workers=worker_threads, thread_name_prefix='eventbus_')
        self._worker_thread: Optional[threading.Thread] = None
        self._shutdown_event = threading.Event()
        
        # Stats
        self._stats = {
            'published': 0,
            'delivered': 0,
            'failed': 0,
            'dropped': 0,
            'dead_letter': 0
        }
        self._stats_lock = threading.Lock()
        
        # Retry tracking
        self._retry_counts: Dict[str, int] = {}
    
    def start(self):
        """Start the event bus processing."""
        with self._lock:
            if self._running:
                return
            self._running = True
            self._shutdown_event.clear()
        
        # Start async worker
        self._worker_thread = threading.Thread(target=self._async_loop, daemon=True)
        self._worker_thread.start()
        
        logger.info("EventBus started")
        self.emit_system_event('system.bus.started', {'status': 'active'})
    
    def stop(self, timeout: float = 10.0):
        """Stop the event bus gracefully."""
        with self._lock:
            if not self._running:
                return
            self._running = False
        
        self._shutdown_event.set()
        
        # Wait for queue to drain
        try:
            self._queue.join(timeout=timeout)
        except Exception:
            pass
        
        # Shutdown executor
        self._executor.shutdown(wait=True)
        
        # Flush store
        self._store.flush()
        
        logger.info("EventBus stopped")
    
    def _async_loop(self):
        """Background thread for async event processing."""
        while not self._shutdown_event.is_set():
            try:
                event = self._queue.get(timeout=0.1)
                self._route_event(event)
                self._queue.task_done()
            except Empty:
                continue
            except Exception as e:
                logger.error(f"Error in async loop: {e}")
    
    def subscribe(
        self,
        subscriber_id: str,
        handler: Callable[[Event], None],
        event_types: Optional[List[str]] = None,
        sources: Optional[List[str]] = None,
        priority_min: EventPriority = EventPriority.BACKGROUND,
        synchronous: bool = False,
        filter_fn: Optional[Callable[[Event], bool]] = None,
        max_retries: int = 3
    ) -> str:
        """
        Subscribe to events with optional filtering.
        
        Returns subscription ID for unsubscribe.
        """
        subscription = Subscription(
            subscriber_id=subscriber_id,
            event_types=set(event_types) if event_types else None,
            sources=set(sources) if sources else None,
            priority_min=priority_min,
            synchronous=synchronous,
            handler=handler,
            filter_fn=filter_fn,
            max_retries=max_retries
        )
        
        with self._lock:
            self._subscriptions[subscriber_id] = subscription
        
        logger.debug(f"Subscription registered: {subscriber_id}")
        self.emit_system_event('system.subscription.added', {
            'subscriber_id': subscriber_id,
            'event_types': event_types
        })
        
        return subscriber_id
    
    def unsubscribe(self, subscriber_id: str) -> bool:
        """Remove a subscription."""
        with self._lock:
            if subscriber_id in self._subscriptions:
                del self._subscriptions[subscriber_id]
                logger.debug(f"Subscription removed: {subscriber_id}")
                return True
        return False
    
    def publish(
        self,
        event_type: str,
        source: str,
        payload: Dict[str, Any],
        priority: EventPriority = EventPriority.NORMAL,
        correlation_id: Optional[str] = None,
        synchronous: bool = False
    ) -> Event:
        """
        Publish an event to the bus.
        
        Returns the created Event object.
        """
        event = Event(
            event_type=event_type,
            source=source,
            payload=payload,
            priority=priority,
            correlation_id=correlation_id
        )
        
        # Check for infinite loop protection
        if event.depth > self.max_event_depth:
            logger.warning(f"Event depth exceeded for {event_type}, dropping")
            with self._stats_lock:
                self._stats['dropped'] += 1
            self._store.log_event(event, EventStatus.DEAD_LETTER)
            self._store.add_to_dead_letter(event, "Max event depth exceeded", 0)
            return event
        
        # Log event
        self._store.log_event(event, EventStatus.PENDING)
        
        with self._stats_lock:
            self._stats['published'] += 1
        
        if synchronous:
            self._route_event(event)
        else:
            # Check queue capacity
            if self._queue.qsize() >= self.max_queue_size:
                logger.warning(f"Event queue full, dropping {event_type}")
                with self._stats_lock:
                    self._stats['dropped'] += 1
                return event
            
            try:
                self._queue.put(event, block=False)
            except Exception:
                with self._stats_lock:
                    self._stats['dropped'] += 1
        
        return event
    
    def _route_event(self, event: Event):
        """Route event to matching subscribers."""
        with self._lock:
            subscriptions = list(self._subscriptions.values())
        
        if not subscriptions:
            # No subscribers - log and drop
            logger.debug(f"No subscribers for {event.event_type}, dropping")
            self._store.log_event(event, EventStatus.COMPLETED)
            with self._stats_lock:
                self._stats['dropped'] += 1
            return
        
        matching = [s for s in subscriptions if s.matches(event)]
        
        if not matching:
            logger.debug(f"No matching subscriptions for {event.event_type}")
            return
        
        # Deliver to matching subscribers
        for subscription in matching:
            self._deliver(event, subscription)
    
    def _deliver(self, event: Event, subscription: Subscription):
        """Deliver event to a subscriber with retry logic."""
        delivery_key = f"{event.event_id}:{subscription.subscriber_id}"
        attempts = self._retry_counts.get(delivery_key, 0)
        
        try:
            if subscription.handler is None:
                raise ValueError("No handler registered")
            
            # Execute handler with timeout
            future = self._executor.submit(subscription.handler, event)
            future.result(timeout=self.handler_timeout)
            
            # Success
            self._retry_counts.pop(delivery_key, None)
            self._store.update_status(event.event_id, EventStatus.COMPLETED)
            with self._stats_lock:
                self._stats['delivered'] += 1
            
        except Exception as e:
            attempts += 1
            self._retry_counts[delivery_key] = attempts
            
            error_msg = str(e)
            logger.error(f"Handler failed for {subscription.subscriber_id}: {error_msg}")
            
            if attempts >= subscription.max_retries:
                # Move to dead letter queue
                self._store.update_status(event.event_id, EventStatus.DEAD_LETTER, error_msg)
                self._store.add_to_dead_letter(event, error_msg, attempts)
                self._retry_counts.pop(delivery_key, None)
                with self._stats_lock:
                    self._stats['dead_letter'] += 1
                
                self.emit_system_event('system.event.failed', {
                    'event_id': event.event_id,
                    'subscriber_id': subscription.subscriber_id,
                    'error': error_msg,
                    'attempts': attempts
                })
            else:
                self._store.update_status(event.event_id, EventStatus.FAILED, error_msg)
                with self._stats_lock:
                    self._stats['failed'] += 1
    
    def emit_system_event(self, event_type: str, payload: Dict[str, Any]):
        """Emit a system-level event."""
        try:
            event = Event(
                event_type=event_type,
                source='eventbus',
                payload=payload,
                priority=EventPriority.HIGH
            )
            self._store.log_event(event)
        except Exception:
            pass  # Don't let system events break things
    
    def get_stats(self) -> Dict[str, Any]:
        """Get event bus statistics."""
        with self._stats_lock:
            return {
                **self._stats,
                'queue_size': self._queue.qsize(),
                'subscriptions': len(self._subscriptions)
            }
    
    def get_event_log(
        self,
        limit: int = 100,
        event_type: Optional[str] = None
    ) -> List[Dict]:
        """Retrieve event log."""
        return self._store.get_event_log(limit, event_type)
    
    def clear_dead_letter(self) -> int:
        """Clear dead letter queue, returns count cleared."""
        with self._store._lock:
            count = len(self._store._dead_letter_queue)
            self._store._dead_letter_queue = []
            return count


class EventEmitter:
    """
    Convenience class for publishing events.
    Used by skills to emit events without direct EventBus access.
    """
    
    def __init__(self, bus: EventBus, source: str):
        self._bus = bus
        self._source = source
    
    def emit(
        self,
        event_type: str,
        payload: Dict[str, Any],
        priority: EventPriority = EventPriority.NORMAL,
        synchronous: bool = False
    ) -> Event:
        """Emit an event from the source skill."""
        return self._bus.publish(
            event_type=event_type,
            source=self._source,
            payload=payload,
            priority=priority,
            synchronous=synchronous
        )
    
    def emit_chain(
        self,
        parent_event: Event,
        event_type: str,
        payload: Dict[str, Any]
    ) -> Event:
        """Emit a child event in a chain."""
        child = parent_event.child(event_type, payload, self._source)
        return self._bus.publish(
            event_type=child.event_type,
            source=child.source,
            payload=child.payload,
            priority=child.priority,
            correlation_id=child.correlation_id,
            synchronous=False
        )


class EventSubscriber:
    """
    Convenience class for receiving events.
    Used by skills to subscribe to events.
    """
    
    def __init__(self, bus: EventBus, subscriber_id: str):
        self._bus = bus
        self._subscriber_id = subscriber_id
    
    def on(
        self,
        event_types: List[str],
        handler: Callable[[Event], None],
        **kwargs
    ) -> str:
        """Subscribe to specific event types."""
        return self._bus.subscribe(
            subscriber_id=self._subscriber_id,
            handler=handler,
            event_types=event_types,
            **kwargs
        )
    
    def on_all(
        self,
        handler: Callable[[Event], None],
        **kwargs
    ) -> str:
        """Subscribe to all events."""
        return self._bus.subscribe(
            subscriber_id=self._subscriber_id,
            handler=handler,
            event_types=None,
            **kwargs
        )
    
    def unsubscribe(self) -> bool:
        """Unsubscribe from all events."""
        return self._bus.unsubscribe(self._subscriber_id)


# Global event bus instance
_global_bus: Optional[EventBus] = None


def get_event_bus(
    state_dir: Optional[Path] = None,
    **kwargs
) -> EventBus:
    """Get or create global event bus instance."""
    global _global_bus
    if _global_bus is None:
        _global_bus = EventBus(state_dir=state_dir, **kwargs)
    return _global_bus


def reset_event_bus():
    """Reset global event bus (mainly for testing)."""
    global _global_bus
    _global_bus = None


if __name__ == '__main__':
    # Simple demonstration
    bus = EventBus()
    bus.start()
    
    # Subscribe to test events
    def test_handler(event: Event):
        print(f"Received: {event.event_type} from {event.source}")
        print(f"Payload: {event.payload}")
    
    bus.subscribe('test_subscriber', test_handler, event_types=['test.event'])
    
    # Publish test events
    bus.publish('test.event', 'demo', {'message': 'Hello EventBus!'})
    bus.publish('other.event', 'demo', {'message': 'This will be dropped (no subscribers)'})
    
    # Wait a bit for async processing
    time.sleep(1)
    
    # Show stats
    print(f"\nStats: {bus.get_stats()}")
    
    bus.stop()
