#!/usr/bin/env python3
"""
Omnibot Phase 1 Tests

Run with: cd .. && PYTHONDONTWRITEBYTECODE=1 python3 tests/test_phase1.py
"""

# Pre-import stdlib modules that may conflict with local folder names
import uuid
import json
from datetime import datetime

import sys
import logging

sys.path.insert(0, '/home/skux/.openclaw/workspace/skills/omnibot')

logging.basicConfig(level=logging.WARNING)

from core.orchestrator import Orchestrator, OrchestratorState
from core.checkpoint_manager import CheckpointManager, Checkpoint, CheckpointStatus, ActionType
from core.intent_parser import IntentParser, Intent, IntentType
from core.task_planner import TaskPlanner, Task, TaskStatus, TaskPriority
from memory.memory_manager import MemoryManager

def run_tests():
    print()
    print('=' * 60)
    print('RUNNING PHASE 1 FUNCTIONALITY TESTS')
    print('=' * 60)
    print()
    
    # Test 1: Orchestrator State Transitions
    print('TEST 1: Orchestrator State Machine')
    orch = Orchestrator()
    assert orch.get_status()['state'] == 'IDLE', 'Initial state should be IDLE'
    orch._transition_to(OrchestratorState.PARSING)
    assert orch.get_status()['state'] == 'PARSING', 'Should transition to PARSING'
    orch._transition_to(OrchestratorState.PLANNING)
    assert orch.get_status()['state'] == 'PLANNING', 'Should transition to PLANNING'
    print('   ✅ State transitions working')
    
    # Test 2: Intent Parsing
    print('TEST 2: Intent Parser')
    parser = IntentParser()
    intents = [
        ('Create a website', IntentType.DESIGN.value),
        ('Find info about Python', IntentType.RESEARCH.value),
        ('Write a script', IntentType.CODE.value),
        ('What did we decide?', IntentType.QUERY.value),
    ]
    for text, expected_type in intents:
        intent = parser.parse(text)
        assert intent.intent_type == expected_type, f'Expected {expected_type} for "{text}"'
    print(f'   ✅ {len(intents)} intent types parsed correctly')
    
    # Test 3: Hot Memory
    print('TEST 3: Hot Memory (RAM)')
    memory = MemoryManager()
    memory.store_hot('key1', 'value1')
    memory.store_hot('key2', {'nested': 'data'})
    assert memory.get_hot('key1') == 'value1'
    assert memory.get_hot('key2')['nested'] == 'data'
    print('   ✅ Hot memory storage/retrieval working')
    
    # Test 4: Warm Memory (Daily Files)
    print('TEST 4: Warm Memory (Daily Logs)')
    memory.store_warm('Test log entry', category='test')
    entries = memory.get_warm(category='test')
    assert len(entries) > 0
    assert 'Test log entry' in entries[0]
    print('   ✅ Warm memory logging working')
    
    # Test 5: Cold Memory (Curated)
    print('TEST 5: Cold Memory (Long-term)')
    memory.store_cold('test_fact', 'Important info', section='important_facts')
    retrieved = memory.get_cold('test_fact', section='important_facts')
    assert retrieved == 'Important info'
    print('   ✅ Cold memory persistence working')
    
    # Test 6: Recall Across Tiers
    print('TEST 6: Cross-Tier Recall')
    memory.store_hot('search_term', 'hot data')
    memory.store_cold('search_term', 'cold data', section='important_facts')
    results = memory.recall('search_term')
    assert len(results['hot']) > 0 or len(results['cold']) > 0
    print('   ✅ Cross-tier recall working')
    
    # Test 7: Checkpoint Manager
    print('TEST 7: Checkpoint Manager')
    cp_mgr = CheckpointManager()
    assert cp_mgr.check_permission('file_read') == False  # Auto-execute
    assert cp_mgr.check_permission('email_send') == True  # Human required
    cp = cp_mgr.request_approval('Test action', {}, 'Test consequences')
    assert cp.status == CheckpointStatus.PENDING
    assert len(cp_mgr.get_pending()) == 1
    print('   ✅ Checkpoint creation working')
    
    # Test 8: Task Planner
    print('TEST 8: Task Planner')
    planner = TaskPlanner()
    
    class MockIntent:
        intent_type = 'code'
    
    tasks = planner.create_plan(MockIntent(), {'user_input': 'Build a script'})
    assert len(tasks) > 0
    progress = planner.get_plan_progress()
    assert progress['total'] == len(tasks)
    print(f'   ✅ Task planning ({len(tasks)} tasks) working')
    
    # Test 9: End-to-End Flow
    print('TEST 9: End-to-End Integration')
    orch2 = Orchestrator(
        intent_parser=parser,
        task_planner=planner,
        checkpoint_manager=cp_mgr,
        memory_manager=memory
    )
    result = orch2.process_request('Create a website')
    assert 'status' in result
    assert 'intent' in result
    print(f'   ✅ End-to-end flow: {result["status"]} -> {result["intent"]}')
    
    print()
    print('=' * 60)
    print('🎉 ALL PHASE 1 TESTS PASSED')
    print('=' * 60)
    print()
    print('MODULES BUILT:')
    print('  1. ✅ Core Orchestrator')
    print('  2. ✅ Memory Manager (Hot/Warm/Cold tiers)')
    print('  3. ✅ Checkpoint Manager')
    print('  4. ✅ Intent Parser')
    print('  5. ✅ Task Planner')
    print()
    print('STATUS: Ready for Phase 2 (Safety + Research)')
    return True

if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)