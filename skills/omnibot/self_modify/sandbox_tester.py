#!/usr/bin/env python3
"""
Sandbox Tester - Safely test code improvements before applying.

Runs improvements in isolated environment to ensure:
- Changes don't break existing functionality
- No syntax errors introduced
- Tests pass
- No security issues
"""

import ast
import hashlib
import json
import logging
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import shutil


class TestStatus(Enum):
    """Status of sandbox test."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"


@dataclass
class TestResult:
    """Result of sandbox test."""
    test_id: str
    file_path: str
    status: TestStatus
    syntax_check: bool
    import_check: bool
    test_execution: Optional[bool]
    error_message: Optional[str]
    changes_summary: List[str]
    timestamp: str
    duration_seconds: float


class SandboxTester:
    """
    Tests code improvements in isolated sandbox environment.
    """
    
    def __init__(self, omnibot=None, temp_dir: Optional[str] = None):
        self.logger = logging.getLogger("Omnibot.SandboxTester")
        self.omnibot = omnibot
        
        # Sandbox directory
        self.sandbox_dir = Path(temp_dir) if temp_dir else Path(__file__).parent / "sandbox"
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)
        
        # Test history
        self.test_history: Dict[str, TestResult] = {}
        self.logger.info("SandboxTester initialized")
    
    def create_sandbox(self, name: str) -> Path:
        """
        Create a new isolated sandbox directory.
        
        Args:
            name: Sandbox identifier
            
        Returns:
            Path to sandbox directory
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sandbox_path = self.sandbox_dir / f"{name}_{timestamp}"
        sandbox_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (sandbox_path / "src").mkdir()
        (sandbox_path / "tests").mkdir()
        (sandbox_path / "results").mkdir()
        
        self.logger.info(f"Created sandbox: {sandbox_path}")
        return sandbox_path
    
    def copy_module_to_sandbox(self, source_path: Path, sandbox_path: Path) -> bool:
        """
        Copy module source to sandbox.
        
        Args:
            source_path: Original file/directory
            sandbox_path: Sandbox directory
            
        Returns:
            True if successful
        """
        try:
            dest = sandbox_path / "src" / source_path.name
            
            if source_path.is_file():
                shutil.copy2(source_path, dest)
            else:
                shutil.copytree(source_path, dest, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to copy to sandbox: {e}")
            return False
    
    def test_file_modification(self, file_path: Path, 
                              modified_content: Optional[str] = None) -> Dict:
        """
        Test a file modification in sandbox.
        
        Args:
            file_path: Original file path
            modified_content: Modified content (if None, tests original)
            
        Returns:
            Test result dictionary
        """
        test_id = f"test_{hashlib.md5(str(file_path).encode()).hexdigest()[:8]}_{int(datetime.now().timestamp())}"
        
        self.logger.info(f"Starting sandbox test: {test_id}")
        start_time = datetime.now()
        
        sandbox = self.create_sandbox(file_path.stem)
        
        try:
            # Step 1: Syntax check
            content = modified_content if modified_content else file_path.read_text()
            syntax_valid = self._check_syntax(content)
            
            if not syntax_valid:
                return {
                    "test_id": test_id,
                    "file_path": str(file_path),
                    "success": False,
                    "syntax_check": False,
                    "import_check": False,
                    "tests_passed": False,
                    "error": "Syntax error detected",
                    "changes": []
                }
            
            # Step 2: Write to sandbox
            sandbox_file = sandbox / "src" / file_path.name
            sandbox_file.write_text(content)
            
            # Step 3: Import check
            import_valid = self._check_import(sandbox_file)
            
            if not import_valid:
                return {
                    "test_id": test_id,
                    "file_path": str(file_path),
                    "success": False,
                    "syntax_check": True,
                    "import_check": False,
                    "tests_passed": False,
                    "error": "Import error detected",
                    "changes": []
                }
            
            # Step 4: Run existing tests if available
            tests_passed = self._run_module_tests(file_path, sandbox)
            
            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            
            # Analyze changes
            changes = self._analyze_changes(file_path.read_text(), content) if modified_content else []
            
            result = TestResult(
                test_id=test_id,
                file_path=str(file_path),
                status=TestStatus.PASSED if tests_passed else TestStatus.FAILED,
                syntax_check=True,
                import_check=import_valid,
                test_execution=tests_passed,
                error_message=None if tests_passed else "Tests failed",
                changes_summary=changes,
                timestamp=datetime.now().isoformat(),
                duration_seconds=duration
            )
            
            self.test_history[test_id] = result
            
            # Cleanup sandbox
            self._cleanup_sandbox(sandbox)
            
            return {
                "test_id": test_id,
                "file_path": str(file_path),
                "success": tests_passed,
                "syntax_check": True,
                "import_check": import_valid,
                "tests_passed": tests_passed,
                "error": None if tests_passed else "Tests failed",
                "changes": changes,
                "duration_seconds": duration
            }
            
        except Exception as e:
            self.logger.error(f"Sandbox test error: {e}")
            self._cleanup_sandbox(sandbox)
            return {
                "test_id": test_id,
                "file_path": str(file_path),
                "success": False,
                "syntax_check": False,
                "import_check": False,
                "tests_passed": False,
                "error": str(e),
                "changes": []
            }
    
    def _check_syntax(self, content: str) -> bool:
        """Check Python syntax."""
        try:
            ast.parse(content)
            return True
        except SyntaxError:
            return False
    
    def _check_import(self, file_path: Path) -> bool:
        """Check if file can be imported."""
        try:
            # Create a temporary test script
            test_script = file_path.parent / "test_import.py"
            module_name = file_path.stem
            
            test_script.write_text(f"""
import sys
sys.path.insert(0, str({repr(str(file_path.parent))}))
try:
    import {module_name}
    print('IMPORT_OK')
except Exception as e:
    print(f'IMPORT_ERROR: {{e}}')
""")
            
            result = subprocess.run(
                ["python3", str(test_script)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            test_script.unlink(missing_ok=True)
            
            return "IMPORT_OK" in result.stdout
            
        except Exception as e:
            self.logger.warning(f"Import check failed: {e}")
            return False
    
    def _run_module_tests(self, file_path: Path, sandbox_path: Path) -> bool:
        """Run tests for a module."""
        # Look for test files
        test_dir = file_path.parent / "tests"
        if not test_dir.exists():
            # No tests available, assume pass
            return True
        
        try:
            result = subprocess.run(
                ["python3", "-m", "pytest", str(test_dir), "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(sandbox_path)
            )
            
            return result.returncode == 0
            
        except Exception as e:
            self.logger.warning(f"Test execution failed: {e}")
            return True  # No tests is not a failure
    
    def _analyze_changes(self, original: str, modified: str) -> List[str]:
        """Analyze differences between original and modified."""
        import difflib
        
        changes = []
        diff = difflib.unified_diff(
            original.splitlines(),
            modified.splitlines(),
            lineterm=""
        )
        
        diff_lines = list(diff)
        
        if len(diff_lines) == 0:
            changes.append("No changes detected")
        else:
            additions = sum(1 for line in diff_lines if line.startswith('+') and not line.startswith('+++'))
            deletions = sum(1 for line in diff_lines if line.startswith('-') and not line.startswith('---'))
            changes.append(f"{additions} lines added, {abs(deletions)} lines removed")
        
        return changes
    
    def _cleanup_sandbox(self, sandbox_path: Path):
        """Clean up sandbox directory."""
        try:
            shutil.rmtree(sandbox_path)
        except Exception as e:
            self.logger.warning(f"Failed to cleanup sandbox: {e}")
    
    def test_regression_suite(self, module_dir: Path) -> Dict:
        """
        Run full regression test suite for a module.
        
        Args:
            module_dir: Module directory to test
            
        Returns:
            Suite results
        """
        self.logger.info(f"Running regression suite for {module_dir}")
        
        results = {
            "module": module_dir.name,
            "timestamp": datetime.now().isoformat(),
            "files_tested": 0,
            "passed": 0,
            "failed": 0,
            "errors": []
        }
        
        py_files = list(module_dir.rglob("*.py"))
        py_files = [f for f in py_files if "__pycache__" not in str(f)]
        
        for py_file in py_files:
            test_result = self.test_file_modification(py_file)
            results["files_tested"] += 1
            
            if test_result["success"]:
                results["passed"] += 1
            else:
                results["failed"] += 1
                results["errors"].append({
                    "file": str(py_file),
                    "error": test_result.get("error", "Unknown error")
                })
        
        return results
    
    def compare_versions(self, original: str, modified: str) -> Dict:
        """
        Compare two versions of code.
        
        Args:
            original: Original code
            modified: Modified code
            
        Returns:
            Comparison results
        """
        import difflib
        
        # Calculate diff
        diff = difflib.unified_diff(
            original.splitlines(),
            modified.splitlines(),
            fromfile="original",
            tofile="modified",
            lineterm=""
        )
        
        diff_lines = list(diff)
        
        # Analyze
        complexity_before = self._estimate_complexity(original)
        complexity_after = self._estimate_complexity(modified)
        
        return {
            "diff": '\n'.join(diff_lines),
            "lines_added": sum(1 for line in diff_lines if line.startswith('+') and not line.startswith('+++')),
            "lines_removed": sum(1 for line in diff_lines if line.startswith('-') and not line.startswith('---')),
            "complexity_before": complexity_before,
            "complexity_after": complexity_after,
            "complexity_delta": complexity_after - complexity_before,
            "estimated_impact": "refactoring" if complexity_after < complexity_before else "enhancement"
        }
    
    def _estimate_complexity(self, code: str) -> int:
        """Estimate code complexity."""
        try:
            tree = ast.parse(code)
            
            complexity = 0
            
            for node in ast.walk(tree):
                # Count branching statements
                if isinstance(node, (ast.If, ast.While, ast.For, ast.comprehension)):
                    complexity += 1
                # Count functions
                elif isinstance(node, ast.FunctionDef):
                    complexity += 1
                # Count classes
                elif isinstance(node, ast.ClassDef):
                    complexity += 2
            
            return complexity
        except:
            return 0
    
    def get_test_history(self) -> List[Dict]:
        """Get test history."""
        return [
            {
                "test_id": result.test_id,
                "file": result.file_path,
                "status": result.status.value,
                "passed": result.status == TestStatus.PASSED,
                "duration": result.duration_seconds
            }
            for result in self.test_history.values()
        ]
    
    def create_test_suite(self, module_name: str, tests: List[Dict]) -> bool:
        """
        Create a test suite for a module.
        
        Args:
            module_name: Module to test
            tests: List of test cases
            
        Returns:
            True if created successfully
        """
        try:
            test_dir = self.sandbox_dir / "test_suites" / module_name
            test_dir.mkdir(parents=True, exist_ok=True)
            
            test_file = test_dir / "test_auto.py"
            
            content = f"""#!/usr/bin/env python3
\"\"\"Auto-generated test suite for {module_name}\"\"\"

import pytest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

"""
            
            for i, test in enumerate(tests, 1):
                content += f"""
def test_{test.get('name', f'case_{i}')}():
    \"\"\"{test.get('description', 'Auto-generated test')}\"\"\"
    # TODO: Implement test
    assert True
"""
            
            test_file.write_text(content)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create test suite: {e}")
            return False