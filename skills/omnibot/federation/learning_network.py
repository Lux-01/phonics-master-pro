#!/usr/bin/env python3
"""
Federated Learning Network - Securely shares improvements:
- New successful code patterns
- API discoveries (rate limits, pricing)
- Failure recovery strategies

WITHOUT exposing user data or secrets
"""

import json
import hashlib
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
import threading


class KnowledgeType(Enum):
    """Types of knowledge that can be shared."""
    CODE_PATTERN = "code_pattern"
    API_DISCOVERY = "api_discovery"
    RECOVERY_STRATEGY = "recovery_strategy"
    PERFORMANCE_TIP = "performance_tip"
    SECURITY_NOTICE = "security_notice"
    LIBRARY_UPDATE = "library_update"


@dataclass
class KnowledgeEntry:
    """A piece of knowledge to share or receive."""
    entry_id: str
    knowledge_type: KnowledgeType
    category: str  # e.g., 'openai', 'python', 'error_handling'
    content: str  # Sanitized content
    hash_signature: str  # To detect duplicates
    created_at: datetime
    source_node: str  # Node identifier (anonymized)
    version: str  # Software version
    verified: bool = False
    usage_count: int = 0
    success_rate: float = 0.0


@dataclass
class SecurityPolicy:
    """Security policy for federation."""
    allow_sharing: bool = True
    allow_receiving: bool = True
    anonymize_source: bool = True
    require_verification: bool = True
    max_sharing_frequency: int = 10  # per hour
    blocked_categories: Optional[Set[str]] = None


class FederatedLearning:
    """
    Federated learning system for sharing improvements
    while maintaining privacy and security.
    """
    
    def __init__(self, omnibot=None, data_dir: Optional[str] = None):
        self.logger = logging.getLogger("Omnibot.FederatedLearning")
        self.omnibot = omnibot
        
        # Storage
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent / "federation_data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Knowledge repositories
        self.local_knowledge: List[KnowledgeEntry] = []
        self.shared_knowledge: List[KnowledgeEntry] = []
        self.received_knowledge: List[KnowledgeEntry] = []
        
        # Security
        self.security_policy = SecurityPolicy()
        self._load_security_policy()
        
        # Node identification (anonymized)
        self.node_id = self._generate_node_id()
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Load existing knowledge
        self._load_knowledge()
        
        self.logger.info(f"FederatedLearning initialized (node: {self.node_id[:8]}...)")
    
    def _generate_node_id(self) -> str:
        """Generate an anonymized node identifier."""
        node_file = self.data_dir / "node_id"
        if node_file.exists():
            return node_file.read_text().strip()
        
        # Generate new ID
        import uuid
        node_id = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()[:16]
        node_file.write_text(node_id)
        return node_id
    
    def _load_security_policy(self):
        """Load security policy."""
        policy_file = self.data_dir / "security_policy.json"
        if policy_file.exists():
            try:
                data = json.loads(policy_file.read_text())
                self.security_policy = SecurityPolicy(**data)
            except Exception as e:
                self.logger.error(f"Failed to load security policy: {e}")
    
    def _save_security_policy(self):
        """Save security policy."""
        try:
            policy_file = self.data_dir / "security_policy.json"
            policy_file.write_text(json.dumps(asdict(self.security_policy), indent=2))
        except Exception as e:
            self.logger.error(f"Failed to save security policy: {e}")
    
    def _load_knowledge(self):
        """Load existing knowledge."""
        # Local knowledge
        local_file = self.data_dir / "local_knowledge.json"
        if local_file.exists():
            try:
                data = json.loads(local_file.read_text())
                self.local_knowledge = [KnowledgeEntry(**k) for k in data.get("entries", [])]
            except Exception as e:
                self.logger.error(f"Failed to load local knowledge: {e}")
        
        # Received knowledge
        received_file = self.data_dir / "received_knowledge.json"
        if received_file.exists():
            try:
                data = json.loads(received_file.read_text())
                self.received_knowledge = [KnowledgeEntry(**k) for k in data.get("entries", [])]
            except Exception as e:
                self.logger.error(f"Failed to received knowledge: {e}")
    
    def _save_knowledge(self):
        """Save knowledge repositories."""
        try:
            # Local
            local_file = self.data_dir / "local_knowledge.json"
            local_file.write_text(json.dumps({
                "last_updated": datetime.now().isoformat(),
                "entries": [asdict(k) for k in self.local_knowledge]
            }, indent=2, default=str))
            
            # Received
            received_file = self.data_dir / "received_knowledge.json"
            received_file.write_text(json.dumps({
                "last_updated": datetime.now().isoformat(),
                "entries": [asdict(k) for k in self.received_knowledge]
            }, indent=2, default=str))
            
        except Exception as e:
            self.logger.error(f"Failed to save knowledge: {e}")
    
    # ==================== LOCAL LEARNING ====================
    
    def learn_from_experience(self, experience_type: str, content: str,
                           success: bool, category: str = "general") -> Optional[KnowledgeEntry]:
        """
        Learn from local experience and potentially share.
        
        Args:
            experience_type: Type of experience
            content: Sanitized content (NO secrets)
            success: Whether it was successful
            category: Knowledge category
            
        Returns:
            KnowledgeEntry if created
        """
        # Determine knowledge type
        knowledge_type = self._classify_experience(experience_type)
        
        # Sanitize content (ensure no secrets)
        sanitized = self._sanitize_content(content)
        if not sanitized:
            self.logger.warning("Content too sensitive to share")
            return None
        
        # Create knowledge entry
        entry = KnowledgeEntry(
            entry_id=f"local_{datetime.now().timestamp()}",
            knowledge_type=knowledge_type,
            category=category,
            content=sanitized,
            hash_signature=hashlib.sha256(sanitized.encode()).hexdigest()[:16],
            created_at=datetime.now(),
            source_node=self.node_id if not self.security_policy.anonymize_source else "anonymous",
            version=self._get_version(),
            success_rate=1.0 if success else 0.0,
            usage_count=1
        )
        
        with self._lock:
            self.local_knowledge.append(entry)
        
        self._save_knowledge()
        self.logger.info(f"Learned from experience: {entry.entry_id}")
        
        # Consider sharing
        if self._should_share(entry):
            self.share_knowledge(entry)
        
        return entry
    
    def _classify_experience(self, experience_type: str) -> KnowledgeType:
        """Classify experience into knowledge type."""
        mapping = {
            "api_discovery": KnowledgeType.API_DISCOVERY,
            "api_error": KnowledgeType.API_DISCOVERY,
            "recovery": KnowledgeType.RECOVERY_STRATEGY,
            "fix": KnowledgeType.RECOVERY_STRATEGY,
            "optimization": KnowledgeType.PERFORMANCE_TIP,
            "performance": KnowledgeType.PERFORMANCE_TIP,
            "security": KnowledgeType.SECURITY_NOTICE,
            "vulnerability": KnowledgeType.SECURITY_NOTICE,
            "pattern": KnowledgeType.CODE_PATTERN,
            "code": KnowledgeType.CODE_PATTERN,
            "library": KnowledgeType.LIBRARY_UPDATE
        }
        return mapping.get(experience_type.lower(), KnowledgeType.CODE_PATTERN)
    
    def _sanitize_content(self, content: str) -> Optional[str]:
        """
        Sanitize content to ensure no secrets or PII.
        
        Removes:
        - API keys
        - Passwords
        - Private keys
        - Personal identifiers
        """
        import re
        
        # Patterns to redact
        patterns = [
            (r'sk-[a-zA-Z0-9]{48}', '[API_KEY_REDACTED]'),  # OpenAI
            (r'ghp_[a-zA-Z0-9]{36}', '[GITHUB_TOKEN_REDACTED]'),  # GitHub
            (r'[a-f0-9]{64}', '[HASH_REDACTED]'),  # Private keys
            (r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}', '[EMAIL_REDACTED]'),
            (r'\b(?:\d{1,3}\.){3}\d{1,3}\b', '[IP_REDACTED]'),
        ]
        
        sanitized = content
        for pattern, replacement in patterns:
            sanitized = re.sub(pattern, replacement, sanitized)
        
        # Check if too much was redacted
        if sanitized.count('[*_REDACTED]') > content.count(' ') / 10:
            return None  # Too sensitive
        
        return sanitized
    
    def _get_version(self) -> str:
        """Get current software version."""
        return "1.0.0"  # Would be dynamic in real implementation
    
    def _should_share(self, entry: KnowledgeEntry) -> bool:
        """Determine if knowledge should be shared."""
        if not self.security_policy.allow_sharing:
            return False
        
        if entry.knowledge_type == KnowledgeType.SECURITY_NOTICE:
            # Always share security notices
            return True
        
        # Check if duplicate exists
        for existing in self.shared_knowledge:
            if existing.hash_signature == entry.hash_signature:
                return False  # Already shared
        
        # Check success rate threshold
        if entry.success_rate < 0.8:
            return False
        
        # Check category not blocked
        if self.security_policy.blocked_categories and entry.category in self.security_policy.blocked_categories:
            return False
        
        return True
    
    # ==================== KNOWLEDGE SHARING ====================
    
    def share_knowledge(self, entry: KnowledgeEntry) -> bool:
        """
        Share knowledge with the federation.
        
        Args:
            entry: Knowledge to share
            
        Returns:
            True if shared successfully
        """
        if not self.security_policy.allow_sharing:
            return False
        
        self.logger.info(f"Sharing knowledge: {entry.entry_id}")
        
        # In real implementation, this would send to federation servers
        # For now, we simulate by adding to shared list
        
        with self._lock:
            self.shared_knowledge.append(entry)
        
        self._save_knowledge()
        return True
    
    def receive_knowledge(self, entry: KnowledgeEntry) -> bool:
        """
        Receive knowledge from the federation.
        
        Args:
            entry: Received knowledge
            
        Returns:
            True if accepted
        """
        if not self.security_policy.allow_receiving:
            return False
        
        # Verify knowledge
        if self.security_policy.require_verification and not self._verify_knowledge(entry):
            self.logger.warning(f"Knowledge failed verification: {entry.entry_id}")
            return False
        
        # Check for duplicates
        for existing in self.received_knowledge:
            if existing.hash_signature == entry.hash_signature:
                return False  # Already have this
        
        # Add to received knowledge
        with self._lock:
            self.received_knowledge.append(entry)
        
        self._save_knowledge()
        self.logger.info(f"Received and stored knowledge: {entry.entry_id}")
        return True
    
    def _verify_knowledge(self, entry: KnowledgeEntry) -> bool:
        """Verify received knowledge is safe and valid."""
        # Check content doesn't contain dangerous patterns
        dangerous_patterns = ['eval(', 'exec(', '__import__', 'subprocess', 'os.system']
        
        if entry.knowledge_type == KnowledgeType.CODE_PATTERN:
            for pattern in dangerous_patterns:
                if pattern in entry.content:
                    return False
        
        # Check hash matches
        calculated_hash = hashlib.sha256(entry.content.encode()).hexdigest()[:16]
        if calculated_hash != entry.hash_signature:
            return False
        
        return True
    
    # ==================== KNOWLEDGE RETRIEVAL ====================
    
    def query_knowledge(self, category: Optional[str] = None,
                       knowledge_type: Optional[KnowledgeType] = None,
                       min_success_rate: float = 0.7) -> List[KnowledgeEntry]:
        """
        Query knowledge base for relevant information.
        
        Args:
            category: Filter by category
            knowledge_type: Filter by type
            min_success_rate: Minimum success rate
            
        Returns:
            List of matching entries
        """
        all_knowledge = self.local_knowledge + self.received_knowledge
        
        filtered = all_knowledge
        
        if category:
            filtered = [k for k in filtered if k.category == category]
        
        if knowledge_type:
            filtered = [k for k in filtered if k.knowledge_type == knowledge_type]
        
        filtered = [k for k in filtered if k.success_rate >= min_success_rate]
        
        # Sort by success rate and usage
        filtered.sort(key=lambda k: (k.success_rate, k.usage_count), reverse=True)
        
        return filtered
    
    def get_best_practices(self, category: str, limit: int = 5) -> List[Dict]:
        """
        Get best practices for a category.
        
        Args:
            category: Category to query
            limit: Maximum results
            
        Returns:
            List of best practices
        """
        entries = self.query_knowledge(category=category, min_success_rate=0.8)
        
        return [
            {
                "content": entry.content,
                "type": entry.knowledge_type.value,
                "success_rate": entry.success_rate,
                "usage_count": entry.usage_count,
                "age_days": (datetime.now() - entry.created_at).days,
                "verified": entry.verified
            }
            for entry in entries[:limit]
        ]
    
    def get_api_insights(self, api_name: str) -> List[Dict]:
        """Get shared insights about an API."""
        entries = self.query_knowledge(
            category=api_name,
            knowledge_type=KnowledgeType.API_DISCOVERY
        )
        
        return [
            {
                "insight": entry.content,
                "success_rate": entry.success_rate,
                "from_network": entry.source_node != self.node_id
            }
            for entry in entries
        ]
    
    # ==================== STATISTICS ====================
    
    def get_federation_stats(self) -> Dict:
        """Get federation statistics."""
        return {
            "local_knowledge_count": len(self.local_knowledge),
            "shared_knowledge_count": len(self.shared_knowledge),
            "received_knowledge_count": len(self.received_knowledge),
            "by_type": {
                kt.value: len([k for k in self.local_knowledge + self.received_knowledge 
                              if k.knowledge_type == kt])
                for kt in KnowledgeType
            },
            "total_verified": len([k for k in self.received_knowledge if k.verified]),
            "security_enabled": {
                "anonymize": self.security_policy.anonymize_source,
                "require_verification": self.security_policy.require_verification,
                "allow_sharing": self.security_policy.allow_sharing
            }
        }
    
    def apply_learned_knowledge(self, context: str) -> Optional[str]:
        """
        Try to apply learned knowledge to current context.
        
        Args:
            context: Current task context
            
        Returns:
            Suggestion if applicable
        """
        # Simple keyword matching
        relevant = []
        for entry in self.received_knowledge:
            # Check if keywords match
            if any(keyword in context.lower() and keyword in entry.content.lower() 
                   for keyword in context.lower().split()[:5]):
                relevant.append(entry)
        
        if relevant:
            best = max(relevant, key=lambda k: k.success_rate)
            return f"💡 Federation Tip ({best.success_rate*100:.0f}% success): {best.content[:200]}..."
        
        return None
    
    def report_outcome(self, entry_id: str, success: bool):
        """
        Report outcome of applying knowledge.
        
        Args:
            entry_id: Knowledge entry ID
            success: Whether it helped
        """
        # Update success rate
        for entry in self.received_knowledge + self.local_knowledge:
            if entry.entry_id == entry_id:
                entry.usage_count += 1
                # Update moving average
                entry.success_rate = (entry.success_rate * (entry.usage_count - 1) + (1.0 if success else 0.0)) / entry.usage_count
                self._save_knowledge()
                break
    
    # ==================== SECURITY ====================
    
    def set_security_policy(self, policy: SecurityPolicy):
        """Update security policy."""
        self.security_policy = policy
        self._save_security_policy()
        self.logger.info("Updated security policy")
    
    def redact_sensitive(self, content: str) -> str:
        """Public method to redact sensitive content."""
        result = self._sanitize_content(content)
        return result if result else "[CONTENT_REDACTED_FOR_SECURITY]"