"""PyInstaller entry point — dual transport for HandBrake MCP."""
import os
import sys

sys.path.insert(0, "src")

# Overwrite sys.argv to prevent PyInstaller's frozen args from breaking argparse
port = os.environ.get("MCP_PORT") or os.environ.get("PORT")
if port:
    host = os.environ.get("MCP_HOST", "127.0.0.1")
    sys.argv = ["run_server.py", "--http", "--host", host, "--port", str(port)]
else:
    sys.argv = ["run_server.py", "--stdio"]

from handbrake_mcp.server import run
run()
