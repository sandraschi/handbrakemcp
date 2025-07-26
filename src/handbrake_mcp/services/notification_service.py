"""Notification service for sending alerts and updates."""
import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

import aiohttp
from pydantic import BaseModel, EmailStr

from handbrake_mcp.core.config import settings

logger = logging.getLogger(__name__)


class NotificationRecipient(BaseModel):
    """Recipient for notifications."""
    email: Optional[EmailStr] = None
    webhook_url: Optional[str] = None


class NotificationService:
    """Service for sending notifications."""
    
    def __init__(self):
        """Initialize the notification service."""
        self.recipients: List[NotificationRecipient] = []
        self.enabled_events: List[str] = settings.webhook_events
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def initialize(self):
        """Initialize the notification service."""
        self.session = aiohttp.ClientSession()
    
    async def shutdown(self):
        """Shut down the notification service."""
        if self.session:
            await self.session.close()
            self.session = None
    
    def add_recipient(self, recipient: NotificationRecipient):
        """Add a notification recipient."""
        self.recipients.append(recipient)
    
    def remove_recipient(self, recipient: NotificationRecipient):
        """Remove a notification recipient."""
        self.recipients.remove(recipient)
    
    def set_enabled_events(self, events: List[str]):
        """Set the list of enabled notification events."""
        self.enabled_events = events
    
    async def notify(self, event_type: str, data: Dict[str, Any]):
        """Send a notification for an event.
        
        Args:
            event_type: Type of event (e.g., 'job_started', 'job_completed')
            data: Event data to include in the notification
        """
        if event_type not in self.enabled_events:
            return
        
        notification = {
            "event": event_type,
            "timestamp": asyncio.get_event_loop().time(),
            "data": data,
        }
        
        # Send notifications to all recipients
        tasks = []
        for recipient in self.recipients:
            if recipient.webhook_url:
                tasks.append(self._send_webhook(recipient.webhook_url, notification))
            if recipient.email:
                tasks.append(self._send_email(recipient.email, notification))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _send_webhook(self, url: str, data: Dict[str, Any]):
        """Send a webhook notification."""
        if not self.session:
            logger.warning("Webhook not sent: session not initialized")
            return
        
        try:
            async with self.session.post(url, json=data) as response:
                if response.status >= 400:
                    logger.error(
                        f"Webhook failed with status {response.status}: {await response.text()}"
                    )
        except Exception as e:
            logger.error(f"Error sending webhook to {url}: {e}")
    
    async def _send_email(self, email: str, data: Dict[str, Any]):
        """Send an email notification.
        
        Note: This is a placeholder. In a real implementation, you would use
        an email service like SendGrid, Mailgun, or an SMTP server.
        """
        logger.info(f"[EMAIL] To: {email}, Data: {json.dumps(data, indent=2)}")
        # Implementation would go here


# Global instance
notification_service = NotificationService()
