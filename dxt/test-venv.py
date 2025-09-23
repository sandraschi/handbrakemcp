#!/usr/bin/env python3
"""Test script to verify DXT virtual environment setup.

This script tests that all necessary dependencies are available
and the virtual environment is properly configured.
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported."""
    required_modules = [
        'fastmcp',
        'fastapi',
        'uvicorn',
        'pydantic',
        'dotenv',  # python-dotenv installs as 'dotenv'
        'watchdog',
        'httpx',
        'psutil',
        'pathlib',
        'typing',
        'json',
        'shutil',
        'zipfile'
    ]

    missing_modules = []

    for module in required_modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module} - {e}")
            missing_modules.append(module)

    return len(missing_modules) == 0

def test_venv_location():
    """Test that we're running in the correct virtual environment."""
    script_dir = Path(__file__).parent
    venv_path = script_dir / "venv"

    if not venv_path.exists():
        print("✗ Virtual environment not found")
        return False

    # Check if we're running from the venv
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✓ Running in virtual environment")
        return True
    else:
        print("⚠ Not running in virtual environment")
        return False

def test_package_versions():
    """Test that we have appropriate versions of key packages."""
    version_tests = [
        ('fastmcp', '2.12.0', lambda v: tuple(map(int, v.split('.'))) >= (2, 12, 0)),
        ('fastapi', '0.68.0', lambda v: tuple(map(int, v.split('.'))) >= (0, 68, 0)),
        ('pydantic', '2.0.0', lambda v: tuple(map(int, v.split('.'))) >= (2, 0, 0)),
    ]

    all_good = True

    for package, min_version, version_check in version_tests:
        try:
            module = __import__(package)
            version = getattr(module, '__version__', 'unknown')
            if version_check(version):
                print(f"✓ {package} {version} (>= {min_version})")
            else:
                print(f"⚠ {package} {version} (< {min_version})")
                all_good = False
        except Exception as e:
            print(f"✗ {package} - Error checking version: {e}")
            all_good = False

    return all_good

def main():
    """Run all tests."""
    print("DXT Virtual Environment Test")
    print("=" * 40)

    print("\n1. Testing virtual environment location:")
    venv_ok = test_venv_location()

    print("\n2. Testing required imports:")
    imports_ok = test_imports()

    print("\n3. Testing package versions:")
    versions_ok = test_package_versions()

    print("\n" + "=" * 40)
    if venv_ok and imports_ok and versions_ok:
        print("✓ All tests passed! Virtual environment is ready for DXT building.")
        return 0
    else:
        print("✗ Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
