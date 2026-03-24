#!/usr/bin/env python3
"""
Report Generator Module
Creates human-readable and machine-readable test reports.
"""

import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime
from .test_runner import SkillTestResults


class ReportGenerator:
    """
    Generates comprehensive reports from test results.
    
    Output formats:
    - Markdown (human-readable)
    - JSON (machine-readable)
    - HTML (visual dashboard)
    """
    
    def __init__(self, results: List[SkillTestResults] = None):
        self.results = results or []
        self.timestamp = datetime.now()
    
    def generate_markdown(self) -> str:
        """Generate markdown report"""
        lines = [
            "# Skill Testing Report",
            "",
            f"**Generated:** {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Summary",
            ""
        ]
        
        # Overall stats
        total = len(self.results)
        passed = sum(1 for r in self.results if r.overall_pass)
        failed = total - passed
        
        lines.extend([
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Total Skills | {total} |",
            f"| Passed | {passed} |",
            f"| Failed | {failed} |",
            f"| Pass Rate | {(passed/total*100):.1f}% |",
            "",
            "## Results by Skill",
            ""
        ])
        
        # Sort by pass/fail
        sorted_results = sorted(self.results, key=lambda r: (r.overall_pass, r.skill_name))
        
        for result in sorted_results:
            icon = "✅" if result.overall_pass else "❌"
            lines.extend([
                f"### {icon} {result.skill_name}",
                "",
                f"- **Path:** `{result.skill_path}`",
                f"- **Overall:** {'PASS' if result.overall_pass else 'FAIL'}",
                f"- **Structure:** {'✅' if result.structure_pass else '❌'}",
                f"- **Imports:** {'✅' if result.imports_pass else '❌'}",
            ])
            
            if result.unit_tests_pass is not None:
                lines.append(f"- **Unit Tests:** {'✅' if result.unit_tests_pass else '❌'}")
            
            if result.integration_pass is not None:
                lines.append(f"- **Integration:** {'✅' if result.integration_pass else '❌'}")
            
            # Add test details
            lines.append("")
            lines.append("| Test Type | Status | Duration | Message |")
            lines.append("|-----------|--------|----------|----------|")
            
            for test in result.results:
                status = "✅ PASS" if test.passed else "❌ FAIL"
                lines.append(f"| {test.test_type} | {status} | {test.duration_ms}ms | {test.message[:40]} |")
            
            lines.append("")
        
        # Recommendations
        lines.extend([
            "## Recommendations",
            ""
        ])
        
        failed_skills = [r for r in self.results if not r.overall_pass]
        if failed_skills:
            lines.append("### Skills Needing Attention")
            lines.append("")
            for skill in failed_skills:
                lines.append(f"- **{skill.skill_name}**: Check {', '.join([r.test_type for r in skill.results if not r.passed])}")
            lines.append("")
        else:
            lines.append("All skills passed! 🎉")
            lines.append("")
        
        return "\n".join(lines)
    
    def generate_json(self) -> str:
        """Generate JSON report"""
        data = {
            'metadata': {
                'generated_at': self.timestamp.isoformat(),
                'version': '1.0'
            },
            'summary': {
                'total_skills': len(self.results),
                'passed': sum(1 for r in self.results if r.overall_pass),
                'failed': sum(1 for r in self.results if not r.overall_pass),
            },
            'results': [
                {
                    'skill_name': r.skill_name,
                    'skill_path': r.skill_path,
                    'overall_pass': r.overall_pass,
                    'structure_pass': r.structure_pass,
                    'imports_pass': r.imports_pass,
                    'unit_tests_pass': r.unit_tests_pass,
                    'integration_pass': r.integration_pass,
                    'timestamp': r.timestamp,
                    'tests': [
                        {
                            'type': t.test_type,
                            'passed': t.passed,
                            'message': t.message,
                            'duration_ms': t.duration_ms
                        }
                        for t in r.results
                    ]
                }
                for r in self.results
            ]
        }
        
        return json.dumps(data, indent=2)
    
    def generate_html(self) -> str:
        """Generate HTML dashboard"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.overall_pass)
        failed = total - passed
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        html = f'''<!DOCTYPE html>
<html>
<head>
    <title>Skill Testing Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }}
        h1 {{ color: #333; }}
        .summary {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 30px 0; }}
        .stat-box {{ background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
        .stat-value {{ font-size: 36px; font-weight: bold; color: #4a90d9; }}
        .stat-label {{ color: #666; margin-top: 5px; }}
        .skill-item {{ padding: 15px; margin: 10px 0; border-radius: 6px; border-left: 4px solid #ddd; }}
        .skill-pass {{ border-left-color: #28a745; background: #f8fff8; }}
        .skill-fail {{ border-left-color: #dc3545; background: #fff8f8; }}
        .skill-name {{ font-weight: bold; font-size: 16px; }}
        .test-badges {{ margin-top: 8px; }}
        .badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; margin-right: 5px; }}
        .badge-ok {{ background: #d4edda; color: #155724; }}
        .badge-fail {{ background: #f8d7da; color: #721c24; }}
        .badge-na {{ background: #e2e3e5; color: #383d41; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🧪 Skill Testing Report</h1>
        <p>Generated: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div class="summary">
            <div class="stat-box">
                <div class="stat-value">{total}</div>
                <div class="stat-label">Total Skills</div>
            </div>
            <div class="stat-box">
                <div class="stat-value" style="color: #28a745">{passed}</div>
                <div class="stat-label">Passed</div>
            </div>
            <div class="stat-box">
                <div class="stat-value" style="color: #dc3545">{failed}</div>
                <div class="stat-label">Failed</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{pass_rate:.1f}%</div>
                <div class="stat-label">Pass Rate</div>
            </div>
        </div>
        
        <h2>Results</h2>
'''
        
        for result in sorted(self.results, key=lambda r: (not r.overall_pass, r.skill_name)):
            css_class = 'skill-pass' if result.overall_pass else 'skill-fail'
            
            html += f'''
        <div class="skill-item {css_class}">
            <div class="skill-name">{result.skill_name}</div>
            <div class="test-badges">
                <span class="badge {'badge-ok' if result.structure_pass else 'badge-fail'}">structure</span>
                <span class="badge {'badge-ok' if result.imports_pass else 'badge-fail'}">imports</span>
                <span class="badge {'badge-ok' if result.unit_tests_pass else 'badge-fail' if result.unit_tests_pass is not None else 'badge-na'}">unit tests</span>
                <span class="badge {'badge-ok' if result.integration_pass else 'badge-fail' if result.integration_pass is not None else 'badge-na'}">integration</span>
            </div>
        </div>
'''
        
        html += '''
    </div>
</body>
</html>'''
        
        return html
    
    def save_reports(self, output_dir: str = None):
        """
        Save all report formats.
        
        Args:
            output_dir: Directory to save reports (default: workspace)
        """
        if output_dir is None:
            output_dir = Path.home() / ".openclaw/workspace"
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Markdown
        md_path = output_dir / "testing_report.md"
        md_path.write_text(self.generate_markdown())
        
        # JSON
        json_path = output_dir / "testing_report.json"
        json_path.write_text(self.generate_json())
        
        # HTML
        html_path = output_dir / "testing_report.html"
        html_path.write_text(self.generate_html())
        
        return {
            'markdown': str(md_path),
            'json': str(json_path),
            'html': str(html_path)
        }
    
    def print_summary(self):
        """Print summary to console"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.overall_pass)
        failed = total - passed
        
        print("\n" + "=" * 60)
        print("📊 Test Summary")
        print("=" * 60)
        print(f"\nTotal skills tested: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Pass rate: {(passed/total*100):.1f}%")
        
        if failed > 0:
            print("\n⚠️ Skills needing attention:")
            for result in self.results:
                if not result.overall_pass:
                    print(f"  - {result.skill_name}")


def main():
    """CLI for report generation"""
    import argparse
    from .test_runner import TestRunner
    
    parser = argparse.ArgumentParser(description='Generate test reports')
    parser.add_argument('--format', choices=['markdown', 'json', 'html', 'all'],
                       default='markdown', help='Output format')
    parser.add_argument('--output', type=str, help='Output directory')
    
    args = parser.parse_args()
    
    # Run tests
    runner = TestRunner()
    results = runner.run_all_tests()
    
    # Generate report
    generator = ReportGenerator(results)
    
    if args.format == 'markdown':
        print(generator.generate_markdown())
    elif args.format == 'json':
        print(generator.generate_json())
    elif args.format == 'html':
        print(generator.generate_html())
    else:  # all
        paths = generator.save_reports(args.output)
        print("Saved reports:")
        for fmt, path in paths.items():
            print(f"  {fmt}: {path}")


if __name__ == "__main__":
    main()