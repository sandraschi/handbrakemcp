"""Configuration management for HandBrake MCP."""
import os
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class Settings(BaseModel):
    """Application settings."""

    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "info"
    api_key: Optional[str] = None

    # MCP Transport configuration
    mcp_transport: str = "stdio"
    mcp_host: str = "127.0.0.1"
    mcp_port: int = 8000

    # HandBrake configuration
    hbb_path: str = "HandBrakeCLI"
    default_preset: str = "Fast 1080p30"

    # Watch folder configuration
    watch_folders: List[Path] = Field(default_factory=list)
    processed_folder: Optional[Path] = None
    delete_original_after_processing: bool = False
    file_patterns: List[str] = Field(
        default_factory=lambda: ["*.mp4", "*.mkv", "*.avi", "*.mov", "*.m4v"]
    )

    # Notification configuration
    webhook_url: Optional[str] = None
    webhook_events: List[str] = Field(
        default_factory=lambda: ["job_started", "job_completed", "job_failed"]
    )
    email_notifications: bool = False
    email_recipients: List[str] = Field(default_factory=list)
    email_sender: Optional[str] = None

    # SMTP configuration for email notifications
    smtp_server: Optional[str] = Field(None, description="SMTP server hostname")
    smtp_port: Optional[int] = Field(587, description="SMTP server port")
    smtp_username: Optional[str] = Field(None, description="SMTP username")
    smtp_password: Optional[str] = Field(None, description="SMTP password")
    smtp_use_tls: bool = Field(True, description="Use TLS encryption for SMTP")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "env_prefix": "",  # Allow environment variables without prefix
    }

    @field_validator("watch_folders", mode="before")
    @classmethod
    def parse_watch_folders(cls, v):
        """Parse watch folders from comma-separated string."""
        if isinstance(v, str):
            return [Path(folder.strip()) for folder in v.split(",") if folder.strip()]
        return v or []

    @field_validator("webhook_events", mode="before")
    @classmethod
    def parse_webhook_events(cls, v):
        """Parse webhook events from comma-separated string."""
        if isinstance(v, str):
            return [event.strip() for event in v.split(",") if event.strip()]
        return v or []

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ["debug", "info", "warning", "error", "critical"]
        if v.lower() not in valid_levels:
            raise ValueError(f"Invalid log level. Must be one of: {', '.join(valid_levels)}")
        return v.lower()


def get_config() -> Settings:
    """Get application settings."""
    return Settings()


# Global settings instance
settings = get_config()
