#!/usr/bin/env python3
"""
Proactive AI Integration Layer
Central orchestrator that wires together all 6 proactive AI components.
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from collections import defaultdict

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('proactive_ai')

class EventBus:
    """Central event bus for component communication"""
    
    def __init__(self, persistence_path: Optional[str] = None):
        self.subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.history: List[Dict] = []
        self.persistence_path = persistence_path or "memory/proactive_ai/event_bus/event_history.jsonl"
        
        # Ensure directory exists
        Path(self.persistence_path).parent.mkdir(parents=True, exist_ok=True)
    
    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to event type"""
        self.subscribers[event_type].append(handler)
        logger.debug(f"Handler subscribed to {event_type}")
    
    def publish(self, event: Dict[str, Any]):
        """Publish event to all subscribers"""
        event['id'] = f"evt-{datetime.now().strftime('%Y%m%d%H%M%S')}-{len(self.history)}"
        event['timestamp'] = datetime.now().isoformat()
        
        # Store in history
        self.history.append(event)
        
        # Persist event
        self._persist_event(event)
        
        # Notify subscribers
        event_type = event.get('type', '')
        handlers = self.subscribers.get(event_type, [])
        handlers.extend(self.subscribers.get('*', []))  # Wildcard subscribers
        
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Handler error for {event_type}: {e}")
    
    def _persist_event(self, event: Dict):
        """Persist event to disk"""
        try:
            with open(self.persistence_path, 'a') as f:
                f.write(json.dumps(event) + '\n')
        except Exception as e:
            logger.warning(f"Failed to persist event: {e}")


class ComponentCache:
    """Shared cache for cross-component data"""
    
    def __init__(self, cache_dir: str = "memory/proactive_ai/cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._memory_cache: Dict[str, Any] = {}
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Store value in cache"""
        self._memory_cache[key] = {
            'value': value,
            'timestamp': datetime.now().isoformat(),
            'ttl': ttl
        }
        
        # Also persist to disk for large values
        if isinstance(value, (dict, list)) and len(str(value)) > 1000:
            cache_file = self.cache_dir / f"{key}.json"
            with open(cache_file, 'w') as f:
                json.dump(self._memory_cache[key], f)
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve value from cache"""
        if key in self._memory_cache:
            entry = self._memory_cache[key]
            # Check TTL
            if entry.get('ttl'):
                stored = datetime.fromisoformat(entry['timestamp'])
                elapsed = (datetime.now() - stored).total_seconds()
                if elapsed > entry['ttl']:
                    del self._memory_cache[key]
                    return None
            return entry['value']
        
        # Try loading from disk
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                entry = json.load(f)
                self._memory_cache[key] = entry
                return entry['value']
        
        return None
    
    def clear(self):
        """Clear all cached data"""
        self._memory_cache.clear()
        for f in self.cache_dir.glob('*.json'):
            f.unlink()


class ProactiveAIOrchestrator:
    """Central hub that coordinates all proactive AI components"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "memory/proactive_ai/orchestrator/config.yaml"
        self.config = self._load_config()
        
        # Initialize event bus
        self.event_bus = EventBus()
        
        # Initialize cache
        self.cache = ComponentCache()
        
        # Component states
        self.components: Dict[str, Any] = {}
        self.component_status: Dict[str, str] = {}
        
        # Initialize components (placeholder)
        self._init_components()
        
        # Register event handlers
        self._register_handlers()
        
        logger.info("Proactive AI Orchestrator initialized")
    
    def _load_config(self) -> Dict:
        """Load configuration"""
        default_config = {
            'orchestrator': {
                'auto_start': True,
                'event_bus': True,
                'learning': True
            },
            'components': {
                'predictive_engine': {'enabled': True, 'auto_prepare_threshold': 0.9, 'suggest_threshold': 0.7},
                'proactive_monitor': {'enabled': True, 'batch_window': 300, 'max_alerts_per_hour': 10},
                'suggestion_engine': {'enabled': True, 'max_per_hour': 5, 'min_interval': 600},
                'outcome_tracker': {'enabled': True, 'auto_track': True},
                'pattern_extractor': {'enabled': True, 'min_support': 0.1, 'min_confidence': 0.7},
                'user_model': {'enabled': True, 'update_frequency': 'real_time', 'personalization_level': 'high'}
            },
            'integration': {
                'aloe_feeding': True,
                'event_bus_persistence': True,
                'cross_component_cache': True
            }
        }
        
        # Try to load from file
        config_file = Path(self.config_path)
        if config_file.exists():
            try:
                import yaml
                with open(config_file, 'r') as f:
                    loaded = yaml.safe_load(f)
                    if loaded:
                        default_config.update(loaded)
            except Exception as e:
                logger.warning(f"Failed to load config: {e}")
        
        return default_config
    
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
        
        logger.info("Event handlers registered")
    
    def start(self):
        """Start the proactive AI system"""
        logger.info("=" * 50)
        logger.info("Starting Proactive AI Integration Layer")
        logger.info("=" * 50)
        
        # Initialize components
        self._init_components()
        
        # Start enabled components
        for name, component in self.components.items():
            if self.config['components'].get(name, {}).get('enabled', True):
                try:
                    if hasattr(component, 'start'):
                        component.start()
                    self.component_status[name] = 'running'
                    logger.info(f"✓ {name} started")
                except Exception as e:
                    self.component_status[name] = f'error: {e}'
                    logger.error(f"✗ {name} failed to start: {e}")
        
        logger.info("-" * 50)
        logger.info("Proactive AI system ready")
        logger.info("-" * 50)
    
    def stop(self):
        """Stop the proactive AI system"""
        logger.info("Stopping Proactive AI Integration Layer...")
        
        for name, component in self.components.items():
            try:
                if hasattr(component, 'stop'):
                    component.stop()
                self.component_status[name] = 'stopped'
                logger.info(f"✓ {name} stopped")
            except Exception as e:
                logger.error(f"✗ {name} error during stop: {e}")
        
        # Save user model
        if 'user_model' in self.components:
            try:
                self.components['user_model'].save()
            except Exception as e:
                logger.error(f"Failed to save user model: {e}")
        
        logger.info("Proactive AI system stopped")
    
    def _init_components(self):
        """Initialize all components"""
        # These would import and initialize the actual components
        # For now, we create placeholder references
        
        self.components = {
            'predictive_engine': PlaceholderComponent('predictive_engine'),
            'proactive_monitor': PlaceholderComponent('proactive_monitor'),
            'suggestion_engine': PlaceholderComponent('suggestion_engine'),
            'outcome_tracker': PlaceholderComponent('outcome_tracker'),
            'pattern_extractor': PlaceholderComponent('pattern_extractor'),
            'user_model': PlaceholderComponent('user_model')
        }
    
    # Event Handlers
    
    def _on_user_message(self, event):
        """Handle user message - predict needs, update model"""
        logger.debug(f"User message received: {event.get('content', '')[:50]}...")
        
        # Update user model
        if 'user_model' in self.components:
            self.components['user_model'].update_from_interaction(event)
        
        # Generate predictions
        if 'predictive_engine' in self.components:
            predictions = self.components['predictive_engine'].predict_needs(
                context=event.get('context', {})
            )
            
            # Filter high-confidence predictions
            for prediction in predictions:
                confidence = prediction.get('confidence', 0)
                if confidence >= self.config['components']['predictive_engine']['auto_prepare_threshold']:
                    self._auto_prepare(prediction)
                elif confidence >= self.config['components']['predictive_engine']['suggest_threshold']:
                    if 'suggestion_engine' in self.components:
                        self.components['suggestion_engine'].offer_prediction(prediction)
    
    def _on_user_command(self, event):
        """Handle user command"""
        command = event.get('command', '')
        logger.info(f"Command received: {command}")
        
        # Track as outcome
        if 'outcome_tracker' in self.components:
            self.components['outcome_tracker'].track_command(event)
    
    def _on_user_idle(self, event):
        """Handle user idle"""
        logger.debug("User idle detected")
        
        # May offer suggestions or prepare data
        if 'suggestion_engine' in self.components:
            suggestions = self.components['suggestion_engine'].suggest_for_idle()
            for suggestion in suggestions:
                if suggestion.get('confidence', 0) >= 0.7:
                    self.event_bus.publish({
                        'type': 'suggestion.offered',
                        'suggestion': suggestion
                    })
    
    def _on_monitor_alert(self, event):
        """Handle monitor alert - prioritize and route"""
        logger.info(f"Monitor alert: {event.get('alert_type', 'unknown')}")
        
        # Get user context
        context = {}
        if 'user_model' in self.components:
            context = self.components['user_model'].get_current_context()
        
        # Decide delivery
        if self._should_deliver_now(event, context):
            self._send_alert(event)
        else:
            # Batch for later
            logger.info("Alert batched for later delivery")
        
        # Track outcome
        if 'outcome_tracker' in self.components:
            self.components['outcome_tracker'].track_alert(event)
    
    def _on_condition_met(self, event):
        """Handle condition being met"""
        logger.info(f"Condition met: {event.get('condition', 'unknown')}")
        
        # May trigger actions
        self._trigger_condition_actions(event)
    
    def _on_prediction_made(self, event):
        """Handle prediction made"""
        logger.debug(f"Prediction made: {event.get('prediction', {})}")
    
    def _on_prediction_confirmed(self, event):
        """Handle prediction confirmed"""
        logger.info(f"Prediction confirmed: {event.get('prediction_id', '')}")
        
        # Learn from successful prediction
        if 'pattern_extractor' in self.components:
            self.components['pattern_extractor'].record_successful_prediction(event)
    
    def _on_suggestion_offered(self, event):
        """Handle suggestion offered"""
        logger.info(f"Suggestion offered: {event.get('suggestion', {}).get('text', '')[:50]}...")
    
    def _on_suggestion_accepted(self, event):
        """Handle accepted suggestion - learn and execute"""
        logger.info("Suggestion accepted")
        
        suggestion = event.get('suggestion', {})
        
        # Execute the suggestion
        result = self._execute_suggestion(suggestion)
        
        # Track outcome
        if 'outcome_tracker' in self.components:
            self.components['outcome_tracker'].track_suggestion_outcome(
                suggestion=suggestion,
                response='accept',
                result=result
            )
        
        # Update user model
        if 'user_model' in self.components:
            self.components['user_model'].learn_from_feedback(
                suggestion=suggestion,
                response='accept'
            )
        
        # Feed to ALOE
        self._feed_to_aloe('suggestion_accepted', 'success', event.get('context', {}))
    
    def _on_suggestion_rejected(self, event):
        """Handle rejected suggestion"""
        logger.info("Suggestion rejected")
        
        suggestion = event.get('suggestion', {})
        
        # Track outcome
        if 'outcome_tracker' in self.components:
            self.components['outcome_tracker'].track_suggestion_outcome(
                suggestion=suggestion,
                response='reject'
            )
        
        # Update user model
        if 'user_model' in self.components:
            self.components['user_model'].learn_from_feedback(
                suggestion=suggestion,
                response='reject'
            )
    
    def _on_task_completed(self, event):
        """Handle completed task - extract patterns, learn"""
        logger.info(f"Task completed: {event.get('task', {}).get('description', '')[:50]}...")
        
        # Track outcome
        if 'outcome_tracker' in self.components:
            self.components['outcome_tracker'].track_task_outcome(
                task=event.get('task', {}),
                status='success'
            )
        
        # Extract patterns
        if 'pattern_extractor' in self.components:
            patterns = self.components['pattern_extractor'].extract_from_outcome(event)
            for pattern in patterns:
                self.event_bus.publish({
                    'type': 'pattern.extracted',
                    'pattern': pattern
                })
        
        # Update user model
        if 'user_model' in self.components:
            self.components['user_model'].update_from_outcome(event)
        
        # Feed to ALOE
        self._feed_to_aloe('task_completed', 'success', event.get('context', {}))
        
        # Generate proactive suggestions for next steps
        if 'suggestion_engine' in self.components:
            suggestions = self.components['suggestion_engine'].suggest_next_steps(event)
            for suggestion in suggestions:
                if suggestion.get('confidence', 0) >= 0.7:
                    self.event_bus.publish({
                        'type': 'suggestion.offered',
                        'suggestion': suggestion
                    })
    
    def _on_task_failed(self, event):
        """Handle failed task"""
        logger.warning(f"Task failed: {event.get('task', {}).get('description', '')[:50]}...")
        
        # Track outcome
        if 'outcome_tracker' in self.components:
            self.components['outcome_tracker'].track_task_outcome(
                task=event.get('task', {}),
                status='failure',
                error=event.get('error', '')
            )
        
        # Feed to ALOE
        self._feed_to_aloe('task_failed', 'failure', event.get('context', {}))
    
    # Helper Methods
    
    def _auto_prepare(self, prediction: Dict):
        """Silently prepare for predicted need"""
        pred_type = prediction.get('type', '')
        logger.info(f"Auto-preparing for: {pred_type}")
        
        if pred_type == 'crypto_check':
            # Pre-fetch portfolio data
            logger.info("Pre-fetching portfolio data")
            # Implementation would fetch actual data
            self.cache.set('prepared_portfolio', {'status': 'ready'}, ttl=300)
            
        elif pred_type == 'meeting_prep':
            logger.info("Preparing meeting context")
            self.cache.set('prepared_meeting', {'status': 'ready'}, ttl=600)
            
        elif pred_type == 'code_session':
            logger.info("Preparing dev environment")
            self.cache.set('dev_env_ready', True, ttl=1800)
    
    def _should_deliver_now(self, alert: Dict, context: Dict) -> bool:
        """Decide if alert should be delivered immediately"""
        
        # Critical alerts always immediate
        if alert.get('priority') == 'critical':
            return True
        
        # Check user focus
        if context.get('is_focused') and alert.get('priority') != 'high':
            return False
        
        # Check quiet hours
        if context.get('is_quiet_hours'):
            return False
        
        # Check recent alert frequency
        if context.get('recent_alerts', 0) > 3:
            return False
        
        return True
    
    def _send_alert(self, alert: Dict):
        """Send alert to user"""
        logger.info(f"Sending alert: {alert.get('alert_type', 'unknown')}")
        # Implementation would send via appropriate channel
    
    def _execute_suggestion(self, suggestion: Dict) -> Dict:
        """Execute an accepted suggestion"""
        action = suggestion.get('action', '')
        logger.info(f"Executing suggestion: {action}")
        
        # Placeholder implementations
        if action == 'run_scanner':
            return {'status': 'success', 'action': 'scanner_started'}
        elif action == 'commit_changes':
            return {'status': 'success', 'action': 'changes_committed'}
        elif action == 'prepare_summary':
            return {'status': 'success', 'action': 'summary_prepared'}
        else:
            return {'status': 'unknown_action'}
    
    def _trigger_condition_actions(self, event: Dict):
        """Trigger actions for met conditions"""
        logger.info(f"Triggering actions for condition: {event.get('condition', '')}")
    
    def _feed_to_aloe(self, action: str, outcome: str, context: Dict):
        """Feed outcome to ALOE for learning"""
        if not self.config['integration'].get('aloe_feeding', True):
            return
        
        logger.debug(f"Feeding to ALOE: {action} -> {outcome}")
        # Implementation would call ALOE
    
    def get_status(self) -> Dict:
        """Get system status"""
        return {
            'orchestrator': 'running',
            'components': self.component_status,
            'event_bus': {
                'subscribers': len(self.event_bus.subscribers),
                'events_processed': len(self.event_bus.history)
            },
            'cache': {
                'items': len(self.cache._memory_cache)
            }
        }


class PlaceholderComponent:
    """Placeholder for actual components"""
    
    def __init__(self, name: str):
        self.name = name
        self.status = 'initialized'
    
    def start(self):
        self.status = 'running'
    
    def stop(self):
        self.status = 'stopped'
    
    def __getattr__(self, name):
        """Return placeholder method for any attribute"""
        def placeholder(*args, **kwargs):
            logger.debug(f"Placeholder {self.name}.{name} called")
            return []
        return placeholder


def main():
    """Main entry point"""
    orchestrator = ProactiveAIOrchestrator()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'start':
            orchestrator.start()
            # Keep running
            try:
                while True:
                    import time
                    time.sleep(1)
            except KeyboardInterrupt:
                orchestrator.stop()
        
        elif command == 'stop':
            orchestrator.stop()
        
        elif command == 'status':
            status = orchestrator.get_status()
            print(json.dumps(status, indent=2))
        
        elif command == 'event':
            # Publish test event
            if len(sys.argv) > 2:
                event_type = sys.argv[2]
                event = {
                    'type': event_type,
                    'content': 'Test event',
                    'context': {}
                }
                orchestrator.event_bus.publish(event)
                print(f"Published event: {event_type}")
        
        else:
            print(f"Unknown command: {command}")
            print("Usage: python proactive_ai_orchestrator.py [start|stop|status|event <type>]")
    else:
        # Start by default
        orchestrator.start()
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            orchestrator.stop()


if __name__ == '__main__':
    main()
