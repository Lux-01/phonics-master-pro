#!/usr/bin/env python3
"""
Skill Evolution Engine for Scanners
Self-audits, analyzes, and evolves scanner capabilities automatically.
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

# Paths
SEE_DIR = Path("/home/skux/.openclaw/workspace/skills/skill-evolution-engine")
MEMORY_DIR = Path("/home/skux/.openclaw/workspace/memory/skill_evolution")
AUDIT_DIR = MEMORY_DIR / "audits"
PROPOSALS_DIR = MEMORY_DIR / "proposals"
METRICS_DIR = MEMORY_DIR / "metrics"

for d in [SEE_DIR, MEMORY_DIR, AUDIT_DIR, PROPOSALS_DIR, METRICS_DIR]:
    d.mkdir(parents=True, exist_ok=True)


class ScannerEvolver:
    """
    Self-evolving system for scanners.
    Analyzes, proposes improvements, implements with approval.
    """
    
    def __init__(self):
        self.audit_dir = AUDIT_DIR
        self.proposals_dir = PROPOSALS_DIR
        self.metrics_dir = METRICS_DIR
        
    def audit_scanner(self, scanner_file: str) -> Dict[str, Any]:
        """
        Perform comprehensive self-audit of a scanner.
        """
        file_path = Path(f"/home/skux/.openclaw/workspace/{scanner_file}")
        
        if not file_path.exists():
            return {"error": "Scanner not found", "file": scanner_file}
        
        audit_id = f"AUDIT-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Read scanner code
        with open(file_path) as f:
            code = f.read()
        
        # Perform analysis
        audit = {
            "id": audit_id,
            "timestamp": datetime.now().isoformat(),
            "scanner_file": scanner_file,
            "health_score": 0,
            "findings": self._analyze_scanner(code, scanner_file),
            "recommendations": [],
            "performance_metrics": self._get_performance_metrics(scanner_file),
            "comparison": self._compare_with_history(scanner_file),
            "improvement_opportunities": []
        }
        
        # Calculate health score
        audit["health_score"] = self._calculate_health_score(audit["findings"])
        
        # Generate recommendations
        audit["recommendations"] = self._generate_recommendations(audit)
        
        # Find opportunities
        audit["improvement_opportunities"] = self._find_opportunities(audit)
        
        self._save_audit(audit)
        
        return audit
    
    def _analyze_scanner(self, code: str, scanner_file: str) -> Dict:
        """Deep analysis of scanner code."""
        findings = {
            "outdated": [],
            "inefficient": [],
            "missing": [],
            "contradicting": [],
            "redundant": [],
            "security": [],
            "performance": [],
            "maintainability": []
        }
        
        # Check for outdated API versions
        if "Jupiter API v4" in code:
            findings["outdated"].append({
                "issue": "Jupiter API v4 mentioned",
                "fix": "Upgrade to Jupiter API v6",
                "impact": "MEDIUM"
            })
        
        if "DexScreener API v1" in code:
            findings["outdated"].append({
                "issue": "Old DexScreener API",
                "fix": "Update to latest schema",
                "impact": "LOW"
            })
        
        # Check for inefficient patterns
        if "requests.get" in code and "async" not in code and "await" not in code:
            # Check if sequential calls are being made
            api_calls = code.count("requests.get")
            if api_calls >= 3:
                findings["inefficient"].append({
                    "issue": f"Sequential API calls ({api_calls} found)",
                    "fix": "Parallelize with asyncio/aiohttp",
                    "expected_improvement": f"~{api_calls * 0.5}s faster",
                    "impact": "HIGH"
                })
        
        # Check for missing features
        if "slippage" not in code.lower():
            findings["missing"].append({
                "issue": "No slippage calculation",
                "fix": "Add slippage model for entry/exit",
                "reason": "Important for execution quality",
                "impact": "MEDIUM"
            })
        
        if "time_stop" not in code.lower():
            findings["missing"].append({
                "issue": "No time-based stop loss",
                "fix": "Add 4h/6h time stop logic",
                "reason": "Risk management gap",
                "impact": "HIGH"
            })
        
        if "pattern_learning" not in code.lower():
            findings["missing"].append({
                "issue": "No pattern learning from outcomes",
                "fix": "Integrate with ALOE outcomes",
                "reason": "Could prevent future false positives",
                "impact": "HIGH"
            })
        
        # Check for contradictions
        if "age >= 6" in code and "grade A" in code.lower():
            # Check if there's a younger allowance
            if "age >= 2" in code and "A" in code:
                findings["contradicting"].append({
                    "issue": "Age requirements inconsistent",
                    "details": "Multiple thresholds without clear logic",
                    "fix": "Standardize age requirements",
                    "impact": "MEDIUM"
                })
        
        # Check for redundancy
        if code.count("try:") >= 5 and code.count("except") >= 5:
            # Check for duplicate error handling patterns
            error_patterns = re.findall(r'except \w+ as e:', code)
            unique_errors = set(error_patterns)
            if len(error_patterns) > len(unique_errors) * 1.5:
                findings["redundant"].append({
                    "issue": "Potentially duplicate error handling",
                    "details": f"{len(error_patterns)} handlers, {len(unique_errors)} unique",
                    "fix": "Consolidate error handling into functions",
                    "impact": "LOW"
                })
        
        # Security checks
        if "api_key" in code.lower():
            if "os.getenv" not in code and "environ" not in code:
                findings["security"].append({
                    "issue": "API key possibly hardcoded",
                    "fix": "Use environment variables",
                    "impact": "CRITICAL"
                })
        
        # Performance checks
        if re.search(r'for .* in .*\n.*for .* in', code):
            findings["performance"].append({
                "issue": "Nested loops detected",
                "fix": "Consider vectorization or pre-computation",
                "impact": "MEDIUM"
            })
        
        # Maintainability
        lines = code.split('\n')
        if len(lines) > 500:
            findings["maintainability"].append({
                "issue": f"Large file ({len(lines)} lines)",
                "fix": "Consider breaking into modules",
                "impact": "MEDIUM"
            })
        
        if len([l for l in lines if l.strip() and not l.strip().startswith('#')]) > 0:
            comment_ratio = len([l for l in lines if l.strip().startswith('#')]) / len([l for l in lines if l.strip()])
            if comment_ratio < 0.05:
                findings["maintainability"].append({
                    "issue": f"Low comment ratio ({comment_ratio:.1%})",
                    "fix": "Add docstrings and inline comments",
                    "impact": "LOW"
                })
        
        return findings
    
    def _get_performance_metrics(self, scanner_file: str) -> Dict:
        """Get performance metrics from outcome tracking."""
        try:
            outcomes_file = Path("/home/skux/.openclaw/workspace/memory/outcomes/trading_outcomes.json")
            if outcomes_file.exists():
                with open(outcomes_file) as f:
                    outcomes = json.load(f)
                
                scanner_outcomes = [o for o in outcomes if scanner_file in o.get('scanner_version', '')]
                
                if scanner_outcomes:
                    rugs = sum(1 for o in scanner_outcomes if o['outcome'].get('status') == 'RUG')
                    profits = sum(1 for o in scanner_outcomes if o['outcome'].get('status') == 'PROFIT')
                    
                    total_closed = len([o for o in scanner_outcomes if o['outcome'].get('status') in ['RUG', 'PROFIT', 'LOSS']])
                    
                    if total_closed > 0:
                        accuracy = profits / total_closed
                        rug_rate = rugs / total_closed
                    else:
                        accuracy = 0
                        rug_rate = 0
                    
                    return {
                        "total_signals": len(scanner_outcomes),
                        "rugs": rugs,
                        "profits": profits,
                        "accuracy": f"{accuracy:.1%}",
                        "rug_rate": f"{rug_rate:.1%}",
                        "grade_a_accuracy": self._calculate_grade_a_accuracy(scanner_outcomes)
                    }
        except:
            pass
        
        return {
            "total_signals": 0,
            "rugs": 0,
            "profits": 0,
            "accuracy": "N/A",
            "rug_rate": "N/A",
            "grade_a_accuracy": "N/A"
        }
    
    def _calculate_grade_a_accuracy(self, outcomes: List[Dict]) -> str:
        """Calculate accuracy specifically for Grade A signals."""
        grade_a = [o for o in outcomes if 'A' in str(o.get('scanner', {}).get('grade', ''))]
        
        if not grade_a:
            return "N/A"
        
        rugs = sum(1 for o in grade_a if o['outcome'].get('status') == 'RUG')
        profits = sum(1 for o in grade_a if o['outcome'].get('status') == 'PROFIT')
        total = len([o for o in grade_a if o['outcome'].get('status') in ['RUG', 'PROFIT', 'LOSS']])
        
        if total > 0:
            return f"{(profits / total):.1%}"
        
        return "N/A"
    
    def _compare_with_history(self, scanner_file: str) -> Dict:
        """Compare with previous audits."""
        audit_files = sorted(self.audit_dir.glob(f"AUDIT-*-{scanner_file.replace('.py', '')}.json"))
        
        if len(audit_files) >= 2:
            # Compare with previous
            with open(audit_files[-2]) as f:
                previous = json.load(f)
            
            return {
                "previous_audit": previous.get('id'),
                "previous_health": previous.get('health_score'),
                "trend": "improving" if previous.get('health_score', 0) < 100 else "stable"
            }
        
        return {"previous_audit": None, "trend": "new"}
    
    def _calculate_health_score(self, findings: Dict) -> int:
        """Calculate overall health score."""
        score = 100
        
        # Deduct for critical issues
        score -= len(findings.get('security', [])) * 20
        score -= len(findings.get('outdated', [])) * 10
        
        # Deduct for high impact
        score -= len([f for f in findings.get('inefficient', []) if f.get('impact') == 'HIGH']) * 5
        score -= len([f for f in findings.get('missing', []) if f.get('impact') == 'HIGH']) * 5
        
        # Deduct for medium
        score -= len([f for f in findings.get('inefficient', []) if f.get('impact') == 'MEDIUM']) * 3
        score -= len([f for f in findings.get('missing', []) if f.get('impact') == 'MEDIUM']) * 3
        
        # Deduct for low
        score -= len(findings.get('inefficient', [])) * 1
        score -= len(findings.get('redundant', [])) * 1
        score -= len(findings.get('maintainability', [])) * 1
        
        return max(0, score)
    
    def _generate_recommendations(self, audit: Dict) -> List[Dict]:
        """Generate prioritized recommendations."""
        recommendations = []
        findings = audit['findings']
        
        # Prioritize by impact
        priority_order = ['security', 'missing', 'inefficient', 'outdated', 'contradicting', 'redundant', 'maintainability']
        
        for category in priority_order:
            for finding in findings.get(category, []):
                rec = {
                    "category": category,
                    "issue": finding.get('issue'),
                    "fix": finding.get('fix'),
                    "priority": self._calculate_priority(category, finding),
                    "estimated_time": self._estimate_fix_time(finding),
                    "impact": finding.get('impact', 'LOW'),
                    "confidence": 0.85
                }
                recommendations.append(rec)
        
        # Sort by priority
        priority_rank = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        recommendations.sort(key=lambda x: priority_rank.get(x['priority'], 4))
        
        return recommendations
    
    def _calculate_priority(self, category: str, finding: Dict) -> str:
        """Calculate priority for a finding."""
        if category == 'security':
            return "CRITICAL"
        if finding.get('impact') == 'HIGH':
            return "HIGH"
        if finding.get('impact') == 'MEDIUM':
            return "MEDIUM"
        return "LOW"
    
    def _estimate_fix_time(self, finding: Dict) -> str:
        """Estimate time to fix."""
        fix = finding.get('fix', '')
        
        if 'Parallelize' in fix:
            return "2-4 hours"
        if 'Add' in fix:
            return "1-2 hours"
        if 'Upgrade' in fix:
            return "30-60 min"
        if 'Refactor' in fix:
            return "4-8 hours"
        
        return "30-60 min"
    
    def _find_opportunities(self, audit: Dict) -> List[Dict]:
        """Find improvement opportunities."""
        opportunities = []
        
        metrics = audit.get('performance_metrics', {})
        
        # If rug rate is high, suggest pattern learning
        if metrics.get('rug_rate', '0%').rstrip('%').isdigit():
            rug_rate = float(metrics['rug_rate'].rstrip('%'))
            if rug_rate > 10:
                opportunities.append({
                    "type": "pattern_learning",
                    "opportunity": "Implement ALOE pattern learning",
                    "potential_impact": f"Reduce {rug_rate:.0f}% rug rate to ~5%",
                    "effort": "3-5 hours",
                    "roi": "HIGH"
                })
        
        # If accuracy is low, suggest feature improvements
        if metrics.get('accuracy', '0%').rstrip('%').isdigit():
            accuracy = float(metrics['accuracy'].rstrip('%'))
            if accuracy < 70:
                opportunities.append({
                    "type": "feature_improvement",
                    "opportunity": "Add more filters (age, whale, narrative)",
                    "potential_impact": f"Improve {accuracy:.0f}% to 80%+",
                    "effort": "2-4 hours",
                    "roi": "HIGH"
                })
        
        # Always suggest parallelization for performance
        findings = audit.get('findings', {})
        for finding in findings.get('inefficient', []):
            if 'Parallelize' in str(finding.get('fix', '')):
                opportunities.append({
                    "type": "performance",
                    "opportunity": finding.get('issue'),
                    "potential_impact": finding.get('expected_improvement', 'Faster'),
                    "effort": "2-3 hours",
                    "roi": "MEDIUM"
                })
        
        return opportunities
    
    def _save_audit(self, audit: Dict):
        """Save audit to disk."""
        audit_file = self.audit_dir / f"{audit['id']}-{audit['scanner_file'].replace('.py', '')}.json"
        with open(audit_file, 'w') as f:
            json.dump(audit, f, indent=2)
    
    def generate_proposal(self, audit_id: str, recommendation_index: int) -> Optional[Dict]:
        """Generate implementation proposal."""
        audit = self._load_audit(audit_id)
        if not audit or recommendation_index >= len(audit.get('recommendations', [])):
            return None
        
        rec = audit['recommendations'][recommendation_index]
        
        proposal = {
            "id": f"PROP-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "audit_id": audit_id,
            "based_on_recommendation": rec,
            "status": "PENDING_APPROVAL",
            "created": datetime.now().isoformat(),
            "requires_approval": rec.get('priority') in ['CRITICAL', 'HIGH'],
            "implementation_plan": self._create_implementation_plan(rec),
            "testing_plan": self._create_testing_plan(rec),
            "rollback_plan": self._create_rollback_plan(rec)
        }
        
        self._save_proposal(proposal)
        
        return proposal
    
    def _load_audit(self, audit_id: str) -> Optional[Dict]:
        """Load an audit by ID."""
        for audit_file in self.audit_dir.glob(f"{audit_id}*.json"):
            with open(audit_file) as f:
                return json.load(f)
        return None
    
    def _save_proposal(self, proposal: Dict):
        """Save proposal to disk."""
        proposal_file = self.proposals_dir / f"{proposal['id']}.json"
        with open(proposal_file, 'w') as f:
            json.dump(proposal, f, indent=2)
    
    def _create_implementation_plan(self, rec: Dict) -> str:
        """Create step-by-step implementation plan."""
        return f"""## Implementation Plan

1. **Backup** current scanner file
2. **Create** test cases for {rec.get('issue')}
3. **Implement** fix: {rec.get('fix')}
4. **Test** against test cases
5. **Run** full scanner test suite
6. **Compare** results with baseline
7. **Commit** changes if tests pass
"""

    def _create_testing_plan(self, rec: Dict) -> List[str]:
        """Create testing checklist."""
        return [
            "Test with known good token",
            "Test with known bad token",
            "Test edge cases",
            "Verify performance",
            "Check error handling"
        ]
    
    def _create_rollback_plan(self, rec: Dict) -> str:
        """Create rollback plan."""
        return """## Rollback Plan

If issues detected:
1. Restore from backup
2. Re-run scanner to verify fix
3. Investigate what went wrong
4. Create new proposal with fixes
"""
    
    def list_pending_proposals(self) -> List[Dict]:
        """List all pending proposals."""
        proposals = []
        for prop_file in self.proposals_dir.glob("PROP-*.json"):
            with open(prop_file) as f:
                prop = json.load(f)
                if prop.get('status') == 'PENDING_APPROVAL':
                    proposals.append(prop)
        return proposals
    
    def approve_proposal(self, proposal_id: str) -> bool:
        """Mark proposal as approved."""
        prop_file = self.proposals_dir / f"{proposal_id}.json"
        if prop_file.exists():
            with open(prop_file) as f:
                prop = json.load(f)
            prop['status'] = 'APPROVED'
            prop['approved_at'] = datetime.now().isoformat()
            with open(prop_file, 'w') as f:
                json.dump(prop, f, indent=2)
            return True
        return False
    
    def reject_proposal(self, proposal_id: str, reason: str) -> bool:
        """Mark proposal as rejected."""
        prop_file = self.proposals_dir / f"{proposal_id}.json"
        if prop_file.exists():
            with open(prop_file) as f:
                prop = json.load(f)
            prop['status'] = 'REJECTED'
            prop['rejected_at'] = datetime.now().isoformat()
            prop['rejection_reason'] = reason
            with open(prop_file, 'w') as f:
                json.dump(prop, f, indent=2)
            return True
        return False


# Global instance
evolver = ScannerEvolver()


def audit_scanner(scanner_file: str) -> Dict:
    """Quick audit function."""
    return evolver.audit_scanner(scanner_file)


def generate_proposal(audit_id: str, rec_index: int) -> Optional[Dict]:
    """Quick proposal function."""
    return evolver.generate_proposal(audit_id, rec_index)


def list_proposals() -> List[Dict]:
    """Quick list function."""
    return evolver.list_pending_proposals()


if __name__ == "__main__":
    print("🧬 Skill Evolution Engine - Scanner Evolver")
    print("=" * 60)
    
    # Example: Audit v54 scanner
    print("\n🔍 Auditing scanner...")
    audit = audit_scanner("solana_alpha_hunter_v54.py")
    
    print(f"✅ Audit complete: {audit['id']}")
    print(f"   Health Score: {audit['health_score']}/100")
    
    print(f"\n📊 Findings:")
    for category, findings in audit['findings'].items():
        if findings:
            print(f"   {category.upper()}: {len(findings)} issues")
    
    print(f"\n📈 Performance:")
    print(f"   Total signals: {audit['performance_metrics']['total_signals']}")
    print(f"   Rug rate: {audit['performance_metrics']['rug_rate']}")
    print(f"   Grade A accuracy: {audit['performance_metrics']['grade_a_accuracy']}")
    
    print(f"\n💡 Top Recommendations:")
    for i, rec in enumerate(audit['recommendations'][:3], 1):
        print(f"   {i}. [{rec['priority']}] {rec['issue'][:50]}...")
    
    print(f"\n🧬 Scanner Evolver ready!")
