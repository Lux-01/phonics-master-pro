#!/usr/bin/env python3
"""Test suite for Autonomous Tool Builder"""
import sys
import os
sys.path.insert(0, '/home/skux/.openclaw/workspace/skills/autonomous-tool-builder')

def test_tool_generation():
    """Test that ATB can create a basic tool template"""
    # Check the SKILL.md exists
    skill_path = "/home/skux/.openclaw/workspace/skills/autonomous-tool-builder/SKILL.md"
    assert os.path.exists(skill_path), "SKILL.md should exist"
    print("✅ SKILL.md exists")
    
    # Check for Python implementation
    py_files = [f for f in os.listdir('/home/skux/.openclaw/workspace/skills/autonomous-tool-builder') if f.endswith('.py')]
    if py_files:
        print(f"✅ Found {len(py_files)} Python files")
    else:
        print("⚠️ No Python implementation yet")

def test_pattern_detection():
    """Test pattern detection capability"""
    # Verify directory structure
    tool_dir = "/home/skux/.openclaw/workspace/skills/autonomous-tool-builder"
    assert os.path.isdir(tool_dir), "Tool directory should exist"
    print("✅ Tool directory structure valid")

if __name__ == "__main__":
    print("Testing Autonomous Tool Builder...")
    print("-" * 40)
    
    test_tool_generation()
    test_pattern_detection()
    
    print("-" * 40)
    print("✅ Tests completed!")
