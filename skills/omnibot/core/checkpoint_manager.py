"""
Omnibot Checkpoint Manager

Human-in-the-loop approval system for sensitive actions.
Ensures human oversight before irreversible or external actions.
"""

import json
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger("omnibot.checkpoint")


class CheckpointStatus(Enum):
    """Checkpoint status states."""
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    EXPIRED = "expired"


class ActionType(Enum):
    """Categories of actions with different approval requirements."""
    AUTO_EXECUTE = "auto"        # No approval needed
    HUMAN_REQUIRED = "human"     # Always require approval
    CONFIG_DEPENDENT = "config"  # Depends on configuration


# Default action categorization
DEFAULT_ACTION_CATEGORIES = {
    # Auto-execute (no approval)
    "file_read": ActionType.AUTO_EXECUTE,
    "file_write": ActionType.AUTO_EXECUTE,
    "file_create": ActionType.AUTO_EXECUTE,
    "code_generate": ActionType.AUTO_EXECUTE,
    "code_test": ActionType.AUTO_EXECUTE,
    "research_web": ActionType.AUTO_EXECUTE,
    "research_local": ActionType.AUTO_EXECUTE,
    "tool_internal": ActionType.AUTO_EXECUTE,
    "doc_create": ActionType.AUTO_EXECUTE,
    "doc_update": ActionType.AUTO_EXECUTE,
    
    # Human required (approval gate)
    "message_external": ActionType.HUMAN_REQUIRED,
    "email_send": ActionType.HUMAN_REQUIRED,
    "post_social": ActionType.HUMAN_REQUIRED,
    "proposal_submit": ActionType.HUMAN_REQUIRED,
    "spending_money": ActionType.HUMAN_REQUIRED,
    "api_external": ActionType.HUMAN_REQUIRED,
    "service_purchase": ActionType.HUMAN_REQUIRED,
    "file_delete": ActionType.HUMAN_REQUIRED,
    "data_delete": ActionType.HUMAN_REQUIRED,
    "client_submit": ActionType.HUMAN_REQUIRED,
    "credential_access": ActionType.HUMAN_REQUIRED,
    "config_system": ActionType.HUMAN_REQUIRED,
    
    # Config dependent
    "script_execute": ActionType.CONFIG_DEPENDENT,
    "command_shell": ActionType.CONFIG_DEPENDENT,
}


@dataclass
class Checkpoint:
    """
    Checkpoint data structure for human approval.
    
    Attributes:
        checkpoint_id: Unique identifier
        timestamp: ISO-8601 timestamp
        action: Description of action
        context: Execution context
        consequences: What happens if approved
        alternatives: Alternative options
        required: Whether approval is mandatory
        status: Current checkpoint status
        response: User response if given
        reason: Reason for approval/denial
    """
    checkpoint_id: str
    timestamp: str
    action: str
    context: Dict[str, Any]
    consequences: str
    alternatives: List[str]
    required: bool
    status: CheckpointStatus = CheckpointStatus.PENDING
    response: Optional[str] = None
    reason: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        data = asdict(self)
        data["status"] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Checkpoint":
        """Create from dictionary."""
        data = data.copy()
        data["status"] = CheckpointStatus(data.get("status", "pending"))
        data["required"] = data.get("required", True)
        return cls(**data)


class CheckpointManager:
    """
    Manages human-in-the-loop approval system.
    
    Features:
    - Automatic action categorization
    - Checkpoint creation and tracking
    - Audit trail logging
    - Configurable approval rules
    
    Example:
        manager = CheckpointManager()
        
        # Check if action needs approval
        if manager.check_permission("email_send"):
            checkpoint = manager.request_approval(
                action="Send email to client",
                context={"recipient": "client@example.com"},
                consequences="Email will be sent immediately"
            )
            # ... wait for user response ...
    """
    
    def __init__(self, 
                 audit_log_path: Optional[Path] = None,
                 auto_approve: Optional[List[str]] = None,
                 require_approval: Optional[List[str]] = None):
        """
        Initialize checkpoint manager.
        
        Args:
            audit_log_path: Path to audit log file
            auto_approve: Action types to auto-approve
            require_approval: Action types requiring explicit approval
        """
        self.audit_log_path = audit_log_path or Path("checkpoint_audit.log")
        self.action_categories = DEFAULT_ACTION_CATEGORIES.copy()
        self.auto_approve = set(auto_approve or [])
        self.require_approval = set(require_approval or [])
        self._pending_checkpoints: Dict[str, Checkpoint] = {}
        self._decision_callbacks: Dict[str, Callable] = {}
        
        # Ensure audit log directory exists
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info("CheckpointManager initialized")
    
    def check_permission(self, action_type: str, 
                        context: Optional[Dict] = None) -> bool:
        """
        Determine if action requires human approval.
        
        Args:
            action_type: Category of action
            context: Additional context for decision
            
        Returns:
            True if approval is required
        """
        context = context or {}
        
        # Override checks
        if action_type in self.auto_approve:
            logger.debug(f"Auto-approved (whitelist): {action_type}")
            return False
        
        if action_type in self.require_approval:
            logger.debug(f"Requires approval (blacklist): {action_type}")
            return True
        
        # Default categorization
        category = self.action_categories.get(action_type, ActionType.HUMAN_REQUIRED)
        
        if category == ActionType.AUTO_EXECUTE:
            # Additional safety checks for file operations
            if action_type in ["file_write", "file_create"]:
                path = context.get("path", "")
                if self._is_sensitive_path(path):
                    logger.info(f"Sensitive path requires approval: {path}")
                    return True
            return False
        
        elif category == ActionType.HUMAN_REQUIRED:
            return True
        
        elif category == ActionType.CONFIG_DEPENDENT:
            # Check context for explicit approval override
            return context.get("require_approval", True)
        
        return True
    
    def _is_sensitive_path(self, path: str) -> bool:
        """Check if path is in sensitive location."""
        sensitive_patterns = [
            "/etc/",
            "/usr/",
            "/bin/",
            "/sbin/",
            "/sys/",
            "/proc/",
            ".ssh/",
            ".gnupg/",
            ".aws/",
            ".config/",
        ]
        path_lower = path.lower()
        return any(pattern in path_lower for pattern in sensitive_patterns)
    
    def request_approval(self,
                        action: str,
                        context: Dict[str, Any],
                        consequences: str,
                        alternatives: Optional[List[str]] = None,
                        required: bool = True) -> Checkpoint:
        """
        Create checkpoint requesting human approval.
        
        Args:
            action: Action description
            context: Execution context
            consequences: Expected consequences
            alternatives: Alternative options
            required: Whether approval is mandatory
            
        Returns:
            Checkpoint object
        """
        checkpoint = Checkpoint(
            checkpoint_id=str(uuid.uuid4())[:8],
            timestamp=datetime.now().isoformat(),
            action=action,
            context=context,
            consequences=consequences,
            alternatives=alternatives or [],
            required=required,
            status=CheckpointStatus.PENDING
        )
        
        self._pending_checkpoints[checkpoint.checkpoint_id] = checkpoint
        
        # Log checkpoint creation
        self.log_decision(checkpoint, None, "checkpoint_created")
        
        logger.info(f"Checkpoint created: {checkpoint.checkpoint_id} - {action}")
        
        return checkpoint
    
    def submit_decision(self, 
                       checkpoint_id: str, 
                       approved: bool,
                       reason: Optional[str] = None) -> Checkpoint:
        """
        Submit user decision for checkpoint.
        
        Args:
            checkpoint_id: Checkpoint ID
            approved: True if approved
            reason: Optional reason
            
        Returns:
            Updated checkpoint
        """
        checkpoint = self._pending_checkpoints.get(checkpoint_id)
        
        if not checkpoint:
            raise ValueError(f"Checkpoint not found: {checkpoint_id}")
        
        checkpoint.status = CheckpointStatus.APPROVED if approved else CheckpointStatus.DENIED
        checkpoint.response = "approved" if approved else "denied"
        checkpoint.reason = reason
        
        # Move from pending to logged
        del self._pending_checkpoints[checkpoint_id]
        
        # Log the decision
        self.log_decision(checkpoint, approved, reason)
        
        # Trigger callback if registered
        callback = self._decision_callbacks.pop(checkpoint_id, None)
        if callback:
            try:
                callback(checkpoint)
            except Exception as e:
                logger.error(f"Callback error: {e}")
        
        logger.info(f"Checkpoint {checkpoint_id}: {'APPROVED' if approved else 'DENIED'}")
        
        return checkpoint
    
    def get_pending(self) -> List[Checkpoint]:
        """Get all pending checkpoints."""
        return list(self._pending_checkpoints.values())
    
    def get_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """Get specific checkpoint by ID."""
        return self._pending_checkpoints.get(checkpoint_id)
    
    def log_decision(self, checkpoint: Checkpoint, 
                    approved: Optional[bool],
                    reason: Optional[str]):
        """
        Write decision to audit log.
        
        Args:
            checkpoint: Checkpoint data
            approved: Approval status
            reason: Decision reason
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "checkpoint_id": checkpoint.checkpoint_id,
            "action": checkpoint.action,
            "approved": approved,
            "reason": reason or checkpoint.reason,
            "context_hash": hash(json.dumps(checkpoint.context, sort_keys=True)) % 10000
        }
        
        with open(self.audit_log_path, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def get_audit_log(self, limit: int = 100) -> List[Dict]:
        """
        Retrieve recent audit log entries.
        
        Args:
            limit: Max entries to return
            
        Returns:
            List of log entries
        """
        if not self.audit_log_path.exists():
            return []
        
        entries = []
        with open(self.audit_log_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        
        return entries[-limit:]
    
    def format_checkpoint_prompt(self, checkpoint: Checkpoint) -> str:
        """
        Format checkpoint as human-readable prompt.
        
        Args:
            checkpoint: Checkpoint to format
            
        Returns:
            Formatted prompt string
        """
        lines = [
            "┌─────────────────────────────────────────────────────────┐",
            "│                     🚦 CHECKPOINT                         │",
            "├─────────────────────────────────────────────────────────┤",
            f"│ Action: {checkpoint.action[:50]:<47} │",
            f"│ ID: {checkpoint.checkpoint_id:<51} │",
            "│                                                         │",
        ]
        
        # Context (key info only)
        context_str = json.dumps(checkpoint.context, default=str)[:150]
        if len(context_str) > 50:
            lines.append(f"│ Context: {context_str[:50]:<46} │")
            for i in range(50, min(len(context_str), 150), 50):
                lines.append(f"│         {context_str[i:i+50]:<47} │")
        else:
            lines.append(f"│ Context: {context_str:<46} │")
        
        lines.extend([
            "│                                                         │",
            f"│ Consequences: {checkpoint.consequences[:40]:<36} │",
        ])
        
        if checkpoint.alternatives:
            lines.append("│                                                         │")
            lines.append("│ Alternatives:                                           │")
            for alt in checkpoint.alternatives[:3]:
                lines.append(f"│   - {alt[:45]:<48} │")
        
        lines.extend([
            "│                                                         │",
            "│ Options: [approve] [deny] [skip]                        │",
            "└─────────────────────────────────────────────────────────┘",
            "",
            f"Checkpoint ID: {checkpoint.checkpoint_id}",
        ])
        
        return "\n".join(lines)
    
    def configure_action(self, action_type: str, category: ActionType):
        """
        Configure action type category.
        
        Args:
            action_type: Action type to configure
            category: New category
        """
        self.action_categories[action_type] = category
        logger.info(f"Configured {action_type} as {category.value}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get manager status."""
        return {
            "pending_count": len(self._pending_checkpoints),
            "pending_ids": list(self._pending_checkpoints.keys()),
            "configured_actions": len(self.action_categories),
            "audit_log_path": str(self.audit_log_path),
            "audit_entries": len(self.get_audit_log(1)) if self.audit_log_path.exists() else 0
        }