"""
Omnibot Core Orchestrator

Central hub that routes requests to appropriate modules.
Implements event-driven architecture with state machine for task lifecycle.
"""

from enum import Enum, auto
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("omnibot.orchestrator")


class OrchestratorState(Enum):
    """State machine states for task lifecycle."""
    IDLE = auto()
    PARSING = auto()
    PLANNING = auto()
    AWAITING_APPROVAL = auto()
    EXECUTING = auto()
    PAUSED = auto()
    COMPLETED = auto()
    FAILED = auto()


@dataclass
class SessionContext:
    """Current session state container."""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    start_time: datetime = field(default_factory=datetime.now)
    current_state: OrchestratorState = OrchestratorState.IDLE
    current_task: Optional[str] = None
    task_queue: List[str] = field(default_factory=list)
    completed_tasks: List[str] = field(default_factory=list)
    messages: List[Dict] = field(default_factory=list, repr=False)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_message(self, role: str, content: str):
        """Add message to session history (max 10)."""
        self.messages.append({
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "content": content
        })
        # Keep only last 10 messages (hot memory limit)
        if len(self.messages) > 10:
            self.messages = self.messages[-10:]


class Orchestrator:
    """
    Central hub for processing user requests and coordinating modules.
    
    Implements event-driven architecture with:
    - Module registry for plugins
    - State machine for task lifecycle
    - Event callbacks for extensibility
    """
    
    def __init__(self, 
                 intent_parser=None, 
                 task_planner=None, 
                 checkpoint_manager=None,
                 memory_manager=None):
        """
        Initialize orchestrator with module dependencies.
        
        Args:
            intent_parser: IntentParser instance
            task_planner: TaskPlanner instance
            checkpoint_manager: CheckpointManager instance
            memory_manager: MemoryManager instance
        """
        self.session = SessionContext()
        self._modules: Dict[str, Any] = {}
        self._event_handlers: Dict[str, List[Callable]] = {}
        self._state_transitions: Dict[tuple, OrchestratorState] = {}
        
        # Register core modules
        self._modules["intent_parser"] = intent_parser
        self._modules["task_planner"] = task_planner
        self._modules["checkpoint_manager"] = checkpoint_manager
        self._modules["memory_manager"] = memory_manager
        
        # Setup default state transitions
        self._setup_state_transitions()
        
        logger.info(f"Orchestrator initialized with session {self.session.session_id}")
    
    def _setup_state_transitions(self):
        """Define valid state transitions."""
        valid_transitions = [
            (OrchestratorState.IDLE, OrchestratorState.PARSING),
            (OrchestratorState.PARSING, OrchestratorState.PLANNING),
            (OrchestratorState.PLANNING, OrchestratorState.AWAITING_APPROVAL),
            (OrchestratorState.PLANNING, OrchestratorState.EXECUTING),
            (OrchestratorState.AWAITING_APPROVAL, OrchestratorState.EXECUTING),
            (OrchestratorState.AWAITING_APPROVAL, OrchestratorState.FAILED),
            (OrchestratorState.EXECUTING, OrchestratorState.PAUSED),
            (OrchestratorState.EXECUTING, OrchestratorState.AWAITING_APPROVAL),
            (OrchestratorState.EXECUTING, OrchestratorState.COMPLETED),
            (OrchestratorState.EXECUTING, OrchestratorState.FAILED),
            (OrchestratorState.PAUSED, OrchestratorState.EXECUTING),
            (OrchestratorState.PAUSED, OrchestratorState.FAILED),
            (OrchestratorState.FAILED, OrchestratorState.IDLE),
            (OrchestratorState.COMPLETED, OrchestratorState.IDLE),
        ]
        for from_state, to_state in valid_transitions:
            self._state_transitions[(from_state, to_state)] = to_state
    
    def _transition_to(self, new_state: OrchestratorState) -> bool:
        """
        Attempt state transition.
        
        Args:
            new_state: Target state
            
        Returns:
            True if transition successful
        """
        current = self.session.current_state
        if (current, new_state) in self._state_transitions or new_state == OrchestratorState.FAILED:
            old_state = self.session.current_state
            self.session.current_state = new_state
            self._emit_event("state_change", {
                "from": old_state.name,
                "to": new_state.name,
                "timestamp": datetime.now().isoformat()
            })
            logger.debug(f"State transition: {old_state.name} -> {new_state.name}")
            return True
        else:
            logger.warning(f"Invalid state transition: {current.name} -> {new_state.name}")
            return False
    
    def register_module(self, name: str, module: Any):
        """
        Register a plugin module.
        
        Args:
            name: Module identifier
            module: Module instance
        """
        self._modules[name] = module
        self._emit_event("module_registered", {"name": name})
        logger.info(f"Module registered: {name}")
    
    def on(self, event_name: str, handler: Callable):
        """
        Register event handler callback.
        
        Args:
            event_name: Event to listen for
            handler: Callback function
        """
        if event_name not in self._event_handlers:
            self._event_handlers[event_name] = []
        self._event_handlers[event_name].append(handler)
    
    def _emit_event(self, event_name: str, data: Dict):
        """Emit event to all registered handlers."""
        handlers = self._event_handlers.get(event_name, [])
        for handler in handlers:
            try:
                handler(data)
            except Exception as e:
                logger.error(f"Event handler error: {e}")
    
    def process_request(self, user_input: str) -> Dict[str, Any]:
        """
        Main entry point for processing user requests.
        
        Flow:
        1. Parse intent from user input
        2. Route to appropriate module
        3. Execute and return results
        
        Args:
            user_input: Raw user request
            
        Returns:
            Processing result with status and data
        """
        # Log user input to session
        self.session.add_message("user", user_input)
        
        # Store in hot memory if available
        if self._modules.get("memory_manager"):
            self._modules["memory_manager"].store_hot("last_input", user_input)
        
        # Transition to parsing state
        self._transition_to(OrchestratorState.PARSING)
        
        try:
            # Parse intent
            intent_parser = self._modules.get("intent_parser")
            if not intent_parser:
                raise RuntimeError("Intent parser not configured")
            
            intent = intent_parser.parse(user_input)
            
            # Route to appropriate handler
            return self.route_to_module(intent, {"user_input": user_input})
            
        except Exception as e:
            self._transition_to(OrchestratorState.FAILED)
            error_result = {
                "status": "error",
                "error": str(e),
                "session_id": self.session.session_id
            }
            self.session.add_message("system", f"Error: {str(e)}")
            return error_result
    
    def route_to_module(self, intent: Any, context: Dict) -> Dict[str, Any]:
        """
        Dispatch intent to appropriate module handler.
        
        Args:
            intent: Parsed intent object
            context: Execution context
            
        Returns:
            Handler result
        """
        intent_type = getattr(intent, "intent_type", "unknown")
        self._emit_event("routing", {"intent": intent_type, "context": context})
        
        # Route based on intent type
        routing_map = {
            "research": self._handle_research,
            "design": self._handle_design,
            "code": self._handle_code,
            "job_seek": self._handle_job_seek,
            "job_execute": self._handle_job_execute,
            "query": self._handle_query,
            "meta": self._handle_meta,
        }
        
        handler = routing_map.get(intent_type, self._handle_unknown)
        return handler(intent, context)
    
    def _handle_research(self, intent, context):
        """Handler for research intents."""
        self._transition_to(OrchestratorState.PLANNING)
        return {"status": "planned", "intent": "research", "next_step": "gather_information"}
    
    def _handle_design(self, intent, context):
        """Handler for design intents."""
        self._transition_to(OrchestratorState.PLANNING)
        return {"status": "planned", "intent": "design", "next_step": "create_prototype"}
    
    def _handle_code(self, intent, context):
        """Handler for code intents."""
        self._transition_to(OrchestratorState.PLANNING)
        return {"status": "planned", "intent": "code", "next_step": "generate_code"}
    
    def _handle_job_seek(self, intent, context):
        """Handler for job seeking intents."""
        self._transition_to(OrchestratorState.PLANNING)
        return {"status": "planned", "intent": "job_seek", "next_step": "search_opportunities"}
    
    def _handle_job_execute(self, intent, context):
        """Handler for job execution intents."""
        self._transition_to(OrchestratorState.EXECUTING)
        return {"status": "executing", "intent": "job_execute", "next_step": "run_task"}
    
    def _handle_query(self, intent, context):
        """Handler for query intents."""
        # Query uses memory manager
        memory = self._modules.get("memory_manager")
        if memory:
            query_text = getattr(intent, "entities", {}).get("query", "")
            result = memory.recall(query_text)
            return {"status": "success", "intent": "query", "result": result}
        return {"status": "error", "intent": "query", "error": "Memory not available"}
    
    def _handle_meta(self, intent, context):
        """Handler for meta/system intents."""
        return {
            "status": "success",
            "intent": "meta",
            "response": "I am Omnibot, an intelligent task automation system with human-in-the-loop oversight."
        }
    
    def _handle_unknown(self, intent, context):
        """Handler for unknown intents."""
        return {"status": "unknown", "intent": "unknown", "message": "I don't understand that request type"}
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current task status.
        
        Returns:
            Status dictionary with session info
        """
        return {
            "session_id": self.session.session_id,
            "state": self.session.current_state.name,
            "current_task": self.session.current_task,
            "task_queue_length": len(self.session.task_queue),
            "completed_tasks_count": len(self.session.completed_tasks),
            "uptime_seconds": (datetime.now() - self.session.start_time).total_seconds()
        }
    
    def pause(self) -> bool:
        """
        Pause current execution (for long tasks).
        
        Returns:
            True if successfully paused
        """
        if self.session.current_state == OrchestratorState.EXECUTING:
            self._transition_to(OrchestratorState.PAUSED)
            self._emit_event("paused", {"session_id": self.session.session_id})
            logger.info("Orchestrator paused")
            return True
        return False
    
    def resume(self) -> bool:
        """
        Resume paused execution.
        
        Returns:
            True if successfully resumed
        """
        if self.session.current_state == OrchestratorState.PAUSED:
            self._transition_to(OrchestratorState.EXECUTING)
            self._emit_event("resumed", {"session_id": self.session.session_id})
            logger.info("Orchestrator resumed")
            return True
        return False
    
    def reset(self):
        """Reset session to initial state."""
        self.session = SessionContext()
        self._transition_to(OrchestratorState.IDLE)
        logger.info("Orchestrator reset")