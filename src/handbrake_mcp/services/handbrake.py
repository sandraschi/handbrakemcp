"""HandBrake service for video transcoding."""
import asyncio
import json
import logging
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field

from handbrake_mcp.core.config import settings

logger = logging.getLogger(__name__)


class HandBrakeError(Exception):
    """Custom exception for HandBrake related errors."""
    pass


class TranscodeJob(BaseModel):
    """Model for a transcoding job."""
    job_id: str
    input_path: Path
    output_path: Path
    preset: str = settings.default_preset
    options: Dict[str, Union[str, int, float, bool]] = Field(default_factory=dict)
    status: str = "pending"
    progress: float = 0.0
    error: Optional[str] = None
    process: Optional[asyncio.subprocess.Process] = None


class HandBrakeService:
    """Service for handling HandBrake operations."""
    
    def __init__(self):
        self.handbrake_path = self._find_handbrake()
        self.jobs: Dict[str, TranscodeJob] = {}
        self._supported_presets: List[str] = []
    
    def _find_handbrake(self) -> Path:
        """Find HandBrakeCLI in the system PATH or use configured path."""
        handbrake_path = shutil.which(settings.hbb_path)
        if not handbrake_path:
            raise HandBrakeError(
                f"HandBrakeCLI not found. Please install HandBrakeCLI and ensure it's in your PATH "
                f"or set HBB_PATH in your environment variables."
            )
        return Path(handbrake_path)
    
    async def get_presets(self) -> List[str]:
        """Get list of available HandBrake presets."""
        if not self._supported_presets:
            try:
                result = await self._run_handbrake(["--preset-import-gui", "--preset-import-file", "-"])
                # Parse the output to extract preset names
                # This is a simplified example - actual parsing would depend on HandBrakeCLI output
                self._supported_presets = ["Fast 1080p30", "HQ 1080p30 Surround", "Web Optimized"]
            except Exception as e:
                logger.error(f"Failed to get presets: {e}")
                raise HandBrakeError(f"Failed to get presets: {e}")
        return self._supported_presets
    
    async def transcode(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        preset: Optional[str] = None,
        options: Optional[Dict[str, Union[str, int, float, bool]]] = None,
    ) -> str:
        """Start a transcoding job.
        
        Args:
            input_path: Path to input video file
            output_path: Path for output file
            preset: HandBrake preset name
            options: Additional HandBrake options
            
        Returns:
            Job ID for tracking progress
        """
        input_path = Path(input_path)
        output_path = Path(output_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        job_id = f"job_{len(self.jobs) + 1}_{input_path.stem}"
        
        job = TranscodeJob(
            job_id=job_id,
            input_path=input_path,
            output_path=output_path,
            preset=preset or settings.default_preset,
            options=options or {},
            status="queued",
        )
        
        self.jobs[job_id] = job
        
        # Start the transcoding task
        asyncio.create_task(self._run_transcode_job(job))
        
        return job_id
    
    async def _run_transcode_job(self, job: TranscodeJob):
        """Run a transcoding job in the background."""
        try:
            job.status = "processing"
            
            # Prepare output directory
            job.output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Build HandBrakeCLI command
            cmd = [
                str(self.handbrake_path),
                "--input", str(job.input_path),
                "--output", str(job.output_path),
                "--preset-import-gui",
                "--preset", job.preset,
                "--json",
            ]
            
            # Add additional options
            for key, value in job.options.items():
                if value is True:
                    cmd.append(f"--{key}")
                elif value is not False and value is not None:
                    cmd.extend([f"--{key}", str(value)])
            
            # Start the process
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            job.process = process
            
            # Process output
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                
                try:
                    # Parse progress from JSON output
                    data = json.loads(line)
                    if "Progress" in data:
                        job.progress = float(data["Progress"])
                except json.JSONDecodeError:
                    logger.debug(f"Non-JSON output: {line.decode().strip()}")
            
            # Wait for process to complete
            await process.wait()
            
            if process.returncode == 0:
                job.status = "completed"
                job.progress = 100.0
                logger.info(f"Transcoding completed: {job.job_id}")
            else:
                error_output = await process.stderr.read()
                job.status = "failed"
                job.error = f"HandBrakeCLI failed with code {process.returncode}: {error_output.decode()}"
                logger.error(f"Transcoding failed: {job.job_id} - {job.error}")
        
        except Exception as e:
            job.status = "failed"
            job.error = str(e)
            logger.exception(f"Error in transcode job {job.job_id}")
    
    async def get_job_status(self, job_id: str) -> Optional[TranscodeJob]:
        """Get the status of a transcoding job."""
        return self.jobs.get(job_id)
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a running transcoding job."""
        job = self.jobs.get(job_id)
        if not job or not job.process:
            return False
        
        try:
            job.process.terminate()
            await asyncio.wait_for(job.process.wait(), timeout=5.0)
        except (ProcessLookupError, asyncio.TimeoutError):
            job.process.kill()
            await job.process.wait()
        
        job.status = "cancelled"
        return True
    
    async def _run_handbrake(self, args: List[str]) -> str:
        """Run HandBrakeCLI with the given arguments."""
        cmd = [str(self.handbrake_path)] + args
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            error_msg = stderr.decode().strip() or "Unknown error"
            raise HandBrakeError(f"HandBrakeCLI failed: {error_msg}")
        
        return stdout.decode().strip()


# Global instance
handbrake_service = HandBrakeService()
