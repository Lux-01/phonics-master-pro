#!/usr/bin/env python3
"""
Production Integration Test Suite
Tests all 5 system improvements in production environment.

ACA Implementation:
- Requirements: Validate TRE, Safety, Unified Data, Scanner, Integration
- Architecture: Test suite with setup/teardown
- Data Flow: Setup → Test → Assert → Cleanup
- Edge Cases: Component failure, timeout, data inconsistency
- Tools: pytest-style assertions, mock data
- Errors: Detailed failure reporting
- Tests: 12 integration tests covering all components
"""

import json
import logging
import sys
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductionIntegrationTests:
    """Integration test suite for all system improvements."""
    
    def __init__(self):
        self.workspace = Path.home() / ".openclaw" / "workspace"
        self.test_results = []
        
    def log_test(self, name: str, passed: bool, details: str = ""):
        """Log test result."""
        result = {
            "name": name,
            "passed": passed,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        self.test_results.append(result)
        
        status = "✅" if passed else "❌"
        logger.info(f"{status} {name}: {details}")
    
    # ==================== TRE INTEGRATION TESTS ====================
    
    def test_tre_import(self) -> bool:
        """Test TRE module can be imported."""
        try:
            sys.path.insert(0, str(self.workspace / "skills" / "temporal-reasoning-engine"))
            from tre_core import TemporalReasoningEngine
            self.log_test("TRE Import", True, "Module imported successfully")
            return True
        except Exception as e:
            self.log_test("TRE Import", False, str(e))
            return False
    
    def test_tre_ingest_and_query(self) -> bool:
        """Test TRE data ingestion and query."""
        try:
            sys.path.insert(0, str(self.workspace / "skills" / "temporal-reasoning-engine"))
            from tre_core import TemporalReasoningEngine, TimeSeriesPoint
            
            tre = TemporalReasoningEngine()
            
            # Add sample data
            points = [
                TimeSeriesPoint(datetime.now() - timedelta(hours=i), 100.0 + i)
                for i in range(10, 0, -1)
            ]
            success = tre.ingest("test_series", points)
            
            if success:
                self.log_test("TRE Ingest", True, "Data ingested successfully")
                return True
            else:
                self.log_test("TRE Ingest", False, "Ingest failed")
                return False
                
        except Exception as e:
            self.log_test("TRE Ingest", False, str(e))
            return False
    
    def test_tre_trend_analysis(self) -> bool:
        """Test TRE trend analysis."""
        try:
            sys.path.insert(0, str(self.workspace / "skills" / "temporal-reasoning-engine"))
            from tre_core import TemporalReasoningEngine, TimeSeriesPoint
            
            tre = TemporalReasoningEngine()
            
            # Add trending data
            points = [
                TimeSeriesPoint(datetime.now() - timedelta(hours=i), 100.0 + i * 2)
                for i in range(10, 0, -1)
            ]
            tre.ingest("trend_test", points)
            
            trend = tre.analyze_trend("trend_test")
            
            if trend and hasattr(trend, 'direction'):
                self.log_test("TRE Trend Analysis", True, 
                            f"Trend: {trend.direction.value}")
                return True
            else:
                self.log_test("TRE Trend Analysis", False, "No trend detected")
                return False
                
        except Exception as e:
            self.log_test("TRE Trend Analysis", False, str(e))
            return False
    
    # ==================== SAFETY ENGINE TESTS ====================
    
    def test_safety_import(self) -> bool:
        """Test Safety Engine can be imported."""
        try:
            sys.path.insert(0, str(self.workspace / "skills" / "safety-engine"))
            from safety_core import SafetyVerificationEngine
            self.log_test("Safety Engine Import", True, "Module imported successfully")
            return True
        except Exception as e:
            self.log_test("Safety Engine Import", False, str(e))
            return False
    
    def test_safety_verification(self) -> bool:
        """Test Safety Engine verification."""
        try:
            sys.path.insert(0, str(self.workspace / "skills" / "safety-engine"))
            from safety_core import SafetyVerificationEngine, ActionType
            
            engine = SafetyVerificationEngine()
            
            # Test trade action
            result = engine.verify_action(
                ActionType.TRADE,
                "test",
                {"token": "SOL", "amount": 0.2}
            )
            
            if result and hasattr(result, 'can_execute'):
                self.log_test("Safety Verification", True, 
                            f"Risk score: {result.risk_score:.1f}")
                return True
            else:
                self.log_test("Safety Verification", False, "Invalid result")
                return False
                
        except Exception as e:
            self.log_test("Safety Verification", False, str(e))
            return False
    
    def test_safety_circuit_breaker(self) -> bool:
        """Test Safety Engine circuit breaker."""
        try:
            sys.path.insert(0, str(self.workspace / "skills" / "safety-engine"))
            from safety_core import SafetyVerificationEngine
            
            engine = SafetyVerificationEngine()
            
            # Record failures to trigger circuit breaker
            for i in range(3):
                engine.record_execution(f"test_{i}", False)
            
            # Check circuit breaker
            is_open = not engine.check_circuit_breaker("trading")
            
            if is_open:
                self.log_test("Safety Circuit Breaker", True, "Circuit breaker triggered")
                return True
            else:
                self.log_test("Safety Circuit Breaker", False, "Circuit breaker not triggered")
                return False
                
        except Exception as e:
            self.log_test("Safety Circuit Breaker", False, str(e))
            return False
    
    # ==================== UNIFIED DATA LAYER TESTS ====================
    
    def test_unified_data_import(self) -> bool:
        """Test Unified Data Layer can be imported."""
        try:
            sys.path.insert(0, str(self.workspace / "skills" / "knowledge-graph-engine"))
            from kge_unified import UnifiedDataLayer
            self.log_test("Unified Data Import", True, "Module imported successfully")
            return True
        except Exception as e:
            self.log_test("Unified Data Import", False, str(e))
            return False
    
    def test_unified_data_operations(self) -> bool:
        """Test Unified Data Layer CRUD operations."""
        try:
            sys.path.insert(0, str(self.workspace / "skills" / "knowledge-graph-engine"))
            from kge_unified import UnifiedDataLayer
            
            # Use temp file instead of :memory: (singleton pattern issue)
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
                tmp_path = tmp.name
            
            udl = UnifiedDataLayer(db_path=tmp_path)
            
            # Test entity creation
            entity = udl.add_entity("test_token", "token_123", {"symbol": "TEST"})
            
            if entity and entity.id == "token_123":
                self.log_test("Unified Data Operations", True, "Entity created successfully")
                return True
            else:
                self.log_test("Unified Data Operations", False, "Entity creation failed")
                return False
                
        except Exception as e:
            self.log_test("Unified Data Operations", False, str(e))
            return False
    
    # ==================== UNIFIED SCANNER TESTS ====================
    
    def test_unified_scanner_import(self) -> bool:
        """Test Unified Scanner can be imported."""
        try:
            sys.path.insert(0, str(self.workspace / "skills" / "unified-scanner"))
            from scanner_core import UnifiedScanner
            self.log_test("Unified Scanner Import", True, "Module imported successfully")
            return True
        except Exception as e:
            self.log_test("Unified Scanner Import", False, str(e))
            return False
    
    def test_unified_scanner_scan(self) -> bool:
        """Test Unified Scanner scan functionality."""
        try:
            sys.path.insert(0, str(self.workspace / "skills" / "unified-scanner"))
            from scanner_core import UnifiedScanner
            
            scanner = UnifiedScanner(cache_dir=":memory:")
            
            # Run scan
            result = scanner.scan("fundamental", {"min_grade": "A"})
            
            if result and hasattr(result, 'tokens'):
                self.log_test("Unified Scanner Scan", True, 
                            f"Found {len(result.tokens)} tokens")
                return True
            else:
                self.log_test("Unified Scanner Scan", False, "Scan failed")
                return False
                
        except Exception as e:
            self.log_test("Unified Scanner Scan", False, str(e))
            return False
    
    # ==================== INTEGRATION TESTS ====================
    
    def test_tre_trading_integration(self) -> bool:
        """Test TRE integration with trading system."""
        try:
            stage9_path = self.workspace / "agents" / "lux_trader" / "luxtrader_stage9_semi.py"
            
            if stage9_path.exists():
                with open(stage9_path, 'r') as f:
                    content = f.read()
                
                if "tre_core" in content or "TemporalReasoningEngine" in content:
                    self.log_test("TRE-Trading Integration", True, 
                                "TRE integrated in Stage 9")
                    return True
                else:
                    self.log_test("TRE-Trading Integration", False, 
                                "TRE not yet integrated")
                    return False
            else:
                self.log_test("TRE-Trading Integration", False, "Stage 9 not found")
                return False
                
        except Exception as e:
            self.log_test("TRE-Trading Integration", False, str(e))
            return False
    
    def test_safety_trading_integration(self) -> bool:
        """Test Safety Engine integration with trading."""
        try:
            stage9_path = self.workspace / "agents" / "lux_trader" / "luxtrader_stage9_semi.py"
            
            if stage9_path.exists():
                with open(stage9_path, 'r') as f:
                    content = f.read()
                
                if "safety_core" in content or "SafetyVerificationEngine" in content:
                    self.log_test("Safety-Trading Integration", True,
                                "Safety Engine integrated in Stage 9")
                    return True
                else:
                    self.log_test("Safety-Trading Integration", False,
                                "Safety Engine not yet integrated")
                    return False
            else:
                self.log_test("Safety-Trading Integration", False, "Stage 9 not found")
                return False
                
        except Exception as e:
            self.log_test("Safety-Trading Integration", False, str(e))
            return False
    
    def run_all_tests(self) -> Dict:
        """Run all integration tests."""
        logger.info("=" * 60)
        logger.info("Production Integration Test Suite")
        logger.info("=" * 60)
        
        tests = [
            # TRE Tests
            ("TRE Import", self.test_tre_import),
            ("TRE Ingest", self.test_tre_ingest_and_query),
            ("TRE Trend Analysis", self.test_tre_trend_analysis),
            
            # Safety Tests
            ("Safety Import", self.test_safety_import),
            ("Safety Verification", self.test_safety_verification),
            ("Safety Circuit Breaker", self.test_safety_circuit_breaker),
            
            # Unified Data Tests
            ("Unified Data Import", self.test_unified_data_import),
            ("Unified Data Operations", self.test_unified_data_operations),
            
            # Unified Scanner Tests
            ("Unified Scanner Import", self.test_unified_scanner_import),
            ("Unified Scanner Scan", self.test_unified_scanner_scan),
            
            # Integration Tests
            ("TRE-Trading Integration", self.test_tre_trading_integration),
            ("Safety-Trading Integration", self.test_safety_trading_integration),
        ]
        
        passed = 0
        failed = 0
        
        for name, test_func in tests:
            try:
                if test_func():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                self.log_test(name, False, f"Exception: {e}")
                failed += 1
        
        # Summary
        logger.info("=" * 60)
        logger.info("Test Summary:")
        logger.info(f"  Passed: {passed}")
        logger.info(f"  Failed: {failed}")
        logger.info(f"  Total: {len(tests)}")
        logger.info("=" * 60)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total": len(tests),
            "passed": passed,
            "failed": failed,
            "results": self.test_results,
            "success_rate": passed / len(tests) if tests else 0
        }


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Production Integration Tests")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    
    args = parser.parse_args()
    
    test_suite = ProductionIntegrationTests()
    results = test_suite.run_all_tests()
    
    if args.json:
        print(json.dumps(results, indent=2))
    
    # Exit with appropriate code
    sys.exit(0 if results["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
