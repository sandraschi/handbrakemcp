"""DXT manifest generator for HandBrake MCP."""
import importlib
import inspect
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Type, Union

import pkg_resources
from fastmcp import FastMCP
from pydantic import BaseModel

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import the main app to register MCP tools
from handbrake_mcp.main import app, mcp  # noqa: E402


def get_package_info() -> Dict[str, str]:
    """Get package information from pyproject.toml."""
    try:
        import toml
        
        pyproject_path = PROJECT_ROOT / "pyproject.toml"
        if not pyproject_path.exists():
            return {}
            
        pyproject = toml.load(pyproject_path)
        project = pyproject.get("project", {})
        
        return {
            "name": project.get("name", "handbrake-mcp"),
            "version": project.get("version", "0.1.0"),
            "description": project.get("description", "HandBrake MCP Server"),
        }
    except ImportError:
        return {
            "name": "handbrake-mcp",
            "version": "0.1.0",
            "description": "HandBrake MCP Server",
        }


def get_mcp_tools() -> List[Dict[str, Any]]:
    """Extract MCP tools from the FastMCP instance."""
    tools = []
    
    # Get all registered tools from the FastMCP instance
    for tool_name, tool_func in mcp.tools.items():
        # Skip internal FastMCP tools
        if tool_name.startswith("mcp."):
            continue
            
        # Get function signature
        sig = inspect.signature(tool_func)
        
        # Get parameter information
        parameters = []
        for param_name, param in sig.parameters.items():
            if param_name in ["self", "mcp_context"]:
                continue
                
            param_info = {
                "name": param_name,
                "type": _get_type_name(param.annotation),
                "required": param.default == inspect.Parameter.empty,
            }
            
            if param.default != inspect.Parameter.empty:
                param_info["default"] = str(param.default)
                
            parameters.append(param_info)
        
        # Get docstring
        doc = inspect.getdoc(tool_func) or ""
        description = doc.split("\n")[0] if doc else f"{tool_name} tool"
        
        tools.append({
            "name": tool_name,
            "description": description,
            "parameters": parameters,
        })
    
    return tools


def _get_type_name(type_hint) -> str:
    """Convert a Python type hint to a string representation."""
    if type_hint is inspect.Parameter.empty:
        return "any"
    
    # Handle Optional types
    if hasattr(type_hint, "__origin__") and type_hint.__origin__ is Union:
        args = [arg for arg in type_hint.__args__ if arg is not type(None)]  # noqa: E721
        if args:
            return _get_type_name(args[0])
    
    # Handle List, Dict, etc.
    if hasattr(type_hint, "__origin__"):
        origin = type_hint.__origin__
        if origin is list or origin is List:
            args = type_hint.__args__
            item_type = _get_type_name(args[0]) if args else "any"
            return f"list[{item_type}]"
        elif origin is dict or origin is Dict:
            args = type_hint.__args__
            key_type = _get_type_name(args[0]) if len(args) > 0 else "any"
            value_type = _get_type_name(args[1]) if len(args) > 1 else "any"
            return f"dict[{key_type}, {value_type}]"
    
    # Handle built-in types
    if hasattr(type_hint, "__name__"):
        return type_hint.__name__.lower()
    elif hasattr(type_hint, "__origin__"):
        return str(type_hint).replace("typing.", "").lower()
    
    return "any"


def generate_dxt_manifest() -> Dict[str, Any]:
    """Generate DXT manifest for the HandBrake MCP server."""
    pkg_info = get_package_info()
    
    return {
        "schema_version": "1.0",
        "name": pkg_info["name"],
        "version": pkg_info["version"],
        "description": pkg_info["description"],
        "entrypoint": "handbrake_mcp.main:app",
        "capabilities": ["mcp"],
        "permissions": {
            "filesystem": {
                "read": [
                    "./"  # Allow reading from the package directory
                ],
                "write": [
                    "./"  # Allow writing to the package directory
                ]
            },
            "network": [
                "*"  # Allow all network access (for webhooks, etc.)
            ]
        },
        "mcp": {
            "tools": get_mcp_tools()
        },
        "environment": [
            {
                "name": "HBB_PATH",
                "description": "Path to HandBrakeCLI executable",
                "required": False,
                "default": "HandBrakeCLI"
            },
            {
                "name": "DEFAULT_PRESET",
                "description": "Default HandBrake preset to use",
                "required": False,
                "default": "Fast 1080p30"
            },
            {
                "name": "WATCH_FOLDERS",
                "description": "Comma-separated list of folders to watch for new videos",
                "required": False,
                "default": ""
            },
            {
                "name": "PROCESSED_FOLDER",
                "description": "Folder to move processed files to (optional)",
                "required": False,
                "default": ""
            },
            {
                "name": "DELETE_ORIGINAL_AFTER_PROCESSING",
                "description": "Whether to delete original files after processing",
                "required": False,
                "default": "false"
            },
            {
                "name": "FILE_PATTERNS",
                "description": "Comma-separated list of file patterns to watch for",
                "required": False,
                "default": "*.mp4,*.mkv,*.avi,*.mov,*.m4v"
            },
            {
                "name": "WEBHOOK_URL",
                "description": "URL to send webhook notifications to",
                "required": False,
                "default": ""
            },
            {
                "name": "WEBHOOK_EVENTS",
                "description": "Comma-separated list of events to send webhooks for",
                "required": False,
                "default": "job_started,job_completed,job_failed"
            },
            {
                "name": "LOG_LEVEL",
                "description": "Logging level (debug, info, warning, error, critical)",
                "required": False,
                "default": "info"
            }
        ]
    }


def generate_dxt_package(output_dir: Optional[Path] = None):
    """Generate DXT package for the HandBrake MCP server."""
    if output_dir is None:
        output_dir = PROJECT_ROOT / "dist"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate manifest
    manifest = generate_dxt_manifest()
    manifest_path = output_dir / "manifest.json"
    
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    
    print(f"✅ Generated DXT manifest at {manifest_path}")
    
    # Create package (zip file)
    import shutil
    import tempfile
    
    pkg_name = f"{manifest['name']}-{manifest['version']}.dxt"
    pkg_path = output_dir / pkg_name
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        
        # Copy package files
        shutil.copytree(
            PROJECT_ROOT / "src" / "handbrake_mcp",
            temp_dir / "handbrake_mcp",
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo")
        )
        
        # Copy requirements
        shutil.copy2(PROJECT_ROOT / "requirements.txt", temp_dir)
        
        # Copy manifest
        shutil.copy2(manifest_path, temp_dir / "manifest.json")
        
        # Create zip file
        shutil.make_archive(str(pkg_path.with_suffix('')), 'zip', temp_dir)
        
        # Rename .zip to .dxt
        (pkg_path.with_suffix('.zip')).rename(pkg_path)
    
    print(f"✅ Created DXT package at {pkg_path}")
    return pkg_path


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate DXT package for HandBrake MCP")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT / "dist",
        help="Output directory for the DXT package"
    )
    
    args = parser.parse_args()
    generate_dxt_package(args.output_dir)
