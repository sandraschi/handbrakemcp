"""MCP tools for HandBrake MCP server."""
import logging
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from handbrake_mcp.services.handbrake import get_handbrake_service, TranscodeJob
from handbrake_mcp.core.config import settings

logger = logging.getLogger(__name__)


def register_tools_with_mcp(mcp_instance):
    """Register all tools with the FastMCP instance using FastMCP 2.12 best practices."""

    # Import FastMCP tools
    from fastmcp.tools import Tool

    # Create and register tool objects with proper metadata
    # FastMCP 2.12 supports name, description, and tags parameters
    tools = [
        Tool.from_function(
            transcode_video,
            name="transcode_video",
            description="Transcode a single video file using HandBrake with professional quality settings",
            tags={"video", "transcoding", "handbrake", "media"}
        ),
        Tool.from_function(
            batch_transcode,
            name="batch_transcode",
            description="Transcode multiple video files in batch processing mode",
            tags={"video", "transcoding", "batch", "bulk"}
        ),
        Tool.from_function(
            get_job_status,
            name="get_job_status",
            description="Check the status and progress of a video transcode job",
            tags={"status", "monitoring", "jobs", "progress"}
        ),
        Tool.from_function(
            cancel_job,
            name="cancel_job",
            description="Cancel a running or queued video transcode job",
            tags={"control", "jobs", "cancel", "management"}
        ),
        Tool.from_function(
            get_presets,
            name="get_presets",
            description="Get a list of all available HandBrake presets for video encoding",
            tags={"presets", "configuration", "info", "settings"}
        ),
        Tool.from_function(
            get_loaded_models,
            name="get_loaded_models",
            description="Get list of loaded models (presets) - MCP compatibility endpoint",
            tags={"presets", "models", "compatibility", "mcp"}
        ),
        Tool.from_function(
            get_provider_status,
            name="get_provider_status",
            description="Get status and system information about the HandBrake video processing provider",
            tags={"status", "info", "system", "health"}
        )
    ]

    # Add all tools to the MCP instance
    for tool in tools:
        mcp_instance.add_tool(tool)


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


async def transcode_video(
    input_path: str,
    output_path: str,
    preset: Optional[str] = None,
    options: Optional[Dict[str, str]] = None,
) -> TranscodeResponse:
    """
    Transcode a video file using HandBrake with professional quality settings.

    This tool provides high-quality video transcoding using HandBrake's advanced
    encoding engine. It supports various formats and presets for optimal output.

    Args:
        input_path: Absolute or relative path to the input video file.
                   Supports common formats: MP4, MKV, AVI, MOV, M4V, etc.
        output_path: Absolute or relative path where the transcoded file will be saved.
                    The output format is determined by the file extension.
        preset: HandBrake preset name to use for encoding. If not provided,
               uses the default preset from configuration. Examples:
               "Fast 1080p30", "HQ 1080p30", "Very Fast 1080p30"
        options: Additional HandBrake CLI options as key-value pairs.
                Example: {"quality": "20", "encoder": "x264"}

    Returns:
        TranscodeResponse: Object containing:
            - job_id: Unique identifier for tracking the transcode job
            - status: Current status ("queued", "processing", "completed", "failed")
            - input_path: Path to the input file
            - output_path: Path to the output file

    Raises:
        FileNotFoundError: If the input file doesn't exist
        ValueError: If the preset is not valid or parameters are incorrect
    """
    job_id = await get_handbrake_service().transcode(
        input_path=input_path,
        output_path=output_path,
        preset=preset,
        options=options or {},
    )
    
    return TranscodeResponse(
        job_id=job_id,
        status="queued",
        input_path=input_path,
        output_path=output_path,
    )


async def batch_transcode(
    jobs: List[Dict[str, str]],
    default_preset: Optional[str] = None,
) -> List[TranscodeResponse]:
    """
    Transcode multiple video files in efficient batch processing mode.

    This tool enables processing multiple videos simultaneously using HandBrake's
    batch processing capabilities. Each job runs independently and can have
    different settings.

    Args:
        jobs: List of job dictionaries, each containing:
            - input_path: Path to the input video file
            - output_path: Path where the output file will be saved
            - preset: (optional) HandBrake preset to use for this job
            - options: (optional) Additional HandBrake options as key-value pairs
        default_preset: Default preset to use for jobs that don't specify one.
                       If not provided, uses the global default preset.

    Returns:
        List[TranscodeResponse]: List of response objects for each job, containing:
            - job_id: Unique identifier for tracking each transcode job
            - status: Current status ("queued", "processing", "completed", "failed")
            - input_path: Path to the input file
            - output_path: Path to the output file
            - error: Error message if the job failed

    Example:
        jobs = [
            {
                "input_path": "/videos/movie1.mp4",
                "output_path": "/videos/movie1_encoded.mkv",
                "preset": "Fast 1080p30"
            },
            {
                "input_path": "/videos/movie2.mp4",
                "output_path": "/videos/movie2_encoded.mp4"
            }
        ]

    Raises:
        ValueError: If the jobs list is empty or contains invalid job specifications
    """
    results = []
    for job in jobs:
        try:
            job_id = await get_handbrake_service().transcode(
                input_path=job["input_path"],
                output_path=job["output_path"],
                preset=job.get("preset", default_preset or settings.default_preset),
                options=job.get("options", {}),
            )
            results.append(TranscodeResponse(
                job_id=job_id,
                status="queued",
                input_path=job["input_path"],
                output_path=job["output_path"],
            ))
        except Exception as e:
            results.append(TranscodeResponse(
                job_id=f"error_{len(results)}",
                status="failed",
                input_path=job.get("input_path", ""),
                output_path=job.get("output_path", ""),
                error=str(e),
            ))
    
    return results


async def get_job_status(job_id: str) -> JobStatusResponse:
    """
    Get the current status and progress of a video transcode job.

    This tool provides real-time monitoring of video transcoding jobs, including
    progress percentage, current status, and any error messages.

    Args:
        job_id: Unique identifier of the transcode job to check.
               This ID is returned when a job is created via transcode_video or batch_transcode.

    Returns:
        JobStatusResponse: Object containing:
            - job_id: Unique identifier of the job
            - status: Current status ("queued", "processing", "completed", "failed", "cancelled")
            - progress: Progress percentage (0-100)
            - error: Error message if the job failed (null if no error)
            - input_path: Path to the input file being processed
            - output_path: Path to the output file being created

    Examples:
        - Queued: status="queued", progress=0
        - Processing: status="processing", progress=45
        - Completed: status="completed", progress=100
        - Failed: status="failed", progress=0, error="HandBrake error message"

    Raises:
        ValueError: If the job_id is not found or is invalid
    """
    job = await get_handbrake_service().get_job_status(job_id)
    if not job:
        return JobStatusResponse(
            job_id=job_id,
            status="not_found",
            progress=0.0,
            error="Job not found",
            input_path="",
            output_path="",
        )
    
    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        progress=job.progress,
        error=job.error,
        input_path=str(job.input_path),
        output_path=str(job.output_path),
    )


async def cancel_job(job_id: str) -> bool:
    """
    Cancel a running or queued video transcode job.

    This tool allows you to stop a transcode job that is currently running or
    waiting in the queue. Useful for stopping long-running jobs or freeing up
    system resources.

    Args:
        job_id: Unique identifier of the transcode job to cancel.
               Must be a valid job ID returned from transcode_video or batch_transcode.

    Returns:
        bool: True if the job was successfully cancelled, False if:
            - The job was not found
            - The job was already completed
            - The job was already cancelled
            - The job cannot be cancelled (already finishing)

    Notes:
        - Cancelled jobs cannot be resumed - they must be restarted
        - Partial output files may be left behind depending on when cancellation occurs
        - System resources are freed immediately upon cancellation

    Raises:
        ValueError: If the job_id format is invalid
    """
    return await get_handbrake_service().cancel_job(job_id)


async def get_presets() -> List[str]:
    """
    Get a comprehensive list of all available HandBrake presets for video encoding.

    This tool provides access to all HandBrake presets installed on the system,
    including built-in presets and any custom presets. Presets define encoding
    settings optimized for different use cases and quality levels.

    Returns:
        List[str]: Alphabetically sorted list of preset names available in HandBrake.
                 Common presets include:
                 - "Fast 1080p30" - Quick encoding with good quality
                 - "HQ 1080p30" - High quality encoding, slower
                 - "Very Fast 1080p30" - Fastest encoding, lower quality
                 - "Fast 720p30" - 720p resolution preset
                 - "Apple 1080p30 Surround" - Apple TV compatible
                 - "Android 1080p30" - Android device compatible

    Notes:
        - The actual list depends on the HandBrake installation
        - Preset names may vary between HandBrake versions
        - Custom presets will also be included if installed

    Raises:
        RuntimeError: If HandBrake CLI is not available or not functioning
    """
    return await get_handbrake_service().get_presets()


async def get_loaded_models() -> List[str]:
    """
    Get a list of loaded models (presets) - MCP compatibility endpoint.

    This tool provides the same functionality as get_presets() but uses MCP
    terminology for better integration with MCP-compatible clients and tools.
    It serves as a compatibility layer for systems that expect a "models" endpoint.

    Returns:
        List[str]: List of loaded model names (HandBrake presets). This is identical
                 to the output of get_presets() and includes all available encoding
                 configurations.

    Notes:
        - This function is functionally identical to get_presets()
        - Provided for MCP protocol compatibility
        - Returns the same data with the same format

    See Also:
        get_presets(): The primary function for retrieving preset information
    """
    return await get_handbrake_service().get_presets()


async def get_provider_status() -> Dict[str, str]:
    """
    Get comprehensive status and system information about the HandBrake video processing provider.

    This tool provides detailed information about the HandBrake MCP server's health,
    configuration, and capabilities. It's useful for monitoring, debugging, and
    integration purposes.

    Returns:
        Dict[str, str]: Dictionary containing provider information:
            - status: Current operational status ("ready", "error", "maintenance")
            - version: HandBrake MCP server version (from pyproject.toml)
            - handbrake_version: Version of the underlying HandBrake CLI (dynamically detected)
            - supported_presets: List of available HandBrake presets
            - system_info: Basic system information (OS, architecture)
            - max_concurrent_jobs: Maximum number of concurrent transcoding jobs
            - active_jobs: Number of currently active jobs
            - error: Error message if status is "error"

    Example:
        {
            "status": "ready",
            "version": "1.0.0",
            "handbrake_version": "1.5.1",
            "supported_presets": ["Fast 1080p30", "HQ 1080p30", ...],
            "system_info": "Windows 10 x64",
            "max_concurrent_jobs": 5,
            "active_jobs": 2
        }

    Notes:
        - Use this endpoint to verify the server is functioning correctly
        - Check supported_presets to see available encoding options
        - Error status indicates a problem with HandBrake CLI or configuration

    Raises:
        RuntimeError: If unable to determine provider status
    """
    try:
        handbrake_service = get_handbrake_service()

        # Get dynamic information
        handbrake_version = await handbrake_service.get_handbrake_version()
        supported_presets = await handbrake_service.get_presets()
        active_jobs = len([job for job in handbrake_service.jobs.values() if job.status == "processing"])

        # Get server version from pyproject.toml
        import os
        server_version = "unknown"
        try:
            pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
            if pyproject_path.exists():
                import tomllib
                with open(pyproject_path, "rb") as f:
                    data = tomllib.load(f)
                    server_version = data.get("project", {}).get("version", "unknown")
        except Exception as e:
            logger.warning(f"Could not read version from pyproject.toml: {e}")

        # Get system information
        system_info = f"{os.name} {os.sys.platform}"

        return {
            "status": "ready",
            "version": server_version,
            "handbrake_version": handbrake_version,
            "supported_presets": supported_presets,
            "system_info": system_info,
            "max_concurrent_jobs": handbrake_service._max_concurrent_jobs,
            "active_jobs": active_jobs,
        }
    except Exception as e:
        logger.exception("Error getting provider status")
        return {
            "status": "error",
            "error": str(e),
        }
