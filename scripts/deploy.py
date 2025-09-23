#!/usr/bin/env python3
"""
Deployment script for HandBrake MCP Server.

This script handles various deployment scenarios including:
- Local development setup
- Production deployment
- Docker container deployment
- Cloud deployment (AWS, Azure, GCP)
- Kubernetes deployment
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

class DeploymentManager:
    """Manages deployment of HandBrake MCP Server."""

    def __init__(self, environment: str = "development"):
        self.environment = environment
        self.project_root = Path(__file__).parent.parent
        self.dxt_manifest = self._load_dxt_manifest()

    def _load_dxt_manifest(self) -> Dict:
        """Load DXT manifest file."""
        manifest_path = self.project_root / "dxt" / "manifest.json"
        if not manifest_path.exists():
            raise FileNotFoundError(f"DXT manifest not found: {manifest_path}")

        with open(manifest_path, 'r') as f:
            return json.load(f)

    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met."""
        print("Checking prerequisites...")

        # Check Python version
        python_version = sys.version_info
        if python_version < (3, 8):
            print(f"❌ Python 3.8+ required, found {python_version.major}.{python_version.minor}")
            return False
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")

        # Check HandBrake CLI
        try:
            result = subprocess.run(['HandBrakeCLI', '--version'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ HandBrake CLI found: {result.stdout.strip()}")
            else:
                print("⚠️  HandBrake CLI not found in PATH")
                print("   Please install HandBrake CLI or set HBB_PATH environment variable")
        except FileNotFoundError:
            print("⚠️  HandBrake CLI not found in PATH")
            print("   Please install HandBrake CLI or set HBB_PATH environment variable")

        # Check DXT package
        dxt_package = self.project_root / "dist" / f"handbrake-mcp-{self.dxt_manifest['version']}.dxt"
        if dxt_package.exists():
            size_mb = dxt_package.stat().st_size / (1024 * 1024)
            print(f"✅ DXT package found: {size_mb:.1f".1f"B")
        else:
            print("⚠️  DXT package not found. Run build script first.")

        return True

    def build_package(self) -> bool:
        """Build the DXT package."""
        print("Building DXT package...")

        # Check if virtual environment exists
        venv_path = self.project_root / "dxt" / "venv"
        if not venv_path.exists():
            print("Setting up virtual environment...")
            if not self.setup_venv():
                return False

        # Activate venv and build
        if self.environment == "production":
            # Use system Python for production builds
            result = subprocess.run([sys.executable, "dxt/scripts/build.py"],
                                  cwd=self.project_root)
        else:
            # Use virtual environment
            if os.name == 'nt':  # Windows
                python_path = venv_path / "Scripts" / "python.exe"
            else:  # Unix/Linux
                python_path = venv_path / "bin" / "python"

            result = subprocess.run([str(python_path), "dxt/scripts/build.py"],
                                  cwd=self.project_root)

        return result.returncode == 0

    def setup_venv(self) -> bool:
        """Set up virtual environment."""
        print("Setting up virtual environment...")

        venv_path = self.project_root / "dxt" / "venv"
        setup_script = self.project_root / "dxt" / "setup-venv.py"

        if setup_script.exists():
            result = subprocess.run([sys.executable, str(setup_script)],
                                  cwd=self.project_root)
            return result.returncode == 0
        else:
            # Manual venv setup
            result = subprocess.run([sys.executable, "-m", "venv", str(venv_path)],
                                  cwd=self.project_root)
            if result.returncode != 0:
                return False

            # Install requirements
            if os.name == 'nt':  # Windows
                pip_path = venv_path / "Scripts" / "pip.exe"
            else:  # Unix/Linux
                pip_path = venv_path / "bin" / "pip"

            requirements_path = self.project_root / "dxt" / "requirements-dxt.txt"
            if requirements_path.exists():
                result = subprocess.run([str(pip_path), "install", "-r", str(requirements_path)],
                                      cwd=self.project_root)
                return result.returncode == 0

        return True

    def deploy_local(self) -> bool:
        """Deploy locally for development/testing."""
        print("Setting up local development environment...")

        # Create necessary directories
        directories = ["watch", "processed", "logs", "config"]
        for dir_name in directories:
            Path(dir_name).mkdir(exist_ok=True)

        # Create example config
        config_path = Path("config") / "handbrake-mcp.yml"
        if not config_path.exists():
            config_content = f"""# HandBrake MCP Configuration
server:
  host: "127.0.0.1"
  port: 8000
  log_level: "info"

handbrake:
  cli_path: "HandBrakeCLI"
  default_preset: "Fast 1080p30"
  max_concurrent_jobs: 2

watch_folders:
  - "watch"

processed_folder: "processed"

notifications:
  enabled: false
  webhook_url: ""
  email_recipients: []
"""
            with open(config_path, 'w') as f:
                f.write(config_content)
            print(f"✅ Created example configuration: {config_path}")

        # Build package if needed
        if not self.build_package():
            return False

        print("✅ Local development environment ready!")
        print("   To start the server:")
        print("   python -m uvicorn handbrake_mcp.main:app --reload --host 127.0.0.1 --port 8000")
        return True

    def deploy_docker(self, tag: str = "latest") -> bool:
        """Deploy using Docker."""
        print(f"Building Docker image with tag: {tag}")

        # Build Docker image
        cmd = ["docker", "build", "-t", f"handbrake-mcp:{tag}", "."]
        result = subprocess.run(cmd, cwd=self.project_root)

        if result.returncode != 0:
            print("❌ Docker build failed")
            return False

        print(f"✅ Docker image built: handbrake-mcp:{tag}")

        # Run container
        container_name = "handbrake-mcp-server"
        run_cmd = [
            "docker", "run", "-d",
            "--name", container_name,
            "-p", "8000:8000",
            "-v", f"{self.project_root}/watch:/app/watch",
            "-v", f"{self.project_root}/processed:/app/processed",
            f"handbrake-mcp:{tag}"
        ]

        result = subprocess.run(run_cmd, cwd=self.project_root)

        if result.returncode != 0:
            print("❌ Docker run failed")
            return False

        print(f"✅ Container started: {container_name}")
        print("   View logs: docker logs handbrake-mcp-server")
        print("   Stop container: docker stop handbrake-mcp-server")
        return True

    def deploy_docker_compose(self) -> bool:
        """Deploy using Docker Compose."""
        print("Deploying with Docker Compose...")

        if not Path("docker-compose.yml").exists():
            print("❌ docker-compose.yml not found")
            return False

        # Start services
        cmd = ["docker-compose", "up", "-d"]
        result = subprocess.run(cmd, cwd=self.project_root)

        if result.returncode != 0:
            print("❌ Docker Compose failed")
            return False

        print("✅ Docker Compose services started")
        print("   Check status: docker-compose ps")
        print("   View logs: docker-compose logs -f")
        print("   Stop services: docker-compose down")
        return True

    def create_release(self) -> bool:
        """Create a release."""
        print("Creating release...")

        version = self.dxt_manifest.get('version', '0.1.0')
        print(f"Creating release v{version}")

        # Create git tag
        result = subprocess.run(['git', 'tag', f'v{version}'],
                              cwd=self.project_root)
        if result.returncode != 0:
            print("❌ Failed to create git tag")
            return False

        # Push tag
        result = subprocess.run(['git', 'push', 'origin', f'v{version}'],
                              cwd=self.project_root)
        if result.returncode != 0:
            print("❌ Failed to push tag")
            return False

        print(f"✅ Release v{version} created successfully")
        print("   GitHub Actions will handle the rest of the release process")
        return True

def main():
    """Main deployment function."""
    parser = argparse.ArgumentParser(description="HandBrake MCP Deployment Script")
    parser.add_argument(
        "action",
        choices=["check", "build", "deploy-local", "deploy-docker", "deploy-compose", "release"],
        help="Deployment action to perform"
    )
    parser.add_argument(
        "--env",
        choices=["development", "staging", "production"],
        default="development",
        help="Deployment environment"
    )
    parser.add_argument(
        "--tag",
        default="latest",
        help="Docker image tag"
    )

    args = parser.parse_args()

    # Initialize deployment manager
    deployer = DeploymentManager(args.env)

    # Execute action
    actions = {
        "check": deployer.check_prerequisites,
        "build": deployer.build_package,
        "deploy-local": deployer.deploy_local,
        "deploy-docker": lambda: deployer.deploy_docker(args.tag),
        "deploy-compose": deployer.deploy_docker_compose,
        "release": deployer.create_release,
    }

    if args.action not in actions:
        print(f"❌ Unknown action: {args.action}")
        return 1

    try:
        success = actions[args.action]()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
