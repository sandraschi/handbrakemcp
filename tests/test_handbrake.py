"""Tests for HandBrake MCP server."""

import asyncio
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from handbrake_mcp.core.config import Settings
from handbrake_mcp.services.activity_log import ActivityLog, activity_log
from handbrake_mcp.services.handbrake import HandBrakeService, TranscodeJob


def create_test_video(output_path: Path, duration_seconds: int = 10) -> bool:
    """Create a minimal test video using ffmpeg if available, otherwise skip."""
    try:
        # 720p/30fps/yuv420p so HandBrake finds a valid title AND the encode
        # lasts long enough for progress-tracking/cancel tests to observe it.
        result = subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "lavfi",
                "-i",
                f"testsrc=size=1280x720:rate=30:duration={duration_seconds}",
                "-pix_fmt",
                "yuv420p",
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-movflags",
                "+faststart",
                str(output_path),
            ],
            capture_output=True,
            timeout=120,
        )
        return result.returncode == 0 and output_path.exists() and output_path.stat().st_size > 10000
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
    patcher = patch("asyncio.create_subprocess_exec")
    mock_subprocess = patcher.start()

    # Patch resource gate: unit tests must not depend on host CPU/RAM load
    # (Goliath idles above the service's 85% memory gate; without this the
    # "unit" tests fail on a busy machine while testing nothing about load).
    res_patcher = patch.object(HandBrakeService, "_check_system_resources", new=AsyncMock())
    res_patcher.start()

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
        b"",  # End of output
    ]
    mock_process.stdout = mock_stdout
    mock_process.stderr = AsyncMock()
    mock_process.stderr.read.return_value = b""

    mock_subprocess.return_value = mock_process

    yield {
        "service": service,
        "test_dir": test_dir,
        "input_file": input_file,
        "output_file": output_file,
        "settings": settings,
        "patcher": patcher,
        "mock_process": mock_process,
    }

    # Cleanup
    patcher.stop()
    res_patcher.stop()
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)


@pytest.mark.unit
class TestHandBrakeServiceUnit:
    """Unit tests for HandBrakeService using mocks."""

    async def test_transcode_success(self, unit_test_setup):
        """Test successful video transcode."""
        setup = unit_test_setup
        job_id = await setup["service"].transcode(
            input_path=str(setup["input_file"]),
            output_path=str(setup["output_file"]),
            preset="Fast 1080p30",
        )

        assert job_id is not None
        assert job_id in setup["service"].jobs

        # Check job status
        job = setup["service"].jobs[job_id]
        assert job.status == "queued"

        # Simulate job completion
        await setup["service"]._run_transcode_job(job)
        assert job.status == "completed"
        assert job.progress == 100.0

    async def test_get_job_status(self, unit_test_setup):
        """Test getting job status."""
        setup = unit_test_setup
        job_id = await setup["service"].transcode(
            input_path=str(setup["input_file"]),
            output_path=str(setup["output_file"]),
        )

        job = await setup["service"].get_job_status(job_id)
        assert job is not None
        assert job.job_id == job_id

    async def test_cancel_job(self, unit_test_setup):
        """Test job cancellation."""
        setup = unit_test_setup

        # Create a job with a running process (bypass validation for testing)
        job_id = "test_cancel_job"
        job = TranscodeJob.model_construct(
            job_id=job_id,
            input_path=setup["input_file"],
            output_path=setup["output_file"],
            status="processing",
            process=setup["mock_process"],
        )
        setup["service"].jobs[job_id] = job

        # Test cancellation
        result = await setup["service"].cancel_job(job_id)
        assert result is True
        assert job.status == "cancelled"

    async def test_get_presets(self, unit_test_setup):
        """Test getting HandBrake presets."""
        setup = unit_test_setup
        # Mock the _run_handbrake method
        with patch.object(setup["service"], "_run_handbrake") as mock_run:
            mock_run.return_value = "Available presets:\n  Fast 1080p30\n  HQ 1080p30\n  Very Fast 1080p30\n"
            presets = await setup["service"].get_presets()
            assert "Fast 1080p30" in presets
            assert "HQ 1080p30" in presets
            assert "Very Fast 1080p30" in presets

    def test_probe_cli_present(self):
        """Probe reports available when the CLI resolves via PATH."""
        from handbrake_mcp.services import handbrake as hb_module
        from handbrake_mcp.services.handbrake import probe_handbrake_cli

        with (
            patch("shutil.which", return_value="C:/fake/HandBrakeCLI.exe"),
            patch.object(hb_module, "gui_install_paths", return_value=[]),
        ):
            result = probe_handbrake_cli()
        assert result == {"available": True, "path": "C:/fake/HandBrakeCLI.exe", "gui_present": False}

    def test_probe_cli_missing(self, tmp_path):
        """Probe reports unavailable (never raises) when nothing resolves."""
        from handbrake_mcp.core.config import settings
        from handbrake_mcp.services import handbrake as hb_module
        from handbrake_mcp.services.handbrake import probe_handbrake_cli

        with (
            patch("shutil.which", return_value=None),
            patch.object(settings, "winget_hbb_path", str(tmp_path / "nope.exe")),
            patch.object(hb_module, "gui_install_paths", return_value=[]),
        ):
            result = probe_handbrake_cli()
        assert result == {"available": False, "path": None, "gui_present": False}

    def test_probe_gui_without_cli(self, tmp_path):
        """Probe flags the classic trap: GUI installed, CLI missing."""
        from handbrake_mcp.core.config import settings
        from handbrake_mcp.services import handbrake as hb_module
        from handbrake_mcp.services.handbrake import probe_handbrake_cli

        fake_gui = tmp_path / "HandBrake.exe"
        fake_gui.write_bytes(b"fake")
        with (
            patch("shutil.which", return_value=None),
            patch.object(settings, "winget_hbb_path", str(tmp_path / "nope.exe")),
            patch.object(hb_module, "gui_install_paths", return_value=[str(fake_gui)]),
        ):
            result = probe_handbrake_cli()
        assert result == {"available": False, "path": None, "gui_present": True}

    def test_parse_presets_modern_cli(self):
        """Parser handles the HandBrakeCLI 1.11 stderr shape (no log/category leakage)."""
        from handbrake_mcp.services.handbrake import HandBrakeService

        sample = (
            "[10:35:18] hb_init: starting libhb thread\n"
            "General/\n"
            "    Very Fast 1080p30\n"
            "        Small H.264 video (up to 1080p30) and AAC stereo audio\n"
            "    Fast 1080p30\n"
            "        H.264 video (up to 1080p30) and AAC stereo audio\n"
            "Devices/\n"
            "    Apple 1080p30 Surround\n"
            "        H.264 video for Apple devices\n"
        )
        presets = HandBrakeService._parse_presets_from_output(HandBrakeService, sample)
        assert "Very Fast 1080p30" in presets
        assert "Fast 1080p30" in presets
        assert "Apple 1080p30 Surround" in presets
        assert not any(p.startswith("[") or p.endswith("/") for p in presets)
        assert not any("H.264 video (up to" in p for p in presets)

    def test_extract_progress_fraction(self):
        """Parser reads the pretty-printed Progress.Working.Progress fraction."""
        from handbrake_mcp.services.handbrake import HandBrakeService

        transcript = (
            'Version: {\n    "Name": "HandBrake"\n}\n'
            "Progress: {\n"
            '    "Working": {\n'
            '        "ETASeconds": 12,\n'
            '        "Progress": 0.4277777,\n'
            "    }\n"
            "}\n"
            "Progress: {\n"
            '    "Working": {\n'
            '        "ETASeconds": 0,\n'
            '        "Progress": 1.0,\n'
            "    }\n"
            "}\n"
        )
        assert HandBrakeService._extract_progress(HandBrakeService, transcript) == 100.0

    def test_extract_progress_ignores_noise(self):
        """Parser returns None with no complete progress block, never raises."""
        from handbrake_mcp.services.handbrake import HandBrakeService

        assert HandBrakeService._extract_progress(HandBrakeService, "") is None
        assert HandBrakeService._extract_progress(HandBrakeService, "[10:35:18] hb_init: x\n") is None
        # truncated block: braces never balance
        assert HandBrakeService._extract_progress(HandBrakeService, 'Progress: {\n    "Working": {\n') is None
        assert HandBrakeService._extract_progress(HandBrakeService, "not json at all {{{") is None


@pytest.fixture
async def integration_test_setup():
    """Pytest fixture for real-CLI integration tests (replaces dead unittest asyncSetUp)."""
    test_dir = Path(tempfile.mkdtemp(prefix="handbrake_integration_test_"))
    input_file = test_dir / "input.mp4"
    output_file = test_dir / "output.mkv"

    # Real test video via ffmpeg; skip the test when neither ffmpeg nor a
    # valid file is available (a dummy header is NOT transcodable input).
    if not create_test_video(input_file):
        shutil.rmtree(test_dir, ignore_errors=True)
        pytest.skip("ffmpeg unavailable: cannot fabricate a transcodable test video")

    service = HandBrakeService()

    # Verify HandBrake is working before the test body runs
    version = await service.get_handbrake_version()
    assert version is not None and version != "unknown", "HandBrakeCLI did not report a version"

    yield {"service": service, "test_dir": test_dir, "input_file": input_file, "output_file": output_file}

    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)


def skip_if_host_loaded():
    """Skip transcode tests when host RAM exceeds the service 85% safety gate.

    The service correctly refuses new encodes on a loaded box; failing the
    test would punish the suite for the service working as designed.
    """
    import psutil

    if psutil.virtual_memory().percent > 85:
        pytest.skip("host RAM above the service 85% gate: encodes correctly refused")


@pytest.mark.integration
@pytest.mark.slow
class TestHandBrakeServiceIntegration:
    """Integration tests for HandBrakeService using real HandBrakeCLI."""

    async def test_real_transcode_success(self, integration_test_setup):
        """Test successful video transcode with real HandBrakeCLI."""
        skip_if_host_loaded()
        setup = integration_test_setup
        job_id = await setup["service"].transcode(
            input_path=str(setup["input_file"]),
            output_path=str(setup["output_file"]),
            preset="Fast 1080p30",
        )

        assert job_id is not None
        assert job_id in setup["service"].jobs

        # Wait for job to complete (with timeout)
        job = setup["service"].jobs[job_id]
        await asyncio.wait_for(setup["service"]._run_transcode_job(job), timeout=120)

        # Verify job completed (progress scale is 0-100)
        assert job.status == "completed"
        assert job.progress == 100.0

        # Verify output file was created
        assert setup["output_file"].exists()
        assert setup["output_file"].stat().st_size > 0

    async def test_real_get_presets(self, integration_test_setup):
        """Test getting HandBrake presets with real CLI."""
        setup = integration_test_setup
        presets = await setup["service"].get_presets()
        assert isinstance(presets, list)
        assert len(presets) > 0

        # Should contain some common presets
        preset_names = [p.lower() for p in presets]
        assert any("fast" in name for name in preset_names) or any("1080p" in name for name in preset_names)

    async def test_real_get_version(self, integration_test_setup):
        """Test getting HandBrake version with real CLI."""
        setup = integration_test_setup
        version = await setup["service"].get_handbrake_version()
        assert version is not None
        assert version != "unknown"

        # Version should be in format like "1.11.2"
        import re

        assert re.match(r"\d+\.\d+\.\d+", version)

    async def test_real_job_status_tracking(self, integration_test_setup):
        """Test job status tracking during real transcoding.

        Honest contract: the job moves queued -> processing -> completed and
        ends at progress 100. Intermediate progress values depend on pipe
        buffering (short encodes flush once); the parser itself is covered
        by test_extract_progress_* unit tests with a canned transcript.
        """
        skip_if_host_loaded()
        setup = integration_test_setup
        # Build the job directly (transcode() would auto-start a second run).
        job_id = "track_001"
        job = TranscodeJob(
            job_id=job_id,
            input_path=setup["input_file"],
            output_path=setup["output_file"],
            preset="Fast 1080p30",
            options={},
            status="queued",
        )
        setup["service"].jobs[job_id] = job

        # Check initial status
        assert job.status == "queued"

        # Start the job and monitor status transitions
        seen_statuses = {job.status}

        async def monitor_progress():
            while job.status in ["queued", "processing"]:
                status = await setup["service"].get_job_status(job_id)
                seen_statuses.add(status.status)
                if status.progress > 0:
                    assert 0 < status.progress <= 100.0
                await asyncio.sleep(0.05)
                # Safety bound: the encode itself finishes; don't spin forever
                if job.status not in ["queued", "processing"]:
                    break

        # Run monitoring and transcoding concurrently
        await asyncio.gather(monitor_progress(), setup["service"]._run_transcode_job(job))

        # Verify lifecycle completed and progress landed on 100
        assert job.status == "completed"
        assert job.progress == 100.0
        assert "processing" in seen_statuses
        assert setup["output_file"].exists()

    async def test_real_cancel_job(self, integration_test_setup):
        """Test job cancellation with real HandBrake process."""
        skip_if_host_loaded()
        setup = integration_test_setup
        # Build the job directly: transcode() would auto-start a duplicate
        # run, leaving a second HandBrake holding input.mp4 at teardown.
        job_id = "cancel_001"
        job = TranscodeJob(
            job_id=job_id,
            input_path=setup["input_file"],
            output_path=setup["output_file"],
            preset="Fast 1080p30",
            options={},
            status="queued",
        )
        setup["service"].jobs[job_id] = job

        # Start transcoding
        transcode_task = asyncio.create_task(setup["service"]._run_transcode_job(job))

        # Wait a bit then cancel
        await asyncio.sleep(0.5)
        result = await setup["service"].cancel_job(job_id)

        # Wait for cancellation to complete
        try:
            await asyncio.wait_for(transcode_task, timeout=10)
        except TimeoutError:
            transcode_task.cancel()

        assert result
        assert job.status == "cancelled"

        # Reap the process before fixture teardown: on Windows a live
        # HandBrake handle keeps input.mp4 locked and rmtree fails.
        for _ in range(100):
            if job.process is None or job.process.returncode is not None:
                break
            await asyncio.sleep(0.1)


class TestActivityLog:
    """Unit tests for the dashboard activity ring (Logging page backend)."""

    def test_log_and_query(self):
        log = ActivityLog(maxlen=10)
        log.log("api", "job queued", meta={"job_id": "job_1"})
        log.log("server", "transcode done", level="INFO")
        out = log.entries()
        assert out["total"] == 2
        assert len(out["entries"]) == 2
        # newest first
        assert out["entries"][0]["detail"] == "transcode done"

    def test_filter_and_clear(self):
        log = ActivityLog(maxlen=10)
        log.log("api", "job queued")
        log.log("server", "all good", level="WARNING")
        assert log.entries(level="warning")["total"] == 1
        assert log.entries(kind="api")["total"] == 1
        assert log.entries(search="QUEUED")["total"] == 1
        assert log.entries(search="nope")["total"] == 0
        assert log.clear() == 2
        assert log.entries()["total"] == 0

    def test_export_shapes(self):
        log = ActivityLog(maxlen=10)
        log.log("api", "hello")
        content, media = log.export("json")
        assert media == "application/json"
        assert '"hello"' in content
        csv_content, csv_media = log.export("csv")
        assert csv_media == "text/csv"
        assert "hello" in csv_content


class TestLoggingApiRoutes:
    """Smoke tests for /api/logs* + /api/browse on the canonical app."""

    @pytest.fixture
    def client(self):
        from starlette.testclient import TestClient

        import handbrake_mcp.server as srv

        with TestClient(srv.app, raise_server_exceptions=False) as c:
            yield c

    def test_logs_roundtrip(self, client):
        r = client.get("/api/logs?limit=5")
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "ok"
        assert isinstance(body["entries"], list)
        assert isinstance(body["total"], int)

    def test_logs_clear_and_export(self, client):
        activity_log.log("test", "clear-me")
        assert client.get("/api/logs?search=clear-me").json()["total"] >= 1
        r = client.request("DELETE", "/api/logs")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"
        r = client.get("/api/logs/export?format=csv")
        assert r.status_code == 200
        assert "text/csv" in r.headers["content-type"]

    def test_browse_drives_and_dir(self, client, tmp_path):
        (tmp_path / "clip.mp4").write_bytes(b"x" * 2048)
        (tmp_path / "subs").mkdir()
        r = client.get("/api/browse")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"
        assert isinstance(r.json()["entries"], list)
        r = client.get("/api/browse", params={"path": str(tmp_path)})
        body = r.json()
        assert body["status"] == "ok"
        names = {e["name"] for e in body["entries"]}
        assert "clip.mp4" in names and "subs" in names
        r = client.get("/api/browse", params={"path": str(tmp_path / "nope")})
        assert r.json()["status"] == "error"

    def test_transcode_accepts_options(self, client, tmp_path):
        import handbrake_mcp.services.handbrake as hb_module

        seen = {}

        async def fake_transcode(input_path, output_path, preset=None, options=None):
            seen.update({"input": input_path, "preset": preset, "options": options})
            return "job_test_1"

        fake_service = MagicMock()
        fake_service.transcode = fake_transcode
        with patch.object(hb_module, "get_handbrake_service", return_value=fake_service):
            r = client.post(
                "/api/transcode",
                json={
                    "input": str(tmp_path / "in.mp4"),
                    "preset": "Fast 1080p30",
                    "options": {"quality": "24", "audio-lang-list": "eng", "subtitle-burned": True},
                },
            )
        assert r.status_code == 200
        assert r.json()["status"] == "ok"
        assert seen["options"]["audio-lang-list"] == "eng"
        assert seen["options"]["subtitle-burned"] is True
