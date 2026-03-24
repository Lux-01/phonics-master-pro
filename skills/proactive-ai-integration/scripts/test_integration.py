#!/usr/bin/env python3
"""
Integration Test for Proactive AI Layer
Tests all components and event flow.
"""

import json
import sys
import time
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from proactive_ai_orchestrator import (
    ProactiveAIOrchestrator, 
    EventBus, 
    ComponentCache,
    PlaceholderComponent
)


def test_event_bus():
    """Test event bus functionality"""
    print("\n" + "="*50)
    print("Testing Event Bus")
    print("="*50)
    
    bus = EventBus(persistence_path="/tmp/test_events.jsonl")
    
    events_received = []
    
    def handler(event):
        events_received.append(event)
        print(f"✓ Received: {event['type']}")
    
    # Subscribe
    bus.subscribe('test.event', handler)
    bus.subscribe('test.*', handler)  # Wildcard
    
    # Publish events
    test_events = [
        {'type': 'test.event', 'data': 'hello'},
        {'type': 'test.other', 'data': 'world'},
        {'type': 'test.event', 'data': 'again'}
    ]
    
    for event in test_events:
        bus.publish(event)
        time.sleep(0.1)
    
    # Verify (2 specific + 2 wildcard matches for 'test.event' = 4 total)
    assert len(events_received) >= 2, f"Expected at least 2 events, got {len(events_received)}"
    print(f"✓ Event bus working: {len(events_received)} events processed")
    
    # Cleanup
    Path("/tmp/test_events.jsonl").unlink(missing_ok=True)
    
    return True


def test_cache():
    """Test cache functionality"""
    print("\n" + "="*50)
    print("Testing Component Cache")
    print("="*50)
    
    cache = ComponentCache(cache_dir="/tmp/test_cache")
    
    # Test set/get
    cache.set('test_key', {'data': 'value'})
    result = cache.get('test_key')
    assert result == {'data': 'value'}, "Cache get/set failed"
    print("✓ Cache set/get working")
    
    # Test TTL
    cache.set('ttl_key', 'value', ttl=1)
    assert cache.get('ttl_key') == 'value', "TTL value not stored"
    time.sleep(1.5)
    assert cache.get('ttl_key') is None, "TTL not expired"
    print("✓ Cache TTL working")
    
    # Cleanup
    cache.clear()
    import shutil
    shutil.rmtree("/tmp/test_cache", ignore_errors=True)
    
    return True


def test_orchestrator_init():
    """Test orchestrator initialization"""
    print("\n" + "="*50)
    print("Testing Orchestrator Initialization")
    print("="*50)
    
    orch = ProactiveAIOrchestrator(config_path="/tmp/test_config.yaml")
    
    # Check components initialized
    assert 'predictive_engine' in orch.components, "Predictive engine not initialized"
    assert 'proactive_monitor' in orch.components, "Proactive monitor not initialized"
    assert 'suggestion_engine' in orch.components, "Suggestion engine not initialized"
    assert 'outcome_tracker' in orch.components, "Outcome tracker not initialized"
    assert 'pattern_extractor' in orch.components, "Pattern extractor not initialized"
    assert 'user_model' in orch.components, "User model not initialized"
    
    print("✓ All 6 components initialized")
    
    # Check event bus
    assert orch.event_bus is not None, "Event bus not initialized"
    assert len(orch.event_bus.subscribers) > 0, "No event subscribers registered"
    print(f"✓ Event bus initialized with {len(orch.event_bus.subscribers)} subscriber types")
    
    # Check cache
    assert orch.cache is not None, "Cache not initialized"
    print("✓ Cache initialized")
    
    return True


def test_event_flow():
    """Test end-to-end event flow"""
    print("\n" + "="*50)
    print("Testing Event Flow")
    print("="*50)
    
    orch = ProactiveAIOrchestrator(config_path="/tmp/test_config.yaml")
    
    # Track events
    events_processed = []
    
    def tracker(event):
        events_processed.append(event['type'])
    
    orch.event_bus.subscribe('*', tracker)
    
    # Publish test events
    test_events = [
        {'type': 'user.message', 'content': 'Hello', 'context': {}},
        {'type': 'monitor.alert', 'alert_type': 'test', 'priority': 'low'},
        {'type': 'task.completed', 'task': {'description': 'Test task'}, 'context': {}},
        {'type': 'suggestion.accepted', 'suggestion': {'action': 'test'}, 'context': {}}
    ]
    
    for event in test_events:
        orch.event_bus.publish(event)
        time.sleep(0.1)
    
    # Verify events processed
    print(f"✓ Published {len(test_events)} events")
    print(f"✓ Processed {len(events_processed)} events")
    
    # Check specific handlers were called
    assert 'user.message' in events_processed, "User message not processed"
    assert 'monitor.alert' in events_processed, "Monitor alert not processed"
    assert 'task.completed' in events_processed, "Task completed not processed"
    assert 'suggestion.accepted' in events_processed, "Suggestion accepted not processed"
    
    print("✓ All event types processed correctly")
    
    return True


def test_status():
    """Test status reporting"""
    print("\n" + "="*50)
    print("Testing Status Reporting")
    print("="*50)
    
    orch = ProactiveAIOrchestrator(config_path="/tmp/test_config.yaml")
    
    status = orch.get_status()
    
    assert 'orchestrator' in status, "Orchestrator status missing"
    assert 'components' in status, "Components status missing"
    assert 'event_bus' in status, "Event bus status missing"
    assert 'cache' in status, "Cache status missing"
    
    print("✓ Status report generated")
    print(f"  - Components: {len(status['components'])}")
    print(f"  - Event subscribers: {status['event_bus']['subscribers']}")
    print(f"  - Cache items: {status['cache']['items']}")
    
    return True


def test_config_loading():
    """Test configuration loading"""
    print("\n" + "="*50)
    print("Testing Configuration Loading")
    print("="*50)
    
    orch = ProactiveAIOrchestrator(config_path="/tmp/test_config.yaml")
    
    # Check default config loaded
    assert 'components' in orch.config, "Components config missing"
    assert 'predictive_engine' in orch.config['components'], "Predictive engine config missing"
    assert 'proactive_monitor' in orch.config['components'], "Proactive monitor config missing"
    
    # Check thresholds
    pe_config = orch.config['components']['predictive_engine']
    assert 'auto_prepare_threshold' in pe_config, "Auto-prepare threshold missing"
    assert 'suggest_threshold' in pe_config, "Suggest threshold missing"
    
    print("✓ Configuration loaded successfully")
    print(f"  - Auto-prepare threshold: {pe_config['auto_prepare_threshold']}")
    print(f"  - Suggest threshold: {pe_config['suggest_threshold']}")
    
    return True


def run_all_tests():
    """Run all integration tests"""
    print("\n" + "="*60)
    print("PROACTIVE AI INTEGRATION TESTS")
    print("="*60)
    
    tests = [
        ("Event Bus", test_event_bus),
        ("Component Cache", test_cache),
        ("Orchestrator Init", test_orchestrator_init),
        ("Event Flow", test_event_flow),
        ("Status Reporting", test_status),
        ("Config Loading", test_config_loading)
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n✅ {name}: PASSED")
            else:
                failed += 1
                print(f"\n❌ {name}: FAILED")
        except Exception as e:
            failed += 1
            print(f"\n❌ {name}: ERROR - {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*60)
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
