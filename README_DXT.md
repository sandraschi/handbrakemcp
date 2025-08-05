# HandBrake MCP DXT Package

This document provides instructions for building, installing, and using the HandBrake MCP DXT package, which enables automation of HandBrake video conversion through the MCP protocol.

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git (for cloning the repository)
- HandBrake CLI installed on your system
- Windows, macOS, or Linux (Windows recommended for best compatibility)

## Building the DXT Package

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone https://github.com/sandraschi/handbrake-mcp.git
   cd handbrake-mcp
   ```

2. **Build the DXT package** using the provided build script:
   ```powershell
   # Windows (PowerShell)
   .\build_dxt.ps1
   
   # Linux/macOS
   # chmod +x build_dxt.ps1
   # pwsh -File build_dxt.ps1
   ```

   This will:
   - Create a virtual environment
   - Install all dependencies
   - Run tests (can be skipped with `-NoTests`)
   - Generate the DXT package in the `dist` directory

3. **Verify the DXT package** was created:
   ```
   dist/handbrake-mcp-{version}.dxt
   ```

## Installing the DXT Package

1. **Copy the DXT file** to your Claude Desktop packages directory:
   - Windows: `%APPDATA%\Claude\packages\`
   - macOS: `~/Library/Application Support/Claude/packages/`
   - Linux: `~/.config/claude/packages/`

2. **Restart Claude Desktop** to load the new package

3. **Verify installation** by checking the Claude Desktop logs or using the MCP client to list available services

## Configuring HandBrake MCP

Before using the MCP service, you may need to configure it to work with your HandBrake installation:

1. Copy `.env.example` to `.env` and update the settings:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your preferred text editor and update the following settings:
   ```ini
   # Path to HandBrakeCLI executable
   HANDBRAKE_CLI_PATH="C:\\Program Files\\HandBrake\\HandBrakeCLI.exe"
   
   # Default output directory for converted files
   DEFAULT_OUTPUT_DIR="./output"
   
   # Default encoding preset
   DEFAULT_PRESET="Fast 1080p30"
   
   # Maximum concurrent encoding jobs
   MAX_CONCURRENT_JOBS=2
   
   # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
   LOG_LEVEL="INFO"
   
   # Keep intermediate files after processing
   KEEP_FILES=false
   
   # Send notification when job completes
   NOTIFY_ON_COMPLETE=true
   
   # Default video quality (lower is better, 20-30 is good for HD)
   VIDEO_QUALITY=20
   
   # Default audio bitrate in kbps
   AUDIO_BITRATE=160
   ```

3. Start the MCP server through Claude Desktop or manually:
   ```bash
   python -m handbrake_mcp.server
   ```

## Using the HandBrake MCP Service

Once installed, you can interact with the HandBrake MCP service using the Claude Desktop MCP client or any HTTP client.

### Example: Converting a Video

```python
import requests

# Convert a video to H.264
response = requests.post(
    "http://localhost:8080/convert",
    json={
        "input_file": "/path/to/input.mp4",
        "output_file": "/path/to/output.mkv",
        "preset": "Fast 1080p30",
        "video_quality": 22,
        "audio_bitrate": 192,
        "options": {
            "optimize": True,
            "two_pass": False,
            "deinterlace": True
        }
    }
)
print("Conversion result:", response.json())
```

### Example: Batch Converting Videos

```python
# Batch convert all videos in a directory
response = requests.post(
    "http://localhost:8080/batch_convert",
    json={
        "input_dir": "/path/to/input/videos",
        "output_dir": "/path/to/output",
        "preset": "Fast 1080p30",
        "file_pattern": "*.mp4",
        "recursive": True,
        "options": {
            "overwrite": False,
            "delete_source": False
        }
    }
)
print("Batch conversion results:", response.json())
```

### Example: Creating a Custom Preset

```python
# Create a custom encoding preset
response = requests.post(
    "http://localhost:8080/presets",
    json={
        "name": "My Custom Preset",
        "description": "High quality 1080p with surround sound",
        "settings": {
            "video_encoder": "x264",
            "video_quality": 20,
            "audio_encoder": "av_aac",
            "audio_bitrate": 256,
            "audio_channels": 6,
            "audio_mixdown": "5.1",
            "format": "av_mkv"
        },
        "options": [
            "optimize",
            "keep_common_metadata"
        ]
    }
)
print("Preset creation result:", response.json())
```

## Available Prompts

The following prompts are available for natural language interaction:

- **Convert Video**: "Convert {input_file} to {output_format} with {preset} preset and {quality} quality, then save to {output_dir} with options {options}."
- **Batch Convert**: "Convert all {file_pattern} files in {input_dir} to {output_format} using {preset} preset and save to {output_dir} with {options}."
- **Create Preset**: "Create a new preset named {preset_name} with video settings {video_settings}, audio settings {audio_settings}, and options {options}."
- **List Presets**: "List all available presets matching {filter} with {options}."
- **Get Video Info**: "Show detailed information about {input_file} including {details} with {options}."
- **Optimize Video**: "Optimize {input_file} for {platform} with quality {quality_level} and save to {output_file} with {options}."
- **Extract Audio**: "Extract audio from {input_file} in {format} format with {bitrate}kbps and save to {output_file} with {options}."
- **Create GIF**: "Create a GIF from {input_file} starting at {start_time} with duration {duration} seconds, size {width}x{height}, and {fps}fps, then save to {output_file} with {options}."
- **Resize Video**: "Resize {input_file} to {width}x{height} with {method} scaling and save to {output_file} with {options}."
- **Trim Video**: "Trim {input_file} from {start_time} to {end_time} and save to {output_file} with {options}."
- **Add Subtitles**: "Add subtitles from {subtitle_file} to {input_file} with language {language} and save to {output_file} with {options}."
- **Rotate Video**: "Rotate {input_file} by {degrees} degrees and save to {output_file} with {options}."
- **Adjust Volume**: "Adjust volume of {input_file} by {factor}x and save to {output_file} with {options}."
- **Concatenate Videos**: "Concatenate {input_files} in order and save to {output_file} with {options}."
- **Extract Frames**: "Extract {frame_count} frames from {input_file} starting at {start_time} with interval {interval} seconds and save to {output_dir} with {options}."
- **Stabilize Video**: "Stabilize {input_file} with {method} method and save to {output_file} with {options}."
- **Add Watermark**: "Add watermark from {watermark_file} to {input_file} at position {position} with opacity {opacity} and save to {output_file} with {options}."
- **Change Aspect Ratio**: "Change aspect ratio of {input_file} to {aspect_ratio} using {method} and save to {output_file} with {options}."
- **Adjust Speed**: "Change speed of {input_file} to {speed}x and save to {output_file} with {options}."
- **Create Slideshow**: "Create a slideshow from images in {input_dir} with {duration} seconds per image, {transition} transitions, and save to {output_file} with {options}."

## Troubleshooting

### Common Issues

1. **HandBrakeCLI Not Found**:
   - Ensure HandBrake CLI is installed and the path in the configuration is correct
   - On Windows, the default path is `C:\Program Files\HandBrake\HandBrakeCLI.exe`
   - On macOS, install via Homebrew: `brew install handbrake`
   - On Linux, install via your package manager: `sudo apt install handbrake-cli`

2. **Permission Issues**:
   - Make sure the user running the MCP service has read/write permissions to the input and output directories
   - On Linux/macOS, you may need to run the service with `sudo`

3. **Encoding Failures**:
   - Check the logs for specific error messages
   - Verify that the input file is not corrupted
   - Ensure there's enough disk space for the output file
   - Try with a simpler preset or lower quality settings

### Viewing Logs

Logs can be found in the standard Claude Desktop log location:
- Windows: `%APPDATA%\Claude\logs\`
- macOS: `~/Library/Logs/Claude/`
- Linux: `~/.local/share/claude/logs/`

## Development

### Testing Changes

1. Make your changes to the code
2. Run tests:
   ```bash
   pytest -v
   ```
3. Rebuild the DXT package
4. Copy to Claude Desktop packages directory and restart

### Directory Structure

```
handbrake-mcp/
├── config/                    # Configuration files
│   └── default.toml          # Default configuration
├── src/
│   └── handbrake_mcp/        # Main package
│       ├── __init__.py       # Package initialization
│       ├── server.py         # Main server implementation
│       ├── encoder.py        # HandBrake encoding logic
│       ├── presets.py        # Preset management
│       ├── models.py         # Data models
│       └── utils.py          # Utility functions
├── tests/                    # Test files
├── dxt_build.py              # DXT package builder
├── build_dxt.ps1             # Build script (PowerShell)
├── dxt_manifest.json         # DXT package manifest
└── pyproject.toml            # Project configuration
```

## License

MIT License - See [LICENSE](LICENSE) for details.
