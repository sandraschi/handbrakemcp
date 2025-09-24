"""DXT build script for HandBrake MCP.

This script handles the packaging of HandBrake MCP into a DXT package.
"""

import json
import os
import shutil
import site
import sys
import zipfile
from pathlib import Path
from typing import Optional, Dict, Any

# Package information
PACKAGE_NAME = "handbrake_mcp"
VERSION = "0.1.0"
DIST_DIR = Path("dist")
DIST_DIR.mkdir(exist_ok=True)

def validate_manifest(manifest_path: Path) -> Dict[str, Any]:
    """Validate the DXT manifest file."""
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        # Check required fields
        required_fields = ["name", "version", "display_name", "description", "server"]
        for field in required_fields:
            if field not in manifest:
                raise ValueError(f"Missing required field in manifest: {field}")
        
        # Ensure server configuration is valid
        server = manifest.get("server", {})
        if "command" not in server or not isinstance(server["command"], list):
            raise ValueError("Invalid or missing 'command' in server configuration")
        
        # Validate prompts
        if "prompts" not in manifest:
            raise ValueError("Missing 'prompts' section in manifest")
            
        for prompt in manifest["prompts"]:
            if not all(key in prompt for key in ["name", "description", "template"]):
                raise ValueError("Prompt is missing required fields (name, description, or template)")
        
        return manifest
    
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in manifest: {e}")

def get_python_site_packages():
    """Get the path to the current Python's site-packages directory."""
    import sys

    # Get the site-packages directories
    site_packages_paths = site.getsitepackages()

    # Look for the site-packages directory that contains our packages
    for path_str in site_packages_paths:
        path = Path(path_str)
        if path.exists():
            # Check if it contains fastmcp or fastapi (our key packages)
            if (path / "fastmcp").exists() or (path / "fastapi").exists():
                return path

    # Fallback: construct the path manually
    python_dir = Path(sys.executable).parent
    fallback_path = python_dir / "Lib" / "site-packages"
    if fallback_path.exists() and (fallback_path / "fastmcp").exists():
        return fallback_path

    return None

def copy_dependencies(temp_dir: Path):
    """Skip copying dependencies - Claude Desktop installs them from requirements.txt."""
    print("Skipping dependency copying - Claude Desktop handles this automatically from requirements.txt")

def copy_required_files(temp_dir: Path, root_dir: Path, version: str):
    """Copy required files to the temporary directory."""
    # Create necessary directories
    (temp_dir / PACKAGE_NAME).mkdir(exist_ok=True, parents=True)

    # Copy Python package files
    src_dir = Path("src") / PACKAGE_NAME
    if not src_dir.exists():
        raise FileNotFoundError(f"Source directory not found: {src_dir}")

    # Copy all Python files from src/handbrake_mcp
    for py_file in src_dir.glob("**/*.py"):
        rel_path = py_file.relative_to(src_dir)
        target_path = temp_dir / PACKAGE_NAME / rel_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(py_file, target_path)

    # Copy the manifest
    manifest_src = root_dir / "manifest.json"
    if manifest_src.exists():
        shutil.copy2(manifest_src, temp_dir / "manifest.json")
    else:
        raise FileNotFoundError(f"DXT manifest not found: {manifest_src}")

    # Copy config directory if it exists
    config_src = root_dir / "config" if (root_dir / "config").exists() else root_dir / "src" / PACKAGE_NAME / "config"
    if config_src.exists():
        shutil.copytree(config_src, temp_dir / "config", dirs_exist_ok=True)
    
    # Copy any additional required files
    for extra_file in ["README.md", ".env.example", "pyproject.toml", "requirements.txt", "requirements-dev.txt"]:
        extra_file_path = root_dir / extra_file
        if extra_file_path.exists():
            shutil.copy2(extra_file_path, temp_dir)

    # Copy DXT-specific documentation
    dxt_readme = root_dir / "README.md"
    if dxt_readme.exists():
        shutil.copy2(dxt_readme, temp_dir / "README_DXT.md")

    # Copy docs directory if it exists
    docs_dir = root_dir / "docs"
    if docs_dir.exists():
        shutil.copytree(docs_dir, temp_dir / "docs", dirs_exist_ok=True)

    # Create __init__.py in package directory if it doesn't exist
    init_file = temp_dir / PACKAGE_NAME / "__init__.py"
    if not init_file.exists():
        init_file.parent.mkdir(parents=True, exist_ok=True)
        init_file.write_text("# HandBrake MCP package\n")

    # Create setup.py for the package
    setup_py = temp_dir / "setup.py"
    setup_py_content = f'''"""Setup script for {PACKAGE_NAME}."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="{PACKAGE_NAME}",
    version="{version}",
    author="Sandra Schi",
    author_email="your.email@example.com",
    description="HandBrake MCP Server for video transcoding",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={dict(
        console_scripts=[
            "{PACKAGE_NAME.replace('_', '-')}-server = {PACKAGE_NAME}.main:main",
            "{PACKAGE_NAME.replace('_', '-')}-stdio = {PACKAGE_NAME}.stdio_main:main",
        ],
    )},
)
'''
    # Replace placeholders in the content
    final_content = (setup_py_content
                    .replace("{PACKAGE_NAME}", PACKAGE_NAME)
                    .replace("{version}", version))
    setup_py.write_text(final_content)

def check_venv_and_provide_instructions():
    """Check if virtual environment exists and provide instructions."""
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    venv_path = root_dir / "venv"

    if not venv_path.exists():
        print("=" * 60)
        print("WARNING: Virtual environment not found!")
        print("Please run one of the following to set up the environment:")
        print("")
        print("Windows:")
        print("  python dxt/setup-venv.py")
        print("  OR")
        print("  .\\dxt\\activate-venv.ps1 -Create -Install")
        print("")
        print("Unix/Linux:")
        print("  python dxt/setup-venv.py")
        print("  OR")
        print("  ./dxt/activate-venv.sh --create --install")
        print("=" * 60)
        return False

    return True

def create_dxt_package():
    """Create the DXT package."""
    # Check virtual environment
    if not check_venv_and_provide_instructions():
        return False

    # Get the script's directory to handle paths correctly
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent

    # Validate the manifest first
    manifest_path = root_dir / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"DXT manifest not found: {manifest_path}")
    manifest = validate_manifest(manifest_path)
    version = manifest.get("version", VERSION)

    # Create temporary directory for packaging
    temp_dir = DIST_DIR / f"{PACKAGE_NAME.replace('_', '-')}-{version}"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True)

    try:
        # Copy required files
        print(f"Creating DXT package in: {temp_dir}")
        copy_required_files(temp_dir, root_dir, version)

        # Copy Python dependencies
        copy_dependencies(temp_dir)
        
        # Create the zip archive
        output_file = DIST_DIR / f"{PACKAGE_NAME.replace('_', '-')}-{version}.dxt"
        if output_file.exists():
            output_file.unlink()
        
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(temp_dir)
                    zipf.write(file_path, arcname)
        
        print(f"Successfully created DXT package: {output_file}")
        return True
    
    except Exception as e:
        print(f"Error creating DXT package: {e}", file=sys.stderr)
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        return False
    finally:
        # Clean up temporary directory
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    if create_dxt_package():
        sys.exit(0)
    else:
        sys.exit(1)
