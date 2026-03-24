"""
Omnibot Task Planner

Breaks goals into executable sub-tasks with dependency management.
Implements task graph for complex workflows.
"""

import uuid
from enum import Enum, auto
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging

logger = logging.getLogger("omnibot.planner")


class TaskStatus(Enum):
    """Task lifecycle states."""
    PENDING = auto()
    READY = auto()
    RUNNING = auto()
    BLOCKED = auto()     # Waiting for dependencies
    COMPLETED = auto()
    FAILED = auto()
    SKIPPED = auto()


class TaskPriority(Enum):
    """Task priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Task:
    """
    Executable task with dependencies and metadata.
    
    Attributes:
        task_id: Unique identifier
        description: Task description
        dependencies: List of task IDs that must complete first
        estimated_time: Estimated completion time in minutes
        required_tools: Tools needed for execution
        checkpoint_before: Require approval before execution
        checkpoint_after: Require approval after execution
        status: Current task status
        priority: Task priority
        created_at: Creation timestamp
        started_at: Execution start timestamp
        completed_at: Completion timestamp
        result: Task execution result
        error: Error message if failed
        metadata: Additional task data
    """
    task_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    description: str = ""
    dependencies: List[str] = field(default_factory=list)
    estimated_time: int = 10
    required_tools: List[str] = field(default_factory=list)
    checkpoint_before: bool = False
    checkpoint_after: bool = False
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_ready(self) -> bool:
        """Check if all dependencies are satisfied."""
        return self.status == TaskStatus.READY
    
    def is_blocked(self) -> bool:
        """Check if task is blocked by dependencies."""
        return self.status == TaskStatus.BLOCKED
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "task_id": self.task_id,
            "description": self.description,
            "dependencies": self.dependencies,
            "estimated_time": self.estimated_time,
            "required_tools": self.required_tools,
            "checkpoint_before": self.checkpoint_before,
            "checkpoint_after": self.checkpoint_after,
            "status": self.status.name,
            "priority": self.priority.name,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "result": self.result,
            "error": self.error,
        }


class TaskPlanner:
    """
    Breaks goals into executable sub-tasks.
    
    Features:
    - Task graph with dependency management
    - Priority-based execution ordering
    - Checkpoint integration
    - Failure recovery planning
    - Progress tracking
    
    Example:
        planner = TaskPlanner()
        
        # Create task graph
        plan = planner.create_plan("Build a website", {
            "intent_type": "design",
            "entities": {"topic": "website", "business": "coffee shop"}
        })
        
        # Get next executable task
        task = planner.get_next_task()
    """
    
    def __init__(self, checkpoint_manager=None):
        """
        Initialize task planner.
        
        Args:
            checkpoint_manager: Optional checkpoint manager for approval gates
        """
        self.tasks: Dict[str, Task] = {}
        self.current_plan: Optional[str] = None
        self.plan_metadata: Dict[str, Any] = {}
        self._checkpoint_manager = checkpoint_manager
        self._execution_order: List[str] = []
        self._failed_tasks: List[str] = []
        self._completed_tasks: List[str] = []
        
        logger.info("TaskPlanner initialized")
    
    def create_plan(self, intent: Any, context: Dict[str, Any]) -> List[Task]:
        """
        Create task graph from intent and context.
        
        Args:
            intent: Parsed intent object
            context: Execution context
            
        Returns:
            List of tasks in dependency order
        """
        intent_type = getattr(intent, "intent_type", "unknown")
        
        # Clear existing tasks
        self.tasks.clear()
        self._execution_order.clear()
        self._failed_tasks.clear()
        self._completed_tasks.clear()
        
        # Create plan based on intent type
        plan_creators = {
            "research": self._create_research_plan,
            "design": self._create_design_plan,
            "code": self._create_code_plan,
            "job_seek": self._create_job_seek_plan,
            "job_execute": self._create_job_execute_plan,
            "query": self._create_query_plan,
            "meta": self._create_meta_plan,
        }
        
        creator = plan_creators.get(intent_type, self._create_generic_plan)
        tasks = creator(intent, context)
        
        # Build dependency graph
        self._build_dependency_graph()
        
        self.current_plan = str(uuid.uuid4())[:8]
        self.plan_metadata = {
            "created_at": datetime.now().isoformat(),
            "intent_type": intent_type,
            "total_tasks": len(tasks),
            "context_summary": str(context)[:200]
        }
        
        logger.info(f"Created plan with {len(tasks)} tasks for intent: {intent_type}")
        
        return tasks
    
    def _create_research_plan(self, intent: Any, context: Dict) -> List[Task]:
        """Create tasks for research intent."""
        query = context.get("entities", {}).get("about_topic", "")
        
        tasks = [
            Task(
                description="Clarify research scope",
                estimated_time=5,
                required_tools=["intent_parser"],
                checkpoint_after=True,
            ),
            Task(
                description=f"Gather information about: {query or 'topic'}",
                estimated_time=15,
                required_tools=["web_search", "browser"],
                dependencies=["*"],  # Requires previous task
            ),
            Task(
                description="Synthesize findings",
                estimated_time=10,
                required_tools=["memory"],
                dependencies=["*"],
            ),
        ]
        
        return self._add_tasks(tasks)
    
    def _create_design_plan(self, intent: Any, context: Dict) -> List[Task]:
        """Create tasks for design intent."""
        topic = context.get("entities", {}).get("for_target", "")
        
        tasks = [
            Task(
                description=f"Define requirements for {topic or 'design'}",
                estimated_time=10,
                required_tools=["intent_parser"],
                checkpoint_after=True,
            ),
            Task(
                description="Create wireframe/mockup",
                estimated_time=20,
                required_tools=["canvas"],
                dependencies=["*"],
            ),
            Task(
                description="Generate design assets",
                estimated_time=30,
                required_tools=["file_write", "canvas"],
                dependencies=["*"],
                checkpoint_before=True,
            ),
        ]
        
        return self._add_tasks(tasks)
    
    def _create_code_plan(self, intent: Any, context: Dict) -> List[Task]:
        """Create tasks for code intent."""
        description = context.get("user_input", "")
        
        tasks = [
            Task(
                description="Analyze requirements and design approach",
                estimated_time=10,
                required_tools=["intent_parser"],
            ),
            Task(
                description="Generate code structure",
                estimated_time=15,
                required_tools=["file_write"],
                dependencies=["*"],
            ),
            Task(
                description="Implement functionality",
                estimated_time=30,
                required_tools=["file_write", "exec"],
                dependencies=["*"],
            ),
            Task(
                description="Test implementation",
                estimated_time=10,
                required_tools=["exec"],
                dependencies=["*"],
            ),
            Task(
                description="Review and finalize",
                estimated_time=5,
                required_tools=["file_read"],
                dependencies=["*"],
                checkpoint_after=True,
            ),
        ]
        
        return self._add_tasks(tasks)
    
    def _create_job_seek_plan(self, intent: Any, context: Dict) -> List[Task]:
        """Create tasks for job seeking intent."""
        tasks = [
            Task(
                description="Clarify job preferences",
                estimated_time=10,
                required_tools=["intent_parser"],
            ),
            Task(
                description="Search job listings",
                estimated_time=20,
                required_tools=["web_search", "browser"],
                dependencies=["*"],
            ),
            Task(
                description="Evaluate matches",
                estimated_time=15,
                required_tools=["memory"],
                dependencies=["*"],
            ),
        ]
        
        return self._add_tasks(tasks)
    
    def _create_job_execute_plan(self, intent: Any, context: Dict) -> List[Task]:
        """Create tasks for job execution intent."""
        tasks = [
            Task(
                description="Review existing task context",
                estimated_time=5,
                required_tools=["memory"],
            ),
            Task(
                description="Execute task steps",
                estimated_time=30,
                required_tools=["exec", "file_write"],
                dependencies=["*"],
            ),
            Task(
                description="Verify completion",
                estimated_time=5,
                required_tools=["file_read"],
                dependencies=["*"],
            ),
        ]
        
        return self._add_tasks(tasks)
    
    def _create_query_plan(self, intent: Any, context: Dict) -> List[Task]:
        """Create tasks for query intent."""
        tasks = [
            Task(
                description="Search memory for answer",
                estimated_time=5,
                required_tools=["memory"],
            ),
            Task(
                description="Formulate response",
                estimated_time=3,
                required_tools=[],
                dependencies=["*"],
            ),
        ]
        
        return self._add_tasks(tasks)
    
    def _create_meta_plan(self, intent: Any, context: Dict) -> List[Task]:
        """Create tasks for meta/system intents."""
        tasks = [
            Task(
                description="Provide system information",
                estimated_time=2,
                required_tools=[],
            ),
        ]
        
        return self._add_tasks(tasks)
    
    def _create_generic_plan(self, intent: Any, context: Dict) -> List[Task]:
        """Create generic tasks for unknown intents."""
        tasks = [
            Task(
                description="Analyze user request",
                estimated_time=5,
                required_tools=["intent_parser"],
                checkpoint_after=True,
            ),
            Task(
                description="Determine best approach",
                estimated_time=5,
                required_tools=[],
                dependencies=["*"],
            ),
        ]
        
        return self._add_tasks(tasks)
    
    def _add_tasks(self, tasks: List[Task]) -> List[Task]:
        """Add tasks to planner and resolve dependencies."""
        task_ids = []
        
        for i, task in enumerate(tasks):
            self.tasks[task.task_id] = task
            task_ids.append(task.task_id)
            
            # Resolve "*" dependency to previous task
            if "*" in task.dependencies and i > 0:
                task.dependencies = [task_ids[i-1] if dep == "*" else dep 
                                   for dep in task.dependencies]
        
        return tasks
    
    def _build_dependency_graph(self):
        """Calculate execution order based on dependencies."""
        # Topological sort
        in_degree: Dict[str, int] = {tid: 0 for tid in self.tasks}
        adj: Dict[str, List[str]] = {tid: [] for tid in self.tasks}
        
        for task_id, task in self.tasks.items():
            for dep in task.dependencies:
                if dep in self.tasks:
                    adj[dep].append(task_id)
                    in_degree[task_id] += 1
        
        # Start with tasks having no dependencies
        queue = [tid for tid, deg in in_degree.items() if deg == 0]
        queue.sort(key=lambda x: self.tasks[x].priority.value, reverse=True)
        
        self._execution_order = []
        
        while queue:
            task_id = queue.pop(0)
            self._execution_order.append(task_id)
            
            # Update status to READY if no dependencies
            if not self.tasks[task_id].dependencies:
                self.tasks[task_id].status = TaskStatus.READY
            
            for neighbor in adj[task_id]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
                    queue.sort(key=lambda x: self.tasks[x].priority.value, reverse=True)
        
        # Mark remaining as BLOCKED if dependencies not satisfied
        for task_id, task in self.tasks.items():
            if task_id not in self._execution_order:
                task.status = TaskStatus.BLOCKED
    
    def get_next_task(self) -> Optional[Task]:
        """
        Get next task ready for execution.
        
        Returns:
            Next ready task or None
        """
        # Check for checkpoint approval first
        for task_id in self._execution_order:
            task = self.tasks[task_id]
            if task.status == TaskStatus.READY:
                # Check for checkpoint manager
                if task.checkpoint_before and self._checkpoint_manager:
                    checkpoint = self._checkpoint_manager.request_approval(
                        action=f"Execute task: {task.description}",
                        context={"task_id": task_id, "plan": self.current_plan},
                        consequences=f"This will execute: {task.description}"
                    )
                    task.status = TaskStatus.BLOCKED  # Wait for approval
                    return None  # Return next time after approval
                
                task.status = TaskStatus.RUNNING
                task.started_at = datetime.now().isoformat()
                return task
            elif task.status == TaskStatus.PENDING:
                # Check if dependencies completed
                deps_satisfied = all(
                    self.tasks[dep].status == TaskStatus.COMPLETED
                    for dep in task.dependencies if dep in self.tasks
                )
                if deps_satisfied:
                    task.status = TaskStatus.READY
                    return self.get_next_task()
        
        return None
    
    def update_status(self, task_id: str, status: TaskStatus, 
                     result: Any = None, error: str = None):
        """
        Update task status.
        
        Args:
            task_id: Task identifier
            status: New status
            result: Execution result
            error: Error message if failed
        """
        if task_id not in self.tasks:
            logger.error(f"Task not found: {task_id}")
            return
        
        task = self.tasks[task_id]
        task.status = status
        
        if status == TaskStatus.COMPLETED:
            task.completed_at = datetime.now().isoformat()
            task.result = result
            self._completed_tasks.append(task_id)
            
            # Trigger checkpoint after if configured
            if task.checkpoint_after and self._checkpoint_manager:
                self._checkpoint_manager.request_approval(
                    action=f"Task completed: {task.description}",
                    context={"task_id": task_id, "result": result},
                    consequences="Task execution finished, continue?"
                )
        
        elif status == TaskStatus.FAILED:
            task.error = error
            self._failed_tasks.append(task_id)
            logger.error(f"Task {task_id} failed: {error}")
        
        logger.debug(f"Task {task_id} status updated to {status.name}")
    
    def handle_failure(self, task_id: str, error: str) -> List[Task]:
        """
        Handle task failure with recovery planning.
        
        Args:
            task_id: Failed task ID
            error: Error message
            
        Returns:
            List of recovery tasks
        """
        if task_id not in self.tasks:
            return []
        
        task = self.tasks[task_id]
        task.status = TaskStatus.FAILED
        task.error = error
        
        # Create recovery tasks
        recovery_tasks = [
            Task(
                description=f"Analyze failure of task {task_id}",
                estimated_time=5,
                required_tools=[],
            ),
            Task(
                description=f"Attempt recovery for: {task.description}",
                estimated_time=task.estimated_time,
                required_tools=task.required_tools,
                dependencies=["*"],
            ),
        ]
        
        recovery_tasks = self._add_tasks(recovery_tasks)
        self._build_dependency_graph()
        
        logger.info(f"Created {len(recovery_tasks)} recovery tasks for {task_id}")
        
        return recovery_tasks
    
    def get_plan_progress(self) -> Dict[str, Any]:
        """Get plan execution progress."""
        total = len(self.tasks)
        if total == 0:
            return {"percent": 0}
        
        completed = sum(1 for t in self.tasks.values() 
                       if t.status == TaskStatus.COMPLETED)
        failed = sum(1 for t in self.tasks.values() 
                    if t.status == TaskStatus.FAILED)
        running = sum(1 for t in self.tasks.values() 
                     if t.status == TaskStatus.RUNNING)
        
        return {
            "plan_id": self.current_plan,
            "total": total,
            "completed": completed,
            "failed": failed,
            "running": running,
            "percent": round((completed / total) * 100, 1),
            "is_complete": completed + failed == total,
        }
    
    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        return self.tasks.get(task_id)
    
    def get_all_tasks(self, status: Optional[TaskStatus] = None) -> List[Task]:
        """
        Get all tasks, optionally filtered by status.
        
        Args:
            status: Filter by status
            
        Returns:
            List of tasks
        """
        if status:
            return [t for t in self.tasks.values() if t.status == status]
        return list(self.tasks.values())
    
    def clear(self):
        """Clear all tasks and reset planner."""
        self.tasks.clear()
        self._execution_order.clear()
        self._failed_tasks.clear()
        self._completed_tasks.clear()
        self.current_plan = None
        self.plan_metadata = {}
        logger.info("Task planner cleared")