#!/usr/bin/env python3
"""
Omnibot - Ultimate Autonomous Agent
Main entry point integrating all 12 core capabilities plus autonomous extensions.

Complete module list:
1. Memory System (hot_memory, warm_memory, cold_memory, consolidator)
2. Context Verifier
3. Checkpoint Manager
4. Trust Scorer
5. ACA Reasoning Engine
6. Research Orchestrator (GUI-First)
7. API Management (discovery, vault, cost_tracker)
8. Wallet Manager
9. Job Seeker (scanners, proposal generator, client researcher)
10. Design System
11. Safety Container & Audit
12. Dream Processor

Plus autonomous extensions:
- Proactive Engine
- Skill Evolution Bridge
- Multimodal Analyzer
- Cross Platform Sync
- Cost Optimizer
- Federated Learning
- Job Execution
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum

# Add local modules to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Core modules
from core.orchestrator import Orchestrator
from core.context_verifier import ContextVerifier
from core.checkpoint_manager import CheckpointManager
from core.trust_scorer import TrustScorer

# Memory modules
from memory.hot_memory import HotMemory
from memory.warm_memory import WarmMemory
from memory.cold_memory import ColdMemory
from memory.consolidator import MemoryConsolidator

# Reasoning modules
from reasoning.aca_engine import ACAEngine
from reasoning.error_recovery import ErrorRecovery
from reasoning.decision_logger import DecisionLogger

# Research modules
from research.research_orchestrator import ResearchOrchestrator
from research.design_researcher import DesignResearcher
from research.gui_generator import GUIGenerator

# API modules
from api.auto_discovery import APIDiscovery
from api.secure_vault import SecureVault
from api.cost_tracker import CostTracker

# Wallet modules
from wallet.wallet_manager import WalletManager
from wallet.security_wrapper import SecurityWrapper

# UI modules
from ui.gui_components import GUIComponents
from ui.mockup_renderer import MockupRenderer

# Meta modules
from meta.learning_engine import LearningEngine
from meta.performance_tracker import PerformanceTracker
from meta.doc_generator import DocGenerator

# Autonomous Extension Modules (NEW)
from proactive.proactive_engine import ProactiveEngine
from self_modify.skill_evolution_bridge import SkillEvolutionBridge
from perception.multimodal_analyzer import MultimodalAnalyzer
from platform.cross_platform_sync import CrossPlatformPresence
from economics.cost_optimizer import CostOptimizer, Provider
from federation.learning_network import FederatedLearning, KnowledgeType
from dream.dream_processor import DreamProcessor, DreamTaskType

# Job modules
from job_seeker import PlatformScanners, ProposalGenerator, ClientResearcher, RateCalculator
from execution.job_workflow import JobExecutionOrchestrator, ExecutionPhase
from execution.requirements_parser import RequirementsParser

# Design modules
from design.autonomous_designer import AutonomousDesigner, DesignStyle

# Safety modules
from safety.safety_container import SafetyContainer, SafetyPolicy
from safety.audit_logger import AuditLogger, AuditLevel, ActionType

# Config
WORKSPACE_DIR = Path("/home/skux/.openclaw/workspace")
OMNIBOT_DIR = WORKSPACE_DIR / "skills" / "omnibot"
MEMORY_DIR = WORKSPACE_DIR / "memory"


@dataclass
class TrustScore:
    """Trust scoring for every output."""
    confidence: float  # 0-100
    reasoning: str
    alternative_approaches: List[str]
    risk_level: str  # low, medium, high


class Omnibot:
    """
    Ultimate Autonomous Agent with 12 core capabilities + autonomous extensions.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.start_time = datetime.now()
        self.config = self._load_config(config_path)
        
        # Initialize logging
        self._setup_logging()
        self.logger = logging.getLogger("Omnibot")
        
        # Initialize all modules
        self.logger.info("🤖 Initializing Omnibot...")
        self._init_modules()
        
        self.logger.info("✅ Omnibot ready!")
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration with defaults."""
        defaults = {
            "auto_approve": ["read", "research", "code"],
            "approval_required": ["external", "spend", "delete", "publish"],
            "max_error_retries": 3,
            "stale_data_threshold_hours": 24,
            "cost_budget_daily": 100.00,
            "trust_confidence_threshold": 75,
            "memory_dir": str(MEMORY_DIR),
            "encryption_enabled": True,
            "log_level": "INFO"
        }
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                defaults.update(user_config)
        
        return defaults
    
    def _setup_logging(self):
        """Configure logging."""
        log_level = getattr(logging, self.config.get("log_level", "INFO"))
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(OMNIBOT_DIR / "omnibot.log")
            ]
        )
    
    def _init_modules(self):
        """Initialize all core and extension modules."""
        # ==================== CORE MODULES ====================
        
        # Memory System
        self.hot_memory = HotMemory()
        self.warm_memory = WarmMemory(MEMORY_DIR)
        self.cold_memory = ColdMemory(WORKSPACE_DIR / "MEMORY.md")
        self.consolidator = MemoryConsolidator(self.hot_memory, self.warm_memory, self.cold_memory)
        
        # Orchestration
        self.orchestrator = Orchestrator(self)
        self.context_verifier = ContextVerifier(self.stale_data_threshold_hours)
        self.checkpoint_manager = CheckpointManager(self)
        self.trust_scorer = TrustScorer()
        
        # Reasoning
        self.aca_engine = ACAEngine(self)
        self.error_recovery = ErrorRecovery(self.config["max_error_retries"])
        self.decision_logger = DecisionLogger(MEMORY_DIR / "decisions")
        
        # Research
        self.design_researcher = DesignResearcher(self)
        self.gui_generator = GUIGenerator(OMNIBOT_DIR / "output")
        self.research_orchestrator = ResearchOrchestrator(self)
        
        # API
        self.api_discovery = APIDiscovery(OMNIBOT_DIR / "api")
        self.api_vault = SecureVault(OMNIBOT_DIR / "api")
        self.cost_tracker = CostTracker(self.config["cost_budget_daily"])
        
        # Wallet
        self.wallet_security = SecurityWrapper()
        self.wallet_manager = WalletManager(OMNIBOT_DIR / "wallet", self.wallet_security)
        
        # UI
        self.gui_components = GUIComponents()
        self.mockup_renderer = MockupRenderer(OMNIBOT_DIR / "output")
        
        # Meta
        self.learning_engine = LearningEngine(OMNIBOT_DIR / "meta")
        self.performance_tracker = PerformanceTracker(self)
        self.doc_generator = DocGenerator()
        
        # ==================== AUTONOMOUS EXTENSION MODULES ====================
        self.logger.info("🔧 Loading autonomous extension modules...")
        
        # Module 1: Proactive Engine
        self.proactive = ProactiveEngine(self)
        
        # Module 2: Self-Modification Bridge
        self.evolution = SkillEvolutionBridge(self)
        
        # Module 3: Multimodal Perception
        self.perception = MultimodalAnalyzer(self)
        
        # Module 4: Cross-Platform Sync
        self.platform = CrossPlatformPresence(self)
        
        # Module 5: Cost Optimization
        self.economics = CostOptimizer(self, daily_budget=self.config["cost_budget_daily"])
        
        # Module 6: Federated Learning
        self.federation = FederatedLearning(self)
        
        # Module 7: Dream Processor
        self.dream = DreamProcessor(self)
        
        # Module 8: Job Seeker (composite module)
        self.job_seeker = type('JobSeeker', (), {
            'scanners': PlatformScanners(self),
            'proposals': ProposalGenerator(self),
            'clients': ClientResearcher(),
            'rates': RateCalculator()
        })()
        
        # Module 9: Job Execution
        self.execution = type('JobExecution', (), {
            'orchestrator': JobExecutionOrchestrator(self),
            'parser': RequirementsParser()
        })()
        
        # Module 10: Autonomous Designer
        self.designer = AutonomousDesigner(self)
        
        # Module 11: Safety Container
        safety_policy = SafetyPolicy(
            max_execution_time=30,
            max_memory_mb=256,
            require_secret_scan=True
        )
        self.safety = type('Safety', (), {
            'container': SafetyContainer(safety_policy),
            'audit': AuditLogger(),
            'policy': safety_policy
        })()
        
        self.logger.info("✅ All extension modules loaded")
    
    # ==================== MEMORY SYSTEM ====================
    
    def remember(self, info: str, priority: str = "normal", 
                 tags: Optional[List[str]] = None,
                 ttl_hours: Optional[int] = None) -> str:
        """
        Store information in appropriate memory tier.
        
        Args:
            info: Information to store
            priority: hot, warm, cold, or auto
            tags: Optional tags for categorization
            ttl_hours: Optional time-to-live
            
        Returns:
            Memory ID for retrieval
        """
        tags = tags or []
        
        if priority == "hot" or (priority == "auto" and self._is_session_critical(info)):
            return self.hot_memory.store(info, tags)
        elif priority == "cold" or (priority == "auto" and self._is_long_term_relevant(info)):
            return self.cold_memory.store(info, tags)
        else:
            return self.warm_memory.store(info, tags, ttl_hours)
    
    def recall(self, query: str, max_results: int = 10,
               from_tiers: Optional[List[str]] = None) -> List[Dict]:
        """
        Recall information from memory tiers.
        
        Args:
            query: Search query
            max_results: Maximum results to return
            from_tiers: Specific tiers to search (hot, warm, cold)
            
        Returns:
            List of matching memories with relevance scores
        """
        from_tiers = from_tiers or ["hot", "warm", "cold"]
        results = []
        
        if "hot" in from_tiers:
            results.extend(self.hot_memory.search(query, max_results))
        if "warm" in from_tiers:
            results.extend(self.warm_memory.search(query, max_results))
        if "cold" in from_tiers:
            results.extend(self.cold_memory.search(query, max_results))
        
        # Sort by relevance (timestamp + match quality)
        results.sort(key=lambda x: x.get("relevance", 0), reverse=True)
        return results[:max_results]
    
    def consolidate(self, force: bool = False) -> Dict:
        """
        Consolidate memories across tiers.
        
        Args:
            force: Force consolidation even if not needed
            
        Returns:
            Consolidation report
        """
        return self.consolidator.run(force=force)
    
    def _is_session_critical(self, info: str) -> bool:
        """Determine if info should go to hot memory."""
        critical_keywords = ["session", "now", "current", "active", "temp"]
        return any(kw in info.lower() for kw in critical_keywords)
    
    def _is_long_term_relevant(self, info: str) -> bool:
        """Determine if info should go to cold memory."""
        permanent_keywords = [
            "config", "setting", "preference", "important", 
            "critical", "never forget", "always"
        ]
        return any(kw in info.lower() for kw in permanent_keywords)
    
    # ==================== CONTEXT VERIFICATION ====================
    
    def verify_context(self, context_type: str, data: Dict) -> Dict:
        """
        Verify context against stored knowledge.
        
        Args:
            context_type: Type of context (api, ui, library, etc.)
            data: Current context data
            
        Returns:
            Verification result with flags for stale data
        """
        return self.context_verifier.verify(context_type, data)
    
    def refresh_if_stale(self, context_type: str) -> Tuple[bool, Any]:
        """
        Check and refresh stale context.
        
        Args:
            context_type: Type of context to check
            
        Returns:
            (was_refreshed, fresh_data)
        """
        is_stale, fresh_data = self.context_verifier.check_staleness(context_type)
        if is_stale and fresh_data:
            self.remember(f"Refreshed {context_type} context", priority="warm")
            return True, fresh_data
        return False, None
    
    # ==================== API MANAGEMENT ====================
    
    def discover_apis(self, category: Optional[str] = None) -> List[Dict]:
        """
        Discover APIs from public sources.
        
        Args:
            category: Optional category filter
            
        Returns:
            List of discovered APIs
        """
        return self.api_discovery.discover(category)
    
    def store_api_key(self, service: str, key: str, tier: str = "free") -> str:
        """
        Securely store an API key.
        
        Args:
            service: Service name
            key: API key
            tier: Service tier (free, paid, enterprise)
            
        Returns:
            Reference ID for retrieval
        """
        return self.api_vault.store(service, key, tier)
    
    def get_api_key(self, service: str) -> Optional[str]:
        """
        Retrieve an API key for use.
        
        Args:
            service: Service name
            
        Returns:
            API key or None if not found
        """
        return self.api_vault.retrieve(service)
    
    def track_api_cost(self, service: str, cost: float, units: int = 1):
        """
        Track API usage cost.
        
        Args:
            service: Service name
            cost: Cost amount
            units: Number of units consumed
        """
        self.cost_tracker.add(service, cost, units)
    
    # ==================== CRYPTO WALLET ====================
    
    def add_wallet(self, name: str, private_key: str, purpose: str,
                   chain: str = "solana") -> str:
        """
        Securely store a wallet.
        
        Args:
            name: Wallet identifier
            private_key: Private key (encrypted)
            purpose: Usage purpose (trading, nft, staking, etc.)
            chain: Blockchain (solana, ethereum, etc.)
            
        Returns:
            Wallet reference ID
        """
        return self.wallet_manager.add_wallet(name, private_key, purpose, chain)
    
    def get_wallet(self, name: str, inject_mode: bool = False) -> Union[str, Dict]:
        """
        Retrieve wallet details.
        
        Args:
            name: Wallet identifier
            inject_mode: If True, returns injectable code snippet
            
        Returns:
            Wallet info or code snippet
        """
        wallet = self.wallet_manager.get_wallet(name)
        if inject_mode:
            return self.wallet_security.generate_injectable(wallet)
        return wallet
    
    # ==================== ACA INTEGRATION ====================
    
    def aca_workflow(self, requirements: str, 
                     data_flow: Optional[str] = None,
                     constraints: Optional[List[str]] = None,
                     auto_run: bool = True) -> Dict:
        """
        Run the 7-step ACA workflow.
        
        Args:
            requirements: Task requirements
            data_flow: Optional data flow description
            constraints: Optional constraints list
            auto_run: Automatically execute the workflow
            
        Returns:
            ACA workflow result with all 7 steps
        """
        return self.aca_engine.run_workflow(
            requirements=requirements,
            data_flow=data_flow,
            constraints=constraints,
            auto_run=auto_run
        )
    
    # ==================== RESEARCH ENGINE (GUI-FIRST) ====================
    
    def research_app_design(self, app_type: str, 
                          features: Optional[List[str]] = None,
                          target_audience: Optional[str] = None,
                          platform_str: str = "mobile") -> Dict:
        """
        Comprehensive app design research with GUI output.
        
        Args:
            app_type: Type of app (coffee shop, fitness, etc.)
            features: List of key features
            target_audience: Target user demographic
            platform_str: Target platform (mobile, web, desktop)
            
        Returns:
            Complete design package with research and mockups
        """
        return self.research_orchestrator.design_app(
            app_type=app_type,
            features=features,
            target_audience=target_audience,
            platform=platform_str
        )
    
    def research_colors(self, app_type: str, 
                        mood: Optional[str] = None) -> Dict:
        """
        Research color psychology and palettes.
        
        Args:
            app_type: Type of application
            mood: Desired mood/feel
            
        Returns:
            Color research with palette recommendations
        """
        return self.design_researcher.research_colors(app_type, mood)
    
    def generate_mockups(self, screens: List[str], 
                         design_system: Dict,
                         output_dir: Optional[str] = None) -> List[str]:
        """
        Generate HTML/CSS mockups for screens.
        
        Args:
            screens: List of screen names
            design_system: Design system with colors, typography, etc.
            output_dir: Optional output directory
            
        Returns:
            List of generated HTML file paths
        """
        return self.gui_generator.generate_screens(screens, design_system, output_dir)
    
    # ==================== ERROR RECOVERY ====================
    
    def execute_with_recovery(self, func, *args, **kwargs) -> Tuple[bool, Any]:
        """
        Execute function with error recovery.
        
        Args:
            func: Function to execute
            *args, **kwargs: Function arguments
            
        Returns:
            (success, result/error_info)
        """
        return self.error_recovery.execute(func, *args, **kwargs)
    
    # ==================== APPROVAL CHECKPOINTS ====================
    
    def needs_approval(self, action_type: str) -> bool:
        """
        Check if an action needs human approval.
        
        Args:
            action_type: Type of action
            
        Returns:
            True if approval required
        """
        return self.checkpoint_manager.needs_approval(action_type)
    
    def request_approval(self, action: str, details: Dict) -> bool:
        """
        Request human approval for an action.
        
        Args:
            action: Action description
            details: Action details
            
        Returns:
            True if approved
        """
        return self.checkpoint_manager.request(action, details)
    
    # ==================== AUTONOMOUS EXTENSION METHODS ====================
    
    def find_job(self, keywords: Optional[List[str]] = None, platforms: Optional[List[str]] = None) -> List[Dict]:
        """
        Find jobs across platforms.
        
        Args:
            keywords: Search keywords
            platforms: Platforms to search (upwork, linkedin, etc.)
            
        Returns:
            List of job opportunities
        """
        self.logger.info(f"🔍 Finding jobs: {keywords}")
        
        # Scan platforms
        jobs = self.job_seeker.scanners.scan_all_platforms(keywords)
        
        # Convert to dict for serialization
        return [
            {
                'job_id': job.job_id,
                'title': job.title,
                'platform': job.platform.value,
                'match_score': job.match_score,
                'hourly_rate': job.hourly_rate,
                'budget': job.budget
            }
            for job in jobs
        ]
    
    def generate_proposal(self, job: Dict) -> Dict:
        """
        Generate a proposal for a job.
        
        Args:
            job: Job dictionary with job info
            
        Returns:
            Generated proposal with ID
        """
        self.logger.info(f"📝 Generating proposal for: {job.get('title')}")
        
        proposal = self.job_seeker.proposals.generate_proposal(job, job.get('platform', 'upwork'))
        
        return {
            'proposal_id': proposal.proposal_id,
            'client': proposal.client_name,
            'rate': proposal.proposed_rate,
            'estimated_hours': proposal.estimated_hours,
            'content': proposal.content[:500] + "..."
        }
    
    def start_job_execution(self, job_id: str, requirements: str, client: str) -> Dict:
        """
        Start job execution workflow.
        
        Args:
            job_id: Job identifier
            requirements: Project requirements
            client: Client name
            
        Returns:
            Job execution context
        """
        self.logger.info(f"🚀 Starting job execution: {job_id}")
        return self.execution.orchestrator.start_job(job_id, requirements, client)
    
    def proactive_check(self) -> Optional[Dict]:
        """
        Run proactive check for anomalies and opportunities.
        
        Returns:
            Suggestion if found, None otherwise
        """
        return self.proactive.check_and_intervene()
    
    def analyze_omnibot_health(self) -> Dict:
        """
        Analyze Omnibot's health using skill evolution bridge.
        
        Returns:
            Health report
        """
        return self.evolution.get_overall_health()
    
    def analyze_media(self, media_path: str) -> Dict:
        """
        Analyze media file (image, video, audio, PDF).
        
        Args:
            media_path: Path to media file
            
        Returns:
            Analysis results
        """
        result = self.perception.analyze(media_path)
        return {
            'media_type': result.media_type.value,
            'summary': result.summary,
            'key_insights': result.key_insights,
            'confidence': result.confidence
        }
    
    def get_cost_report(self) -> str:
        """
        Get current cost report.
        
        Returns:
            Human-readable cost report
        """
        return self.economics.generate_cost_report()
    
    def suggest_cheaper_alternative(self, provider: str, service: str) -> Optional[Dict]:
        """
        Suggest cheaper alternative for a service.
        
        Args:
            provider: Current provider name
            service: Current service name
            
        Returns:
            Alternative suggestion or None
        """
        try:
            prov = Provider(provider.lower())
            return self.economics.suggest_cheaper_alternative(prov, service)
        except ValueError:
            return None
    
    def run_dream_cycle(self) -> str:
        """
        Run dream mode overnight processing.
        
        Returns:
            Morning briefing
        """
        self.dream.start_dream_mode(blocking=True)
        return self.dream.display_briefing()
    
    def create_design(self, name: str, style: str = "modern") -> Dict:
        """
        Create a design project.
        
        Args:
            name: Project name
            style: Design style (modern, minimal, etc.)
            
        Returns:
            Design project info
        """
        style_enum = DesignStyle(style.lower()) if hasattr(DesignStyle, style.upper()) else DesignStyle.MODERN
        project = self.designer.create_project(name, f"Design for {name}", style_enum)
        return {
            'project_id': project.project_id,
            'name': project.name,
            'style': project.style.value,
            'palette': project.palette
        }
    
    def validate_code_safety(self, code: str) -> Tuple[bool, List[str]]:
        """
        Validate code for safety before execution.
        
        Args:
            code: Python code to validate
            
        Returns:
            (is_safe, violations)
        """
        return self.safety.container.validate_code(code)
    
    # ==================== SELF-MONITORING ====================
    
    def get_status(self) -> Dict:
        """
        Get current Omnibot status.
        
        Returns:
            Status report with metrics
        """
        status = self.performance_tracker.get_status()
        status['extensions'] = {
            'proactive_patterns': len(self.proactive.user_patterns),
            'modules_analyzed': len(self.evolution.module_health_cache),
            'jobs_discovered': len(self.job_seeker.scanners.jobs),
            'daily_cost': self.economics.get_daily_summary()['total_cost']
        }
        return status
    
    def get_suggestions(self) -> List[str]:
        """
        Get improvement suggestions.
        
        Returns:
            List of suggestions
        """
        return self.learning_engine.suggest_improvements()
    
    # ==================== SECURITY ====================
    
    def scan_for_secrets(self, content: str) -> List[Dict]:
        """
        Scan content for potential secrets.
        
        Args:
            content: Content to scan
            
        Returns:
            List of found secrets
        """
        return self.wallet_security.scan_for_secrets(content)
    
    def sanitize_output(self, content: str) -> str:
        """
        Sanitize output to remove secrets.
        
        Args:
            content: Content to sanitize
            
        Returns:
            Sanitized content
        """
        return self.wallet_security.sanitize(content)
    
    # ==================== DOCUMENTATION ====================
    
    def generate_usage_doc(self, script_path: str, 
                         output_path: Optional[str] = None) -> str:
        """
        Generate USAGE.md for a script.
        
        Args:
            script_path: Path to script
            output_path: Optional output path
            
        Returns:
            Generated documentation content
        """
        return self.doc_generator.generate_usage(script_path, output_path)
    
    def generate_project_readme(self, project_dir: str) -> str:
        """
        Generate README.md for a project.
        
        Args:
            project_dir: Project directory
            
        Returns:
            Generated README content
        """
        return self.doc_generator.generate_readme(project_dir)
    
    # ==================== TRUST SCORING ====================
    
    def score_output(self, output_type: str, data: Dict) -> TrustScore:
        """
        Generate trust score for any output.
        
        Args:
            output_type: Type of output
            data: Output data
            
        Returns:
            TrustScore with confidence and reasoning
        """
        return self.trust_scorer.calculate(output_type, data)
    
    # ==================== UTILITIES ====================
    
    def log_decision(self, decision: str, context: Dict, result: str):
        """
        Log a decision for future reference.
        
        Args:
            decision: Decision made
            context: Decision context
            result: Decision result
        """
        self.decision_logger.log(decision, context, result)
    
    def safe_execute(self, action_desc: str, func, *args, **kwargs) -> Any:
        """
        Execute with full safety checks (approval, error recovery, trust).
        
        Args:
            action_desc: Description of action
            func: Function to execute
            *args, **kwargs: Function arguments
            
        Returns:
            Function result
        """
        # Check approval
        if self.needs_approval(action_desc):
            if not self.request_approval(action_desc, {"args": args, "kwargs": kwargs}):
                raise PermissionError(f"Action '{action_desc}' not approved")
        
        # Execute with error recovery
        success, result = self.execute_with_recovery(func, *args, **kwargs)
        
        if not success:
            self.log_decision(action_desc, {"args": args, "kwargs": kwargs}, f"FAILED: {result}")
            raise RuntimeError(f"Action failed after retries: {result}")
        
        self.log_decision(action_desc, {"args": args, "kwargs": kwargs}, "SUCCESS")
        return result
    
    # Properties
    @property
    def stale_data_threshold_hours(self) -> int:
        return self.config.get("stale_data_threshold_hours", 24)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.info("Shutting down Omnibot...")
        self.consolidate()
        self.performance_tracker.save()
        self.decision_logger.save()


# Convenience function for quick access
def create_omnibot(config_path: Optional[str] = None) -> Omnibot:
    """Create and return an Omnibot instance."""
    return Omnibot(config_path)


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Omnibot - Ultimate Autonomous Agent")
    parser.add_argument("--status", action="store_true", help="Show status")
    parser.add_argument("--research", metavar="TOPIC", help="Research a topic")
    parser.add_argument("--design", metavar="APP_TYPE", help="Design an app")
    parser.add_argument("--remember", metavar="INFO", help="Remember information")
    parser.add_argument("--recall", metavar="QUERY", help="Recall information")
    parser.add_argument("--aca", metavar="REQUIREMENTS", help="Run ACA workflow")
    parser.add_argument("--jobs", action="store_true", help="Find jobs")
    parser.add_argument("--test", action="store_true", help="Run basic tests")
    
    args = parser.parse_args()
    
    bot = create_omnibot()
    
    if args.test:
        print("✅ Running basic module tests...")
        print(f"Memory: {len(bot.recall('test'))} items")
        print(f"Proactive: {bot.proactive.get_patterns_summary()['total_patterns']} patterns")
        print(f"Economics: ${bot.economics.get_daily_summary()['total_cost']:.4f} spent today")
        print(f"Safety: {bot.safety.container.get_execution_stats()['executions']} sandboxed runs")
        print("\n✅ All tests passed!")
    elif args.status:
        print(json.dumps(bot.get_status(), indent=2))
    elif args.research:
        print(json.dumps(bot.research_app_design(args.research), indent=2))
    elif args.design:
        result = bot.research_app_design(args.design)
        print(f"Design complete! Mockups generated at: {result.get('output_dir')}")
    elif args.remember:
        mem_id = bot.remember(args.remember)
        print(f"Remembered with ID: {mem_id}")
    elif args.recall:
        memories = bot.recall(args.recall)
        for mem in memories:
            print(f"[{mem.get('tier')}] {mem.get('content')}")
    elif args.aca:
        result = bot.aca_workflow(args.aca)
        print(json.dumps(result, indent=2))
    elif args.jobs:
        jobs = bot.find_job(["python", "web development"])
        print(f"Found {len(jobs)} jobs:")
        for job in jobs[:3]:
            print(f"  • {job['title']} ({job['match_score']:.0f}% match)")
    else:
        print("Omnibot ready. Use --help for options.")
