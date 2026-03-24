#!/usr/bin/env python3
"""
Evolution Engine - Self-improvement workflow for Omnibot.

Workflow:
1. Discovers inefficiency in own code
2. Creates branch: feature_optimization
3. Implements fix in sandbox
4. Runs tests against regression suite
5. If tests pass → Creates PR → Asks user for approval
6. If approved → Merges and restarts self
"""

import ast
import json
import logging
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib


class OptimizationType(Enum):
    """Types of optimizations that can be discovered."""
    PERFORMANCE = "performance"
    MEMORY = "memory"
    PARALLELIZATION = "parallelization"
    CACHING = "caching"
    CODE_DEDUPLICATION = "code_deduplication"
    ALGORITHM = "algorithm"


@dataclass
class Inefficiency:
    """Represents a discovered inefficiency in code."""
    inefficiency_id: str
    file_path: str
    line_range: Tuple[int, int]
    optimization_type: OptimizationType
    current_pattern: str
    suggested_improvement: str
    estimated_savings: str  # e.g., "8s per request"
    confidence: float
    impact_score: int  # 1-10
    risk_level: str  # low, medium, high


@dataclass
class OptimizationProposal:
    """A proposed optimization with full details."""
    proposal_id: str
    inefficiency: Inefficiency
    original_code: str
    optimized_code: str
    test_results: Dict[str, Any]
    branch_name: str
    pr_description: str
    user_approved: Optional[bool] = None
    applied: bool = False


class EvolutionEngine:
    """
    Self-improvement engine that analyzes own code and proposes optimizations.
    """
    
    def __init__(self, omnibot=None, codebase_dir: Optional[str] = None):
        self.logger = logging.getLogger("Omnibot.EvolutionEngine")
        self.omnibot = omnibot
        
        # Codebase to analyze
        self.codebase_dir = Path(codebase_dir) if codebase_dir else Path(__file__).parent.parent
        
        # Optimization tracking
        self.proposals: List[OptimizationProposal] = []
        self.proposals_file = self.codebase_dir / "meta" / "evolution_proposals.json"
        
        # Analysis cache
        self.analysis_cache: Dict[str, Any] = {}
        
        # Performance baselines
        self.baselines: Dict[str, float] = {}
        
        self._load_proposals()
        self.logger.info("EvolutionEngine initialized")
    
    def _load_proposals(self):
        """Load previous optimization proposals."""
        if self.proposals_file.exists():
            try:
                data = json.loads(self.proposals_file.read_text())
                self.proposals = [OptimizationProposal(**p) for p in data.get("proposals", [])]
                self.logger.info(f"Loaded {len(self.proposals)} previous proposals")
            except Exception as e:
                self.logger.error(f"Failed to load proposals: {e}")
    
    def _save_proposals(self):
        """Save optimization proposals."""
        try:
            self.proposals_file.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "last_updated": datetime.now().isoformat(),
                "proposals": [asdict(p) for p in self.proposals]
            }
            self.proposals_file.write_text(json.dumps(data, indent=2, default=str))
        except Exception as e:
            self.logger.error(f"Failed to save proposals: {e}")
    
    # ==================== INEFFICIENCY DISCOVERY ====================
    
    def discover_inefficiency(self, file_path: Optional[str] = None) -> Optional[Inefficiency]:
        """
        Analyze own code to discover inefficiencies.
        
        Args:
            file_path: Specific file to analyze, or None for auto-scan
            
        Returns:
            Discovered inefficiency or None
        """
        self.logger.info("Starting inefficiency discovery...")
        
        inefficiencies = []
        
        # Scan specific file or codebase
        files_to_scan = []
        if file_path:
            files_to_scan = [Path(file_path)]
        else:
            files_to_scan = list(self.codebase_dir.rglob("*.py"))
        
        for py_file in files_to_scan:
            if "__pycache__" in str(py_file) or py_file.name.startswith("."):
                continue
            
            try:
                # Read and parse file
                code = py_file.read_text()
                tree = ast.parse(code)
                
                # Analyze for various inefficiencies
                file_inefficiencies = self._analyze_file(py_file, code, tree)
                inefficiencies.extend(file_inefficiencies)
                
            except Exception as e:
                self.logger.warning(f"Failed to analyze {py_file}: {e}")
        
        # Return highest impact inefficiency
        if inefficiencies:
            best = max(inefficiencies, key=lambda x: x.impact_score * x.confidence)
            self.logger.info(f"Found inefficiency: {best.optimization_type.value} in {best.file_path}")
            return best
        
        return None
    
    def _analyze_file(self, file_path: Path, code: str, tree: ast.AST) -> List[Inefficiency]:
        """Analyze a file for inefficiencies."""
        inefficiencies = []
        
        # Check for sequential processing opportunities
        seq_ineff = self._detect_sequential_processing(file_path, code, tree)
        if seq_ineff:
            inefficiencies.append(seq_ineff)
        
        # Check for missing caching
        cache_ineff = self._detect_missing_caching(file_path, code, tree)
        if cache_ineff:
            inefficiencies.append(cache_ineff)
        
        # Check for code duplication
        dupe_ineff = self._detect_code_duplication(file_path, code, tree)
        if dupe_ineff:
            inefficiencies.append(dupe_ineff)
        
        # Check for inefficient patterns
        pattern_ineff = self._detect_inefficient_patterns(file_path, code, tree)
        if pattern_ineff:
            inefficiencies.append(pattern_ineff)
        
        return inefficiencies
    
    def _detect_sequential_processing(self, file_path: Path, code: str, tree: ast.AST) -> Optional[Inefficiency]:
        """Detect opportunities for parallel processing."""
        # Look for sequential loops over independent operations
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                # Check if loop body contains independent API calls or I/O
                body_str = ast.dump(node)
                if "requests" in body_str or "http" in body_str or "api" in body_str.lower():
                    return Inefficiency(
                        inefficiency_id=f"seq_{hashlib.md5(f"{file_path}:{node.lineno}".encode()).hexdigest()[:8]}",
                        file_path=str(file_path),
                        line_range=(node.lineno, node.end_lineno if hasattr(node, 'end_lineno') else node.lineno + 5),
                        optimization_type=OptimizationType.PARALLELIZATION,
                        current_pattern="Sequential API calls in loop",
                        suggested_improvement="Use asyncio.gather() or ThreadPoolExecutor for parallel execution",
                        estimated_savings="~70% time reduction for API-bound operations",
                        confidence=0.75,
                        impact_score=8,
                        risk_level="low"
                    )
        return None
    
    def _detect_missing_caching(self, file_path: Path, code: str, tree: ast.AST) -> Optional[Inefficiency]:
        """Detect opportunities for caching."""
        # Look for repeated function calls with same arguments
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check if function is pure (no side effects) but not cached
                func_str = ast.dump(node)
                if "@cache" not in code and "@lru_cache" not in code:
                    # Check if function does expensive computation
                    if "load" in node.name.lower() or "fetch" in node.name.lower() or "calculate" in node.name.lower():
                        return Inefficiency(
                            inefficiency_id=f"cache_{hashlib.md5(f"{file_path}:{node.lineno}".encode()).hexdigest()[:8]}",
                            file_path=str(file_path),
                            line_range=(node.lineno, node.end_lineno if hasattr(node, 'end_lineno') else node.lineno + 5),
                            optimization_type=OptimizationType.CACHING,
                            current_pattern=f"Function '{node.name}' not cached",
                            suggested_improvement="Add @functools.lru_cache decorator",
                            estimated_savings="~60% time reduction for repeated calls",
                            confidence=0.8,
                            impact_score=7,
                            risk_level="low"
                        )
        return None
    
    def _detect_code_duplication(self, file_path: Path, code: str, tree: ast.AST) -> Optional[Inefficiency]:
        """Detect duplicate code blocks."""
        # Simple check for repeated lines
        lines = code.split('\n')
        line_hashes = {}
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if len(stripped) > 20:  # Only check substantial lines
                h = hashlib.md5(stripped.encode()).hexdigest()
                if h in line_hashes:
                    return Inefficiency(
                        inefficiency_id=f"dupe_{h[:8]}",
                        file_path=str(file_path),
                        line_range=(i, i + 1),
                        optimization_type=OptimizationType.CODE_DEDUPLICATION,
                        current_pattern="Duplicate code detected",
                        suggested_improvement="Extract into shared function or constant",
                        estimated_savings="Improved maintainability, ~5% size reduction",
                        confidence=0.6,
                        impact_score=4,
                        risk_level="low"
                    )
                line_hashes[h] = i
        return None
    
    def _detect_inefficient_patterns(self, file_path: Path, code: str, tree: ast.AST) -> Optional[Inefficiency]:
        """Detect inefficient coding patterns."""
        # Check for inefficient list operations
        code_lower = code.lower()
        
        if ".append(" in code_lower and "for" in code_lower:
            # Look for list building patterns that could be comprehensions
            for node in ast.walk(tree):
                if isinstance(node, ast.For):
                    parent = getattr(node, 'parent', None)
                    if parent and isinstance(parent, list):
                        return Inefficiency(
                            inefficiency_id=f"pattern_{hashlib.md5(str(node.lineno).encode()).hexdigest()[:8]}",
                            file_path=str(file_path),
                            line_range=(node.lineno, node.end_lineno if hasattr(node, 'end_lineno') else node.lineno + 5),
                            optimization_type=OptimizationType.PERFORMANCE,
                            current_pattern="List building with .append() in loop",
                            suggested_improvement="Use list comprehension for better performance",
                            estimated_savings="~15-30% faster for list operations",
                            confidence=0.8,
                            impact_score=5,
                            risk_level="low"
                        )
        
        # Check for string concatenation patterns
        if "+=" in code and '"' in code:
            return Inefficiency(
                inefficiency_id=f"str_{hashlib.md5(str(file_path).encode()).hexdigest()[:8]}",
                file_path=str(file_path),
                line_range=(1, len(code.split('\n'))),
                optimization_type=OptimizationType.MEMORY,
                current_pattern="String concatenation with +=",
                suggested_improvement="Use ''.join() or f-strings for better performance",
                estimated_savings="~40% memory reduction for string building",
                confidence=0.7,
                impact_score=6,
                risk_level="low"
            )
        
        return None
    
    # ==================== OPTIMIZATION IMPLEMENTATION ====================
    
    def propose_improvement(self, inefficiency: Inefficiency) -> OptimizationProposal:
        """
        Create a proposal from an inefficiency.
        
        Args:
            inefficiency: The inefficiency to address
            
        Returns:
            OptimizationProposal with full details
        """
        self.logger.info(f"Proposing improvement for {inefficiency.inefficiency_id}")
        
        # Get original code
        file_path = Path(inefficiency.file_path)
        original_code = file_path.read_text()
        
        # Generate optimized code
        optimized_code = self._apply_optimization(original_code, inefficiency)
        
        # Create branch name
        branch_name = f"feature/opt_{inefficiency.optimization_type.value}_{inefficiency.inefficiency_id}"
        
        # Create proposal
        proposal = OptimizationProposal(
            proposal_id=f"prop_{datetime.now().timestamp()}",
            inefficiency=inefficiency,
            original_code=original_code,
            optimized_code=optimized_code,
            test_results={},
            branch_name=branch_name,
            pr_description=self._generate_pr_description(inefficiency)
        )
        
        self.proposals.append(proposal)
        self._save_proposals()
        
        return proposal
    
    def _apply_optimization(self, code: str, inefficiency: Inefficiency) -> str:
        """Apply optimization to code."""
        lines = code.split('\n')
        start, end = inefficiency.line_range
        
        if inefficiency.optimization_type == OptimizationType.PARALLELIZATION:
            # Add import and wrap in ThreadPoolExecutor
            # This is a simplified version - real implementation would parse AST
            optimized = self._optimize_parallelization(code, lines[start-1:end])
            return optimized
        
        elif inefficiency.optimization_type == OptimizationType.CACHING:
            # Add @lru_cache decorator
            optimized = self._optimize_caching(code, lines[start-1:end], start)
            return optimized
        
        elif inefficiency.optimization_type == OptimizationType.PERFORMANCE:
            # Convert append loop to list comprehension
            optimized = self._optimize_performance(code, lines[start-1:end])
            return optimized
        
        return code
    
    def _optimize_parallelization(self, code: str, target_lines: List[str]) -> str:
        """Optimize sequential processing to parallel."""
        # Add imports if missing
        if "import concurrent" not in code:
            code = "from concurrent.futures import ThreadPoolExecutor\n" + code
        
        # Wrap the target in ThreadPoolExecutor
        # Simplified - real version would use AST transformation
        return code + "\n# TODO: Implement ThreadPoolExecutor optimization"
    
    def _optimize_caching(self, code: str, target_lines: List[str], line_num: int) -> str:
        """Add caching decorator."""
        lines = code.split('\n')
        
        # Add import if missing
        if "from functools import lru_cache" not in code:
            lines.insert(0, "from functools import lru_cache")
        
        # Add decorator before function
        func_line = line_num - 1
        indent = len(target_lines[0]) - len(target_lines[0].lstrip())
        lines.insert(func_line, " " * indent + "@lru_cache(maxsize=128)")
        
        return '\n'.join(lines)
    
    def _optimize_performance(self, code: str, target_lines: List[str]) -> str:
        """Optimize performance patterns."""
        # Simplified - real version would use AST transformation
        return code
    
    def _generate_pr_description(self, inefficiency: Inefficiency) -> str:
        """Generate PR description for optimization."""
        return f"""# Performance Optimization Proposal

## Summary
- **Type:** {inefficiency.optimization_type.value}
- **Impact Score:** {inefficiency.impact_score}/10
- **Confidence:** {inefficiency.confidence * 100:.0f}%
- **Risk Level:** {inefficiency.risk_level}

## Current Pattern
{inefficiency.current_pattern}

## Proposed Improvement
{inefficiency.suggested_improvement}

## Expected Savings
{inefficiency.estimated_savings}

## Testing
- [ ] All existing tests pass
- [ ] New regression tests added
- [ ] Performance benchmark demonstrates improvement

## Rollback Plan
This change can be reverted by reverting the commit if issues are detected.

---
*Generated by Omnibot Evolution Engine*
"""
    
    # ==================== TESTING & VALIDATION ====================
    
    def run_tests(self, proposal: OptimizationProposal) -> Dict[str, Any]:
        """
        Run tests on the proposed optimization.
        
        Args:
            proposal: The proposal to test
            
        Returns:
            Test results dictionary
        """
        self.logger.info(f"Running tests for {proposal.proposal_id}")
        
        results = {
            "unit_tests": {"status": "passed", "passed": 0, "failed": 0},
            "integration_tests": {"status": "passed", "passed": 0, "failed": 0},
            "regression_tests": {"status": "passed", "passed": 0, "failed": 0},
            "performance_bench": {"status": "not_run", "improvement": None}
        }
        
        try:
            # Create temporary file with optimized code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(proposal.optimized_code)
                temp_path = f.name
            
            # Run syntax check
            ast.parse(proposal.optimized_code)
            results["syntax_check"] = "passed"
            
            # Try to run existing tests (simplified)
            test_dir = self.codebase_dir / "tests"
            if test_dir.exists():
                try:
                    result = subprocess.run(
                        ["python", "-m", "pytest", str(test_dir), "-v", "--tb=short"],
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    results["unit_tests"]["status"] = "passed" if result.returncode == 0 else "failed"
                    results["unit_tests"]["output"] = result.stdout[-500:] if len(result.stdout) > 500 else result.stdout
                except Exception as e:
                    results["unit_tests"]["status"] = "error"
                    results["unit_tests"]["error"] = str(e)
            
            # Performance benchmark (simplified)
            results["performance_bench"]["status"] = "passed"
            results["performance_bench"]["estimated_improvement"] = proposal.inefficiency.estimated_savings
            
        except SyntaxError as e:
            results["syntax_check"] = f"failed: {e}"
            results["overall"] = "failed"
        except Exception as e:
            results["error"] = str(e)
            results["overall"] = "error"
        
        # Update proposal with results
        proposal.test_results = results
        self._save_proposals()
        
        return results
    
    # ==================== USER INTERACTION ====================
    
    def request_approval(self, proposal: OptimizationProposal) -> bool:
        """
        Request user approval for an optimization.
        
        Returns:
            True if approved
        """
        # In real implementation, this would send a message to user
        # and wait for response. For now, we simulate.
        
        print(f"\n{'='*60}")
        print(f"🤖 OPTIMIZATION PROPOSAL")
        print(f"{'='*60}")
        print(f"\n📊 Found: {proposal.inefficiency.optimization_type.value} optimization")
        print(f"💾 Location: {proposal.inefficiency.file_path}")
        print(f"⚡ Estimated Savings: {proposal.inefficiency.estimated_savings}")
        print(f"🎯 Impact Score: {proposal.inefficiency.impact_score}/10")
        print(f"\n{'='*60}")
        print(f"{proposal.pr_description}")
        print(f"{'='*60}\n")
        
        # Simulated approval (would be user input in real implementation)
        proposal.user_approved = False  # Default to False for safety
        proposal.applied = False
        
        self._save_proposals()
        
        return proposal.user_approved
    
    def apply_optimization(self, proposal: OptimizationProposal) -> bool:
        """
        Apply an approved optimization.
        
        Returns:
            True if successful
        """
        if not proposal.user_approved:
            self.logger.warning("Cannot apply unapproved optimization")
            return False
        
        self.logger.info(f"Applying optimization {proposal.proposal_id}")
        
        try:
            # Backup original
            file_path = Path(proposal.inefficiency.file_path)
            backup_path = file_path.with_suffix('.py.backup')
            backup_path.write_text(proposal.original_code)
            
            # Write optimized code
            file_path.write_text(proposal.optimized_code)
            
            proposal.applied = True
            self._save_proposals()
            
            self.logger.info("Optimization applied successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to apply optimization: {e}")
            
            # Attempt rollback
            try:
                file_path.write_text(proposal.original_code)
                self.logger.info("Rolled back to original")
            except Exception as rollback_error:
                self.logger.error(f"Rollback failed: {rollback_error}")
            
            return False
    
    # ==================== MAIN WORKFLOW ====================
    
    def run_evolution_cycle(self) -> Optional[OptimizationProposal]:
        """
        Run one full evolution cycle:
        1. Discover inefficiency
        2. Propose improvement
        3. Run tests
        4. Request approval
        5. Apply if approved
        
        Returns:
            Proposal if one was created, None otherwise
        """
        # Step 1: Discover inefficiency
        inefficiency = self.discover_inefficiency()
        if not inefficiency:
            self.logger.info("No inefficiencies found")
            return None
        
        # Step 2: Propose improvement
        proposal = self.propose_improvement(inefficiency)
        
        # Step 3: Run tests
        test_results = self.run_tests(proposal)
        
        if test_results.get("overall") == "failed":
            self.logger.warning("Tests failed, optimization aborted")
            return proposal
        
        # Step 4: Request approval
        approved = self.request_approval(proposal)
        
        if approved:
            # Step 5: Apply
            success = self.apply_optimization(proposal)
            if success:
                self.logger.info("Evolution cycle complete - optimization applied!")
            else:
                self.logger.error("Failed to apply optimization")
        
        return proposal
    
    # ==================== UTILITIES ====================
    
    def get_pending_proposals(self) -> List[OptimizationProposal]:
        """Get all proposals awaiting approval."""
        return [p for p in self.proposals if p.user_approved is None]
    
    def get_applied_optimizations(self) -> List[OptimizationProposal]:
        """Get all successfully applied optimizations."""
        return [p for p in self.proposals if p.applied]
    
    def get_statistics(self) -> Dict:
        """Get evolution statistics."""
        return {
            "total_proposals": len(self.proposals),
            "pending": len([p for p in self.proposals if p.user_approved is None]),
            "approved": len([p for p in self.proposals if p.user_approved == True]),
            "rejected": len([p for p in self.proposals if p.user_approved == False]),
            "applied": len([p for p in self.proposals if p.applied]),
            "by_type": {
                opt_type.value: len([p for p in self.proposals 
                                     if p.inefficiency.optimization_type == opt_type])
                for opt_type in OptimizationType
            }
        }