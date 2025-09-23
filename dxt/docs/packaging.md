# DXT Packaging Guide for HandBrake MCP

This guide explains how to package the HandBrake MCP server as a DXT (Docker eXecution Template) package for deployment in environments that support the DXT standard.

## Prerequisites

- Python 3.8 or higher
- `pip` package manager
- `git` (for cloning the repository)
- HandBrakeCLI installed on the target system

## Generating the DXT Package

1. **Install Dependencies**

   First, install the required Python packages:

   ```bash
   pip install -r requirements.txt
   pip install toml  # Needed for reading pyproject.toml
   ```

2. **Generate the DXT Package**

   Run the DXT generator script:

   ```bash
   python tools/dxt_generator.py
   ```

   This will create a DXT package in the `dist` directory with a name like `handbrake-mcp-0.1.0.dxt`.

## DXT Package Contents

The generated DXT package includes:

- `manifest.json`: DXT manifest with tool definitions and configuration
- `handbrake_mcp/`: The Python package with all source code
- `requirements.txt`: Python dependencies

## Configuration

The following environment variables can be configured in the DXT manifest or deployment environment:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `HBB_PATH` | Path to HandBrakeCLI executable | `HandBrakeCLI` | No |
| `DEFAULT_PRESET` | Default HandBrake preset | `Fast 1080p30` | No |
| `WATCH_FOLDERS` | Comma-separated list of folders to watch | `` | No |
| `PROCESSED_FOLDER` | Folder to move processed files to | `` | No |
| `DELETE_ORIGINAL_AFTER_PROCESSING` | Delete original files after processing | `false` | No |
| `FILE_PATTERNS` | File patterns to watch for | `*.mp4,*.mkv,*.avi,*.mov,*.m4v` | No |
| `WEBHOOK_URL` | URL for webhook notifications | `` | No |
| `WEBHOOK_EVENTS` | Events to send webhooks for | `job_started,job_completed,job_failed` | No |
| `LOG_LEVEL` | Logging level | `info` | No |

## Deploying the DXT Package

1. **Upload the DXT package** to your DXT-compatible platform
2. **Configure** the environment variables as needed
3. **Deploy** the package

## Testing the DXT Package

After deployment, you can test the MCP tools using the platform's interface or by making HTTP requests to the MCP endpoints.

## Troubleshooting

- **HandBrakeCLI not found**: Ensure HandBrakeCLI is installed and in the system PATH, or set the `HBB_PATH` environment variable to the full path of the HandBrakeCLI executable.
- **Permission denied**: The DXT package needs read/write access to the watch folders and processed folder.
- **Webhook failures**: Check the logs for connection errors and verify the webhook URL is correct.

## Building for Production

For production deployments, consider:

1. Using a specific version of HandBrakeCLI
2. Setting appropriate resource limits
3. Configuring persistent storage for the watch and processed folders
4. Setting up monitoring and alerting for the MCP server

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
