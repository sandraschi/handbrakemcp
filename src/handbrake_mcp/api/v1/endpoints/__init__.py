"""API v1 endpoints for HandBrake MCP."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union

from handbrake_mcp.services.handbrake import handbrake_service, TranscodeJob
from handbrake_mcp.core.config import settings

router = APIRouter()


class TranscodeRequest(BaseModel):
    """Request model for starting a transcode job."""
    input_path: str = Field(..., description="Path to input video file")
    output_path: str = Field(..., description="Path for output file")
    preset: Optional[str] = Field(
        settings.default_preset,
        description=f"HandBrake preset to use (default: {settings.default_preset})"
    )
    options: Optional[Dict[str, Union[str, int, float, bool]]] = Field(
        default_factory=dict,
        description="Additional HandBrake options"
    )


class JobStatusResponse(BaseModel):
    """Response model for job status."""
    job_id: str
    status: str
    progress: float
    error: Optional[str] = None
    input_path: str
    output_path: str


@router.post("/transcode", response_model=Dict[str, str])
async def start_transcode(request: TranscodeRequest):
    """Start a new video transcode job."""
    try:
        job_id = await handbrake_service.transcode(
            input_path=request.input_path,
            output_path=request.output_path,
            preset=request.preset,
            options=request.options,
        )
        return {"job_id": job_id, "status": "queued"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Get the status of a transcode job."""
    job = await handbrake_service.get_job_status(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found"
        )
    
    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        progress=job.progress,
        error=job.error,
        input_path=str(job.input_path),
        output_path=str(job.output_path),
    )


@router.get("/presets", response_model=List[str])
async def list_presets():
    """List available HandBrake presets."""
    try:
        return await handbrake_service.get_presets()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get presets: {str(e)}"
        )


@router.delete("/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_job(job_id: str):
    """Cancel a running transcode job."""
    success = await handbrake_service.cancel_job(job_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found or not running"
        )
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content=None)
