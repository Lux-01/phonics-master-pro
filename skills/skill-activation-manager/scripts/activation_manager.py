#!/usr/bin/env python3
"""
Skill Activation Manager (SAM)
Wakes up dormant skills and maximizes utilization across the ALOE ecosystem.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

class DormancyStatus(Enum):
    ACTIVE = "active"                    # Used in last 7 days
    UNDER_UTILIZED = "under-utilized"    # Last use 7-21 days
    DORMANT = "dormant"                  # Last use 21-45 days
    FORGOTTEN = "forgotten"              # 45+ days
    ARCHIVE_CANDIDATE = "archive"        # 90+ days

@dataclass
class SkillUsage:
    skill_name: str
    last_used: datetime
    times_used_this_week: int
    times_used_this_month: int
    total_uses: int
    successful_outcomes: int
    avg_satisfaction: float
    total_time_saved_minutes: int

@dataclass
class SkillActivationRecord:
    skill_name: str
    activated_at: datetime
    activation_trigger: str
    user_accepted: bool
    outcome: Optional[str]

class SkillActivationManager:
    """Monitors and activates dormant skills."""
    
    # All skills in the ecosystem
    ALL_SKILLS = [
        "context-optimizer",
        "decision-log",
        "workspace-organizer",
        "research-synthesizer",
        "tool-orchestrator",
        "code-evolution-tracker",
        "memory-manager",
        "autonomous-agent",
        "aloe",
        "sensory-input-layer",
        "multi-agent-coordinator",
        "autonomous-trading-strategist",
        "long-term-project-manager",
        "autonomous-workflow-builder",
        "knowledge-graph-engine",
        "autonomous-opportunity-engine",
        "skill-evolution-engine",
        "skill-activation-manager",
        "event-bus",
        "integration-orchestrator",
        "income-optimizer"
    ]
    
    DORMANCY_THRESHOLDS = {
        DormancyStatus.ACTIVE: 7,
        DormancyStatus.UNDER_UTILIZED: 21,
        DormancyStatus.DORMANT: 45,
        DormancyStatus.FORGOTTEN: 90,
        DormancyStatus.ARCHIVE_CANDIDATE: float('inf')
    }
    
    def __init__(self, memory_path: str = "/home/skux/.openclaw/workspace/memory"):
        self.memory_path = Path(memory_path)
        self.sam_path = self.memory_path / "sam"
        self.usage_file = self.sam_path / "utilization" / "skill_usage.json"
        self.dormancy_file = self.sam_path / "dormancy" / "dormant_skills.json"
        self.audit_file = self.sam_path / "utilization" / "weekly_reports.json"
        
        self._ensure_directories()
        
    def _ensure_directories(self):
        """Create necessary directories."""
        directories = [
            self.sam_path / "utilization",
            self.sam_path / "dormancy",
            self.sam_path / "prompts",
            self.sam_path / "strategies"
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def record_usage(self, skill_name: str, outcome: str = "success", 
                     time_saved: int = 0, satisfaction: float = 5.0) -> None:
        """Record a skill usage event."""
        usage_data = self._load_usage_data()
        
        if skill_name not in usage_data:
            usage_data[skill_name] = {
                "first_used": datetime.now().isoformat(),
                "total_uses": 0,
                "successful_outcomes": 0,
                "total_time_saved_minutes": 0,
                "satisfaction_scores": []
            }
        
        entry = usage_data[skill_name]
        entry["last_used"] = datetime.now().isoformat()
        entry["total_uses"] = entry.get("total_uses", 0) + 1
        entry["successful_outcomes"] = entry.get("successful_outcomes", 0) + (1 if outcome == "success" else 0)
        entry["total_time_saved_minutes"] = entry.get("total_time_saved_minutes", 0) + time_saved
        entry["satisfaction_scores"].append(satisfaction)
        
        # Keep only last 20 satisfaction scores
        entry["satisfaction_scores"] = entry["satisfaction_scores"][-20:]
        
        self._save_usage_data(usage_data)
        
    def get_skill_status(self, skill_name: str) -> Optional[SkillUsage]:
        """Get current status of a skill."""
        usage_data = self._load_usage_data()
        
        if skill_name not in usage_data:
            return None
        
        entry = usage_data[skill_name]
        last_used = datetime.fromisoformat(entry.get("last_used", entry["first_used"]))
        now = datetime.now()
        
        # Calculate weekly/monthly usage
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        # Get usage history if available
        history = entry.get("history", [])
        week_uses = sum(1 for h in history if datetime.fromisoformat(h["timestamp"]) > week_ago)
        month_uses = sum(1 for h in history if datetime.fromisoformat(h["timestamp"]) > month_ago)
        
        satisfaction_scores = entry.get("satisfaction_scores", [5.0])
        avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores) if satisfaction_scores else 5.0
        
        return SkillUsage(
            skill_name=skill_name,
            last_used=last_used,
            times_used_this_week=week_uses,
            times_used_this_month=month_uses,
            total_uses=entry.get("total_uses", 0),
            successful_outcomes=entry.get("successful_outcomes", 0),
            avg_satisfaction=avg_satisfaction,
            total_time_saved_minutes=entry.get("total_time_saved_minutes", 0)
        )
    
    def get_dormancy_status(self, skill_name: str) -> DormancyStatus:
        """Determine dormancy status of a skill."""
        usage = self.get_skill_status(skill_name)
        
        if usage is None:
            return DormancyStatus.FORGOTTEN  # Never used
        
        days_since_use = (datetime.now() - usage.last_used).days
        
        if days_since_use <= self.DORMANCY_THRESHOLDS[DormancyStatus.ACTIVE]:
            return DormancyStatus.ACTIVE
        elif days_since_use <= self.DORMANCY_THRESHOLDS[DormancyStatus.UNDER_UTILIZED]:
            return DormancyStatus.UNDER_UTILIZED
        elif days_since_use <= self.DORMANCY_THRESHOLDS[DormancyStatus.DORMANT]:
            return DormancyStatus.DORMANT
        elif days_since_use <= self.DORMANCY_THRESHOLDS[DormancyStatus.FORGOTTEN]:
            return DormancyStatus.FORGOTTEN
        else:
            return DormancyStatus.ARCHIVE_CANDIDATE
    
    def get_all_dormant_skills(self, threshold: DormancyStatus = DormancyStatus.UNDER_UTILIZED) -> List[str]:
        """Get list of all skills at or above a dormancy threshold."""
        dormant = []
        for skill in self.ALL_SKILLS:
            status = self.get_dormancy_status(skill)
            if self._status_rank(status) >= self._status_rank(threshold):
                dormant.append(skill)
        return dormant
    
    def _status_rank(self, status: DormancyStatus) -> int:
        """Get numeric rank for status comparison."""
        ranks = {
            DormancyStatus.ACTIVE: 0,
            DormancyStatus.UNDER_UTILIZED: 1,
            DormancyStatus.DORMANT: 2,
            DormancyStatus.FORGOTTEN: 3,
            DormancyStatus.ARCHIVE_CANDIDATE: 4
        }
        return ranks.get(status, 0)
    
    def analyze_dormancy_reason(self, skill_name: str) -> str:
        """Analyze why a skill went dormant."""
        usage = self.get_skill_status(skill_name)
        
        if usage is None:
            return "never_used"
        
        if usage.total_uses < 3:
            return "low_adoption"
        
        if usage.avg_satisfaction < 3.5:
            return "low_satisfaction"
        
        if usage.total_time_saved_minutes < 10:
            return "low_perceived_value"
        
        return "unknown"
    
    def generate_contextual_prompt(self, skill_name: str, user_context: Dict[str, Any]) -> Optional[str]:
        """Generate a contextual prompt for skill activation."""
        prompts = {
            "context-optimizer": {
                "triggers": ["session_length", "confusion", "re-reading"],
                "template": "Your session has {session_length} messages. The context-optimizer can summarize what we've done so far to help you get back on track. Want me to do that?"
            },
            "decision-log": {
                "triggers": ["comparing", "choosing", "trade-off"],
                "template": "This looks like an important decision. Want me to document the trade-offs in the decision-log for future reference?"
            },
            "workspace-organizer": {
                "triggers": ["cluttered", "disorganized", "many_files"],
                "template": "I notice your workspace has {file_count} files. Want me to run the workspace-organizer to clean up and detect duplicates?"
            },
            "research-synthesizer": {
                "triggers": ["research", "compare", "analyze"],
                "template": "I can use the research-synthesizer to pull from multiple sources and summarize findings. Want the full multi-source analysis?"
            },
            "tool-orchestrator": {
                "triggers": ["multiple_tools", "complex_task"],
                "template": "This needs {tool_count} tools in sequence. Want me to use the tool-orchestrator to parallelize and optimize this workflow?"
            },
            "code-evolution-tracker": {
                "triggers": ["refactoring", "improving", "editing"],
                "template": "You've edited {file_name} {edit_count} times. Want me to track this evolution with the code-evolution-tracker?"
            },
            "memory-manager": {
                "triggers": ["remember", "what did I", "last time"],
                "template": "I can search through our past conversations with the memory-manager to find what we discussed about {topic}. Want me to do that?"
            },
            "long-term-project-manager": {
                "triggers": ["deadline", "milestone", "multi-day"],
                "template": "This looks like a multi-day project. Want me to create a project in LPM to track tasks, deadlines, and progress?"
            },
            "autonomous-workflow-builder": {
                "triggers": ["every time", "always", "repetitive"],
                "template": "You seem to do this task regularly. Want me to use AWB to create a reusable workflow for it?"
            },
            "knowledge-graph-engine": {
                "triggers": ["related", "connections", "ecosystem"],
                "template": "This involves understanding relationships between multiple concepts. Want me to map this with the knowledge-graph-engine?"
            }
        }
        
        if skill_name not in prompts:
            return None
        
        template = prompts[skill_name]["template"]
        
        # Fill context
        try:
            return template.format(**user_context)
        except:
            return template
    
    def run_weekly_audit(self) -> Dict:
        """Run a weekly skill utilization audit."""
        now = datetime.now()
        audit = {
            "date": now.isoformat(),
            "active_skills": [],
            "under_utilized": [],
            "dormant": [],
            "forgotten": [],
            "archive_candidates": [],
            "recommendations": []
        }
        
        for skill in self.ALL_SKILLS:
            status = self.get_dormancy_status(skill)
            usage = self.get_skill_status(skill)
            
            entry = {
                "skill": skill,
                "days_since_use": (now - (usage.last_used if usage else now)).days if usage else 999,
                "total_uses": usage.total_uses if usage else 0
            }
            
            if status == DormancyStatus.ACTIVE:
                audit["active_skills"].append(entry)
            elif status == DormancyStatus.UNDER_UTILIZED:
                audit["under_utilized"].append(entry)
            elif status == DormancyStatus.DORMANT:
                audit["dormant"].append(entry)
            elif status == DormancyStatus.FORGOTTEN:
                audit["forgotten"].append(entry)
            elif status == DormancyStatus.ARCHIVE_CANDIDATE:
                audit["archive_candidates"].append(entry)
        
        # Generate recommendations
        if audit["dormant"]:
            audit["recommendations"].append({
                "type": "activation",
                "priority": "high",
                "skills": [s["skill"] for s in audit["dormant"]],
                "action": "Create contextual prompts for dormant skills"
            })
        
        # Save audit
        audits = self._load_json(self.audit_file, [])
        audits.append(audit)
        self._save_json(self.audit_file, audits[-10:])  # Keep last 10
        
        return audit
    
    def format_audit_report(self, audit: Dict) -> str:
        """Format audit as readable report."""
        lines = [
            "# SAM Weekly Skill Audit",
            f"**Date:** {datetime.now().strftime('%Y-%m-%d')}",
            "",
            "## Summary",
            f"- ✅ Active: {len(audit['active_skills'])} skills",
            f"- ⚠️ Under-utilized: {len(audit['under_utilized'])} skills",
            f"- 🔴 Dormant: {len(audit['dormant'])} skills",
            f"- ⚫ Forgotten: {len(audit['forgotten'])} skills",
            "",
            "## Dormant Skills Requiring Activation"
        ]
        
        for skill_entry in audit['dormant']:
            lines.append(f"\n### {skill_entry['skill']}")
            lines.append(f"- Days since use: {skill_entry['days_since_use']}")
            lines.append(f"- Total uses: {skill_entry['total_uses']}")
            reason = self.analyze_dormancy_reason(skill_entry['skill'])
            lines.append(f"- Likely reason: {reason}")
        
        if audit['recommendations']:
            lines.append("\n## Recommended Actions")
            for rec in audit['recommendations']:
                lines.append(f"\n### {rec['type'].upper()}")
                lines.append(f"- Priority: {rec['priority']}")
                lines.append(f"- Skills: {', '.join(rec['skills'])}")
                lines.append(f"- Action: {rec['action']}")
        
        return "\n".join(lines)
    
    def suggest_skills_for_task(self, task_description: str) -> List[str]:
        """Suggest skills appropriate for a given task description."""
        task_lower = task_description.lower()
        suggestions = []
        
        keywords = {
            "context-optimizer": ["confused", "lost", "remind", "summary"],
            "decision-log": ["decide", "choose", "compare", "option"],
            "workspace-organizer": ["organize", "clean", "clutter", "files"],
            "research-synthesizer": ["research", "find", "information", "sources"],
            "tool-orchestrator": ["workflow", "multiple", "sequence", "steps"],
            "code-evolution-tracker": ["code", "refactor", "improve", "optimize"],
            "memory-manager": ["remember", "past", "previous", "history"],
            "long-term-project-manager": ["project", "deadline", "milestone", "track"],
            "autonomous-workflow-builder": ["automate", "repetitive", "every time"],
            "knowledge-graph-engine": ["relationship", "connect", "ecosystem", "map"],
            "autonomous-trading-strategist": ["crypto", "trade", "token", "market"],
            "autonomous-opportunity-engine": ["opportunity", "alpha", "scan", "hunt"]
        }
        
        for skill, words in keywords.items():
            if any(word in task_lower for word in words):
                status = self.get_dormancy_status(skill)
                if status != DormancyStatus.ACTIVE:
                    suggestions.append(skill)
        
        return suggestions
    
    def _load_usage_data(self) -> Dict:
        """Load usage data from file."""
        return self._load_json(self.usage_file, {})
    
    def _save_usage_data(self, data: Dict):
        """Save usage data to file."""
        self._save_json(self.usage_file, data)
    
    def _load_json(self, path: Path, default: Any) -> Any:
        """Load JSON from file."""
        if path.exists():
            with open(path, 'r') as f:
                return json.load(f)
        return default
    
    def _save_json(self, path: Path, data: Any):
        """Save JSON to file."""
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)


def main():
    """CLI for activation manager."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Skill Activation Manager")
    parser.add_argument('--audit', action='store_true', help='Run weekly audit')
    parser.add_argument('--status', action='store_true', help='Show skill status')
    parser.add_argument('--dormant', action='store_true', help='List dormant skills')
    parser.add_argument('--suggest', type=str, help='Suggest skills for task')
    parser.add_argument('--record', nargs=2, metavar=('SKILL', 'OUTCOME'), 
                       help='Record skill usage')
    
    args = parser.parse_args()
    sam = SkillActivationManager()
    
    if args.audit:
        audit = sam.run_weekly_audit()
        print(sam.format_audit_report(audit))
    elif args.status:
        for skill in sam.ALL_SKILLS[:10]:  # First 10
            usage = sam.get_skill_status(skill)
            status = sam.get_dormancy_status(skill)
            if usage:
                print(f"{skill}: {status.value} (last used: {(datetime.now() - usage.last_used).days} days ago)")
    elif args.dormant:
        dormant = sam.get_all_dormant_skills(DormancyStatus.UNDER_UTILIZED)
        print("Dormant/Under-utilized Skills:")
        for skill in dormant:
            status = sam.get_dormancy_status(skill)
            usage = sam.get_skill_status(skill)
            days = (datetime.now() - usage.last_used).days if usage else "never"
            print(f"  - {skill}: {status.value} ({days} days)")
    elif args.suggest:
        suggestions = sam.suggest_skills_for_task(args.suggest)
        print(f"Suggested skills for: {args.suggest}")
        for skill in suggestions:
            print(f"  - {skill}")
    elif args.record:
        sam.record_usage(args.record[0], args.record[1])
        print(f"Recorded usage: {args.record[0]} - {args.record[1]}")
    else:
        print("SAM - Skill Activation Manager")
        print("Use --audit, --status, --dormant, --suggest, or --record")

if __name__ == "__main__":
    main()
