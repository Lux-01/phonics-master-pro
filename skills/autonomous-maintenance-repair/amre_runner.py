#!/usr/bin/env python3
"""
Autonomous Maintenance & Repair (AMRE)
Self-healing system that detects broken components and automatically repairs them.
"""

import json
import os
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import subprocess

# Paths
AMRE_DIR = Path("/home/skux/.openclaw/workspace/skills/autonomous-maintenance-repair")
DATA_DIR = AMRE_DIR / "data"
LOGS_DIR = DATA_DIR / "logs"
BACKUPS_DIR = DATA_DIR / "backups"
HEALTH_FILE = DATA_DIR / "health_status.json"

for d in [AMRE_DIR, DATA_DIR, LOGS_DIR, BACKUPS_DIR]:
    d.mkdir(parents=True, exist_ok=True)


class AutonomousMaintenanceRepair:
    """
    Self-healing system for OpenClaw workspace.
    Detects and repairs issues automatically.
    """
    
    def __init__(self):
        self.data_dir = DATA_DIR
        self.logs_dir = LOGS_DIR
        self.backups_dir = BACKUPS_DIR
        self.health_file = HEALTH_FILE
        self.components = self._register_components()
        
    def _register_components(self) -> Dict[str, Dict]:
        """Register all components to monitor."""
        return {
            "scanners": {
                "path": "/home/skux/.openclaw/workspace/skills/pattern-extractor/rug_pattern_extractor.py",
                "type": "skill",
                "critical": True,
                "check": "file_exists"
            },
            "outcome_tracker": {
                "path": "/home/skux/.openclaw/workspace/skills/outcome-tracker/trading_outcome_tracker.py",
                "type": "skill",
                "critical": True,
                "check": "file_exists"
            },
            "aloe": {
                "path": "/home/skux/.openclaw/workspace/skills/aloe/aloe_coordinator.py",
                "type": "skill",
                "critical": True,
                "check": "file_exists"
            },
            "ats": {
                "path": "/home/skux/.openclaw/workspace/skills/autonomous-trading-strategist/ats_runner.py",
                "type": "skill",
                "critical": False,
                "check": "file_exists"
            },
            "aoe": {
                "path": "/home/skux/.openclaw/workspace/skills/autonomous-opportunity-engine/aoe_runner.py",
                "type": "skill",
                "critical": False,
                "check": "file_exists"
            },
            "mac": {
                "path": "/home/skux/.openclaw/workspace/skills/multi-agent-coordinator/mac_runner.py",
                "type": "skill",
                "critical": False,
                "check": "file_exists"
            },
            "memory_outcomes": {
                "path": "/home/skux/.openclaw/workspace/memory/outcomes",
                "type": "directory",
                "critical": True,
                "check": "dir_exists"
            },
            "memory_aloe": {
                "path": "/home/skux/.openclaw/workspace/memory/aloe",
                "type": "directory",
                "critical": True,
                "check": "dir_exists"
            },
            "memory_patterns": {
                "path": "/home/skux/.openclaw/workspace/memory/patterns",
                "type": "directory",
                "critical": True,
                "check": "dir_exists"
            }
        }
    
    def check_health(self) -> Dict[str, Any]:
        """Perform health check on all components."""
        
        health_report = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "components_checked": {},
            "issues_found": [],
            "repairs_made": []
        }
        
        for name, config in self.components.items():
            status = self._check_component(name, config)
            health_report["components_checked"][name] = status
            
            if status["status"] == "missing":
                health_report["issues_found"].append({
                    "component": name,
                    "issue": "File/directory missing",
                    "critical": config.get("critical", False)
                })
                
                # Attempt repair
                repair = self._repair_component(name, config)
                health_report["repairs_made"].append(repair)
                
            elif status["status"] == "corrupted":
                health_report["issues_found"].append({
                    "component": name,
                    "issue": "Corrupted data",
                    "critical": config.get("critical", False)
                })
                
                # Attempt repair
                repair = self._repair_component(name, config)
                health_report["repairs_made"].append(repair)
        
        # Determine overall status
        critical_issues = [i for i in health_report["issues_found"] if i.get("critical")]
        if critical_issues:
            health_report["overall_status"] = "critical"
        elif health_report["issues_found"]:
            health_report["overall_status"] = "degraded"
        
        # Save health report
        self._save_health_report(health_report)
        
        return health_report
    
    def _check_component(self, name: str, config: Dict) -> Dict:
        """Check a single component."""
        
        path = Path(config["path"])
        check_type = config.get("check", "file_exists")
        
        if check_type == "file_exists":
            if not path.exists():
                return {"status": "missing", "path": str(path)}
            
            # Check if file is readable
            try:
                with open(path) as f:
                    content = f.read()
                return {"status": "healthy", "size": len(content)}
            except Exception as e:
                return {"status": "corrupted", "error": str(e)}
        
        elif check_type == "dir_exists":
            if not path.exists():
                return {"status": "missing", "path": str(path)}
            
            # Check if directory is accessible
            try:
                files = list(path.iterdir())
                return {"status": "healthy", "file_count": len(files)}
            except Exception as e:
                return {"status": "corrupted", "error": str(e)}
        
        return {"status": "unknown"}
    
    def _repair_component(self, name: str, config: Dict) -> Dict:
        """Attempt to repair a component."""
        
        repair = {
            "component": name,
            "attempted": False,
            "successful": False,
            "action_taken": None
        }
        
        if config["type"] == "directory":
            # Create directory
            try:
                Path(config["path"]).mkdir(parents=True, exist_ok=True)
                repair["attempted"] = True
                repair["successful"] = True
                repair["action_taken"] = "created_directory"
            except Exception as e:
                repair["attempted"] = True
                repair["error"] = str(e)
        
        elif config["type"] == "skill":
            # Restore from template/backup
            backup = self._find_backup(name)
            if backup:
                try:
                    import shutil
                    shutil.copy(backup, config["path"])
                    repair["attempted"] = True
                    repair["successful"] = True
                    repair["action_taken"] = "restored_from_backup"
                except Exception as e:
                    repair["attempted"] = True
                    repair["error"] = str(e)
            else:
                repair["attempted"] = True
                repair["error"] = "No backup found"
        
        return repair
    
    def _find_backup(self, name: str) -> Optional[str]:
        """Find backup for a component."""
        # Look for backups in backups directory
        backup_files = list(self.backups_dir.glob(f"*{name}*"))
        if backup_files:
            return str(backup_files[-1])  # Return most recent
        return None
    
    def repair_all(self) -> Dict:
        """Repair all issues found."""
        
        health = self.check_health()
        repairs = []
        
        for issue in health.get("issues_found", []):
            component = issue["component"]
            config = self.components.get(component)
            if config:
                repair = self._repair_component(component, config)
                repairs.append(repair)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "repairs_attempted": len(repairs),
            "repairs_successful": len([r for r in repairs if r.get("successful")]),
            "repairs": repairs
        }
    
    def create_backup(self, component_name: Optional[str] = None) -> Dict:
        """Create backup of component(s)."""
        
        backup_report = {
            "timestamp": datetime.now().isoformat(),
            "backups_created": []
        }
        
        components_to_backup = [component_name] if component_name else list(self.components.keys())
        
        for name in components_to_backup:
            config = self.components.get(name)
            if not config:
                continue
            
            source = Path(config["path"])
            if source.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"{name}_{timestamp}.backup"
                backup_path = self.backups_dir / backup_name
                
                try:
                    if config["type"] == "file":
                        import shutil
                        shutil.copy(source, backup_path)
                    elif config["type"] == "directory":
                        import shutil
                        shutil.copytree(source, backup_path, dirs_exist_ok=True)
                    
                    backup_report["backups_created"].append({
                        "component": name,
                        "backup_path": str(backup_path)
                    })
                except Exception as e:
                    backup_report["backups_created"].append({
                        "component": name,
                        "error": str(e)
                    })
        
        return backup_report
    
    def monitor(self, duration_minutes: int = 60) -> Dict:
        """Monitor system for specified duration."""
        
        import time
        
        monitor_report = {
            "start_time": datetime.now().isoformat(),
            "duration_minutes": duration_minutes,
            "checks": []
        }
        
        end_time = datetime.now().timestamp() + (duration_minutes * 60)
        
        while datetime.now().timestamp() < end_time:
            health = self.check_health()
            monitor_report["checks"].append({
                "time": datetime.now().isoformat(),
                "status": health["overall_status"],
                "issues": len(health["issues_found"])
            })
            
            # Sleep for 5 minutes between checks
            time.sleep(300)
        
        monitor_report["end_time"] = datetime.now().isoformat()
        return monitor_report
    
    def _save_health_report(self, report: Dict):
        """Save health report to disk."""
        report_file = self.logs_dir / f"health_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Also update latest health file
        with open(self.health_file, 'w') as f:
            json.dump(report, f, indent=2)
    
    def get_health_history(self, limit: int = 10) -> List[Dict]:
        """Get recent health reports."""
        reports = sorted(self.logs_dir.glob("health_*.json"), reverse=True)
        return [json.load(open(r)) for r in reports[:limit]]
    
    def get_status(self) -> Dict:
        """Get current system status."""
        
        if self.health_file.exists():
            with open(self.health_file) as f:
                return json.load(f)
        
        return {"status": "unknown", "message": "No health data available"}


# Global instance
amre = AutonomousMaintenanceRepair()


def check_health() -> Dict:
    """Quick health check function."""
    return amre.check_health()


def repair_all() -> Dict:
    """Quick repair all function."""
    return amre.repair_all()


def create_backup(component: str = None) -> Dict:
    """Quick backup function."""
    return amre.create_backup(component)


def get_status() -> Dict:
    """Quick get status function."""
    return amre.get_status()


if __name__ == "__main__":
    print("🔧 Autonomous Maintenance & Repair (AMRE)")
    print("=" * 60)
    
    # Run health check
    print("\n🏥 Running health check...")
    health = check_health()
    
    print(f"\n📊 Health Report:")
    print(f"   Overall Status: {health['overall_status'].upper()}")
    print(f"   Components Checked: {len(health['components_checked'])}")
    print(f"   Issues Found: {len(health['issues_found'])}")
    
    if health['issues_found']:
        print(f"\n⚠️  Issues:")
        for issue in health['issues_found']:
            critical = "🔴" if issue.get('critical') else "🟡"
            print(f"   {critical} {issue['component']}: {issue['issue']}")
    
    if health['repairs_made']:
        print(f"\n🔧 Repairs Made:")
        for repair in health['repairs_made']:
            status = "✅" if repair.get('successful') else "❌"
            print(f"   {status} {repair['component']}: {repair.get('action_taken', 'failed')}")
    
    # Component status
    print(f"\n📋 Component Status:")
    for name, status in health['components_checked'].items():
        icon = "✅" if status['status'] == 'healthy' else "⚠️"
        print(f"   {icon} {name}: {status['status']}")
    
    print(f"\n🔧 AMRE ready for self-healing!")
    print(f"   Logs: {LOGS_DIR}")
    print(f"   Backups: {BACKUPS_DIR}")
