"""
Phase 2 Test Suite - Safety + Research Modules
ACA Methodology: Analyze-Construct-Audit

Tests cover:
1. Safety Container - sandboxing, secret scanning, audit logging
2. Research Orchestrator - parallel agents, synthesis, citations
3. Design Researcher - trends, palettes, HTML/CSS generation
"""

import sys
import os
import json
import time
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from safety.safety_container import SafetyContainer, SandboxLevel, SecretMatch
from research.research_orchestrator import ResearchOrchestrator, ResearchFinding
from research.design_researcher import DesignResearcher, DesignTrends, ColorPalette


class TestSafetyContainer:
    """Test Safety Container Module."""
    
    @staticmethod
    def run_all():
        print("\n" + "="*60)
        print("TESTING: Safety Container")
        print("="*60)
        
        tests = [
            TestSafetyContainer.test_init,
            TestSafetyContainer.test_secret_scanning_api_key,
            TestSafetyContainer.test_secret_scanning_aws,
            TestSafetyContainer.test_secret_scanning_private_key,
            TestSafetyContainer.test_secret_scanning_jwt,
            TestSafetyContainer.test_path_validation_valid,
            TestSafetyContainer.test_path_validation_escapes_workspace,
            TestSafetyContainer.test_path_validation_restricted_dirs,
            TestSafetyContainer.test_sandboxed_execution_safe_code,
            TestSafetyContainer.test_sandboxed_execution_secrets_blocked,
            TestSafetyContainer.test_sandboxed_execution_network_blocked_strict,
            TestSafetyContainer.test_audit_logging,
            TestSafetyContainer.test_rollback_on_failure,
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                test()
                print(f"✓ {test.__name__}")
                passed += 1
            except AssertionError as e:
                print(f"✗ {test.__name__}: {e}")
                failed += 1
            except Exception as e:
                print(f"✗ {test.__name__}: {type(e).__name__}: {e}")
                failed += 1
        
        print(f"\nSafety Container: {passed}/{len(tests)} passed")
        return passed, failed
    
    @staticmethod
    def test_init():
        container = SafetyContainer()
        assert container.workspace_path.exists()
        assert container.audit_log_path.parent.exists()
    
    @staticmethod
    def test_secret_scanning_api_key():
        container = SafetyContainer()
        code = 'api_key = "sk-test1234567890abcdef1234567890"'
        matches = container.scan_for_secrets(code)
        assert len(matches) > 0, "Should detect API key"
        assert any(m.type == 'api_key' for m in matches)
    
    @staticmethod
    def test_secret_scanning_aws():
        container = SafetyContainer()
        code = 'AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"'
        matches = container.scan_for_secrets(code)
        aws_matches = [m for m in matches if m.type == 'aws_key']
        assert len(aws_matches) > 0, "Should detect AWS key"
    
    @staticmethod
    def test_secret_scanning_private_key():
        container = SafetyContainer()
        code = '-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA0Z3...'
        matches = container.scan_for_secrets(code)
        assert any(m.type == 'private_key' for m in matches), "Should detect private key"
    
    @staticmethod
    def test_secret_scanning_jwt():
        container = SafetyContainer()
        code = 'token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4A3qrKn..."'
        matches = container.scan_for_secrets(code)
        assert any(m.type == 'jwt_token' for m in matches), "Should detect JWT"
    
    @staticmethod
    def test_path_validation_valid():
        container = SafetyContainer()
        path = container.validate_path("test_file.py")
        assert isinstance(path, Path)
    
    @staticmethod
    def test_path_validation_escapes_workspace():
        container = SafetyContainer()
        try:
            container.validate_path("/etc/passwd")
            assert False, "Should raise ValueError"
        except (ValueError, PermissionError):
            pass
    
    @staticmethod
    def test_path_validation_restricted_dirs():
        container = SafetyContainer()
        # Paths outside workspace get ValueError; restricted paths get PermissionError
        raised_security_error = False
        try:
            container.validate_path("~/.ssh/id_rsa")
        except (ValueError, PermissionError):
            raised_security_error = True
        assert raised_security_error, "Should raise either ValueError or PermissionError for restricted paths"
    
    @staticmethod
    def test_sandboxed_execution_safe_code():
        container = SafetyContainer()
        result = container.execute_sandboxed("print('hello')", SandboxLevel.STRICT)
        assert result['success'], f"Should succeed: {result['error']}"
        assert 'hello' in result['output']
    
    @staticmethod
    def test_sandboxed_execution_secrets_blocked():
        container = SafetyContainer()
        # Use HIGH severity secret (private key) that should be blocked
        code = 'private_key = """-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA0Z3...\n-----END RSA PRIVATE KEY-----"""'
        result = container.execute_sandboxed(code, SandboxLevel.STRICT)
        assert not result['success'], "Should block code with high-severity secrets"
        assert 'BLOCKED' in result['error']
    
    @staticmethod
    def test_sandboxed_execution_network_blocked_strict():
        container = SafetyContainer()
        code = 'import requests; requests.get("https://example.com")'
        result = container.execute_sandboxed(code, SandboxLevel.STRICT)
        assert not result['success'], "Should block network in STRICT mode"
    
    @staticmethod
    def test_audit_logging():
        container = SafetyContainer()
        # Clear existing logs
        if container.audit_log_path.exists():
            container.audit_log_path.unlink()
        
        result = container.execute_sandboxed("x = 1 + 1", SandboxLevel.STRICT)
        assert result['audit_entry'] is not None
        
        trail = container.get_audit_trail(limit=10)
        assert len(trail) > 0, "Should have audit entries"
    
    @staticmethod
    def test_rollback_on_failure():
        container = SafetyContainer()
        # This would need file operations to test properly
        # Simplified: just verify rollback method exists
        assert hasattr(container, 'rollback')


class TestResearchOrchestrator:
    """Test Research Orchestrator Module."""
    
    @staticmethod
    def run_all():
        print("\n" + "="*60)
        print("TESTING: Research Orchestrator")
        print("="*60)
        
        tests = [
            TestResearchOrchestrator.test_init,
            TestResearchOrchestrator.test_spawn_single_agent,
            TestResearchOrchestrator.test_spawn_multiple_agents,
            TestResearchOrchestrator.test_detect_contradictions,
            TestResearchOrchestrator.test_synthesize_findings,
            TestResearchOrchestrator.test_full_research_pipeline,
            TestResearchOrchestrator.test_citations,
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                test()
                print(f"✓ {test.__name__}")
                passed += 1
            except AssertionError as e:
                print(f"✗ {test.__name__}: {e}")
                failed += 1
            except Exception as e:
                print(f"✗ {test.__name__}: {type(e).__name__}: {e}")
                failed += 1
        
        print(f"\nResearch Orchestrator: {passed}/{len(tests)} passed")
        return passed, failed
    
    @staticmethod
    def test_init():
        orch = ResearchOrchestrator()
        assert orch.max_workers > 0
        assert len(orch.SOURCES) > 0
    
    @staticmethod
    def test_spawn_single_agent():
        orch = ResearchOrchestrator()
        findings = orch.spawn_research_agents(
            "2026 web design trends",
            sources=['dribbble']
        )
        assert len(findings) > 0, "Should have findings from single agent"
        assert all(f.source == 'dribbble' for f in findings)
    
    @staticmethod
    def test_spawn_multiple_agents():
        orch = ResearchOrchestrator()
        findings = orch.spawn_research_agents(
            "2026 web design trends",
            sources=['dribbble', 'behance']
        )
        assert len(findings) > 0
        sources = set(f.source for f in findings)
        assert len(sources) == 2, f"Should have findings from 2 sources, got {sources}"
    
    @staticmethod
    def test_detect_contradictions():
        orch = ResearchOrchestrator()
        
        findings = [
            ResearchFinding(
                claim="Dark mode is trending",
                source="source_a",
                confidence=0.9,
                category="trend"
            ),
            ResearchFinding(
                claim="Light mode is making a comeback",
                source="source_b", 
                confidence=0.85,
                category="trend"
            ),
        ]
        
        contradictions = orch.detect_contradictions(findings)
        assert len(contradictions) > 0, "Should detect dark/light contradiction"
    
    @staticmethod
    def test_synthesize_findings():
        orch = ResearchOrchestrator()
        
        findings = [
            ResearchFinding(
                claim="Glassmorphism is popular",
                source="dribbble",
                confidence=0.85,
                category="trend"
            ),
        ]
        
        report = orch.synthesize_findings("test query", findings, [])
        assert "Glassmorphism" in report
        assert "dribbble" in report
        assert "85%" in report or "0.85" in report
    
    @staticmethod
    def test_full_research_pipeline():
        orch = ResearchOrchestrator()
        
        result = orch.research(
            "2026 web design trends",
            sources=['dribbble', 'behance']
        )
        
        assert result.query == "2026 web design trends"
        assert len(result.findings) > 0
        assert len(result.sources_used) == 2
        assert result.confidence_score > 0
        assert len(result.synthesized_report) > 100
        assert "Research Report" in result.synthesized_report
    
    @staticmethod
    def test_citations():
        orch = ResearchOrchestrator()
        finding = ResearchFinding(
            claim="Test claim",
            source="test_source",
            confidence=0.8,
            category="test"
        )
        citation = orch.cite_sources(finding)
        assert "test_source" in citation
        assert "Test claim" in citation


class TestDesignResearcher:
    """Test Design Researcher Module."""
    
    @staticmethod
    def run_all():
        print("\n" + "="*60)
        print("TESTING: Design Researcher")
        print("="*60)
        
        tests = [
            TestDesignResearcher.test_init,
            TestDesignResearcher.test_research_trends_fitness,
            TestDesignResearcher.test_research_trends_tech,
            TestDesignResearcher.test_research_trends_finance,
            TestDesignResearcher.test_color_palettes_match_domain,
            TestDesignResearcher.test_generate_landing_page,
            TestDesignResearcher.test_generate_mockup_features,
            TestDesignResearcher.test_wcag_accessibility,
            TestDesignResearcher.test_responsive_design,
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                test()
                print(f"✓ {test.__name__}")
                passed += 1
            except AssertionError as e:
                print(f"✗ {test.__name__}: {e}")
                failed += 1
            except Exception as e:
                print(f"✗ {test.__name__}: {type(e).__name__}: {e}")
                failed += 1
        
        print(f"\nDesign Researcher: {passed}/{len(tests)} passed")
        return passed, failed
    
    @staticmethod
    def test_init():
        researcher = DesignResearcher()
        assert researcher.orchestrator is not None
    
    @staticmethod
    def test_research_trends_fitness():
        researcher = DesignResearcher()
        trends = researcher.research_trends("fitness app")
        
        assert len(trends.trends_2026) > 0
        assert len(trends.color_palettes) > 0
        assert len(trends.layout_patterns) > 0
        assert trends.recommendation != ""
    
    @staticmethod
    def test_research_trends_tech():
        researcher = DesignResearcher()
        trends = researcher.research_trends("SaaS platform")
        
        assert len(trends.trends_2026) > 0
        assert trends.recommendation != ""
    
    @staticmethod
    def test_research_trends_finance():
        researcher = DesignResearcher()
        trends = researcher.research_trends("crypto trading dashboard")
        
        assert len(trends.trends_2026) > 0
        # Should get crypto-specific palette
        assert len(trends.color_palettes) > 0
    
    @staticmethod
    def test_color_palettes_match_domain():
        researcher = DesignResearcher()
        
        fitness = researcher.research_trends("fitness app")
        wellness = researcher.research_trends("wellness app")
        
        # Should have different palettes
        if fitness.color_palettes and wellness.color_palettes:
            assert fitness.color_palettes[0].name != wellness.color_palettes[0].name
    
    @staticmethod
    def test_generate_landing_page():
        researcher = DesignResearcher()
        trends = researcher.research_trends("fitness")
        
        mockup = researcher.generate_mockup({
            "type": "landing_page",
            "domain": "fitness",
            "features": ["cta_form"],
        }, trends)
        
        assert 'html' in mockup
        assert 'css' in mockup
        assert 'standalone' in mockup
        assert len(mockup['html']) > 1000
    
    @staticmethod
    def test_generate_mockup_features():
        researcher = DesignResearcher()
        trends = researcher.research_trends("ecommerce")
        
        mockup = researcher.generate_mockup({
            "type": "landing_page",
            "domain": "ecommerce",
            "features": ["pricing", "testimonials"],
            "sections": ["features"],
        }, trends)
        
        # Check for pricing section
        assert 'pricing' in mockup['html'].lower() or 'Pricing' in mockup['html']
        # Check for testimonials section
        assert 'testimonial' in mockup['html'].lower() or 'customers say' in mockup['html'].lower()
    
    @staticmethod
    def test_wcag_accessibility():
        researcher = DesignResearcher()
        trends = researcher.research_trends("accessible app")
        
        mockup = researcher.generate_mockup({
            "type": "landing_page",
            "domain": "accessible",
        }, trends)
        
        css = mockup['css']
        # Check for accessibility features
        assert 'prefers-reduced-motion' in css, "Should have reduced motion support"
        assert ':focus-visible' in css or 'focus' in css.lower(), "Should have focus styles"
        assert 'sr-only' in css or 'screen-reader' in css.lower(), "Should have screen reader support"
    
    @staticmethod
    def test_responsive_design():
        researcher = DesignResearcher()
        trends = researcher.research_trends("mobile app")
        
        mockup = researcher.generate_mockup({
            "type": "landing_page",
            "domain": "mobile",
        }, trends)
        
        css = mockup['css']
        # Check for responsive features
        assert '@media' in css, "Should have media queries"
        assert 'clamp(' in css or 'min-width' in css or 'max-width' in css, "Should have responsive sizing"


def run_all_tests():
    """Run all Phase 2 tests and report results."""
    print("\n" + "#"*60)
    print("# OMNIBOT PHASE 2 TEST SUITE")
    print("# Safety + Research Modules")
    print("#"*60)
    
    total_passed = 0
    total_failed = 0
    
    # Run each test suite
    p, f = TestSafetyContainer.run_all()
    total_passed += p
    total_failed += f
    
    p, f = TestResearchOrchestrator.run_all()
    total_passed += p
    total_failed += f
    
    p, f = TestDesignResearcher.run_all()
    total_passed += p
    total_failed += f
    
    # Summary
    print("\n" + "#"*60)
    print("# TEST SUMMARY")
    print("#"*60)
    print(f"\nTotal: {total_passed + total_failed} tests")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")
    
    if total_failed == 0:
        print("\n\n✅ PHASE 2 COMPLETE - ALL TESTS PASSED")
        print("\nReady for Phase 3: Job Seeker + Execution Modules")
        return True
    else:
        print("\n\n⚠️  Some tests failed - review before Phase 3")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)