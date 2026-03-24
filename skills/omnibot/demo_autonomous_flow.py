#!/usr/bin/env python3
"""
Demo: Autonomous Job-Seeking & Execution Flow

Demonstrates the complete flow from job discovery to execution.
"""

import sys
from pathlib import Path

# Add omnibot to path
sys.path.insert(0, str(Path(__file__).parent))

from omnibot import Omnibot


def demo_job_discovery():
    """Demonstrate job discovery flow."""
    print("\n" + "="*70)
    print("🤖 OMNIBOT AUTONOMOUS DEMO")
    print("="*70)
    
    print("\n" + "─"*70)
    print("STEP 1: INITIALIZING OMNIBOT")
    print("─"*70)
    
    bot = Omnibot()
    print("✅ Omnibot initialized with all modules")
    
    # Check modules
    modules = [
        "proactive_engine",
        "skill_evolution_bridge", 
        "multimodal_analyzer",
        "cross_platform_sync",
        "cost_optimizer",
        "federated_learning",
        "dream_processor",
        "platform_scanners",
        "proposal_generator",
        "job_execution_orchestrator",
        "autonomous_designer",
        "safety_container"
    ]
    
    print("\n📦 Active Modules:")
    for module in modules:
        available = hasattr(bot, module)
        status = "✅" if available else "❌"
        print(f"  {status} {module}")
    
    print("\n" + "─"*70)
    print("STEP 2: JOB DISCOVERY")
    print("─"*70)
    
    # Scan for jobs
    if hasattr(bot, 'platform_scanners'):
        print("\n🔍 Scanning platforms for opportunities...")
        opportunities = bot.platform_scanners.scan_all_platforms()
        
        print(f"\n   Found {len(opportunities)} matching opportunities:")
        for i, opp in enumerate(opportunities[:3], 1):
            print(f"\n   {i}. {opp.title}")
            print(f"      Platform: {opp.platform.value}")
            print(f"      Match Score: {opp.match_score:.0f}%")
            print(f"      Client: {opp.client_info.get('company', 'Individual')}")
        
        if opportunities:
            selected_job = opportunities[0]
            
            print("\n" + "─"*70)
            print("STEP 3: CLIENT RESEARCH")
            print("─"*70)
            
            if hasattr(bot, 'client_researcher'):
                client = bot.client_researcher.research_client(
                    selected_job.client_info.get('company', 'Client'),
                    selected_job.platform.value,
                    selected_job.client_info
                )
                
                quality = bot.client_researcher.assess_client_quality(client)
                print(f"\n   Client: {client.name}")
                print(f"   Rating: {client.rating or 'N/A'}/5.0")
                print(f"   Quality Score: {quality['quality_score']:.0f}/100")
                print(f"   Risk: {quality['risk_level']}")
                print(f"   Recommendation: {quality['recommendation']}")
            
            print("\n" + "─"*70)
            print("STEP 4: PROPOSAL GENERATION")
            print("─"*70)
            
            if hasattr(bot, 'proposal_generator'):
                job_data = {
                    'id': selected_job.job_id,
                    'title': selected_job.title,
                    'description': selected_job.description,
                    'client_name': selected_job.client_info.get('company', 'Client'),
                    'skills': selected_job.skills,
                    'platform': selected_job.platform.value,
                    'client_info': selected_job.client_info
                }
                
                proposal = bot.proposal_generator.generate_proposal(
                    job_data, 
                    selected_job.platform.value
                )
                
                print("\n   Proposal for:", proposal.client_name)
                print(f"   Proposed Rate: ${proposal.proposed_rate.get('suggested_hourly', 0)}/hr")
                print(f"   Estimated Hours: {proposal.estimated_hours}")
                print("\n   Preview:")
                print("   " + "-"*40)
                print(f"   {proposal.content[:300]}...")
                
                # Queue for review
                bot.proposal_generator.queue_for_review(proposal)
                print("\n   ⏳ Proposal queued for human approval")
            
            print("\n" + "─"*70)
            print("STEP 5: JOB EXECUTION SIMULATION (If Won)")
            print("─"*70)
            
            if hasattr(bot, 'job_execution_orchestrator'):
                # Start hypothetical job
                job = bot.job_execution_orchestrator.start_job(
                    job_id=f"job_{selected_job.job_id}",
                    requirements=selected_job.description,
                    client=selected_job.client_info.get('company', 'Client')
                )
                
                print(f"\n   Job started: {job['job_id']}")
                print(f"   Client: {job['client']}")
                print(f"   Tasks created: {len(job.get('tasks', []))}")
                
                print("\n   📋 Tasks Breakdown:")
                for task in job.get('tasks', [])[:5]:
                    print(f"      - {task.get('description')} ({task.get('estimated_hours')}h)")
                
                # Simulate execution phases
                print("\n   🔧 Executing phases:")
                for phase in ["research", "design", "implementation", "testing"]:
                    print(f"      → {phase.capitalize()}... ✓")
                
                status = bot.job_execution_orchestrator.get_job_status(job['job_id'])
                print(f"\n   Current Status: {status['status']}")
            
            print("\n" + "─"*70)
            print("STEP 6: CHECKPOINT REQUEST")
            print("─"*70)
            
            print("\n   ⏸️ HUMAN CHECKPOINT: Ready for review")
            print("   Artifacts: Implementation complete, test suite ready")
            print("   Action required: Approve for client delivery")
            print("   [Approve] [Request Changes] [Abort]")
    
    print("\n" + "="*70)
    print("✅ DEMO COMPLETE")
    print("="*70)
    
    # Summary
    print("\n📊 SUMMARY:")
    print("   • Job scouting: Automated across platforms")
    print("   • Client research: Background validation")
    print("   • Proposal: Auto-generated, human-approved")
    print("   • Execution: Phase-based with checkpoints")
    print("   • Delivery: Human-gated final approval")
    
    print("\n🎯 Human-in-the-loop checkpoints:")
    print("   1. ✅ Proposal review (before sending)")
    print("   2. ✅ Requirements confirmation")
    print("   3. ✅ Design approval")
    print("   4. ✅ Final delivery approval")
    
    return bot


def demonstrate_individual_modules():
    """Demonstrate each module individually."""
    print("\n" + "="*70)
    print("INDIVIDUAL MODULE DEMOS")
    print("="*70)
    
    bot = Omnibot()
    
    # Proactive Engine
    print("\n📱 PROACTIVE ENGINE")
    if hasattr(bot, 'proactive_engine'):
        bot.proactive_engine.record_activity("check_email", {"count": 5})
        suggestion = bot.proactive_engine.check_and_intervene()
        if suggestion:
            print(f"   Suggestion: {suggestion.title}")
        else:
            print("   No immediate suggestions")
    
    # Cost Optimizer
    print("\n💰 COST OPTIMIZER")
    if hasattr(bot, 'cost_optimizer'):
        bot.cost_optimizer.track_token_usage(
            provider="openai",
            model="gpt-4",
            input_tokens=1000,
            output_tokens=500,
            task_id="demo_task"
        )
        summary = bot.cost_optimizer.get_daily_summary()
        print(f"   Today's cost: ${summary['total_cost']:.4f}")
    
    # Autonomous Designer
    print("\n🎨 AUTONOMOUS DESIGNER")
    if hasattr(bot, 'autonomous_designer'):
        design_result = bot.autonomous_designer.design(
            project_type="fitness",
            context="Landing page for fitness tracking app"
        )
        print(f"   Concepts generated: {design_result['concepts_generated']}")
        print(f"   Selected concept: {design_result['selected_concept']}")
    
    # Safety Container
    print("\n🔒 SAFETY CONTAINER")
    if hasattr(bot, 'safety_container'):
        is_safe = bot.safety_container.validate_file_path(
            "/home/skux/.openclaw/workspace/test.py"
        )
        print(f"   Path validation: {'Safe' if is_safe else 'Blocked'}")
    
    # Secret Scanner
    print("\n🔐 SECRET SCANNER")
    if hasattr(bot, 'secret_scanner'):
        test_content = "api_key = 'sk-test123456789'"
        scan_result = bot.secret_scanner.scan(test_content)
        if scan_result:
            print(f"   Detected: {len(scan_result)} secret(s)")
            for finding in scan_result:
                print(f"      - {finding['type']}: {finding['match']}")
        else:
            print("   No secrets detected")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    print("\n🚀 Starting Omnibot Autonomous Demo\n")
    
    # Run main demo
    demo_job_discovery()
    
    # Run individual demos
    demonstrate_individual_modules()
    
    print("\n✨ All demos complete!")