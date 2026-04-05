from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "info"
    api_key: str | None = None

    # MCP Transport configuration
    mcp_transport: str = "stdio"
    mcp_host: str = "127.0.0.1"
    mcp_port: int = 8000

    # HandBrake configuration
    hbb_path: str = "HandBrakeCLI"
    default_preset: str = "Fast 1080p30"

    # Watch folder configuration
    watch_folders: list[Path] = Field(default_factory=list)
    processed_folder: Path | None = None
    delete_original_after_processing: bool = False
    file_patterns: list[str] = Field(
        default_factory=lambda: ["*.mp4", "*.mkv", "*.avi", "*.mov", "*.m4v"]
    )

    # Notification configuration
    webhook_url: str | None = None
    webhook_events: list[str] = Field(
        default_factory=lambda: ["job_started", "job_completed", "job_failed"]
    )
    email_notifications: bool = False
    email_recipients: list[str] = Field(default_factory=list)
    email_sender: str | None = None

    # SMTP configuration for email notifications
    smtp_server: str | None = Field(None, description="SMTP server hostname")
    smtp_port: int | None = Field(587, description="SMTP server port")
    smtp_username: str | None = Field(None, description="SMTP username")
    smtp_password: str | None = Field(None, description="SMTP password")
    smtp_use_tls: bool = Field(True, description="Use TLS encryption for SMTP")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="",  # Allow environment variables without prefix
    )

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
