"""
HandBrake MCP Server

Standardized FastMCP 3.1.0+ compliant server for video transcoding.
Provides dual-mode support (stdio/HTTP) and modular tool registration.
"""

import argparse
import logging
import sys
from contextlib import asynccontextmanager

from fastmcp import FastMCP

# Import tools for registration
import handbrake_mcp.tools.handbrake_tools
import handbrake_mcp.tools.help_tools
import handbrake_mcp.tools.status_tools
from handbrake_mcp.core.config import settings
from handbrake_mcp.services.notification_service import notification_service
from handbrake_mcp.services.processing_service import processing_service
from handbrake_mcp.services.watch_service import watch_service

# Configure logging
logging.basicConfig(
    level=settings.log_level.upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

async def process_new_file(file_path):
    """Callback for file watch service."""
    logger.info(f"New file detected: {file_path}")
    try:
        output_dir = settings.processed_folder or file_path.parent
        await processing_service.process_file(
            input_path=file_path,
            output_dir=output_dir,
            preset=settings.default_preset,
            delete_original=settings.delete_original_after_processing,
        )
    except Exception as e:
        logger.error(f"Processing failed for {file_path}: {e}")


# Lifecycle manager for startup and shutdown
@asynccontextmanager
async def lifespan(mcp_instance: FastMCP):
    """Initialize and shut down background services."""
    logger.info("Initializing background services...")

    # Initialize notification service
    try:
        await notification_service.initialize()
    except Exception as e:
        logger.error(f"Failed to initialize notifications: {e}")

    # Start folder watching if configured
    if settings.watch_folders:
        logger.info(f"Starting watch service for: {settings.watch_folders}")
        try:
            await watch_service.start(
                callback=process_new_file, watch_dirs=settings.watch_folders
            )
        except Exception as e:
            logger.error(f"Failed to start watch service: {e}")

    yield

    logger.info("Shutting down services...")
    if watch_service.is_running():
        await watch_service.stop()
    await notification_service.shutdown()


# Initialize FastMCP app with conversational features
app = FastMCP(
    "HandBrake MCP",
    lifespan=lifespan,
    instructions="""You are HandBrake MCP, an automation server for video transcoding on Windows.

FEATURES:
- Conversational tool returns for natural AI interaction
- Sampling capabilities for agentic workflows (SEP-1577)
- Dual-mode transport support (stdio/HTTP)
- Automated folder watching and processing

USAGE:
1. Use help_ops() to discover available transcoding presets.
2. Use handbrake_ops("transcode", ...) to convert files.
3. Use status_ops() to monitor active encoding jobs.
""",
)


# Register via portmanteau pattern managers if needed,
# or direct registration if they use @app.tool()
# Note: Existing tools use a 'set_mcp_instance' pattern
handbrake_mcp.tools.handbrake_tools.set_mcp_instance(app)
handbrake_mcp.tools.help_tools.set_mcp_instance(app)
handbrake_mcp.tools.status_tools.set_mcp_instance(app)

handbrake_mcp.tools.handbrake_tools.register_pending_tools()
handbrake_mcp.tools.help_tools.register_pending_tools()
handbrake_mcp.tools.status_tools.register_pending_tools()






def run():
    """SOTA-compliant entry point with CLI argument support."""
    parser = argparse.ArgumentParser(description="HandBrake MCP Server")
    parser.add_argument("--http", action="store_true", help="Run in HTTP mode")
    parser.add_argument("--port", type=int, default=10875, help="Port for HTTP mode")
    args, unknown = parser.parse_known_args()

    if args.http:
        logger.info(f"Starting HandBrake MCP on HTTP port {args.port}")
        app.run(transport="http", port=args.port)
    else:
        logger.info("Starting HandBrake MCP on stdio transport")
        app.run(transport="stdio")


if __name__ == "__main__":
    run()
