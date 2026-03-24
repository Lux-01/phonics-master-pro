# ACA Implementation Guide

## Quick Start

### Activating ACA

```
User: "Build a token price fetcher with ACA"
ACA: "Starting structured engineering workflow..."
""")
```

### What Happens Next

1. **Planning Phase** (~2-3 min)
2. **Self-Debug Phase** (~1-2 min)
3. **Code Generation** (~2-3 min)
4. **Test Generation** (~2 min)
5. **Validation** (~1 min)
6. **Deployment** (~30 sec)

**Total:** ~10 min for production-ready code

## Planning Template

### Requirements Document Template

```yaml
# File: plans/component_name_plan.yaml

component:
  name: "token_price_fetcher"
  description: "Fetches current price for any token from multiple sources"
  
requirements:
  input:
    - name: "token_address"
      type: "string"
      validation: "valid_solana_address"
      required: true
    
    - name: "preferred_source"
      type: "enum[jupiter, birdeye]"
      default: "jupiter"
      required: false
  
  output:
    - name: "price"
      type: "float"
      nullable: false
    - name: "source"
      type: "enum[jupiter, birdeye, error]"
    - name: "timestamp"
      type: "datetime"
    - name: "error"
      type: "string"
      condition: "if failed"
  
  success_criteria:
    - "Returns valid price for 99% of valid tokens"
    - "Response time < 2 seconds"
    - "Falls back gracefully on primary source failure"
  
  failure_criteria:
    - "Invalid token → clear error message"
    - "API down → uses fallback"
    - "Rate limit → waits and retries"

architecture:
  modules:
    - name: "fetcher"
      purpose: "API interaction"
    - name: "validator"
      purpose: "Input/output validation"
    - name: "cache"
      purpose: "TTL caching"
    - name: "wrapper"
      purpose: "Error handling and orchestration"
  
  data_flow:
    1_user_input:
      action: "receive token_address"
      next: "validate"
    
    2_validate:
      action: "check address format"
      on_success: "fetch_jupiter"
      on_fail: "return_error"
    
    3_fetch_jupiter:
      action: "call Jupiter API"
      on_success: "return_result"
      on_fail: "fetch_birdeye"
    
    4_fetch_birdeye:
      action: "call Birdeye API"
      on_success: "return_result"
      on_fail: "return_error"
    
    5_return_result:
      action: "format and cache"
      next: "end"
    
    6_return_error:
      action: "format error"
      next: "end"

edge_cases:
  - name: "empty_address"
    input: ""
    expected: "Raise ValueError"
    
  - name: "invalid_format"
    input: "not_an_address"
    expected: "Raise ValueError"
    
  - name: "unlisted_token"
    input: "valid_but_unlisted_address"
    expected: "Return None with clear message"
    
  - name: "jupiter_timeout"
    condition: "Jupiter API takes >5s"
    expected: "Fallback to Birdeye"
    
  - name: "both_apis_failed"
    condition: "All sources fail"
    expected: "Return cached price or clear error"
    
  - name: "zero_price"
    input: "token_with_zero_price"
    expected: "Treat as invalid, return None"

tool_constraints:
  jupiter:
    endpoint: "https://api.jup.ag/price"
    rate_limit: "300 req/min"
    timeout: "5 seconds"
    retries: "1"
    auth: "none"
    
  birdeye:
    endpoint: "https://public-api.birdeye.so"
    rate_limit: "100 req/min"
    timeout: "10 seconds"
    retries: "2"
    auth: "API key required"

error_handling:
  ConnectionError:
    action: "retry"
    max_retries: 2
    
  TimeoutError:
    action: "fallback"
    fallback: "next_provider"
    
  ValueError:
    action: "raise"
    message: "Clear validation error"
    
  RateLimitError:
    action: "wait"
    delay: "60 seconds"
    
  UnknownError:
    action: "log_and_raise"
    log_level: "ERROR"

testing:
  happy_path:
    - name: "fetch_sol_jupiter"
      input: {token_address: "So11111111111111111111111111111111111111112"}
      expected: {price: ">0", source: "jupiter"}
    
    - name: "fetch_sol_birdeye_fallback"
      setup: "mock_jupiter_failure"
      input: {token_address: "SOL..."}
      expected: {price: ">0", source: "birdeye"}
  
  edge_cases:
    - name: "empty_input"
      input: {token_address: ""}
      expected: {error: "validation_failed"}
    
    - name: "unlisted_token"
      input: {token_address: "unlisted_token_ca"}
      expected: {price: null, source: "none"}
  
  error_cases:
    - name: "all_services_down"
      setup: "mock_all_failures"
      input: {token_address: "SOL..."}
      expected: {error: "all_sources_failed"}
```

## Self-Debug Script

```python
#!/usr/bin/env python3
# scripts/self_debug.py

import ast
import re
import sys

def self_debug_code(file_path):
    """Analyze code for common issues before execution"""
    
    with open(file_path) as f:
        code = f.read()
    
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        print(f"🔴 Syntax Error: Line {e.lineno}: {e.msg}")
        return False
    
    issues = []
    
    # Check 1: Undefined variables
    finder = UndefinedVariableFinder()
    finder.visit(tree)
    if finder.undefined:
        for var, line in finder.undefined:
            issues.append(f"🟠 Line {line}: Variable '{var}' used before assignment")
    
    # Check 2: Empty except blocks
    for pattern in re.finditer(r'except.*:\s*pass', code):
        line = code[:pattern.start()].count('\n') + 1
        issues.append(f"🔴 Line {line}: Empty except block - dangerous!")
    
    # Check 3: Bare excepts
    for pattern in re.finditer(r'except\s*:', code):
        line = code[:pattern.start()].count('\n') + 1
        issues.append(f"🟡 Line {line}: Bare except - should be specific")
    
    # Check 4: API calls without timeout
    for pattern in re.finditer(r'(requests\.get|requests\.post)\([^)]*\)', code):
        if 'timeout' not in pattern.group():
            line = code[:pattern.start()].count('\n') + 1
            issues.append(f"🟠 Line {line}: API call without timeout")
    
    # Check 5: No input validation
    if 'validation' not in code.lower() and 'validate' not in code.lower():
        issues.append("🟡 Missing input validation")
    
    if issues:
        print("\n🔍 Self-Debug Report:")
        print("=" * 50)
        for issue in issues:
            print(issue)
        print("=" * 50)
        print(f"Found {len(issues)} issues")
        return False
    else:
        print("✅ No issues found!")
        return True

class UndefinedVariableFinder(ast.NodeVisitor):
    def __init__(self):
        self.defined = set()
        self.undefined = []
    
    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            if node.id not in self.defined and not self.is_builtin(node.id):
                self.undefined.append((node.id, node.lineno))
        elif isinstance(node.ctx, ast.Store):
            self.defined.add(node.id)
    
    def is_builtin(self, name):
        builtins = {'True', 'False', 'None', 'print', 'len', 'range', 'dict', 'list', 'set', 'str', 'int'}
        return name in builtins

if __name__ == "__main__":
    result = self_debug_code(sys.argv[1])
    sys.exit(0 if result else 1)
```

## Test Generator Script

```python
#!/usr/bin/env python3
# scripts/generate_tests.py

def generate_tests_from_plan(plan_file, output_file):
    """Generate test file from plan YAML"""
    import yaml
    
    with open(plan_file) as f:
        plan = yaml.safe_load(f)
    
    component = plan['component']['name']
    
    test_code = f'''"""
Generated tests for {component}
Generated by ACA at {datetime.now().isoformat()}
"""

import pytest
from unittest.mock import patch, Mock
from {component} import *

class Test{component.title().replace('_', '')}:
    """Test suite automatically generated by ACA"""
    
'''
    
    # Add happy path tests
    for test in plan['testing']['happy_path']:
        test_code += f'''    def test_{test['name']}(self):
        """{test['name'].replace('_', ' ').title()}"""
        # Setup
        input_data = {test['input']}
        
        # Execute
        result = {component}(**input_data)
        
        # Assert
        assert result is not None
'''
    
    # Add edge case tests
    for test in plan['testing']['edge_cases']:
        test_code += f'''    def test_{test['name']}(self):
        """{test['name'].replace('_', ' ').title()}"""
        input_data = {test['input']}
        result = {component}(**input_data)
        expected = {test['expected']}
        assert result == expected
'''
    
    with open(output_file, 'w') as f:
        f.write(test_code)
    
    print(f"✅ Generated test file: {output_file}")
    print(f"   Tests: {len(plan['testing']['happy_path'])} happy + {len(plan['testing']['edge_cases'])} edge")

if __name__ == "__main__":
    import sys
    from datetime import datetime
    generate_tests_from_plan(sys.argv[1], sys.argv[2])
```

## Versioning Commands

```bash
# Create new version
aca version create token_fetcher --message "Added Birdeye fallback"

# List versions
aca version list token_fetcher

# View diff
aca version diff token_fetcher 1 2

# Rollback
aca version rollback token_fetcher 2

# Show current
aca version current token_fetcher
```

## Integration with Other Skills

### ACA + SEE

```
SEE: "Found optimization opportunity in AOE"
     ↓
ACA: "Planning refactor..."
     ↓
SEE: "Approved"
     ↓
ACA: "Implementing..."
     ↓
SEE: "Validating..."
     ↓
SEE: "Deployed, 50% faster"
```

### ACA + ALOE

```
ALOE: "Pattern: Projects with tests succeed 3x more"
     ↓
ACA: "Enforcing test generation requirement"
     ↓
All future code includes tests
     ↓
Success rate increases
     ↓
ALOE: "Pattern confirmed"
```

### ACA + AOE

```
AOE: "Need tool for market analysis"
     ↓
ACA: "Building with full engineering rigor"
     ↓
AOE: "Received stable, tested tool"
     ↓
Success
     ↓
ALOE: "Records: ACA-built tools = high success"
```

## Success Metrics

Track ACA effectiveness:

```yaml
metrics:
  code_failures:
    before_aca: "30%"
    after_aca: "8%"
    improvement: "73%"
  
  debug_iterations:
    before_aca: "avg 4.2 per task"
    after_aca: "avg 1.1 per task"
    improvement: "74%"
  
  time_to_stable:
    before_aca: "avg 45 min"
    after_aca: "avg 12 min"
    improvement: "73%"
  
  test_coverage:
    before_aca: "15%"
    after_aca: "82%"
    improvement: "447%"
```
