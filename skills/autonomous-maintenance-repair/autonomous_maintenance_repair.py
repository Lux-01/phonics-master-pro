#!/usr/bin/env python3
"""
Autonomous Maintenance & Repair v1.0
Self-healing system that detects and repairs broken components

## ACA Plan:
1. Requirements: Monitor file integrity, service health, API availability → auto-fix issues
2. Architecture: HealthMonitor → IssueDetector → RepairEngine → Reporter
3. Data Flow: Check health → Detect issues → Attempt repair → Log results
4. Edge Cases: No permissions, repair fails, circular repairs, false positives
5. Tool Constraints: File read/write, subprocess, HTTP requests, file stat
6. Error Handling: Permission denied, file locked, repair failures
7. Testing: Test with mock broken files

Author: Autonomous Code Architect (ACA)
"""

import argparse
import json
import os
import shutil
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import requests

WORKSPACE_DIR = Path("/home/skux/.openclaw/workspace")
MEMORY_DIR = WORKSPACE_DIR / "memory"
STATE_FILE = MEMORY_DIR / "maintenance" / "state.json"


@dataclass
class HealthCheck:
    component: str
    status: str  # healthy, warning, error
    message: str
    auto_fixable: bool = False
    fix_attempted: bool = False
    fix_success: bool = False


class HealthMonitor:
    """Monitor system health"""
    
    def __init__(self):
        self.checks: List[HealthCheck] = []
    
    def check_skill_integrity(self) -> List[HealthCheck]:
        """Check skill files are valid"""
        checks = []
        skills_dir = WORKSPACE_DIR / "skills"
        
        for skill_dir in skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue
            
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                checks.append(HealthCheck(
                    component=f"skill:{skill_dir.name}",
                    status="error",
                    message=f"Missing SKILL.md in {skill_dir.name}",
                    auto_fixable=False
                ))
            elif skill_md.stat().st_size == 0:
                checks.append(HealthCheck(
                    component=f"skill:{skill_dir.name}",
                    status="warning",
                    message=f"Empty SKILL.md in {skill_dir.name}",
                    auto_fixable=False
                ))
        
        return checks
    
    def check_api_health(self) -> List[HealthCheck]:
        """Check API endpoints"""
        checks = []
        
        # Check Helius (optional - may fail without key)
        try:
            result = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", 
                 "https://api.helius.xyz/health"],
                capture_output=True, text=True, timeout=5
            )
            status = "healthy" if result.stdout.strip() == "200" else "warning"
        except:
            status = "warning"
        
        checks.append(HealthCheck(
            component="api:helius",
            status=status,
            message="Helius API connectivity",
            auto_fixable=False
        ))
        
        return checks
    
    def check_disk_space(self) -> List[HealthCheck]:
        """Check available disk space"""
        try:
            stat = os.statvfs(str(WORKSPACE_DIR))
            free_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
            
            if free_gb < 1:
                status = "error"
                message = f"Critical: only {free_gb:.1f}GB free"
                auto_fix = False
            elif free_gb < 5:
                status = "warning"
                message = f"Low space: {free_gb:.1f}GB free"
                auto_fix = True
            else:
                status = "healthy"
                message = f"OK: {free_gb:.1f}GB free"
                auto_fix = False
            
            return [HealthCheck(
                component="system:disk",
                status=status,
                message=message,
                auto_fixable=auto_fix
            )]
        
        except Exception as e:
            return [HealthCheck(
                component="system:disk",
                status="warning",
                message=f"Could not check disk: {e}",
                auto_fixable=False
            )]
    
    def check_memory_integrity(self) -> List[HealthCheck]:
        """Check memory files are not corrupted"""
        checks = []
        
        # Check main memory file
        memory_md = MEMORY_DIR / "MEMORY.md"
        if memory_md.exists():
            content = memory_md.read_text()
            
            # Check for common corruption signs
            if content.count("---") > 100:  # Excessive dividers
                checks.append(HealthCheck(
                    component="memory:main",
                    status="warning",
                    message="Possible corruption: excessive dividers",
                    auto_fixable=False
                ))
            
            # Check for broken markdown
            if content.count("[[") != content.count("]]"):
                checks.append(HealthCheck(
                    component="memory:main",
                    status="error",
                    message="Broken markdown: unmatched brackets",
                    auto_fixable=False
                ))
        
        return checks


class RepairEngine:
    """Attempt automatic repair"""
    
    def repair(self, check: HealthCheck) -> bool:
        """Attempt to repair an issue"""
        if not check.auto_fixable:
            return False
        
        check.fix_attempted = True
        
        if check.message.startswith("Low space"):
            # Clean temporary files
            return self._cleanup_temp_files()
        
        return False
    
    def _cleanup_temp_files(self) -> bool:
        """Clean temporary and cache files"""
        try:
            cleaned = 0
            
            # Remove __pycache__
            for root, dirs, files in os.walk(WORKSPACE_DIR):
                for d in dirs:
                    if d == "__pycache__":
                        shutil.rmtree(Path(root) / d)
                        cleaned += 1
            
            return cleaned > 0
        except:
            return False


class AutonomousMaintenanceRepair:
    def __init__(self):
        self.monitor = HealthMonitor()
        self.repairer = RepairEngine()
        self.results: Dict = {}
    
    def run_health_check(self) -> List[HealthCheck]:
        """Run all health checks"""
        checks = []
        checks.extend(self.monitor.check_skill_integrity())
        checks.extend(self.monitor.check_api_health())
        checks.extend(self.monitor.check_disk_space())
        checks.extend(self.monitor.check_memory_integrity())
        return checks
    
    def attempt_repairs(self, checks: List[HealthCheck]) -> Tuple[int, int]:
        """Attempt to repair issues"""
        attempted = 0
        fixed = 0
        
        for check in checks:
            if check.auto_fixable:
                attempted += 1
                if self.repairer.repair(check):
                    check.fix_success = True
                    check.status = "healthy"
                    fixed += 1
        
        return attempted, fixed
    
    def generate_report(self, checks: List[HealthCheck]) -> str:
        """Generate maintenance report"""
        report = []
        report.append("# Maintenance \u0026 Repair Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append("")
        
        healthy = len([c for c in checks if c.status == "healthy"])
        warning = len([c for c in checks if c.status == "warning"])
        error = len([c for c in checks if c.status == "error"])
        fixed = len([c for c in checks if c.fix_success])
        
        report.append(f"## Summary")
        report.append(f"- ✅ Healthy: {healthy}")
        report.append(f"- ⚠️ Warning: {warning}")
        report.append(f"- 🔴 Error: {error}")
        report.append(f"- 🔧 Auto-fixed: {fixed}")
        report.append("")
        
        if error > 0:
            report.append("## Errors Requiring Attention")
            for check in checks:
                if check.status == "error":
                    report.append(f"\n### {check.component}")
                    report.append(f"{check.message}")
            report.append("")
        
        return "\n".join(report)
    
    def run(self) -> Dict:
        """Main execution"""
        # Ensure directories
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        # Run checks
        checks = self.run_health_check()
        
        # Attempt repairs
        attempted, fixed = self.attempt_repairs(checks)
        
        # Generate report
        report = self.generate_report(checks)
        report_file = MEMORY_DIR / "maintenance" / "report.md"
        with open(report_file, "w") as f:
            f.write(report)
        
        # Save state
        state = {
            "last_run": datetime.now().isoformat(),
            "total_checks": len(checks),
            "healthy": len([c for c in checks if c.status == "healthy"]),
            "warning": len([c for c in checks if c.status == "warning"]),
            "error": len([c for c in checks if c.status == "error"]),
            "auto_fixed": fixed
        }
        
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
        
        return {
            "success": True,
            "total_checks": len(checks),
            "errors": len([c for c in checks if c.status == "error"]),
            "auto_fixed": fixed,
            "report": str(report_file)
        }


def main():
    parser = argparse.ArgumentParser(description="Autonomous Maintenance & Repair")
    args = parser.parse_args()
    
    amr = AutonomousMaintenanceRepair()
    result = amr.run()
    
    if result.get("success"):
        print(f"✓ Maintenance complete")
        print(f"  Checks: {result['total_checks']}")
        print(f"  Errors: {result['errors']}")
        print(f"  Auto-fixed: {result['auto_fixed']}")
    else:
        print(f"✗ Error")


if __name__ == "__main__":
    main()
