"""Test script for HandBrake MCP server."""
import asyncio
import sys
from pathlib import Path

import httpx

# Add the parent directory to the path so we can import handbrake_mcp
sys.path.insert(0, str(Path(__file__).parent))

from handbrake_mcp.core.config import settings


async def test_server():
    """Test the HandBrake MCP server."""
    base_url = f"http://{settings.host}:{settings.port}"
    
    async with httpx.AsyncClient() as client:
        # Test health check
        print("Testing health check...")
        response = await client.get(f"{base_url}/health")
        response.raise_for_status()
        print(f"Health check: {response.json()}")
        
        # Test getting presets
        print("\nTesting get presets...")
        try:
            response = await client.get(f"{base_url}/mcp/tools/get_presets")
            response.raise_for_status()
            print(f"Available presets: {response.json()}")
        except Exception as e:
            print(f"Error getting presets: {e}")
        
        # Test getting provider status
        print("\nTesting get provider status...")
        try:
            response = await client.get(f"{base_url}/mcp/tools/get_provider_status")
            response.raise_for_status()
            print(f"Provider status: {response.json()}")
        except Exception as e:
            print(f"Error getting provider status: {e}")


if __name__ == "__main__":
    print("Testing HandBrake MCP server...")
    asyncio.run(test_server())
