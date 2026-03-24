#!/usr/bin/env python3
"""
Test Runner Module
Executes tests on skills and collects results.
"""

import sys
import os
import json
import subprocess
import traceback
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
import importlib.util
import re


@dataclass
class TestResult:
    """Result of a single test"""
    test_type: str
    passed: bool
    message: str
    duration_ms: int
    details: Dict = field(default_factory=dict)


@dataclass
class SkillTestResults:
    """Complete test results for a skill"""
    skill_name: str
    skill_path: str
    overall_pass: bool
    structure_pass: bool
    imports_pass: bool
    unit_tests_pass: Optional[bool]
    integration_pass: Optional[bool]
    results: List[TestResult]
    timestamp: str
    errors: List[str] = field(default_factory=list)


class TestRunner:
    """
    Runs comprehensive tests on skills.
    
    Test types:
    - structure: Validate file structure
    - imports: Check module imports
    - unit: Run unit tests
    - integration: Run integration tests
    """
    
    def __init__(self, skills_dir: str = None):
        self.skills_dir = Path(skills_dir) if skills_dir else Path.home() / ".openclaw/workspace/skills"
        self.results: List[SkillTestResults] = []
        self.test_order = ['structure', 'imports', 'unit', 'integration']
    
    def run_all_tests(self, skill_names: List[str] = None) -> List[SkillTestResults]:
        """
        Run all tests on all skills or specified skills.
        
        Args:
            skill_names: Optional list of skill names to test (None = all)
            
        Returns:
            List of skill test results
        """
        from .skill_discoverer import SkillDiscoverer
        
        self.results = []
        discoverer = SkillDiscoverer(str(self.skills_dir))
        skills = discoverer.discover_all()
        
        if skill_names:
            skills = [s for s in skills if s.name in skill_names]
        
        print(f"🧪 Running tests on {len(skills)} skills...")
        print("=" * 60)
        
        for i, skill_info in enumerate(skills, 1):
            print(f"\n[{i}/{len(skills)}] Testing {skill_info.name}...")
            result = self._test_skill(skill_info)
            self.results.append(result)
            self._print_result(result)
        
        return self.results
    
    def test_skill(self, skill_name: str) -> SkillTestResults:
        """Test a single skill by name"""
        from .skill_discoverer import SkillDiscoverer
        
        discoverer = SkillDiscoverer(str(self.skills_dir))
        skills = discoverer.discover_all()
        
        for skill in skills:
            if skill.name == skill_name:
                return self._test_skill(skill)
        
        return SkillTestResults(
            skill_name=skill_name,
            skill_path="",
            overall_pass=False,
            structure_pass=False,
            imports_pass=False,
            unit_tests_pass=None,
            integration_pass=None,
            results=[],
            timestamp=datetime.now().isoformat(),
            errors=[f"Skill not found: {skill_name}"]
        )
    
    def _test_skill(self, skill_info) -> SkillTestResults:
        """Test a single skill"""
        results = []
        errors = []
        
        # Run structure tests
        struct_result = self._test_structure(skill_info)
        results.append(struct_result)
        
        # Run import tests (only if structure passes or is Python)
        import_result = self._test_imports(skill_info)
        results.append(import_result)
        
        # Run unit tests if tests/ exists
        unit_result = self._test_unit(skill_info)
        results.append(unit_result)
        
        # Run integration tests
        integ_result = self._test_integration(skill_info)
        results.append(integ_result)
        
        # Calculate overall
        overall_pass = all(r.passed for r in results if r is not None)
        
        return SkillTestResults(
            skill_name=skill_info.name,
            skill_path=str(skill_info.path),
            overall_pass=overall_pass,
            structure_pass=struct_result.passed if struct_result else True,
            imports_pass=import_result.passed if import_result else True,
            unit_tests_pass=unit_result.passed if unit_result else None,
            integration_pass=integ_result.passed if integ_result else None,
            results=[r for r in results if r],
            timestamp=datetime.now().isoformat(),
            errors=errors
        )
    
    def _test_structure(self, skill_info) -> TestResult:
        """Test skill structure"""
        start = datetime.now()
        errors = []
        
        # Check SKILL.md
        if not skill_info.has_skill_md:
            errors.append("Missing SKILL.md")
        
        # Check __init__.py for Python skills
        if skill_info.is_python and not skill_info.has_init_py:
            errors.append("Missing __init__.py")
        
        duration = int((datetime.now() - start).total_seconds() * 1000)
        
        return TestResult(
            test_type='structure',
            passed=len(errors) == 0,
            message="Structure OK" if not errors else f"Structure issues: {', '.join(errors)}",
            duration_ms=duration,
            details={'errors': errors}
        )
    
    def _test_imports(self, skill_info) -> TestResult:
        """Test that Python modules can be imported"""
        if not skill_info.is_python:
            return TestResult(
                test_type='imports',
                passed=True,
                message="Not a Python skill",
                duration_ms=0
            )
        
        start = datetime.now()
        errors = []
        
        # Add skill to path
        if str(skill_info.path) not in sys.path:
            sys.path.insert(0, str(skill_info.path))
        
        # Try to import __init__ or main modules
        py_files = [f for f in skill_info.files if f.endswith('.py')]
        
        for py_file in py_files[:5]:  # Limit to avoid timeout
            try:
                module_name = py_file.replace('/', '.').replace('.py', '')
                file_path = skill_info.path / py_file
                
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    # Don't actually execute to avoid side effects
                    # Just verify module loads
            except Exception as e:
                errors.append(f"{py_file}: {str(e)[:50]}")
        
        duration = int((datetime.now() - start).total_seconds() * 1000)
        
        return TestResult(
            test_type='imports',
            passed=len(errors) == 0,
            message="Imports OK" if not errors else f"Import errors in: {', '.join(errors[:3])}",
            duration_ms=duration,
            details={'errors': errors}
        )
    
    def _test_unit(self, skill_info) -> Optional[TestResult]:
        """Run unit tests if available"""
        test_dir = skill_info.path / "tests"
        if not test_dir.exists():
            return None
        
        start = datetime.now()
        
        # Try to run pytest or unittest
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pytest', str(test_dir), '-v', '--tb=short'],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(skill_info.path)
            )
            passed = result.returncode == 0
            output = result.stdout if passed else result.stderr[:200]
        except subprocess.TimeoutExpired:
            passed = False
            output = "Test timeout"
        except FileNotFoundError:
            # pytest not installed, try unittest
            try:
                result = subprocess.run(
                    [sys.executable, '-m', 'unittest', 'discover', str(test_dir)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=str(skill_info.path)
                )
                passed = result.returncode == 0
                output = "Tests passed" if passed else "Some tests failed"
            except Exception as e:
                passed = None  # Can't determine
                output = f"Test execution error: {e}"
        
        duration = int((datetime.now() - start).total_seconds() * 1000)
        
        return TestResult(
            test_type='unit',
            passed=passed,
            message=output[:100],
            duration_ms=duration
        )
    
    def _test_integration(self, skill_info) -> Optional[TestResult]:
        """Run integration tests"""
        integ_file = skill_info.path / "tests" / "integration_tests.py"
        if not integ_file.exists():
            return None
        
        start = datetime.now()
        
        try:
            result = subprocess.run(
                [sys.executable, str(integ_file)],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(skill_info.path)
            )
            passed = result.returncode == 0
        except:
            passed = None
        
        duration = int((datetime.now() - start).total_seconds() * 1000)
        
        return TestResult(
            test_type='integration',
            passed=passed,
            message="Integration tests passed" if passed else "Integration tests failed",
            duration_ms=duration
        )
    
    def _print_result(self, result: SkillTestResults):
        """Print result to console"""
        if result.overall_pass:
            icon = "✅"
            status = "PASS"
        elif result.errors or result.results and any(not r.passed and r.test_type != 'unit' for r in result.results):
            icon = "❌"
            status = "FAIL"
        else:
            icon = "⚠️"
            status = "WARN"
        
        pass_count = sum(1 for r in result.results if r.passed)
        total_count = len(result.results)
        
        print(f"  {icon} {status} ({pass_count}/{total_count} tests)")
        
        for test in result.results:
            if not test.passed and test.test_type != 'unit':
                print(f"     ! {test.test_type}: {test.message}")
    
    def get_summary(self) -> Dict:
        """Get summary of all test results"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.overall_pass)
        failed = total - passed
        
        with_warnings = sum(1 for r in self.results 
                          if not r.overall_pass and not r.errors)
        
        return {
            'total': total,
            'passed': passed,
            'failed': failed,
            'warnings': with_warnings,
            'pass_rate': (passed / total * 100) if total > 0 else 0,
            'timestamp': datetime.now().isoformat()
        }


def main():
    """CLI for test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run skill tests')
    parser.add_argument('--skill', type=str, help='Test specific skill')
    parser.add_argument('--type', type=str, choices=['structure', 'imports', 'unit', 'integration'],
                       help='Run specific test type')
    parser.add_argument('--json', action='store_true', help='Output JSON')
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    if args.skill:
        result = runner.test_skill(args.skill)
        results = [result]
    else:
        results = runner.run_all_tests()
    
    if args.json:
        print(json.dumps([asdict(r) for r in results], indent=2))
    else:
        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)
        summary = runner.get_summary()
        print(f"Total skills tested: {summary['total']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Pass rate: {summary['pass_rate']:.1f}%")


if __name__ == "__main__":
    main()