#!/usr/bin/env python3
"""
Cross-Platform Presence - Unified context follows user across:
- WhatsApp
- Discord
- Telegram
- Email
- Web chat

User starts task on WhatsApp → Continues on Discord → Context preserved
"""

import json
import logging
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import threading


class Platform(Enum):
    """Supported platforms."""
    WHATSAPP = "whatsapp"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    EMAIL = "email"
    WEB = "web"
    SMS = "sms"
    SLACK = "slack"


class MessageType(Enum):
    """Types of messages/tasks."""
    TASK_START = "task_start"
    TASK_UPDATE = "task_update"
    TASK_COMPLETE = "task_complete"
    QUESTION = "question"
    ANSWER = "answer"
    FILE_SHARE = "file_share"
    REMINDER = "reminder"


@dataclass
class PlatformMessage:
    """A message across any platform."""
    message_id: str
    platform: Platform
    user_id: str
    content: str
    timestamp: datetime
    message_type: MessageType
    thread_id: Optional[str]  # Groups related messages
    metadata: Dict[str, Any]
    synced: bool = False


@dataclass
class UserSession:
    """User session spanning multiple platforms."""
    session_id: str
    user_id: str
    active_platforms: List[Platform]
    current_task: Optional[str]
    context_threads: Dict[str, List[str]]  # thread_id -> message_ids
    started_at: datetime
    last_activity: datetime
    preferences: Dict[str, Any]


class CrossPlatformPresence:
    """
    Manages unified user presence across all platforms.
    Context follows the user regardless of platform.
    """
    
    def __init__(self, omnibot=None, sync_dir: Optional[str] = None):
        self.logger = logging.getLogger("Omnibot.CrossPlatformPresence")
        self.omnibot = omnibot
        
        # Storage
        self.sync_dir = Path(sync_dir) if sync_dir else Path(__file__).parent / "sync_data"
        self.sync_dir.mkdir(parents=True, exist_ok=True)
        
        # Session management
        self.active_sessions: Dict[str, UserSession] = {}
        self.message_history: Dict[str, PlatformMessage] = {}
        
        # Sync tracking
        self.last_sync_time = datetime.now()
        self.pending_sync: List[PlatformMessage] = []
        
        # Platform adapters (would be actual integrations)
        self.adapters: Dict[Platform, Any] = {}
        
        # Context persistence
        self.context_file = self.sync_dir / "context_state.json"
        self._load_context()
        
        # Thread lock for concurrent access
        self._lock = threading.Lock()
        
        self.logger.info("CrossPlatformPresence initialized")
    
    def _load_context(self):
        """Load persisted context state."""
        if self.context_file.exists():
            try:
                data = json.loads(self.context_file.read_text())
                self.last_sync_time = datetime.fromisoformat(data.get("last_sync", datetime.now().isoformat()))
                self.logger.info("Loaded persisted context")
            except Exception as e:
                self.logger.error(f"Failed to load context: {e}")
    
    def _save_context(self):
        """Save context state."""
        try:
            data = {
                "last_sync": datetime.now().isoformat(),
                "active_sessions": len(self.active_sessions),
                "pending_messages": len(self.pending_sync)
            }
            self.context_file.write_text(json.dumps(data, indent=2, default=str))
        except Exception as e:
            self.logger.error(f"Failed to save context: {e}")
    
    # ==================== SESSION MANAGEMENT ====================
    
    def start_session(self, user_id: str, platform: Platform) -> UserSession:
        """
        Start or resume a user session.
        
        Args:
            user_id: Unique user identifier
            platform: Platform where user is active
            
        Returns:
            UserSession object
        """
        session_id = f"{user_id}_{datetime.now().strftime('%Y%m%d')}"
        
        with self._lock:
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                if platform not in session.active_platforms:
                    session.active_platforms.append(platform)
                    self.logger.info(f"User {user_id} now active on {platform.value}")
                session.last_activity = datetime.now()
            else:
                session = UserSession(
                    session_id=session_id,
                    user_id=user_id,
                    active_platforms=[platform],
                    current_task=None,
                    context_threads={},
                    started_at=datetime.now(),
                    last_activity=datetime.now(),
                    preferences=self._load_user_preferences(user_id)
                )
                self.active_sessions[session_id] = session
                self.logger.info(f"Started new session for {user_id} on {platform.value}")
        
        self._save_context()
        return session
    
    def end_session(self, user_id: str, platform: Optional[Platform] = None):
        """
        End a user session or remove from specific platform.
        
        Args:
            user_id: User identifier
            platform: Platform to leave, or None for all
        """
        session_id = f"{user_id}_{datetime.now().strftime('%Y%m%d')}"
        
        with self._lock:
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                if platform:
                    if platform in session.active_platforms:
                        session.active_platforms.remove(platform)
                        self.logger.info(f"User {user_id} left {platform.value}")
                    if not session.active_platforms:
                        del self.active_sessions[session_id]
                        self.logger.info(f"Session ended for {user_id}")
                else:
                    del self.active_sessions[session_id]
                    self.logger.info(f"All sessions ended for {user_id}")
        
        self._save_context()
    
    def _load_user_preferences(self, user_id: str) -> Dict:
        """Load user preferences for cross-platform behavior."""
        pref_file = self.sync_dir / f"user_{user_id}_prefs.json"
        if pref_file.exists():
            try:
                return json.loads(pref_file.read_text())
            except Exception:
                pass
        
        # Default preferences
        return {
            "preferred_platforms": ["web", "discord"],
            "notification_preferences": {
                "urgent": ["whatsapp", "sms"],
                "normal": ["discord", "telegram"],
                "low": ["email"]
            },
            "sync_enabled": True,
            "context_ttl_hours": 24
        }
    
    # ==================== MESSAGE SYNCING ====================
    
    def sync_message(self, message: PlatformMessage, target_platforms: Optional[List[Platform]] = None):
        """
        Sync a message across platforms.
        
        Args:
            message: Message to sync
            target_platforms: Platforms to sync to, or None for all active
        """
        if not target_platforms:
            # Get user's active platforms
            session = self.active_sessions.get(message.user_id)
            if session:
                target_platforms = [p for p in session.active_platforms if p != message.platform]
        
        if not target_platforms:
            return
        
        for platform in target_platforms:
            self._send_to_platform(platform, message)
        
        message.synced = True
        self.logger.debug(f"Synced message {message.message_id} to {len(target_platforms)} platforms")
    
    def _send_to_platform(self, platform: Platform, message: PlatformMessage):
        """Send message to specific platform."""
        adapter = self.adapters.get(platform)
        if adapter:
            try:
                adapter.send(message)
            except Exception as e:
                self.logger.error(f"Failed to send to {platform.value}: {e}")
        else:
            self.logger.debug(f"No adapter for {platform.value}, queuing for later")
            self.pending_sync.append(message)
    
    def receive_message(self, platform: Platform, user_id: str, content: str,
                       message_type: MessageType = MessageType.QUESTION,
                       metadata: Optional[Dict] = None) -> PlatformMessage:
        """
        Receive a message from any platform.
        
        Args:
            platform: Source platform
            user_id: User identifier
            content: Message content
            message_type: Type of message
            metadata: Additional metadata
            
        Returns:
            Created PlatformMessage
        """
        # Ensure session exists
        session = self.start_session(user_id, platform)
        
        # Create message
        message = PlatformMessage(
            message_id=f"{platform.value}_{datetime.now().timestamp()}",
            platform=platform,
            user_id=user_id,
            content=content,
            timestamp=datetime.now(),
            message_type=message_type,
            thread_id=session.current_task,
            metadata=metadata or {},
            synced=False
        )
        
        # Store message
        self.message_history[message.message_id] = message
        
        # Update session
        if message.thread_id:
            if message.thread_id not in session.context_threads:
                session.context_threads[message.thread_id] = []
            session.context_threads[message.thread_id].append(message.message_id)
        
        self._save_context()
        self.logger.info(f"Received message from {user_id} on {platform.value}")
        
        return message
    
    # ==================== CONTEXT MANAGEMENT ====================
    
    def get_context(self, user_id: str, thread_id: Optional[str] = None) -> Dict:
        """
        Get user context across platforms.
        
        Args:
            user_id: User identifier
            thread_id: Optional thread to get context for
            
        Returns:
            Context dictionary
        """
        session_id = f"{user_id}_{datetime.now().strftime('%Y%m%d')}"
        session = self.active_sessions.get(session_id)
        
        if not session:
            return {"error": "No active session"}
        
        context = {
            "user_id": user_id,
            "active_platforms": [p.value for p in session.active_platforms],
            "current_task": session.current_task,
            "session_duration": (datetime.now() - session.started_at).total_seconds() // 60,
            "recent_messages": []
        }
        
        # Get recent messages
        if thread_id and thread_id in session.context_threads:
            message_ids = session.context_threads[thread_id][-10:]  # Last 10 messages
            context["recent_messages"] = [
                {
                    "platform": self.message_history[mid].platform.value,
                    "content": self.message_history[mid].content,
                    "type": self.message_history[mid].message_type.value,
                    "time": self.message_history[mid].timestamp.isoformat()
                }
                for mid in message_ids if mid in self.message_history
            ]
        else:
            # Get recent messages across all threads
            recent = [
                msg for msg in self.message_history.values()
                if msg.user_id == user_id and 
                (datetime.now() - msg.timestamp) < timedelta(hours=24)
            ]
            recent.sort(key=lambda x: x.timestamp, reverse=True)
            
            context["recent_messages"] = [
                {
                    "platform": msg.platform.value,
                    "content": msg.content[:100],  # Truncate
                    "type": msg.message_type.value,
                    "time": msg.timestamp.isoformat()
                }
                for msg in recent[:10]
            ]
        
        return context
    
    def set_task(self, user_id: str, task_description: str):
        """
        Set current task for user session.
        
        Args:
            user_id: User identifier
            task_description: Task description
        """
        session_id = f"{user_id}_{datetime.now().strftime('%Y%m%d')}"
        
        with self._lock:
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                session.current_task = task_description
                if task_description not in session.context_threads:
                    session.context_threads[task_description] = []
                self.logger.info(f"Set task for {user_id}: {task_description}")
    
    def get_task(self, user_id: str) -> Optional[str]:
        """Get current task for user."""
        session_id = f"{user_id}_{datetime.now().strftime('%Y%m%d')}"
        session = self.active_sessions.get(session_id)
        return session.current_task if session else None
    
    def continue_on_platform(self, user_id: str, from_platform: Platform, to_platform: Platform,
                            message: str = "Continuing conversation") -> bool:
        """
        Notify user to continue on another platform.
        
        Example:
            User starts task on WhatsApp → Bot suggests: "Switch to Discord for better file sharing"
        
        Args:
            user_id: User identifier
            from_platform: Current platform
            to_platform: Target platform
            message: Continuation message
            
        Returns:
            True if notification sent
        """
        self.logger.info(f"Prompting {user_id} to move from {from_platform.value} to {to_platform.value}")
        
        # Send notification to target platform
        notification = PlatformMessage(
            message_id=f"notify_{datetime.now().timestamp()}",
            platform=to_platform,
            user_id=user_id,
            content=f"📱 Continuing from {from_platform.value}: {message}",
            timestamp=datetime.now(),
            message_type=MessageType.REMINDER,
            thread_id=self.get_task(user_id),
            metadata={"source_platform": from_platform.value}
        )
        
        self._send_to_platform(to_platform, notification)
        return True
    
    # ==================== PLATFORM ADAPTERS ====================
    
    def register_adapter(self, platform: Platform, adapter: Any):
        """
        Register a platform adapter.
        
        Args:
            platform: Platform type
            adapter: Adapter instance with send() method
        """
        self.adapters[platform] = adapter
        self.logger.info(f"Registered adapter for {platform.value}")
    
    def get_supported_platforms(self) -> List[str]:
        """Get list of supported platform names."""
        return [p.value for p in Platform]
    
    # ==================== SMART SYNC ====================
    
    def should_sync_to_platform(self, message: PlatformMessage, target_platform: Platform) -> bool:
        """
        Determine if a message should be synced to a platform.
        
        Considers:
        - User preferences
        - Message urgency
        - Platform capabilities
        """
        session = self.active_sessions.get(message.user_id)
        if not session:
            return False
        
        prefs = session.preferences
        
        # Check user preference for this platform
        if not prefs.get("sync_enabled", True):
            return False
        
        # Check notification preferences by urgency
        urgency = message.metadata.get("urgency", "normal")
        preferred_platforms = prefs.get("notification_preferences", {}).get(urgency, [])
        
        return target_platform.value in preferred_platforms
    
    def format_for_platform(self, content: str, platform: Platform) -> str:
        """
        Format content for specific platform.
        
        WhatsApp: No markdown
        Discord: Rich embeds, colored text
        Telegram: HTML or Markdown
        Email: Full HTML
        """
        if platform == Platform.WHATSAPP:
            # Remove markdown, keep simple formatting
            return content.replace("**", "*").replace("##", "")
        elif platform == Platform.DISCORD:
            # Enhance with Discord markdown
            return content
        elif platform == Platform.EMAIL:
            # Wrap in HTML
            return f"<html><body>{content}</body></html>"
        else:
            return content
    
    # ==================== UTILITIES ====================
    
    def get_session_summary(self, user_id: Optional[str] = None) -> Dict:
        """Get summary of active sessions."""
        if user_id:
            session_id = f"{user_id}_{datetime.now().strftime('%Y%m%d')}"
            session = self.active_sessions.get(session_id)
            if session:
                return {
                    "user_id": user_id,
                    "active_platforms": [p.value for p in session.active_platforms],
                    "current_task": session.current_task,
                    "session_duration_minutes": (datetime.now() - session.started_at).total_seconds() // 60,
                    "total_messages": len([m for m in self.message_history.values() if m.user_id == user_id])
                }
            return {"error": "No active session"}
        
        return {
            "total_active_sessions": len(self.active_sessions),
            "total_messages_today": len([
                m for m in self.message_history.values()
                if m.timestamp.date() == datetime.now().date()
            ]),
            "active_users": list(set(s.user_id for s in self.active_sessions.values()))
        }