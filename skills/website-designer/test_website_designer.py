#!/usr/bin/env python3
"""
Test the website designer skill
"""
import sys
import os
import shutil

# Add parent directory to path
sys.path.insert(0, '/home/skux/.openclaw/workspace/skills/website-designer')

import website_designer

def test_create():
    """Test creating a website"""
    print("Testing: Create website")
    print("-" * 50)
    
    # Clean up old test
    test_dir = "test_website"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    
    # Create
    result = website_designer.create_website(test_dir, "business")
    
    # Verify
    assert os.path.exists(test_dir), "Site directory not created"
    assert os.path.exists(f"{test_dir}/site.json"), "site.json not created"
    assert os.path.exists(f"{test_dir}/src/index.html"), "index.html not created"
    assert os.path.exists(f"{test_dir}/src/css/main.css"), "main.css not created"
    assert os.path.exists(f"{test_dir}/security.conf"), "security.conf not created"
    
    print("\n✅ Test: CREATE PASSED")
    
    # Cleanup
    shutil.rmtree(test_dir)
    print(f"  Cleanup: removed {test_dir}/")
    
    return True

def test_cli():
    """Test CLI commands"""
    print("\nTesting: CLI")
    print("-" * 50)
    
    import subprocess
    
    result = subprocess.run(
        ["python3", "/home/skux/.openclaw/workspace/skills/website-designer/website_designer.py"],
        capture_output=True,
        text=True
    )
    
    assert "Usage:" in result.stdout or "Usage:" in result.stderr, "Help message not shown"
    
    print("✅ Test: CLI PASSED")
    
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("  Website Designer Test Suite")
    print("=" * 50)
    print()
    
    tests = [test_create, test_cli]
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"❌ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ ERROR: {e}")
            failed += 1
    
    print()
    print("=" * 50)
    print(f"  Tests: {passed} passed, {failed} failed")
    print("=" * 50)
