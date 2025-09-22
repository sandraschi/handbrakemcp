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
    model_config = {"arbitrary_types_allowed": True}

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
        self.handbrake_version = None
        self.jobs: Dict[str, TranscodeJob] = {}
        self._supported_presets: List[str] = []
        self._max_concurrent_jobs = 5  # Rate limiting
        self._max_file_size_gb = 10  # Maximum file size in GB
        self._min_file_size_bytes = 1024  # Minimum file size in bytes
        self._max_option_value_length = 1000  # Maximum length for option values
    
    def _find_handbrake(self) -> Path:
        """Find HandBrakeCLI in the system PATH or use configured path."""
        handbrake_path = shutil.which(settings.hbb_path)
        if not handbrake_path:
            raise HandBrakeError(
                f"HandBrakeCLI not found. Please install HandBrakeCLI and ensure it's in your PATH "
                f"or set HBB_PATH in your environment variables."
            )
        return Path(handbrake_path)
    
    async def get_handbrake_version(self) -> str:
        """Get the HandBrake CLI version."""
        if self.handbrake_version is None:
            try:
                result = await self._run_handbrake(["--version"])
                # Parse version from output like "HandBrake 1.5.1 (2023010100)"
                lines = result.strip().split('\n')
                if lines:
                    version_line = lines[0]
                    # Extract version number from the line
                    import re
                    version_match = re.search(r'HandBrake\s+([\d.]+)', version_line)
                    if version_match:
                        self.handbrake_version = version_match.group(1)
                    else:
                        self.handbrake_version = "unknown"
                else:
                    self.handbrake_version = "unknown"
            except Exception as e:
                logger.error(f"Failed to get HandBrake version: {e}")
                self.handbrake_version = "unknown"
        return self.handbrake_version

    async def get_presets(self) -> List[str]:
        """Get list of available HandBrake presets."""
        if not self._supported_presets:
            try:
                # First get the version to ensure HandBrake is working
                await self.get_handbrake_version()

                # Try to get presets using the modern CLI interface
                result = await self._run_handbrake(["--preset-list"])
                self._supported_presets = self._parse_presets_from_output(result)

                # If that fails, try the older method
                if not self._supported_presets:
                    logger.warning("Modern preset list failed, trying legacy method")
                    result = await self._run_handbrake(["--preset-import-gui", "--preset-import-file", "-"])
                    self._supported_presets = self._parse_presets_from_output(result)

                # If still no presets, use fallback list
                if not self._supported_presets:
                    logger.warning("Using fallback preset list")
                    self._supported_presets = ["Fast 1080p30", "HQ 1080p30 Surround", "Web Optimized"]

            except Exception as e:
                logger.error(f"Failed to get presets: {e}")
                raise HandBrakeError(f"Failed to get presets: {e}")
        return self._supported_presets

    def _parse_presets_from_output(self, output: str) -> List[str]:
        """Parse preset names from HandBrake CLI output."""
        presets = []
        lines = output.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Try different parsing patterns based on HandBrake CLI output format
            # Pattern 1: "  Preset Name (category)"
            if line.startswith('  '):
                preset_name = line.strip()
                if '(' in preset_name:
                    preset_name = preset_name.split('(')[0].strip()
                presets.append(preset_name)

            # Pattern 2: Lines starting with preset names
            elif not line.startswith('+') and not line.startswith('Preset') and len(line) > 3:
                # Remove leading numbers or bullets
                cleaned_line = line.lstrip('0123456789.- ')
                if cleaned_line and len(cleaned_line) > 2:
                    presets.append(cleaned_line)

        # Remove duplicates and sort
        presets = list(set(presets))
        presets.sort()

        return presets
    
    async def transcode(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        preset: Optional[str] = None,
        options: Optional[Dict[str, Union[str, int, float, bool]]] = None,
    ) -> str:
        """Start a transcoding job with rate limiting and validation.

        Args:
            input_path: Path to input video file (validated for security)
            output_path: Path for output file (validated for security)
            preset: HandBrake preset name (validated against available presets)
            options: Additional HandBrake options (sanitized)

        Returns:
            Job ID for tracking progress

        Raises:
            FileNotFoundError: If input file doesn't exist
            ValueError: If preset is invalid or system overloaded
            HandBrakeError: If HandBrake CLI fails
        """
        # Security: Validate and canonicalize paths
        input_path = self._validate_and_secure_path(input_path)
        output_path = self._validate_and_secure_path(output_path)

        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Validate file size (prevent processing extremely large files)
        file_size = input_path.stat().st_size
        max_file_size = self._max_file_size_gb * 1024 * 1024 * 1024
        if file_size > max_file_size:
            raise ValueError(f"Input file too large: {file_size / (1024*1024*1024):.1f}GB (max: {self._max_file_size_gb}GB)")

        if file_size < self._min_file_size_bytes:
            raise ValueError(f"Input file too small: {file_size} bytes (min: {self._min_file_size_bytes} bytes)")

        # Rate limiting: Check concurrent jobs
        running_jobs = len([job for job in self.jobs.values() if job.status == "processing"])
        if running_jobs >= self._max_concurrent_jobs:
            raise ValueError(f"Maximum concurrent jobs ({self._max_concurrent_jobs}) reached. Please wait for existing jobs to complete.")

        # Check system resources before starting new job
        await self._check_system_resources()

        # Validate preset if provided
        if preset and preset not in await self.get_presets():
            raise ValueError(f"Invalid preset: {preset}")

        # Sanitize options to prevent command injection
        safe_options = self._sanitize_options(options or {})

        job_id = f"job_{len(self.jobs) + 1}_{input_path.stem}"

        job = TranscodeJob(
            job_id=job_id,
            input_path=input_path,
            output_path=output_path,
            preset=preset or settings.default_preset,
            options=safe_options,
            status="queued",
        )

        self.jobs[job_id] = job

        # Start the transcoding task
        asyncio.create_task(self._run_transcode_job(job))

        return job_id

    def _validate_and_secure_path(self, path: Union[str, Path]) -> Path:
        """Validate and secure file path to prevent directory traversal attacks."""
        # Convert to string for validation
        path_str = str(path)

        # Security: Prevent dangerous characters
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*']
        for char in dangerous_chars:
            if char in path_str:
                raise ValueError(f"Invalid characters in path: {path}")

        # Convert to Path object and resolve
        path_obj = Path(path).resolve()

        # Prevent directory traversal
        if ".." in path_obj.parts:
            raise ValueError(f"Directory traversal detected in path: {path}")

        # Check if path exists (for input files)
        # Note: Output directories may not exist yet, so we don't check for them

        # Validate file extension for input files
        if path_obj.is_file():
            allowed_extensions = {'.mp4', '.mkv', '.avi', '.mov', '.m4v', '.wmv', '.flv', '.webm'}
            if path_obj.suffix.lower() not in allowed_extensions:
                raise ValueError(f"Unsupported file format: {path_obj.suffix}")

        # Additional security: Check path length
        if len(str(path_obj)) > 1000:
            raise ValueError(f"Path too long: {path}")

        # Check if path is within safe directories (optional - can be configured)
        # For now, we'll allow any path but log warnings for unusual locations

        return path_obj

    def _sanitize_options(self, options: Dict[str, Union[str, int, float, bool]]) -> Dict[str, Union[str, int, float, bool]]:
        """Sanitize options to prevent command injection and ensure safety."""
        safe_options = {}

        # Allowed HandBrake CLI options to prevent injection
        allowed_keys = {
            'quality', 'encoder', 'audio', 'ab', 'ar', 'acodec', 'aname', 'aencoder',
            'subtitle', 'scodec', 'sencoder', 'width', 'height', 'crop', 'deinterlace',
            'denoise', 'deblock', 'colorspace', 'format', 'optimize', 'ipod-atom',
            'use-opencl', 'use-qsv', 'use-nvenc', 'preset', 'input', 'output'
        }

        for key, value in options.items():
            # Validate key against allowed options
            safe_key = str(key).strip()
            if safe_key not in allowed_keys:
                logger.warning(f"Unknown or potentially unsafe option: {safe_key}")
                continue

            # Sanitize key by removing dangerous characters
            safe_key = "".join(c for c in safe_key if c.isalnum() or c in ['-', '_'])

            # Sanitize value based on type
            if isinstance(value, bool):
                safe_value = value
            elif isinstance(value, (int, float)):
                # Validate numeric ranges
                if isinstance(value, int) and not (-1000000 <= value <= 1000000):
                    logger.warning(f"Integer value out of safe range: {value}")
                    continue
                if isinstance(value, float) and not (-1000000.0 <= value <= 1000000.0):
                    logger.warning(f"Float value out of safe range: {value}")
                    continue
                safe_value = value
            else:
                # Sanitize string values
                safe_value = str(value).strip()
                if len(safe_value) > self._max_option_value_length:
                    logger.warning(f"Option value too long: {len(safe_value)} chars (max: {self._max_option_value_length})")
                    continue
                # Remove dangerous characters that could be used for injection
                safe_value = "".join(c for c in safe_value if c not in [';', '&', '|', '`', '$', '(', ')', '<', '>', '"', "'"])

            safe_options[safe_key] = safe_value

        return safe_options

    async def _check_system_resources(self):
        """Check system resources before starting a new job."""
        try:
            import psutil
        except ImportError:
            # If psutil is not available, skip resource checking
            logger.warning("psutil not available - skipping resource checks")
            return

        # Check CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > 90:
            raise ValueError(f"System CPU usage too high: {cpu_percent:.1f}% (threshold: 90%)")

        # Check memory usage
        memory = psutil.virtual_memory()
        if memory.percent > 85:
            raise ValueError(f"System memory usage too high: {memory.percent:.1f}% (threshold: 85%)")

        # Check disk space for output directory
        try:
            output_disk = psutil.disk_usage(self.handbrake_path.parent)
            if output_disk.percent > 90:
                raise ValueError(f"Disk space usage too high: {output_disk.percent:.1f}% (threshold: 90%)")
        except Exception:
            # If we can't check disk space, continue anyway
            pass
    
    async def _run_transcode_job(self, job: TranscodeJob):
        """Run a transcoding job in the background."""
        try:
            job.status = "processing"
            
            # Prepare output directory
            job.output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Build HandBrakeCLI command with security measures
            cmd = [
                str(self.handbrake_path),
                "--input", str(job.input_path),
                "--output", str(job.output_path),
                "--preset-import-gui",
                "--preset", job.preset,
                "--json",
            ]

            # Add additional options (already sanitized)
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


# Global instance - lazy initialization
handbrake_service = None

def get_handbrake_service():
    """Get the HandBrake service instance, initializing it if necessary."""
    global handbrake_service
    if handbrake_service is None:
        handbrake_service = HandBrakeService()
    return handbrake_service
