#!/usr/bin/env python3
"""Test suite for KPI Performance Tracker"""
import sys
import os
sys.path.insert(0, '/home/skux/.openclaw/workspace/skills/kpi-performance-tracker')

def test_skill_structure():
    """Test basic skill structure"""
    skill_dir = "/home/skux/.openclaw/workspace/skills/kpi-performance-tracker"
    assert os.path.isdir(skill_dir), "Skill directory exists"
    
    # Check SKILL.md
    skill_md = os.path.join(skill_dir, "SKILL.md")
    assert os.path.exists(skill_md), "SKILL.md exists"
    print("✅ Skill structure valid")

def test_kpi_categories():
    """Test that KPI categories are defined"""
    skill_md = "/home/skux/.openclaw/workspace/skills/kpi-performance-tracker/SKILL.md"
    with open(skill_md) as f:
        content = f.read()
    
    assert "Skills" in content
    assert "Business" in content
    assert "System" in content
    print("✅ KPI categories defined")

if __name__ == "__main__":
    print("Testing KPI Tracker...")
    print("-" * 40)
    
    test_skill_structure()
    test_kpi_categories()
    
    print("-" * 40)
    print("✅ Tests completed!")
