#!/usr/bin/env python3
"""Simple test script to verify the MCP server starts in stdio mode."""

import subprocess
import sys
import time

def test_stdio_server():
    """Test if the MCP server starts in stdio mode without Unicode errors."""

    print("Testing HandBrake MCP server stdio startup...")

    # Start the server process
    try:
        cmd = [sys.executable, "-m", "handbrake_mcp.main"]
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )

        # Send initialize message
        init_msg = '{"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}},"jsonrpc":"2.0","id":0}\n'

        process.stdin.write(init_msg)
        process.stdin.flush()

        # Wait a bit for response
        time.sleep(2)

        # Read any output
        if process.poll() is None:  # Process is still running
            print("✅ Server started successfully (no immediate crash)")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            return True
        else:
            # Process exited
            stdout, stderr = process.communicate()
            print("❌ Server crashed immediately")
            print("STDOUT:", stdout)
            print("STDERR:", stderr)
            return False

    except Exception as e:
        print(f"❌ Error testing server: {e}")
        return False

if __name__ == "__main__":
    success = test_stdio_server()
    sys.exit(0 if success else 1)
