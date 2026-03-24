#!/usr/bin/env python3
"""Test suite for Business Strategy Engine"""
import sys
import os
sys.path.insert(0, '/home/skux/.openclaw/workspace/skills/business-strategy-engine')

def test_skill_exists():
    """Test BSE skill structure"""
    skill_dir = "/home/skux/.openclaw/workspace/skills/business-strategy-engine"
    assert os.path.isdir(skill_dir)
    
    skill_md = os.path.join(skill_dir, "SKILL.md")
    assert os.path.exists(skill_md)
    print("✅ BSE skill exists")

def test_capabilities():
    """Test that capabilities are documented"""
    skill_md = "/home/skux/.openclaw/workspace/skills/business-strategy-engine/SKILL.md"
    with open(skill_md) as f:
        content = f.read()
    
    assert "Revenue" in content
    assert "Strategy" in content
    assert "Growth" in content
    print("✅ Capabilities documented")

if __name__ == "__main__":
    print("Testing Business Strategy Engine...")
    print("-" * 40)
    
    test_skill_exists()
    test_capabilities()
    
    print("-" * 40)
    print("✅ Tests completed!")
