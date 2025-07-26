# HandBrake MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![DXT Compatible](https://img.shields.io/badge/DXT-Compatible-brightgreen)](https://github.com/anthropics/dxt)

A FastMCP 2.10-compliant server for video transcoding using HandBrakeCLI. Part of the media processing toolchain.

## 🌟 Features

- **Video Transcoding**: Convert between various video formats
- **Batch Processing**: Process multiple files in sequence
- **Watch Folders**: Automatically process new video files
- **Progress Tracking**: Real-time job status updates
- **MCP 2.10 Compliant**: Full compatibility with Model Control Protocol
- **DXT Ready**: Package as a Desktop Extension

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- [HandBrakeCLI](https://handbrake.fr/downloads2.php) installed and in PATH
- (Optional) [DXT CLI](https://github.com/anthropics/dxt) for packaging

### Installation

1. Clone the repository:
   ```powershell
   git clone https://github.com/yourusername/handbrakemcp.git
   cd handbrakemcp
   ```

2. Create and activate a virtual environment:
   ```powershell
   # Windows
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   
   # Unix/macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the package in development mode:
   ```powershell
   pip install -e ".[dev]"
   ```

4. Configure your environment:
   ```powershell
   Copy-Item .env.example .env
   # Edit .env with your configuration
   ```

## 🛠️ Usage

### Start the server

```powershell
uvicorn handbrake_mcp.main:app --reload
```

### Using the API

Transcode a video:
```http
POST /api/v1/transcode
Content-Type: application/json

{
    "input_path": "/path/to/input.mp4",
    "output_path": "/path/to/output.mkv",
    "preset": "Fast 1080p30"
}
```

### Available MCP Tools

- `transcode_video`: Transcode a single video file
- `batch_transcode`: Process multiple video files
- `get_presets`: List available HandBrake presets
- `get_job_status`: Check status of a transcoding job
- `cancel_job`: Stop an ongoing transcoding job

## 📦 DXT Packaging

Package the server as a DXT extension:

```powershell
# Install DXT CLI (if not already installed)
npm install -g @anthropic/dxt

# Create the package
dxt pack -o handbrakemcp.dxt
```

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📚 Resources

- [FastMCP Documentation](https://fastmcp.readthedocs.io/)
- [DXT Documentation](https://github.com/anthropics/dxt)
- [HandBrake CLI Documentation](https://handbrake.fr/docs/)
- [Anthropic MCP](https://github.com/anthropics/mcp)
