#!/usr/bin/env python3
"""
Autonomous Scheduler v1.0
Intelligent task scheduling with dependency management

## ACA Plan:
1. Requirements: Parse MEMORY.md for recurring tasks → auto-create cron jobs
2. Architecture: TaskParser → DependencyResolver → Scheduler → CronGenerator
3. Data Flow: Extract tasks → Resolve deps → Schedule → Generate crontab
4. Edge Cases: Circular deps, missing tasks, invalid schedules, conflicts
5. Tool Constraints: File read, regex, cron syntax, subprocess
6. Error Handling: Parse errors, schedule conflicts, invalid cron
7. Testing: Test parsing, verify cron syntax

Author: Autonomous Code Architect (ACA)
"""

import argparse
import json
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set

WORKSPACE_DIR = Path("/home/skux/.openclaw/workspace")
MEMORY_DIR = WORKSPACE_DIR / "memory"


class TaskFrequency(Enum):
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


@dataclass
class ScheduledTask:
    name: str
    command: str
    frequency: TaskFrequency
    schedule: str  # cron expression or descriptor
    depends_on: List[str] = field(default_factory=list)
    enabled: bool = True
    last_run: Optional[str] = None
    next_run: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3


class TaskParser:
    """Parse tasks from MEMORY.md and other sources"""
    
    def __init__(self):
        self.tasks: List[ScheduledTask] = []
    
    def parse_memory_for_tasks(self) -> List[ScheduledTask]:
        """Extract scheduled tasks from memory files"""
        tasks = []
        
        # Parse cron jobs from memory
        for mem_file in MEMORY_DIR.glob("2026-*.md"):
            content = mem_file.read_text()
            
            # Look for Cron Jobs table specifically
            # Find sections that look like cron job tables
            # Pattern: | Job | Schedule | Status |
            cron_table_pattern = r'##\s*Cron[^#]*?\|[^\n]*Job[^\n]*\|[^\n]*Schedule[^\n]*\|[^\n]*\n((?:\|[^\n]+\n)+)'
            
            for table_match in re.finditer(cron_table_pattern, content, re.DOTALL | re.IGNORECASE):
                table_content = table_match.group(1)
                
                # Parse each row in the table
                # Skip header separator line
                row_pattern = r'\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|'
                for row_match in re.finditer(row_pattern, table_content):
                    name = row_match.group(1).strip()
                    schedule = row_match.group(2).strip()
                    
                    # FILTER: Skip garbage rows
                    if self._is_valid_cron_job(name, schedule):
                        cron_expr = self._schedule_to_cron(name, schedule)
                        
                        if cron_expr:
                            tasks.append(ScheduledTask(
                                name=name,
                                command=self._get_command_for_task(name),
                                frequency=TaskFrequency.CUSTOM,
                                schedule=cron_expr
                            ))
        
        return tasks
    
    def _is_valid_cron_job(self, name: str, schedule: str) -> bool:
        """Validate that this looks like a real cron job, not table garbage"""
        # Must have reasonable length
        if len(name) < 3 or len(name) > 50:
            return False
        
        # Must not contain emojis
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+", 
            flags=re.UNICODE
        )
        if emoji_pattern.search(name):
            return False
        
        # Must not contain $ (mcap values)
        if '$' in name:
            return False
        
        # Must not be just numbers
        if re.match(r'^[\d\s]+$', name):
            return False
        
        # Must not be crypto/token symbols (all caps, short)
        if re.match(r'^[A-Z]{2,6}$', name):
            return False
        
        # Schedule must look like a schedule (contain time words)
        schedule_indicators = ['min', 'hour', 'daily', 'weekly', 'monthly', 
                              'cron', 'am', 'pm', 'every', 'day', 'night',
                              '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
        schedule_lower = schedule.lower()
        if not any(indicator in schedule_lower for indicator in schedule_indicators):
            return False
        
        # Common noise patterns to skip
        noise_patterns = [
            r'^-$', r'^-$', r'^\s*$',  # dashes, empty
            r'^(status|job|schedule)$',  # headers
            r'^[\-\|]+$'  # separator lines
        ]
        for pattern in noise_patterns:
            if re.match(pattern, name, re.IGNORECASE):
                return False
        
        return True
        
        # Add inferred tasks from skills
        tasks.append(ScheduledTask(
            name="skill-health-check",
            command=f"cd {WORKSPACE_DIR}/skills && python3 generate_skill_map.py",
            frequency=TaskFrequency.DAILY,
            schedule="0 9 * * *"  # 9 AM daily
        ))
        
        tasks.append(ScheduledTask(
            name="goal-generation",
            command=f"cd {WORKSPACE_DIR}/skills/autonomous-goal-generator && python3 autonomous_goal_generator.py --mode generate",
            frequency=TaskFrequency.DAILY,
            schedule="0 8 * * *"  # 8 AM daily
        ))
        
        tasks.append(ScheduledTask(
            name="kpi-tracking",
            command=f"cd {WORKSPACE_DIR}/skills/kpi-performance-tracker && python3 kpi_performance_tracker.py",
            frequency=TaskFrequency.DAILY,
            schedule="0 7 * * *"  # 7 AM daily
        ))
        
        return tasks
    
    def _schedule_to_cron(self, name: str, schedule: str) -> Optional[str]:
        """Convert human-readable schedule to cron"""
        schedule_lower = schedule.lower()
        
        if "30 mins" in schedule_lower or "30 minutes" in schedule_lower:
            return "*/30 * * * *"
        elif "every hour" in schedule_lower or "hourly" in schedule_lower:
            return "0 * * * *"
        elif "2 hours" in schedule_lower:
            return "0 */2 * * *"
        elif "6 hours" in schedule_lower:
            return "0 */6 * * *"
        elif "daily" in schedule_lower or "every day" in schedule_lower:
            return "0 0 * * *"
        elif "11 pm" in schedule_lower or "23:00" in schedule_lower:
            return "0 23 * * *"
        elif "9 pm" in schedule_lower or "21:00" in schedule_lower:
            return "0 21 * * *"
        else:
            # Default: daily at midnight
            return "0 0 * * *"
    
    def _get_command_for_task(self, name: str) -> str:
        """Map task names to commands"""
        commands = {
            "moltbook-heartbeat": f"cd {WORKSPACE_DIR} && python3 check_moltbook.py",
            "nightly-build": f"cd {WORKSPACE_DIR} && ./nightly_build.sh",
            "solana-alpha-monitor-v54": f"cd {WORKSPACE_DIR} && python3 agents/lux_trader/solana_alpha_hunter_v54.py",
            "lux-trader-paper": f"cd {WORKSPACE_DIR}/agents/lux_trader && python3 luxtrader_live.py",
            "lux-trader-learn": f"cd {WORKSPACE_DIR}/agents/lux_trader && python3 learning_engine.py",
        }
        return commands.get(name, f"echo 'Task {name} not configured'")


class AutonomousScheduler:
    def __init__(self):
        self.parser = TaskParser()
        self.tasks: List[ScheduledTask] = []
    
    def discover_tasks(self) -> List[ScheduledTask]:
        """Discover all schedulable tasks"""
        self.tasks = self.parser.parse_memory_for_tasks()
        return self.tasks
    
    def resolve_dependencies(self) -> List[ScheduledTask]:
        """Resolve task dependencies (simplified)"""
        # For now, just ensure order makes sense
        # In future: build DAG, topological sort
        return self.tasks
    
    def generate_crontab(self) -> str:
        """Generate crontab entries"""
        lines = []
        lines.append("# Autonomous Scheduler - Generated crontab")
        lines.append(f"# Generated: {datetime.now().isoformat()}")
        lines.append("")
        
        for task in self.tasks:
            if not task.enabled:
                lines.append(f"# DISABLED: {task.name}")
                continue
            
            lines.append(f"# {task.name}")
            lines.append(f"{task.schedule} {task.command}")
            lines.append("")
        
        return "\n".join(lines)
    
    def save_crontab(self, crontab: str):
        """Save to file"""
        output_file = MEMORY_DIR / "autonomous_scheduler" / "crontab.txt"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, "w") as f:
            f.write(crontab)
        
        return output_file
    
    def run(self, mode: str = "generate") -> Dict:
        """Main execution"""
        tasks = self.discover_tasks()
        tasks = self.resolve_dependencies()
        
        crontab = self.generate_crontab()
        output_file = self.save_crontab(crontab)
        
        # Save task list
        tasks_file = MEMORY_DIR / "autonomous_scheduler" / "tasks.json"
        with open(tasks_file, "w") as f:
            json.dump([{
                "name": t.name,
                "schedule": t.schedule,
                "enabled": t.enabled
            } for t in tasks], f, indent=2)
        
        if mode == "preview":
            print(crontab)
            return {"success": True, "tasks": len(tasks)}
        
        return {
            "success": True,
            "tasks_scheduled": len(tasks),
            "crontab_saved": str(output_file),
            "tasks_file": str(tasks_file)
        }


def main():
    parser = argparse.ArgumentParser(description="Autonomous Scheduler")
    parser.add_argument("--mode", choices=["generate", "preview"], default="generate")
    args = parser.parse_args()
    
    scheduler = AutonomousScheduler()
    result = scheduler.run(args.mode)
    
    if result.get("success"):
        print(f"✓ Scheduler complete")
        print(f"  Tasks: {result.get('tasks_scheduled', 0)}")
    else:
        print(f"✗ Error: {result.get('error', 'Unknown')}")


if __name__ == "__main__":
    main()
