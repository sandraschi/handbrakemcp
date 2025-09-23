#!/usr/bin/env python3
"""Test runner for HandBrake MCP with flexible test execution."""
import argparse
import subprocess
import sys
from pathlib import Path

def check_handbrake():
    """Check if HandBrakeCLI is available."""
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

def run_tests(test_type="unit", verbose=True, coverage=True):
    """Run tests with specified configuration."""
    cmd = [sys.executable, "-m", "pytest", "tests/"]

    if test_type == "unit":
        cmd.extend(["-m", "unit"])
        if coverage:
            cmd.extend(["--cov=src", "--cov-report=term-missing"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration"])
        cmd.extend(["--tb=short"])
    elif test_type == "fast_integration":
        # Run integration tests but skip slow ones
        cmd.extend(["-m", "integration and not slow"])
        cmd.extend(["--tb=short"])
    elif test_type == "all":
        if coverage:
            cmd.extend(["--cov=src", "--cov-report=term-missing"])
    else:
        print(f"Unknown test type: {test_type}")
        return False

    if verbose:
        cmd.append("-v")

    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode == 0

def main():
    parser = argparse.ArgumentParser(
        description="Run HandBrake MCP tests",
        epilog="""
Test Types:
  unit              - Fast unit tests using mocks (default)
  integration       - Real HandBrake CLI integration tests (all)
  fast_integration  - Real HandBrake CLI tests (excluding slow ones)
  all               - Run all tests (unit + integration)
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "test_type",
        choices=["unit", "integration", "fast_integration", "all"],
        default="unit",
        nargs="?",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="Skip coverage reporting"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Reduce output verbosity"
    )

    args = parser.parse_args()

    # Check HandBrake availability for integration tests
    if args.test_type == "integration":
        if not check_handbrake():
            print("❌ HandBrakeCLI not found. Cannot run integration tests.")
            print("   Install HandBrakeCLI and ensure it's in your PATH.")
            return 1
        print("✅ HandBrakeCLI found, running integration tests...")

    elif args.test_type == "all":
        handbrake_available = check_handbrake()
        if handbrake_available:
            print("✅ HandBrakeCLI found, will run all tests including integration")
        else:
            print("⚠️  HandBrakeCLI not found, skipping integration tests")

    # Run tests
    success = run_tests(
        test_type=args.test_type,
        verbose=not args.quiet,
        coverage=not args.no_coverage
    )

    if success:
        print("✅ Tests completed successfully!")
        return 0
    else:
        print("❌ Tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
