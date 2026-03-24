#!/usr/bin/env python3
"""
Status Updater - Tracks and updates project status.
"""

from datetime import datetime
from typing import Dict, Optional


class StatusUpdater:
    """Update and track project status."""
    
    def __init__(self):
        self.statuses: Dict[str, Dict] = {}
    
    def update_status(self, project_id: str, status: str, notes: str = "") -> Dict:
        """Update project status."""
        self.statuses[project_id] = {
            "status": status,
            "last_updated": datetime.now().isoformat(),
            "notes": notes
        }
        return self.statuses[project_id]
    
    def get_status(self, project_id: str) -> Optional[Dict]:
        """Get current project status."""
        return self.statuses.get(project_id)
    
    def format_for_client(self, project_id: str) -> str:
        """Format status for client communication."""
        status = self.get_status(project_id)
        if not status:
            return "Status not available"
        
        return f"Status: {status['status']} (updated {status['last_updated'][:10]})"