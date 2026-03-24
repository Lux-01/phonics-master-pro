# ACA Code Patterns

## Pre-Code Checklist

### Requirements Phase
- [ ] What problem does this solve?
- [ ] Who is the user?
- [ ] What are the inputs?
- [ ] What are the outputs?
- [ ] What defines success?
- [ ] What defines failure?

### Architecture Phase
- [ ] Single responsibility (one thing well)
- [ ] Clear module boundaries
- [ ] Data flow diagram drawn
- [ ] State management decided
- [ ] External dependencies identified

### Edge Cases Phase
- [ ] Empty inputs handled
- [ ] Maximum input size handled
- [ ] Invalid inputs handled
- [ ] Concurrent access handled (if applicable)
- [ ] Timeout scenarios handled
- [ ] API failure scenarios handled

### Error Handling Phase
- [ ] Try/except around every external call
- [ ] Specific exception types caught
- [ ] Fallback behavior specified
- [ ] Error logged appropriately
- [ ] User-friendly error messages

### Testing Phase
- [ ] Happy path test identified
- [ ] Edge case tests identified
- [ ] Error tests identified
- [ ] Mock strategy decided
- [ ] Expected outputs documented

## Common Code Patterns

### Pattern 1: Defensive Input Validation

```python
# BEFORE (fragile)
def process_token(token):
    return fetch_data(token)

# AFTER (robust)
def process_token(token):
    # Validate input
    if not token:
        raise ValueError("Token required")
    
    if not isinstance(token, str):
        raise TypeError("Token must be string")
    
    if len(token) != 44:  # Solana address length
        raise ValueError("Invalid token address length")
    
    try:
        return fetch_data(token)
    except Exception as e:
        logger.error(f"Failed to process {token}: {e}")
        raise
```

### Pattern 2: Circuit Breaker (API Fallback)

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=3):
        self.failures = 0
        self.threshold = failure_threshold
        self.is_open = False
    
    def call(self, func, *args, **kwargs):
        if self.is_open:
            raise Exception("Circuit breaker open")
        
        try:
            result = func(*args, **kwargs)
            self.failures = 0
            return result
        except Exception as e:
            self.failures += 1
            if self.failures >= self.threshold:
                self.is_open = True
            raise
```

### Pattern 3: Result Type (Explicit Errors)

```python
from typing import Optional
from dataclasses import dataclass

@dataclass
class Result:
    success: bool
    data: Optional[dict]
    error: Optional[str]
    metadata: dict

def fetch_price_safe(token) -> Result:
    try:
        price = fetch_price(token)
        return Result(
            success=True,
            data=price,
            error=None,
            metadata={"source": "jupiter", "timestamp": time()}
        )
    except Exception as e:
        return Result(
            success=False,
            data=None,
            error=str(e),
            metadata={"attempted": True}
        )

# Usage
result = fetch_price_safe("SOL")
if result.success:
    print(result.data)
else:
    print(f"Error: {result.error}")
```

### Pattern 4: Retry with Backoff

```python
import time
from functools import wraps

def retry(max_attempts=3, backoff=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(backoff ** attempt)
            return None
        return wrapper
    return decorator

@retry(max_attempts=3, backoff=2)
def fetch_api_data(url):
    return requests.get(url)
```

### Pattern 5: Context Managers (Resource Safety)

```python
# BEFORE
file = open("data.txt")
data = file.read()
# Might forget to close!

# AFTER
with open("data.txt") as file:
    data = file.read()
# Auto-closed, even on error

# Custom context manager
from contextlib import contextmanager

@contextmanager
def timed_operation(name):
    start = time.time()
    try:
        yield
    finally:
        duration = time.time() - start
        logger.info(f"{name} took {duration:.2f}s")

with timed_operation("API call"):
    response = api.fetch()
```

## Self-Debug Checklist

### Static Analysis
- [ ] All variables defined before use
- [ ] No unused imports
- [ ] No unused variables
- [ ] Consistent naming
- [ ] Proper indentation
- [ ] No syntax errors

### Logic Analysis
- [ ] All paths return expected type
- [ ] No infinite loops
- [ ] No division by zero
- [ ] No index out of bounds
- [ ] Proper boolean logic
- [ ] Switch/if-else coverage complete

### API Analysis
- [ ] All API calls wrapped in try/except
- [ ] API parameters validated
- [ ] Return values checked before use
- [ ] Expected response structure documented
- [ ] Rate limits respected
- [ ] Timeouts specified

### Security Analysis
- [ ] No SQL injection vectors
- [ ] Input sanitized
- [ ] No hardcoded secrets
- [ ] Privilege principle respected
- [ ] Sensitive data logged carefully

## Testing Templates

### Template 1: Happy Path

```python
def test_function_name_happy_path():
    """Basic functionality works with valid inputs."""
    # Setup
    input_data = create_valid_input()
    
    # Execute
    result = function_name(input_data)
    
    # Assert
    assert result is not None
    assert result.status == "success"
    assert "expected_field" in result
```

### Template 2: Edge Cases

```python
def test_function_name_edge_cases():
    """Edge cases handled gracefully."""
    edge_cases = [
        None,
        "",
        [],
        0,
        -1,
        9999999,  # Very large
        {"empty": "dict"},
    ]
    
    for case in edge_cases:
        result = function_name(case)
        # Should not crash
        assert result is not None or isinstance(result, Exception)
```

### Template 3: Errors

```python
def test_function_name_api_failure():
    """API failures handled gracefully."""
    with patch('module.api_call') as mock:
        mock.side_effect = Exception("API down")
        
        result = function_name("input")
        
        assert result.status == "error"
        assert "API" in result.error_message
```

## Error Handling Patterns

```python
# DON'T: Catch all
except Exception as e:
    pass  # Silent failure - dangerous

# DO: Specific exceptions
from requests.exceptions import (
    ConnectionError,
    Timeout,
    HTTPError,
    TooManyRedirects
)

try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
except ConnectionError:
    logger.error("Network unavailable")
    return fallback_to_cache()
except Timeout:
    logger.error("Request timeout")
    return retry_later()
except HTTPError as e:
    if e.response.status_code == 429:
        logger.warning("Rate limited")
        return wait_and_retry()
    raise
```

## Documentation Standards

```python
def function_name(
    param1: str,
    param2: int,
    optional_param: Optional[str] = None
) -> dict:
    """
    Brief description of what this function does.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        optional_param: Optional parameter description
    
    Returns:
        Dictionary with:
        - status: 'success' or 'error'
        - data: Result payload (if success)
        - error: Error message (if failed)
    
    Raises:
        ValueError: If param1 is invalid
        APIException: If API call fails
    
    Example:
        >>> result = function_name("test", 42)
        >>> print(result['status'])
        'success'
    """
```

## Version Control Best Practices

### Commit Messages

```
Format: ACTION: Component - Description

Examples:
✓ ADD: Token fetcher - Jupiter integration
✓ FIX: Timeout handling - Handle 30s timeout
✓ UPDATE: Caching logic - Reduce TTL to 5min
✓ REFACTOR: Price module - Extract validation
✓ TEST: Token fetcher - Add edge case tests
✓ DOCS: API module - Add usage examples

BAD:
✗ "fix stuff"
✗ "updates"
✗ "work in progress"
```

### Semantic Versioning

```
MAJOR.MINOR.PATCH

MAJOR: Incompatible API changes
MINOR: New functionality, backwards compatible
PATCH: Bug fixes, backwards compatible

Examples:
v1.0.0 - Initial release
v1.1.0 - Added caching
v1.1.1 - Fixed timeout bug
v2.0.0 - Breaking change: new API
```

## ACA Mode Activation

When activated, ACA forces this workflow:

```
1. REQUIREMENTS (cannot proceed until complete)
2. ARCHITECTURE (cannot proceed until complete)
3. DATA FLOW (cannot proceed until complete)
4. EDGE CASES (must have at least 5)
5. TOOL CONSTRAINTS (must document limits)
6. ERROR HANDLING (80% coverage required)
7. TESTING PLAN (must have happy + edge + error tests)
     ↓
8. SELF-DEBUG (analyze before writing code)
     ↓
9. CODE GENERATION (structured by plan)
     ↓
10. TEST GENERATION (auto-generate from plan)
     ↓
11. VALIDATION (mental execution)
     ↓
12. VERSIONING (snapshot before deploy)
     ↓
DEPLOY
```

**Cannot skip steps.** This is the engineering discipline.
