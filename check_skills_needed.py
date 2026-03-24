#!/usr/bin/env python3
"""
🔍 SKILL ACTIVATION ANALYSIS
Skill: skill-activation-manager (SAM)
Method: Analyze current context, identify dormant skills, suggest activations

Current Context: Live trading systems (LuxTrader v3.0 + Holy Trinity)
Goal: Identify which skills would enhance this setup
"""

import json
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/home/skux/.openclaw/workspace")

def analyze_skill_needs():
    """
    SAM Analysis: What skills would enhance live trading?
    """
    
    print("="*80)
    print("🔍 SKILL ACTIVATION MANAGER (SAM) - CONTEXTUAL ANALYSIS")
    print("="*80)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Current Context: Live Trading System (LIVE MODE)")
    print(f"Systems: LuxTrader v3.0 + Holy Trinity")
    print("="*80)
    
    # Current situation analysis
    print("\n📊 CURRENT SITUATION ANALYSIS")
    print("-"*80)
    
    context = {
        "mode": "LIVE trading",
        "systems": ["LuxTrader v3.0", "Holy Trinity"],
        "capital": "2.01 SOL",
        "status": "Monitoring AOE scanner",
        "risk_level": "HIGH (real money)",
        "active": True,
        "needs_monitoring": True,
        "needs_alerts": True,
        "needs_tracking": True
    }
    
    for k, v in context.items():
        print(f"  {k}: {v}")
    
    # Skill gap analysis
    print("\n🔍 SKILL GAP ANALYSIS")
    print("-"*80)
    
    # Analyze what skills would help
    skill_recommendations = []
    
    # 1. Monitoring needs
    skill_recommendations.append({
        "skill": "kpi-performance-tracker",
        "relevance": "HIGH",
        "reason": "Live trading needs real-time KPI monitoring",
        "use_case": "Track win rates, PnL, drawdown in real-time",
        "dormant": True,
        "suggested_action": "Activate to monitor trading performance"
    })
    
    # 2. Safety needs
    skill_recommendations.append({
        "skill": "autonomous-maintenance-repair",
        "relevance": "CRITICAL",
        "reason": "Live system needs self-healing if errors occur",
        "use_case": "Auto-restart failed agents, fix corrupted state",
        "dormant": False,  # Was used for bug test
        "suggested_action": "Already used - keep monitoring"
    })
    
    # 3. Alert needs (user requested no email, but other alerts)
    skill_recommendations.append({
        "skill": "sensory-input-layer",
        "relevance": "MEDIUM",
        "reason": "Monitor external data sources (Discord, Telegram, Twitter)",
        "use_case": "Detect alpha from social channels",
        "dormant": True,
        "suggested_action": "Connect to trading signals"
    })
    
    # 4. Pattern learning
    skill_recommendations.append({
        "skill": "aloe",
        "relevance": "HIGH",
        "reason": "Track trade outcomes, learn patterns",
        "use_case": "After trades complete, analyze what worked",
        "dormant": False,  # Active
        "suggested_action": "Already learning from trades"
    })
    
    # 5. Decision tracking
    skill_recommendations.append({
        "skill": "decision-log",
        "relevance": "MEDIUM",
        "reason": "Important decisions being made (MODE changes, entry/exit)",
        "use_case": "Log why trades were taken or skipped",
        "dormant": True,
        "suggested_action": "Log the switch to LIVE mode decision"
    })
    
    # 6. Code evolution
    skill_recommendations.append({
        "skill": "code-evolution-tracker",
        "relevance": "MEDIUM",
        "reason": "Trading code will evolve based on results",
        "use_case": "Track improvements to strategies",
        "dormant": False,  # Active
        "suggested_action": "Already tracking - continue"
    })
    
    # 7. Business strategy
    skill_recommendations.append({
        "skill": "business-strategy-engine",
        "relevance": "LOW",
        "reason": "Small scale - not business-level yet",
        "use_case": "When trading scales to serious capital",
        "dormant": True,
        "suggested_action": "Not needed at current scale"
    })
    
    # 8. Long-term project
    skill_recommendations.append({
        "skill": "long-term-project-manager",
        "relevance": "HIGH",
        "reason": "This is an ongoing project with phases",
        "use_case": "Track v3.0 → v3.1 → v4.0 evolution roadmap",
        "dormant": True,
        "suggested_action": "Create trading evolution roadmap"
    })
    
    # 9. Research
    skill_recommendations.append({
        "skill": "research-synthesizer",
        "relevance": "MEDIUM",
        "reason": "Constantly researching new strategies, tokens, narratives",
        "use_case": "Research alpha sources, compare strategies",
        "dormant": True,
        "suggested_action": "Activate for strategy research"
    })
    
    # 10. Multi-agent
    skill_recommendations.append({
        "skill": "multi-agent-coordinator",
        "relevance": "HIGH",
        "reason": "Already running 2 agents in parallel",
        "use_case": "Coordinate LuxTrader + Holy Trinity execution",
        "dormant": False,  # Active
        "suggested_action": "Already used - maintain coordination"
    })
    
    # Display recommendations
    print("\n📋 SKILL RECOMMENDATIONS")
    print("-"*80)
    
    for rec in sorted(skill_recommendations, key=lambda x: x['relevance'], reverse=True):
        status = "🟢 ACTIVE" if not rec['dormant'] else "🔴 DORMANT"
        print(f"\n{rec['relevance']} | {rec['skill']} [{status}]")
        print(f"    Why: {rec['reason']}")
        print(f"    Use: {rec['use_case']}")
        print(f"    Action: {rec['suggested_action']}")
    
    # Priority summary
    print("\n" + "="*80)
    print("🎯 PRIORITY ACTIVATIONS")
    print("="*80)
    
    critical = [r for r in skill_recommendations if r['relevance'] == 'CRITICAL' and r['dormant']]
    high = [r for r in skill_recommendations if r['relevance'] == 'HIGH' and r['dormant']]
    medium = [r for r in skill_recommendations if r['relevance'] == 'MEDIUM' and r['dormant']]
    
    print(f"\n🔴 CRITICAL (needs activation): {len(critical)}")
    for r in critical:
        print(f"   - {r['skill']}")
        
    print(f"\n🟠 HIGH (recommended): {len(high)}")
    for r in high:
        print(f"   - {r['skill']}")
        
    print(f"\n🟡 MEDIUM (optional): {len(medium)}")
    for r in medium:
        print(f"   - {r['skill']}")
    
    # SAM recommendations
    print("\n" + "="*80)
    print("💡 SAM CONTEXTUAL PROMPTS")
    print("="*80)
    
    prompts = [
        {
            "trigger": "Trading for 1+ hours",
            "skill": "kpi-performance-tracker",
            "prompt": "Want me to track real-time trading KPIs? Win rate, PnL trends, drawdown monitoring?"
        },
        {
            "trigger": "Made important decision",
            "skill": "decision-log",
            "prompt": "Should we log the decision to switch to LIVE mode? For future reference?"
        },
        {
            "trigger": "Long-term project",
            "skill": "long-term-project-manager",
            "prompt": "This trading system is evolving. Want to create a roadmap for v3.0 → v4.0?"
        },
        {
            "trigger": "Need market research",
            "skill": "research-synthesizer",
            "prompt": "Want me to research other Solana trading strategies? Compare approaches?"
        }
    ]
    
    for p in prompts:
        print(f"\n📌 Trigger: {p['trigger']}")
        print(f"   Skill: {p['skill']}")
        print(f"   Prompt: {p['prompt']}")
        print(f"   Action: [Activate] [Skip]")
    
    return skill_recommendations


def generate_summary(recommendations):
    """Generate summary report"""
    
    print("\n" + "="*80)
    print("📊 SKILL ACTIVATION SUMMARY")
    print("="*80)
    
    active = len([r for r in recommendations if not r['dormant']])
    dormant = len([r for r in recommendations if r['dormant']])
    critical = len([r for r in recommendations if r['relevance'] == 'CRITICAL' and r['dormant']])
    
    print(f"\nTotal Skills Analyzed: {len(recommendations)}")
    print(f"  🟢 Active: {active}")
    print(f"  🔴 Dormant: {dormant}")
    print(f"  🔴 Critical dormant: {critical}")
    
    print("\n" + "="*80)
    print("✅ ANALYSIS COMPLETE")
    print("="*80)
    print("\nNext Steps:")
    print("  1. Consider activating kpi-performance-tracker for live monitoring")
    print("  2. Log the LIVE mode decision in decision-log")
    print("  3. Create trading evolution roadmap with long-term-project-manager")
    print("  4. Continue using multi-agent-coordinator for execution")
    print("\nSkills are tools - use them when the context fits!")
    print("="*80)


def main():
    recommendations = analyze_skill_needs()
    generate_summary(recommendations)
    
    # Save report
    report = {
        "timestamp": datetime.now().isoformat(),
        "context": "Live Trading Systems",
        "recommendations": recommendations
    }
    
    WORKSPACE.mkdir(exist_ok=True)
    report_file = WORKSPACE / "agents/lux_trader/skill_activation_analysis.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Report saved: {report_file}")


if __name__ == "__main__":
    main()
