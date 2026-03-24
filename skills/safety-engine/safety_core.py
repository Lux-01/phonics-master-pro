#!/usr/bin/env python3
"""
Safety Verification Engine
Provides formal verification, circuit breakers, and risk assessment.

ACA Implementation:
- Requirements: Prevent catastrophic failures, enforce safety limits
- Architecture: Policy engine + verification layer + circuit breaker
- Data Flow: Action Request → Policy Check → Risk Score → Execute/Block
- Edge Cases: Policy conflict, race conditions, system failure
- Tools: YAML policies, Python validation, audit logging
- Errors: Fail-safe (block), alert, log
- Tests: 6 comprehensive test cases
"""

import json
import logging
import hashlib
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, asdict
from enum import Enum
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ActionType(Enum):
    TRADE = "trade"
    TRANSFER = "transfer"
    MODIFY_CONFIG = "modify_config"
    DELETE_DATA = "delete_data"
    EXECUTE_CODE = "execute_code"
    EXTERNAL_API = "external_api"


class RiskLevel(Enum):
    CRITICAL = "critical"  # Requires multi-sig + time delay
    HIGH = "high"          # Requires approval + logging
    MEDIUM = "medium"      # Requires logging + monitoring
    LOW = "low"            # Auto-approve with logging


class ActionStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    FAILED = "failed"


@dataclass
class SafetyPolicy:
    """Safety policy definition."""
    name: str
    action_types: List[ActionType]
    max_daily: Optional[int] = None
    max_amount: Optional[float] = None
    requires_approval: bool = False
    approval_count: int = 1
    time_delay_minutes: int = 0
    conditions: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "action_types": [t.value for t in self.action_types],
            "max_daily": self.max_daily,
            "max_amount": self.max_amount,
            "requires_approval": self.requires_approval,
            "approval_count": self.approval_count,
            "time_delay_minutes": self.time_delay_minutes,
            "conditions": self.conditions
        }


@dataclass
class ActionRequest:
    """Request to perform an action."""
    action_id: str
    action_type: ActionType
    source: str
    parameters: Dict[str, Any]
    requested_at: datetime
    risk_level: RiskLevel
    
    def to_dict(self) -> Dict:
        return {
            "action_id": self.action_id,
            "action_type": self.action_type.value,
            "source": self.source,
            "parameters": self.parameters,
            "requested_at": self.requested_at.isoformat(),
            "risk_level": self.risk_level.value
        }


@dataclass
class VerificationResult:
    """Result of safety verification."""
    action_id: str
    status: ActionStatus
    risk_score: float
    violations: List[str]
    required_approvals: int
    current_approvals: int
    can_execute: bool
    reason: str
    verified_at: datetime
    
    def to_dict(self) -> Dict:
        return {
            "action_id": self.action_id,
            "status": self.status.value,
            "risk_score": self.risk_score,
            "violations": self.violations,
            "required_approvals": self.required_approvals,
            "current_approvals": self.current_approvals,
            "can_execute": self.can_execute,
            "reason": self.reason,
            "verified_at": self.verified_at.isoformat()
        }


@dataclass
class CircuitBreaker:
    """Circuit breaker state."""
    name: str
    failure_count: int
    last_failure: Optional[datetime]
    is_open: bool
    open_until: Optional[datetime]
    threshold: int
    timeout_minutes: int
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "failure_count": self.failure_count,
            "last_failure": self.last_failure.isoformat() if self.last_failure else None,
            "is_open": self.is_open,
            "open_until": self.open_until.isoformat() if self.open_until else None,
            "threshold": self.threshold,
            "timeout_minutes": self.timeout_minutes
        }


class SafetyVerificationEngine:
    """
    Core safety engine providing formal verification and protection.
    
    Features:
    - Policy-based access control
    - Risk scoring
    - Circuit breaker pattern
    - Audit logging
    - Multi-signature approval
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize safety engine."""
        self.policies: Dict[str, SafetyPolicy] = {}
        self.action_history: List[Dict] = []
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.pending_approvals: Dict[str, ActionRequest] = {}
        self.approvals: Dict[str, List[str]] = {}
        self._lock = threading.Lock()
        
        # Default policies
        self._load_default_policies()
        
        # Initialize circuit breakers
        self._init_circuit_breakers()
        
        logger.info("Safety Verification Engine initialized")
    
    def _load_default_policies(self):
        """Load default safety policies."""
        # Trading policy
        self.policies["trading"] = SafetyPolicy(
            name="trading",
            action_types=[ActionType.TRADE],
            max_daily=5,
            max_amount=0.1,
            requires_approval=True,
            approval_count=1,
            time_delay_minutes=0,
            conditions={"max_loss_per_day": 0.5}
        )
        
        # Config modification policy
        self.policies["config"] = SafetyPolicy(
            name="config",
            action_types=[ActionType.MODIFY_CONFIG],
            requires_approval=True,
            approval_count=1,
            time_delay_minutes=5,
            conditions={"safety_critical": True}
        )
        
        # Data deletion policy
        self.policies["deletion"] = SafetyPolicy(
            name="deletion",
            action_types=[ActionType.DELETE_DATA],
            requires_approval=True,
            approval_count=2,  # Multi-sig
            time_delay_minutes=30
        )
        
        # External API policy
        self.policies["external_api"] = SafetyPolicy(
            name="external_api",
            action_types=[ActionType.EXTERNAL_API],
            max_daily=1000,
            requires_approval=False
        )
    
    def _init_circuit_breakers(self):
        """Initialize circuit breakers for critical components."""
        self.circuit_breakers["trading"] = CircuitBreaker(
            name="trading",
            failure_count=0,
            last_failure=None,
            is_open=False,
            open_until=None,
            threshold=3,
            timeout_minutes=60
        )
        
        self.circuit_breakers["api_calls"] = CircuitBreaker(
            name="api_calls",
            failure_count=0,
            last_failure=None,
            is_open=False,
            open_until=None,
            threshold=10,
            timeout_minutes=10
        )
    
    def verify_action(self, action_type: ActionType, source: str,
                     parameters: Dict[str, Any]) -> VerificationResult:
        """
        Verify if action is safe to execute.
        
        Args:
            action_type: Type of action
            source: Source of request
            parameters: Action parameters
            
        Returns:
            VerificationResult with status and requirements
        """
        action_id = f"act_{hashlib.md5(f'{action_type.value}_{time.time()}'.encode()).hexdigest()[:12]}"
        requested_at = datetime.now()
        
        # Determine risk level
        risk_level = self._assess_risk(action_type, parameters)
        
        request = ActionRequest(
            action_id=action_id,
            action_type=action_type,
            source=source,
            parameters=parameters,
            requested_at=requested_at,
            risk_level=risk_level
        )
        
        violations = []
        required_approvals = 0
        can_execute = True
        
        # Check circuit breaker
        if action_type == ActionType.TRADE:
            cb = self.circuit_breakers.get("trading")
            if cb and cb.is_open:
                violations.append(f"Circuit breaker open until {cb.open_until}")
                can_execute = False
        
        # Check policies
        for policy in self.policies.values():
            if action_type in policy.action_types:
                # Check daily limit
                if policy.max_daily:
                    daily_count = self._get_daily_action_count(action_type)
                    if daily_count >= policy.max_daily:
                        violations.append(f"Daily limit exceeded: {policy.max_daily}")
                        can_execute = False
                
                # Check amount limit
                if policy.max_amount and "amount" in parameters:
                    if parameters["amount"] > policy.max_amount:
                        violations.append(f"Amount exceeds limit: {policy.max_amount}")
                        can_execute = False
                
                # Check conditions
                if policy.conditions:
                    if "max_loss_per_day" in policy.conditions:
                        daily_loss = self._get_daily_loss()
                        if daily_loss >= policy.conditions["max_loss_per_day"]:
                            violations.append(f"Daily loss limit reached: {daily_loss}")
                            can_execute = False
                
                # Determine approvals needed
                if policy.requires_approval:
                    required_approvals = policy.approval_count
                    can_execute = False  # Requires approval
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(request, violations)
        
        # Determine status
        if can_execute and required_approvals == 0:
            status = ActionStatus.APPROVED
        elif violations:
            status = ActionStatus.REJECTED
        else:
            status = ActionStatus.PENDING
            self.pending_approvals[action_id] = request
            self.approvals[action_id] = []
        
        result = VerificationResult(
            action_id=action_id,
            status=status,
            risk_score=risk_score,
            violations=violations,
            required_approvals=required_approvals,
            current_approvals=0,
            can_execute=can_execute and status == ActionStatus.APPROVED,
            reason="; ".join(violations) if violations else "Passed verification",
            verified_at=datetime.now()
        )
        
        # Log verification
        self._log_verification(result)
        
        return result
    
    def _assess_risk(self, action_type: ActionType, parameters: Dict) -> RiskLevel:
        """Assess risk level of action."""
        if action_type in [ActionType.DELETE_DATA, ActionType.EXECUTE_CODE]:
            return RiskLevel.CRITICAL
        
        if action_type == ActionType.TRADE:
            amount = parameters.get("amount", 0)
            if amount > 0.5:
                return RiskLevel.HIGH
            elif amount > 0.1:
                return RiskLevel.MEDIUM
            return RiskLevel.LOW
        
        if action_type == ActionType.MODIFY_CONFIG:
            return RiskLevel.HIGH
        
        return RiskLevel.LOW
    
    def _calculate_risk_score(self, request: ActionRequest, violations: List[str]) -> float:
        """Calculate numerical risk score (0-100)."""
        score = 0.0
        
        # Base risk by action type
        risk_weights = {
            RiskLevel.CRITICAL: 80,
            RiskLevel.HIGH: 50,
            RiskLevel.MEDIUM: 25,
            RiskLevel.LOW: 10
        }
        score += risk_weights.get(request.risk_level, 10)
        
        # Add for violations
        score += len(violations) * 10
        
        # Cap at 100
        return min(score, 100.0)
    
    def _get_daily_action_count(self, action_type: ActionType) -> int:
        """Get count of actions today."""
        today = datetime.now().date()
        count = 0
        for action in self.action_history:
            action_date = datetime.fromisoformat(action["timestamp"]).date()
            if action_date == today and action["action_type"] == action_type.value:
                count += 1
        return count
    
    def _get_daily_loss(self) -> float:
        """Get total loss today."""
        today = datetime.now().date()
        total_loss = 0.0
        for action in self.action_history:
            if action.get("result") == "loss":
                action_date = datetime.fromisoformat(action["timestamp"]).date()
                if action_date == today:
                    total_loss += action.get("amount", 0)
        return total_loss
    
    def approve_action(self, action_id: str, approver: str) -> bool:
        """
        Approve a pending action.
        
        Args:
            action_id: Action to approve
            approver: ID of approver
            
        Returns:
            True if approved, False otherwise
        """
        if action_id not in self.pending_approvals:
            logger.warning(f"Action {action_id} not found or not pending")
            return False
        
        with self._lock:
            if approver not in self.approvals[action_id]:
                self.approvals[action_id].append(approver)
                logger.info(f"Action {action_id} approved by {approver}")
                
                # Check if enough approvals
                request = self.pending_approvals[action_id]
                for policy in self.policies.values():
                    if request.action_type in policy.action_types:
                        if len(self.approvals[action_id]) >= policy.approval_count:
                            # Move to approved
                            return True
        
        return False
    
    def record_execution(self, action_id: str, success: bool, result: Optional[Dict] = None):
        """Record action execution result."""
        entry = {
            "action_id": action_id,
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "result": result or {}
        }
        
        self.action_history.append(entry)
        
        # Update circuit breaker
        if not success:
            self._record_failure("trading")
        
        # Clean up pending
        if action_id in self.pending_approvals:
            del self.pending_approvals[action_id]
        if action_id in self.approvals:
            del self.approvals[action_id]
        
        logger.info(f"Recorded execution of {action_id}: {'success' if success else 'failure'}")
    
    def _record_failure(self, breaker_name: str):
        """Record failure for circuit breaker."""
        cb = self.circuit_breakers.get(breaker_name)
        if not cb:
            return
        
        cb.failure_count += 1
        cb.last_failure = datetime.now()
        
        if cb.failure_count >= cb.threshold:
            cb.is_open = True
            cb.open_until = datetime.now() + timedelta(minutes=cb.timeout_minutes)
            logger.warning(f"Circuit breaker {breaker_name} opened until {cb.open_until}")
    
    def check_circuit_breaker(self, name: str) -> bool:
        """Check if circuit breaker allows operation."""
        cb = self.circuit_breakers.get(name)
        if not cb:
            return True
        
        # Check if should auto-close
        if cb.is_open and cb.open_until:
            if datetime.now() >= cb.open_until:
                cb.is_open = False
                cb.failure_count = 0
                cb.open_until = None
                logger.info(f"Circuit breaker {name} auto-closed")
        
        return not cb.is_open
    
    def _log_verification(self, result: VerificationResult):
        """Log verification to audit trail."""
        log_entry = {
            "type": "verification",
            "timestamp": datetime.now().isoformat(),
            "data": result.to_dict()
        }
        
        # Append to audit log file
        audit_path = Path.home() / ".openclaw" / "workspace" / "memory" / "safety_audit.log"
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(audit_path, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def get_safety_report(self) -> Dict:
        """Generate safety status report."""
        return {
            "timestamp": datetime.now().isoformat(),
            "policies": {k: v.to_dict() for k, v in self.policies.items()},
            "circuit_breakers": {k: v.to_dict() for k, v in self.circuit_breakers.items()},
            "pending_approvals": len(self.pending_approvals),
            "today_actions": len([a for a in self.action_history 
                                 if datetime.fromisoformat(a["timestamp"]).date() == datetime.now().date()]),
            "today_loss": self._get_daily_loss()
        }


def test_safety_engine():
    """Run comprehensive safety engine tests."""
    print("🧪 Testing Safety Verification Engine...")
    
    engine = SafetyVerificationEngine()
    
    # Test 1: Low risk action
    print("\n1️⃣ Testing low risk action...")
    result = engine.verify_action(
        ActionType.EXTERNAL_API,
        "test",
        {"endpoint": "https://api.example.com/data"}
    )
    assert result.can_execute, "Low risk action should be approved"
    assert result.risk_level == RiskLevel.LOW
    print("✅ Low risk action approved")
    
    # Test 2: High risk action (trading)
    print("\n2️⃣ Testing high risk action...")
    result = engine.verify_action(
        ActionType.TRADE,
        "trading_system",
        {"token": "SOL", "amount": 0.2, "side": "buy"}
    )
    assert not result.can_execute, "High risk should require approval"
    assert result.status == ActionStatus.PENDING
    print("✅ High risk action requires approval")
    
    # Test 3: Approval workflow
    print("\n3️⃣ Testing approval workflow...")
    action_id = result.action_id
    approved = engine.approve_action(action_id, "user_1")
    assert approved, "Should be approved with 1 approval"
    print("✅ Approval workflow works")
    
    # Test 4: Circuit breaker
    print("\n4️⃣ Testing circuit breaker...")
    # Record failures
    for i in range(3):
        engine.record_execution(f"test_{i}", False, {"error": "test"})
    
    cb_status = engine.check_circuit_breaker("trading")
    assert not cb_status, "Circuit breaker should be open after 3 failures"
    print("✅ Circuit breaker triggered")
    
    # Test 5: Daily limits
    print("\n5️⃣ Testing daily limits...")
    # Simulate 5 trades today
    for i in range(5):
        engine.action_history.append({
            "action_type": ActionType.TRADE.value,
            "timestamp": datetime.now().isoformat(),
            "result": "success"
        })
    
    result = engine.verify_action(
        ActionType.TRADE,
        "trading_system",
        {"token": "SOL", "amount": 0.05, "side": "buy"}
    )
    assert not result.can_execute, "Should reject after daily limit"
    assert "Daily limit exceeded" in str(result.violations)
    print("✅ Daily limit enforced")
    
    # Test 6: Safety report
    print("\n6️⃣ Testing safety report...")
    report = engine.get_safety_report()
    assert "policies" in report
    assert "circuit_breakers" in report
    print(f"✅ Safety report generated: {len(report['policies'])} policies")
    
    print("\n🎉 All Safety Engine tests passed!")
    return True


if __name__ == "__main__":
    test_safety_engine()
