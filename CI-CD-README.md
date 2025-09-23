# CI/CD Setup Guide

This document describes the comprehensive CI/CD pipeline for the HandBrake MCP Server project.

## 🚀 Overview

The CI/CD pipeline automates:
- ✅ **Code Quality Checks** - Linting, formatting, type checking
- ✅ **Automated Testing** - Unit tests, integration tests, coverage
- ✅ **Security Scanning** - Vulnerability scans, dependency checks
- ✅ **DXT Package Building** - Automated package creation with dependencies
- ✅ **Docker Building** - Multi-stage Docker builds with security scanning
- ✅ **Version Management** - Automated versioning and releases
- ✅ **Deployment** - Docker, Kubernetes, and cloud deployment

## 📋 Prerequisites

- GitHub repository with admin access
- GitHub Actions enabled
- Docker Hub or container registry (for Docker builds)
- Kubernetes cluster (optional, for K8s deployment)

## 🔧 GitHub Actions Workflows

### 1. Main CI/CD Pipeline (`.github/workflows/ci.yml`)
**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`
- Manual workflow dispatch

**Features:**
- **Quality Checks**: Black, isort, flake8, mypy, security scanning
- **Multi-Platform Testing**: Ubuntu, Windows, macOS with Python 3.8-3.11
- **DXT Package Building**: Automated package creation with dependency validation
- **Automated Releases**: GitHub releases with DXT packages
- **Coverage Reporting**: Codecov integration

### 2. Version Management (`.github/workflows/version-management.yml`)
**Triggers:**
- Manual workflow dispatch with version bump options

**Features:**
- **Automated Version Bumping**: patch, minor, major versions
- **Multi-file Updates**: Updates version in manifest.json, pyproject.toml, __init__.py
- **Git Tagging**: Creates and pushes version tags
- **Release Creation**: Automated GitHub releases with DXT packages

### 3. Dependency Updates (`.github/workflows/dependency-updates.yml`)
**Triggers:**
- Weekly schedule (Mondays at 6 AM UTC)
- Manual workflow dispatch

**Features:**
- **Outdated Package Detection**: Identifies packages needing updates
- **Security Vulnerability Scanning**: Safety and Bandit scans
- **Automated Updates**: Updates requirements files and commits changes
- **Security Reporting**: Comprehensive dependency reports

### 4. Docker Build and Deploy (`.github/workflows/docker.yml`)
**Triggers:**
- Push to `main` branch
- Version tags (v*)
- Manual workflow dispatch

**Features:**
- **Multi-stage Docker Builds**: Production and development images
- **Security Scanning**: Trivy vulnerability scanning
- **SBOM Generation**: Software Bill of Materials
- **Container Testing**: Automated container health checks

## 🐳 Docker Setup

### Building Docker Images

**Local Development:**
```bash
# Build development image
docker build --target development -t handbrake-mcp:dev .

# Build production image
docker build --target production -t handbrake-mcp:latest .
```

**GitHub Actions:**
- Automatically builds on main branch pushes
- Creates images with proper tagging
- Runs security scans
- Generates SBOMs

### Docker Compose (Local Development)

```bash
# Start all services
docker-compose up -d

# Start with monitoring
docker-compose --profile with-monitoring up -d

# View logs
docker-compose logs -f handbrake-mcp

# Stop services
docker-compose down
```

## ☸️ Kubernetes Deployment

### Prerequisites
```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

# Install Helm (optional)
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

### Deploy to Kubernetes

```bash
# Apply all configurations
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -l app=handbrake-mcp
kubectl get svc handbrake-mcp

# View logs
kubectl logs -f deployment/handbrake-mcp

# Scale deployment
kubectl scale deployment handbrake-mcp --replicas=5

# Update deployment
kubectl set image deployment/handbrake-mcp handbrake-mcp=ghcr.io/sandraschi/handbrake-mcp:v1.2.0
```

### Kubernetes Resources

- **Deployment**: Scalable pod management with health checks
- **Services**: Load balancing and service discovery
- **Ingress**: HTTP routing and SSL termination
- **PVCs**: Persistent storage for watch/processed folders
- **ConfigMaps**: Configuration management

## 🔄 Deployment Scripts

### Automated Deployment (`scripts/deploy.py`)

```bash
# Check prerequisites
python scripts/deploy.py check

# Build DXT package
python scripts/deploy.py build

# Deploy locally
python scripts/deploy.py deploy-local

# Deploy with Docker
python scripts/deploy.py deploy-docker --tag v1.2.0

# Deploy with Docker Compose
python scripts/deploy.py deploy-compose

# Create release
python scripts/deploy.py release
```

### Manual Deployment Options

#### 1. Local Development
```bash
# Setup virtual environment
python dxt/setup-venv.py

# Activate and build
source dxt/venv/bin/activate  # Linux/Mac
# or
.\dxt\venv\Scripts\Activate.ps1  # Windows

# Build DXT package
python dxt/scripts/build.py
```

#### 2. Docker Deployment
```bash
# Build image
docker build -t handbrake-mcp:latest .

# Run container
docker run -p 8000:8000 \
  -v ./watch:/app/watch \
  -v ./processed:/app/processed \
  handbrake-mcp:latest
```

#### 3. Docker Compose
```bash
# Start services
docker-compose up -d

# With monitoring
docker-compose --profile with-monitoring up -d
```

## 📊 Monitoring and Observability

### Health Checks
- **Application Health**: `/health` endpoint
- **Metrics**: `/metrics` endpoint (Prometheus format)
- **Readiness**: Kubernetes readiness probes

### Logging
- **Structured JSON logging** with configurable levels
- **Container logs** via Docker/Kubernetes
- **Centralized logging** setup ready

### Metrics (Prometheus)
- Job progress and status
- System resource usage
- API request metrics
- Error rates and types

## 🔐 Security Features

### GitHub Actions Security
- **Branch Protection**: Required status checks
- **Security Scanning**: Automated vulnerability detection
- **Dependency Checks**: Weekly security updates
- **SBOM Generation**: Software Bill of Materials

### Container Security
- **Non-root User**: Runs as user 1000
- **Read-only Root FS**: Prevents file system modifications
- **Minimal Attack Surface**: Only necessary permissions
- **Security Scanning**: Trivy scans for vulnerabilities

### Application Security
- **Input Validation**: Pydantic models for all inputs
- **CORS Configuration**: Configurable origin policies
- **Rate Limiting**: Built-in request limits
- **API Authentication**: Optional API key support

## 🚀 Release Process

### Automated Releases
1. **Version Bump**: Use GitHub Actions workflow
2. **Build**: Automatic DXT package creation
3. **Test**: All tests pass on multiple platforms
4. **Release**: GitHub release with DXT package
5. **Deploy**: Optional Docker and K8s deployment

### Manual Releases
```bash
# 1. Update version in dxt/manifest.json
# 2. Commit changes
git commit -m "chore: bump version to 1.2.0"

# 3. Create and push tag
git tag v1.2.0
git push origin v1.2.0

# 4. GitHub Actions will handle the rest
```

## 📈 CI/CD Pipeline Status

### Quality Gates
- ✅ **Code Quality**: Black, isort, flake8, mypy
- ✅ **Security**: Safety, Bandit, Trivy scans
- ✅ **Testing**: 95%+ test coverage required
- ✅ **Performance**: Load testing and benchmarks
- ✅ **Documentation**: README and API docs

### Deployment Gates
- ✅ **Build Success**: All platforms must build
- ✅ **Test Success**: All tests must pass
- ✅ **Security Scan**: No critical vulnerabilities
- ✅ **Package Validation**: DXT package size and integrity checks

## 🛠️ Maintenance

### Regular Tasks
- **Dependency Updates**: Weekly automated updates
- **Security Scans**: Continuous monitoring
- **Performance Monitoring**: Regular load testing
- **Documentation Updates**: Keep docs current

### Monitoring
- **GitHub Actions**: Monitor workflow runs
- **Application Health**: Check service endpoints
- **Resource Usage**: Monitor CPU/memory usage
- **Error Rates**: Track and analyze errors

## 📞 Support

For CI/CD issues:
1. Check GitHub Actions workflow runs
2. Review logs and error messages
3. Check the CI-CD-README.md for troubleshooting
4. Create issues for persistent problems

## 🔄 Workflow Integration

The CI/CD pipeline integrates with:
- **Git Flow**: Branch-based development workflow
- **Semantic Versioning**: Automated version management
- **Conventional Commits**: Automated changelog generation
- **Pull Request Process**: Automated testing and reviews

---

**🎯 The CI/CD pipeline is production-ready and provides comprehensive automation for the entire development lifecycle!**
