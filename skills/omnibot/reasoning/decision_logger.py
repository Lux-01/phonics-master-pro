"""
Decision Logger.
Records decisions for future reference and learning.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import json
import hashlib

class DecisionLogger:
    """
    Logs decisions made by Omnibot.
    Enables learning from past decisions.
    """
    
    def __init__(self, log_dir: Path):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Current session log
        self.session_log = []
        self.current_file = self._get_current_file()
    
    def log(self, decision: str, context: Dict, result: str,
            metadata: Optional[Dict] = None):
        """
        Log a decision.
        
        Args:
            decision: The decision made
            context: Decision context
            result: Decision result
            metadata: Optional additional metadata
        """
        entry = {
            "id": self._generate_id(decision, context),
            "timestamp": datetime.now().isoformat(),
            "decision": decision,
            "context": self._sanitize_context(context),
            "result": result,
            "metadata": metadata or {},
            "searchable": self._extract_searchable_text(decision, context, result)
        }
        
        self.session_log.append(entry)
        
        # Auto-save every 10 entries
        if len(self.session_log) >= 10:
            self.save()
    
    def query(self, query: str, limit: int = 20) -> List[Dict]:
        """
        Query decision history.
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            Matching decisions
        """
        results = []
        query_lower = query.lower()
        
        # Search session log
        for entry in self.session_log:
            if query_lower in entry.get("searchable", "").lower():
                results.append(entry)
        
        # Search archived logs
        for log_file in self._get_log_files():
            try:
                entries = self._read_log_file(log_file)
                for entry in entries:
                    if query_lower in entry.get("searchable", "").lower():
                        results.append(entry)
            except Exception:
                continue
        
        # Sort by timestamp (newest first)
        results.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return results[:limit]
    
    def get_recent(self, count: int = 20) -> List[Dict]:
        """Get recent decisions."""
        all_entries = self.session_log.copy()
        
        # Get from today's file
        if self.current_file.exists():
            all_entries.extend(self._read_log_file(self.current_file))
        
        # Sort and return
        all_entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return all_entries[:count]
    
    def get_decision_stats(self) -> Dict:
        """Get decision statistics."""
        total_in_session = len(self.session_log)
        
        # Count from files
        total_in_files = 0
        for log_file in self._get_log_files():
            try:
                entries = self._read_log_file(log_file)
                total_in_files += len(entries)
            except Exception:
                continue
        
        # Analyze recent decisions
        recent = self.get_recent(100)
        success_count = sum(1 for d in recent if "success" in d.get("result", "").lower())
        fail_count = sum(1 for d in recent if "fail" in d.get("result", "").lower())
        
        return {
            "total_logged": total_in_session + total_in_files,
            "session_count": total_in_session,
            "files_count": total_in_files,
            "recent_success_rate": f"{success_count}%" if recent else "N/A",
            "recent_fail_count": fail_count
        }
    
    def save(self):
        """Save session log to disk."""
        if not self.session_log:
            return
        
        self.current_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Append to file
        with open(self.current_file, 'a') as f:
            for entry in self.session_log:
                f.write(json.dumps(entry) + "\n")
        
        # Clear session log
        self.session_log = []
    
    def _get_current_file(self) -> Path:
        """Get current day's log file."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        return self.log_dir / f"decisions_{date_str}.jsonl"
    
    def _get_log_files(self) -> List[Path]:
        """Get all log files."""
        if self.log_dir.exists():
            return sorted(self.log_dir.glob("decisions_*.jsonl"), reverse=True)
        return []
    
    def _read_log_file(self, file_path: Path) -> List[Dict]:
        """Read a log file."""
        entries = []
        if file_path.exists():
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            entries.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        return entries
    
    def _generate_id(self, decision: str, context: Dict) -> str:
        """Generate unique ID for entry."""
        content = f"{decision}_{json.dumps(context, sort_keys=True, default=str)}_{datetime.now().isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _sanitize_context(self, context: Dict) -> Dict:
        """Remove sensitive data from context."""
        sanitized = {}
        sensitive_keys = ["password", "key", "token", "secret", "credential", 
                         "private_key", "api_key", "auth"]
        
        for key, value in context.items():
            if any(s in key.lower() for s in sensitive_keys):
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_context(value)
            else:
                sanitized[key] = value
        
        return sanitized
    
    def _extract_searchable_text(self, decision: str, context: Dict, result: str) -> str:
        """Extract searchable text from decision."""
        parts = [decision, result]
        
        # Add context values
        for value in context.values():
            if isinstance(value, str):
                parts.append(value)
            elif isinstance(value, (list, tuple)):
                parts.extend(str(v) for v in value if isinstance(v, str))
        
        return " ".join(parts)