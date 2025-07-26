"""Tests for HandBrake MCP server."""
import asyncio
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from handbrake_mcp.services.handbrake import HandBrakeService, TranscodeJob
from handbrake_mcp.core.config import Settings


class TestHandBrakeService(unittest.IsolatedAsyncioTestCase):
    """Test cases for HandBrakeService."""
    
    async def asyncSetUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp(prefix="handbrake_test_"))
        self.input_file = self.test_dir / "input.mp4"
        self.output_file = self.test_dir / "output.mkv"
        
        # Create a dummy input file
        with open(self.input_file, "wb") as f:
            f.write(b"test video data")
        
        # Mock settings
        self.settings = Settings(
            hbb_path="HandBrakeCLI",
            default_preset="Fast 1080p30",
        )
        
        # Initialize service with mocked settings
        self.service = HandBrakeService()
        
        # Patch subprocess calls
        self.patcher = patch('asyncio.create_subprocess_exec')
        self.mock_subprocess = self.patcher.start()
        
        # Mock process
        self.mock_process = AsyncMock()
        self.mock_process.returncode = 0
        self.mock_process.communicate.return_value = (b"", b"")
        self.mock_subprocess.return_value = self.mock_process
    
    async def asyncTearDown(self):
        """Clean up after tests."""
        self.patcher.stop()
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    async def test_transcode_success(self):
        """Test successful video transcode."""
        job_id = await self.service.transcode(
            input_path=str(self.input_file),
            output_path=str(self.output_file),
            preset="Fast 1080p30",
        )
        
        self.assertIsNotNone(job_id)
        self.assertIn(job_id, self.service.jobs)
        
        # Check job status
        job = self.service.jobs[job_id]
        self.assertEqual(job.status, "queued")
        
        # Simulate job completion
        await self.service._run_transcode_job(job)
        self.assertEqual(job.status, "completed")
        self.assertEqual(job.progress, 100.0)
    
    async def test_get_job_status(self):
        """Test getting job status."""
        job_id = await self.service.transcode(
            input_path=str(self.input_file),
            output_path=str(self.output_file),
        )
        
        job = await self.service.get_job_status(job_id)
        self.assertIsNotNone(job)
        self.assertEqual(job.job_id, job_id)
    
    async def test_cancel_job(self):
        """Test job cancellation."""
        job_id = await self.service.transcode(
            input_path=str(self.input_file),
            output_path=str(self.output_file),
        )
        
        # Mock process for cancellation test
        mock_process = AsyncMock()
        mock_process.returncode = None
        mock_process.wait.return_value = 0
        self.mock_subprocess.return_value = mock_process
        
        # Create a job with a running process
        job = TranscodeJob(
            job_id=job_id,
            input_path=self.input_file,
            output_path=self.output_file,
            status="processing",
            process=mock_process,
        )
        self.service.jobs[job_id] = job
        
        # Test cancellation
        result = await self.service.cancel_job(job_id)
        self.assertTrue(result)
        self.assertEqual(job.status, "cancelled")
    
    async def test_get_presets(self):
        """Test getting HandBrake presets."""
        # Mock the _run_handbrake method
        with patch.object(self.service, '_run_handbrake') as mock_run:
            mock_run.return_value = "Preset List:\n  1) Fast 1080p30\n  2: HQ 1080p30\n"
            presets = await self.service.get_presets()
            self.assertIn("Fast 1080p30", presets)
            self.assertIn("HQ 1080p30", presets)


if __name__ == "__main__":
    unittest.main()
