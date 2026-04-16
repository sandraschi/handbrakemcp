"""
HandBrake MCP Server

Standardized FastMCP 3.1.0+ compliant server for video transcoding.
Provides dual-mode support (stdio/HTTP) and modular tool registration.
"""

import subprocess
import argparse
import logging
import sys
import psutil
from contextlib import asynccontextmanager

from fastmcp import FastMCP, Context
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import tools for registration
import handbrake_mcp.tools.handbrake_tools
import handbrake_mcp.tools.help_tools
import handbrake_mcp.tools.status_tools
import handbrake_mcp.tools.agentic_workflow
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
mcp = FastMCP(
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

# Initialize FastAPI for custom routes and dashboard support
# Standard FastAPI pattern with CORS support
app = FastAPI(
    title="HandBrake MCP SOTA Bridge",
    description="Universal media ingestion engine with Agentic Workflows",
    version="1.0.0"
)

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mandatory SOTA 3.2: FastAPI Mounting Pattern
# This enables the MCP protocol at /mcp while keeping /api for custom routes
# Register via portmanteau pattern managers
handbrake_mcp.tools.handbrake_tools.set_mcp_instance(mcp)
handbrake_mcp.tools.help_tools.set_mcp_instance(mcp)
handbrake_mcp.tools.status_tools.set_mcp_instance(mcp)
handbrake_mcp.tools.agentic_workflow.set_mcp_instance(mcp)

handbrake_mcp.tools.handbrake_tools.register_pending_tools()
handbrake_mcp.tools.help_tools.register_pending_tools()
handbrake_mcp.tools.status_tools.register_pending_tools()

# =============================================================================
# SOTA 3.2 FEATURES: SAMPLING & PROMPTS
# =============================================================================

@mcp.prompt()
def advanced_transcoding_guide():
    """Returns a SOTA guide for hardware-accelerated transcoding constants."""
    return """
# HandBrake Transcoding Gold Standard (2026)

1. **NVENC (RTX 4090)**: Use `AV1 NVENC` for the best speed/quality ratio.
   - Recommended CRF-equivalent: 24-28 (Constant Quality).
   - Speed Preset: P4 or P5.
2. **Audio**: Use `Opus` at 128k for stereo, `E-AC3` for surround.
3. **Containers**: Always use `MKV` for preservation, `MP4` for web compatibility.
"""

# =============================================================================
# MANDATORY CAPABILITY INTROSPECTION (SOTA 2026)
# =============================================================================

@app.get("/api/capabilities")
async def get_capabilities():
    """Runtime source of truth for HandBrake MCP capabilities."""
    from datetime import datetime
    
    # Introspect registered tools
    # FastMCP 3.2+ uses async methods for listing
    tools = await mcp.list_tools()
    prompts = await mcp.list_prompts()
    
    return {
        "status": "ok",
        "server": { 
            "name": "handbrake-mcp", 
            "version": "1.0.0", 
            "fastmcp": "3.2.0" 
        },
        "tool_surface": {
            "total": len(tools),
            "portmanteau_count": 3,
            "atomic_count": 0,
            "portmanteau_tools": ["handbrake_ops", "status_ops", "help_ops"],
            "atomic_tools": []
        },
        "features": {
            "sampling": True,
            "agentic_workflows": True,
            "prompts": True,
            "resources": False,
            "skills": True
        },
        "inventory": {
            "workflow_tools": ["handbrake_agentic_workflow"],
            "prompt_names": [p.name for p in prompts],
            "resource_uris": [],
            "skill_uris": ["skill://handbrake-expert/SKILL.md"]
        },
        "runtime": {
            "transport": "dual",
            "surface_mode": "portmanteau"
        },
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

# =============================================================================
# CUSTOM HTTP ROUTES (FastAPI)
# =============================================================================

@app.get("/health")
async def health():
    """System health endpoint for the SOTA dashboard."""
    cpu_percent = psutil.cpu_percent()
    memory = psutil.virtual_memory()

    # Attempt to get GPU temp via nvidia-smi
    gpu_temp = "N/A"
    gpu_util = "N/A"
    gpu_model = "Not Detected"
    
    try:
        # Run nvidia-smi to get temp and utilization
        # Using -L first to check if GPU exists to avoid errors on non-NVIDIA systems
        res_list = subprocess.run(["nvidia-smi", "-L"], capture_output=True, text=True, check=False)
        if res_list.returncode == 0:
            gpu_model = res_list.stdout.strip().split("\n")[0]
            
            res = subprocess.run(
                ["nvidia-smi", "--query-gpu=temperature.gpu,utilization.gpu", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                check=False
            )
            if res.returncode == 0:
                parts = res.stdout.strip().split(",")
                if len(parts) >= 2:
                    gpu_temp = parts[0].strip()
                    gpu_util = parts[1].strip()
    except Exception:
        pass

    return {
        "status": "ok",
        "version": "1.0.0",
        "system": {
            "cpu_percent": cpu_percent,
            "memory": {
                "percent": memory.percent,
                "available_gb": round(memory.available / (1024**3), 2)
            },
            "gpu": {
                "temp_c": gpu_temp,
                "utilization_percent": gpu_util,
                "model": gpu_model
            }
        }
    }

# =============================================================================
# INDUSTRIAL CONTROL API (SOTA 2026)
# =============================================================================

@app.get("/api/tools")
async def list_tools():
    """Industrial tool discovery for the dashboard (Fixes 404/500)."""
    tools = await mcp.list_tools()
    tool_list = []
    for t in tools:
        try:
            mcp_tool = t.to_mcp_tool()
            tool_list.append({
                "name": mcp_tool.name,
                "description": mcp_tool.description,
                "inputSchema": mcp_tool.inputSchema
            })
        except Exception as e:
            logger.error(f"Failed to map tool {t.name}: {e}")
            
    return {
        "status": "ok",
        "tools": tool_list
    }

@app.get("/api/presets")
async def get_presets():
    """Fetch live HandBrake presets from the system CLI."""
    try:
        from handbrake_mcp.services.handbrake import get_handbrake_service
        hb = get_handbrake_service()
        presets = await hb.get_presets()
        return {"status": "ok", "presets": presets}
    except Exception as e:
        logger.error(f"Failed to fetch presets: {e}")
        return {"status": "error", "message": str(e), "presets": ["Fast 1080p30", "HQ 1080p30 Surround"]}

@app.get("/api/jobs")
async def list_jobs():
    """Return the status of all current transcoding jobs."""
    try:
        from handbrake_mcp.services.handbrake import get_handbrake_service
        hb = get_handbrake_service()
        job_list = []
        for job_id, job in hb.jobs.items():
            job_list.append({
                "job_id": job.job_id,
                "input": str(job.input_path),
                "output": str(job.output_path),
                "preset": job.preset,
                "status": job.status,
                "progress": job.progress,
                "error": job.error
            })
        return {"status": "ok", "jobs": job_list}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/transcode")
async def start_transcode(data: dict):
    """Trigger a transcoding job directly from the dashboard."""
    try:
        from handbrake_mcp.services.handbrake import get_handbrake_service
        hb = get_handbrake_service()
        
        input_path = data.get("input")
        output_path = data.get("output")
        preset = data.get("preset", settings.default_preset)
        
        if not input_path:
            return {"status": "error", "message": "Input path is required"}
            
        # Default output path if not provided
        if not output_path:
            p = Path(input_path)
            output_path = str(p.with_suffix(".mkv"))
            
        job_id = await hb.transcode(input_path, output_path, preset)
        return {"status": "ok", "job_id": job_id, "message": "Job queued successfully"}
    except Exception as e:
        logger.error(f"Transcode trigger failed: {e}")
        return {"status": "error", "message": str(e)}

# Mount the MCP app to the FastAPI instance
# FastMCP 3.2 provides http_app() for this purpose
# This returns a Starlette app that we mount as a sub-app
mcp_app = mcp.http_app()
app.mount("/mcp", mcp_app)

def run():
    """SOTA-compliant entry point with CLI argument support."""
    import uvicorn
    parser = argparse.ArgumentParser(description="HandBrake MCP Server")
    parser.add_argument("--http", action="store_true", help="Run in HTTP mode")
    parser.add_argument("--port", type=int, default=10875, help="Port for HTTP mode")
    parser.add_argument("--log-level", type=str, default="info", help="Log level")
    args, unknown = parser.parse_known_args()

    if args.http:
        logger.info(f"Starting HandBrake MCP Bridge on http://0.0.0.0:{args.port}")
        logger.info(f"MCP Endpoint: http://0.0.0.0:{args.port}/mcp")
        logger.info(f"Health Endpoint: http://0.0.0.0:{args.port}/health")
        logger.info(f"Capabilities Endpoint: http://0.0.0.0:{args.port}/api/capabilities")
        uvicorn.run(app, host="0.0.0.0", port=args.port, log_level=args.log_level.lower())
    else:
        logger.info("Starting HandBrake MCP on stdio transport")
        mcp.run(transport="stdio")


if __name__ == "__main__":
    run()

