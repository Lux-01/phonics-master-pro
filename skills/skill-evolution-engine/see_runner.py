#!/usr/bin/env python3
"""
SEE Runner - Quick test wrapper for Skill Evolution Engine
"""

import subprocess
import sys

def test_see():
    """Run SEE in automatic mode."""
    result = subprocess.run(
        ["python3", "/home/skux/.openclaw/workspace/skills/skill-evolution-engine/skill_evolution_engine.py", "--automatic"],
        capture_output=True,
        text=True
    )
    print("SEE Output:")
    print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
    if result.returncode == 0:
        print("✓ SEE execution successful")
    else:
        print(f"✗ SEE failed: {result.stderr}")

if __name__ == "__main__":
    test_see()
