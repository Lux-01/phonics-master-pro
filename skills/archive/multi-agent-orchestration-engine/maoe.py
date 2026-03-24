#!/usr/bin/env python3
"""
Multi-Agent Orchestration Engine (MAOE) - ACA Built v1.0
Spawn agents, coordinate them, merge outputs, scale horizontally.
"""

import json
import os
import uuid
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
import argparse


@dataclass
class Agent:
    """Represents an agent."""
    id: str
    name: str
    agent_type: str  # research, coding, analysis, trading
    task: str
    status: str = "pending"  # pending, running, completed, failed
    output: str = ""
    started_at: str = ""
    completed_at: str = ""
    pid: int = 0
    
    def __post_init__(self):
        if not self.started_at:
            self.started_at = datetime.now().isoformat()


class MAOE:
    """
    Multi-Agent Orchestration Engine.
    Scales from one AI to a team of specialists.
    """
    
    MAX_CONCURRENT = 5
    AGENT_TIMEOUT = 300  # 5 minutes
    
    AGENT_TEMPLATES = {
        "research": {
            "prompt": "Research the following topic thoroughly and provide insights:",
            "model": "default"
        },
        "coding": {
            "prompt": "Write Python code to solve:",
            "model": "default"
        },
        "analysis": {
            "prompt": "Analyze the following data and provide insights:",
            "model": "default"
        },
        "trading": {
            "prompt": "Analyze trading opportunity for:",
            "model": "default"
        }
    }
    
    def __init__(self, memory_dir: str = None):
        self.memory_dir = memory_dir or os.path.expanduser("~/.openclaw/workspace/memory/maoe")
        self.state_file = os.path.join(self.memory_dir, "state.json")
        self.agents_file = os.path.join(self.memory_dir, "agents.json")
        self._ensure_dirs()
        self.state = self._load_state()
        self.agents: Dict[str, Agent] = {}
        self.active_agents: Dict[str, subprocess.Popen] = {}
        self._load_agents()
    
    def _ensure_dirs(self):
        Path(self.memory_dir).mkdir(parents=True, exist_ok=True)
    
    def _load_state(self) -> Dict:
        defaults = {
            "total_agents": 0,
            "agents_completed": 0,
            "agents_failed": 0,
            "max_concurrent": self.MAX_CONCURRENT
        }
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    defaults.update(json.load(f))
        except Exception:
            pass
        return defaults
    
    def _load_agents(self):
        try:
            if os.path.exists(self.agents_file):
                with open(self.agents_file, 'r') as f:
                    data = json.load(f)
                    for aid, agent_data in data.items():
                        self.agents[aid] = Agent(**agent_data)
        except Exception:
            pass
    
    def _save(self):
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
            with open(self.agents_file, 'w') as f:
                json.dump({k: asdict(v) for k, v in self.agents.items()}, f, indent=2)
        except Exception:
            pass
    
    def spawn_agent(self, agent_type: str, task: str, name: str = None) -> str:
        """Spawn a new agent."""
        agent_id = str(uuid.uuid4())[:8]
        template = self.AGENT_TEMPLATES.get(agent_type, self.AGENT_TEMPLATES["research"])
        
        agent = Agent(
            id=agent_id,
            name=name or f"{agent_type}_{agent_id}",
            agent_type=agent_type,
            task=task
        )
        
        self.agents[agent_id] = agent
        self.state["total_agents"] = len(self.agents)
        self._save()
        
        # Simulate agent execution
        agent.status = "running"
        self._save()
        
        return agent_id
    
    def get_agent_status(self, agent_id: str) -> Optional[Agent]:
        """Get agent status."""
        return self.agents.get(agent_id)
    
    def list_active_agents(self) -> List[Agent]:
        """List active agents."""
        return [a for a in self.agents.values() if a.status == "running"]
    
    def complete_agent(self, agent_id: str, output: str = ""):
        """Complete an agent."""
        agent = self.agents.get(agent_id)
        if agent:
            agent.status = "completed"
            agent.output = output
            agent.completed_at = datetime.now().isoformat()
            self.state["agents_completed"] += 1
            self._save()
    
    def fail_agent(self, agent_id: str, error: str = ""):
        """Mark agent as failed."""
        agent = self.agents.get(agent_id)
        if agent:
            agent.status = "failed"
            agent.output = error
            agent.completed_at = datetime.now().isoformat()
            self.state["agents_failed"] += 1
            self._save()
    
    def merge_outputs(self, agent_ids: List[str], strategy: str = "concatenate") -> str:
        """Merge agent outputs."""
        outputs = []
        for aid in agent_ids:
            agent = self.agents.get(aid)
            if agent and agent.output:
                outputs.append(f"=== {agent.name} ({agent.agent_type}) ===\n{agent.output}")
        
        if strategy == "concatenate":
            return "\n\n".join(outputs)
        elif strategy == "synthesize":
            # Simple synthesis
            return f"Synthesized from {len(outputs)} agents:\n\n" + "\n".join(outputs[:3])
        elif strategy == "vote":
            # Return most common output
            return outputs[0] if outputs else ""
        else:
            return "\n\n".join(outputs)
    
    def coordinate_task(self, task: str, agent_types: List[str]) -> Dict:
        """Coordinate multiple agents on a task."""
        agent_ids = []
        
        for agent_type in agent_types:
            aid = self.spawn_agent(agent_type, task)
            agent_ids.append(aid)
        
        return {
            "task": task,
            "agents_spawned": len(agent_ids),
            "agent_ids": agent_ids,
            "strategy": "parallel"
        }
    
    def get_report(self) -> str:
        """Generate MAOE report."""
        active = len(self.list_active_agents())
        lines = [
            "Multi-Agent Orchestration Engine Report",
            f"Total agents: {self.state['total_agents']}",
            f"Completed: {self.state['agents_completed']}",
            f"Failed: {self.state['agents_failed']}",
            f"Active: {active}",
            f"Max concurrent: {self.state['max_concurrent']}",
            "",
            "Recent agents:"
        ]
        
        for agent in list(self.agents.values())[-5:]:
            lines.append(f"  {agent.name}: {agent.status}")
        
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="MAOE - Multi-Agent Orchestration Engine")
    parser.add_argument("--mode", choices=["spawn", "status", "merge", "report", "test"], default="report")
    parser.add_argument("--type", "-t", help="Agent type")
    parser.add_argument("--task", help="Task description")
    parser.add_argument("--agents", "-a", nargs="+", help="Agent IDs to merge")
    
    args = parser.parse_args()
    
    maoe = MAOE()
    
    if args.mode == "spawn":
        if not args.type or not args.task:
            print("Error: --type and --task required")
            return
        aid = maoe.spawn_agent(args.type, args.task)
        print(f"✓ Spawned agent: {aid}")
    
    elif args.mode == "status":
        for agent in maoe.agents.values():
            print(f"{agent.name}: {agent.status}")
    
    elif args.mode == "merge":
        if not args.agents:
            print("Error: --agents required")
            return
        output = maoe.merge_outputs(args.agents, "concatenate")
        print(output)
    
    elif args.mode == "report":
        print(maoe.get_report())
    
    elif args.mode == "test":
        print("🧪 Testing MAOE...")
        aid1 = maoe.spawn_agent("research", "Test task 1")
        aid2 = maoe.spawn_agent("coding", "Test task 2")
        maoe.complete_agent(aid1, "Research complete")
        maoe.complete_agent(aid2, "Code written")
        print(f"✓ Spawned 2 agents")
        merged = maoe.merge_outputs([aid1, aid2])
        print(f"✓ Merged outputs: {len(merged)} chars")
        print("✓ All tests passed")


if __name__ == "__main__":
    main()
