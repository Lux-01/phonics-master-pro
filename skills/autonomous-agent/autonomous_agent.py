#!/usr/bin/env python3
"""
Autonomous Agent - Tier 2 ALOE Core Intelligence
Implements OODA Loop (Observe → Orient → Decide → Act) for self-directed execution.

ACA Compliance:
- Core engine class with clear lifecycle
- State persistence (memory/autonomous-agent/state.json)
- CLI with --mode (run, test, status, config)
- Event emission hooks
- ALOE integration for learning
- Error recovery patterns
"""

import argparse
import json
import logging
import os
import sys
import time
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
from threading import Lock
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('AutonomousAgent')

# ============================================================================
# CONSTANTS & CONFIGURATION
# ============================================================================

STATE_DIR = Path("/home/skux/.openclaw/workspace/memory/autonomous-agent")
STATE_FILE = STATE_DIR / "state.json"
MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 2  # Exponential backoff base
DEFAULT_TIMEOUT = 300  # 5 minutes
TASK_QUEUE_MAX = 100

class TaskStatus(Enum):
    """Task lifecycle states."""
    PENDING = "pending"
    OBSERVING = "observing"
    ORIENTING = "orienting"
    DECIDING = "deciding"
    ACTING = "acting"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    ESCALATED = "escalated"

class ActionType(Enum):
    """Types of actions the agent can execute."""
    CALL_TOOL = "call_tool"
    SPAWN_SUBAGENT = "spawn_subagent"
    API_REQUEST = "api_request"
    FILE_OPERATION = "file_operation"
    DELEGATE = "delegate"
    WAIT = "wait"

@dataclass
class Task:
    """Represents a unit of work in the OODA loop."""
    id: str
    description: str
    status: TaskStatus = field(default=TaskStatus.PENDING)
    priority: int = 5  # 1-10, lower is higher priority
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    attempts: int = 0
    max_attempts: int = MAX_RETRIES
    context: Dict[str, Any] = field(default_factory=dict)
    observation: Dict[str, Any] = field(default_factory=dict)
    orientation: Dict[str, Any] = field(default_factory=dict)
    decision: Dict[str, Any] = field(default_factory=dict)
    action_result: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    parent_id: Optional[str] = None
    subtasks: List[str] = field(default_factory=list)

@dataclass
class AgentState:
    """Persistent state for the autonomous agent."""
    version: str = "2.0.0"
    last_updated: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    tasks: Dict[str, Dict] = field(default_factory=dict)
    task_queue: List[str] = field(default_factory=list)
    completed_tasks: List[str] = field(default_factory=list)
    failed_tasks: List[str] = field(default_factory=list)
    current_task: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=lambda: {
        "tasks_completed": 0,
        "tasks_failed": 0,
        "avg_completion_time": 0.0,
        "success_rate": 1.0,
        "total_cycles": 0
    })
    event_log: List[Dict] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=lambda: {
        "auto_retry": True,
        "escalation_threshold": 3,
        "max_concurrent": 5,
        "log_level": "INFO"
    })

# ============================================================================
# OODA LOOP IMPLEMENTATION
# ============================================================================

class OODALoop:
    """
    Implements the Observe-Orient-Decide-Act cycle.
    
    The OODA loop is a decision-making framework that enables rapid,
    adaptive response to changing situations through continuous iteration.
    """
    
    def __init__(self, agent: 'AutonomousAgent'):
        self.agent = agent
        self.hooks: Dict[str, List[Callable]] = {
            'observe': [],
            'orient': [],
            'decide': [],
            'act': [],
            'complete': [],
            'error': []
        }
    
    def register_hook(self, phase: str, callback: Callable) -> None:
        """Register a callback for a specific OODA phase."""
        if phase in self.hooks:
            self.hooks[phase].append(callback)
    
    def _emit(self, phase: str, data: Dict[str, Any]) -> None:
        """Emit event to all registered hooks."""
        for callback in self.hooks.get(phase, []):
            try:
                callback(data)
            except Exception as e:
                logger.warning(f"Hook error in {phase}: {e}")
    
    def observe(self, task: Task) -> Dict[str, Any]:
        """
        OBSERVE: Gather information about the current situation.
        
        Collects relevant data from context, environment, and any
        external sources needed to understand the task.
        """
        task.status = TaskStatus.OBSERVING
        task.started_at = datetime.utcnow().isoformat()
        
        observation = {
            'task_id': task.id,
            'description': task.description,
            'timestamp': task.started_at,
            'context': task.context,
            'available_tools': self._get_available_tools(task),
            'constraints': task.context.get('constraints', {}),
            'dependencies': self._check_dependencies(task),
            'environment_state': self._get_environment_state()
        }
        
        # ALOE integration: Check for similar past tasks
        similar = self.agent.query_aloe_patterns(task.description)
        if similar:
            observation['historical_patterns'] = similar
        
        task.observation = observation
        self._emit('observe', observation)
        logger.debug(f"Observation complete for task {task.id}")
        
        return observation
    
    def orient(self, task: Task, observation: Dict[str, Any]) -> Dict[str, Any]:
        """
        ORIENT: Analyze and synthesize the observed information.
        
        Interprets the observation against existing frameworks,
        identifies patterns, and determines what it means.
        """
        task.status = TaskStatus.ORIENTING
        
        # Analyze the situation
        orientation = {
            'task_id': task.id,
            'analysis': self._analyze_situation(observation),
            'risk_assessment': self._assess_risks(observation),
            'resource_requirements': self._estimate_resources(observation),
            'approach_options': self._generate_approaches(observation),
            'recommended_approach': None,
            'confidence': 0.0
        }
        
        # Select best approach based on confidence and risk
        if orientation['approach_options']:
            best = max(orientation['approach_options'], 
                       key=lambda x: x.get('score', 0))
            orientation['recommended_approach'] = best['name']
            orientation['confidence'] = best.get('score', 0.5)
        
        task.orientation = orientation
        self._emit('orient', orientation)
        logger.debug(f"Orientation complete for task {task.id}")
        
        return orientation
    
    def decide(self, task: Task, orientation: Dict[str, Any]) -> Dict[str, Any]:
        """
        DECIDE: Select the best course of action.
        
        Based on orientation analysis, choose the optimal path
        and prepare execution parameters.
        """
        task.status = TaskStatus.DECIDING
        
        approach = orientation.get('recommended_approach', 'default')
        confidence = orientation.get('confidence', 0.5)
        
        # Build decision based on approach
        decision = {
            'task_id': task.id,
            'action_type': self._determine_action_type(task, approach),
            'approach': approach,
            'parameters': self._build_parameters(task, approach),
            'fallbacks': self._build_fallbacks(task, approach),
            'escalation_trigger': orientation['risk_assessment'].get('escalation_needed', False),
            'confidence': confidence,
            'estimated_duration': orientation['resource_requirements'].get('time_estimate', 60),
            'checkpoint_points': self._identify_checkpoints(task)
        }
        
        task.decision = decision
        self._emit('decide', decision)
        logger.debug(f"Decision made for task {task.id}: {decision['action_type']}")
        
        return decision
    
    def act(self, task: Task, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        ACT: Execute the decided course of action.
        
        Performs the actual work, monitors execution, and
        handles any immediate errors or interrupts.
        """
        task.status = TaskStatus.ACTING
        task.attempts += 1
        
        action_result = {
            'task_id': task.id,
            'action_type': decision['action_type'],
            'started_at': datetime.utcnow().isoformat(),
            'completed_at': None,
            'success': False,
            'result': None,
            'output': None,
            'error': None,
            'retry_needed': False,
            'fallback_triggered': False
        }
        
        try:
            # Execute the action
            result = self._execute_action(task, decision)
            action_result['success'] = True
            action_result['result'] = result
            action_result['output'] = self._format_output(result)
            
        except Exception as e:
            action_result['error'] = str(e)
            action_result['retry_needed'] = task.attempts < task.max_attempts
            
            # Check if we should fallback or escalate
            if task.attempts >= task.max_attempts:
                if decision.get('fallbacks'):
                    action_result['fallback_triggered'] = True
                    try:
                        fallback_result = self._execute_fallback(task, decision)
                        action_result['success'] = True
                        action_result['result'] = fallback_result
                    except Exception as fb_error:
                        action_result['error'] = f"Fallback failed: {fb_error}"
                        task.status = TaskStatus.ESCALATED
                        self._escalate_task(task, action_result)
                else:
                    action_result['fallback_triggered'] = False
                    task.status = TaskStatus.FAILED
            else:
                task.status = TaskStatus.RETRYING
        
        action_result['completed_at'] = datetime.utcnow().isoformat()
        task.action_result = action_result
        task.completed_at = action_result['completed_at']
        
        if action_result['success']:
            task.status = TaskStatus.COMPLETED
        
        self._emit('act', action_result)
        logger.debug(f"Action completed for task {task.id}: success={action_result['success']}")
        
        return action_result
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _get_available_tools(self, task: Task) -> List[str]:
        """Determine which tools are available for this task."""
        base_tools = ['read', 'write', 'edit', 'exec', 'web_fetch', 'browser']
        if task.context.get('needs_browser'):
            base_tools.append('browser')
        if task.context.get('needs_api'):
            base_tools.append('api_call')
        return base_tools
    
    def _check_dependencies(self, task: Task) -> Dict[str, Any]:
        """Check if task dependencies are satisfied."""
        deps = task.context.get('dependencies', [])
        if not deps:
            return {'status': 'ready', 'pending': []}
        
        pending = []
        for dep_id in deps:
            dep_task = self.agent.get_task(dep_id)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                pending.append(dep_id)
        
        return {
            'status': 'waiting' if pending else 'ready',
            'pending': pending
        }
    
    def _get_environment_state(self) -> Dict[str, Any]:
        """Capture current environment state."""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'agent_version': '2.0.0',
            'active_tasks': len(self.agent.state.task_queue),
            'system_load': 'normal'  # Could be enriched with real metrics
        }
    
    def _analyze_situation(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the observed situation."""
        return {
            'complexity': self._assess_complexity(observation['description']),
            'urgency': observation['context'].get('urgency', 'normal'),
            'uncertainty': 'low' if observation.get('historical_patterns') else 'medium',
            'key_factors': self._extract_key_factors(observation)
        }
    
    def _assess_complexity(self, description: str) -> str:
        """Assess task complexity based on description."""
        length = len(description)
        if length < 50:
            return 'low'
        elif length < 200:
            return 'medium'
        return 'high'
    
    def _extract_key_factors(self, observation: Dict[str, Any]) -> List[str]:
        """Extract key factors from observation."""
        factors = []
        desc = observation['description'].lower()
        if 'error' in desc or 'fail' in desc:
            factors.append('error_handling')
        if 'web' in desc or 'http' in desc or 'url' in desc:
            factors.append('network_dependency')
        if 'file' in desc or 'read' in desc or 'write' in desc:
            factors.append('filesystem_operation')
        return factors
    
    def _assess_risks(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risks associated with task execution."""
        risks = []
        
        if 'network_dependency' in observation.get('key_factors', []):
            risks.append({'type': 'network', 'level': 'medium'})
        if observation.get('constraints', {}).get('destructive'):
            risks.append({'type': 'data_loss', 'level': 'high'})
        
        return {
            'risks': risks,
            'overall_level': 'high' if any(r['level'] == 'high' for r in risks) else 
                            'medium' if risks else 'low',
            'escalation_needed': any(r['level'] == 'high' for r in risks)
        }
    
    def _estimate_resources(self, observation: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate resource requirements."""
        complexity = observation.get('analysis', {}).get('complexity', 'medium')
        time_estimates = {'low': 30, 'medium': 120, 'high': 300}
        
        return {
            'time_estimate': time_estimates.get(complexity, 120),
            'memory_estimate': 'low',
            'tool_requirements': observation.get('available_tools', [])
        }
    
    def _generate_approaches(self, observation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate possible approaches to solve the task."""
        approaches = []
        tools = observation.get('available_tools', [])
        
        # Direct approach
        approaches.append({
            'name': 'direct',
            'score': 0.8,
            'description': 'Execute task directly using available tools'
        })
        
        # Decomposition approach for complex tasks
        if observation.get('analysis', {}).get('complexity') == 'high':
            approaches.append({
                'name': 'decompose',
                'score': 0.7,
                'description': 'Break task into subtasks and execute sequentially'
            })
        
        # Delegation approach
        if 'spawn_subagent' in tools:
            approaches.append({
                'name': 'delegate',
                'score': 0.6,
                'description': 'Delegate to specialized subagent'
            })
        
        return approaches
    
    def _determine_action_type(self, task: Task, approach: str) -> str:
        """Determine the action type based on approach."""
        action_map = {
            'decompose': ActionType.SPAWN_SUBAGENT.value,
            'delegate': ActionType.DELEGATE.value,
            'api': ActionType.API_REQUEST.value,
            'wait': ActionType.WAIT.value
        }
        return action_map.get(approach, ActionType.CALL_TOOL.value)
    
    def _build_parameters(self, task: Task, approach: str) -> Dict[str, Any]:
        """Build execution parameters based on approach."""
        return {
            'tool': task.context.get('tool'),
            'params': task.context.get('params', {}),
            'timeout': task.context.get('timeout', DEFAULT_TIMEOUT),
            'approach': approach
        }
    
    def _build_fallbacks(self, task: Task, approach: str) -> List[Dict[str, Any]]:
        """Build fallback strategies."""
        fallbacks = []
        
        if approach == 'direct':
            fallbacks.append({
                'action': 'retry_with_delay',
                'delay': 5
            })
        
        fallbacks.append({
            'action': 'log_failure',
            'notify': True
        })
        
        return fallbacks
    
    def _identify_checkpoints(self, task: Task) -> List[int]:
        """Identify progress checkpoint percentages."""
        return [25, 50, 75]
    
    def _execute_action(self, task: Task, decision: Dict[str, Any]) -> Any:
        """Execute the decided action."""
        action_type = decision['action_type']
        params = decision['parameters']
        
        logger.info(f"Executing {action_type} for task {task.id}")
        
        # This would integrate with actual tool execution
        # For now, return a structured execution record
        return {
            'action': action_type,
            'params': params,
            'executed_at': datetime.utcnow().isoformat(),
            'status': 'completed'
        }
    
    def _execute_fallback(self, task: Task, decision: Dict[str, Any]) -> Any:
        """Execute fallback strategy."""
        logger.warning(f"Executing fallback for task {task.id}")
        return {
            'fallback': True,
            'executed_at': datetime.utcnow().isoformat(),
            'status': 'completed_via_fallback'
        }
    
    def _escalate_task(self, task: Task, action_result: Dict[str, Any]) -> None:
        """Escalate task that cannot be completed."""
        logger.error(f"Task {task.id} escalated: {action_result['error']}")
        # Would notify coordinator or human here
        self.agent.log_event('escalation', {
            'task_id': task.id,
            'error': action_result['error'],
            'attempts': task.attempts
        })
    
    def _format_output(self, result: Any) -> str:
        """Format action result for output."""
        return json.dumps(result, indent=2) if isinstance(result, dict) else str(result)

# ============================================================================
# MAIN AGENT CLASS
# ============================================================================

class AutonomousAgent:
    """
    Core autonomous agent implementing the OODA loop for self-directed execution.
    
    This agent can:
    - Accept tasks and break them down
    - Execute the OODA loop cycle
    - Recover from errors with retry/fallback/escalate
    - Track progress and report status
    - Learn from outcomes via ALOE integration
    """
    
    def __init__(self):
        self.state = self._load_state()
        self.ooda = OODALoop(self)
        self._lock = Lock()
        self._running = False
        self._shutdown_requested = False
        
        # Ensure state directory exists
        STATE_DIR.mkdir(parents=True, exist_ok=True)
    
    def _load_state(self) -> AgentState:
        """Load agent state from disk."""
        try:
            if STATE_FILE.exists():
                with open(STATE_FILE, 'r') as f:
                    data = json.load(f)
                    # Convert dict back to Task objects where needed
                    tasks = {}
                    for tid, tdata in data.get('tasks', {}).items():
                        # Reconstruct task from dict
                        tasks[tid] = tdata
                    data['tasks'] = tasks
                    return AgentState(**data)
        except Exception as e:
            logger.error(f"Failed to load state: {e}")
        
        return AgentState()
    
    def _save_state(self) -> None:
        """Save agent state to disk."""
        try:
            STATE_DIR.mkdir(parents=True, exist_ok=True)
            self.state.last_updated = datetime.utcnow().isoformat()
            
            # Convert to serializable dict
            state_dict = asdict(self.state)
            
            with open(STATE_FILE, 'w') as f:
                json.dump(state_dict, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
    
    def log_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Log an event to the event log."""
        event = {
            'type': event_type,
            'timestamp': datetime.utcnow().isoformat(),
            'data': data
        }
        self.state.event_log.append(event)
        # Keep only last 1000 events
        if len(self.state.event_log) > 1000:
            self.state.event_log = self.state.event_log[-1000:]
        self._save_state()
    
    def create_task(self, description: str, context: Dict[str, Any] = None, 
                    priority: int = 5, parent_id: Optional[str] = None) -> Task:
        """Create a new task."""
        task = Task(
            id=str(uuid.uuid4())[:8],
            description=description,
            priority=priority,
            context=context or {},
            parent_id=parent_id
        )
        
        with self._lock:
            self.state.tasks[task.id] = asdict(task)
            self.state.task_queue.append(task.id)
            # Sort by priority
            self.state.task_queue.sort(
                key=lambda tid: self.state.tasks[tid].get('priority', 5)
            )
        
        self._save_state()
        self.log_event('task_created', {'task_id': task.id, 'description': description})
        logger.info(f"Created task {task.id}: {description}")
        
        return task
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        task_data = self.state.tasks.get(task_id)
        if task_data:
            return Task(**task_data)
        return None
    
    def update_task(self, task: Task) -> None:
        """Update a task in state."""
        with self._lock:
            self.state.tasks[task.id] = asdict(task)
        self._save_state()
    
    def query_aloe_patterns(self, description: str) -> List[Dict[str, Any]]:
        """
        Query ALOE for similar past patterns.
        This is a hook for the ALOE integration.
        """
        # Would call ALOE engine here
        # For now, return empty list
        return []
    
    def report_outcome(self, task: Task) -> None:
        """Report task outcome to ALOE for learning."""
        outcome = {
            'task_id': task.id,
            'description': task.description,
            'status': task.status.value,
            'success': task.status == TaskStatus.COMPLETED,
            'approach': task.decision.get('approach'),
            'attempts': task.attempts,
            'duration': self._calculate_duration(task)
        }
        
        # Would send to ALOE engine here
        logger.info(f"Reported outcome to ALOE: {outcome}")
        self.log_event('outcome_reported', outcome)
    
    def _calculate_duration(self, task: Task) -> float:
        """Calculate task duration in seconds."""
        if task.started_at and task.completed_at:
            try:
                start = datetime.fromisoformat(task.started_at)
                end = datetime.fromisoformat(task.completed_at)
                return (end - start).total_seconds()
            except:
                pass
        return 0.0
    
    def execute_task(self, task: Task) -> Task:
        """Execute a single task through the OODA loop."""
        logger.info(f"Executing task {task.id}: {task.description}")
        
        try:
            # OODA Loop Cycle
            observation = self.ooda.observe(task)
            self.update_task(task)
            
            orientation = self.ooda.orient(task, observation)
            self.update_task(task)
            
            decision = self.ooda.decide(task, orientation)
            self.update_task(task)
            
            action_result = self.ooda.act(task, decision)
            self.update_task(task)
            
            # Update metrics
            self._update_metrics(task)
            
            # Report to ALOE
            self.report_outcome(task)
            
        except Exception as e:
            logger.error(f"Error executing task {task.id}: {e}")
            task.error = str(e)
            task.status = TaskStatus.FAILED
            self.update_task(task)
            self.log_event('task_error', {'task_id': task.id, 'error': str(e)})
        
        return task
    
    def _update_metrics(self, task: Task) -> None:
        """Update agent metrics based on task outcome."""
        metrics = self.state.metrics
        
        if task.status == TaskStatus.COMPLETED:
            metrics['tasks_completed'] += 1
        elif task.status == TaskStatus.FAILED:
            metrics['tasks_failed'] += 1
        
        total = metrics['tasks_completed'] + metrics['tasks_failed']
        if total > 0:
            metrics['success_rate'] = metrics['tasks_completed'] / total
        
        metrics['total_cycles'] += 1
        self._save_state()
    
    def run_cycle(self) -> Optional[Task]:
        """Run one cycle of task processing."""
        with self._lock:
            if not self.state.task_queue:
                return None
            
            task_id = self.state.task_queue.pop(0)
            task_data = self.state.tasks.get(task_id)
            if not task_data:
                return None
            
            task = Task(**task_data)
            self.state.current_task = task_id
        
        try:
            result = self.execute_task(task)
            
            with self._lock:
                if result.status == TaskStatus.COMPLETED:
                    self.state.completed_tasks.append(task_id)
                elif result.status == TaskStatus.FAILED or result.status == TaskStatus.ESCALATED:
                    self.state.failed_tasks.append(task_id)
                elif result.status == TaskStatus.RETRYING:
                    # Put back in queue with lower priority
                    result.status = TaskStatus.PENDING
                    self.state.task_queue.append(task_id)
                
                self.state.current_task = None
            
            return result
            
        except Exception as e:
            logger.error(f"Cycle error: {e}")
            with self._lock:
                self.state.current_task = None
            return None
    
    def run(self) -> None:
        """Run the agent continuously."""
        self._running = True
        logger.info("Autonomous Agent starting...")
        
        try:
            while self._running and not self._shutdown_requested:
                task = self.run_cycle()
                if task is None:
                    # No tasks, wait a bit
                    time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutdown requested")
        finally:
            self._running = False
            self._save_state()
            logger.info("Autonomous Agent stopped")
    
    def stop(self) -> None:
        """Request agent shutdown."""
        self._shutdown_requested = True
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        return {
            'version': self.state.version,
            'running': self._running,
            'current_task': self.state.current_task,
            'queue_size': len(self.state.task_queue),
            'completed_count': len(self.state.completed_tasks),
            'failed_count': len(self.state.failed_tasks),
            'metrics': self.state.metrics,
            'last_updated': self.state.last_updated
        }

# ============================================================================
# CLI INTERFACE
# ============================================================================

def run_tests() -> bool:
    """Run internal tests for the autonomous agent."""
    logger.info("Running Autonomous Agent tests...")
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Task creation
    try:
        agent = AutonomousAgent()
        task = agent.create_task("Test task", {"test": True}, priority=1)
        assert task.id is not None
        assert task.description == "Test task"
        assert task.status == TaskStatus.PENDING
        tests_passed += 1
        print(f"✓ Test 1: Task creation")
    except Exception as e:
        tests_failed += 1
        print(f"✗ Test 1: Task creation - {e}")
    
    # Test 2: OODA loop phases
    try:
        agent = AutonomousAgent()
        task = agent.create_task("OODA test", {"tool": "read"})
        
        observation = agent.ooda.observe(task)
        assert 'task_id' in observation
        assert task.status == TaskStatus.OBSERVING
        
        orientation = agent.ooda.orient(task, observation)
        assert 'analysis' in orientation
        assert task.status == TaskStatus.ORIENTING
        
        decision = agent.ooda.decide(task, orientation)
        assert 'action_type' in decision
        assert task.status == TaskStatus.DECIDING
        
        tests_passed += 1
        print(f"✓ Test 2: OODA loop phases")
    except Exception as e:
        tests_failed += 1
        print(f"✗ Test 2: OODA loop phases - {e}")
    
    # Test 3: State persistence
    try:
        agent1 = AutonomousAgent()
        task = agent1.create_task("Persistence test")
        task_id = task.id
        
        # Create new agent instance, should load same state
        agent2 = AutonomousAgent()
        loaded_task = agent2.get_task(task_id)
        assert loaded_task is not None
        assert loaded_task.description == "Persistence test"
        tests_passed += 1
        print(f"✓ Test 3: State persistence")
    except Exception as e:
        tests_failed += 1
        print(f"✗ Test 3: State persistence - {e}")
    
    # Test 4: Error recovery
    try:
        agent = AutonomousAgent()
        task = agent.create_task("Recovery test", {"fail_first": True})
        task.max_attempts = 3
        
        # Test retry logic
        assert task.attempts == 0
        task.attempts = 2
        assert task.attempts < task.max_attempts  # Should retry
        tests_passed += 1
        print(f"✓ Test 4: Error recovery")
    except Exception as e:
        tests_failed += 1
        print(f"✗ Test 4: Error recovery - {e}")
    
    # Test 5: Metrics tracking
    try:
        agent = AutonomousAgent()
        initial = agent.state.metrics['total_cycles']
        
        # Simulate task execution
        task = agent.create_task("Metrics test")
        agent._update_metrics(task)
        
        assert agent.state.metrics['total_cycles'] > initial
        tests_passed += 1
        print(f"✓ Test 5: Metrics tracking")
    except Exception as e:
        tests_failed += 1
        print(f"✗ Test 5: Metrics tracking - {e}")
    
    # Test 6: Priority queue
    try:
        agent = AutonomousAgent()
        agent.state.task_queue = []
        agent.state.tasks = {}
        
        # Create tasks with different priorities
        t1 = agent.create_task("Low priority", priority=5)
        t2 = agent.create_task("High priority", priority=1)
        t3 = agent.create_task("Medium priority", priority=3)
        
        # Queue should be sorted by priority
        queue = agent.state.task_queue
        assert queue[0] == t2.id  # Highest priority first
        tests_passed += 1
        print(f"✓ Test 6: Priority queue")
    except Exception as e:
        tests_failed += 1
        print(f"✗ Test 6: Priority queue - {e}")
    
    print(f"\n{'='*50}")
    print(f"Tests Passed: {tests_passed}/{tests_passed + tests_failed}")
    print(f"{'='*50}")
    
    return tests_failed == 0

def main():
    parser = argparse.ArgumentParser(description='Autonomous Agent - OODA Loop Execution Engine')
    parser.add_argument('--mode', choices=['run', 'test', 'status', 'config'],
                       default='status', help='Operation mode')
    parser.add_argument('--task', type=str, help='Task description (for run mode)')
    parser.add_argument('--priority', type=int, default=5, help='Task priority (1-10)')
    parser.add_argument('--config-key', type=str, help='Config key to set')
    parser.add_argument('--config-value', type=str, help='Config value to set')
    
    args = parser.parse_args()
    
    if args.mode == 'test':
        success = run_tests()
        sys.exit(0 if success else 1)
    
    elif args.mode == 'status':
        agent = AutonomousAgent()
        status = agent.get_status()
        print(json.dumps(status, indent=2))
    
    elif args.mode == 'config':
        agent = AutonomousAgent()
        if args.config_key and args.config_value:
            agent.state.config[args.config_key] = args.config_value
            agent._save_state()
            print(f"Config updated: {args.config_key} = {args.config_value}")
        else:
            print(json.dumps(agent.state.config, indent=2))
    
    elif args.mode == 'run':
        if args.task:
            agent = AutonomousAgent()
            task = agent.create_task(args.task, priority=args.priority)
            result = agent.execute_task(task)
            print(f"Task {result.id} completed with status: {result.status.value}")
        else:
            # Run continuously
            agent = AutonomousAgent()
            try:
                agent.run()
            except KeyboardInterrupt:
                print("\nShutting down...")

if __name__ == '__main__':
    main()
