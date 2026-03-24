#!/usr/bin/env python3
"""
SEE Skill Audit Report
Generated: 2026-03-11
Auditor: SEE (Skill Evolution Engine)
"""

import json
from pathlib import Path
from datetime import datetime

class SkillAuditor:
    def __init__(self, skills_dir="/home/skux/.openclaw/workspace/skills"):
        self.skills_dir = Path(skills_dir)
        self.results = {}
    
    def audit_all(self):
        """Run full skill audit"""
        print("=" * 60)
        print("  SEE SKILL AUDIT REPORT")
        print("=" * 60)
        print(f"\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Audited: 36 skills")
        print()
        
        skills_data = []
        
        # Tier 1: Foundation Skills
        tier1 = [
            "context-optimizer", "decision-log", "memory-manager",
            "workspace-organizer", "tool-orchestrator", "code-evolution-tracker"
        ]
        
        # Tier 2: Intelligence Skills
        tier2 = [
            "autonomous-agent", "aloe", "sensory-input-layer",
            "multi-agent-coordinator", "research-synthesizer", "stealth-browser"
        ]
        
        # Tier 3: Income Skills
        tier3 = [
            "autonomous-trading-strategist", "autonomous-opportunity-engine",
            "income-optimizer"
        ]
        
        # Tier 4: Meta Skills
        tier4 = [
            "skill-activation-manager", "skill-evolution-engine", "knowledge-graph-engine",
            "long-term-project-manager"
        ]
        
        # Tier 5: Integration Skills
        tier5 = [
            "event-bus", "integration-orchestrator", "income-stream-expansion-engine"
        ]
        
        # Tier 6: CEO Skills
        tier6 = [
            "autonomous-goal-generator", "autonomous-scheduler",
            "autonomous-maintenance-repair", "autonomous-tool-builder",
            "autonomous-workflow-builder", "autonomous-code-architect",
            "business-strategy-engine", "integration-compatibility-engine",
            "kpi-performance-tracker", "multi-agent-orchestration-engine"
        ]
        
        # Specialty Skills
        specialty = [
            "chart-analyzer", "captcha-solver", "website-designer"
        ]
        
        tiers = [
            ("1. Foundation", tier1),
            ("2. Intelligence", tier2),
            ("3. Income", tier3),
            ("4. Meta", tier4),
            ("5. Integration", tier5),
            ("6. CEO", tier6),
            ("Specialty", specialty)
        ]
        
        all_skills = []
        for tier_name, skills in tiers:
            print(f"\n{'─' * 60}")
            print(f"  TIER {tier_name}")
            print(f"{'─' * 60}")
            for skill_name in skills:
                result = self.audit_skill(skill_name)
                all_skills.append(result)
                print(f"  {result['status']} {skill_name:<35} Score: {result['score']}/100")
        
        # Calculate overall health
        avg_score = sum(s['score'] for s in all_skills) / len(all_skills)
        critical = sum(1 for s in all_skills if s['issues'] == 'CRITICAL')
        warnings = sum(1 for s in all_skills if s['issues'] == 'WARNING')
        
        print()
        print("=" * 60)
        print("  AUDIT SUMMARY")
        print("=" * 60)
        print(f"\n  Overall Health Score: {avg_score:.1f}/100")
        print(f"  Critical Issues: {critical}")
        print(f"  Warnings: {warnings}")
        print(f"  Healthy Skills: {len(all_skills) - critical - warnings}/{len(all_skills)}")
        
        # Recommendations
        print()
        print("=" * 60)
        print("  RECOMMENDATIONS")
        print("=" * 60)
        
        recommendations = self.generate_recommendations(all_skills)
        for i, rec in enumerate(recommendations, 1):
            print(f"\n  {i}. {rec['priority']}: {rec['message']}")
            print(f"     Impact: {rec['impact']}")
            print(f"     Effort: {rec['effort']}")
        
        print()
        print("=" * 60)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_skills': len(all_skills),
            'avg_score': avg_score,
            'critical': critical,
            'warnings': warnings,
            'details': all_skills,
            'recommendations': recommendations
        }
    
    def audit_skill(self, name):
        """Audit individual skill"""
        skill_path = self.skills_dir / name
        
        # Base score
        score = 100
        issues = []
        status = "✅"
        issue_level = "NONE"
        
        # Check if exists
        if not skill_path.exists():
            score -= 40
            issues.append("Skill directory missing")
            status = "❌"
            issue_level = "CRITICAL"
        else:
            # Check SKILL.md
            skill_md = skill_path / "SKILL.md"
            if not skill_md.exists():
                score -= 30
                issues.append("No SKILL.md documentation")
                status = "⚠️"
                issue_level = "CRITICAL"
            else:
                # Check documentation quality
                content = skill_md.read_text() if skill_md.exists() else ""
                if len(content) < 500:
                    score -= 10
                    issues.append("Documentation too brief")
                if "---" not in content[:100]:
                    score -= 5
                    issues.append("Missing YAML frontmatter")
            
            # Check for runnable code
            has_code = list(skill_path.glob("*.py")) or list(skill_path.glob("*.js")) or list(skill_path.glob("*.sh"))
            if not has_code:
                score -= 20
                issues.append("No executable code found")
                if issue_level != "CRITICAL":
                    status = "⚠️"
                    issue_level = "WARNING"
            
            # Check for tests
            has_tests = list(skill_path.glob("*test*.py")) or "test" in str(skill_path).lower()
            if not has_tests:
                score -= 10
                issues.append("No test coverage")
            
            # Check for examples
            has_examples = (skill_path / "examples").exists()
            if not has_examples:
                score -= 5
                # Minor issue
        
        # Cap score
        score = max(0, score)
        
        # Determine status
        if score < 50:
            issue_level = "CRITICAL"
            status = "❌"
        elif score < 80:
            issue_level = "WARNING"
            status = "⚠️"
        
        return {
            'name': name,
            'score': score,
            'status': status,
            'issues': issue_level,
            'issues_list': issues,
            'path': str(skill_path)
        }
    
    def generate_recommendations(self, skills):
        """Generate improvement recommendations"""
        recommendations = []
        
        # Find problematic skills
        critical = [s for s in skills if s['issues'] == 'CRITICAL']
        warnings = [s for s in skills if s['issues'] == 'WARNING']
        
        # High priority
        if critical:
            recommendations.append({
                'priority': 'HIGH',
                'message': f'Fix {len(critical)} critical skill(s): {", ".join(c["name"] for c in critical[:3])}',
                'impact': 'Restores broken functionality',
                'effort': '2-4 hours per skill'
            })
        
        # Medium priority
        low_score = [s for s in skills if s['score'] < 70]
        if low_score:
            recommendations.append({
                'priority': 'MEDIUM',
                'message': f'Improve documentation for {len(low_score)} underperforming skills',
                'impact': 'Better usability and adoption',
                'effort': '1-2 hours per skill'
            })
        
        # Opportunity
        untested = [s for s in skills if 'No test coverage' in s.get('issues_list', [])]
        if untested:
            recommendations.append({
                'priority': 'LOW',
                'message': f'Add test coverage to {len(untested)} skills',
                'impact': 'Improved reliability and maintenance',
                'effort': '2-3 hours per skill'
            })
        
        # Strategic recommendation
        recommendations.append({
            'priority': 'STRATEGIC',
            'message': 'Consider skill consolidation - 36 skills may cause cognitive overhead',
            'impact': 'Simpler maintenance, clearer usage',
            'effort': 'Medium (analysis required)'
        })
        
        return recommendations

if __name__ == "__main__":
    auditor = SkillAuditor()
    results = auditor.audit_all()
    
    # Save to file
    output_path = "/home/skux/.openclaw/workspace/memory/see_audit_results.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📊 Full report saved to: {output_path}")
