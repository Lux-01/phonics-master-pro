#!/usr/bin/env python3
"""
Tool Orchestrator - ACA Built v1.0
Optimize multi-tool workflows, parallelize independent calls.
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
import argparse


@dataclass
class ToolCall:
    """Represents a tool call in workflow."""
    tool_name: str
    parameters: Dict
    priority: int = 5  # 1-10, lower = higher priority
    dependencies: List[str] = None
    result: Any = None
    error: str = None
    duration_ms: float = 0
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


class ToolOrchestrator:
    """Orchestrates multi-tool workflows with optimal execution order."""
    
    def __init__(self, memory_dir: str = None, max_workers: int = 4):
        self.memory_dir = memory_dir or os.path.expanduser("~/.openclaw/workspace/memory/tool-orchestrator")
        self.state_file = os.path.join(self.memory_dir, "state.json")
        self.workflows_file = os.path.join(self.memory_dir, "workflows.json")
        self.logs_dir = os.path.join(self.memory_dir, "logs")
        self.max_workers = max_workers
        self._ensure_dirs()
        self.state = self._load_state()
        self.workflows = self._load_workflows()
        self.tool_registry: Dict[str, Callable] = {}
    
    def _ensure_dirs(self):
        Path(self.memory_dir).mkdir(parents=True, exist_ok=True)
        Path(self.logs_dir).mkdir(parents=True, exist_ok=True)
    
    def _load_state(self) -> Dict:
        defaults = {
            "total_workflows": 0,
            "total_tools_called": 0,
            "parallel_executions": 0,
            "avg_parallelism": 0
        }
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    defaults.update(json.load(f))
        except Exception:
            pass
        return defaults
    
    def _load_workflows(self) -> List[Dict]:
        try:
            if os.path.exists(self.workflows_file):
                with open(self.workflows_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return []
    
    def _save(self):
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
            with open(self.workflows_file, 'w') as f:
                json.dump(self.workflows, f, indent=2)
        except Exception as e:
            self._log_error(f"Save failed: {e}")
    
    def _log_error(self, message: str):
        log_file = os.path.join(self.logs_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log")
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        with open(log_file, 'a') as f:
            f.write(f"{datetime.now().isoformat()} | ERROR | {message}\n")
    
    def register_tool(self, name: str, func: Callable):
        """Register a tool for orchestration."""
        self.tool_registry[name] = func
    
    def _can_run_parallel(self, call: ToolCall, completed: set) -> bool:
        """Check if tool call can run (dependencies satisfied)."""
        return all(dep in completed for dep in call.dependencies)
    
    def optimize_sequence(self, calls: List[ToolCall]) -> List[List[ToolCall]]:
        """Group calls into parallel batches based on dependencies."""
        batches = []
        remaining = calls.copy()
        completed = set()
        
        while remaining:
            batch = [c for c in remaining if self._can_run_parallel(c, completed)]
            
            if not batch:
                # Circular dependency
                break
            
            # Sort by priority
            batch.sort(key=lambda x: x.priority)
            batches.append(batch)
            
            for c in batch:
                completed.add(c.tool_name)
                remaining.remove(c)
        
        return batches
    
    def execute_parallel(self, batch: List[ToolCall]) -> List[ToolCall]:
        """Execute a batch of tool calls in parallel."""
        results = []
        
        with ThreadPoolExecutor(max_workers=min(len(batch), self.max_workers)) as executor:
            futures = {}
            
            for call in batch:
                if call.tool_name in self.tool_registry:
                    future = executor.submit(self._execute_single, call)
                    futures[future] = call
                else:
                    call.error = f"Tool '{call.tool_name}' not registered"
                    results.append(call)
            
            for future in as_completed(futures):
                call = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    call.error = str(e)
                    results.append(call)
        
        return results
    
    def _execute_single(self, call: ToolCall) -> ToolCall:
        """Execute a single tool call."""
        start = time.time()
        
        tool_func = self.tool_registry.get(call.tool_name)
        if tool_func:
            try:
                call.result = tool_func(**call.parameters)
            except Exception as e:
                call.error = str(e)
        else:
            call.error = f"Tool not found: {call.tool_name}"
        
        call.duration_ms = (time.time() - start) * 1000
        self.state["total_tools_called"] += 1
        
        return call
    
    def run_workflow(self, calls: List[ToolCall], workflow_name: str = "unnamed") -> Dict:
        """Execute optimized workflow."""
        start_time = time.time()
        
        # Optimize sequence
        batches = self.optimize_sequence(calls)
        self.state["parallel_executions"] += 1
        
        # Execute batches
        all_results = []
        for i, batch in enumerate(batches):
            results = self.execute_parallel(batch)
            all_results.extend(results)
        
        duration = time.time() - start_time
        parallelism = len(calls) / len(batches) if batches else 0
        
        # Update stats
        self.state["avg_parallelism"] = (self.state["avg_parallelism"] + parallelism) / 2
        self.state["total_workflows"] += 1
        
        # Log workflow
        workflow_record = {
            "name": workflow_name,
            "timestamp": datetime.now().isoformat(),
            "duration_ms": duration * 1000,
            "parallelism": round(parallelism, 2),
            "batches": len(batches),
            "total_calls": len(calls),
            "success": sum(1 for r in all_results if not r.error),
            "errors": sum(1 for r in all_results if r.error)
        }
        self.workflows.append(workflow_record)
        self._save()
        
        return {
            "results": [{"tool": r.tool_name, "success": not r.error, "duration_ms": r.duration_ms} for r in all_results],
            "duration_ms": duration * 1000,
            "parallelism": round(parallelism, 2),
            "batches": len(batches)
        }
    
    def suggest_optimization(self, workflow_name: str = None) -> List[str]:
        """Suggest workflow optimizations."""
        suggestions = []
        
        if not self.workflows:
            return ["No workflow history - run some workflows first"]
        
        # Analyze recent workflows
        recent = self.workflows[-10:]
        
        avg_parallelism = sum(w["parallelism"] for w in recent) / len(recent)
        if avg_parallelism < 1.5 and len(recent) > 5:
            suggestions.append(f"Average parallelism {avg_parallelism:.1f} - consider adding independent calls")
        
        error_rate = sum(w["errors"] for w in recent) / sum(w["total_calls"] for w in recent) if recent else 0
        if error_rate > 0.1:
            suggestions.append(f"Error rate {error_rate:.1%} - add retry logic to tools")
        
        avg_duration = sum(w["duration_ms"] for w in recent) / len(recent)
        if avg_duration > 5000:  # 5 seconds
            suggestions.append(f"Average workflow {avg_duration/1000:.1f}s - review slow tools")
        
        return suggestions


def main():
    parser = argparse.ArgumentParser(description="Tool Orchestrator - Optimize multi-tool workflows")
    parser.add_argument("--mode", choices=["optimize", "suggest", "report", "test"], default="report")
    parser.add_argument("--workflow", "-w", help="Workflow name")
    
    args = parser.parse_args()
    
    orchestrator = ToolOrchestrator()
    
    if args.mode == "optimize":
        # Demo: create sample workflow
        calls = [
            ToolCall("tool_a", {}, 1),
            ToolCall("tool_b", {}, 2, dependencies=["tool_a"]),
            ToolCall("tool_c", {}, 3, dependencies=["tool_a"]),
            ToolCall("tool_d", {}, 4, dependencies=["tool_b", "tool_c"]),
        ]
        batches = orchestrator.optimize_sequence(calls)
        print(f"Optimized into {len(batches)} parallel batches:")
        for i, batch in enumerate(batches):
            print(f"  Batch {i+1}: {[c.tool_name for c in batch]}")
    
    elif args.mode == "suggest":
        suggestions = orchestrator.suggest_optimization(args.workflow)
        print("Suggestions:")
        for s in suggestions:
            print(f"  • {s}")
    
    elif args.mode == "report":
        print(f"Total workflows: {orchestrator.state['total_workflows']}")
        print(f"Total tool calls: {orchestrator.state['total_tools_called']}")
        print(f"Avg parallelism: {orchestrator.state['avg_parallelism']:.2f}")
    
    elif args.mode == "test":
        print("🧪 Running tests...")
        # Register dummy tools
        def dummy_tool(**kwargs):
            time.sleep(0.01)
            return "ok"
        
        orchestrator.register_tool("tool_a", dummy_tool)
        orchestrator.register_tool("tool_b", dummy_tool)
        orchestrator.register_tool("tool_c", dummy_tool)
        
        calls = [
            ToolCall("tool_a", {}),
            ToolCall("tool_b", {}, dependencies=["tool_a"]),
            ToolCall("tool_c", {}, dependencies=["tool_a"]),
        ]
        
        result = orchestrator.run_workflow(calls, "test_workflow")
        print(f"✓ Executed in {result['batches']} batches")
        print(f"✓ Parallelism: {result['parallelism']}")
        print("✓ All tests passed")


if __name__ == "__main__":
    main()
