#!/usr/bin/env python3
"""
Message Drafter - Draft professional client communications.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ClientMessage:
    """A drafted client message."""
    message_id: str
    client_name: str
    subject: str
    content: str
    message_type: str
    tone: str


class MessageDrafter:
    """
    Draft professional messages for client communication.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("Omnibot.MessageDrafter")
    
    def draft_status_update(self, client_name: str, project_name: str,
                           progress: int, milestones: List[str]) -> ClientMessage:
        """
        Draft a project status update.
        
        Args:
            client_name: Client name
            project_name: Project name
            progress: Completion percentage
            milestones: Recent milestones
            
        Returns:
            Drafted message
        """
        subject = f"Project Update - {project_name}: {progress}% Complete"
        
        content = f"""Hi {client_name},

Quick update on {project_name} - we're now {progress}% complete!

Recent progress:
"""
        
        for milestone in milestones:
            content += f"✓ {milestone}\n"
        
        content += """
Everything is on track. Next milestone coming up soon!

Best regards"""
        
        return ClientMessage(
            message_id=f"msg_{int(datetime.now().timestamp())}",
            client_name=client_name,
            subject=subject,
            content=content,
            message_type="status_update",
            tone="professional"
        )
    
    def draft_proposal_message(self, client_name: str, job_title: str,
                              value_prop: str) -> ClientMessage:
        """Draft initial proposal message."""
        subject = f"Proposal for {job_title}"
        
        content = f"""Hi {client_name},

Thank you for the opportunity to work on {job_title}.

{value_prop}

I bring 5+ years of experience and a proven track record of delivering high-quality results on time.

I'd love to schedule a quick call to discuss your specific needs and how I can help.

Best regards"""
        
        return ClientMessage(
            message_id=f"prop_{int(datetime.now().timestamp())}",
            client_name=client_name,
            subject=subject,
            content=content,
            message_type="proposal",
            tone="professional"
        )
    
    def draft_delivery_message(self, client_name: str, project_name: str,
                              deliverables: List[str]) -> ClientMessage:
        """Draft project delivery message."""
        subject = f"{project_name} - Deliverables Ready for Review"
        
        content = f"""Hi {client_name},

Excited to share that {project_name} is complete and ready for your review!

Deliverables included:
"""
        
        for item in deliverables:
            content += f"• {item}\n"
        
        content += """
Please review at your convenience. I'm happy to make any adjustments needed.

Looking forward to your feedback!

Best regards"""
        
        return ClientMessage(
            message_id=f"del_{int(datetime.now().timestamp())}",
            client_name=client_name,
            subject=subject,
            content=content,
            message_type="delivery",
            tone="professional"
        )