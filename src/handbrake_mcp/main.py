"""Main FastMCP application for HandBrake MCP server."""

import logging
import subprocess
import time
from contextlib import asynccontextmanager
from pathlib import Path

import psutil
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from handbrake_mcp.core.config import settings
from handbrake_mcp.services.notification_service import notification_service
from handbrake_mcp.services.processing_service import processing_service
from handbrake_mcp.services.watch_service import watch_service
from handbrake_mcp.stdio_main import mcp

# Configure logging
logging.basicConfig(
    level=settings.log_level.upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# NOTE: legacy/alternate HTTP entry (Docker + old docs point here).
# The canonical live server is handbrake_mcp.server:app.
@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    """Startup/shutdown: init services on entry, stop them on exit."""
    logger.info("Starting HandBrake MCP server (main.py legacy entry)...")
    await notification_service.initialize()
    if settings.watch_folders:
        logger.info(f"Watching folders: {', '.join(str(f) for f in settings.watch_folders)}")
        await watch_service.start(
            callback=process_new_file,
            watch_dirs=settings.watch_folders,
        )
    logger.info("HandBrake MCP server started successfully")
    yield
    logger.info("Shutting down HandBrake MCP server (main.py legacy entry)...")
    if watch_service.is_running():
        await watch_service.stop()
    await notification_service.shutdown()
    logger.info("HandBrake MCP server has been shut down")


# Initialize FastAPI app
app = FastAPI(
    title="HandBrake MCP Server",
    description="FastMCP 3.4 compliant server for video transcoding with HandBrake (legacy entry; canonical: handbrake_mcp.server:app)",
    version="1.1.1",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add CORS middleware (no wildcard: explicit origins + LAN/Tauri regex)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:10874",
        "http://localhost:10874",
        "http://goliath:10874",
        "http://tauri.localhost",
        "https://tauri.localhost",
        "tauri://localhost",
    ],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|goliath|tauri\.localhost)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# FastMCP instance for stdio mode is in stdio_main.py

# MCP tools are not used in the main FastAPI server

# Include API routers
# from handbrake_mcp.api.v1.endpoints import router as api_router
# app.include_router(api_router, prefix="/api/v1")

# Mount MCP app for HTTP access (FastMCP 3.x: http_app, not the removed .app)
app.mount("/mcp", mcp.http_app(path="/"))


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
