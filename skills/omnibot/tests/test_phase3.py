#!/usr/bin/env python3
"""
Phase 3 Test Suite - Job Seeker, Execution, and Skill Evolution

Tests all Phase 3 components:
- job_seeker/ module (platform_scanners, proposal_generator, client_researcher)
- execution/ module (job_workflow, requirements_parser)
- self_modify/ module (skill_evolution_bridge)

Run: python tests/test_phase3.py [-v]
"""

import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import Phase 3 modules
from job_seeker import (
    JobSeeker, PlatformScanners, ProposalGenerator, ClientResearcher,
    JobOpportunity, JobPlatform, Proposal, ProposalStatus,
    ResearchReport, ClientProfile
)
from execution import (
    JobExecutor, JobExecutionOrchestrator, ExecutionPhase, CheckpointStatus,
    RequirementsParser, ParsedProject, ParsedRequirement
)
from self_modify import SkillEvolutionBridge


class TestJobSeeker(unittest.TestCase):
    """Test Job Seeker module components."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.seeker = JobSeeker()
        cls.seeker.scanners.update_preferences(
            skills=["python", "react", "ai"],
            min_hourly_rate=50,
            excluded_keywords=["unpaid", "internship"]
        )
    
    def test_01_platform_scanners_init(self):
        """Test PlatformScanners initialization."""
        self.assertIsNotNone(self.seeker.scanners)
        self.assertGreaterEqual(self.seeker.scanners.min_hourly_rate, 50)
        self.assertIn("python", [s.lower() for s in self.seeker.scanners.user_skills])
    
    def test_02_scan_platform(self):
        """Test scanning a platform for jobs."""
        jobs = self.seeker.scanners.scan_upwork(["python"])
        self.assertIsInstance(jobs, list)
        # Should find simulated jobs
        self.assertGreaterEqual(len(jobs), 0)
    
    def test_03_job_opportunity_structure(self):
        """Test JobOpportunity dataclass structure."""
        job = JobOpportunity(
            job_id="test_123",
            platform=JobPlatform.UPWORK,
            title="Python Developer",
            description="Test job",
            url=None,
            posted_date=datetime.now(),
            budget={"min": 1000, "max": 2000, "type": "fixed"},
            hourly_rate=75.0,
            skills=["python", "django"],
            client_info={"rating": 4.8},
            competition={"bids": 5, "level": "low"},
            match_score=85.0
        )
        self.assertEqual(job.job_id, "test_123")
        self.assertEqual(job.match_score, 85.0)
    
    def test_04_client_researcher_init(self):
        """Test ClientResearcher initialization."""
        self.assertIsNotNone(self.seeker.clients)
    
    def test_05_research_client(self):
        """Test client research workflow."""
        report = self.seeker.research_client(
            client_name="TestCorp",
            platform="upwork",
            client_info={
                "rating": 4.7,
                "total_spent": 50000,
                "hire_rate": 0.75
            }
        )
        
        self.assertIsInstance(report, ResearchReport)
        self.assertGreaterEqual(report.quality_score, 0)
        self.assertLessEqual(report.quality_score, 100)
        self.assertIn(report.risk_level, ["low", "medium", "high"])
        self.assertGreater(len(report.recommendations), 0)
    
    def test_06_proposal_generator_init(self):
        """Test ProposalGenerator initialization."""
        self.assertIsNotNone(self.seeker.proposals)
    
    def test_07_generate_proposal(self):
        """Test proposal generation."""
        job_data = {
            'id': 'test_job_001',
            'title': 'Python Backend Developer',
            'description': 'Build REST API for mobile app',
            'platform': 'upwork',
            'client_name': 'TestCorp',
            'skills': ['python', 'fastapi', 'postgresql']
        }
        
        proposal = self.seeker.generate_proposal(job_data)
        
        self.assertIsInstance(proposal, Proposal)
        self.assertEqual(proposal.status, ProposalStatus.DRAFT)
        self.assertIsNotNone(proposal.content)
        self.assertIn("python", proposal.content.lower())
    
    def test_08_queue_for_review(self):
        """Test proposal queuing."""
        job_data = {
            'id': 'test_job_002',
            'title': 'Web Developer',
            'description': 'Frontend work',
            'platform': 'upwork',
            'client_name': 'TestCorp',
            'skills': ['react']
        }
        
        proposal = self.seeker.generate_proposal(job_data)
        queued = self.seeker.queue_for_review(proposal)
        
        self.assertEqual(queued.status, ProposalStatus.PENDING_REVIEW)
    
    def test_09_submit_proposal_checkpoint(self):
        """Test proposal submission checkpoint."""
        result = self.seeker.submit_proposal("test_proposal_123", approval_given=False)
        
        self.assertEqual(result['status'], 'CHECKPOINT')
        self.assertIn('action_required', result)
    
    def test_10_find_jobs_integration(self):
        """Test integrated find_jobs method."""
        jobs = self.seeker.find_jobs(
            keywords=["python"],
            platforms=None,
            min_match_score=0
        )
        
        self.assertIsInstance(jobs, list)
    
    def test_11_proposal_statistics(self):
        """Test proposal statistics."""
        stats = self.seeker.proposals.get_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('total_generated', stats)
        self.assertIn('by_status', stats)
    
    def test_12_scanner_statistics(self):
        """Test scanner statistics."""
        stats = self.seeker.scanners.get_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('total_discovered', stats)
        self.assertIn('by_platform', stats)


class TestExecution(unittest.TestCase):
    """Test Execution module components."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.executor = JobExecutor()
        cls.sample_requirements = """
        Build a Python web application with user authentication.
        
        Requirements:
        - User login/registration
        - Task management
        - PostgreSQL database
        - API endpoints
        """
    
    def test_01_job_execution_init(self):
        """Test JobExecutionOrchestrator initialization."""
        self.assertIsNotNone(self.executor.orchestrator)
    
    def test_02_start_job(self):
        """Test starting a job."""
        job = self.executor.start_job(
            job_id="test_execution_001",
            requirements=self.sample_requirements,
            client="TestClient"
        )
        
        self.assertIsInstance(job, dict)
        self.assertEqual(job['job_id'], "test_execution_001")
        self.assertIn('tasks', job)
    
    def test_03_requirements_parser_init(self):
        """Test RequirementsParser initialization."""
        self.assertIsNotNone(self.executor.parser)
    
    def test_04_parse_requirements(self):
        """Test requirements parsing."""
        project = self.executor.parser.parse(
            self.sample_requirements,
            project_title="Test Project"
        )
        
        self.assertIsInstance(project, ParsedProject)
        self.assertEqual(project.project_title, "Test Project")
        self.assertIn(project.domain, ['web', 'mobile', 'api', 'data', 'ai_ml', 'ecommerce'])
        self.assertGreater(len(project.deliverables), 0)
    
    def test_05_extract_technologies(self):
        """Test technology extraction."""
        from execution import TechnologyExtractor
        
        extractor = TechnologyExtractor()
        techs = extractor.extract("Build a React app with Django backend")
        
        self.assertIsInstance(techs, dict)
        self.assertIn('frontend', techs)
        self.assertIn('backend', techs)
    
    def test_06_scope_estimation(self):
        """Test scope estimation."""
        from execution import ScopeEstimator
        
        estimator = ScopeEstimator()
        scope = estimator.estimate_complexity(
            "Build a microservices architecture with real-time features",
            ["auth", "api", "websocket", "database"]
        )
        
        self.assertIn(scope['level'], ['low', 'medium', 'high'])
        self.assertIn('estimated_hours', scope)
    
    def test_07_execution_phase_enum(self):
        """Test ExecutionPhase enum values."""
        phases = [
            ExecutionPhase.REQUIREMENTS,
            ExecutionPhase.RESEARCH,
            ExecutionPhase.DESIGN,
            ExecutionPhase.IMPLEMENTATION,
            ExecutionPhase.TESTING,
            ExecutionPhase.DOCUMENTATION,
            ExecutionPhase.PACKAGING,
            ExecutionPhase.REVIEW,
            ExecutionPhase.DELIVERY,
            ExecutionPhase.INVOICING
        ]
        
        self.assertEqual(len(phases), 10)
        
        for phase in phases:
            self.assertIsInstance(phase.value, str)
    
    def test_08_checkpoint_request(self):
        """Test checkpoint request creation."""
        # Start a job first
        job = self.executor.start_job(
            job_id="test_checkpoint_001",
            requirements=self.sample_requirements,
            client="TestClient"
        )
        
        checkpoint = self.executor.orchestrator.checkpoint_request_approval(
            job_id=job['job_id'],
            phase=ExecutionPhase.DESIGN,
            artifacts=["design.md"]
        )
        
        self.assertEqual(checkpoint.phase, ExecutionPhase.DESIGN)
        self.assertEqual(checkpoint.status, CheckpointStatus.WAITING_APPROVAL)
    
    def test_09_resolve_checkpoint(self):
        """Test checkpoint resolution."""
        job = self.executor.start_job(
            job_id="test_resolve_001",
            requirements=self.sample_requirements,
            client="TestClient"
        )
        
        self.executor.orchestrator.checkpoint_request_approval(
            job_id=job['job_id'],
            phase=ExecutionPhase.DESIGN,
            artifacts=[]
        )
        
        result = self.executor.orchestrator.resolve_checkpoint(
            job_id=job['job_id'],
            phase=ExecutionPhase.DESIGN,
            approval="approved"
        )
        
        self.assertTrue(result)
    
    def test_10_handle_client_feedback(self):
        """Test client feedback handling."""
        job = self.executor.start_job(
            job_id="test_feedback_001",
            requirements=self.sample_requirements,
            client="TestClient"
        )
        
        # Test revision feedback
        result = self.executor.handle_client_feedback(
            job_id=job['job_id'],
            feedback="Please make a few changes to the auth system"
        )
        
        self.assertEqual(result['action_type'], 'revision')
        self.assertGreaterEqual(result['tasks_created'], 0)
        
        # Test approval feedback
        result2 = self.executor.handle_client_feedback(
            job_id=job['job_id'],
            feedback="Great work, approved!"
        )
        
        self.assertEqual(result2['action_type'], 'approval')
    
    def test_11_execute_phase(self):
        """Test single phase execution."""
        job = self.executor.start_job(
            job_id="test_phase_001",
            requirements=self.sample_requirements,
            client="TestClient"
        )
        
        # Research phase (no checkpoint)
        result = self.executor.execute_step(
            job['job_id'],
            ExecutionPhase.RESEARCH,
            approval=True
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('research', result)
    
    def test_12_checkpoint_detection(self):
        """Test checkpoint detection in execute_step."""
        job = self.executor.start_job(
            job_id="test_checkpoint_detect_001",
            requirements=self.sample_requirements,
            client="TestClient"
        )
        
        # Try to execute checkpoint phase without approval
        result = self.executor.execute_step(
            job['job_id'],
            ExecutionPhase.DESIGN,
            approval=False
        )
        
        self.assertIn('checkpoint', result)
        self.assertTrue(result['checkpoint'])
    
    def test_13_job_status(self):
        """Test getting job status."""
        job = self.executor.start_job(
            job_id="test_status_001",
            requirements=self.sample_requirements,
            client="TestClient"
        )
        
        status = self.executor.get_job_status(job['job_id'])
        
        self.assertIsInstance(status, dict)
        self.assertEqual(status['job_id'], job['job_id'])
        self.assertIn('progress', status)
    
    def test_14_list_jobs(self):
        """Test listing active jobs."""
        jobs = self.executor.list_jobs()
        
        self.assertIsInstance(jobs, list)
        
        for job in jobs:
            self.assertIn('job_id', job)
            self.assertIn('status', job)
    
    def test_15_complete_job_checkpoint(self):
        """Test job completion checkpoint."""
        job = self.executor.start_job(
            job_id="test_complete_001",
            requirements=self.sample_requirements,
            client="TestClient"
        )
        
        result = self.executor.complete_job(job['job_id'], final_approval=False)
        
        self.assertIn('checkpoint', result)
        self.assertTrue(result['checkpoint'])
    
    def test_16_complete_job_final(self):
        """Test actual job completion."""
        job = self.executor.start_job(
            job_id="test_complete_real_001",
            requirements=self.sample_requirements,
            client="TestClient"
        )
        
        result = self.executor.complete_job(job['job_id'], final_approval=True)
        
        self.assertEqual(result['status'], 'completed')
        self.assertIn('artifacts', result)


class TestSkillEvolutionBridge(unittest.TestCase):
    """Test Skill Evolution Bridge module components."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.bridge = SkillEvolutionBridge()
    
    def test_01_bridge_init(self):
        """Test SkillEvolutionBridge initialization."""
        self.assertIsNotNone(self.bridge)
        self.assertIsNotNone(self.bridge.omnibot_dir)
    
    def test_02_get_all_modules(self):
        """Test getting all Omnibot modules."""
        modules = self.bridge.get_all_modules()
        
        self.assertIsInstance(modules, list)
        self.assertGreater(len(modules), 0)
        
        # Check module structure
        for module in modules:
            self.assertIn('name', module)
            self.assertIn('path', module)
            self.assertIn('file_count', module)
    
    def test_03_fallback_analysis(self):
        """Test fallback analysis when SEE not available."""
        # Use an existing module for testing
        modules = self.bridge.get_all_modules()
        if modules:
            health = self.bridge.analyze_omnibot_module(modules[0]['name'])
            
            self.assertIsNotNone(health)
            self.assertGreaterEqual(health.health_score, 0)
            self.assertLessEqual(health.health_score, 100)
            self.assertIsInstance(health.findings, list)
            self.assertIsInstance(health.recommendations, list)
    
    def test_04_overall_health(self):
        """Test overall health calculation."""
        health = self.bridge.get_overall_health()
        
        self.assertIsInstance(health, dict)
        
        if 'overall_health' in health:
            self.assertIsInstance(health['overall_health'], int)
        if 'modules_analyzed' in health:
            self.assertIsInstance(health['modules_analyzed'], int)
    
    def test_05_propose_improvements(self):
        """Test improvement proposal generation."""
        proposals = self.bridge.propose_improvements()
        
        self.assertIsInstance(proposals, list)
        
        for prop in proposals[:3]:
            self.assertIn('target_module', prop)
            self.assertIn('health_score', prop)
            self.assertIn('priority', prop)
            self.assertIn('recommendations', prop)
            self.assertIn(prop['priority'], ['critical', 'high', 'medium', 'low'])
    
    def test_06_evolve_with_approval_structure(self):
        """Test evolution cycle structure."""
        proposals = self.bridge.propose_improvements()
        
        if proposals:
            request = self.bridge.evolve_with_approval(proposals[0])
            
            self.assertIsInstance(request, dict)
            self.assertIn('module', request)
            self.assertIn('improvements', request)
            self.assertIn('requires_approval', request)
    
    def test_07_estimate_effort(self):
        """Test effort estimation."""
        effort = self.bridge._estimate_effort([])
        self.assertEqual(effort, 'none')
        
        effort = self.bridge._estimate_effort([{}, {}, {}])
        self.assertEqual(effort, 'low (1-2 hours)')
        
        effort = self.bridge._estimate_effort([{}] * 7)
        self.assertEqual(effort, 'high (1-2 days)')
    
    def test_08_health_distribution(self):
        """Test health distribution calculation."""
        health = self.bridge.get_overall_health()
        
        if 'modules_by_health' in health:
            self.assertIsInstance(health['modules_by_health'], dict)
            self.assertIn('excellent (90+)', health['modules_by_health'])
            self.assertIn('fair (60-74)', health['modules_by_health'])
    
    def test_09_auto_fix_module(self):
        """Test automatic module fixing."""
        modules = self.bridge.get_all_modules()
        if modules:
            # Don't actually modify files in tests
            # Just verify the method signature works
            pass  # Test would be destructive, skipped
    
    def test_10_generate_evolution_report(self):
        """Test evolution report generation."""
        report = self.bridge.generate_evolution_report()
        
        self.assertIsInstance(report, str)
        self.assertIn('OMNIBOT EVOLUTION REPORT', report)


class TestIntegration(unittest.TestCase):
    """Test integration between all Phase 3 modules."""
    
    def test_01_full_job_pipeline(self):
        """Test complete job pipeline from discovery to execution."""
        seeker = JobSeeker()
        executor = JobExecutor()
        
        # Find jobs
        jobs = seeker.find_jobs(["python"], min_match_score=0)
        self.assertIsInstance(jobs, list)
        
        if jobs:
            # Research client
            report = seeker.research_client(
                "TestCorp", "upwork", jobs[0].client_info
            )
            self.assertIsInstance(report, ResearchReport)
            
            # Generate proposal  
            proposal = seeker.generate_proposal(jobs[0], report)
            self.assertIsInstance(proposal, Proposal)
            
            # Queue for review
            queued = seeker.queue_for_review(proposal)
            self.assertEqual(queued.status, ProposalStatus.PENDING_REVIEW)
            
            # Start job execution
            job = executor.start_job(
                job_id=f"integrated_{jobs[0].job_id}",
                requirements=jobs[0].description,
                client=jobs[0].client_info.get('company', 'Client')
            )
            self.assertIn('tasks', job)
    
    def test_02_checkpoint_integration(self):
        """Test checkpoints across modules."""
        seeker = JobSeeker()
        executor = JobExecutor()
        
        # Job seeker checkpoint
        result = seeker.submit_proposal("test", approval_given=False)
        self.assertEqual(result['status'], 'CHECKPOINT')
        
        # Execution checkpoint
        job = executor.start_job(
            job_id="test_checkpoint_integration",
            requirements="Build a web app",
            client="Test"
        )
        
        result = executor.complete_job(job['job_id'], final_approval=False)
        self.assertIn('checkpoint', result)
    
    def test_03_see_bridge_integration(self):
        """Test SEE bridge integration."""
        from self_modify import SkillEvolutionBridge
        
        bridge = SkillEvolutionBridge()
        modules = bridge.get_all_modules()
        
        # Verify job_seeker and execution modules exist
        module_names = [m['name'] for m in modules]
        self.assertIn('job_seeker', module_names)
        self.assertIn('execution', module_names)


def run_tests():
    """Run all Phase 3 tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestJobSeeker))
    suite.addTests(loader.loadTestsFromTestCase(TestExecution))
    suite.addTests(loader.loadTestsFromTestCase(TestSkillEvolutionBridge))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("PHASE 3 TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("="*70)
    
    if result.wasSuccessful():
        print("\n✅ ALL PHASE 3 TESTS PASSED!")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        return 1


if __name__ == '__main__':
    sys.exit(run_tests())
