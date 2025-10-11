"""Utility tools and base classes for HandBrake MCP server.

This module contains shared utilities, documentation classes, and base functionality
used by other tool modules in the HandBrake MCP server.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any, Type
from functools import wraps
from inspect import signature, Parameter
from dataclasses import dataclass

from pydantic import BaseModel, Field

from handbrake_mcp.services.handbrake import get_handbrake_service, TranscodeJob
from handbrake_mcp.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class ToolDocumentation:
    """Container for comprehensive tool documentation."""

    name: str
    description: str
    summary: str
    parameters: Dict[str, Dict[str, Any]]
    examples: List[Dict[str, Any]]
    returns: Dict[str, Any]
    notes: List[str]
    warnings: List[str]
    related_tools: List[str]
    categories: List[str]
    version: str = "1.0.0"

    def get_multiline_description(self) -> str:
        """Get the full multiline description."""
        lines = []
        lines.append(f"[TOOL] {self.name.upper()}")
        lines.append("")
        lines.append(self.description)
        lines.append("")

        if self.summary:
            lines.append(f"SUMMARY: {self.summary}")
            lines.append("")

        if self.parameters:
            lines.append("PARAMETERS:")
            for param_name, param_info in self.parameters.items():
                lines.append(f"  - {param_name}: {param_info.get('description', 'No description')}")
                if 'type' in param_info:
                    lines.append(f"    Type: {param_info['type']}")
                if 'default' in param_info:
                    lines.append(f"    Default: {param_info['default']}")
                if 'required' in param_info:
                    lines.append(f"    Required: {param_info['required']}")
                lines.append("")

        if self.examples:
            lines.append("EXAMPLES:")
            for i, example in enumerate(self.examples, 1):
                lines.append(f"  {i}. {example.get('description', 'Example')}")
                if 'code' in example:
                    lines.append(f"     {example['code']}")
                lines.append("")

        if self.returns:
            lines.append("RETURNS:")
            lines.append(f"  {self.returns.get('description', 'No return description')}")
            if 'type' in self.returns:
                lines.append(f"  Type: {self.returns['type']}")
            lines.append("")

        if self.notes:
            lines.append("NOTES:")
            for note in self.notes:
                lines.append(f"  - {note}")
            lines.append("")

        if self.warnings:
            lines.append("WARNINGS:")
            for warning in self.warnings:
                lines.append(f"  - {warning}")
            lines.append("")

        if self.related_tools:
            lines.append("RELATED TOOLS:")
            for tool in self.related_tools:
                lines.append(f"  - {tool}")
            lines.append("")

        lines.append(f"Version: {self.version}")
        return "\n".join(lines)

    def get_basic_description(self) -> str:
        """Get a basic single-line description."""
        return self.summary or self.description.split('.')[0] + '.'

    def get_detailed_description(self) -> str:
        """Get a detailed but concise description."""
        return f"{self.description} (Version: {self.version})"


def tool_documentation(
    name: str,
    description: str = "",
    summary: str = "",
    parameters: Optional[Dict[str, Dict[str, Any]]] = None,
    examples: Optional[List[Dict[str, Any]]] = None,
    returns: Optional[Dict[str, Any]] = None,
    notes: Optional[List[str]] = None,
    warnings: Optional[List[str]] = None,
    related_tools: Optional[List[str]] = None,
    categories: Optional[List[str]] = None,
    version: str = "1.0.0"
):
    """
    Decorator for comprehensive tool documentation.

    Args:
        name: Tool name
        description: Full multiline description
        summary: Brief summary (single line)
        parameters: Parameter documentation
        examples: Usage examples
        returns: Return value documentation
        notes: Additional notes
        warnings: Important warnings
        related_tools: Related tool names
        categories: Tool categories
        version: Tool version

    Returns:
        Decorated function with comprehensive documentation
    """
    def decorator(func: Callable) -> Callable:
        # Create documentation object
        doc = ToolDocumentation(
            name=name,
            description=description,
            summary=summary,
            parameters=parameters or {},
            examples=examples or [],
            returns=returns or {},
            notes=notes or [],
            warnings=warnings or [],
            related_tools=related_tools or [],
            categories=categories or [],
            version=version
        )

        # Store documentation on the function
        func._tool_documentation = doc

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper
    return decorator


def get_all_tool_documentation() -> Dict[str, ToolDocumentation]:
    """Get documentation for all registered tools."""
    # This will be populated when tools are registered
    return getattr(get_all_tool_documentation, '_docs', {})


# Tool registration is now handled via @mcp.tool() decorators
# This function is deprecated and kept for backward compatibility

    # Tools registered successfully - MCP protocol handles this silently


class TranscodeRequest(BaseModel):
    """Request model for the transcode_video tool with FastMCP 2.12 compliant schema."""
    input_path: str = Field(
        ...,
        description="Absolute or relative path to the input video file. Supports common formats: MP4, MKV, AVI, MOV, M4V, etc.",
        min_length=1,
        max_length=1000,
        examples=["/videos/input.mp4", "C:\\videos\\input.mkv", "./movie.avi"]
    )
    output_path: str = Field(
        ...,
        description="Absolute or relative path where the transcoded file will be saved. Format determined by file extension.",
        min_length=1,
        max_length=1000,
        examples=["/videos/output.mkv", "C:\\videos\\output.mp4", "./encoded_video.webm"]
    )
    preset: Optional[str] = Field(
        settings.default_preset,
        description=f"HandBrake preset name for encoding. If not provided, uses '{settings.default_preset}'",
        min_length=1,
        max_length=100,
        examples=["Fast 1080p30", "HQ 1080p30", "Very Fast 1080p30", "Apple 1080p30 Surround"]
    )
    options: Optional[Dict[str, str]] = Field(
        default_factory=dict,
        description="Additional HandBrake CLI options as key-value pairs",
        examples=[{"quality": "20", "encoder": "x264", "audio": "copy"}]
    )


class TranscodeResponse(BaseModel):
    """Response model for the transcode_video tool with FastMCP 2.12 compliant schema."""
    job_id: str = Field(
        ...,
        description="Unique identifier for tracking the transcode job",
        min_length=1,
        max_length=100,
        examples=["job_12345", "batch_001_001", "transcode_2025_01_22_143022"]
    )
    status: str = Field(
        ...,
        description="Current status of the transcode job",
        pattern="^(queued|processing|completed|failed|cancelled)$",
        examples=["queued", "processing", "completed", "failed"]
    )
    input_path: str = Field(
        ...,
        description="Path to the input video file",
        min_length=1,
        max_length=1000,
        examples=["/videos/input.mp4", "C:\\videos\\input.mkv"]
    )
    output_path: str = Field(
        ...,
        description="Path where the output file will be saved",
        min_length=1,
        max_length=1000,
        examples=["/videos/output.mkv", "C:\\videos\\output.mp4"]
    )


class JobStatusResponse(BaseModel):
    """Response model for job status with FastMCP 2.12 compliant schema."""
    job_id: str = Field(
        ...,
        description="Unique identifier of the transcode job",
        min_length=1,
        max_length=100,
        examples=["job_12345", "batch_001_001"]
    )
    status: str = Field(
        ...,
        description="Current status of the transcode job",
        pattern="^(queued|processing|completed|failed|cancelled|not_found)$",
        examples=["queued", "processing", "completed", "failed"]
    )
    progress: float = Field(
        ...,
        description="Progress percentage of the transcode job",
        ge=0.0,
        le=100.0,
        examples=[0.0, 25.5, 50.0, 75.2, 100.0]
    )
    error: Optional[str] = Field(
        None,
        description="Error message if the job failed",
        examples=["HandBrake CLI not found", "Input file not found", "Encoding failed"]
    )
    input_path: str = Field(
        ...,
        description="Path to the input video file",
        min_length=1,
        max_length=1000,
        examples=["/videos/input.mp4", "C:\\videos\\input.mkv"]
    )
    output_path: str = Field(
        ...,
        description="Path where the output file will be saved",
        min_length=1,
        max_length=1000,
        examples=["/videos/output.mkv", "C:\\videos\\output.mp4"]
    )
