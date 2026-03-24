---
name: testing-automation
description: Auto-discover, test, and report on all skills. Validates code quality, dependencies, and functionality.
---

# Testing Automation Skill

Comprehensive testing automation for the OpenClaw skill ecosystem.

## Overview

Automatically validates all skills in the workspace, generating detailed reports and suggesting fixes for common issues.

### What It Tests

1. **Structure Validation** - Does the skill have required files?
2. **Import/Dependency Checks** - Can all modules be imported?
3. **Unit Tests** - Runs tests if test/ folder exists
4. **Integration Tests** - Tests skills working together
5. **Code Quality** - Basic linting and style checks

## Installation

```bash
# No installation needed - self-contained Python
cd /home/skux/.openclaw/workspace/skills/testing-automation
python3 -m core.skill_discoverer  # Quick test
```

## Usage

### CLI

```bash
# Run all tests
python3 run_tests.py

# Run specific test types
python3 run_tests.py --type structure
python3 run_tests.py --type imports
python3 run_tests.py --type unit

# Auto-fix issues
python3 run_tests.py --fix

# Generate report only
python3 run_tests.py --report-only
```

### API

```python
from skills.testing_automation import TestRunner

runner = TestRunner()
results = runner.run_all_tests()

# Check specific skill
skill_result = runner.test_skill("universal-memory-system")

# Generate report
from core.report_generator import ReportGenerator
generator = ReportGenerator(results)
report = generator.generate_markdown()
```

## Test Types

### Structure Tests
- SKILL.md exists
- __init__.py present (if Python)
- Required directories exist
- Configuration files valid

### Import Tests
- All Python modules importable
- No circular dependencies
- Required packages available

### Unit Tests
- Runs tests/ folder contents
- Captures pass/fail and output
- Measures coverage if available

### Integration Tests
- Tests skill interactions
- Validates shared interfaces
- Checks for conflicts

## Output

### Console Output
```
🧪 Running Tests on 47 skills...

✅ universal-memory-system - PASS (5/5 tests)
✅ safety-engine - PASS (4/5 tests)
⚠️  proactive-monitor - WARN (3/5 tests, import errors)
❌ pattern-extractor - FAIL (2/5 tests)

📊 Summary: 44/47 passed, 2 warnings, 1 failure
```

### Report Files
- `testing_report.md` - Human-readable report
- `testing_report.json` - Machine-readable results
- `test_coverage.html` - Coverage visualization (if generated)

## Auto-Fix Capabilities

The auto-fixer can resolve:
- Missing __init__.py files
- Import path issues (common patterns)
- Missing SKILL.md (generates template)
- Broken relative imports

Manual review required for:
- Logic errors
- Architectural issues
- Complex dependency conflicts

## Configuration

Create `.testing_config.json` in skill directory for custom settings:

```json
{
  "exclude_modules": ["legacy_script.py"],
  "skip_tests": ["slow_integration_test"],
  "required_packages": ["numpy", "requests"],
  "minimum_coverage": 60
}
```

## Performance

- Typical runtime: 30-60 seconds for 50 skills
- Parallel testing on supported systems
- Incremental testing available

## CI Integration

```yaml
name: Skill Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run skill tests
        run: python3 skills/testing-automation/run_tests.py --fail-fast
```

## Files

- `core/skill_discoverer.py` - Find and categorize skills
- `core/test_runner.py` - Execute tests
- `core/report_generator.py` - Create reports
- `core/auto_fixer.py` - Fix common issues
- `run_tests.py` - Main entry point
- `tests/` - Self-tests

## Troubleshooting

**Test fails with import error**
- Check PYTHONPATH includes skills/
- Verify dependencies installed

**Skills not discovered**
- Ensure directory in /skills/
- Check directory permissions

**Auto-fix doesn't work**
- Review permissions on skill files
- Some fixes require manual review

---

Built with ACA methodology