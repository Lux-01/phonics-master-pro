#!/usr/bin/env python3
"""
Multi-Agent Coordinator (MAC)
Spawn, manage, and coordinate multiple sub-agents working in parallel.
Scale from one mind to a team of minds.
"""

import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import uuid

# Paths
MAC_DIR = Path("/home/skux/.openclaw/workspace/skills/multi-agent-coordinator")
DATA_DIR = MAC_DIR / "data"
STATE_FILE = DATA_DIR / "state.json"
AGENTS_DIR = DATA_DIR / "agents"
TASKS_DIR = DATA_DIR / "tasks"

for d in [MAC_DIR, DATA_DIR, AGENTS_DIR, TASKS_DIR]:
    d.mkdir(parents=True, exist_ok=True)


class AgentType(Enum):
    RESEARCH = "research"
    TRADING = "trading"
    WRITING = "writing"
    DATA_CLEANING = "data_cleaning"
    RISK_ANALYSIS = "risk_analysis"
    NARRATIVE_MAPPING = "narrative_mapping"


class AgentStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Agent:
    id: str
    type: AgentType
    task: str
    params: Dict
    status: AgentStatus = AgentStatus.PENDING
    result: Optional[Dict] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    confidence: float = 0.7
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.type.value,
            "task": self.task,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "confidence": self.confidence
        }


@dataclass
class Task:
    id: str
    description: str
    agents: List[Agent] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    final_output: Optional[Dict] = None
    merge_strategy: str = "integration"  # concat / integration / consensus
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "description": self.description,
            "status": self.status.value,
            "agents": [a.to_dict() for a in self.agents],
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "merge_strategy": self.merge_strategy
        }


class MultiAgentCoordinator:
    """
    Coordinates multiple agents working in parallel.
    """
    
    def __init__(self):
        self.data_dir = DATA_DIR
        self.agents_dir = AGENTS_DIR
        self.tasks_dir = TASKS_DIR
        self.active_tasks: Dict[str, Task] = {}
        self.agent_pool: Dict[str, Agent] = {}
        self.max_concurrent = 10
        
        # Agent capabilities
        self.agent_capabilities = {
            AgentType.RESEARCH: {
                "description": "Information gathering and web research",
                "strengths": ["web_search", "api_queries", "documentation"],
                "typical_duration": 60
            },
            AgentType.TRADING: {
                "description": "Crypto analysis and signal detection",
                "strengths": ["token_scanning", "market_analysis", "risk_assessment"],
                "typical_duration": 45
            },
            AgentType.WRITING: {
                "description": "Content creation and documentation",
                "strengths": ["summaries", "reports", "documentation"],
                "typical_duration": 30
            },
            AgentType.DATA_CLEANING: {
                "description": "Data processing and normalization",
                "strengths": ["formatting", "deduplication", "validation"],
                "typical_duration": 40
            },
            AgentType.RISK_ANALYSIS: {
                "description": "Risk assessment and danger detection",
                "strengths": ["contract_audit", "investment_risk", "compliance"],
                "typical_duration": 50
            },
            AgentType.NARRATIVE_MAPPING: {
                "description": "Trend tracking and story analysis",
                "strengths": ["topic_extraction", "sentiment", "influencer_tracking"],
                "typical_duration": 35
            }
        }
    
    def spawn_agent(self, agent_type: AgentType, task: str, 
                   params: Dict = None, timeout: int = 300) -> Agent:
        """Spawn a new agent."""
        
        agent_id = f"AGENT-{uuid.uuid4().hex[:8]}"
        
        agent = Agent(
            id=agent_id,
            type=agent_type,
            task=task,
            params=params or {},
            status=AgentStatus.PENDING
        )
        
        self.agent_pool[agent_id] = agent
        
        # Simulate agent execution (in production: actual spawn)
        try:
            asyncio.create_task(self._execute_agent(agent))
        except RuntimeError:
            # No event loop running - execute synchronously
            agent.status = AgentStatus.RUNNING
            agent.started_at = datetime.now()
            agent.result = {
                "agent_type": agent.type.value,
                "task": agent.task,
                "output": f"Completed {agent.task}",
                "confidence": 0.85,
                "data": agent.params
            }
            agent.status = AgentStatus.COMPLETED
            agent.completed_at = datetime.now()
            agent.confidence = 0.85
            self._save_agent(agent)
        
        return agent
    
    async def _execute_agent(self, agent: Agent):
        """Execute agent task."""
        agent.status = AgentStatus.RUNNING
        agent.started_at = datetime.now()
        
        # Simulate work (in production: actual agent execution)
        await asyncio.sleep(1)
        
        # Generate simulated result
        agent.result = {
            "agent_type": agent.type.value,
            "task": agent.task,
            "output": f"Completed {agent.task}",
            "confidence": 0.85,
            "data": agent.params
        }
        
        agent.status = AgentStatus.COMPLETED
        agent.completed_at = datetime.now()
        agent.confidence = 0.85
        
        # Save agent state
        self._save_agent(agent)
    
    def coordinate_task(self, description: str, 
                       agent_configs: List[Dict],
                       merge_strategy: str = "integration") -> Task:
        """
        Coordinate multiple agents on a task.
        
        Example:
            task = mac.coordinate_task(
                "Research Solana DEXs",
                [
                    {"type": AgentType.RESEARCH, "task": "Research Jupiter DEX"},
                    {"type": AgentType.RESEARCH, "task": "Research Orca DEX"},
                    {"type": AgentType.RESEARCH, "task": "Research Raydium DEX"}
                ],
                merge_strategy="integration"
            )
        """
        
        task_id = f"TASK-{uuid.uuid4().hex[:8]}"
        
        task = Task(
            id=task_id,
            description=description,
            merge_strategy=merge_strategy
        )
        
        # Spawn agents
        for config in agent_configs:
            agent = self.spawn_agent(
                agent_type=config.get("type", AgentType.RESEARCH),
                task=config.get("task", "Unknown task"),
                params=config.get("params", {}),
                timeout=config.get("timeout", 300)
            )
            task.agents.append(agent)
        
        self.active_tasks[task_id] = task
        
        # Start coordination
        try:
            asyncio.create_task(self._coordinate_task(task))
        except RuntimeError:
            # No event loop - execute synchronously
            task.status = TaskStatus.IN_PROGRESS
            
            # Wait for all agents to complete (they're already done in sync mode)
            # Merge results
            task.final_output = self._merge_results(task.agents, task.merge_strategy)
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            
            # Save task
            self._save_task(task)
        
        return task
    
    async def _coordinate_task(self, task: Task):
        """Coordinate agent execution and merge results."""
        
        task.status = TaskStatus.IN_PROGRESS
        
        # Wait for all agents to complete
        while any(a.status in [AgentStatus.PENDING, AgentStatus.RUNNING] 
                  for a in task.agents):
            await asyncio.sleep(0.5)
        
        # Check for failures
        failed = [a for a in task.agents if a.status == AgentStatus.FAILED]
        if failed:
            task.status = TaskStatus.FAILED
            return
        
        # Merge results
        task.final_output = self._merge_results(task.agents, task.merge_strategy)
        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now()
        
        # Save task
        self._save_task(task)
    
    def _merge_results(self, agents: List[Agent], strategy: str) -> Dict:
        """Merge agent results based on strategy."""
        
        if strategy == "concat":
            # Simple concatenation
            return {
                "strategy": "concat",
                "sections": [
                    {
                        "agent": a.type.value,
                        "output": a.result.get("output", "")
                    }
                    for a in agents if a.result
                ]
            }
        
        elif strategy == "integration":
            # Interleaved based on dependencies
            return {
                "strategy": "integration",
                "executive_summary": self._generate_summary(agents),
                "detailed_findings": [
                    {
                        "agent": a.type.value,
                        "task": a.task,
                        "result": a.result,
                        "confidence": a.confidence
                    }
                    for a in agents if a.result
                ],
                "consensus": self._calculate_consensus(agents)
            }
        
        elif strategy == "consensus":
            # Resolve conflicts
            return {
                "strategy": "consensus",
                "agreement": self._calculate_consensus(agents),
                "conflicts": self._detect_conflicts(agents),
                "resolution": self._resolve_conflicts(agents)
            }
        
        else:
            return {
                "strategy": "unknown",
                "agents": len(agents)
            }
    
    def _generate_summary(self, agents: List[Agent]) -> str:
        """Generate executive summary from agent results."""
        summaries = []
        for agent in agents:
            if agent.result:
                summaries.append(f"{agent.type.value}: {agent.result.get('output', '')}")
        
        return " | ".join(summaries)
    
    def _calculate_consensus(self, agents: List[Agent]) -> Dict:
        """Calculate consensus across agents."""
        
        confidences = [a.confidence for a in agents if a.confidence]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        return {
            "agent_count": len(agents),
            "completed": len([a for a in agents if a.status == AgentStatus.COMPLETED]),
            "average_confidence": round(avg_confidence, 2),
            "consensus_level": "high" if avg_confidence > 0.8 else "medium" if avg_confidence > 0.6 else "low"
        }
    
    def _detect_conflicts(self, agents: List[Agent]) -> List[Dict]:
        """Detect conflicts between agents."""
        conflicts = []
        
        # Simple conflict detection (in production: semantic analysis)
        for i, a1 in enumerate(agents):
            for a2 in agents[i+1:]:
                if a1.result and a2.result:
                    # Check for contradictory outputs
                    if "bullish" in str(a1.result) and "bearish" in str(a2.result):
                        conflicts.append({
                            "agents": [a1.id, a2.id],
                            "type": "sentiment_conflict",
                            "severity": "medium"
                        })
        
        return conflicts
    
    def _resolve_conflicts(self, agents: List[Agent]) -> Dict:
        """Resolve conflicts between agents."""
        conflicts = self._detect_conflicts(agents)
        
        if not conflicts:
            return {"status": "no_conflicts"}
        
        # Resolution strategy: confidence-based
        resolutions = []
        for conflict in conflicts:
            # In production: more sophisticated resolution
            resolutions.append({
                "conflict": conflict,
                "resolution": "present_both",
                "reasoning": "Both perspectives have merit"
            })
        
        return {
            "status": "conflicts_resolved",
            "conflicts_found": len(conflicts),
            "resolutions": resolutions
        }
    
    def get_task_status(self, task_id: str) -> Optional[Task]:
        """Get task status."""
        return self.active_tasks.get(task_id)
    
    def get_active_tasks(self) -> List[Task]:
        """Get all active tasks."""
        return [t for t in self.active_tasks.values() 
                if t.status in [TaskStatus.PENDING, TaskStatus.IN_PROGRESS]]
    
    def get_agent_status(self, agent_id: str) -> Optional[Agent]:
        """Get agent status."""
        return self.agent_pool.get(agent_id)
    
    def get_stats(self) -> Dict:
        """Get coordinator statistics."""
        
        all_agents = list(self.agent_pool.values())
        all_tasks = list(self.active_tasks.values())
        
        return {
            "total_agents_spawned": len(all_agents),
            "active_agents": len([a for a in all_agents if a.status == AgentStatus.RUNNING]),
            "completed_agents": len([a for a in all_agents if a.status == AgentStatus.COMPLETED]),
            "failed_agents": len([a for a in all_agents if a.status == AgentStatus.FAILED]),
            "total_tasks": len(all_tasks),
            "active_tasks": len([t for t in all_tasks if t.status == TaskStatus.IN_PROGRESS]),
            "completed_tasks": len([t for t in all_tasks if t.status == TaskStatus.COMPLETED]),
            "agent_types": self._count_agent_types(all_agents)
        }
    
    def _count_agent_types(self, agents: List[Agent]) -> Dict[str, int]:
        """Count agents by type."""
        counts = {}
        for agent in agents:
            counts[agent.type.value] = counts.get(agent.type.value, 0) + 1
        return counts
    
    def _save_agent(self, agent: Agent):
        """Save agent state."""
        agent_file = self.agents_dir / f"{agent.id}.json"
        with open(agent_file, 'w') as f:
            json.dump(agent.to_dict(), f, indent=2)
    
    def _save_task(self, task: Task):
        """Save task state."""
        task_file = self.tasks_dir / f"{task.id}.json"
        with open(task_file, 'w') as f:
            json.dump(task.to_dict(), f, indent=2)


# Global instance
mac = MultiAgentCoordinator()


def spawn(agent_type: str, task: str, **kwargs) -> Agent:
    """Quick spawn function."""
    atype = AgentType(agent_type) if agent_type in [t.value for t in AgentType] else AgentType.RESEARCH
    return mac.spawn_agent(atype, task, kwargs)


def coordinate(description: str, agents: List[Dict], merge: str = "integration") -> Task:
    """Quick coordinate function."""
    return mac.coordinate_task(description, agents, merge)


def get_stats() -> Dict:
    """Quick get stats function."""
    return mac.get_stats()


if __name__ == "__main__":
    print("🤖 Multi-Agent Coordinator (MAC)")
    print("=" * 60)
    
    # Example: Coordinate research task
    print("\n🎯 Coordinating: Research Solana DEXs")
    
    task = coordinate(
        "Research Solana DEXs",
        [
            {"type": AgentType.RESEARCH, "task": "Research Jupiter DEX features"},
            {"type": AgentType.RESEARCH, "task": "Research Orca DEX features"},
            {"type": AgentType.RESEARCH, "task": "Research Raydium DEX features"}
        ],
        merge="integration"
    )
    
    print(f"   Task ID: {task.id}")
    print(f"   Agents spawned: {len(task.agents)}")
    
    # Wait for completion (simulated)
    import time
    time.sleep(2)
    
    # Check status
    task_status = mac.get_task_status(task.id)
    if task_status:
        print(f"\n📊 Task Status: {task_status.status.value}")
        print(f"   Agents completed: {len([a for a in task_status.agents if a.status == AgentStatus.COMPLETED])}")
        
        if task_status.final_output:
            print(f"\n📄 Final Output:")
            print(f"   Strategy: {task_status.final_output.get('strategy')}")
            print(f"   Summary: {task_status.final_output.get('executive_summary', 'N/A')[:100]}...")
    
    # Stats
    print(f"\n📈 Stats: {json.dumps(get_stats(), indent=2)}")
    
    print(f"\n✅ MAC ready for multi-agent coordination!")
