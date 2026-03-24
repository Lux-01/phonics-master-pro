#!/usr/bin/env python3
"""
Audit Logger - Complete audit trail for all Omnibot actions.

Features:
1. Immutable action logging - tamper-evident records
2. Decision justification - why was something done
3. Human oversight checkpoints - approval tracking
4. Compliance reporting - GDPR, SOC2 ready
5. Chain of custody - for security incidents
6. Real-time alerting - suspicious activity detection
"""

import hashlib
import json
import logging
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import threading
import uuid


class AuditLevel(Enum):
    """Audit log severity levels."""
    DEBUG = "debug"          # Internal operations
    INFO = "info"            # Normal operations
    NOTICE = "notice"        # Significant actions
    WARNING = "warning"        # Suspicious but allowed
    ERROR = "error"          # Failed operations
    CRITICAL = "critical"    # Security incidents


class ActionType(Enum):
    """Types of audited actions."""
    # File operations
    FILE_READ = "file_read"
    FILE_WRITE = "file_write"
    FILE_DELETE = "file_delete"
    FILE_EXECUTE = "file_execute"
    
    # Memory operations
    MEMORY_STORE = "memory_store"
    MEMORY_RETRIEVE = "memory_retrieve"
    MEMORY_DELETE = "memory_delete"
    
    # External operations
    API_CALL = "api_call"
    WEB_REQUEST = "web_request"
    WEBHOOK_SEND = "webhook_send"
    EMAIL_SEND = "email_send"
    
    # Job operations
    JOB_START = "job_start"
    JOB_CHECKPOINT = "job_checkpoint"
    JOB_COMPLETE = "job_complete"
    JOB_CANCEL = "job_cancel"
    
    # AI operations
    INFERENCE = "inference"
    TRAINING = "training"
    FINE_TUNE = "fine_tune"
    
    # Security operations
    AUTH_LOGIN = "auth_login"
    AUTH_LOGOUT = "auth_logout"
    PERMISSION_CHECK = "permission_check"
    SECRET_ACCESS = "secret_access"
    
    # System operations
    CONFIG_CHANGE = "config_change"
    MODULE_LOAD = "module_load"
    MODULE_UNLOAD = "module_unload"
    SHUTDOWN = "shutdown"


@dataclass
class AuditEvent:
    """A single audit event."""
    event_id: str
    timestamp: str
    level: AuditLevel
    action_type: ActionType
    actor: str  # user_id, system, or module_name
    resource: str  # file path, API endpoint, etc.
    description: str
    context: Dict[str, Any]
    success: bool
    duration_ms: int
    hash_chain: str  # Hash of previous event + this event for tamper detection
    checkpoint_id: Optional[str] = None
    approval_status: Optional[str] = None


class AuditLogger:
    """
    Immutable audit logging system with chain verification.
    """
    
    def __init__(self, data_dir: Optional[str] = None, enable_sqlite: bool = True):
        self.logger = logging.getLogger("Omnibot.AuditLogger")
        
        # Storage
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent / "audit_data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # SQLite database for structured queries
        self.db_path = self.data_dir / "audit.db"
        self.enable_sqlite = enable_sqlite
        if enable_sqlite:
            self._init_database()
        
        # JSON log file for humans
        self.json_log = self.data_dir / "audit_log.jsonl"
        
        # In-memory buffer
        self.buffer: List[AuditEvent] = []
        self.buffer_size = 100
        
        # Hash chain (ensure tamper-evident)
        self.last_hash = self._load_last_hash()
        
        # Thread lock
        self._lock = threading.Lock()
        
        self.logger.info("AuditLogger initialized")
    
    def _init_database(self):
        """Initialize SQLite database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_events (
                    event_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    level TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    resource TEXT NOT NULL,
                    description TEXT,
                    context TEXT,
                    success INTEGER NOT NULL,
                    duration_ms INTEGER,
                    hash_chain TEXT NOT NULL,
                    checkpoint_id TEXT,
                    approval_status TEXT
                )
            """)
            
            # Indexes for common queries
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_events(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_actor ON audit_events(actor)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_action ON audit_events(action_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_level ON audit_events(level)")
            conn.commit()
    
    def _load_last_hash(self) -> str:
        """Load the last hash from the chain."""
        try:
            if self.json_log.exists():
                with open(self.json_log, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        last_event = json.loads(lines[-1])
                        return last_event.get('hash_chain', '')
        except Exception:
            pass
        return "0" * 64
    
    def _calculate_hash(self, event: AuditEvent) -> str:
        """Calculate hash for this event including previous hash."""
        data = {
            'previous_hash': self.last_hash,
            'event_id': event.event_id,
            'timestamp': event.timestamp,
            'level': event.level.value,
            'action': event.action_type.value,
            'actor': event.actor,
            'resource': event.resource,
            'description': event.description,
            'success': event.success
        }
        hash_data = json.dumps(data, sort_keys=True)
        return hashlib.sha256(hash_data.encode()).hexdigest()
    
    def log(self, action_type: ActionType, actor: str, resource: str,
            description: str = "", level: AuditLevel = AuditLevel.INFO,
            success: bool = True, duration_ms: int = 0,
            context: Optional[Dict] = None) -> AuditEvent:
        """
        Log an audit event.
        
        Args:
            action_type: Type of action performed
            actor: Who performed the action (user_id, system, module)
            resource: What was affected (file, API, etc.)
            description: Human-readable description
            level: Severity level
            success: Whether action succeeded
            duration_ms: Duration in milliseconds
            context: Additional context
            
        Returns:
            Created AuditEvent
        """
        event = AuditEvent(
            event_id=f"evt_{uuid.uuid4().hex[:16]}",
            timestamp=datetime.now().isoformat(),
            level=level,
            action_type=action_type,
            actor=actor,
            resource=resource,
            description=description,
            context=context or {},
            success=success,
            duration_ms=duration_ms,
            hash_chain=""  # Will be calculated
        )
        
        # Calculate hash
        event.hash_chain = self._calculate_hash(event)
        self.last_hash = event.hash_chain
        
        with self._lock:
            self.buffer.append(event)
            
            # Flush if buffer full
            if len(self.buffer) >= self.buffer_size:
                self._flush_buffer()
        
        return event
    
    def log_checkpoint(self, actor: str, checkpoint_name: str, 
                       status: str, context: Optional[Dict] = None) -> str:
        """
        Log a human checkpoint/approval event.
        
        Returns:
            Checkpoint ID
        """
        checkpoint_id = f"ckpt_{uuid.uuid4().hex[:8]}"
        
        self.log(
            action_type=ActionType.JOB_CHECKPOINT,
            actor=actor,
            resource=checkpoint_name,
            description=f"Checkpoint {checkpoint_name}: {status}",
            level=AuditLevel.NOTICE,
            success=status in ["approved", "auto_approved"],
            context={**context, "checkpoint_id": checkpoint_id} if context else {"checkpoint_id": checkpoint_id}
        )
        
        return checkpoint_id
    
    def _flush_buffer(self):
        """Flush buffer to storage."""
        if not self.buffer:
            return
        
        # Write to JSONL
        with open(self.json_log, 'a') as f:
            for event in self.buffer:
                f.write(json.dumps(asdict(event)) + '\n')
        
        # Write to SQLite
        if self.enable_sqlite:
            with sqlite3.connect(self.db_path) as conn:
                for event in self.buffer:
                    conn.execute("""
                        INSERT INTO audit_events 
                        (event_id, timestamp, level, action_type, actor, resource,
                         description, context, success, duration_ms, hash_chain,
                         checkpoint_id, approval_status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        event.event_id,
                        event.timestamp,
                        event.level.value,
                        event.action_type.value,
                        event.actor,
                        event.resource,
                        event.description,
                        json.dumps(event.context),
                        int(event.success),
                        event.duration_ms,
                        event.hash_chain,
                        event.checkpoint_id,
                        event.approval_status
                    ))
                conn.commit()
        
        self.buffer = []
    
    # ==================== QUERY METHODS ====================
    
    def query(self, start_time: Optional[str] = None, 
              end_time: Optional[str] = None,
              actor: Optional[str] = None,
              action_type: Optional[ActionType] = None,
              level: Optional[AuditLevel] = None,
              limit: int = 100) -> List[AuditEvent]:
        """
        Query audit log.
        """
        if not self.enable_sqlite:
            # JSONL fallback
            return self._query_jsonl(start_time, end_time, actor, action_type, level, limit)
        
        with sqlite3.connect(self.data_dir / "audit.db") as conn:
            conn.row_factory = sqlite3.Row
            
            query = "SELECT * FROM audit_events WHERE 1=1"
            params = []
            
            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time)
            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time)
            if actor:
                query += " AND actor = ?"
                params.append(actor)
            if action_type:
                query += " AND action_type = ?"
                params.append(action_type.value)
            if level:
                query += " AND level = ?"
                params.append(level.value)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            rows = conn.execute(query, params).fetchall()
            
            return [
                AuditEvent(
                    event_id=row['event_id'],
                    timestamp=row['timestamp'],
                    level=AuditLevel(row['level']),
                    action_type=ActionType(row['action_type']),
                    actor=row['actor'],
                    resource=row['resource'],
                    description=row['description'],
                    context=json.loads(row['context']) if row['context'] else {},
                    success=bool(row['success']),
                    duration_ms=row['duration_ms'],
                    hash_chain=row['hash_chain'],
                    checkpoint_id=row['checkpoint_id'],
                    approval_status=row['approval_status']
                )
                for row in rows
            ]
    
    def _query_jsonl(self, start_time: Optional[str], end_time: Optional[str],
                    actor: Optional[str], action_type: Optional[ActionType],
                    level: Optional[AuditLevel], limit: int) -> List[AuditEvent]:
        """Fallback query for JSONL."""
        results = []
        
        try:
            with open(self.json_log, 'r') as f:
                for line in reversed(f.readlines()):
                    event_data = json.loads(line)
                    
                    # Apply filters
                    if start_time and event_data['timestamp'] < start_time:
                        continue
                    if end_time and event_data['timestamp'] > end_time:
                        continue
                    if actor and event_data['actor'] != actor:
                        continue
                    if action_type and event_data['action_type'] != action_type.value:
                        continue
                    if level and event_data['level'] != level.value:
                        continue
                    
                    results.append(AuditEvent(**event_data))
                    
                    if len(results) >= limit:
                        break
        except Exception as e:
            self.logger.error(f"JSONL query failed: {e}")
        
        return results
    
    def get_by_checkpoint(self, checkpoint_id: str) -> List[AuditEvent]:
        """Get all events related to a checkpoint."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM audit_events WHERE checkpoint_id = ? OR context LIKE ?",
                (checkpoint_id, f'%"checkpoint_id": "{checkpoint_id}"%')
            ).fetchall()
            
            return [AuditEvent(**{**row, 'context': json.loads(row['context'])}) for row in rows]
    
    def get_statistics(self, period_days: int = 30) -> Dict:
        """Get audit statistics."""
        since = (datetime.now() - timedelta(days=period_days)).isoformat()
        
        events = self.query(start_time=since, limit=10000)
        
        if not events:
            return {'period_days': period_days, 'total_events': 0}
        
        by_type = {}
        by_level = {}
        by_actor = {}
        success_count = 0
        
        for event in events:
            by_type[event.action_type.value] = by_type.get(event.action_type.value, 0) + 1
            by_level[event.level.value] = by_level.get(event.level.value, 0) + 1
            by_actor[event.actor] = by_actor.get(event.actor, 0) + 1
            if event.success:
                success_count += 1
        
        return {
            'period_days': period_days,
            'total_events': len(events),
            'success_rate': (success_count / len(events) * 100) if events else 0,
            'by_action_type': dict(sorted(by_type.items(), key=lambda x: x[1], reverse=True)[:10]),
            'by_level': by_level,
            'by_actor': dict(sorted(by_actor.items(), key=lambda x: x[1], reverse=True)[:10]),
            'critical_events': by_level.get('critical', 0),
            'warning_events': by_level.get('warning', 0)
        }
    
    def verify_chain_integrity(self) -> bool:
        """Verify hash chain integrity."""
        try:
            previous_hash = "0" * 64
            
            with open(self.json_log, 'r') as f:
                for line in f:
                    event = json.loads(line)
                    
                    # Re-calculate hash
                    data = {
                        'previous_hash': previous_hash,
                        'event_id': event['event_id'],
                        'timestamp': event['timestamp'],
                        'level': event['level'],
                        'action': event['action_type'],
                        'actor': event['actor'],
                        'resource': event['resource'],
                        'description': event['description'],
                        'success': event['success']
                    }
                    calculated = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
                    
                    if calculated != event['hash_chain']:
                        self.logger.error(f"Chain integrity failed at event {event['event_id']}")
                        return False
                    
                    previous_hash = event['hash_chain']
            
            return True
        except Exception as e:
            self.logger.error(f"Chain verification failed: {e}")
            return False
    
    # ==================== ALERTING ====================
    
    def check_for_suspicious_activity(self, window_minutes: int = 60) -> List[Dict]:
        """Check for suspicious activity patterns."""
        since = (datetime.now() - timedelta(minutes=window_minutes)).isoformat()
        events = self.query(start_time=since, limit=1000)
        
        alerts = []
        
        # Check for repeated failures
        failed = [e for e in events if not e.success]
        if len(failed) > 10:
            alerts.append({
                'type': 'repeated_failures',
                'severity': 'warning',
                'count': len(failed),
                'message': f'{len(failed)} failed operations in last {window_minutes} minutes'
            })
        
        # Check for critical events
        critical = [e for e in events if e.level == AuditLevel.CRITICAL]
        if critical:
            alerts.append({
                'type': 'critical_events',
                'severity': 'critical',
                'count': len(critical),
                'message': f'{len(critical)} critical events detected'
            })
        
        # Check for unusual volume
        if len(events) > 500:
            alerts.append({
                'type': 'high_volume',
                'severity': 'notice',
                'count': len(events),
                'message': f'Unusually high activity: {len(events)} events'
            })
        
        return alerts
    
    # ==================== REPORTING ====================
    
    def generate_report(self, period_days: int = 7) -> str:
        """Generate human-readable audit report."""
        stats = self.get_statistics(period_days)
        alerts = self.check_for_suspicious_activity()
        
        report = f"""
📝 AUDIT LOG REPORT - Last {period_days} Days
{'='*60}

📊 SUMMARY
Total Events: {stats['total_events']}
Success Rate: {stats['success_rate']:.1f}%
Critical Events: {stats.get('critical_events', 0)}

📈 TOP ACTIONS
"""
        for action, count in stats.get('by_action_type', {}).items():
            report += f"  • {action}: {count}\n"
        
        report += "\n👥 TOP ACTORS\n"
        for actor, count in stats.get('by_actor', {}).items():
            report += f"  • {actor}: {count}\n"
        
        if alerts:
            report += "\n🚨 SUSPICIOUS ACTIVITY ALERTS\n"
            for alert in alerts:
                emoji = "🔴" if alert['severity'] == 'critical' else "🟡" if alert['severity'] == 'warning' else "🟢"
                report += f"  {emoji} {alert['message']}\n"
        
        report += f"\n✅ Chain Integrity: {'VERIFIED' if self.verify_chain_integrity() else 'FAILED'}\n"
        report += f"{'='*60}\n"
        
        return report
    
    def close(self):
        """Flush remaining events before closing."""
        self._flush_buffer()
