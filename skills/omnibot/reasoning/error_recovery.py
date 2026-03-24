"""
Error Recovery System.
Analyze → Hypothesize → Fix → Verify
"""

from typing import Dict, List, Callable, Any, Tuple, Optional
from datetime import datetime
import traceback
import logging

class ErrorRecovery:
    """
    Error recovery with learning:
    - Analyze error context
    - Hypothesize causes
    - Attempt fixes
    - Verify resolution
    """
    
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.failure_patterns = {}
        self.successful_fixes = []
        self.logger = logging.getLogger("Omnibot.ErrorRecovery")
    
    def execute(self, func: Callable, *args, **kwargs) -> Tuple[bool, Any]:
        """
        Execute function with error recovery.
        
        Args:
            func: Function to execute
            *args, **kwargs: Function arguments
            
        Returns:
            (success, result_or_error_info)
        """
        last_error = None
        attempts = 0
        
        while attempts < self.max_retries:
            attempts += 1
            
            try:
                self.logger.info(f"Attempt {attempts}/{self.max_retries}")
                result = func(*args, **kwargs)
                
                # Success!
                if attempts > 1:
                    self.logger.info(f"Succeeded on attempt {attempts}")
                return True, result
                
            except Exception as e:
                last_error = e
                error_context = {
                    "error": str(e),
                    "type": type(e).__name__,
                    "traceback": traceback.format_exc(),
                    "attempt": attempts,
                    "timestamp": datetime.now().isoformat()
                }
                
                self.logger.warning(f"Attempt {attempts} failed: {e}")
                
                if attempts < self.max_retries:
                    # Try to recover
                    recovered = self._attempt_recovery(error_context, func, args, kwargs)
                    if not recovered:
                        # Recovery failed, escalate
                        self.logger.error("Recovery failed, escalating")
                        break
                else:
                    self.logger.error(f"All {self.max_retries} attempts exhausted")
        
        # Max retries reached, report failure
        error_info = {
            "success": False,
            "attempts_made": attempts,
            "last_error": str(last_error),
            "error_type": type(last_error).__name__ if last_error else "Unknown",
            "traceback": traceback.format_exc() if last_error else None,
            "suggested_action": self._suggest_escalation(last_error)
        }
        
        # Learn from failure
        self._learn_from_failure(error_info)
        
        return False, error_info
    
    def _attempt_recovery(self, error_context: Dict, func: Callable,
                         args: tuple, kwargs: dict) -> bool:
        """
        Attempt to recover from an error.
        
        Returns:
            True if recovery succeeded
        """
        error_type = error_context.get("type", "Unknown")
        error_msg = error_context.get("error", "")
        
        self.logger.info(f"Attempting recovery for {error_type}")
        
        # Step 1: Analyze the error
        analysis = self._analyze_error(error_type, error_msg, error_context)
        
        # Step 2: Hypothesize causes
        hypotheses = self._hypothesize_causes(analysis)
        
        # Step 3: Try fixes
        for hypothesis in hypotheses:
            self.logger.info(f"Trying: {hypothesis['strategy']}")
            
            fix_applied = self._apply_fix(hypothesis, args, kwargs)
            if fix_applied:
                return True
        
        return False
    
    def _analyze_error(self, error_type: str, error_msg: str,
                       error_context: Dict) -> Dict:
        """Analyze error context."""
        analysis = {
            "error_type": error_type,
            "error_msg": error_msg,
            "is_common_pattern": error_type in self.failure_patterns,
            "likely_causes": [],
            "location_hint": None
        }
        
        # Check for common error patterns
        common_patterns = {
            "FileNotFoundError": ["missing_file", "path_issue"],
            "PermissionError": ["access_denied", "wrong_permissions"],
            "ValueError": ["invalid_input", "type_mismatch"],
            "TypeError": ["wrong_type", "missing_param"],
            "KeyError": ["missing_key", "dict_access"],
            "IndexError": ["out_of_bounds", "empty_list"],
            "ConnectionError": ["network_issue", "service_down"],
            "TimeoutError": ["slow_response", "deadlock"]
        }
        
        if error_type in common_patterns:
            analysis["likely_causes"] = common_patterns[error_type]
        
        # Extract hint from traceback
        tb = error_context.get("traceback", "")
        if tb:
            lines = tb.strip().split('\n')
            if lines:
                analysis["location_hint"] = lines[-2] if len(lines) > 1 else lines[0]
        
        return analysis
    
    def _hypothesize_causes(self, analysis: Dict) -> List[Dict]:
        """Generate hypotheses about the cause."""
        hypotheses = []
        error_type = analysis.get("error_type", "")
        likely_causes = analysis.get("likely_causes", [])
        
        # Generate fix strategies based on error type
        fix_strategies = {
            "FileNotFoundError": [
                {"strategy": "create_missing_directories", "action": "ensure_dirs"},
                {"strategy": "check_file_path", "action": "validate_path"},
                {"strategy": "retry_with_absolute_path", "action": "abs_path"}
            ],
            "PermissionError": [
                {"strategy": "check_current_permissions", "action": "check_perms"},
                {"strategy": "use_temp_directory", "action": "use_tmp"}
            ],
            "ValueError": [
                {"strategy": "add_input_validation", "action": "validate"},
                {"strategy": "check_none_values", "action": "check_none"}
            ],
            "TypeError": [
                {"strategy": "check_argument_types", "action": "type_check"},
                {"strategy": "add_type_conversion", "action": "convert"}
            ],
            "KeyError": [
                {"strategy": "use_get_with_default", "action": "safe_dict"},
                {"strategy": "check_key_existence", "action": "key_check"}
            ],
            "ConnectionError": [
                {"strategy": "add_retry_with_backoff", "action": "retry"},
                {"strategy": "check_service_status", "action": "health_check"}
            ],
            "TimeoutError": [
                {"strategy": "increase_timeout", "action": "extend_timeout"},
                {"strategy": "check_for_deadlock", "action": "deadlock_check"}
            ]
        }
        
        if error_type in fix_strategies:
            hypotheses.extend(fix_strategies[error_type])
        
        # Add generic fallback
        hypotheses.append({
            "strategy": "log_and_continue",
            "action": "log_continue"
        })
        
        return hypotheses
    
    def _apply_fix(self, hypothesis: Dict, args: tuple, kwargs: dict) -> bool:
        """
        Apply a fix based on hypothesis.
        
        Returns:
            True if fix applied successfully
        """
        action = hypothesis.get("action")
        
        # These are placeholder fixes - in a real system,
        # these would actually modify the execution context
        
        fix_actions = {
            "ensure_dirs": lambda: self._ensure_directories(kwargs),
            "validate_path": lambda: self._validate_paths(kwargs),
            "validate": lambda: self._add_validation(args, kwargs),
            "type_check": lambda: self._check_types(args, kwargs),
            "safe_dict": lambda: self._use_safe_dict_access(kwargs),
            "retry": lambda: self._setup_retry(kwargs),
            "extend_timeout": lambda: self._extend_timeout(kwargs),
            "log_continue": lambda: self._log_and_continue()
        }
        
        if action in fix_actions:
            try:
                fix_actions[action]()
                return True
            except Exception as e:
                self.logger.warning(f"Fix {action} failed: {e}")
                return False
        
        return False
    
    def _suggest_escalation(self, last_error: Optional[Exception]) -> str:
        """Suggest escalation path after max retries."""
        if last_error is None:
            return "Unknown error occurred - manual investigation required"
        
        error_type = type(last_error).__name__
        
        escalation_paths = {
            "FileNotFoundError": "Verify file exists and path is correct",
            "PermissionError": "Check file permissions and user access rights",
            "ConnectionError": "Verify network connectivity and service availability",
            "TimeoutError": "Check for blocking operations or infinite loops",
            "MemoryError": "Reduce memory usage or process in chunks",
            "RecursionError": "Check for infinite recursion in code"
        }
        
        return escalation_paths.get(error_type, 
            f"Unhandled {error_type} - requires developer attention")
    
    def _learn_from_failure(self, error_info: Dict):
        """Learn from failure to improve future recoveries."""
        error_type = error_info.get("error_type", "Unknown")
        
        if error_type not in self.failure_patterns:
            self.failure_patterns[error_type] = {
                "count": 0,
                "contexts": []
            }
        
        self.failure_patterns[error_type]["count"] += 1
        self.failure_patterns[error_type]["contexts"].append({
            "timestamp": datetime.now().isoformat(),
            "attempts": error_info.get("attempts_made"),
            "suggested_action": error_info.get("suggested_action")
        })
        
        # Keep only recent patterns
        if len(self.failure_patterns[error_type]["contexts"]) > 10:
            self.failure_patterns[error_type]["contexts"] = \
                self.failure_patterns[error_type]["contexts"][-10:]
    
    # Fix implementation placeholders
    def _ensure_directories(self, kwargs):
        """Ensure directories exist."""
        if "path" in kwargs or "file_path" in kwargs:
            import os
            path = kwargs.get("path") or kwargs.get("file_path")
            if path:
                os.makedirs(os.path.dirname(path), exist_ok=True)
    
    def _validate_paths(self, kwargs):
        """Validate file paths."""
        pass  # Would check if paths exist
    
    def _add_validation(self, args, kwargs):
        """Add input validation."""
        pass
    
    def _check_types(self, args, kwargs):
        """Check argument types."""
        pass
    
    def _use_safe_dict_access(self, kwargs):
        """Use safe dictionary access."""
        pass
    
    def _setup_retry(self, kwargs):
        """Setup retry configuration."""
        kwargs["_retry_config"] = {"max_retries": 3, "backoff": True}
    
    def _extend_timeout(self, kwargs):
        """Extend timeout values."""
        if "timeout" in kwargs:
            kwargs["timeout"] = kwargs["timeout"] * 2
    
    def _log_and_continue(self):
        """Log error and continue."""
        self.logger.info("Logging error and continuing")

    def get_failure_stats(self) -> Dict:
        """Get failure pattern statistics."""
        return {
            "total_unique_error_types": len(self.failure_patterns),
            "patterns": {
                k: {"count": v["count"]} 
                for k, v in self.failure_patterns.items()
            }
        }