"""Tests for DXT packaging functionality."""
import json
import subprocess
import sys
from pathlib import Path
from unittest import TestCase, mock

import pytest
from fastmcp import FastMCP

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.dxt_generator import generate_dxt_manifest  # noqa: E402


class TestDXTPackaging(TestCase):
    """Test DXT packaging functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manifest = generate_dxt_manifest()
    
    def test_manifest_structure(self):
        """Test that the manifest has the required structure."""
        required_fields = [
            "schema_version",
            "name",
            "version",
            "description",
            "entrypoint",
            "capabilities",
            "permissions",
            "mcp",
            "environment",
        ]
        
        for field in required_fields:
            self.assertIn(field, self.manifest)
    
    def test_mcp_tools_present(self):
        """Test that MCP tools are included in the manifest."""
        self.assertIn("tools", self.manifest["mcp"])
        self.assertIsInstance(self.manifest["mcp"]["tools"], list)
        
        # Check for some expected tools
        tool_names = {tool["name"] for tool in self.manifest["mcp"]["tools"]}
        expected_tools = {"transcode_video", "batch_transcode", "get_presets"}
        self.assertTrue(expected_tools.issubset(tool_names))
    
    def test_environment_variables(self):
        """Test that required environment variables are defined."""
        env_vars = {var["name"]: var for var in self.manifest["environment"]}
        
        # Check for required variables
        required_vars = ["HBB_PATH", "DEFAULT_PRESET", "LOG_LEVEL"]
        for var in required_vars:
            self.assertIn(var, env_vars)
    
    @mock.patch("subprocess.run")
    def test_dxt_generator_script(self, mock_run):
        """Test that the DXT generator script runs successfully."""
        # Mock subprocess.run to avoid actually creating files
        mock_run.return_value.returncode = 0
        
        # Run the DXT generator
        from tools.dxt_generator import generate_dxt_package
        
        with mock.patch("shutil.copytree"), \
             mock.patch("shutil.copy2"), \
             mock.patch("shutil.make_archive"):
            
            output_dir = Path("test_output")
            generate_dxt_package(output_dir)
            
            # Verify the output directory was created
            output_dir.rmdir()  # Clean up
    
    def test_manifest_json_serializable(self):
        """Test that the manifest is JSON serializable."""
        try:
            json.dumps(self.manifest)
        except (TypeError, ValueError) as e:
            self.fail(f"Manifest is not JSON serializable: {e}")


if __name__ == "__main__":
    pytest.main([__file__])
