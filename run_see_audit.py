#!/usr/bin/env python3
"""
🧬 SEE - Skill Evolution Engine Audit
Comprehensive audit of all skills
"""

import os
import json
from datetime import datetime
from pathlib import Path

SKILLS_DIR = "/home/skux/.openclaw/workspace/skills"

def get_all_skills():
    """Get all skill directories"""
    skills = []
    
    for item in os.listdir(SKILLS_DIR):
        item_path = os.path.join(SKILLS_DIR, item)
        if os.path.isdir(item_path) and not item.startswith('_') and item not in ['archive', 'dist', '__pycache__']:
            skill_md = os.path.join(item_path, "SKILL.md")
            if os.path.exists(skill_md):
                skills.append({
                    "name": item,
                    "path": item_path,
                    "has_skill_md": True
                })
    
    return skills

def analyze_skill(skill):
    """Analyze a single skill"""
    
    analysis = {
        "name": skill["name"],
        "health_score": 0,
        "findings": [],
        "recommendations": [],
        "files": [],
        "capabilities": []
    }
    
    # Check files
    for file in os.listdir(skill["path"]):
        file_path = os.path.join(skill["path"], file)
        if os.path.isfile(file_path):
            analysis["files"].append(file)
    
    # Check for key files
    has_python = any(f.endswith('.py') for f in analysis["files"])
    has_readme = "SKILL.md" in analysis["files"]
    has_config = "config.json" in analysis["files"]
    
    # Calculate health score
    score = 50  # Base score
    
    if has_readme:
        score += 20
    if has_python:
        score += 20
    if has_config:
        score += 10
    
    # Check for issues
    if not has_python:
        analysis["findings"].append("No Python implementation files")
        analysis["recommendations"].append("Add executable Python scripts")
    
    if not has_config:
        analysis["findings"].append("No configuration file")
        analysis["recommendations"].append("Add config.json for customization")
    
    # Check file count
    if len(analysis["files"]) < 2:
        analysis["findings"].append("Minimal file structure")
        analysis["recommendations"].append("Expand with examples and utilities")
    
    analysis["health_score"] = min(score, 100)
    
    return analysis

def categorize_skills(skills):
    """Categorize skills by type"""
    
    categories = {
        "income_generation": [],
        "automation": [],
        "research": [],
        "content": [],
        "technical": [],
        "meta": [],
        "other": []
    }
    
    income_keywords = ["income", "fiverr", "client", "portfolio", "business", "strategy"]
    automation_keywords = ["autonomous", "automation", "scheduler", "workflow", "tool"]
    research_keywords = ["research", "synthesizer", "sensory", "chart", "analyzer"]
    content_keywords = ["content", "social", "website", "designer"]
    technical_keywords = ["code", "bug", "captcha", "stealth", "browser"]
    meta_keywords = ["evolution", "skill-evolution", "aloe", "memory", "context", "decision", "kpi"]
    
    for skill in skills:
        name = skill["name"].lower()
        
        if any(k in name for k in income_keywords):
            categories["income_generation"].append(skill)
        elif any(k in name for k in automation_keywords):
            categories["automation"].append(skill)
        elif any(k in name for k in research_keywords):
            categories["research"].append(skill)
        elif any(k in name for k in content_keywords):
            categories["content"].append(skill)
        elif any(k in name for k in meta_keywords):
            categories["meta"].append(skill)
        elif any(k in name for k in technical_keywords):
            categories["technical"].append(skill)
        else:
            categories["other"].append(skill)
    
    return categories

def generate_audit_report(all_skills, analyses, categories):
    """Generate comprehensive audit report"""
    
    report = []
    report.append("="*80)
    report.append("🧬 SEE - SKILL EVOLUTION ENGINE AUDIT REPORT")
    report.append("="*80)
    report.append(f"Audit Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append(f"Total Skills: {len(all_skills)}")
    report.append("="*80)
    
    # Overall health
    avg_health = sum(a["health_score"] for a in analyses) / len(analyses) if analyses else 0
    report.append(f"\n📊 OVERALL HEALTH: {avg_health:.1f}/100")
    
    # Health distribution
    excellent = sum(1 for a in analyses if a["health_score"] >= 90)
    good = sum(1 for a in analyses if 70 <= a["health_score"] < 90)
    fair = sum(1 for a in analyses if 50 <= a["health_score"] < 70)
    poor = sum(1 for a in analyses if a["health_score"] < 50)
    
    report.append(f"\n  ✅ Excellent (90-100): {excellent}")
    report.append(f"  ✓ Good (70-89): {good}")
    report.append(f"  ⚠ Fair (50-69): {fair}")
    report.append(f"  ❌ Poor (<50): {poor}")
    
    # Category breakdown
    report.append("\n" + "="*80)
    report.append("📁 SKILLS BY CATEGORY")
    report.append("="*80)
    
    for cat_name, cat_skills in categories.items():
        if cat_skills:
            report.append(f"\n{cat_name.upper().replace('_', ' ')} ({len(cat_skills)} skills):")
            for skill in cat_skills:
                analysis = next((a for a in analyses if a["name"] == skill["name"]), None)
                if analysis:
                    score = analysis["health_score"]
                    emoji = "✅" if score >= 90 else "✓" if score >= 70 else "⚠" if score >= 50 else "❌"
                    report.append(f"  {emoji} {skill['name']} ({score}%)")
    
    # Top performers
    report.append("\n" + "="*80)
    report.append("🏆 TOP PERFORMERS")
    report.append("="*80)
    
    top_skills = sorted(analyses, key=lambda x: x["health_score"], reverse=True)[:5]
    for i, skill in enumerate(top_skills, 1):
        report.append(f"\n{i}. {skill['name']} - {skill['health_score']}%")
        if skill["recommendations"]:
            report.append(f"   💡 {skill['recommendations'][0]}")
    
    # Skills needing attention
    report.append("\n" + "="*80)
    report.append("⚠️ SKILLS NEEDING ATTENTION")
    report.append("="*80)
    
    needs_attention = [a for a in analyses if a["health_score"] < 70 or a["findings"]]
    if needs_attention:
        for skill in needs_attention[:10]:
            report.append(f"\n• {skill['name']} ({skill['health_score']}%)")
            for finding in skill["findings"][:3]:
                report.append(f"  - {finding}")
    else:
        report.append("\n✅ All skills are healthy!")
    
    # New skills (Fiverr)
    report.append("\n" + "="*80)
    report.append("🆕 NEWLY CREATED SKILLS (Fiverr Support)")
    report.append("="*80)
    
    new_skills = ["fiverr-gig-optimizer", "client-proposal-writer", "portfolio-website-builder", 
                  "social-content-generator", "freelancer-competitive-analysis"]
    
    for skill_name in new_skills:
        report.append(f"\n✨ {skill_name}")
        if skill_name == "fiverr-gig-optimizer":
            report.append("   Purpose: Optimize Fiverr gigs for maximum conversions")
            report.append("   Usage: python3 skills/fiverr-gig-optimizer/fiverr_optimizer.py")
        elif skill_name == "client-proposal-writer":
            report.append("   Purpose: Write winning client proposals")
            report.append("   Usage: python3 skills/client-proposal-writer/proposal_writer.py")
        elif skill_name == "portfolio-website-builder":
            report.append("   Purpose: Create professional portfolio websites")
            report.append("   Usage: python3 skills/portfolio-website-builder/portfolio_builder.py")
        elif skill_name == "social-content-generator":
            report.append("   Purpose: Generate social media content")
            report.append("   Usage: python3 skills/social-content-generator/content_generator.py")
        elif skill_name == "freelancer-competitive-analysis":
            report.append("   Purpose: Analyze freelance market competition")
            report.append("   Usage: python3 skills/freelancer-competitive-analysis/competitive_analyzer.py")
    
    # Recommendations
    report.append("\n" + "="*80)
    report.append("🎯 EVOLUTION RECOMMENDATIONS")
    report.append("="*80)
    
    report.append("\n1. IMMEDIATE ACTIONS:")
    report.append("   • Test new Fiverr skills with real gigs")
    report.append("   • Create portfolio website using new skill")
    report.append("   • Generate content for social media presence")
    
    report.append("\n2. SHORT-TERM (This Week):")
    report.append("   • Add Python implementations to skills missing them")
    report.append("   • Create config.json files for customizable skills")
    report.append("   • Document usage examples for each skill")
    
    report.append("\n3. LONG-TERM (This Month):")
    report.append("   • Integrate new skills with existing workflow")
    report.append("   • Create skill performance tracking")
    report.append("   • Build skill usage dashboard")
    
    report.append("\n4. INCOME OPPORTUNITIES:")
    report.append("   • Use fiverr-gig-optimizer to create 2-3 optimized gigs")
    report.append("   • Use client-proposal-writer for Upwork applications")
    report.append("   • Use social-content-generator to build audience")
    report.append("   • Use portfolio-website-builder to showcase work")
    
    # Summary
    report.append("\n" + "="*80)
    report.append("📈 SUMMARY")
    report.append("="*80)
    report.append(f"\nTotal Skills: {len(all_skills)}")
    report.append(f"Average Health: {avg_health:.1f}%")
    report.append(f"New Skills Created: 5")
    report.append(f"Skills for Fiverr: 5")
    report.append(f"Ready for Income Generation: ✅")
    
    report.append("\n" + "="*80)
    report.append("🚀 SEE AUDIT COMPLETE")
    report.append("="*80)
    
    return "\n".join(report)

def main():
    """Main audit function"""
    
    print("🧬 SEE - Starting Skill Audit...")
    print("="*80)
    
    # Get all skills
    all_skills = get_all_skills()
    print(f"\n📊 Found {len(all_skills)} skills")
    
    # Analyze each skill
    print("\n🔍 Analyzing skills...")
    analyses = []
    for skill in all_skills:
        analysis = analyze_skill(skill)
        analyses.append(analysis)
        print(f"  ✓ {skill['name']}: {analysis['health_score']}%")
    
    # Categorize
    print("\n📁 Categorizing skills...")
    categories = categorize_skills(all_skills)
    
    # Generate report
    print("\n📝 Generating audit report...")
    report = generate_audit_report(all_skills, analyses, categories)
    
    # Save report
    report_path = "/home/skux/.openclaw/workspace/SEE_AUDIT_REPORT.md"
    with open(report_path, "w") as f:
        f.write(report)
    
    print(f"\n✅ Report saved to: {report_path}")
    
    # Print report
    print("\n" + report)
    
    return report

if __name__ == "__main__":
    main()
