"""Notification service for sending alerts and updates."""
import asyncio
import json
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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
    """Service for sending notifications via webhooks and email."""

    def __init__(self):
        """Initialize the notification service."""
        self.recipients: List[NotificationRecipient] = []
        self.enabled_events: List[str] = settings.webhook_events
        self.session: Optional[aiohttp.ClientSession] = None
        self.smtp_server: Optional[str] = None
        self.smtp_port: Optional[int] = None
        self.smtp_username: Optional[str] = None
        self.smtp_password: Optional[str] = None
        self.smtp_use_tls: bool = True
    
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
        """Send an email notification using SMTP.

        Args:
            email: Recipient email address
            data: Notification data to include in the email

        Raises:
            smtplib.SMTPException: If email sending fails
        """
        # If no SMTP configuration is set, log and skip
        if not self.smtp_server:
            logger.warning(f"Email notification skipped for {email}: SMTP not configured")
            return

        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = settings.email_sender or "handbrake-mcp@localhost"
            msg['To'] = email
            msg['Subject'] = f"HandBrake MCP Notification: {data.get('event', 'Unknown')}"

            # Create HTML body
            html_body = f"""
            <html>
            <body>
            <h2>HandBrake MCP Notification</h2>
            <p><strong>Event:</strong> {data.get('event', 'Unknown')}</p>
            <p><strong>Timestamp:</strong> {data.get('timestamp', 'Unknown')}</p>
            <h3>Details:</h3>
            <pre>{json.dumps(data.get('data', {}), indent=2)}</pre>
            </body>
            </html>
            """

            # Create plain text fallback
            text_body = f"""
HandBrake MCP Notification

Event: {data.get('event', 'Unknown')}
Timestamp: {data.get('timestamp', 'Unknown')}

Details:
{json.dumps(data.get('data', {}), indent=2)}
            """

            # Attach parts
            msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))

            # Send email
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self._send_email_sync,
                msg,
                email
            )

            logger.info(f"Email notification sent to {email}")

        except Exception as e:
            logger.error(f"Failed to send email to {email}: {e}")
            raise

    def _send_email_sync(self, msg: MIMEMultipart, email: str):
        """Synchronous email sending function for executor."""
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port or 587)
            server.starttls()  # Always use TLS

            if self.smtp_username and self.smtp_password:
                server.login(self.smtp_username, self.smtp_password)

            server.sendmail(msg['From'], email, msg.as_string())
            server.quit()

        except Exception as e:
            logger.error(f"SMTP error sending to {email}: {e}")
            raise

    def configure_smtp(self, server: str, port: Optional[int] = None,
                      username: Optional[str] = None, password: Optional[str] = None,
                      use_tls: bool = True):
        """Configure SMTP settings for email notifications.

        Args:
            server: SMTP server hostname (e.g., 'smtp.gmail.com')
            port: SMTP port (default: 587 for TLS)
            username: SMTP username/email
            password: SMTP password/app password
            use_tls: Whether to use TLS encryption
        """
        self.smtp_server = server
        self.smtp_port = port or 587
        self.smtp_username = username
        self.smtp_password = password
        self.smtp_use_tls = use_tls
        logger.info(f"SMTP configured for server: {server}")


# Global instance
notification_service = NotificationService()
