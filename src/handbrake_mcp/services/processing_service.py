"""Service for processing video files with HandBrake."""
import asyncio
import logging
import shutil
from pathlib import Path
from typing import Callable, Dict, List, Optional

from handbrake_mcp.core.config import settings
from handbrake_mcp.services.handbrake import get_handbrake_service, TranscodeJob
from handbrake_mcp.services.notification_service import NotificationService, NotificationRecipient

logger = logging.getLogger(__name__)


class ProcessingService:
    """Service for processing video files with HandBrake."""
    
    def __init__(self):
        """Initialize the processing service."""
        self.active_jobs: Dict[str, TranscodeJob] = {}
        self.notification_service = NotificationService()
        self.processed_files: List[Path] = []
        self._on_job_complete: Optional[Callable[[TranscodeJob], None]] = None

        # Configure email notifications if settings are available
        if (settings.smtp_server and settings.email_notifications and
            settings.email_recipients):
            self.notification_service.configure_smtp(
                server=settings.smtp_server,
                port=settings.smtp_port,
                username=settings.smtp_username,
                password=settings.smtp_password,
                use_tls=settings.smtp_use_tls
            )

            # Add email recipients
            for email in settings.email_recipients:
                self.notification_service.add_recipient(
                    NotificationRecipient(email=email)
                )
    
    async def process_file(
        self,
        input_path: Path,
        output_dir: Optional[Path] = None,
        preset: Optional[str] = None,
        options: Optional[Dict] = None,
        delete_original: bool = False,
    ) -> str:
        """Process a video file with HandBrake.
        
        Args:
            input_path: Path to the input video file
            output_dir: Directory to save the output file (default: same as input)
            preset: HandBrake preset to use
            options: Additional HandBrake options
            delete_original: Whether to delete the original file after processing
            
        Returns:
            Job ID for tracking progress
        """
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        # Determine output path
        if output_dir is None:
            output_dir = input_path.parent
        
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{input_path.stem}_converted.mkv"
        
        # Start the transcode job
        job_id = await get_handbrake_service().transcode(
            input_path=str(input_path),
            output_path=str(output_path),
            preset=preset or settings.default_preset,
            options=options or {},
        )
        
        # Store job metadata
        job = await get_handbrake_service().get_job_status(job_id)
        if job:
            job.options = {
                "delete_original": delete_original,
                "original_path": str(input_path),
                "output_path": str(output_path),
            }
            self.active_jobs[job_id] = job
            
            # Set up completion callback
            asyncio.create_task(self._monitor_job(job_id))
            
            # Notify job started
            await self.notification_service.notify(
                "job_started",
                {
                    "job_id": job_id,
                    "input_path": str(input_path),
                    "output_path": str(output_path),
                    "preset": preset or settings.default_preset,
                }
            )
        
        return job_id
    
    async def _monitor_job(self, job_id: str):
        """Monitor a job for completion and handle post-processing."""
        while True:
            job = await get_handbrake_service().get_job_status(job_id)
            if not job or job.status in ["completed", "failed", "cancelled"]:
                break
            await asyncio.sleep(1)
        
        # Handle job completion
        if job:
            if job.status == "completed":
                await self._handle_job_completion(job)
            elif job.status == "failed":
                await self._handle_job_failure(job)
            
            # Remove from active jobs
            self.active_jobs.pop(job_id, None)
            
            # Call completion callback if set
            if self._on_job_complete:
                self._on_job_complete(job)
    
    async def _handle_job_completion(self, job: TranscodeJob):
        """Handle a successfully completed job."""
        options = getattr(job, 'options', {})
        original_path = Path(options.get('original_path', ''))
        output_path = Path(options.get('output_path', ''))
        
        # Move original file to processed directory if specified
        if options.get('delete_original') and original_path.exists():
            try:
                original_path.unlink()
                logger.info(f"Deleted original file: {original_path}")
            except Exception as e:
                logger.error(f"Failed to delete original file {original_path}: {e}")
        
        # Add to processed files list
        self.processed_files.append(original_path)
        
        # Notify job completed
        await self.notification_service.notify(
            "job_completed",
            {
                "job_id": job.job_id,
                "input_path": str(original_path),
                "output_path": str(output_path),
            }
        )
    
    async def _handle_job_failure(self, job: TranscodeJob):
        """Handle a failed job."""
        options = getattr(job, 'options', {})
        
        # Notify job failed
        await self.notification_service.notify(
            "job_failed",
            {
                "job_id": job.job_id,
                "input_path": options.get('original_path', ''),
                "output_path": options.get('output_path', ''),
                "error": job.error,
            }
        )
    
    def set_job_complete_callback(self, callback: Callable[[TranscodeJob], None]):
        """Set a callback to be called when a job completes."""
        self._on_job_complete = callback
    
    def get_active_jobs(self) -> List[Dict]:
        """Get a list of active jobs."""
        return [
            {
                "job_id": job.job_id,
                "status": job.status,
                "progress": job.progress,
                "input_path": str(job.input_path),
                "output_path": str(job.output_path),
            }
            for job in self.active_jobs.values()
        ]


# Global instance
processing_service = ProcessingService()
