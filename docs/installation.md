# Installation

## System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Linux, macOS, or Windows
- **RAM**: Minimum 2GB, recommended 4GB+
- **Storage**: 500MB free space for installation + transcoding space

## Option 1: DXT Package (Recommended)

The easiest way to install HandBrake MCP Server is using the DXT package:

=== "Linux"
    ```bash
    # Download the latest release
    wget https://github.com/sandraschi/handbrake-mcp/releases/latest/download/handbrake-mcp-{{ version }}.dxt

    # Install with DXT
    dxt install handbrake-mcp-{{ version }}.dxt
    ```

=== "macOS"
    ```bash
    # Download the latest release
    curl -L -o handbrake-mcp-{{ version }}.dxt \
         https://github.com/sandraschi/handbrake-mcp/releases/latest/download/handbrake-mcp-{{ version }}.dxt

    # Install with DXT
    dxt install handbrake-mcp-{{ version }}.dxt
    ```

=== "Windows"
    ```powershell
    # Download the latest release
    Invoke-WebRequest -Uri "https://github.com/sandraschi/handbrake-mcp/releases/latest/download/handbrake-mcp-{{ version }}.dxt" `
                      -OutFile "handbrake-mcp-{{ version }}.dxt"

    # Install with DXT
    dxt install handbrake-mcp-{{ version }}.dxt
    ```

## Option 2: Manual Installation

### Install Python Dependencies

```bash
# Clone the repository
git clone https://github.com/sandraschi/handbrake-mcp.git
cd handbrake-mcp

# Install Python package
pip install -e .
```

### Install HandBrake CLI

=== "Ubuntu/Debian"
    ```bash
    sudo add-apt-repository ppa:stebbins/handbrake-releases
    sudo apt update
    sudo apt install -y handbrake-cli
    ```

=== "CentOS/RHEL/Fedora"
    ```bash
    # Install from RPMFusion repository
    sudo dnf install -y handbrake-cli  # Fedora
    # or
    sudo yum install -y handbrake-cli  # CentOS/RHEL
    ```

=== "macOS"
    ```bash
    # Using Homebrew
    brew install handbrake

    # Or download from https://handbrake.fr/
    ```

=== "Windows"
    ```powershell
    # Using Chocolatey
    choco install handbrake-cli

    # Or download from https://handbrake.fr/
    ```

## Option 3: Docker Installation

!!! note "Coming Soon"
    Docker support is planned for a future release. Stay tuned!

```bash
# Planned Docker command
docker run -p 8000:8000 sandraschi/handbrake-mcp:latest
```

## Verification

After installation, verify everything is working:

```bash
# Check HandBrake CLI
HandBrakeCLI --version

# Check Python package
python -c "import handbrake_mcp; print('HandBrake MCP installed successfully')"

# Check MCP server (if using DXT)
dxt list | grep handbrake
```

## Configuration

After installation, you may want to configure the server:

```bash
# Set environment variables
export HBB_PATH=/usr/bin/HandBrakeCLI
export DEFAULT_PRESET="Fast 1080p30"
export LOG_LEVEL=info

# Or create a .env file
cat > .env << EOF
HBB_PATH=/usr/bin/HandBrakeCLI
DEFAULT_PRESET=Fast 1080p30
LOG_LEVEL=info
HOST=0.0.0.0
PORT=8000
EOF
```

## Next Steps

Once installed, you can:

1. [Start the server](quick-start.md)
2. [Configure your settings](configuration.md)
3. [Begin transcoding videos](usage/basic.md)

## Troubleshooting

### Common Installation Issues

#### "HandBrakeCLI not found"
- Ensure HandBrake CLI is installed and in your PATH
- Set the `HBB_PATH` environment variable to the full path

#### "Permission denied"
- Check that you have write permissions for output directories
- Ensure the user running the server can execute HandBrakeCLI

#### "Python version not supported"
- Upgrade to Python 3.8 or higher
- Check your Python installation: `python --version`

### Getting Help

If you encounter issues:

- Check the [troubleshooting guide](../about/faq.md)
- Search [existing issues](https://github.com/sandraschi/handbrake-mcp/issues)
- Start a [discussion](https://github.com/sandraschi/handbrake-mcp/discussions)
- Create a [new issue](https://github.com/sandraschi/handbrake-mcp/issues/new)

