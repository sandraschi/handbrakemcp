#!/usr/bin/env python3
"""
CI/CD Setup Script for HandBrake MCP Server.

This script helps set up the CI/CD pipeline and validates the configuration.
"""

import os
import sys
from pathlib import Path

def check_github_actions():
    """Check GitHub Actions setup."""
    print("🔍 Checking GitHub Actions...")

    workflows_dir = Path(".github/workflows")
    if not workflows_dir.exists():
        print("❌ .github/workflows directory not found")
        return False

    required_files = [
        "ci.yml",
        "version-management.yml",
        "dependency-updates.yml",
        "docker.yml"
    ]

    missing_files = []
    for file in required_files:
        if not (workflows_dir / file).exists():
            missing_files.append(file)

    if missing_files:
        print(f"❌ Missing workflow files: {', '.join(missing_files)}")
        return False

    print("✅ GitHub Actions workflows found")
    return True

def check_docker_setup():
    """Check Docker setup."""
    print("🔍 Checking Docker setup...")

    dockerfile = Path("Dockerfile")
    if not dockerfile.exists():
        print("❌ Dockerfile not found")
        return False

    docker_compose = Path("docker-compose.yml")
    if not docker_compose.exists():
        print("⚠️  docker-compose.yml not found (optional)")

    print("✅ Docker setup found")
    return True

def check_kubernetes_setup():
    """Check Kubernetes setup."""
    print("🔍 Checking Kubernetes setup...")

    k8s_dir = Path("k8s")
    if not k8s_dir.exists():
        print("⚠️  k8s directory not found (optional)")
        return True

    required_k8s_files = [
        "deployment.yml",
        "service.yml",
        "ingress.yml",
        "pvc.yml",
        "configmap.yml"
    ]

    missing_files = []
    for file in required_k8s_files:
        if not (k8s_dir / file).exists():
            missing_files.append(file)

    if missing_files:
        print(f"⚠️  Missing Kubernetes files: {', '.join(missing_files)}")
    else:
        print("✅ Kubernetes setup found")

    return True

def check_monitoring_setup():
    """Check monitoring setup."""
    print("🔍 Checking monitoring setup...")

    monitoring_dir = Path("monitoring")
    if not monitoring_dir.exists():
        print("⚠️  monitoring directory not found (optional)")
        return True

    prometheus_config = monitoring_dir / "prometheus.yml"
    if prometheus_config.exists():
        print("✅ Prometheus configuration found")

    grafana_provisioning = monitoring_dir / "grafana" / "provisioning"
    if grafana_provisioning.exists():
        print("✅ Grafana provisioning found")

    return True

def validate_ci_cd_setup():
    """Validate the complete CI/CD setup."""
    print("🚀 Validating CI/CD Setup")
    print("=" * 50)

    checks = [
        check_github_actions,
        check_docker_setup,
        check_kubernetes_setup,
        check_monitoring_setup
    ]

    all_passed = True
    for check in checks:
        try:
            if not check():
                all_passed = False
        except Exception as e:
            print(f"❌ Error during {check.__name__}: {e}")
            all_passed = False

    print("=" * 50)
    if all_passed:
        print("✅ CI/CD setup validation passed!")
        print("\n📋 Next Steps:")
        print("1. Enable GitHub Actions in repository settings")
        print("2. Configure repository secrets (optional)")
        print("3. Push to main branch to trigger CI/CD")
        print("4. Check .github/workflows/ for workflow files")
        print("5. See CI-CD-README.md for detailed documentation")
    else:
        print("❌ Some checks failed. Please review the output above.")
        return False

    return True

def main():
    """Main setup function."""
    print("HandBrake MCP Server - CI/CD Setup Validation")
    print("=" * 50)

    try:
        success = validate_ci_cd_setup()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⚠️  Setup interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
