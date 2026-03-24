"""
Memory Consolidator.
Manages migration of memories between tiers.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

class MemoryConsolidator:
    """
    Consolidates memories across tiers:
    - Hot → Warm: When low activity or session end
    - Warm → Cold: When highly valuable
    - Cold → Archive: When outdated but potentially useful
    """
    
    def __init__(self, hot_memory, warm_memory, cold_memory):
        self.hot = hot_memory
        self.warm = warm_memory
        self.cold = cold_memory
        self.logger = logging.getLogger("Omnibot.MemoryConsolidator")
    
    def run(self, force: bool = False) -> Dict:
        """
        Run consolidation process.
        
        Args:
            force: Force consolidation even if not due
            
        Returns:
            Consolidation report
        """
        self.logger.info("Starting memory consolidation...")
        
        report = {
            "started_at": datetime.now().isoformat(),
            "migrations": [],
            "cleaned": {},
            "errors": []
        }
        
        try:
            # Promote valuable warm memories to cold
            warm_to_cold = self._promote_warm_to_cold()
            report["migrations"].extend(warm_to_cold)
        except Exception as e:
            report["errors"].append(f"Warm→Cold migration failed: {e}")
        
        try:
            # Demote inactive hot memories to warm
            hot_to_warm = self._demote_hot_to_warm()
            report["migrations"].extend(hot_to_warm)
        except Exception as e:
            report["errors"].append(f"Hot→Warm migration failed: {e}")
        
        try:
            # Clean up expired entries
            report["cleaned"] = self._cleanup_expired()
        except Exception as e:
            report["errors"].append(f"Cleanup failed: {e}")
        
        # Mark critical decisions
        try:
            critical_marked = self._mark_critical_decisions()
            report["critical_decisions_marked"] = critical_marked
        except Exception as e:
            report["errors"].append(f"Critical marking failed: {e}")
        
        report["completed_at"] = datetime.now().isoformat()
        
        self.logger.info(f"Consolidation complete: {len(report['migrations'])} migrations, "
                        f"{report['cleaned'].get('total', 0)} cleaned")
        
        return report
    
    def _promote_warm_to_cold(self) -> List[Dict]:
        """Promote highly valuable warm memories to cold storage."""
        migrations = []
        
        # Get recent warm memories
        recent = self.warm.get_recent(days=30)
        
        for entry in recent:
            # Check if valuable enough for cold
            if self._is_valuable_for_cold(entry):
                mem_id = self.cold.store(
                    content=entry["content"],
                    tags=entry.get("tags", []) + ["auto_promoted"],
                    section=self._infer_section(entry)
                )
                
                migrations.append({
                    "direction": "warm→cold",
                    "source_id": entry["id"],
                    "target_id": mem_id,
                    "reason": "High value content"
                })
        
        return migrations
    
    def _demote_hot_to_warm(self) -> List[Dict]:
        """Demote inactive hot memories to warm storage."""
        migrations = []
        
        items = self.hot.get_all()
        
        for item in items:
            # Check if should demote
            if self._should_demote_from_hot(item):
                mem_id = self.warm.store(
                    content=item["content"],
                    tags=item.get("tags", []) + ["from_hot_memory"]
                )
                
                migrations.append({
                    "direction": "hot→warm",
                    "source_id": item["id"],
                    "target_id": mem_id,
                    "reason": "Low activity, session persistence"
                })
        
        return migrations
    
    def _cleanup_expired(self) -> Dict:
        """Clean up expired entries from all tiers."""
        cleaned = {
            "hot": self.hot.cleanup_expired(),
            "warm": self.warm.cleanup_expired(),
            "total": 0
        }
        cleaned["total"] = cleaned["hot"] + cleaned["warm"]
        return cleaned
    
    def _mark_critical_decisions(self) -> int:
        """Mark critical decision-related memories for cold storage."""
        count = 0
        
        # Scan recent warm memories for decisions
        recent = self.warm.get_recent(days=7)
        
        critical_keywords = [
            "decision", "important", "critical", "approve",
            "reject", "chose", "selected", "determined"
        ]
        
        for entry in recent:
            content = entry.get("content", "").lower()
            
            if any(kw in content for kw in critical_keywords):
                # Already in cold? Check
                if not self._is_in_cold(entry):
                    self.cold.store(
                        content=f"Decision recorded: {entry['content']}",
                        tags=entry.get("tags", []) + ["decision", "important"],
                        section="Decisions"
                    )
                    count += 1
        
        return count
    
    def _is_valuable_for_cold(self, entry: Dict) -> bool:
        """Determine if a warm entry is valuable enough for cold storage."""
        valuable_patterns = [
            "important", "critical", "config", "preference",
            "decision", "key", "essential", "always", "never"
        ]
        
        content = entry.get("content", "").lower()
        tags = [t.lower() for t in entry.get("tags", [])]
        
        # Check content
        if any(p in content for p in valuable_patterns):
            return True
        
        # Check tags
        valuable_tags = ["important", "critical", "config", "preference"]
        if any(t in valuable_tags for t in tags):
            return True
        
        return False
    
    def _should_demote_from_hot(self, item: Dict) -> bool:
        """Determine if a hot item should be demoted."""
        # Low access count
        if item.get("access_count", 0) < 3:
            return True
        
        # Older than 24 hours
        created = datetime.fromisoformat(item["created_at"])
        if datetime.now() - created > timedelta(hours=24):
            return True
        
        return False
    
    def _is_in_cold(self, entry: Dict) -> bool:
        """Check if entry already exists in cold storage."""
        # Simple check - in a real implementation would be more thorough
        cold_items = self.cold.search(entry.get("content", "")[:50], max_results=1)
        return len(cold_items) > 0
    
    def _infer_section(self, entry: Dict) -> str:
        """Infer appropriate section for cold storage."""
        content = entry.get("content", "").lower()
        tags = entry.get("tags", [])
        
        if any(t in tags for t in ["decision", "choice"]):
            return "Decisions"
        if any(t in tags for t in ["config", "setting"]):
            return "Configuration"
        if any(t in tags for t in ["preference", "like", "want"]):
            return "Preferences"
        if "important" in content or "critical" in content:
            return "Important Notes"
        
        return "General"