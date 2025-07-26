"""MCP tools for HandBrake MCP server."""
from typing import Dict, List, Optional

from fastmcp import FastMCP
from pydantic import BaseModel, Field

from handbrake_mcp.services.handbrake import handbrake_service, TranscodeJob
from handbrake_mcp.core.config import settings

# Get the FastMCP instance from the main module
from handbrake_mcp.main import mcp


class TranscodeRequest(BaseModel):
    """Request model for the transcode_video tool."""
    input_path: str = Field(..., description="Path to the input video file")
    output_path: str = Field(..., description="Path where the output file will be saved")
    preset: Optional[str] = Field(
        settings.default_preset,
        description=f"HandBrake preset to use (default: {settings.default_preset})"
    )
    options: Optional[Dict[str, str]] = Field(
        default_factory=dict,
        description="Additional HandBrake options as key-value pairs"
    )


class TranscodeResponse(BaseModel):
    """Response model for the transcode_video tool."""
    job_id: str = Field(..., description="Unique ID for tracking the transcode job")
    status: str = Field(..., description="Current status of the job")
    input_path: str = Field(..., description="Path to the input file")
    output_path: str = Field(..., description="Path to the output file")


class JobStatusResponse(BaseModel):
    """Response model for job status."""
    job_id: str = Field(..., description="Unique ID of the job")
    status: str = Field(..., description="Current status (queued, processing, completed, failed, cancelled)")
    progress: float = Field(..., description="Progress percentage (0-100)")
    error: Optional[str] = Field(None, description="Error message if the job failed")
    input_path: str = Field(..., description="Path to the input file")
    output_path: str = Field(..., description="Path to the output file")


@mcp.tool()
async def transcode_video(
    input_path: str,
    output_path: str,
    preset: Optional[str] = None,
    options: Optional[Dict[str, str]] = None,
) -> TranscodeResponse:
    """
    Transcode a video file using HandBrake.
    
    Args:
        input_path: Path to the input video file
        output_path: Path where the output file will be saved
        preset: HandBrake preset to use (default: from settings)
        options: Additional HandBrake options as key-value pairs
        
    Returns:
        TranscodeResponse with job details
    """
    job_id = await handbrake_service.transcode(
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


@mcp.tool()
async def batch_transcode(
    jobs: List[Dict[str, str]],
    default_preset: Optional[str] = None,
) -> List[TranscodeResponse]:
    """
    Transcode multiple video files in batch.
    
    Args:
        jobs: List of job specifications with 'input_path' and 'output_path'
        default_preset: Default preset to use if not specified in job
        
    Returns:
        List of TranscodeResponse objects for each job
    """
    results = []
    for job in jobs:
        try:
            job_id = await handbrake_service.transcode(
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


@mcp.tool()
async def get_job_status(job_id: str) -> JobStatusResponse:
    """
    Get the status of a transcode job.
    
    Args:
        job_id: ID of the job to check
        
    Returns:
        JobStatusResponse with current status and progress
    """
    job = await handbrake_service.get_job_status(job_id)
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


@mcp.tool()
async def cancel_job(job_id: str) -> bool:
    """
    Cancel a running transcode job.
    
    Args:
        job_id: ID of the job to cancel
        
    Returns:
        bool: True if the job was cancelled, False otherwise
    """
    return await handbrake_service.cancel_job(job_id)


@mcp.tool()
async def get_presets() -> List[str]:
    """
    Get a list of available HandBrake presets.
    
    Returns:
        List of preset names
    """
    return await handbrake_service.get_presets()


@mcp.tool()
async def get_loaded_models() -> List[str]:
    """
    Get a list of loaded models (presets).
    
    This is a compatibility method to match the MCP spec.
    
    Returns:
        List of loaded model (preset) names
    """
    return await handbrake_service.get_presets()


@mcp.tool()
async def get_provider_status() -> Dict[str, str]:
    """
    Get the status of the HandBrake provider.
    
    Returns:
        Dict with provider status information
    """
    try:
        # This would be more sophisticated in a real implementation
        return {
            "status": "ready",
            "version": "1.0.0",
            "handbrake_version": "1.5.1",  # Would be detected in a real implementation
            "supported_presets": await handbrake_service.get_presets(),
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }
