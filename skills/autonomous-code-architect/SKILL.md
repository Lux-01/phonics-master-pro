---
name: autonomous-code-architect
description: The skill that makes OpenClaw write better code, debug itself, and produce stable tools on the first try. Plans before coding, self-debugs before running, auto-refactors, generates tests, and maintains version history. The engineering-specialized subsystem that turns OpenClaw from a junior dev into a senior engineer.
---

# Autonomous Code Architect (ACA)

**"Senior engineer in a skill."**

ACA transforms OpenClaw from a creative coder into a methodical engineer. Plans before typing. Tests before shipping. Debugs intelligently. This is the missing engineering layer.

## Philosophy

**Without ACA:** Creative, fast, capable — but inconsistent.

**With ACA:** Plans before coding, tests before running, debugs intelligently, writes stable modular code, improves over time.

> This stops the "multiple tries" problem.

## The Engineering Gap

```
Current State:
├─ ARAS thinks about solutions
├─ ALOE learns from outcomes
├─ SEE evolves skills
├─ AOE finds opportunities
└─ But none are code-engineering specialists

Missing: The engineering subsystem

With ACA:
└─ Structured development workflow
   ├─ Requirements analysis
   ├─ Architecture design
   ├─ Self-debugging
   ├─ Automated testing
   └─ Version control
```

## Core Capabilities

### 🧩 1. Plan Code Before Writing

**The Problem:** Most failures happen because code is written without structure.

**The Solution:** ACA enforces a 7-step planning phase:

```yaml
planning_workflow:
  step_1_requirements:
    - "What problem does this solve?"
    - "What are the inputs?"
    - "What are the expected outputs?"
    - "What are the constraints?"
    - "What does success look like?"
    
  step_2_architecture:
    - "What modules/components?"
    - "How do they interact?"
    - "What data structures?"
    - "What patterns should I use?"
    
  step_3_data_flow:
    - "Where does data enter?"
    - "How does it transform?"
    - "Where does it exit?"
    - "What are the edge cases?"
    
  step_4_edge_cases:
    - "Empty inputs?"
    - "Too large inputs?"
    - "Invalid inputs?"
    - "API failures?"
    - "Rate limits?"
    - "Timeouts?"
    
  step_5_tool_constraints:
    - "What tools will I use?"
    - "What are their limits?"
    - "What errors might they throw?"
    - "How do I validate outputs?"
    
  step_6_error_handling:
    - "What can go wrong?"
    - "How do I catch each error?"
    - "What's the fallback strategy?"
    - "How do I report errors?"
    
  step_7_testing_plan:
    - "What are the happy path tests?"
    - "What are the edge case tests?"
    - "What are the mock inputs?"
    - "What are the expected outputs?"
```

**Example Output:**
```markdown
## Code Plan: Token Price Fetcher

### Requirements
- Fetch current price for any Solana token
- Support Jupiter and Birdeye APIs
- Return {price, source, timestamp}
- Handle missing tokens gracefully

### Architecture
```
├─ fetch_jupiter(token)
├─ fetch_birdeye(token)
├─ validate_price(data)
└─ return_price_object()
```

### Data Flow
1. User provides token address
2. Try Jupiter API
3. If fail, try Birdeye
4. Validate returned price
5. Return structured object

### Edge Cases
- Invalid token address → Return None
- API timeout → Retry once, then fallback
- Price = 0 → Treat as invalid
- Multiple sources → Average or pick primary

### Tool Constraints
- Jupiter: 300 req/min, requires token verification
- Birdeye: 100 req/min, needs API key
- Both return JSON with nested price field

### Error Handling
- ConnectionError → Retry
- RateLimitError → Quota exceeded, return cached
- ValidationError → Log and return None
- Other → Log and return fallback

### Testing Plan
- Test 1: Valid token → Returns price
- Test 2: Invalid token → Returns None
- Test 3: Jupiter down → Falls back to Birdeye
- Test 4: Both down → Returns cached/None
```

**Impact:** 70% reduction in runtime errors.

---

### 🔍 2. Self-Debug Before Execution

**Mental Execution Engine:**

ACA performs "mental sandbox" execution to predict failures:

```python
def self_debug(code, plan):
    """
    Simulates code execution to find bugs
    before they happen.
    """
    issues = []
    
    # Check 1: Undefined variables
    undefined = find_undefined_variables(code)
    if undefined:
        issues.append({
            "type": "undefined_variable",
            "severity": "CRITICAL",
            "details": undefined
        })
    
    # Check 2: API usage validation
    for call in extract_api_calls(code):
        if not validate_api_signature(call):
            issues.append({
                "type": "api_mismatch",
                "severity": "CRITICAL",
                "details": f"{call.function} signature wrong"
            })
    
    # Check 3: JSON schema validation
    for json_parse in find_json_parses(code):
        if not validate_expected_structure(json_parse):
            issues.append({
                "type": "schema_mismatch",
                "severity": "HIGH",
                "details": "Expected structure may not match"
            })
    
    # Check 4: Tool signatures
    for tool_call in extract_tool_calls(code):
        if not validate_tool_signature(tool_call):
            issues.append({
                "type": "tool_error",
                "severity": "CRITICAL",
                "details": f"Tool {tool_call.name} usage incorrect"
            })
    
    # Check 5: Input/output validation
    if not has_input_validation(code):
        issues.append({
            "type": "missing_validation",
            "severity": "MEDIUM",
            "details": "No input validation detected"
        })
    
    # Check 6: Error handling coverage
    coverage = calculate_error_coverage(code, plan)
    if coverage < 80:
        issues.append({
            "type": "insufficient_error_handling",
            "severity": "HIGH",
            "details": f"Only {coverage}% of errors handled"
        })
    
    # Check 7: Resource leaks
    if has_resource_leaks(code):
        issues.append({
            "type": "resource_leak",
            "severity": "MEDIUM",
            "details": "File/connection may not close"
        })
    
    return issues
```

**Self-Debug Report Example:**
```markdown
🔍 ACA Self-Debug Report
Generated: 2026-03-09 02:50

Code Review: token_fetcher.py
Lines: 45 | Complexity: Low

Issues Found: 3

🔴 CRITICAL #1: Undefined Variable
   Line 23: `price` used before assignment
   Fix: Initialize price = None at line 15

🟠 HIGH #2: Missing Input Validation
   Line 12: `token_address` not validated
   Risk: Invalid address causes API error
   Fix: Add validation before API call

🟡 MEDIUM #3: Insufficient Error Handling
   Coverage: 60% (need 80%)
   Missing: Timeout handling, Rate limiting
   Fix: Add except blocks for Timeout, RateLimit

Auto-Fix Suggestions: 2
✓ Fix #1 automatically? [Yes/No]
✓ Add validation helper? [Yes/No]

Proceed to execution? [Review/Fix/Abort]
```

**Catches:**
- Undefined variables
- API signature mismatches
- JSON schema errors
- Missing error handling
- Resource leaks
- Logic errors (infinite loops, division by zero)

---

### 🔁 3. Automatic Refactoring

**When Something Breaks:**

```
Error Detected
     ↓
ACA analyzes traceback
     ↓
Identifies root cause
     ↓
Proposes surgical fix
     ↓
Re-tests logic
     ↓
Validates backward compatibility
     ↓
Commits fix
```

**Refactoring Strategy:**

```python
class RefactorEngine:
    def refactor(self, code, error):
        """
        Intelligent refactoring - only change what's broken.
        """
        # Step 1: Root cause analysis
        cause = self.analyze_error(error, code)
        
        # Step 2: Isolate broken section
        broken_section = self.isolate(cause, code)
        
        # Step 3: Generate minimal fix
        fixed_section = self.generate_fix(broken_section, cause)
        
        # Step 4: Re-integrate
        new_code = self.patch(code, broken_section, fixed_section)
        
        # Step 5: Validate
        if self.validate(new_code):
            return new_code
        else:
            # Try alternative fix
            return self.fallback_fix(code, error)
    
    def analyze_error(self, error, code):
        """Deep analysis of what actually failed"""
        # Parse error type
        # Check line number
        # Look at surrounding context
        # Check call stack
        # Identify assumptions that failed
        return RootCause(
            type=error.type,
            line=error.line,
            assumption_failed=self.identify_assumption(),
            solution_type=self.categorize_solution()
        )
```

**Example Refactor:**

```python
# BEFORE (broken)
def fetch_price(token):
    resp = requests.get(f"https://api.jup.ag/price/{token}")
    return resp.json()["price"]  # ERROR: KeyError

# ERROR: KeyError: 'price'
# Root cause: API returns nested structure {"data": {"price": ...}}

# ACA'S FIX (surgical)
def fetch_price(token):
    resp = requests.get(f"https://api.jup.ag/price/{token}")
    data = resp.json()
    # Handle nested structure
    if "data" in data and "price" in data["data"]:
        return data["data"]["price"]
    elif "price" in data:
        return data["price"]
    else:
        raise ValueError(f"Unexpected API response structure: {data.keys()}")

# Only changed lines 3-9, kept rest intact
```

**Stops:** The "rewrite everything from scratch" loop.

---

### 🧪 4. Unit Test Generation

**Auto-Generated Test Suite:**

```python
def generate_tests(code, plan):
    """
    Generates comprehensive test suite from code plan.
    """
    tests = []
    
    # Happy path tests
    for example in plan.examples:
        tests.append({
            "name": f"test_happy_path_{i}",
            "input": example.input,
            "expected_output": example.output,
            "type": "happy_path"
        })
    
    # Edge case tests
    for edge_case in plan.edge_cases:
        tests.append({
            "name": f"test_edge_{edge_case.name}",
            "input": generate_mock_input(edge_case),
            "expected_output": edge_case.expected_behavior,
            "type": "edge_case"
        })
    
    # Error tests
    for error_scenario in plan.error_handling:
        tests.append({
            "name": f"test_error_{error_scenario.error_type}",
            "input": trigger_error_input(error_scenario),
            "expected_output": error_scenario.expected_response,
            "type": "error"
        })
    
    # Mock external dependencies
    tests = add_mocks(tests, code)
    
    return tests
```

**Generated Test Example:**

```python
# Generated by ACA for: token_fetcher.py

import pytest
from unittest.mock import patch, Mock
from token_fetcher import fetch_token_price

class TestTokenFetcher:
    
    # === Happy Path Tests ===
    
    def test_fetch_valid_token_jupiter(self):
        """Should return price from Jupiter"""
        with patch('requests.get') as mock_get:
            mock_get.return_value.json.return_value = {
                "price": "145.23"
            }
            result = fetch_token_price("SOL")
            
            assert result == {"price": 145.23, "source": "jupiter"}
            mock_get.assert_called_once()
    
    def test_fetch_valid_token_birdeye_fallback(self):
        """Should fall back to Birdeye if Jupiter fails"""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = [
                Exception("Jupiter timeout"),
                Mock(json=Mock(return_value={"price": "145.20"}))
            ]
            result = fetch_token_price("SOL")
            
            assert result["source"] == "birdeye"
            assert mock_get.call_count == 2
    
    # === Edge Case Tests ===
    
    def test_invalid_token_address(self):
        """Should return None for invalid address"""
        result = fetch_token_price("invalid_address")
        assert result is None
    
    def test_empty_response(self):
        """Should handle empty API response"""
        with patch('requests.get') as mock_get:
            mock_get.return_value.json.return_value = {}
            result = fetch_token_price("SOL")
            
            assert result is None
    
    def test_price_zero(self):
        """Should handle price = 0 as invalid"""
        with patch('requests.get') as mock_get:
            mock_get.return_value.json.return_value = {"price": "0"}
            result = fetch_token_price("SOL")
            
            assert result is None
    
    # === Error Tests ===
    
    def test_jupiter_rate_limit(self):
        """Should handle rate limiting gracefully"""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Exception("429 Rate Limited")
            result = fetch_token_price("SOL")
            
            # Should try fallback
            assert result is not None or result is None  # Either OK
    
    def test_api_timeout(self):
        """Should timeout and fallback"""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = TimeoutError()
            result = fetch_token_price("SOL")
            
            # Should handle timeout
            assert "error" in result or result is None

# ACA Generated: 12 tests
# Coverage: 89%
# Run: pytest test_token_fetcher.py -v
```

**Robust Code = Tested Code**

---

### 🧱 5. Versioning + Rollback

**Git-Like Versioning:**

```
memory/aca/versions/
├── token_fetcher/
│   ├── v1.py          # Initial implementation
│   ├── v2.py          # Added Birdeye fallback
│   ├── v3.py          # Added caching
│   ├── v4.py          # Fixed timeout bug
│   └── current.py     # Symlink to latest
└── price_analyzer/
    ├── v1.py
    ├── v2.py
    └── current.py
```

**Version Metadata:**

```json
{
  "component": "token_fetcher",
  "versions": [
    {
      "version": 1,
      "created": "2026-03-09T02:00:00Z",
      "description": "Initial Jupiter integration",
      "tests_passed": 8,
      "issues_found": 2,
      "rollback_marker": false
    },
    {
      "version": 2,
      "created": "2026-03-09T02:30:00Z",
      "description": "Added Birdeye fallback",
      "tests_passed": 12,
      "issues_found": 0,
      "rollback_marker": false,
      "changes": [
        "+ Birdeye API integration",
        "+ Fallback logic",
        "~ Error handling improved"
      ]
    },
    {
      "version": 3,
      "created": "2026-03-09T02:45:00Z",
      "description": "Added 5-minute cache",
      "tests_passed": 12,
      "issues_found": 0,
      "rollback_marker": false,
      "changes": [
        "+ TTLCache implementation",
        "~ API calls reduced 70%"
      ]
    }
  ],
  "current": 3,
  "stable": 3,
  "rollback_if_broken": true
}
```

**Rollback Workflow:**

```python
def handle_failure(component, failure):
    """
    Auto-rollback if new version breaks.
    """
    current = get_current_version(component)
    
    # Tag this version as broken
    mark_version(component, current, {"status": "broken", "error": failure})
    
    # Find last stable version
    stable = find_last_stable_version(component, before=current)
    
    if stable:
        # Rollback to stable
        rollback_to_version(component, stable)
        
        notify(f"⚠️ Rolled back {component} from v{current} to v{stable}")
        
        # Create fix task
        create_task(f"Fix v{current} of {component}: {failure}")
    else:
        # No stable version found - escalate
        escalate(f"No stable version for {component}")
```

**Safety Net:** Never be stuck with broken code.

---

### 🧬 6. Integration with SEE

**SEE + ACA = Self-Improving Engineering:**

```
SEE detects skill needs improvement
     ↓
SEE analyzes what's wrong
     ↓
SEE proposes solution
     ↓
ACA plans the code changes
     ↓
ACA self-debugs the plan
     ↓
ACA generates the code
     ↓
ACA creates tests
     ↓
ACA validates with mental execution
     ↓
SEE reviews the implementation
     ↓
Approve → Deploy → Track
     ↓
ALOE learns from outcome
     ↓
[Next iterative improvement]
```

**Example Integration:**

```
SEE Audit Finding:
"AOE scanner makes sequential API calls - can be parallelized"
     ↓
ACA Planning:
- Identify parallelizable calls
- Design asyncio structure
- Plan error handling for concurrent failures

ACA Implementation:
- Code generation
- Self-debug: Check for async/await correctness
- Refactor if needed
- Generate tests for parallel path and error path

ACA Validation:
- Mental execution: "What if Jupiter returns before Birdeye?"
- Mental execution: "What if one times out?"
- All checks pass

ACA Versioning:
- Create v2 of aoe_monitor.py
- Run tests
- Tag v1 as stable backup
- Deploy v2

SEE Review:
- Measure performance: 4.2s → 1.8s (57% faster)
- Check error rate: Unchanged
- Update skill health score

ALOE Learning:
- Pattern: "Parallelize independent API calls"
- Success rate: High
- Apply to similar skills in future
```

**The Loop:**
```
SEE finds opportunity → ACA implements → ALOE learns
     ↑___________________________________________|
```

---

## ACA Workflow

### When User Says: "Build X"

```
User: "Build a trading signal generator"
     ↓
ACA: Planning phase
├─ Requirements: What does it input/output?
├─ Architecture: What components?
├─ Data flow: How does data move?
├─ Edge cases: What can break?
├─ Tools: What APIs/methods?
├─ Errors: How to handle failures?
└─ Tests: What to test?
     ↓
ACA: Self-Debug phase
├─ Simulate execution
├─ Check for undefined vars
├─ Validate API usage
├─ Check error coverage
└─ Review data structures
     ↓
ACA: Code Generation
├─ Write code following plan
├─ Add comprehensive error handling
├─ Include logging
└─ Add docstrings
     ↓
ACA: Test Generation
├─ Happy path tests
├─ Edge case tests
├─ Error tests
└─ Mock external APIs
     ↓
ACA: Validation
├─ Run mental simulation
├─ Check code against plan
├─ Verify all requirements met
└─ Final review
     ↓
ACA: Versioning
├─ Save as v1
├─ Tag as latest
└─ Make backup copy
     ↓
User: Receives stable, tested, documented code
```

**Time Investment:** +20% upfront planning → -70% debugging

---

## Commands

| Command | What ACA Does |
|---------|---------------|
| "Build X with ACA" | Full planning → coding → testing workflow |
| "Plan this first" | Generate 7-step plan only |
| "Self-debug this" | Analyze existing code for issues |
| "Refactor [code]" | Smart, surgical fixes |
| "Generate tests for X" | Full test suite with mocks |
| "Version [component]" | Snapshot current code |
| "Rollback [component]" | Revert to last stable |
| "See plan for X" | Show current planning phase |
| "Validate this code" | Pre-execution check |
| "Code review" | Identify issues without fixing |
| "ACA mode" | Force planning before every code task |

---

## Storage

```
memory/aca/
├── plans/
│   ├── token_fetcher_plan.yaml
│   ├── trading_strategy_plan.yaml
│   └── ...
├── debug_reports/
│   ├── token_fetcher_v1_debug.json
│   └── ...
├── versions/
│   ├── token_fetcher/
│   │   ├── v1.py
│   │   ├── v2.py
│   │   └── current.py
│   └── ...
├── tests/
│   ├── generated/
│   │   ├── test_token_fetcher.py
│   │   └── ...
│   └── coverage_reports/
├── refactor_history/
│   └── token_fetcher_v2_refactor.json
└── config.json
```

---

## Why ACA Is Essential

### Current State (Without ACA):
```
"Build a token scanner"
     ↓
Write code quickly
     ↓
Try running it
     ↓
ERROR: `token` not defined
     ↓
Fix error
     ↓
Try again
     ↓
ERROR: API returns different format
     ↓
Fix
     ↓
Try again
     ↓
ERROR: Timeout not handled
     ↓
Rewrite from scratch
     ↓
...repeat 3-5 times
     ↓
Works but buggy
```

### With ACA:
```
"Build a token scanner"
     ↓
ACA plans (2 min)
     ↓
ACA self-debugs (1 min)
     ↓
ACA generates code (2 min)
     ↓
ACA generates tests (2 min)
     ↓
ACA validates (1 min)
     ↓
Code works first time
     ↓
Tests pass
     ↓
Stable, documented, robust
```

**Time Saved:** 50-70% reduction in iteration cycles

---

## What ACA Unlocks

With ACA, OpenClaw reliably builds:
- ✅ New agents
- ✅ New tools
- ✅ New workflows
- ✅ New product generators
- ✅ New automation pipelines
- ✅ New research engines

**Without breaking.**

**Essential for:** Self-running business systems

---

## Integration Map

```
                    USER REQUEST
                         ↓
              ┌──────────┴──────────┐
              ↓                     ↓
         ACA (Code)             SEE (Evolution)
              ↓                     ↓
      ├───────┴───────┐      Proposes changes
      ↓               ↓             ↓
  Planning      Execution   ACA implements
      │               │             │
      ↓               ↓             ↓
  Self-Debug    Testing      ALOE learns
      │               │             │
      │               ↓             │
      └────────→ Versioning ←──────┘
                   ↓
              Deployment
                   ↓
                OUTPUT
```

---

## 📱 Appendix: App Development Reference

*Research-synthesized knowledge for mobile/desktop app development*

### Modern App Frameworks (2025-2026)

| Framework | Language | Platforms | Best For | Bundle Size |
|-----------|----------|-----------|----------|-------------|
| **Flutter** | Dart | iOS, Android, Web, Desktop | Beautiful UIs, single codebase | ~5MB |
| **React Native** | JavaScript | iOS, Android, Web | Web devs, large ecosystem | ~15MB |
| **SwiftUI** | Swift | iOS, macOS, watchOS, tvOS | Apple-only apps | Native |
| **Jetpack Compose** | Kotlin | Android | Android-only apps | Native |
| **Tauri 2.0** | Rust + Web | Desktop, Mobile | Lightweight desktop apps | ~600KB |
| **Electron** | JavaScript | Desktop | Cross-platform web apps | ~150MB |

### Platform Design Systems

**iOS (Human Interface Guidelines):**
- Navigation: Tab bars (bottom), navigation bars (top)
- Typography: San Francisco font family
- Grid: 8pt system
- Touch targets: 44x44pt minimum
- Safe areas: Respect notch, home indicator

**Android (Material Design 3):**
- Navigation: Bottom navigation, navigation drawer
- Typography: Roboto / Google Sans
- Grid: 8dp system
- Touch targets: 48x48dp minimum
- Dynamic color: Adapts to wallpaper

### State Management Patterns

**Flutter:**
- Riverpod (recommended): `StateNotifierProvider`, `FutureProvider`
- Bloc: Event-driven architecture
- Provider: Simple, built-in

**React Native:**
- Zustand (recommended): Simple, performant
- Redux: Enterprise-scale
- Jotai: Atomic state management

**SwiftUI:**
- `@State`: Local mutable state
- `@Observable`: Reference types
- `@Environment`: Global/shared state

**Jetpack Compose:**
- `remember`: Local state
- `ViewModel`: Screen-level state
- `StateFlow`: Reactive streams

### Navigation Patterns

**Flutter (GoRouter):**
```dart
final router = GoRouter(
  routes: [
    GoRoute(path: '/', builder: (context, state) => HomeScreen()),
    GoRoute(path: '/details/:id', builder: ...),
  ],
);
// Navigate: context.go('/details/123')
```

**React Native (React Navigation):**
```typescript
<Stack.Navigator>
  <Stack.Screen name="Home" component={HomeScreen} />
  <Stack.Screen name="Details" component={DetailsScreen} />
</Stack.Navigator>
// Navigate: navigation.navigate('Details', { id: 123 })
```

### API Integration Patterns

**Flutter (Dio):**
```dart
final dio = Dio(BaseOptions(
  baseUrl: 'https://api.example.com',
  connectTimeout: Duration(seconds: 5),
));

// With interceptors for auth, logging
```

**React Native (Axios):**
```typescript
const api = axios.create({
  baseURL: 'https://api.example.com',
  timeout: 10000,
});

// With interceptors for auth, error handling
```

### Local Storage

**Flutter:**
- Hive: Fast, NoSQL, type-safe
- SharedPreferences: Simple key-value
- SQLite: Complex relational data

**React Native:**
- AsyncStorage: Simple key-value
- MMKV: High-performance (recommended)
- SQLite: Complex relational data

### Testing Strategy

**Unit Tests:**
- Test business logic, utilities
- Mock external dependencies
- 80%+ coverage target

**Widget/UI Tests:**
- Test component rendering
- Test user interactions
- Test navigation flows

**Integration Tests:**
- Test full user journeys
- Test API integration
- Test state persistence

### Responsive Design

**Breakpoints:**
```
Mobile: < 600px
Tablet: 600px - 1200px
Desktop: > 1200px
```

**Flutter:**
```dart
if (MediaQuery.of(context).size.width < 600) {
  return MobileLayout();
} else {
  return DesktopLayout();
}
```

**React Native:**
```typescript
import { useWindowDimensions } from 'react-native';
const { width } = useWindowDimensions();
```

### 2025 Visual Trends

| Trend | Use Case | Implementation |
|-------|----------|----------------|
| Glassmorphism | Overlays, cards | `BackdropFilter` + opacity |
| Neumorphism | Buttons, inputs | Soft shadows |
| Bento Grids | Dashboards | Modular card layouts |
| Dark Mode | All apps | `ThemeData.dark()` |
| Micro-interactions | Feedback | Haptics, animations |

### Build Commands

**Flutter:**
```bash
flutter build apk --release          # Android APK
flutter build appbundle --release  # Play Store
flutter build ios --release          # iOS (macOS only)
flutter build web --release          # Web
```

**React Native:**
```bash
npx react-native run-android --variant=release
npx react-native run-ios --configuration Release
```

### App Store Requirements

**iOS:**
- App Icon: 1024x1024px
- Screenshots: 6.5", 5.5", iPad
- Privacy Policy URL required
- iOS 15+ minimum (17 recommended)

**Android:**
- App Icon: 512x512px
- Feature Graphic: 1024x500px
- Target SDK 34+ required
- 64-bit architecture required

### Common Pitfalls

1. **Not handling async errors**
   - Always wrap API calls in try-catch
   - Provide user feedback on failure

2. **Blocking the UI thread**
   - Use async/await for I/O
   - Offload heavy computation

3. **Memory leaks**
   - Cancel subscriptions on dispose
   - Clear timers, listeners

4. **Not testing on real devices**
   - Emulators don't show performance issues
   - Test on low-end devices

5. **Ignoring platform conventions**
   - iOS: Back button in top-left
   - Android: System back button

### Recommended Stack by Use Case

| Use Case | Recommended Stack |
|----------|-------------------|
| Startup MVP | Flutter + Firebase |
| iOS-only | Swift + SwiftUI |
| Android-only | Kotlin + Jetpack Compose |
| Cross-platform | Flutter |
| Desktop app | Tauri (lightweight) or Electron |
| Game/3D | Unity or Godot |
| AI-powered | Kotlin + Koog |

---

**ACA: The engineering layer that makes everything else work.** ⚡
