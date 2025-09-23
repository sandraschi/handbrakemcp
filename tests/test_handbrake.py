"""Tests for HandBrake MCP server."""
import asyncio
import os
import shutil
import subprocess
import tempfile
import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from handbrake_mcp.services.handbrake import HandBrakeService, TranscodeJob
from handbrake_mcp.core.config import Settings


def create_test_video(output_path: Path, duration_seconds: int = 2) -> bool:
    """Create a minimal test video using ffmpeg if available, otherwise skip."""
    try:
        # Try to create a simple test video
        result = subprocess.run([
            "ffmpeg", "-f", "lavfi", "-i", f"testsrc=duration={duration_seconds}:size=320x240:rate=1",
            "-f", "lavfi", "-i", f"sine=frequency=1000:duration={duration_seconds}",
            "-c:v", "libx264", "-c:a", "aac", "-shortest", str(output_path)
        ], capture_output=True, timeout=30)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        return False


@pytest.fixture
async def unit_test_setup():
    """Pytest fixture for unit test setup."""
    test_dir = Path(tempfile.mkdtemp(prefix="handbrake_test_"))
    input_file = test_dir / "input.mp4"
    output_file = test_dir / "output.mkv"

    # Create a dummy input file (must be at least 1024 bytes for validation)
    test_data = b"test video data" * 100  # Make it larger than 1024 bytes
    with open(input_file, "wb") as f:
        f.write(test_data)

    # Mock settings
    settings = Settings(
        hbb_path="HandBrakeCLI",
        default_preset="Fast 1080p30",
    )

    # Initialize service with mocked settings
    service = HandBrakeService()

    # Patch subprocess calls
    patcher = patch('asyncio.create_subprocess_exec')
    mock_subprocess = patcher.start()

    # Mock process with proper HandBrake output simulation
    mock_process = AsyncMock()
    mock_process.returncode = 0
    mock_process.communicate.return_value = (b"", b"")

    # Mock stdout.readline() to simulate progress output
    mock_stdout = AsyncMock()
    mock_stdout.readline.side_effect = [
        b'{"Progress": 25.0}\n',
        b'{"Progress": 50.0}\n',
        b'{"Progress": 75.0}\n',
        b'{"Progress": 100.0}\n',
        b'',  # End of output
    ]
    mock_process.stdout = mock_stdout
    mock_process.stderr = AsyncMock()
    mock_process.stderr.read.return_value = b""

    mock_subprocess.return_value = mock_process

    yield {
        'service': service,
        'test_dir': test_dir,
        'input_file': input_file,
        'output_file': output_file,
        'settings': settings,
        'patcher': patcher,
        'mock_process': mock_process
    }

    # Cleanup
    patcher.stop()
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)


@pytest.mark.unit
class TestHandBrakeServiceUnit:
    """Unit tests for HandBrakeService using mocks."""
    
    async def test_transcode_success(self, unit_test_setup):
        """Test successful video transcode."""
        setup = unit_test_setup
        job_id = await setup['service'].transcode(
            input_path=str(setup['input_file']),
            output_path=str(setup['output_file']),
            preset="Fast 1080p30",
        )

        assert job_id is not None
        assert job_id in setup['service'].jobs

        # Check job status
        job = setup['service'].jobs[job_id]
        assert job.status == "queued"

        # Simulate job completion
        await setup['service']._run_transcode_job(job)
        assert job.status == "completed"
        assert job.progress == 100.0
    
    async def test_get_job_status(self, unit_test_setup):
        """Test getting job status."""
        setup = unit_test_setup
        job_id = await setup['service'].transcode(
            input_path=str(setup['input_file']),
            output_path=str(setup['output_file']),
        )

        job = await setup['service'].get_job_status(job_id)
        assert job is not None
        assert job.job_id == job_id
    
    async def test_cancel_job(self, unit_test_setup):
        """Test job cancellation."""
        setup = unit_test_setup

        # Create a job with a running process (bypass validation for testing)
        job_id = "test_cancel_job"
        job = TranscodeJob.model_construct(
            job_id=job_id,
            input_path=setup['input_file'],
            output_path=setup['output_file'],
            status="processing",
            process=setup['mock_process'],
        )
        setup['service'].jobs[job_id] = job

        # Test cancellation
        result = await setup['service'].cancel_job(job_id)
        assert result is True
        assert job.status == "cancelled"
    
    async def test_get_presets(self, unit_test_setup):
        """Test getting HandBrake presets."""
        setup = unit_test_setup
        # Mock the _run_handbrake method
        with patch.object(setup['service'], '_run_handbrake') as mock_run:
            mock_run.return_value = "Available presets:\n  Fast 1080p30\n  HQ 1080p30\n  Very Fast 1080p30\n"
            presets = await setup['service'].get_presets()
            assert "Fast 1080p30" in presets
            assert "HQ 1080p30" in presets
            assert "Very Fast 1080p30" in presets


@pytest.mark.integration
@pytest.mark.slow
class TestHandBrakeServiceIntegration:
    """Integration tests for HandBrakeService using real HandBrakeCLI."""

    async def asyncSetUp(self):
        """Set up test fixtures with real HandBrake."""
        self.test_dir = Path(tempfile.mkdtemp(prefix="handbrake_integration_test_"))
        self.input_file = self.test_dir / "input.mp4"
        self.output_file = self.test_dir / "output.mkv"

        # Create a real test video if possible
        if not create_test_video(self.input_file):
            # Fallback: create a minimal video file for testing file operations
            with open(self.input_file, "wb") as f:
                # Write a minimal MP4 header + some dummy data to make it look like a video file
                f.write(b'\x00\x00\x00\x20ftypmp41\x00\x00\x00\x00mp41mp42iso5dash\x00\x00\x00\x08free' + b'x' * 1000)

        # Initialize service with real HandBrake
        self.service = HandBrakeService()

        # Verify HandBrake is working
        version = await self.service.get_handbrake_version()
        self.assertIsNotNone(version)
        self.assertNotEqual(version, "unknown")

    async def asyncTearDown(self):
        """Clean up after tests."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    async def test_real_transcode_success(self):
        """Test successful video transcode with real HandBrakeCLI."""
        # Only run if we have a valid input file
        if not self.input_file.exists() or self.input_file.stat().st_size < 100:
            self.skipTest("No valid test video file available")

        job_id = await self.service.transcode(
            input_path=str(self.input_file),
            output_path=str(self.output_file),
            preset="Fast 1080p30",
        )

        self.assertIsNotNone(job_id)
        self.assertIn(job_id, self.service.jobs)

        # Wait for job to complete (with timeout)
        job = self.service.jobs[job_id]
        await asyncio.wait_for(self.service._run_transcode_job(job), timeout=60)

        # Verify job completed
        self.assertEqual(job.status, "completed")
        self.assertEqual(job.progress, 1.0)

        # Verify output file was created
        self.assertTrue(self.output_file.exists())
        self.assertGreater(self.output_file.stat().st_size, 0)

    async def test_real_get_presets(self):
        """Test getting HandBrake presets with real CLI."""
        presets = await self.service.get_presets()
        self.assertIsInstance(presets, list)
        self.assertGreater(len(presets), 0)

        # Should contain some common presets
        preset_names = [p.lower() for p in presets]
        self.assertTrue(any("fast" in name for name in preset_names) or
                       any("1080p" in name for name in preset_names))

    async def test_real_get_version(self):
        """Test getting HandBrake version with real CLI."""
        version = await self.service.get_handbrake_version()
        self.assertIsNotNone(version)
        self.assertNotEqual(version, "unknown")

        # Version should be in format like "1.5.1"
        import re
        self.assertRegex(version, r'\d+\.\d+\.\d+')

    async def test_real_job_status_tracking(self):
        """Test job status tracking during real transcoding."""
        if not self.input_file.exists() or self.input_file.stat().st_size < 100:
            self.skipTest("No valid test video file available")

        job_id = await self.service.transcode(
            input_path=str(self.input_file),
            output_path=str(self.output_file),
            preset="Fast 1080p30",
        )

        job = self.service.jobs[job_id]

        # Check initial status
        self.assertEqual(job.status, "queued")

        # Start the job and monitor progress
        progress_updates = []

        async def monitor_progress():
            while job.status in ["queued", "processing"]:
                status = await self.service.get_job_status(job_id)
                if status.progress > 0:
                    progress_updates.append(status.progress)
                await asyncio.sleep(0.1)
                if len(progress_updates) > 100:  # Safety limit
                    break

        # Run monitoring and transcoding concurrently
        await asyncio.gather(
            monitor_progress(),
            self.service._run_transcode_job(job)
        )

        # Verify we got progress updates
        self.assertGreater(len(progress_updates), 0)
        self.assertEqual(job.status, "completed")

    async def test_real_cancel_job(self):
        """Test job cancellation with real HandBrake process."""
        if not self.input_file.exists() or self.input_file.stat().st_size < 100:
            self.skipTest("No valid test video file available")

        job_id = await self.service.transcode(
            input_path=str(self.input_file),
            output_path=str(self.output_file),
            preset="Fast 1080p30",  # Use a slower preset to allow cancellation
        )

        job = self.service.jobs[job_id]

        # Start transcoding
        transcode_task = asyncio.create_task(self.service._run_transcode_job(job))

        # Wait a bit then cancel
        await asyncio.sleep(0.5)
        result = await self.service.cancel_job(job_id)

        # Wait for cancellation to complete
        try:
            await asyncio.wait_for(transcode_task, timeout=5)
        except asyncio.TimeoutError:
            transcode_task.cancel()

        self.assertTrue(result)
        self.assertEqual(job.status, "cancelled")


if __name__ == "__main__":
    unittest.main()
