#!/usr/bin/env python3
"""
Skill Evolution Bridge - Wraps existing skill-evolution-engine for Omnibot.

Leverages the proven self-refactoring logic from skill-evolution-engine
to enable Omnibot's self-improvement capabilities.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Import from existing skill-evolution-engine
import sys
SEE_PATH = Path('/home/skux/.openclaw/workspace/skills/skill-evolution-engine')
if str(SEE_PATH) not in sys.path:
    sys.path.insert(0, str(SEE_PATH))

try:
    from skill_evolution_engine import (
        SkillEvolutionEngine,
        SkillHealth,
        ImprovementProposal,
        FindingType,
        Priority,
        SEEConfig
    )
    from see_auditor import SkillAuditor as SEEAuditor
    SEE_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Could not import SEE: {e}")
    SEE_AVAILABLE = False


@dataclass
class ModuleHealth:
    """Health report for an Omnibot module."""
    module_id: str
    module_path: str
    health_score: int
    findings: List[Dict]
    recommendations: List[str]
    last_audit: str


class SkillEvolutionBridge:
    """
    Bridge between Omnibot and skill-evolution-engine.
    
    Wraps SEE's proven self-refactoring logic for Omnibot's self-modification needs.
    """
    
    def __init__(self, omnibot=None):
        self.logger = logging.getLogger("Omnibot.SkillEvolutionBridge")
        self.omnibot = omnibot
        
        # Initialize SEE if available
        if SEE_AVAILABLE:
            self.see = SkillEvolutionEngine()
            self.auditor = SEEAuditor()
            self.logger.info("SEE integration active")
        else:
            self.see = None
            self.auditor = None
            self.logger.warning("SEE not available, using fallback mode")
        
        # Track Omnibot modules
        self.omnibot_dir = Path(__file__).parent.parent
        self.module_health_cache: Dict[str, ModuleHealth] = {}
    
    def get_all_modules(self) -> List[Dict]:
        """
        Get all Omnibot modules for analysis.
        
        Returns:
            List of module dictionaries with paths and metadata
        """
        modules = []
        
        module_dirs = [
            "core", "memory", "reasoning", "research", "api", 
            "wallet", "ui", "meta", "proactive", "perception",
            "platform", "economics", "federation", "dream",
            "job_seeker", "execution", "design", "safety"
        ]
        
        for module_name in module_dirs:
            module_path = self.omnibot_dir / module_name
            if module_path.exists():
                # Get Python files in module
                py_files = list(module_path.glob("*.py"))
                py_files = [f for f in py_files if f.name != "__init__.py"]
                
                modules.append({
                    "name": module_name,
                    "path": str(module_path),
                    "file_count": len(py_files),
                    "files": [str(f) for f in py_files]
                })
        
        return modules
    
    def analyze_omnibot_module(self, module_name: str) -> ModuleHealth:
        """
        Analyze a specific Omnibot module using SEE logic.
        
        Args:
            module_name: Name of the module to analyze
            
        Returns:
            ModuleHealth with findings and recommendations
        """
        module_path = self.omnibot_dir / module_name
        
        if not module_path.exists():
            return ModuleHealth(
                module_id=module_name,
                module_path=str(module_path),
                health_score=0,
                findings=[{"error": "Module not found"}],
                recommendations=["Check module name"],
                last_audit=datetime.now().isoformat()
            )
        
        if SEE_AVAILABLE:
            # Use SEE's analysis capabilities
            try:
                # Create a temporary skill representation
                module_files = list(module_path.rglob("*.py"))
                
                # Run SEE analysis on each file
                findings = []
                for py_file in module_files:
                    if "__pycache__" not in str(py_file):
                        # Use SEE's pattern detection
                        audit = self.auditor._quick_scan_file(py_file)
                        if audit:
                            findings.extend(audit)
                
                # Calculate health score
                health_score = self.auditor._calculate_health_score(findings)
                
                # Generate recommendations
                recommendations = self._generate_module_recommendations(
                    module_name, findings
                )
                
                health = ModuleHealth(
                    module_id=module_name,
                    module_path=str(module_path),
                    health_score=health_score,
                    findings=[f.to_dict() if hasattr(f, 'to_dict') else f for f in findings],
                    recommendations=recommendations,
                    last_audit=datetime.now().isoformat()
                )
                
                self.module_health_cache[module_name] = health
                return health
                
            except Exception as e:
                self.logger.error(f"SEE analysis failed: {e}")
        
        # Fallback: Basic analysis
        return self._fallback_analysis(module_name, module_path)
    
    def _fallback_analysis(self, module_name: str, module_path: Path) -> ModuleHealth:
        """Basic analysis when SEE is not available."""
        findings = []
        recommendations = []
        
        # Check for files
        py_files = list(module_path.rglob("*.py"))
        py_files = [f for f in py_files if "__pycache__" not in str(f)]
        
        if not py_files:
            findings.append({
                "type": "MISSING",
                "description": "No Python files found in module",
                "severity": "high"
            })
        
        # Basic code quality checks
        for py_file in py_files:
            content = py_file.read_text()
            
            # Check for TODOs
            if "TODO" in content or "FIXME" in content:
                findings.append({
                    "type": "DOCUMENTATION",
                    "description": f"TODO/FIXME found in {py_file.name}",
                    "severity": "low"
                })
            
            # Check for docstrings
            if '"""' not in content and "'''" not in content:
                findings.append({
                    "type": "DOCUMENTATION",
                    "description": f"Missing docstrings in {py_file.name}",
                    "severity": "medium"
                })
        
        # Calculate basic health score
        health_score = max(50, 100 - len(findings) * 5)
        
        # Generate basic recommendations
        if any(f.get("severity") == "high" for f in findings):
            recommendations.append("Address high-severity findings first")
        if any(f.get("type") == "DOCUMENTATION" for f in findings):
            recommendations.append("Add proper documentation to improve maintainability")
        
        return ModuleHealth(
            module_id=module_name,
            module_path=str(module_path),
            health_score=health_score,
            findings=findings,
            recommendations=recommendations,
            last_audit=datetime.now().isoformat()
        )
    
    def _generate_module_recommendations(self, module_name: str, 
                                        findings: List[Any]) -> List[str]:
        """Generate recommendations based on findings."""
        recommendations = []
        
        # Check finding types
        finding_types = set()
        for finding in findings:
            if hasattr(finding, 'type'):
                finding_types.add(finding.type)
            elif isinstance(finding, dict):
                finding_types.add(finding.get('type', 'UNKNOWN'))
        
        if FindingType.OUTDATED in finding_types:
            recommendations.append("Update outdated dependencies and APIs")
        if FindingType.INEFFICIENT in finding_types:
            recommendations.append("Optimize performance bottlenecks identified")
        if FindingType.MISSING in finding_types:
            recommendations.append("Add missing error handling and validation")
        if FindingType.SECURITY in finding_types:
            recommendations.append("Address security vulnerabilities immediately")
        
        return recommendations if recommendations else ["Module health is good"]
    
    def analyze_omnibot_performance(self) -> List[ModuleHealth]:
        """
        Analyze all Omnibot modules.
        
        Returns:
            List of ModuleHealth for each module
        """
        modules = self.get_all_modules()
        results = []
        
        for module in modules:
            health = self.analyze_omnibot_module(module["name"])
            results.append(health)
        
        return results
    
    def propose_improvements(self) -> List[Dict]:
        """
        Use SEE to propose improvements for Omnibot.
        
        Returns:
            List of improvement proposals
        """
        if not SEE_AVAILABLE:
            self.logger.warning("SEE not available, cannot generate proposals")
            return []
        
        proposals = []
        
        # Analyze each module
        for module in self.get_all_modules():
            health = self.analyze_omnibot_module(module["name"])
            
            # Create improvement proposal if health is below threshold
            if health.health_score < 85:
                proposal = {
                    "id": f"omnibot_{module['name']}_{int(datetime.now().timestamp())}",
                    "target_module": module['name'],
                    "health_score": health.health_score,
                    "priority": "high" if health.health_score < 60 else "medium",
                    "findings_count": len(health.findings),
                    "description": f"Improve {module['name']} from {health.health_score}/100",
                    "recommendations": health.recommendations,
                    "estimated_effort": self._estimate_effort(health.findings),
                    "created_at": datetime.now().isoformat()
                }
                proposals.append(proposal)
        
        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        proposals.sort(key=lambda p: priority_order.get(p["priority"], 99))
        
        return proposals
    
    def _estimate_effort(self, findings: List[Dict]) -> str:
        """Estimate effort based on findings."""
        count = len(findings)
        if count == 0:
            return "none"
        elif count <= 3:
            return "low (1-2 hours)"
        elif count <= 6:
            return "medium (4-6 hours)"
        else:
            return "high (1-2 days)"
    
    def evolve_with_approval(self, improvement: Dict) -> Dict:
        """
        Full evolution cycle with human approval:
        1. Analyze current code
        2. Generate improved version
        3. Test in sandbox
        4. Ask human for approval
        5. If approved: apply update
        
        Args:
            improvement: Improvement proposal
            
        Returns:
            Evolution result
        """
        self.logger.info(f"Starting evolution cycle for {improvement['target_module']}")
        
        # Step 1: Deep analysis
        module_health = self.analyze_omnibot_module(improvement['target_module'])
        
        # Step 2: Generate improvements (via sandbox)
        from .sandbox_tester import SandboxTester
        sandbox = SandboxTester(self.omnibot)
        
        improvements_made = []
        for py_file in Path(module_health.module_path).rglob("*.py"):
            if "__pycache__" not in str(py_file):
                # Step 3: Test in sandbox
                test_result = sandbox.test_file_modification(py_file)
                
                if test_result["success"]:
                    improvements_made.append({
                        "file": str(py_file.relative_to(self.omnibot_dir)),
                        "changes": test_result.get("changes", []),
                        "tests_passed": test_result.get("tests_passed", False)
                    })
        
        # Step 4: Prepare approval request
        approval_request = {
            "module": improvement['target_module'],
            "original_health": improvement['health_score'],
            "improvements": improvements_made,
            "total_files": len(improvements_made),
            "estimated_improvement": f"+{min(20, len(improvements_made) * 5)} health points",
            "requires_approval": True
        }
        
        self.logger.info(f"Evolution cycle ready: {approval_request}")
        
        return approval_request
    
    def get_overall_health(self) -> Dict:
        """Get overall Omnibot health summary."""
        modules = self.analyze_omnibot_performance()
        
        if not modules:
            return {"error": "No modules analyzed"}
        
        scores = [m.health_score for m in modules]
        avg_health = sum(scores) / len(scores)
        
        return {
            "overall_health": round(avg_health),
            "modules_analyzed": len(modules),
            "modules_by_health": {
                "excellent (90+)": len([m for m in modules if m.health_score >= 90]),
                "good (75-89)": len([m for m in modules if 75 <= m.health_score < 90]),
                "fair (60-74)": len([m for m in modules if 60 <= m.health_score < 75]),
                "poor (<60)": len([m for m in modules if m.health_score < 60])
            },
            "total_findings": sum(len(m.findings) for m in modules),
            "recommendations": sum(len(m.recommendations) for m in modules)
        }
    
    def auto_evolve_low_health_modules(self, threshold: int = 60) -> List[str]:
        """
        Automatically fix low-health modules (for maintenance mode).
        
        Args:
            threshold: Health score below which to auto-fix
            
        Returns:
            List of modules processed
        """
        processed = []
        
        for module in self.get_all_modules():
            health = self.analyze_omnibot_module(module["name"])
            if health.health_score < threshold:
                # Auto-fix simple issues
                self._auto_fix_module(module["name"], health)
                processed.append(module["name"])
        
        return processed
    
    def _auto_fix_module(self, module_name: str, health: ModuleHealth):
        """Apply automatic fixes to a module."""
        self.logger.info(f"Auto-fixing {module_name}")
        
        # Simple fixes: remove unused imports, format code
        module_path = Path(health.module_path)
        
        for py_file in module_path.rglob("*.py"):
            if "__pycache__" not in str(py_file):
                # Read and clean
                content = py_file.read_text()
                
                # Remove duplicate blank lines
                content = self._remove_duplicate_lines(content)
                
                # Ensure file ends with newline
                if not content.endswith('\n'):
                    content += '\n'
                
                # Write back
                py_file.write_text(content)
    
    def _remove_duplicate_lines(self, content: str) -> str:
        """Remove consecutive duplicate blank lines."""
        import re
        return re.sub(r'\n{4,}', '\n\n\n', content)
    
    def generate_evolution_report(self) -> str:
        """Generate a comprehensive evolution report."""
        health = self.get_overall_health()
        proposals = self.propose_improvements()
        
        report = f"""
🧬 OMNIBOT EVOLUTION REPORT
{'='*60}

📊 OVERALL HEALTH: {health.get('overall_health', 'N/A')}/100

Modules: {health.get('modules_analyzed', 0)} analyzed
Findings: {health.get('total_findings', 0)} total
Recommendations: {health.get('recommendations', 0)} total

📈 HEALTH DISTRIBUTION
"""
        for category, count in health.get('modules_by_health', {}).items():
            report += f"  • {category}: {count}\n"
        
        if proposals:
            report += f"\n💡 TOP IMPROVEMENT OPPORTUNITIES\n"
            for i, prop in enumerate(proposals[:3], 1):
                report += f"{i}. {prop['target_module']} ({prop['priority']})\n"
                report += f"   Health: {prop['health_score']}/100\n"
                report += f"   Effort: {prop['estimated_effort']}\n"
        
        report += f"\n{'='*60}\n"
        return report