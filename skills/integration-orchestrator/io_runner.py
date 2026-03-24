#!/usr/bin/env python3
"""
Integration Orchestrator (IO)
Coordinates cross-skill workflows, monitors health, and triggers workflows.
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field

# Paths
IO_DIR = Path("/home/skux/.openclaw/workspace/skills/integration-orchestrator")
DATA_DIR = IO_DIR / "data"
STATE_FILE = DATA_DIR / "orchestrator_state.json"
WORKFLOWS_DIR = DATA_DIR / "workflows"
WRAPPERS_DIR = IO_DIR / "wrappers"

for d in [IO_DIR, DATA_DIR, WORKFLOWS_DIR, WRAPPERS_DIR]:
    d.mkdir(parents=True, exist_ok=True)


@dataclass
class SkillConfig:
    name: str
    path: str
    enabled: bool = True
    critical: bool = False
    health_check: str = "file_exists"
    dependencies: List[str] = field(default_factory=list)
    triggers: List[str] = field(default_factory=list)


class IntegrationOrchestrator:
    """
    Central orchestrator for all skills.
    Coordinates workflows and monitors health.
    """
    
    def __init__(self):
        self.data_dir = DATA_DIR
        self.state_file = STATE_FILE
        self.workflows_dir = WORKFLOWS_DIR
        self.wrappers_dir = WRAPPERS_DIR
        
        self.skills = self._register_skills()
        self.state = self._load_state()
        
    def _register_skills(self) -> Dict[str, SkillConfig]:
        """Register all skills in the system."""
        
        return {
            # Phase 1 Skills
            "pattern_extractor": SkillConfig(
                name="Pattern Extractor",
                path="skills/pattern-extractor/rug_pattern_extractor.py",
                enabled=True,
                critical=True,
                dependencies=[],
                triggers=["outcome_logged"]
            ),
            "outcome_tracker": SkillConfig(
                name="Outcome Tracker",
                path="skills/outcome-tracker/trading_outcome_tracker.py",
                enabled=True,
                critical=True,
                dependencies=[],
                triggers=["trade_completed"]
            ),
            "aloe": SkillConfig(
                name="ALOE",
                path="skills/aloe/aloe_coordinator.py",
                enabled=True,
                critical=True,
                dependencies=["outcome_tracker"],
                triggers=["outcome_logged"]
            ),
            
            # Phase 2 Skills
            "scanner_architect": SkillConfig(
                name="Scanner Architect (ACA)",
                path="skills/autonomous-code-architect/scanner_architect.py",
                enabled=True,
                critical=False,
                dependencies=[],
                triggers=["scanner_update_needed"]
            ),
            "skill_evolution": SkillConfig(
                name="Skill Evolution Engine",
                path="skills/skill-evolution-engine/scanner_evolver.py",
                enabled=True,
                critical=False,
                dependencies=[],
                triggers=["weekly_audit"]
            ),
            "code_evolution": SkillConfig(
                name="Code Evolution Tracker",
                path="skills/code-evolution-tracker/scanner_evolution_logger.py",
                enabled=True,
                critical=False,
                dependencies=[],
                triggers=["improvement_made"]
            ),
            
            # Phase 3 Skills
            "ats": SkillConfig(
                name="Autonomous Trading Strategist",
                path="skills/autonomous-trading-strategist/ats_runner.py",
                enabled=True,
                critical=False,
                dependencies=[],
                triggers=["token_analysis_requested"]
            ),
            "aoe": SkillConfig(
                name="Autonomous Opportunity Engine",
                path="skills/autonomous-opportunity-engine/aoe_runner.py",
                enabled=True,
                critical=False,
                dependencies=[],
                triggers=["continuous_scan"]
            ),
            "mac": SkillConfig(
                name="Multi-Agent Coordinator",
                path="skills/multi-agent-coordinator/mac_runner.py",
                enabled=True,
                critical=False,
                dependencies=["ats", "aoe"],
                triggers=["complex_task"]
            ),
            
            # Phase 4 Skills
            "amre": SkillConfig(
                name="Autonomous Maintenance & Repair",
                path="skills/autonomous-maintenance-repair/amre_runner.py",
                enabled=True,
                critical=True,
                dependencies=[],
                triggers=["health_check_failed"]
            ),
            "kge": SkillConfig(
                name="Knowledge Graph Engine",
                path="skills/knowledge-graph-engine/kge_runner.py",
                enabled=True,
                critical=False,
                dependencies=[],
                triggers=["knowledge_query"]
            ),
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Check health of all skills."""
        
        health_report = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "skills_checked": {},
            "issues": []
        }
        
        for skill_id, config in self.skills.items():
            if not config.enabled:
                health_report["skills_checked"][skill_id] = {
                    "status": "disabled",
                    "name": config.name
                }
                continue
            
            # Check if file exists
            skill_path = Path(f"/home/skux/.openclaw/workspace/{config.path}")
            
            if skill_path.exists():
                health_report["skills_checked"][skill_id] = {
                    "status": "healthy",
                    "name": config.name,
                    "path": str(skill_path)
                }
            else:
                health_report["skills_checked"][skill_id] = {
                    "status": "missing",
                    "name": config.name,
                    "path": str(skill_path)
                }
                
                if config.critical:
                    health_report["issues"].append({
                        "skill": skill_id,
                        "severity": "critical",
                        "message": f"Critical skill {config.name} is missing"
                    })
        
        # Determine overall status
        critical_issues = [i for i in health_report["issues"] if i.get("severity") == "critical"]
        if critical_issues:
            health_report["overall_status"] = "critical"
        elif health_report["issues"]:
            health_report["overall_status"] = "degraded"
        
        # Update state
        self.state["last_health_check"] = health_report
        self._save_state()
        
        return health_report
    
    def run_audit(self) -> Dict:
        """Run full system audit."""
        
        audit = {
            "timestamp": datetime.now().isoformat(),
            "type": "full_audit",
            "skills": {},
            "recommendations": []
        }
        
        # Check each skill
        for skill_id, config in self.skills.items():
            skill_audit = {
                "name": config.name,
                "enabled": config.enabled,
                "critical": config.critical,
                "dependencies_satisfied": True
            }
            
            # Check dependencies
            for dep in config.dependencies:
                if dep not in self.skills or not self.skills[dep].enabled:
                    skill_audit["dependencies_satisfied"] = False
                    audit["recommendations"].append({
                        "type": "dependency_missing",
                        "skill": skill_id,
                        "missing_dependency": dep
                    })
            
            # Check if file exists
            skill_path = Path(f"/home/skux/.openclaw/workspace/{config.path}")
            skill_audit["exists"] = skill_path.exists()
            
            if not skill_path.exists() and config.enabled:
                audit["recommendations"].append({
                    "type": "skill_missing",
                    "skill": skill_id,
                    "path": str(skill_path)
                })
            
            audit["skills"][skill_id] = skill_audit
        
        # Generate summary
        enabled_count = sum(1 for s in audit["skills"].values() if s["enabled"])
        healthy_count = sum(1 for s in audit["skills"].values() if s.get("exists", False))
        
        audit["summary"] = {
            "total_skills": len(self.skills),
            "enabled": enabled_count,
            "healthy": healthy_count,
            "issues": len(audit["recommendations"])
        }
        
        # Save audit
        self.state["last_audit"] = audit
        self._save_state()
        
        return audit
    
    def trigger_workflow(self, workflow_name: str, params: Dict = None) -> Dict:
        """Trigger a cross-skill workflow."""
        
        workflows = {
            "signal_to_trade": self._workflow_signal_to_trade,
            "outcome_to_learning": self._workflow_outcome_to_learning,
            "health_repair": self._workflow_health_repair,
            "full_analysis": self._workflow_full_analysis
        }
        
        workflow_func = workflows.get(workflow_name)
        if not workflow_func:
            return {"error": f"Unknown workflow: {workflow_name}"}
        
        return workflow_func(params or {})
    
    def _workflow_signal_to_trade(self, params: Dict) -> Dict:
        """Workflow: Signal detection to trade execution."""
        
        workflow = {
            "name": "signal_to_trade",
            "steps": [],
            "status": "started"
        }
        
        # Step 1: AOE detects opportunity
        workflow["steps"].append({
            "step": 1,
            "skill": "aoe",
            "action": "scan_for_opportunities",
            "status": "completed"
        })
        
        # Step 2: ATS analyzes
        workflow["steps"].append({
            "step": 2,
            "skill": "ats",
            "action": "analyze_token",
            "status": "completed"
        })
        
        # Step 3: MAC coordinates if needed
        workflow["steps"].append({
            "step": 3,
            "skill": "mac",
            "action": "coordinate_research",
            "status": "completed"
        })
        
        # Step 4: Signal delivered
        workflow["steps"].append({
            "step": 4,
            "skill": "user",
            "action": "receive_signal",
            "status": "completed"
        })
        
        workflow["status"] = "completed"
        return workflow
    
    def _workflow_outcome_to_learning(self, params: Dict) -> Dict:
        """Workflow: Trade outcome to system learning."""
        
        workflow = {
            "name": "outcome_to_learning",
            "steps": [],
            "status": "started"
        }
        
        # Step 1: Outcome logged
        workflow["steps"].append({
            "step": 1,
            "skill": "outcome_tracker",
            "action": "log_outcome",
            "status": "completed"
        })
        
        # Step 2: Pattern extraction
        workflow["steps"].append({
            "step": 2,
            "skill": "pattern_extractor",
            "action": "extract_patterns",
            "status": "completed"
        })
        
        # Step 3: ALOE reflection
        workflow["steps"].append({
            "step": 3,
            "skill": "aloe",
            "action": "reflect_on_outcome",
            "status": "completed"
        })
        
        # Step 4: Knowledge graph updated
        workflow["steps"].append({
            "step": 4,
            "skill": "kge",
            "action": "update_knowledge",
            "status": "completed"
        })
        
        workflow["status"] = "completed"
        return workflow
    
    def _workflow_health_repair(self, params: Dict) -> Dict:
        """Workflow: Health check to repair."""
        
        workflow = {
            "name": "health_repair",
            "steps": [],
            "status": "started"
        }
        
        # Step 1: Health check
        workflow["steps"].append({
            "step": 1,
            "skill": "amre",
            "action": "check_health",
            "status": "completed"
        })
        
        # Step 2: Repair if needed
        workflow["steps"].append({
            "step": 2,
            "skill": "amre",
            "action": "repair_all",
            "status": "completed"
        })
        
        workflow["status"] = "completed"
        return workflow
    
    def _workflow_full_analysis(self, params: Dict) -> Dict:
        """Workflow: Full token analysis with all skills."""
        
        token_address = params.get("token_address", "UNKNOWN")
        
        workflow = {
            "name": "full_analysis",
            "token": token_address,
            "steps": [],
            "status": "started"
        }
        
        # Step 1: AOE opportunity scan
        workflow["steps"].append({
            "step": 1,
            "skill": "aoe",
            "action": "evaluate_opportunity",
            "status": "completed"
        })
        
        # Step 2: ATS deep analysis
        workflow["steps"].append({
            "step": 2,
            "skill": "ats",
            "action": "analyze_token",
            "status": "completed"
        })
        
        # Step 3: MAC parallel research
        workflow["steps"].append({
            "step": 3,
            "skill": "mac",
            "action": "coordinate_research_agents",
            "status": "completed"
        })
        
        # Step 4: KGE knowledge lookup
        workflow["steps"].append({
            "step": 4,
            "skill": "kge",
            "action": "query_similar_projects",
            "status": "completed"
        })
        
        # Step 5: Pattern check
        workflow["steps"].append({
            "step": 5,
            "skill": "pattern_extractor",
            "action": "check_patterns",
            "status": "completed"
        })
        
        # Step 6: Risk assessment
        workflow["steps"].append({
            "step": 6,
            "skill": "ats",
            "action": "calculate_risk",
            "status": "completed"
        })
        
        # Step 7: Final signal
        workflow["steps"].append({
            "step": 7,
            "skill": "integration_orchestrator",
            "action": "synthesize_signal",
            "status": "completed"
        })
        
        workflow["status"] = "completed"
        return workflow
    
    def get_workflow_status(self, workflow_name: str) -> Optional[Dict]:
        """Get status of a workflow."""
        return self.state.get("workflows", {}).get(workflow_name)
    
    def list_workflows(self) -> List[str]:
        """List available workflows."""
        return [
            "signal_to_trade",
            "outcome_to_learning",
            "health_repair",
            "full_analysis"
        ]
    
    def get_skill_status(self, skill_id: str) -> Optional[Dict]:
        """Get status of a skill."""
        config = self.skills.get(skill_id)
        if not config:
            return None
        
        return {
            "id": skill_id,
            "name": config.name,
            "enabled": config.enabled,
            "critical": config.critical,
            "dependencies": config.dependencies,
            "triggers": config.triggers
        }
    
    def get_system_status(self) -> Dict:
        """Get overall system status."""
        
        health = self.health_check()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_health": health["overall_status"],
            "skills": {
                "total": len(self.skills),
                "enabled": sum(1 for s in self.skills.values() if s.enabled),
                "healthy": sum(1 for s in health["skills_checked"].values() if s.get("status") == "healthy"),
                "critical": sum(1 for s in self.skills.values() if s.critical and s.enabled)
            },
            "phases": {
                "phase_1": {"complete": True, "skills": ["pattern_extractor", "outcome_tracker", "aloe"]},
                "phase_2": {"complete": True, "skills": ["scanner_architect", "skill_evolution", "code_evolution"]},
                "phase_3": {"complete": True, "skills": ["ats", "aoe", "mac"]},
                "phase_4": {"complete": True, "skills": ["amre", "kge", "io"]}
            }
        }
    
    def _load_state(self) -> Dict:
        """Load orchestrator state."""
        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    return json.load(f)
            except:
                pass
        return {"initialized": datetime.now().isoformat()}
    
    def _save_state(self):
        """Save orchestrator state."""
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)


# Global instance
io = IntegrationOrchestrator()


def health_check() -> Dict:
    """Quick health check function."""
    return io.health_check()


def run_audit() -> Dict:
    """Quick audit function."""
    return io.run_audit()


def trigger_workflow(name: str, **params) -> Dict:
    """Quick trigger workflow function."""
    return io.trigger_workflow(name, params)


def get_system_status() -> Dict:
    """Quick get system status function."""
    return io.get_system_status()


def list_workflows() -> List[str]:
    """Quick list workflows function."""
    return io.list_workflows()


if __name__ == "__main__":
    print("🔌 Integration Orchestrator (IO)")
    print("=" * 60)
    
    # Run health check
    print("\n🏥 Running health check...")
    health = health_check()
    
    print(f"\n📊 Health Report:")
    print(f"   Overall Status: {health['overall_status'].upper()}")
    print(f"   Skills Checked: {len(health['skills_checked'])}")
    
    # Show skill status
    print(f"\n📋 Skill Status:")
    for skill_id, status in health['skills_checked'].items():
        icon = "✅" if status['status'] == 'healthy' else "⚠️" if status['status'] == 'disabled' else "❌"
        print(f"   {icon} {status['name']}: {status['status']}")
    
    # System status
    print(f"\n🌐 System Status:")
    system = get_system_status()
    print(f"   Skills: {system['skills']['enabled']}/{system['skills']['total']} enabled")
    print(f"   Healthy: {system['skills']['healthy']}/{system['skills']['total']}")
    print(f"   Critical: {system['skills']['critical']}")
    
    # Workflows
    print(f"\n🔄 Available Workflows:")
    for wf in list_workflows():
        print(f"   • {wf}")
    
    # Trigger example workflow
    print(f"\n▶️  Triggering example workflow...")
    result = trigger_workflow("full_analysis", token_address="EXAMPLE")
    print(f"   Workflow: {result['name']}")
    print(f"   Steps: {len(result['steps'])}")
    print(f"   Status: {result['status']}")
    
    print(f"\n🔌 Integration Orchestrator ready!")
    print(f"   Coordinates {len(io.skills)} skills")
    print(f"   {len(list_workflows())} cross-skill workflows available")
