"""Pytest configuration for HandBrake MCP tests."""
import pytest
import subprocess
from pathlib import Path


def is_handbrake_available():
    """Check if HandBrakeCLI is available on the system."""
    try:
        result = subprocess.run(
            ["HandBrakeCLI", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        return False


def pytest_configure(config):
    """Add custom markers."""
    config.addinivalue_line("markers", "unit: Fast unit tests using mocks")
    config.addinivalue_line("markers", "integration: Real HandBrake CLI integration tests")
    config.addinivalue_line("markers", "slow: Tests that take longer to run")


@pytest.fixture(scope="session")
def handbrake_available():
    """Fixture to check if HandBrake is available."""
    return is_handbrake_available()


@pytest.fixture
def skip_if_no_handbrake(handbrake_available):
    """Skip test if HandBrake is not available."""
    if not handbrake_available:
        pytest.skip("HandBrakeCLI not available")

