"""Configuration management for HandBrake MCP."""
import os
from pathlib import Path
from typing import List, Optional

from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    """Application settings."""

    # Server configuration
    host: str = Field("0.0.0.0", env="HOST")
    port: int = Field(8000, env="PORT")
    log_level: str = Field("info", env="LOG_LEVEL")
    api_key: Optional[str] = Field(None, env="API_KEY")

    # HandBrake configuration
    hbb_path: str = Field("HandBrakeCLI", env="HBB_PATH")
    default_preset: str = Field("Fast 1080p30", env="DEFAULT_PRESET")
    
    # Watch folder configuration
    watch_folders: List[Path] = Field(default_factory=list, env="WATCH_FOLDERS")
    processed_folder: Optional[Path] = Field(None, env="PROCESSED_FOLDER")
    delete_original_after_processing: bool = Field(False, env="DELETE_ORIGINAL_AFTER_PROCESSING")
    file_patterns: List[str] = Field(
        default_factory=lambda: ["*.mp4", "*.mkv", "*.avi", "*.mov", "*.m4v"],
        env="FILE_PATTERNS"
    )
    
    # Notification configuration
    webhook_url: Optional[str] = Field(None, env="WEBHOOK_URL")
    webhook_events: List[str] = Field(
        default_factory=lambda: ["job_started", "job_completed", "job_failed"],
        env="WEBHOOK_EVENTS"
    )
    email_notifications: bool = Field(False, env="EMAIL_NOTIFICATIONS")
    email_recipients: List[str] = Field(default_factory=list, env="EMAIL_RECIPIENTS")
    email_sender: Optional[str] = Field(None, env="EMAIL_SENDER")

    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    @validator("watch_folders", pre=True)
    def parse_watch_folders(cls, v):
        """Parse watch folders from comma-separated string."""
        if isinstance(v, str):
            return [Path(folder.strip()) for folder in v.split(",") if folder.strip()]
        return v or []

    @validator("webhook_events", pre=True)
    def parse_webhook_events(cls, v):
        """Parse webhook events from comma-separated string."""
        if isinstance(v, str):
            return [event.strip() for event in v.split(",") if event.strip()]
        return v or []

    @validator("log_level")
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
