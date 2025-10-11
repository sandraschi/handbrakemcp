"""Main FastMCP application for HandBrake MCP server."""
import asyncio
import logging
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
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

# Initialize FastAPI app
app = FastAPI(
    title="HandBrake MCP Server",
    description="FastMCP 2.12.0 compliant server for video transcoding with HandBrake",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# FastMCP instance for stdio mode is in stdio_main.py

# MCP tools are not used in the main FastAPI server

# Include API routers
# from handbrake_mcp.api.v1.endpoints import router as api_router
# app.include_router(api_router, prefix="/api/v1")

# Mount MCP app - Note: This may need adjustment based on FastMCP 2.12.0 API
# For now, commenting out as it may not be needed for stdio-only mode
# app.mount("/mcp", mcp.app)


async def process_new_file(file_path: Path):
    """Process a new file detected by the watch service."""
    logger.info(f"Processing new file: {file_path}")
    try:
        output_dir = settings.processed_folder or file_path.parent
        await processing_service.process_file(
            input_path=file_path,
            output_dir=output_dir,
            preset=settings.default_preset,
            delete_original=settings.delete_original_after_processing,
        )
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}")


@app.on_event("startup")
async def startup_event():
    """Initialize application services on startup."""
    logger.info("Starting HandBrake MCP server...")
    
    # Initialize notification service
    await notification_service.initialize()
    
    # Initialize watch folders
    if settings.watch_folders:
        logger.info(f"Watching folders: {', '.join(str(f) for f in settings.watch_folders)}")
        await watch_service.start(
            callback=process_new_file,
            watch_dirs=settings.watch_folders,
        )
    
    logger.info("HandBrake MCP server started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    logger.info("Shutting down HandBrake MCP server...")
    
    # Stop the watch service
    if watch_service.is_running():
        await watch_service.stop()
    
    # Shut down the notification service
    await notification_service.shutdown()
    
    logger.info("HandBrake MCP server has been shut down")


async def main():
    """Main stdio server function."""
    logger.info("Starting HandBrake MCP server (stdio mode)...")

    # Initialize notification service
    await notification_service.initialize()

    # Initialize watch folders
    if settings.watch_folders:
        logger.info(f"Watching folders: {', '.join(str(f) for f in settings.watch_folders)}")
        await watch_service.start(
            callback=process_new_file,
            watch_dirs=settings.watch_folders,
        )

    logger.info("HandBrake MCP server started successfully")

    # Run the MCP server
    # MCP server is not started in FastAPI mode


# Health check endpoint
@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "ok", "version": "0.1.0"}


# MCP tools are registered in stdio_main.py for stdio mode from tools.utility_tools


# For DXT compatibility and dual mode support
if __name__ == "__main__":
    # When run as a module (python -m handbrake_mcp.main), always run in stdio mode for MCP clients
    # Claude Desktop expects stdio mode, not FastAPI HTTP mode
    from handbrake_mcp.stdio_main import main
    main()
