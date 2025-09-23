# HandBrake MCP Server

[![CI/CD Pipeline](https://github.com/sandraschi/handbrake-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/sandraschi/handbrake-mcp/actions/workflows/ci.yml)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue)](https://sandraschi.github.io/handbrake-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MCP 2.12.0](https://img.shields.io/badge/MCP-2.12.0-green.svg)](https://modelcontextprotocol.io/)

> Professional video transcoding server with MCP integration for automated media processing pipelines.

## 🚀 Features

- **🎬 Automated Transcoding**: Convert videos using HandBrakeCLI with preset management
- **📦 Batch Processing**: Handle multiple files with queue management and progress tracking
- **🔍 Real-time Monitoring**: Live progress updates and job status tracking
- **🤖 AI Integration**: MCP 2.12.0 compliant for seamless AI workflow integration
- **📁 Watch Folders**: Automatic processing of new files in monitored directories
- **🔧 REST API**: Web interface for monitoring and control
- **🐳 Container Ready**: Docker support for easy deployment
- **📊 Comprehensive Testing**: Unit and integration tests with real CLI validation

## 📋 Quick Start

### Installation (DXT Package - Recommended)

```bash
# Download latest release
curl -L -o handbrake-mcp.dxt \
     https://github.com/sandraschi/handbrake-mcp/releases/latest/download/handbrake-mcp.dxt

# Install
dxt install handbrake-mcp.dxt
```

### Basic Usage

```bash
# Start the MCP server
handbrake-mcp-server

# Or use stdio mode
handbrake-mcp-stdio
```

## 🛠️ MCP Tools

The server provides comprehensive video processing tools:

- `transcode_video` - Single video file conversion
- `batch_transcode` - Multi-file batch processing
- `get_job_status` - Monitor transcoding progress
- `cancel_job` - Stop running jobs
- `get_presets` - List available HandBrake presets

## 📚 Documentation

- **[📖 Full Documentation](https://sandraschi.github.io/handbrake-mcp/)** - Complete user guide
- **[🚀 Quick Start Guide](https://sandraschi.github.io/handbrake-mcp/quick-start/)** - Get up and running fast
- **[🔧 API Reference](https://sandraschi.github.io/handbrake-mcp/api/tools/)** - Technical documentation
- **[❓ FAQ](https://sandraschi.github.io/handbrake-mcp/about/faq/)** - Common questions and troubleshooting

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   AI Assistant  │────│   MCP Protocol   │────│ HandBrake MCP   │
│                 │    │                  │    │   Server        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Video Files    │────│  HandBrake CLI   │────│  Output Files   │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🎯 Use Cases

- **🏠 Home Media Server**: Automated transcoding for Plex/Jellyfin
- **🎬 Content Creation**: Batch processing for video production
- **🤖 AI Workflows**: Integrated video processing in AI pipelines
- **☁️ Cloud Processing**: Containerized video transcoding
- **📱 Device Optimization**: Convert videos for mobile devices

## 📊 Performance

- **Concurrent Jobs**: Up to 32 simultaneous transcoding tasks
- **Hardware Acceleration**: Automatic detection of NVENC/QSV/AMF
- **Resource Management**: Smart queue management and cleanup
- **Progress Tracking**: Real-time encoding progress updates

## 🔒 Security

- **Input Validation**: Comprehensive path and file validation
- **Resource Limits**: File size and concurrent job limits
- **Process Isolation**: HandBrake CLI runs in separate processes
- **No Data Storage**: Processes files without permanent storage

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone repository
git clone https://github.com/sandraschi/handbrake-mcp.git
cd handbrake-mcp

# Install development dependencies
pip install -e ".[dev]"

# Run tests
python scripts/run_tests.py unit
```

### Testing Strategy

- **Unit Tests**: Fast, isolated component testing
- **Integration Tests**: Real HandBrake CLI validation
- **CI/CD**: Automated testing on multiple platforms

## 📈 Roadmap

- [x] Core MCP integration
- [x] Batch processing capabilities
- [x] Real-time progress tracking
- [x] DXT packaging support
- [ ] Docker containerization
- [ ] Web monitoring interface
- [ ] Plugin system for custom processors
- [ ] Cloud storage integration

## 🙏 Acknowledgments

- **HandBrake Team**: For the excellent HandBrakeCLI encoder
- **MCP Community**: For the Model Context Protocol
- **FastAPI**: For the robust web framework
- **Open Source Community**: For the tools and libraries that make this possible

## 📞 Support

- **[🐛 Issues](https://github.com/sandraschi/handbrake-mcp/issues)** - Bug reports and feature requests
- **[💬 Discussions](https://github.com/sandraschi/handbrake-mcp/discussions)** - Questions and community support
- **[📧 Security](SECURITY.md)** - Security vulnerability reporting
- **[📚 Documentation](https://sandraschi.github.io/handbrake-mcp/)** - User guides and API reference

---

**Built with ❤️ for the media processing community**

[![Star History Chart](https://api.star-history.com/svg?repos=sandraschi/handbrake-mcp&type=Date)](https://star-history.com/#sandraschi/handbrake-mcp&Date)

