#!/usr/bin/env python3
"""
Long-Term Project Manager v1.0
Tracks multi-day projects, deadlines, dependencies

## ACA Plan:
1. Requirements: Track projects, deadlines, dependencies → generate reports
2. Architecture: ProjectStore → DeadlineTracker → DependencyResolver → Reporter
3. Data Flow: Parse memory → Track projects → Check deadlines → Alert on issues
4. Edge Cases: No projects, overdue deadlines, circular deps, completed projects
5. Tool Constraints: File read, JSON, datetime calc
6. Error Handling: File access, parse errors, date issues
7. Testing: Test with sample projects

Author: Autonomous Code Architect (ACA)
"""

import argparse
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

WORKSPACE_DIR = Path("/home/skux/.openclaw/workspace")
MEMORY_DIR = WORKSPACE_DIR / "memory"


class ProjectStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class Project:
    name: str
    description: str
    status: ProjectStatus
    deadline: Optional[datetime]
    dependencies: List[str]
    progress: float  # 0-100
    created_at: datetime
    completed_at: Optional[datetime] = None
    milestones: List[Dict] = field(default_factory=list)


class LongTermProjectManager:
    def __init__(self):
        self.projects: List[Project] = []
        self.projects_file = MEMORY_DIR / "projects" / "projects.json"
    
    def parse_projects_from_memory(self) -> List[Project]:
        """Extract projects from memory files"""
        projects = []
        
        # Parse main memory for projects
        memory_md = MEMORY_DIR / "MEMORY.md"
        if memory_md.exists():
            content = memory_md.read_text()
            
            # Find project sections (## with ###)
            project_pattern = r'##\s*([^#]+?)\s*\n.*?Status:\*\*\s*([^\n]+)'
            for match in re.finditer(project_pattern, content, re.DOTALL):
                name = match.group(1).strip()
                status_str = match.group(2).strip()
                
                # Map status
                status_map = {
                    "Active": ProjectStatus.ACTIVE,
                    "active": ProjectStatus.ACTIVE,
                    "Paused": ProjectStatus.PAUSED,
                    "Completed": ProjectStatus.COMPLETED,
                    "Cancelled": ProjectStatus.CANCELLED
                }
                status = status_map.get(status_str, ProjectStatus.ACTIVE)
                
                projects.append(Project(
                    name=name,
                    description=f"From MEMORY.md",
                    status=status,
                    deadline=None,
                    dependencies=[],
                    progress=0.0,
                    created_at=datetime.now()
                ))
        
        return projects
    
    def check_deadlines(self) -> List[Dict]:
        """Check for approaching/overdue deadlines"""
        alerts = []
        today = datetime.now()
        
        for project in self.projects:
            if not project.deadline:
                continue
            
            days_until = (project.deadline - today).days
            
            if days_until < 0:
                alerts.append({
                    "project": project.name,
                    "alert": "OVERDUE",
                    "days": days_until,
                    "severity": "high"
                })
            elif days_until <= 3:
                alerts.append({
                    "project": project.name,
                    "alert": "DUE_SOON",
                    "days": days_until,
                    "severity": "medium"
                })
        
        return alerts
    
    def generate_report(self) -> str:
        """Generate project status report"""
        if not self.projects:
            return "No projects tracked."
        
        report = []
        report.append("# Project Status Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d')}")
        report.append("")
        
        # Group by status
        active = [p for p in self.projects if p.status == ProjectStatus.ACTIVE]
        paused = [p for p in self.projects if p.status == ProjectStatus.PAUSED]
        completed = [p for p in self.projects if p.status == ProjectStatus.COMPLETED]
        
        report.append(f"## Summary")
        report.append(f"- Active: {len(active)}")
        report.append(f"- Paused: {len(paused)}")
        report.append(f"- Completed: {len(completed)}")
        report.append("")
        
        if active:
            report.append("## Active Projects")
            for p in active:
                report.append(f"\n### {p.name}")
                report.append(f"- Progress: {p.progress:.0f}%")
                if p.deadline:
                    report.append(f"- Deadline: {p.deadline.strftime('%Y-%m-%d')}")
        
        # Check deadlines
        alerts = self.check_deadlines()
        if alerts:
            report.append("\n## ⚠️ Deadline Alerts")
            for alert in alerts:
                icon = "🔴" if alert["severity"] == "high" else "🟡"
                report.append(f"{icon} **{alert['project']}**: {alert['alert']} ({abs(alert['days'])} days)")
        
        return "\n".join(report)
    
    def run(self) -> Dict:
        """Main execution"""
        # Ensure directories
        self.projects_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Parse projects
        self.projects = self.parse_projects_from_memory()
        
        # Save
        projects_data = {
            "updated": datetime.now().isoformat(),
            "count": len(self.projects),
            "projects": [
                {
                    "name": p.name,
                    "description": p.description,
                    "status": p.status.value,
                    "progress": p.progress
                }
                for p in self.projects
            ]
        }
        
        with open(self.projects_file, "w") as f:
            json.dump(projects_data, f, indent=2)
        
        # Generate report
        report = self.generate_report()
        report_file = MEMORY_DIR / "projects" / "report.md"
        with open(report_file, "w") as f:
            f.write(report)
        
        return {
            "success": True,
            "projects_tracked": len(self.projects),
            "active": len([p for p in self.projects if p.status == ProjectStatus.ACTIVE]),
            "report": str(report_file)
        }


def main():
    parser = argparse.ArgumentParser(description="Long-Term Project Manager")
    args = parser.parse_args()
    
    manager = LongTermProjectManager()
    result = manager.run()
    
    if result.get("success"):
        print(f"✓ Project tracking complete")
        print(f"  Projects: {result['projects_tracked']}")
        print(f"  Active: {result['active']}")
    else:
        print(f"✗ Error")


if __name__ == "__main__":
    main()
