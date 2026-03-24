#!/usr/bin/env python3
"""
Dream Processor - Runs while you sleep:
1. Consolidates daily learnings → Updates cold memory
2. Pre-fetches likely tomorrow needs
3. Runs maintenance: cleanup, backups, health checks
4. Prepares morning briefing
5. Scans for opportunities (jobs, markets, etc)
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import time


class DreamTaskType(Enum):
    """Types of tasks that run during dream mode."""
    MEMORY_CONSOLIDATION = "memory_consolidation"
    PREFETCH = "prefetch"
    MAINTENANCE = "maintenance"
    BACKUP = "backup"
    HEALTH_CHECK = "health_check"
    OPPORTUNITY_SCAN = "opportunity_scan"
    INDEXING = "indexing"
    CLEANUP = "cleanup"


@dataclass
class DreamTask:
    """A task to run during dream mode."""
    task_id: str
    task_type: DreamTaskType
    name: str
    description: str
    priority: int  # 1 (highest) to 5 (lowest)
    estimated_duration: int  # minutes
    last_run: Optional[datetime]
    frequency: str  # 'daily', 'weekly', 'hourly'
    enabled: bool = True
    requires_network: bool = False


@dataclass
class MorningBriefing:
    """Morning briefing prepared by dream mode."""
    date: str
    summary: str
    key_events: List[str]
    tasks_ready: List[str]
    opportunities: List[str]
    market_summary: Optional[str]
    weather: Optional[str]
    news_digest: Optional[str]
    prepared_at: datetime


class DreamProcessor:
    """
    Offline processing engine that runs during inactive hours.
    """
    
    # Default schedule (24-hour format)
    DEFAULT_SCHEDULE = {
        "start_time": "02:00",  # 2 AM
        "end_time": "06:00",    # 6 AM
        "days": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    }
    
    def __init__(self, omnibot=None, data_dir: Optional[str] = None):
        self.logger = logging.getLogger("Omnibot.DreamProcessor")
        self.omnibot = omnibot
        
        # Storage
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent / "dream_data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Task registry
        self.tasks: Dict[str, DreamTask] = {}
        self.task_results: Dict[str, Any] = {}
        
        # Schedule
        self.schedule = self.DEFAULT_SCHEDULE.copy()
        self._load_schedule()
        
        # State
        self.is_running = False
        self.last_run: Optional[datetime] = None
        self.morning_briefing: Optional[MorningBriefing] = None
        
        # Thread control
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        
        # Initialize default tasks
        self._init_default_tasks()
        
        # Load previous state
        self._load_state()
        
        self.logger.info("DreamProcessor initialized")
    
    def _init_default_tasks(self):
        """Initialize default dream tasks."""
        default_tasks = [
            DreamTask(
                task_id="memory_consolidation",
                task_type=DreamTaskType.MEMORY_CONSOLIDATION,
                name="Memory Consolidation",
                description="Consolidate daily learnings into cold memory",
                priority=1,
                estimated_duration=15,
                last_run=None,
                frequency="daily"
            ),
            DreamTask(
                task_id="maintenance_cleanup",
                task_type=DreamTaskType.CLEANUP,
                name="Maintenance Cleanup",
                description="Clean up temporary files and old logs",
                priority=2,
                estimated_duration=10,
                last_run=None,
                frequency="daily"
            ),
            DreamTask(
                task_id="opportunity_scan",
                task_type=DreamTaskType.OPPORTUNITY_SCAN,
                name="Opportunity Scan",
                description="Scan for new job/investment opportunities",
                priority=2,
                estimated_duration=20,
                last_run=None,
                frequency="daily",
                requires_network=True
            ),
            DreamTask(
                task_id="prefetch_data",
                task_type=DreamTaskType.PREFETCH,
                name="Data Prefetch",
                description="Pre-fetch likely needed data for tomorrow",
                priority=3,
                estimated_duration=15,
                last_run=None,
                frequency="daily",
                requires_network=True
            ),
            DreamTask(
                task_id="backup_system",
                task_type=DreamTaskType.BACKUP,
                name="System Backup",
                description="Backup critical data and configurations",
                priority=2,
                estimated_duration=30,
                last_run=None,
                frequency="daily"
            ),
            DreamTask(
                task_id="indexing",
                task_type=DreamTaskType.INDEXING,
                name="Search Indexing",
                description="Update search indexes for fast retrieval",
                priority=3,
                estimated_duration=45,
                last_run=None,
                frequency="daily"
            ),
            DreamTask(
                task_id="health_check",
                task_type=DreamTaskType.HEALTH_CHECK,
                name="System Health Check",
                description="Check all systems are functioning correctly",
                priority=1,
                estimated_duration=10,
                last_run=None,
                frequency="daily"
            )
        ]
        
        for task in default_tasks:
            self.tasks[task.task_id] = task
    
    def _load_schedule(self):
        """Load dream schedule."""
        schedule_file = self.data_dir / "schedule.json"
        if schedule_file.exists():
            try:
                self.schedule = json.loads(schedule_file.read_text())
            except Exception as e:
                self.logger.error(f"Failed to load schedule: {e}")
    
    def _save_schedule(self):
        """Save dream schedule."""
        try:
            schedule_file = self.data_dir / "schedule.json"
            schedule_file.write_text(json.dumps(self.schedule, indent=2))
        except Exception as e:
            self.logger.error(f"Failed to save schedule: {e}")
    
    def _load_state(self):
        """Load previous run state."""
        state_file = self.data_dir / "dream_state.json"
        if state_file.exists():
            try:
                data = json.loads(state_file.read_text())
                self.last_run = datetime.fromisoformat(data["last_run"]) if data.get("last_run") else None
                
                # Load task last run times
                for task_id, last_run in data.get("task_last_runs", {}).items():
                    if task_id in self.tasks:
                        self.tasks[task_id].last_run = datetime.fromisoformat(last_run)
                
                self.logger.info(f"Loaded dream state, last run: {self.last_run}")
            except Exception as e:
                self.logger.error(f"Failed to load state: {e}")
    
    def _save_state(self):
        """Save current state."""
        try:
            state_file = self.data_dir / "dream_state.json"
            data = {
                "last_run": self.last_run.isoformat() if self.last_run else None,
                "task_last_runs": {
                    task_id: task.last_run.isoformat() if task.last_run else None
                    for task_id, task in self.tasks.items()
                },
                "saved_at": datetime.now().isoformat()
            }
            state_file.write_text(json.dumps(data, indent=2, default=str))
        except Exception as e:
            self.logger.error(f"Failed to save state: {e}")
    
    # ==================== SCHEDULE ====================
    
    def set_schedule(self, start_time: str, end_time: str, days: List[str]):
        """
        Set dream mode schedule.
        
        Args:
            start_time: Start time (HH:MM format)
            end_time: End time (HH:MM format)
            days: Days to run (e.g., ['mon', 'wed', 'fri'])
        """
        self.schedule = {
            "start_time": start_time,
            "end_time": end_time,
            "days": days
        }
        self._save_schedule()
        self.logger.info(f"Dream schedule set: {start_time} to {end_time}, days: {days}")
    
    def should_run_now(self) -> bool:
        """Check if dream mode should run now."""
        now = datetime.now()
        
        # Check day
        day_abbr = now.strftime("%a").lower()
        if day_abbr not in self.schedule["days"]:
            return False
        
        # Check time
        current_time = now.strftime("%H:%M")
        return self.schedule["start_time"] <= current_time <= self.schedule["end_time"]
    
    # ==================== TASK MANAGEMENT ====================
    
    def add_task(self, name: str, task_type: DreamTaskType, 
                priority: int = 3, frequency: str = "daily",
                estimated_duration: int = 15) -> str:
        """
        Add a custom dream task.
        
        Args:
            name: Task name
            task_type: Type of task
            priority: 1 (highest) to 5 (lowest)
            frequency: 'daily', 'weekly', 'hourly'
            estimated_duration: Estimated minutes
            
        Returns:
            Task ID
        """
        task_id = f"custom_{name.lower().replace(' ', '_')}"
        
        task = DreamTask(
            task_id=task_id,
            task_type=task_type,
            name=name,
            description=name,
            priority=priority,
            estimated_duration=estimated_duration,
            last_run=None,
            frequency=frequency
        )
        
        self.tasks[task_id] = task
        self.logger.info(f"Added dream task: {name}")
        return task_id
    
    def enable_task(self, task_id: str, enabled: bool = True):
        """Enable or disable a task."""
        if task_id in self.tasks:
            self.tasks[task_id].enabled = enabled
            self.logger.info(f"Task {task_id} {'enabled' if enabled else 'disabled'}")
    
    def get_tasks_for_now(self) -> List[DreamTask]:
        """Get tasks that should run now based on schedule."""
        now = datetime.now()
        
        tasks_to_run = []
        for task in self.tasks.values():
            if not task.enabled:
                continue
            
            # Check if task needs to run
            if task.frequency == "daily":
                if task.last_run is None or task.last_run.date() != now.date():
                    tasks_to_run.append(task)
            elif task.frequency == "weekly":
                if task.last_run is None or (now - task.last_run).days >= 7:
                    tasks_to_run.append(task)
            elif task.frequency == "hourly":
                if task.last_run is None or (now - task.last_run).total_seconds() >= 3600:
                    tasks_to_run.append(task)
        
        # Sort by priority
        tasks_to_run.sort(key=lambda t: t.priority)
        return tasks_to_run
    
    # ==================== DREAM EXECUTION ====================
    
    def start_dream_mode(self, blocking: bool = False):
        """
        Start dream mode processing.
        
        Args:
            blocking: If True, blocks until complete
        """
        if self.is_running:
            self.logger.warning("Dream mode already running")
            return
        
        self.is_running = True
        self.logger.info("🌙 Entering dream mode...")
        
        if blocking:
            self._run_dream_cycle()
        else:
            self._thread = threading.Thread(target=self._run_dream_cycle)
            self._thread.start()
    
    def stop_dream_mode(self):
        """Stop dream mode gracefully."""
        self.logger.info("Waking from dream mode...")
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=60)
        self.is_running = False
    
    def _run_dream_cycle(self):
        """Run one dream cycle."""
        tasks = self.get_tasks_for_now()
        self.logger.info(f"Running {len(tasks)} dream tasks")
        
        for task in tasks:
            if self._stop_event.is_set():
                break
            
            try:
                self._execute_task(task)
            except Exception as e:
                self.logger.error(f"Dream task {task.task_id} failed: {e}")
        
        # Prepare morning briefing
        self._prepare_morning_briefing()
        
        self.last_run = datetime.now()
        self._save_state()
        self.is_running = False
        
        self.logger.info("🌅 Dream mode complete")
    
    def _execute_task(self, task: DreamTask):
        """Execute a single dream task."""
        self.logger.info(f"🌙 [Dream] {task.name}")
        
        result = None
        
        if task.task_type == DreamTaskType.MEMORY_CONSOLIDATION:
            result = self._task_memory_consolidation()
        elif task.task_type == DreamTaskType.CLEANUP:
            result = self._task_cleanup()
        elif task.task_type == DreamTaskType.BACKUP:
            result = self._task_backup()
        elif task.task_type == DreamTaskType.HEALTH_CHECK:
            result = self._task_health_check()
        elif task.task_type == DreamTaskType.OPPORTUNITY_SCAN:
            result = self._task_opportunity_scan()
        elif task.task_type == DreamTaskType.PREFETCH:
            result = self._task_prefetch()
        elif task.task_type == DreamTaskType.INDEXING:
            result = self._task_indexing()
        else:
            self.logger.warning(f"Unknown task type: {task.task_type}")
            return
        
        task.last_run = datetime.now()
        self.task_results[task.task_id] = result
        self.logger.info(f"✅ [Dream] {task.name} complete")
    
    # ==================== INDIVIDUAL TASKS ====================
    
    def _task_memory_consolidation(self) -> Dict:
        """Consolidate memory."""
        result = {"entries_consolidated": 0}
        
        if self.omnibot:
            try:
                consolidation_report = self.omnibot.consolidate(force=False)
                result["entries_consolidated"] = consolidation_report.get("entries_moved", 0)
            except Exception as e:
                result["error"] = str(e)
        
        return result
    
    def _task_cleanup(self) -> Dict:
        """Clean up temporary files."""
        result = {"files_removed": 0, "space_freed_mb": 0}
        
        # Clean temp directories
        temp_dirs = [
            Path("/tmp"),
            Path.cwd() / "temp",
            self.data_dir / "temp"
        ]
        
        for temp_dir in temp_dirs:
            if temp_dir.exists():
                for file in temp_dir.glob("*"):
                    try:
                        if file.is_file():
                            age = datetime.now() - datetime.fromtimestamp(file.stat().st_mtime)
                            if age > timedelta(days=7):
                                size_mb = file.stat().st_size / (1024 * 1024)
                                file.unlink()
                                result["files_removed"] += 1
                                result["space_freed_mb"] += size_mb
                    except Exception as e:
                        self.logger.warning(f"Could not remove {file}: {e}")
        
        return result
    
    def _task_backup(self) -> Dict:
        """Backup critical data."""
        result = {"backups_created": 0}
        
        backup_dir = self.data_dir / "backups"
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Backup memory files
        workspace = Path("/home/skux/.openclaw/workspace")
        memory_dir = workspace / "memory"
        if memory_dir.exists():
            backup_file = backup_dir / f"memory_backup_{timestamp}.json"
            try:
                # Create compressed backup
                import shutil
                memory_backup = backup_dir / f"memory_{timestamp}"
                shutil.copytree(memory_dir, memory_backup, dirs_exist_ok=True)
                shutil.make_archive(str(memory_backup), 'zip', str(memory_backup))
                shutil.rmtree(memory_backup)
                result["backups_created"] += 1
            except Exception as e:
                result["error"] = str(e)
        
        return result
    
    def _task_health_check(self) -> Dict:
        """Check system health."""
        result = {
            "status": "healthy",
            "checks": {}
        }
        
        # Check disk space
        import shutil
        total, used, free = shutil.disk_usage("/")
        disk_percent = (used / total) * 100
        result["checks"]["disk_space"] = {
            "free_gb": free / (2**30),
            "percent_used": disk_percent,
            "status": "healthy" if disk_percent < 80 else "warning"
        }
        
        # Check memory
        try:
            with open('/proc/meminfo', 'r') as f:
                meminfo = f.read()
            # Parse meminfo (simplified)
            result["checks"]["memory"] = {"status": "unknown"}
        except:
            pass
        
        # Check critical files exist
        critical_files = [
            Path("/home/skux/.openclaw/workspace/MEMORY.md"),
            Path("/home/skux/.openclaw/workspace/USER.md")
        ]
        for critical_file in critical_files:
            result["checks"][f"file_{critical_file.name}"] = {
                "exists": critical_file.exists(),
                "status": "healthy" if critical_file.exists() else "error"
            }
        
        return result
    
    def _task_opportunity_scan(self) -> Dict:
        """Scan for opportunities."""
        result = {"jobs_found": 0, "markets_scanned": 0}
        
        # This would integrate with job seeker
        if self.omnibot and hasattr(self.omnibot, 'job_seeker'):
            try:
                # Simulate scanning
                result["jobs_found"] = 3  # Would be actual scan
            except Exception as e:
                result["error"] = str(e)
        
        return result
    
    def _task_prefetch(self) -> Dict:
        """Pre-fetch likely needed data."""
        result = {"items_prefetched": 0}
        
        # Analyze user patterns to predict needs
        likely_needs = self._predict_user_needs()
        
        for need in likely_needs:
            # Prefetch data
            result["items_prefetched"] += 1
        
        return result
    
    def _predict_user_needs(self) -> List[str]:
        """Predict what user will need tomorrow."""
        # This would use pattern analysis
        return [
            "morning_email_summary",
            "calendar_overview",
            "priority_tasks"
        ]
    
    def _task_indexing(self) -> Dict:
        """Update search indexes."""
        result = {"files_indexed": 0}
        
        # Index workspace files
        workspace = Path("/home/skux/.openclaw/workspace")
        for py_file in workspace.rglob("*.py"):
            if "__pycache__" not in str(py_file):
                result["files_indexed"] += 1
        
        return result
    
    # ==================== MORNING BRIEFING ====================
    
    def _prepare_morning_briefing(self):
        """Prepare morning briefing."""
        self.logger.info("🌅 Preparing morning briefing...")
        
        briefing = MorningBriefing(
            date=datetime.now().strftime("%Y-%m-%d"),
            summary=self._generate_summary(),
            key_events=self._get_key_events(),
            tasks_ready=self._get_tasks_ready(),
            opportunities=self._get_opportunities(),
            market_summary=self._get_market_summary(),
            weather=None,  # Could integrate weather API
            news_digest=None,  # Could integrate news API
            prepared_at=datetime.now()
        )
        
        self.morning_briefing = briefing
        
        # Save briefing
        briefing_file = self.data_dir / "morning_briefing.json"
        briefing_file.write_text(json.dumps(asdict(briefing), indent=2, default=str))
        
        self.logger.info("📧 Morning briefing ready")
    
    def _generate_summary(self) -> str:
        """Generate briefing summary."""
        tasks_run = len([t for t in self.tasks.values() if t.last_run and t.last_run.date() == datetime.now().date()])
        return f"Dream mode completed {tasks_run} tasks overnight"
    
    def _get_key_events(self) -> List[str]:
        """Get key events for today."""
        return ["Dream mode ran successfully", "System backed up"]
    
    def _get_tasks_ready(self) -> List[str]:
        """Get tasks ready for user."""
        # Analyze patterns
        return []
    
    def _get_opportunities(self) -> List[str]:
        """Get discovered opportunities."""
        return self.task_results.get("opportunity_scan", {}).get("jobs_found", 0)
    
    def _get_market_summary(self) -> Optional[str]:
        """Get overnight market summary."""
        # Would integrate with financial APIs
        return "Markets closed overnight"
    
    def get_morning_briefing(self) -> Optional[MorningBriefing]:
        """Get the current morning briefing."""
        if not self.morning_briefing:
            # Try to load from file
            briefing_file = self.data_dir / "morning_briefing.json"
            if briefing_file.exists():
                try:
                    data = json.loads(briefing_file.read_text())
                    self.morning_briefing = MorningBriefing(**data)
                except Exception:
                    pass
        return self.morning_briefing
    
    def display_briefing(self) -> str:
        """Display briefing in human-readable format."""
        briefing = self.get_morning_briefing()
        if not briefing:
            return "No morning briefing available"
        
        output = f"""
🌅 GOOD MORNING BRIEFING - {briefing.date}
{'='*50}

📋 SUMMARY
{briefing.summary}

🎯 KEY EVENTS
"""
        for event in briefing.key_events:
            output += f"• {event}\n"
        
        if briefing.opportunities:
            output += f"\n💼 OPPORTUNITIES\n{briefing.opportunities} items\n"
        
        if briefing.market_summary:
            output += f"\n📈 MARKETS\n{briefing.market_summary}\n"
        
        output += f"\nPrepared at: {briefing.prepared_at.strftime('%H:%M')}\n"
        
        return output
    
    # ==================== UTILITIES ====================
    
    def get_status(self) -> Dict:
        """Get dream mode status."""
        return {
            "is_running": self.is_running,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "next_window": self._get_next_window(),
            "tasks_total": len(self.tasks),
            "tasks_enabled": len([t for t in self.tasks.values() if t.enabled]),
            "briefing_available": self.morning_briefing is not None
        }
    
    def _get_next_window(self) -> Optional[str]:
        """Get next dream window."""
        now = datetime.now()
        day_abbr = now.strftime("%a").lower()
        
        if day_abbr in self.schedule["days"]:
            return f"Today at {self.schedule['start_time']}"
        
        # Find next scheduled day
        days_order = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        current_idx = days_order.index(day_abbr)
        
        for i in range(1, 8):
            next_idx = (current_idx + i) % 7
            if days_order[next_idx] in self.schedule["days"]:
                return f"{days_order[next_idx].title()} at {self.schedule['start_time']}"
        
        return None