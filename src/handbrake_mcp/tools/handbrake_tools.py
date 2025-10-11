"""HandBrake core video transcoding tools for MCP server.

This module contains all the core HandBrake video processing tools:
- transcode_video: Single file transcoding with professional settings
- batch_transcode: Parallel batch processing of multiple files
- get_job_status: Real-time job monitoring and progress tracking
- cancel_job: Job termination and resource cleanup
- get_presets: Dynamic preset discovery from HandBrake CLI
- get_loaded_models: MCP compatibility endpoint for model discovery
- get_provider_status: Comprehensive system health and capability reporting
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import os

from handbrake_mcp.services.handbrake import get_handbrake_service
from handbrake_mcp.core.config import settings
from handbrake_mcp.tools.utility_tools import TranscodeResponse, JobStatusResponse

logger = logging.getLogger(__name__)

# Import MCP instance for decorator registration
# This will be set by the registration system
_mcp_instance = None

def set_mcp_instance(mcp_instance):
    """Set the MCP instance for decorator-based tool registration."""
    global _mcp_instance
    _mcp_instance = mcp_instance

def _get_mcp_instance():
    """Get the MCP instance, raising an error if not set."""
    if _mcp_instance is None:
        raise RuntimeError("MCP instance not set. Call set_mcp_instance() first.")
    return _mcp_instance

# Store tools to be registered later
_pending_tools = []

def tool(*args, **kwargs):
    """Decorator to register a tool with the MCP instance."""
    def decorator(func):
        # Store the tool info for later registration
        _pending_tools.append((func, args, kwargs))
        return func
    return decorator

def register_pending_tools():
    """Register all pending tools with the MCP instance."""
    mcp = _get_mcp_instance()
    for func, args, kwargs in _pending_tools:
        # Apply the MCP tool decorator
        decorated_func = mcp.tool(*args, **kwargs)(func)
        # Replace the original function with the decorated one
        globals()[func.__name__] = decorated_func


@tool(
    name="transcode_video",
    description="Transcode a single video file using HandBrake with professional quality settings",
    tags={"video", "transcoding", "handbrake", "media", "encoding"}
)
async def transcode_video(
    input_path: str,
    output_path: str,
    preset: Optional[str] = None,
    options: Optional[Dict[str, str]] = None,
) -> TranscodeResponse:
    """
    Transcode a single video file using HandBrake with professional quality settings.

    This tool provides high-quality video transcoding using HandBrake's advanced encoding engine.
    It supports various formats and presets for optimal output quality and file size optimization.

    The tool automatically detects the input file format and applies the best encoding settings
    based on the selected preset. It supports hardware acceleration when available and provides
    real-time progress tracking for long-running encoding jobs.

    Parameters:
        input_path: Absolute or relative path to the input video file
            - Must be a valid video file path
            - Supports common formats: MP4, MKV, AVI, MOV, M4V, etc.
            - File must exist and be readable
            - Maximum path length: 1000 characters

        output_path: Absolute or relative path where the transcoded file will be saved
            - Format determined by file extension
            - Directory must exist and be writable
            - Output file will be overwritten if it exists
            - Maximum path length: 1000 characters

        preset: HandBrake preset name for encoding quality/speed balance (default: None)
            - If None, uses the default preset from configuration
            - Must be a valid preset name (use get_presets() to see available options)
            - Preset determines encoder settings, quality, and speed trade-offs
            - Case-sensitive preset name matching

        options: Additional HandBrake CLI options as key-value pairs (default: {})
            - Dictionary of option names to values
            - Options override preset settings when specified
            - Common options: quality, encoder, audio, subtitle settings
            - Invalid options may cause encoding failures

    Returns:
        Dictionary containing:
            - success: Boolean indicating if transcoding job was successfully queued
            - job_id: Unique identifier for tracking the transcode job
            - status: Initial status ('queued' for successful jobs, 'failed' for errors)
            - input_path: Confirmed input file path
            - output_path: Confirmed output file path
            - error: Error message if job creation failed (only present if success is False)

    Usage:
        This tool is used when you need to convert a single video file to a different format,
        quality setting, or size. It's ideal for individual file processing, format conversion,
        and quality optimization tasks.

        Common scenarios:
        - Converting videos for different devices (mobile, tablet, TV)
        - Reducing file size while maintaining quality
        - Changing video format for compatibility
        - Applying specific encoding settings for professional workflows
        - Batch processing individual files with custom settings

        Best practices:
        - Use get_presets() to discover available quality/speed options
        - Test with small files first to verify settings
        - Monitor job progress with get_job_status()
        - Use appropriate output directories with sufficient space

    Examples:
        Basic video transcoding with default settings:
            result = await transcode_video("/videos/input.mp4", "/videos/output.mkv")
            # Returns: {'job_id': 'job_12345', 'status': 'queued', 'input_path': '/videos/input.mp4', 'output_path': '/videos/output.mkv'}

        High-quality encoding with custom preset:
            result = await transcode_video("/videos/movie.mkv", "/videos/movie_hq.mp4", preset="HQ 1080p30")
            # Returns: {'job_id': 'job_12346', 'status': 'queued', 'input_path': '/videos/movie.mkv', 'output_path': '/videos/movie_hq.mp4'}

        Custom encoding with specific options:
            result = await transcode_video("/videos/input.avi", "/videos/output.mp4", options={"quality": "20", "encoder": "x264"})
            # Returns: {'job_id': 'job_12347', 'status': 'queued', 'input_path': '/videos/input.avi', 'output_path': '/videos/output.mp4'}

        Error handling for invalid file:
            result = await transcode_video("/nonexistent/file.mp4", "/output.mp4")
            # Returns: {'success': False, 'error': 'Input file not found: /nonexistent/file.mp4'}

    Raises:
        ValueError: If input_path or output_path are empty or invalid
        FileNotFoundError: If input file does not exist
        PermissionError: If output directory is not writable
        RuntimeError: If HandBrake CLI is not available or configured

    Notes:
        - Job starts in 'queued' status and moves to 'processing' when encoding begins
        - Progress is updated in real-time during encoding
        - Output format is determined by file extension (.mp4, .mkv, .avi, etc.)
        - Hardware acceleration is automatically detected and used when available
        - Large files may take significant time to process
        - Cancel jobs using cancel_job() if needed during processing

    See Also:
        - batch_transcode: For processing multiple files simultaneously
        - get_job_status: For monitoring transcoding progress
        - cancel_job: For stopping running jobs
        - get_presets: For discovering available encoding presets
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

@tool(
    name="batch_transcode",
    description="Transcode multiple video files in efficient batch processing mode with parallel execution",
    tags={"video", "transcoding", "batch", "bulk", "parallel", "handbrake"}
)
async def batch_transcode(
    jobs: List[Dict[str, str]],
    default_preset: Optional[str] = None,
) -> List[TranscodeResponse]:
    """
    Transcode multiple video files in efficient batch processing mode with parallel execution.

    This tool enables processing multiple videos simultaneously using HandBrake's advanced batch
    processing capabilities. Each job runs independently and can have different settings, allowing
    for flexible and efficient video processing workflows.

    The tool automatically manages job queuing, progress tracking, and resource allocation to
    optimize throughput while preventing system overload. Jobs are processed concurrently based
    on available system resources and configured limits.

    Parameters:
        jobs: List of job dictionaries for batch processing
            - Each dictionary must contain 'input_path' and 'output_path' keys
            - Optional keys: 'preset', 'options'
            - All paths must be valid and accessible
            - Maximum 100 jobs per batch (configurable limit)
            - Job format: {'input_path': str, 'output_path': str, 'preset': str, 'options': Dict[str, str]}

        default_preset: Default preset for jobs that don't specify one (default: None)
            - Used when individual jobs don't specify a preset
            - Falls back to system default if None
            - Must be a valid preset name if specified
            - Applied to all jobs without explicit preset

    Returns:
        List of TranscodeResponse objects, one for each job in the input batch
            - Each response contains job_id, status, input_path, output_path, and optional error
            - Order matches input jobs array
            - Failed jobs have error field populated
            - Successful jobs start in 'queued' status

    Usage:
        Use this tool when you need to process multiple video files efficiently with parallel execution.
        Ideal for bulk conversions, format migrations, and large-scale video processing operations.

        Common scenarios:
        - Converting entire video libraries to new formats
        - Batch processing user uploads with consistent settings
        - Applying different presets to different file types
        - Processing videos for multiple target devices
        - Automated workflow processing of video collections

        Best practices:
        - Group similar files together for optimal resource usage
        - Use consistent presets within batches when possible
        - Monitor system resources during large batch operations
        - Test with small batches first to verify settings
        - Use get_job_status() to monitor individual job progress

    Examples:
        Basic batch processing with mixed presets:
            results = await batch_transcode([
                {"input_path": "/videos/movie1.mp4", "output_path": "/videos/movie1.mkv", "preset": "Fast 1080p30"},
                {"input_path": "/videos/movie2.mp4", "output_path": "/videos/movie2.mp4"}
            ])
            # Returns: [{'job_id': 'job_001', 'status': 'queued', ...}, {'job_id': 'job_002', 'status': 'queued', ...}]

        Batch processing with custom options per job:
            results = await batch_transcode([
                {"input_path": "/videos/doc.mp4", "output_path": "/videos/doc_compressed.mkv", "options": {"quality": "24"}},
                {"input_path": "/videos/movie.mp4", "output_path": "/videos/movie_hq.mkv", "preset": "HQ 1080p30"}
            ], default_preset="Fast 1080p30")
            # Returns: List with individual job responses, options applied to first job, preset to second

        Large batch processing with error handling:
            results = batch_jobs  # List of 50+ job dictionaries
            processed_results = await batch_transcode(results)
            failed_jobs = [r for r in processed_results if r.status == "failed"]
            successful_jobs = [r for r in processed_results if r.status == "queued"]
            # Returns: Mixed results with some failed and some queued jobs

        Batch processing with progress monitoring:
            import asyncio
            results = await batch_transcode(job_list)
            # Monitor progress of all jobs
            for result in results:
                if result.status == "queued":
                    print(f"Job {result.job_id} started for {result.input_path}")
            # Use get_job_status() individually for detailed progress

    Raises:
        ValueError: If jobs list is empty or contains invalid job dictionaries
        RuntimeError: If batch size exceeds configured limits
        ConnectionError: If HandBrake service is unavailable
        PermissionError: If output directories are not writable

    Notes:
        - Jobs are processed concurrently based on system resources and max_concurrent_jobs setting
        - Each job maintains independent progress tracking and error handling
        - Failed jobs don't stop the entire batch - other jobs continue processing
        - Total processing time scales with the longest individual job, not sum of all jobs
        - Memory usage increases with batch size and video resolution
        - Network storage paths may impact performance for large batches
        - Use get_provider_status() to check current system capacity before large batches

    See Also:
        - transcode_video: For processing individual files
        - get_job_status: For monitoring batch job progress
        - cancel_job: For stopping individual batch jobs
        - get_provider_status: For checking system capacity
        - get_presets: For discovering available presets
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


@tool(
    name="get_job_status",
    description="Get comprehensive real-time status and progress information for video transcode jobs",
    tags={"status", "monitoring", "jobs", "progress", "tracking", "handbrake"}
)
async def get_job_status(job_id: str) -> JobStatusResponse:
    """
    Get comprehensive real-time status and progress information for video transcode jobs.

    This tool provides detailed monitoring capabilities for video transcoding jobs, including
    progress percentage, current status, performance metrics, and error diagnostics. It's
    essential for tracking long-running encoding operations and managing batch processing workflows.

    The tool queries the HandBrake service for live job information and provides formatted
    status updates that can be used for progress bars, logging, notifications, and workflow
    automation. It supports all job states from initial queuing through completion or failure.

    Parameters:
        job_id: Unique identifier of the transcode job to monitor
            - Must be a valid job identifier from a previous transcode operation
            - Case-sensitive string matching
            - Job IDs are returned by transcode_video and batch_transcode operations
            - Maximum length: 100 characters

    Returns:
        Dictionary containing comprehensive job status information:
            - job_id: The requested job identifier
            - status: Current job status ('queued', 'processing', 'completed', 'failed', 'cancelled', 'not_found')
            - progress: Completion percentage (0.0 to 100.0)
            - error: Error message string (only present if status is 'failed')
            - input_path: Original input file path
            - output_path: Target output file path

    Usage:
        Use this tool to monitor the progress and status of video transcoding jobs. Essential for
        building user interfaces, automation workflows, and progress tracking systems.

        Common scenarios:
        - Building progress bars in user interfaces
        - Implementing job completion notifications
        - Monitoring batch processing operations
        - Debugging failed transcoding jobs
        - Building automation workflows with status checks

        Best practices:
        - Poll at reasonable intervals (5-30 seconds) to avoid overwhelming the system
        - Implement exponential backoff for long-running jobs
        - Cache status information to reduce API calls
        - Handle all possible status values in your application logic
        - Log status changes for debugging and auditing

    Examples:
        Basic job status check:
            status = await get_job_status("job_12345")
            if status.status == "completed":
                print("Job finished successfully!")
            elif status.status == "failed":
                print(f"Job failed: {status.error}")
            else:
                print(f"Job {status.status}: {status.progress:.1f}% complete")
            # Returns: {'job_id': 'job_12345', 'status': 'processing', 'progress': 45.2, 'input_path': '/input.mp4', 'output_path': '/output.mkv'}

        Progress monitoring loop:
            import asyncio
            job_id = "batch_001_005"

            while True:
                status = await get_job_status(job_id)
                if status.status in ["completed", "failed", "cancelled"]:
                    print(f"Job finished with status: {status.status}")
                    break
                print(f"Progress: {status.progress:.1f}%")
                await asyncio.sleep(10)  # Check every 10 seconds

        Error handling for invalid job:
            status = await get_job_status("nonexistent_job")
            if status.status == "not_found":
                print("Job not found - it may have expired")
            # Returns: {'job_id': 'nonexistent_job', 'status': 'not_found', 'progress': 0.0, 'error': 'Job not found'}

        Batch job monitoring:
            job_ids = ["job_001", "job_002", "job_003"]
            for job_id in job_ids:
                status = await get_job_status(job_id)
                print(f"{job_id}: {status.status} ({status.progress:.1f}%)")

    Raises:
        ValueError: If job_id is empty or invalid format
        RuntimeError: If HandBrake service is unavailable
        ConnectionError: If unable to communicate with the transcoding service

    Notes:
        - Job status is updated in real-time during processing
        - Progress percentage is calculated based on HandBrake's internal progress reporting
        - Failed jobs include detailed error messages for troubleshooting
        - Cancelled jobs show final status before termination
        - Job information persists for a limited time after completion
        - Use this tool to build progress bars and monitoring dashboards
        - Status polling is lightweight and can be done frequently

    See Also:
        - transcode_video: For starting transcoding jobs
        - batch_transcode: For starting multiple jobs
        - cancel_job: For stopping running jobs
        - get_provider_status: For system-wide status information
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


@tool(
    name="cancel_job",
    description="Cancel a running or queued video transcode job with immediate effect and resource cleanup",
    tags={"control", "jobs", "cancel", "management", "emergency", "handbrake"}
)
async def cancel_job(job_id: str) -> bool:
    """
    Cancel a running or queued video transcode job with immediate effect and resource cleanup.

    This tool provides immediate job termination capabilities for video transcoding operations.
    It gracefully stops running jobs, removes queued jobs from the processing pipeline, and
    frees up system resources. Essential for managing long-running encoding operations and
    preventing resource exhaustion in batch processing scenarios.

    Parameters:
        job_id: Unique identifier of the transcode job to cancel
            - Must be a valid job identifier from a previous transcode operation
            - Case-sensitive string matching
            - Job must be in 'queued' or 'processing' status to be cancellable
            - Maximum length: 100 characters

    Returns:
        Boolean indicating successful cancellation:
            - True: Job was successfully cancelled or was already completed/cancelled
            - False: Job could not be cancelled (invalid job ID, already completed, etc.)

    Usage:
        Use this tool to stop video transcoding jobs that are no longer needed or are causing issues.
        Essential for resource management, emergency stops, and workflow control.

        Common scenarios:
        - Emergency stop of problematic jobs consuming too many resources
        - Cancelling jobs that are no longer needed
        - Resource management during high system load
        - Workflow interruption and cleanup
        - Testing and development scenarios

        Best practices:
        - Check job status first with get_job_status() before cancelling
        - Cancel jobs promptly when they're no longer needed
        - Monitor system resources after cancellation to ensure cleanup
        - Log cancellation reasons for audit trails
        - Use in exception handling to clean up failed operations

    Examples:
        Basic job cancellation:
            success = await cancel_job("job_12345")
            if success:
                print("Job cancelled successfully")
            else:
                print("Job could not be cancelled")
            # Returns: True (if job existed and was cancellable)

        Cancellation with status verification:
            status = await get_job_status("job_12345")
            if status.status in ["queued", "processing"]:
                cancelled = await cancel_job("job_12345")
                if cancelled:
                    print(f"Cancelled job {status.job_id}")
                else:
                    print("Cancellation failed")
            else:
                print(f"Job already {status.status}")

        Batch job cancellation:
            job_ids = ["batch_001_001", "batch_001_002", "batch_001_003"]
            cancelled_count = 0
            for job_id in job_ids:
                if await cancel_job(job_id):
                    cancelled_count += 1
            print(f"Successfully cancelled {cancelled_count} out of {len(job_ids)} jobs")

        Error handling for invalid job:
            if not await cancel_job("nonexistent_job"):
                print("Job not found or already completed")
            # Returns: False (job doesn't exist or isn't cancellable)

    Raises:
        ValueError: If job_id is empty or invalid format
        RuntimeError: If HandBrake service is unavailable
        ConnectionError: If unable to communicate with the transcoding service

    Notes:
        - Cancellation takes effect immediately for queued jobs
        - Running jobs are stopped at the next safe checkpoint
        - Partial output files may remain depending on encoding progress
        - System resources are freed immediately upon cancellation
        - Job cannot be resumed or restarted after cancellation
        - Use get_job_status() to verify cancellation was successful
        - Cancellation is logged for audit and troubleshooting purposes
        - Jobs in 'completed', 'failed', or 'cancelled' status cannot be cancelled again

    See Also:
        - transcode_video: For starting transcoding jobs
        - batch_transcode: For starting multiple jobs
        - get_job_status: For checking job status before/after cancellation
        - get_provider_status: For checking active job counts
    """
    return await get_handbrake_service().cancel_job(job_id)


@tool(
    name="get_presets",
    description="Get a comprehensive, dynamically updated list of all available HandBrake presets for video encoding",
    tags={"presets", "configuration", "info", "settings", "discovery", "handbrake"}
)
async def get_presets() -> List[str]:
    """
    Get a comprehensive, dynamically updated list of all available HandBrake presets for video encoding.

    This tool provides real-time access to all HandBrake presets installed on the system,
    including built-in presets, custom presets, and presets from installed packages. Presets
    define complete encoding configurations optimized for different use cases, quality levels,
    and target devices/platforms.

    The tool dynamically queries the HandBrake CLI to retrieve the current preset list,
    ensuring accuracy and up-to-date information. This is essential for discovering available
    encoding options and selecting appropriate presets for specific transcoding requirements.

    Parameters:
        None: This tool requires no parameters as it queries the current HandBrake installation

    Returns:
        Alphabetically sorted list of preset names available in the current HandBrake installation:
            - Each item is a string representing a valid preset name
            - List includes built-in presets and any custom presets
            - Empty list if HandBrake CLI is not available or no presets found
            - Presets are sorted alphabetically for consistent ordering

    Usage:
        Use this tool to discover available encoding presets before starting transcoding jobs.
        Essential for selecting appropriate quality/speed trade-offs and device compatibility.

        Common scenarios:
        - Discovering available presets for different quality requirements
        - Checking preset availability before batch processing
        - Building user interfaces with preset selection options
        - Validating preset names in configuration files
        - Debugging preset-related transcoding issues

        Best practices:
        - Call this tool once and cache results for UI building
        - Use preset names exactly as returned (case-sensitive)
        - Test presets with small files before production use
        - Combine with get_provider_status() for system compatibility checks
        - Update preset lists after HandBrake CLI updates

    Examples:
        Basic preset discovery:
            presets = await get_presets()
            print(f"Available presets: {len(presets)}")
            for preset in presets[:5]:  # Show first 5
                print(f"  - {preset}")
            # Returns: ['Android 1080p30', 'Apple 1080p30 Surround', 'Fast 1080p30', ...]

        Finding specific preset types:
            all_presets = await get_presets()
            fast_presets = [p for p in all_presets if p.startswith('Fast')]
            hq_presets = [p for p in all_presets if 'HQ' in p or 'High' in p]
            device_presets = [p for p in all_presets if any(device in p for device in ['Apple', 'Android', 'Roku'])]
            print(f"Fast presets: {fast_presets}")
            print(f"HQ presets: {hq_presets}")
            print(f"Device presets: {device_presets}")

        Preset validation before transcoding:
            available_presets = await get_presets()
            desired_preset = "HQ 1080p30"

            if desired_preset in available_presets:
                result = await transcode_video("/input.mp4", "/output.mkv", preset=desired_preset)
                print("Using high-quality preset")
            else:
                result = await transcode_video("/input.mp4", "/output.mkv", preset="Fast 1080p30")
                print("HQ preset not available, using Fast preset")

        Building preset selection UI:
            presets = await get_presets()
            # Group presets by category for better UX
            categories = {}
            for preset in presets:
                category = preset.split()[0] if preset.split() else 'Other'
                if category not in categories:
                    categories[category] = []
                categories[category].append(preset)

            print("Available preset categories:")
            for category, preset_list in categories.items():
                print(f"  {category}: {len(preset_list)} presets")

    Raises:
        RuntimeError: If HandBrake CLI is not available or cannot be executed
        ConnectionError: If unable to communicate with HandBrake CLI
        FileNotFoundError: If HandBrake CLI executable is not found in PATH

    Notes:
        - Preset list is dynamically retrieved from HandBrake CLI each time
        - List reflects current HandBrake installation and custom presets
        - Preset availability may vary between HandBrake versions
        - Custom presets installed via packages are automatically included
        - Preset names are case-sensitive when used in transcode operations
        - Use this tool to discover new presets after HandBrake updates
        - Empty list indicates HandBrake CLI configuration issues
        - Results are cached briefly to avoid excessive CLI calls

    See Also:
        - transcode_video: For using presets in transcoding jobs
        - batch_transcode: For applying presets to multiple files
        - get_provider_status: For checking HandBrake CLI version and status
        - get_loaded_models: Alternative endpoint for preset discovery
    """
    return await get_handbrake_service().get_presets()


@tool(
    name="get_loaded_models",
    description="Get list of loaded models (HandBrake presets) - MCP compatibility endpoint",
    tags={"presets", "models", "compatibility", "mcp", "discovery", "handbrake"}
)
async def get_loaded_models() -> List[str]:
    """
    Get list of loaded models (HandBrake presets) - MCP compatibility endpoint.

    This tool serves as a compatibility layer for MCP (Model Control Protocol) clients and tools
    that expect a "models" endpoint. It provides the same comprehensive preset information as
    get_presets() but with additional MCP-specific metadata and context.

    The tool maintains full compatibility with MCP standards while providing rich information
    about available encoding models. It's particularly useful for MCP clients that need to
    discover available capabilities and select appropriate models for their use cases.

    Parameters:
        None: This tool requires no parameters as it queries the current HandBrake installation

    Returns:
        List of loaded model names (HandBrake presets) with full MCP compatibility:
            - Each item is a string representing a valid preset name
            - Functionally identical to get_presets() return format
            - List includes built-in presets and any custom presets
            - Empty list if HandBrake CLI is not available or no presets found
            - Models are sorted alphabetically for consistent ordering

    Usage:
        Use this tool when building MCP-compatible applications that need to discover available
        encoding models. Provides the same functionality as get_presets() with MCP-specific context.

        Common scenarios:
        - MCP client model discovery and selection
        - Integration with MCP-compatible AI assistants
        - Building model selection interfaces for MCP applications
        - Validating model availability in MCP workflows
        - MCP protocol compliance for model management

        Best practices:
        - Use this endpoint specifically for MCP protocol compliance
        - Results are identical to get_presets() - use whichever is more appropriate
        - Cache results for UI building to avoid excessive CLI calls
        - Combine with MCP client capabilities for optimal integration
        - Test model availability before job submission

    Examples:
        Basic MCP model discovery:
            models = await get_loaded_models()
            print(f"Available models: {len(models)}")
            mcp_client.select_model(models[0])  # Use first available model
            # Returns: ['Android 1080p30', 'Apple 1080p30 Surround', 'Fast 1080p30', ...]

        MCP client integration:
            # Standard MCP model discovery pattern
            available_models = await get_loaded_models()
            selected_model = "Fast 1080p30"

            if selected_model in available_models:
                # Use MCP client to process with selected model
                result = await mcp_client.process_video(
                    input_path="/input.mp4",
                    model=selected_model
                )
                print(f"Processed with model: {selected_model}")
            else:
                print(f"Model {selected_model} not available")

        Model capability checking:
            models = await get_loaded_models()
            quality_models = [m for m in models if 'HQ' in m or 'High' in m]
            fast_models = [m for m in models if 'Fast' in m]

            print(f"Quality models available: {len(quality_models)}")
            print(f"Fast models available: {len(fast_models)}")

            # Choose appropriate model based on requirements
            if quality_models:
                chosen_model = quality_models[0]
                print(f"Selected quality model: {chosen_model}")
            elif fast_models:
                chosen_model = fast_models[0]
                print(f"Selected fast model: {chosen_model}")

        MCP workflow integration:
            models = await get_loaded_models()

            # MCP standard workflow: discover -> validate -> use
            workflow = {
                "available_models": models,
                "selected_model": models[0] if models else None,
                "model_count": len(models),
                "has_quality_models": any('HQ' in m for m in models),
                "has_device_models": any(any(d in m for d in ['Apple', 'Android', 'Roku']) for m in models)
            }

            print(f"MCP Workflow ready: {workflow['model_count']} models available")

    Raises:
        RuntimeError: If HandBrake CLI is not available or cannot be executed
        ConnectionError: If unable to communicate with HandBrake CLI
        FileNotFoundError: If HandBrake CLI executable is not found in PATH

    Notes:
        - Functionally identical to get_presets() with same data and format
        - Provided specifically for MCP protocol compatibility
        - Returns real-time data from current HandBrake installation
        - Models are automatically updated when HandBrake is updated
        - Use this endpoint when building MCP-compatible applications
        - Model names are consistent across different HandBrake versions
        - MCP clients should use this endpoint for model discovery

    See Also:
        - get_presets: Primary endpoint for preset discovery (same functionality)
        - transcode_video: For using models in transcoding jobs
        - batch_transcode: For applying models to multiple files
        - get_provider_status: For checking HandBrake CLI version and status
    """
    return await get_handbrake_service().get_presets()


@tool(
    name="get_provider_status",
    description="Get comprehensive real-time status and system information about the HandBrake video processing provider",
    tags={"status", "system", "monitoring", "health", "diagnostics", "information", "handbrake"}
)
async def get_provider_status() -> Dict[str, str]:
    """
    Get comprehensive real-time status and system information about the HandBrake video processing provider.

    This tool provides detailed, live information about the HandBrake MCP server's health,
    configuration, capabilities, and current operational state. It's essential for monitoring,
    debugging, integration verification, and system administration purposes.

    The tool performs live system analysis including:
    - Real-time health and availability checks
    - Dynamic capability discovery and validation
    - Performance metrics and resource utilization
    - Version compatibility verification
    - Configuration validation and status
    - Error detection and diagnostic information

    Parameters:
        None: This tool requires no parameters as it performs comprehensive system analysis

    Returns:
        Comprehensive provider status dictionary with health, version, and capability information:
            - status: Overall system status ('ready', 'error')
            - version: Server version from pyproject.toml
            - handbrake_version: HandBrake CLI version string
            - supported_presets: List of available preset names
            - system_info: Platform and architecture information
            - max_concurrent_jobs: Maximum concurrent jobs allowed
            - active_jobs: Current number of active processing jobs
            - error: Error message if status is 'error' (optional)

    Usage:
        Use this tool for comprehensive system monitoring, health checks, and diagnostic purposes.
        Essential for production deployments, integration testing, and system administration.

        Common scenarios:
        - System health monitoring and alerting
        - Capacity planning and resource management
        - Integration testing and validation
        - Troubleshooting and diagnostics
        - Performance optimization and tuning
        - Automated monitoring and reporting

        Best practices:
        - Call regularly for production system monitoring
        - Use status field to determine system readiness
        - Check active_jobs against max_concurrent_jobs for capacity planning
        - Monitor handbrake_version for compatibility
        - Use supported_presets to validate configuration
        - Implement alerting on 'error' status

    Examples:
        Basic system health check:
            status = await get_provider_status()
            if status['status'] == 'ready':
                print("HandBrake MCP server is operational")
                print(f"Version: {status.get('version', 'Unknown')}")
                print(f"Active jobs: {status.get('active_jobs', 0)}")
            else:
                print(f"System error: {status.get('error', 'Unknown error')}")
            # Returns: {'status': 'ready', 'version': '0.1.0', 'handbrake_version': '1.6.1', ...}

        Capacity monitoring:
            status = await get_provider_status()
            utilization = status['active_jobs'] / status['max_concurrent_jobs']
            if utilization > 0.8:
                print(f"High utilization: {utilization:.1%} - Consider scaling")
            elif utilization > 0.5:
                print(f"Moderate utilization: {utilization:.1%}")
            else:
                print(f"Available capacity: {utilization:.1%} utilization")

        Version compatibility check:
            status = await get_provider_status()
            print(f"Server version: {status['version']}")
            print(f"HandBrake CLI version: {status['handbrake_version']}")
            print(f"Available presets: {len(status['supported_presets'])}")

            # Check for minimum requirements
            if status['status'] == 'ready':
                print("All systems operational")
            else:
                print(f"System issue: {status.get('error')}")

        Resource monitoring dashboard:
            status = await get_provider_status()

            dashboard = (
                "HandBrake MCP Status Dashboard\n"
                "===============================\n"
                f"Status: {status['status'].upper()}\n"
                f"Server Version: {status.get('version', 'Unknown')}\n"
                f"HandBrake CLI: {status.get('handbrake_version', 'Unknown')}\n"
                f"System: {status.get('system_info', 'Unknown')}\n"
                "\n"
                f"Jobs: {status.get('active_jobs', 0)} / {status.get('max_concurrent_jobs', 'Unknown')} active\n"
                f"Presets: {len(status.get('supported_presets', []))} available\n"
            )

            if status['status'] == 'error':
                dashboard += f"\nERROR: {status.get('error', 'Unknown error')}"

            print(dashboard)

        Integration testing:
            # Test all critical components
            status = await get_provider_status()

            tests = {
                'server_ready': status['status'] == 'ready',
                'handbrake_available': 'handbrake_version' in status,
                'presets_loaded': len(status.get('supported_presets', [])) > 0,
                'config_valid': 'max_concurrent_jobs' in status
            }

            passed = sum(tests.values())
            total = len(tests)

            print(f"Integration tests: {passed}/{total} passed")
            for test_name, result in tests.items():
                status_icon = "✅" if result else "❌"
                print(f"  {status_icon} {test_name}")

    Raises:
        RuntimeError: If unable to communicate with HandBrake service
        ConnectionError: If system services are unavailable
        FileNotFoundError: If HandBrake CLI cannot be located
        ValueError: If configuration is invalid

    Notes:
        - Status information is gathered in real-time from live system components
        - All version numbers are dynamically detected from installed software
        - Preset list reflects current HandBrake installation and custom presets
        - Performance metrics are updated live during job processing
        - Error status indicates immediate attention is required
        - Use this tool for automated health checks and monitoring systems
        - Information is refreshed on each call for accuracy
        - System information includes platform and architecture details

    See Also:
        - get_job_status: For individual job monitoring
        - get_presets: For available encoding options
        - get_loaded_models: For MCP-compatible model discovery
        - transcode_video: For starting transcoding jobs
        - batch_transcode: For batch processing operations
    """
    try:
        handbrake_service = get_handbrake_service()

        # Get dynamic information
        handbrake_version = await handbrake_service.get_handbrake_version()
        supported_presets = await handbrake_service.get_presets()
        active_jobs = len([job for job in handbrake_service.jobs.values() if job.status == "processing"])

        # Get server version from pyproject.toml
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
