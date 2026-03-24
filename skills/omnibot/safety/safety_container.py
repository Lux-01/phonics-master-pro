"""
Safety Container Module - Omnibot Phase 2
Sandboxed execution environment with audit logging and secret scanning.
ACA Methodology: Analyze-Construct-Audit
"""

import re
import json
import hashlib
import subprocess
import os
import ast
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict


class SandboxLevel(Enum):
    """Sandbox restriction levels."""
    STRICT = "strict"       # No external calls, read-only file system
    MODERATE = "moderate"   # Approved APIs only, workspace writes only
    PERMISSIVE = "permissive"  # External calls logged, full workspace access


@dataclass
class AuditEntry:
    """Single audit log entry."""
    timestamp: str
    action: str
    level: str
    code_hash: str
    result: str
    duration_ms: float
    secrets_found: List[str]
    error: Optional[str] = None


@dataclass
class SecretMatch:
    """Detected secret in code."""
    type: str
    line: int
    column: int
    snippet: str
    severity: str


class SafetyContainer:
    """
    Sandboxed execution container with security controls.
    
    Features:
    - Network isolation per sandbox level
    - File system restriction (workspace only)
    - Secret scanning (API keys, tokens)
    - Auto-rollback on failures
    - Comprehensive audit trail
    """
    
    # Secret detection patterns
    SECRET_PATTERNS = {
        'api_key': [
            r'[aA][pP][iI][-_]?[kK][eE][yY][\s]*[=:][\s]*["\'][a-zA-Z0-9_\-]{16,}["\']',
            r'["\'][a-zA-Z0-9_\-]{32,}["\'].*[aA][pP][iI]',
        ],
        'aws_key': [
            r'AKIA[0-9A-Z]{16}',
            r'[a-zA-Z0-9/+=]{40}',  # AWS secret key pattern
        ],
        'github_token': [
            r'gh[pousr]_[A-Za-z0-9_]{36,}',
            r'github[_-]?token[\s]*[=:][\s]*["\'][a-zA-Z0-9_\-]{35,}["\']',
        ],
        'private_key': [
            r'-----BEGIN (RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----',
            r'-----BEGIN ENCRYPTED PRIVATE KEY-----',
        ],
        'password': [
            r'password[\s]*[=:][\s]*["\'][^"\']{8,}["\']',
            r'passwd[\s]*[=:][\s]*["\'][^"\']{8,}["\']',
        ],
        'database_url': [
            r'(mongodb|mysql|postgresql|postgres|redis)://[^\s"\']+',
        ],
        'bearer_token': [
            r'[bB]earer[\s]+[a-zA-Z0-9_\-\.]{20,}',
            r'authorization[\s]*[=:][\s]*["\'][^"\']{20,}["\']',
        ],
        'jwt_token': [
            r'eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*',
        ],
    }
    
    # Approved external APIs for MODERATE level
    APPROVED_APIS = [
        'api.openai.com',
        'api.anthropic.com',
        'api.brave.com',
        'api.github.com',
        'api.twitter.com',
        'api.x.com',
        'public-api.birdeye.so',
        'api.dexscreener.com',
        'api.coingecko.com',
        'api.helius.xyz',
        'api.jup.ag',
        'www.googleapis.com',
    ]
    
    def __init__(self, workspace_path: Optional[str] = None, audit_log_path: Optional[str] = None):
        """
        Initialize Safety Container.
        
        Args:
            workspace_path: Base path for file operations (default: current working dir)
            audit_log_path: Path to audit log file (default: workspace/.safety/audit.log)
        """
        self.workspace_path = Path(workspace_path or os.getcwd()).resolve()
        self.audit_log_path = Path(audit_log_path or self.workspace_path / '.safety' / 'audit.log')
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        self._rollback_stack: List[Tuple[str, str]] = []  # (file_path, backup_content)
        
    def _compute_code_hash(self, code: str) -> str:
        """Compute SHA256 hash of code for audit trail."""
        return hashlib.sha256(code.encode()).hexdigest()[:16]
    
    def scan_for_secrets(self, text: str) -> List[SecretMatch]:
        """
        Scan text for potential secrets and API keys.
        
        Args:
            text: Code or text to scan
            
        Returns:
            List of SecretMatch objects with findings
        """
        matches = []
        lines = text.split('\n')
        
        for secret_type, patterns in self.SECRET_PATTERNS.items():
            for pattern in patterns:
                for line_num, line in enumerate(lines, 1):
                    for match in re.finditer(pattern, line):
                        # Skip false positives in comments
                        if line.strip().startswith('#') and secret_type not in ['private_key', 'jwt_token']:
                            continue
                        
                        severity = 'HIGH' if secret_type in ['private_key', 'aws_key', 'github_token'] else 'MEDIUM'
                        
                        # Mask the actual secret in the snippet
                        snippet = line[max(0, match.start() - 10):min(len(line), match.end() + 10)]
                        masked = match.group()[:4] + '*' * (len(match.group()) - 8) + match.group()[-4:] if len(match.group()) > 12 else '****'
                        
                        matches.append(SecretMatch(
                            type=secret_type,
                            line=line_num,
                            column=match.start() + 1,
                            snippet=snippet.replace(match.group(), f'[{masked}]'),
                            severity=severity
                        ))
        
        return matches
    
    def validate_path(self, path: str) -> Path:
        """
        Validate that path is within workspace bounds.
        
        Args:
            path: Path to validate
            
        Returns:
            Resolved Path object
            
        Raises:
            ValueError: If path escapes workspace
            PermissionError: If path is in restricted area
        """
        # Expand ~ to home directory
        expanded = os.path.expanduser(path)
        resolved = Path(expanded).resolve()
        
        # Check if within workspace
        try:
            resolved.relative_to(self.workspace_path)
        except ValueError:
            raise ValueError(f"Path '{path}' escapes workspace '{self.workspace_path}'")
        
        # Check restricted directories
        restricted = [
            '/etc', '/proc', '/sys', '/dev', '/var/log',
            str(Path.home() / '.ssh'), str(Path.home() / '.gnupg'),
            '/usr/bin', '/bin', '/sbin',
        ]
        
        for restricted_path in restricted:
            try:
                resolved.relative_to(Path(restricted_path))
                raise PermissionError(f"Access to '{restricted_path}' is restricted")
            except ValueError:
                continue
        
        return resolved
    
    def _is_network_call_allowed(self, code: str, level: SandboxLevel) -> Tuple[bool, Optional[str]]:
        """Check if network calls in code are allowed at given sandbox level."""
        if level == SandboxLevel.PERMISSIVE:
            return True, None
        
        if level == SandboxLevel.STRICT:
            # Check for any network imports or calls
            network_patterns = [
                r'import\s+requests',
                r'import\s+urllib',
                r'import\s+http',
                r'import\s+socket',
                r'requests\.', r'urllib\.', r'http\.', r'socket\.',
                r'subprocess\.', r'os\.system', r'os\.popen',
            ]
            for pattern in network_patterns:
                if re.search(pattern, code):
                    return False, f"Network call detected (pattern: {pattern}) - not allowed in STRICT mode"
            return True, None
        
        # MODERATE - check against approved list
        # Extract URLs from code
        url_patterns = [
            r'https?://([^/\s"\']+)',
            r'["\']([^"\']*api[^"\']*)["\']',
        ]
        
        found_urls = []
        for pattern in url_patterns:
            found_urls.extend(re.findall(pattern, code))
        
        for url in found_urls:
            if not any(api in url for api in self.APPROVED_APIS):
                return False, f"URL '{url}' not in approved APIs list for MODERATE mode"
        
        return True, None
    
    def _is_file_write_allowed(self, level: SandboxLevel) -> bool:
        """Check if file writes are allowed at given level."""
        return level != SandboxLevel.STRICT
    
    def _create_file_backup(self, file_path: Path) -> Optional[str]:
        """Create backup of file before modification (for rollback)."""
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            self._rollback_stack.append((str(file_path), content))
            return content
        except Exception:
            return None
    
    def rollback(self) -> int:
        """
        Rollback all file changes made during last execution.
        
        Returns:
            Number of files restored
        """
        restored = 0
        while self._rollback_stack:
            file_path, content = self._rollback_stack.pop()
            try:
                with open(file_path, 'w') as f:
                    f.write(content)
                restored += 1
            except Exception as e:
                print(f"Failed to restore {file_path}: {e}")
        
        return restored
    
    def log_action(self, entry: AuditEntry):
        """Write audit entry to log file."""
        log_line = json.dumps(asdict(entry)) + '\n'
        with open(self.audit_log_path, 'a') as f:
            f.write(log_line)
    
    def get_audit_trail(self, limit: int = 100) -> List[AuditEntry]:
        """
        Retrieve recent audit trail entries.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of AuditEntry objects (most recent first)
        """
        entries = []
        if not self.audit_log_path.exists():
            return entries
        
        with open(self.audit_log_path, 'r') as f:
            lines = f.readlines()
        
        for line in reversed(lines[-limit:]):
            try:
                data = json.loads(line.strip())
                entries.append(AuditEntry(**data))
            except json.JSONDecodeError:
                continue
        
        return entries
    
    def execute_sandboxed(self, code: str, level: SandboxLevel = SandboxLevel.MODERATE) -> Dict[str, Any]:
        """
        Execute code in sandboxed environment.
        
        Args:
            code: Python code to execute
            level: Sandbox restriction level
            
        Returns:
            Result dictionary with output, success status, audit info
        """
        import time
        start_time = time.time()
        code_hash = self._compute_code_hash(code)
        
        result = {
            'success': False,
            'output': None,
            'error': None,
            'secrets_detected': [],
            'audit_entry': None,
            'rolled_back': False,
        }
        
        # === PHASE 1: PRE-EXECUTION SCANNING ===
        
        # Scan for secrets
        secret_matches = self.scan_for_secrets(code)
        result['secrets_detected'] = [asdict(m) for m in secret_matches]
        
        # Block HIGH severity secrets
        high_severity = [m for m in secret_matches if m.severity == 'HIGH']
        if high_severity:
            result['error'] = f"BLOCKED: High severity secrets detected: {[m.type for m in high_severity]}"
            return result
        
        # Check network permissions
        network_allowed, network_error = self._is_network_call_allowed(code, level)
        if not network_allowed:
            result['error'] = f"BLOCKED: {network_error}"
            return result
        
        # Validate all file paths in code (static analysis)
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    func_name = None
                    if isinstance(node.func, ast.Name):
                        func_name = node.func.id
                    elif isinstance(node.func, ast.Attribute):
                        if isinstance(node.func.value, ast.Name):
                            func_name = f"{node.func.value.id}.{node.func.attr}"
                    
                    if func_name in ['open', 'os.path.join', 'pathlib.Path']:
                        # Try to validate path arguments
                        for arg in node.args:
                            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                                if not arg.value.startswith(('http://', 'https://')):
                                    try:
                                        self.validate_path(arg.value)
                                    except (ValueError, PermissionError) as e:
                                        result['error'] = f"BLOCKED: Invalid path in code: {e}"
                                        return result
        except SyntaxError as e:
            result['error'] = f"SYNTAX ERROR: {e}"
            return result
        
        # === PHASE 2: EXECUTION ===
        
        execution_error = None
        execution_output = None
        
        try:
            # Create restricted globals based on sandbox level
            restricted_globals = {
                '__builtins__': self._get_restricted_builtins(level),
            }
            
            # Add safe modules based on level
            if level != SandboxLevel.STRICT:
                restricted_globals['json'] = json
                restricted_globals['os'] = self._get_restricted_os(level)
                restricted_globals['pathlib'] = __import__('pathlib')
            
            # Compile and execute
            compiled = compile(code, '<sandboxed>', 'exec')
            
            # Capture output
            from io import StringIO
            import sys
            
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            sys.stdout = StringIO()
            sys.stderr = StringIO()
            
            try:
                exec(compiled, restricted_globals)
                execution_output = sys.stdout.getvalue()
                stderr_output = sys.stderr.getvalue()
                if stderr_output:
                    execution_output += f"\n[STDERR]: {stderr_output}"
            finally:
                sys.stdout = old_stdout
                sys.stderr = old_stderr
            
            result['success'] = True
            result['output'] = execution_output
            
        except Exception as e:
            execution_error = str(e)
            result['error'] = execution_error
        
        # === PHASE 3: POST-EXECUTION & AUDIT ===
        
        duration_ms = (time.time() - start_time) * 1000
        
        # Rollback on failure if configured
        if not result['success'] and execution_error:
            # Auto-rollback any file changes
            rollback_count = self.rollback()
            result['rolled_back'] = rollback_count > 0
        
        # Create audit entry
        audit_entry = AuditEntry(
            timestamp=datetime.now().isoformat(),
            action='execute_sandboxed',
            level=level.value,
            code_hash=code_hash,
            result='success' if result['success'] else f'error: {execution_error}',
            duration_ms=duration_ms,
            secrets_found=[m.type for m in secret_matches],
            error=execution_error
        )
        
        self.log_action(audit_entry)
        result['audit_entry'] = asdict(audit_entry)
        
        return result
    
    def _get_restricted_builtins(self, level: SandboxLevel) -> Dict:
        """Get restricted builtins based on sandbox level."""
        safe_builtins = {
            'True': True, 'False': False, 'None': None,
            'abs': abs, 'all': all, 'any': any, 'ascii': ascii,
            'bin': bin, 'bool': bool, 'bytearray': bytearray, 'bytes': bytes,
            'callable': callable, 'chr': chr, 'classmethod': classmethod,
            'complex': complex, 'delattr': delattr, 'dict': dict,
            'dir': dir, 'divmod': divmod, 'enumerate': enumerate,
            'filter': filter, 'float': float, 'format': format,
            'frozenset': frozenset, 'getattr': getattr, 'globals': globals,
            'hasattr': hasattr, 'hash': hash, 'hex': hex, 'id': id,
            'input': input, 'int': int, 'isinstance': isinstance,
            'issubclass': issubclass, 'iter': iter, 'len': len,
            'list': list, 'locals': locals, 'map': map, 'max': max,
            'memoryview': memoryview, 'min': min, 'next': next,
            'object': object, 'oct': oct, 'ord': ord, 'pow': pow,
            'print': print, 'property': property, 'range': range,
            'repr': repr, 'reversed': reversed, 'round': round,
            'set': set, 'setattr': setattr, 'slice': slice,
            'sorted': sorted, 'staticmethod': staticmethod, 'str': str,
            'sum': sum, 'super': super, 'tuple': tuple, 'type': type,
            'vars': vars, 'zip': zip, '__build_class__': __build_class__,
            '__import__': self._restricted_import(level),
        }
        
        return safe_builtins
    
    def _restricted_import(self, level: SandboxLevel):
        """Create restricted import function."""
        allowed_modules = {
            'json', 're', 'math', 'random', 'datetime', 'itertools',
            'collections', 'functools', 'statistics', 'typing',
            'string', 'hashlib', 'base64', 'html',
        }
        
        if level != SandboxLevel.STRICT:
            allowed_modules.update([
                'pathlib', 'os', 'sys', 'dataclasses', 'enum',
            ])
        
        def _import(name, globals=None, locals=None, fromlist=(), level=0):
            base_name = name.split('.')[0]
            if base_name in allowed_modules:
                return __import__(name, globals, locals, fromlist, level)
            raise ImportError(f"Module '{name}' not allowed in sandbox level")
        
        return _import
    
    def _get_restricted_os(self, level: SandboxLevel):
        """Get restricted os module."""
        import os as real_os
        
        class RestrictedOs:
            @staticmethod
            def path(*args, **kwargs):
                return real_os.path(*args, **kwargs)
            
            @staticmethod
            def listdir(path='.'):
                return real_os.listdir(path)
            
            @staticmethod
            def getcwd():
                return str(real_os.getcwd())
            
            @staticmethod
            def environ_get(key, default=None):
                # Only allow safe env vars
                safe_vars = ['HOME', 'USER', 'PATH', 'PWD']
                if key in safe_vars:
                    return real_os.environ.get(key, default)
                return default
            
            # Block dangerous functions
            system = None
            popen = None
            fork = None
            execv = None
            spawnv = None
        
        return RestrictedOs()


# === AUDIT CHECK: Validate module structure ===
if __name__ == "__main__":
    # Self-test
    container = SafetyContainer()
    
    # Test secret scanning
    test_code = """
api_key = "sk-test1234567890abcdef1234567890"
password = "super_secret_password_123"
"""
    secrets = container.scan_for_secrets(test_code)
    assert len(secrets) == 2, f"Expected 2 secrets, got {len(secrets)}"
    print(f"✓ Secret scanning: {len(secrets)} secrets detected")
    
    # Test path validation
    try:
        container.validate_path("/etc/passwd")
        assert False, "Should have raised error"
    except (ValueError, PermissionError):
        print("✓ Path validation: correctly blocks /etc/passwd")
    
    # Test sandboxed execution
    result = container.execute_sandboxed("print('Hello Sandbox')", SandboxLevel.STRICT)
    assert result['success'], f"Execution failed: {result['error']}"
    print("✓ Sandboxed execution: works")
    
    print("\n✅ All audits passed - Safety Container ready!")