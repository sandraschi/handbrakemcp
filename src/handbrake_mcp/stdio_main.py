"""Stdio entry point for HandBrake MCP server."""
import asyncio
import logging
import sys
from pathlib import Path
from typing import List, Optional

from fastmcp import FastMCP

from handbrake_mcp.core.config import settings
from handbrake_mcp.services.notification_service import notification_service
from handbrake_mcp.services.processing_service import processing_service
from handbrake_mcp.services.watch_service import watch_service

# Configure logging
logging.basicConfig(
    level=settings.log_level.upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastMCP
mcp = FastMCP(
    name="handbrake-mcp",
    version="0.1.0",
)

# Import MCP tools
from handbrake_mcp.mcp_tools import register_tools_with_mcp

# Register tools with the mcp instance
register_tools_with_mcp(mcp)

def process_new_file(file_path: Path):
    """Process a new file detected by the watch service."""
    logger.info(f"Processing new file: {file_path}")
    try:
        output_dir = settings.processed_folder or file_path.parent
        loop = asyncio.get_event_loop()
        loop.run_until_complete(processing_service.process_file(
            input_path=file_path,
            output_dir=output_dir,
            preset=settings.default_preset,
            delete_original=settings.delete_original_after_processing,
        ))
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}")

def main():
    """Main stdio server function."""
    logger.info("Starting HandBrake MCP server (stdio mode)...")

    # Initialize notification service
    # For stdio servers, we initialize services synchronously
    # The MCP client will handle the event loop
    logger.info("Initializing notification service...")
    try:
        # Initialize notification service synchronously
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(notification_service.initialize())
        logger.info("Notification service initialized")
    except Exception as e:
        logger.warning(f"Failed to initialize notification service: {e}")

    # Initialize watch service
    if settings.watch_folders:
        logger.info(f"Initializing watch service for folders: {', '.join(str(f) for f in settings.watch_folders)}")
        try:
            loop.run_until_complete(watch_service.start(
                callback=process_new_file,
                watch_dirs=settings.watch_folders,
            ))
            logger.info("Watch service initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize watch service: {e}")

    logger.info("HandBrake MCP server started successfully")

    # Run the MCP server in stdio mode synchronously
    mcp.run(transport="stdio")

if __name__ == "__main__":
    # For stdio MCP servers, run main() synchronously
    # The MCP client (Claude Desktop) manages the event loop
    main()
