"""Main FastMCP application for HandBrake MCP server."""

import logging
from pathlib import Path

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from handbrake_mcp.core.config import settings
from handbrake_mcp.services.notification_service import notification_service
from handbrake_mcp.services.processing_service import processing_service
from handbrake_mcp.services.watch_service import watch_service
from handbrake_mcp.stdio_main import mcp
import psutil
import time
import subprocess
from pydantic import BaseModel

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

# Mount MCP app for HTTP access
app.mount("/mcp", mcp.app)


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
        logger.info(
            f"Watching folders: {', '.join(str(f) for f in settings.watch_folders)}"
        )
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
        logger.info(
            f"Watching folders: {', '.join(str(f) for f in settings.watch_folders)}"
        )
        await watch_service.start(
            callback=process_new_file,
            watch_dirs=settings.watch_folders,
        )

    logger.info("HandBrake MCP server started successfully")

    # Run the MCP server
    # MCP server is not started in FastAPI mode


# Health check endpoint with system metrics
@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> dict:
    """Health check endpoint with system metrics."""
    return {
        "status": "ok",
        "version": "0.1.0",
        "timestamp": time.time(),
        "system": {
            "cpu_percent": psutil.cpu_percent(),
            "memory": psutil.virtual_memory()._asdict(),
            "disk": psutil.disk_usage("/")._asdict(),
        },
    }


class LaunchRequest(BaseModel):
    repo_path: str


@app.post("/api/fleet/launch")
async def launch_app(request: LaunchRequest):
    """Launch another MCP app via its start.ps1 script."""
    path = Path(request.repo_path)
    if not path.exists():
        return {"success": False, "error": f"Path {request.repo_path} does not exist"}

    # Security check: ensure the path is within the allowed repos directory
    allowed_base = Path("D:/Dev/repos")
    try:
        path.relative_to(allowed_base)
    except ValueError:
        return {
            "success": False,
            "error": "Access denied: outside allowed repository root",
        }

    start_script = path / "web_sota" / "start.ps1"
    if not start_script.exists():
        # Fallback for older structures
        start_script = path / "web" / "start.ps1"
        if not start_script.exists():
            return {
                "success": False,
                "error": f"No start.ps1 found in {request.repo_path}",
            }

    try:
        # Start the process in the background using powershell
        # Use -windowstyle hidden if we don't want a pop-up, but for now let's keep it visible for debugging if needed
        subprocess.Popen(
            [
                "powershell.exe",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(start_script),
            ],
            cwd=str(path),  # Important for relative paths in the script
            creationflags=subprocess.CREATE_NEW_CONSOLE,  # Run in a new window so it persists
        )
        return {
            "success": True,
            "message": f"Launch sequence initiated for {path.name}",
        }
    except Exception as e:
        logger.error(f"Failed to launch app at {request.repo_path}: {e}")
        return {"success": False, "error": str(e)}


# MCP tools are registered in stdio_main.py for stdio mode from tools.utility_tools


# For DXT compatibility and dual mode support
if __name__ == "__main__":
    # When run as a module (python -m handbrake_mcp.main), always run in stdio mode for MCP clients
    # Claude Desktop expects stdio mode, not FastAPI HTTP mode
    from handbrake_mcp.stdio_main import main

    main()
