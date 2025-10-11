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

# Import MCP tools modules first
import handbrake_mcp.tools.handbrake_tools
import handbrake_mcp.tools.help_tools
import handbrake_mcp.tools.status_tools

# Set MCP instance for decorator-based tool registration
handbrake_mcp.tools.handbrake_tools.set_mcp_instance(mcp)
handbrake_mcp.tools.help_tools.set_mcp_instance(mcp)
handbrake_mcp.tools.status_tools.set_mcp_instance(mcp)

# Register all pending tools with decorators
handbrake_mcp.tools.handbrake_tools.register_pending_tools()
handbrake_mcp.tools.help_tools.register_pending_tools()
handbrake_mcp.tools.status_tools.register_pending_tools()

def main():
    """Main stdio server function."""
    logger.info("Starting HandBrake MCP server (stdio mode)...")

    # Note: For stdio MCP servers, we don't initialize background services
    # like notification_service or watch_service. These are meant for
    # the FastAPI server mode. The MCP client (Claude Desktop) will
    # handle the lifecycle and call the tools as needed.

    logger.info("HandBrake MCP server started successfully")

    # Run the MCP server in stdio mode
    mcp.run(transport="stdio")

if __name__ == "__main__":
    # For stdio MCP servers, run main() synchronously
    # The MCP client (Claude Desktop) manages the event loop
    main()
