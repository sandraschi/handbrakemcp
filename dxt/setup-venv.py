#!/usr/bin/env python3
"""Setup script for DXT virtual environment.

This script creates and configures a virtual environment for DXT building.
It works on both Windows and Unix systems.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(cmd, **kwargs):
    """Run a command and return success status."""
    try:
        result = subprocess.run(cmd, shell=True, **kwargs)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running command: {e}")
        return False

def create_venv(venv_path):
    """Create virtual environment."""
    print("Creating virtual environment...")

    if os.path.exists(venv_path):
        print("Virtual environment already exists. Removing...")
        import shutil
        shutil.rmtree(venv_path)

    # Create venv
    if not run_command(f"{sys.executable} -m venv {venv_path}"):
        print("Failed to create virtual environment")
        return False

    print("Virtual environment created successfully")
    return True

def install_dependencies(venv_path, requirements_path):
    """Install dependencies in virtual environment."""
    print("Installing dependencies...")

    if not os.path.exists(requirements_path):
        print(f"Requirements file not found: {requirements_path}")
        return False

    # Get pip path
    if platform.system() == "Windows":
        pip_path = os.path.join(venv_path, "Scripts", "python.exe")
        pip_cmd = f'"{pip_path}" -m pip'
    else:
        pip_path = os.path.join(venv_path, "bin", "python")
        pip_cmd = f'"{pip_path}" -m pip'

    # Upgrade pip
    print("Upgrading pip...")
    if not run_command(f'{pip_cmd} install --upgrade pip'):
        print("Failed to upgrade pip")
        return False

    # Install requirements
    print("Installing requirements...")
    if not run_command(f'{pip_cmd} install -r "{requirements_path}"'):
        print("Failed to install requirements")
        return False

    print("Dependencies installed successfully")
    return True

def activate_venv(venv_path):
    """Print activation instructions."""
    print("\nVirtual environment setup complete!")
    print("=" * 50)

    if platform.system() == "Windows":
        activate_script = os.path.join(venv_path, "Scripts", "Activate.ps1")
        print("To activate the virtual environment, run:")
        print(f'  & "{activate_script}"')
        print("\nThen you can run:")
        print("  python dxt/scripts/build.py")
    else:
        activate_script = os.path.join(venv_path, "bin", "activate")
        print("To activate the virtual environment, run:")
        print(f'  source "{activate_script}"')
        print("\nThen you can run:")
        print("  python dxt/scripts/build.py")

def main():
    """Main setup function."""
    print("DXT Virtual Environment Setup")
    print("=" * 50)

    # Get paths
    script_dir = Path(__file__).parent
    venv_path = script_dir / "venv"
    requirements_path = script_dir / "requirements-dxt.txt"

    # Create venv
    if not create_venv(venv_path):
        return 1

    # Install dependencies
    if not install_dependencies(venv_path, requirements_path):
        return 1

    # Print activation instructions
    activate_venv(venv_path)

    return 0

if __name__ == "__main__":
    sys.exit(main())
