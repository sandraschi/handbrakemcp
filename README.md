# HandBrake MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![MCP 2.12.0](https://img.shields.io/badge/MCP-2.12.0-green.svg)](https://modelcontextprotocol.io/)
[![DXT Compatible](https://img.shields.io/badge/DXT-Compatible-brightgreen)](https://github.com/anthropics/dxt)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue)](https://sandraschi.github.io/handbrake-mcp/)
[![CI/CD Pipeline](https://github.com/sandraschi/handbrake-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/sandraschi/handbrake-mcp/actions/workflows/ci.yml)
[![Docker](https://img.shields.io/badge/Docker-Supported-blue)](https://www.docker.com/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Ready-blue)](https://kubernetes.io/)
[![Security](https://img.shields.io/badge/Security-Enabled-red)](SECURITY.md)
[![Community](https://img.shields.io/badge/Community-Active-blueviolet)](https://github.com/sandraschi/handbrake-mcp/discussions)

A **production-ready**, **FastMCP 3.2.0-compliant** server for professional video transcoding using HandBrakeCLI. Features an **Industrial SOTA Dashboard (v13.1)**, enterprise-grade CI/CD, and robust 127.0.0.1 networking for maximum stability.

##  Features

###  **Core Video Processing**
- ** Professional Transcoding**: Convert between all major video formats (MP4, MKV, AVI, MOV, M4V, etc.)
- ** Batch Processing**: Process multiple files simultaneously with intelligent queue management
- ** Watch Folders**: Automatic processing of new video files with configurable patterns
- ** Real-time Progress**: Live job status updates with detailed progress tracking
- ** Quality Presets**: 50+ optimized HandBrake presets for different use cases
- ** Custom Options**: Fine-tune encoding with advanced HandBrake CLI parameters

###  **Enterprise Infrastructure**
- ** CI/CD Pipeline**: Automated testing, building, and deployment across multiple platforms
- ** Real CLI Integration Testing**: Comprehensive testing with actual HandBrakeCLI calls
- ** Docker Support**: Multi-stage builds with security scanning and monitoring
- ** Kubernetes Ready**: Complete deployment manifests for scalable production use
- ** Monitoring**: Prometheus metrics, Grafana dashboards, and health checks
- ** Security**: Vulnerability scanning, SBOM generation, and security  practices
- ** Professional Documentation**: MkDocs with GitHub Pages deployment and versioned docs
- ** Automated Releases**: Changelog generation, release validation, and community notifications

###  **Advanced Documentation System**
- ** Multiline Decorators**: Self-documenting tools with comprehensive metadata
- ** Multilevel Help**: Basic, detailed, and full documentation levels
- ** Advanced Help**: Troubleshooting, examples, and performance optimization guides
- ** Tool Search**: Find tools by name, description, or category
- ** System Status**: Real-time system health and resource monitoring

###  **MCP 2.12.0 Compliance**
- ** 7 Core Tools**: `transcode_video`, `batch_transcode`, `get_job_status`, `cancel_job`, `get_presets`, `get_loaded_models`, `get_provider_status`
- ** 5 Help Tools**: `help`, `multilevel_help`, `advanced_help`, `tool_categories`, `system_status`
- ** Rich Documentation**: Every tool includes detailed descriptions, examples, and usage notes
- ** Cross-references**: Related tools and workflows for enhanced discoverability

###  **Modern GitHub Features**
- ** GitHub Discussions**: Community Q&A and feature discussions
- ** GitHub Wiki**: Comprehensive documentation and troubleshooting guides
- ** Issue/PR Templates**: Professional bug reports and feature requests
- ** Community Health**: Automated stale issue management and metrics
- ** Security Policy**: Responsible disclosure and vulnerability reporting
- ** Contributing Guide**: Clear development and contribution guidelines
- ** Repository Profile**: Enhanced project showcase and discoverability

##  Quick Start

### Prerequisites

- **Python 3.8+** - Required for core functionality
- **HandBrakeCLI** - Professional video transcoding engine
- **Git** - For cloning the repository
- **(Optional) MCPB CLI** - For packaging distribution bundles
- **(Optional) Docker** - For containerized deployment
- **(Optional) Kubernetes** - For production deployment

### Installing HandBrakeCLI

#### Windows
```powershell
# Using Windows Package Manager (recommended)
winget install HandBrake.HandBrake.CLI

# Verify installation
HandBrakeCLI --version
```

#### macOS
```bash
# Using Homebrew
brew install handbrake

# Verify installation
HandBrakeCLI --version
```

#### Linux (Ubuntu/Debian)
```bash
# Add HandBrake PPA
sudo add-apt-repository ppa:stebbins/handbrake-releases
sudo apt update
sudo apt install handbrake-cli

# Verify installation
HandBrakeCLI --version
```

## 🚀 Installation & Setup

### 1. Prerequisites
- **Python 3.12+** - Core runtime (managed via `uv` recommended).
- **HandBrakeCLI** - Transcoding engine.
- **[uv](https://docs.astral.sh/uv/)** - Modern Python package and tool manager.

### 2. Quick Deployment
You can run the server directly without manual installation using `uvx`:
```powershell
uvx handbrake-mcp-stdio
```

### 3. Claude Desktop Integration
Add the following to your `claude_desktop_config.json`:
```json
"handbrake-mcp": {
  "command": "uv",
  "args": [
    "--directory", 
    "D:/Dev/repos/handbrake-mcp", 
    "run", 
    "handbrake-mcp-stdio"
  ]
}
```

## 📊 Industrial Dashboard (v13.1)
The project includes a premium, SOTA-compliant dashboard for real-time transcoding management.

### Starting the Dashboard
```powershell
cd web_sota
.\start.bat
```
Visit `http://localhost:51595` to access the control plane.

## 📦 Packaging & Distribution
This repository is SOTA 2026 compliant and uses the officially validated `@anthropic-ai/mcpb` workflow for distribution.

```powershell
# Generate a .mcpb distribution bundle
mcpb pack . dist/handbrake-mcp.mcpb
```

### Prerequisites
- [uv](https://docs.astral.sh/uv/) installed (RECOMMENDED)
- Python 3.12+

## 🛠️ Usage

### **Start the Server**

#### FastMCP stdio (Default for Claude)
```powershell
uv run python -m handbrake_mcp.server
```

#### FastAPI Service (For Dashboard)
```powershell
uv run python -m handbrake_mcp.server --http
```

###  **Discover Available Tools**

The server includes a comprehensive self-documentation system:

```python
# Get basic help for all tools
multilevel_help("basic")

# Get detailed help for specific tools
help("transcode_video", "detailed")

# Get comprehensive documentation
multilevel_help("full")

# Search for tools by functionality
search_tools("video")
search_tools("batch")

# Browse tools by category
tool_categories()
```

###  **Industrial Dashboard**

The server includes a premium, SOTA-v13.1 compliant dashboard in `web_sota`. To run it:

```bash
cd web_sota
npm install
npm run dev
```

> [!IMPORTANT]
> **Windows Networking**: If you encounter "Connection Refused" errors, ensure the dashboard is configured to connect to `127.0.0.1` rather than `localhost`. Modern Windows systems resolve `localhost` to IPv6 `::1`, which may bypass the backend IPv4 listeners.

###  **Core MCP Tools**

#### **Video Processing**
- **`transcode_video`** - Single file transcoding with professional quality settings
- **`batch_transcode`** - Multi-file batch processing with parallel execution

#### **Job Management**
- **`get_job_status`** - Real-time progress monitoring with detailed status
- **`cancel_job`** - Immediate job termination with resource cleanup

#### **Configuration & Discovery**
- **`get_presets`** - List all available HandBrake presets
- **`get_loaded_models`** - MCP-compatible model discovery
- **`get_provider_status`** - Comprehensive system health and capabilities

#### **Help & Documentation**
- **`help`** - Tool-specific help at different detail levels
- **`multilevel_help`** - System-wide help (basic, detailed, full, categories)
- **`advanced_help`** - Advanced guides (examples, troubleshooting, performance)
- **`tool_categories`** - Browse tools by functional category
- **`system_status`** - Real-time system health and resource monitoring

###  **Usage Examples**

#### **Basic Video Transcoding**
```python
# Simple conversion with default settings
result = transcode_video("/videos/input.mp4", "/videos/output.mkv")

# High-quality conversion with custom preset
result = transcode_video(
    "/videos/movie.mkv",
    "/videos/movie_hq.mp4",
    preset="HQ 1080p30"
)

# Custom encoding options
result = transcode_video(
    "/videos/input.avi",
    "/videos/output.mp4",
    options={"quality": "20", "encoder": "x264"}
)
```

#### **Batch Processing**
```python
# Process multiple files
results = batch_transcode([
    {
        "input_path": "/videos/movie1.mp4",
        "output_path": "/videos/movie1.mkv",
        "preset": "Fast 1080p30"
    },
    {
        "input_path": "/videos/movie2.mp4",
        "output_path": "/videos/movie2.mp4"
    }
])

# Check progress of batch jobs
for result in results:
    status = get_job_status(result.job_id)
    print(f"Job {result.job_id}: {status.status} ({status.progress}%)")
```

#### **Job Monitoring & Control**
```python
# Monitor job progress
job_id = "transcode_2025_01_22_143022"
while True:
    status = get_job_status(job_id)
    if status.status in ["completed", "failed", "cancelled"]:
        print(f"Job finished: {status.status}")
        if status.error:
            print(f"Error: {status.error}")
        break
    print(f"Progress: {status.progress}%")
    time.sleep(5)

# Cancel problematic job
cancel_job("job_12345")
```

#### **System Management**
```python
# Check system health
status = get_provider_status()
print(f"Active jobs: {status['active_jobs']}")
print(f"Available presets: {len(status['supported_presets'])}")

# Get available presets
presets = get_presets()
fast_presets = [p for p in presets if "Fast" in p]
print(f"Fast presets: {fast_presets}")
```

###  **Advanced Documentation Access**

#### **Multilevel Help System**
```python
# Basic overview of all tools
help_overview = multilevel_help("basic")

# Detailed information about specific tools
transcode_help = multilevel_help("detailed", "transcode_video")

# Complete documentation for all tools
full_docs = multilevel_help("full")

# Browse tools by category
categories = multilevel_help("categories")
```

#### **Advanced Help Types**
```python
# Usage examples and  practices
examples = advanced_help("examples")

# Troubleshooting guide
troubleshooting = advanced_help("troubleshooting")

# Performance optimization guide
performance = advanced_help("performance")

# System overview
overview = advanced_help("overview")
```

###  **Self-Documenting Tools**

Every tool includes comprehensive documentation accessible through the help system:

```python
# Get full documentation for any tool
full_doc = help("transcode_video", "full")
print(full_doc)
```

This will show:
- Complete tool description with features
- Parameter documentation with types and examples
- Multiple usage examples (basic, advanced, real-world)
- Return value specifications
- Important notes and warnings
- Related tools and workflows
- Version information

##  Packaging & Distribution

This repository uses the SOTA 2026 packing workflow. See the [Installation](#installation-options) section for details on generating distribution bundles.


## 📖 Documentation & Resources
For detailed technical guides, standards, and advanced usage, please refer to the local documentation hub:
- **[Documentation Index](docs/index.md)**: Your primary entry point for guides and help.
- **[CHANGELOG.md](CHANGELOG.md)**: Track version history and industrialization milestones.

## 🤝 Contributing
Contributions are welcome! Please follow the materialist efficiency standards-based development patterns outlined in our internal documentation.

## 📜 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
**HandBrake MCP | Industrial Transcoding Control Plane | 2026**
