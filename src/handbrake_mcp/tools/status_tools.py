"""Status and system monitoring tools for HandBrake MCP server.

This module contains system status and monitoring tools:
- get_system_status: Comprehensive system status with tools, configuration, and resources
"""

from handbrake_mcp.core.config import settings
from .help_tools import get_tool_categories
from .utility_tools import get_all_tool_documentation

# Import MCP instance for decorator registration
# This will be set by the registration system
_mcp_instance = None

def set_mcp_instance(mcp_instance):
    """Set the MCP instance for decorator-based tool registration."""
    global _mcp_instance
    _mcp_instance = mcp_instance

def _get_mcp_instance():
    """Get the MCP instance, raising an error if not set."""
    if _mcp_instance is None:
        raise RuntimeError("MCP instance not set. Call set_mcp_instance() first.")
    return _mcp_instance

# Store tools to be registered later
_pending_tools = []

def tool(*args, **kwargs):
    """Decorator to register a tool with the MCP instance."""
    def decorator(func):
        # Store the tool info for later registration
        _pending_tools.append((func, args, kwargs))
        return func
    return decorator

def register_pending_tools():
    """Register all pending tools with the MCP instance."""
    mcp = _get_mcp_instance()
    for func, args, kwargs in _pending_tools:
        # Apply the MCP tool decorator
        decorated_func = mcp.tool(*args, **kwargs)(func)
        # Replace the original function with the decorated one
        globals()[func.__name__] = decorated_func


@tool(
    name="system_status",
    description="Get comprehensive system status including tools, configuration, and resources",
    tags={"status", "system", "monitoring", "health"}
)
def get_system_status() -> str:
    """
    Get comprehensive system status including tools, configuration, and resources.

    This function provides a complete overview of the HandBrake MCP server's current
    state, including registered tools, system configuration, resource utilization,
    and operational status. Essential for monitoring, diagnostics, and system administration.

    Parameters:
        None: This function performs comprehensive system analysis automatically

    Returns:
        Formatted status string containing multiple sections:
            - Server information (status, version, platform)
            - Tool inventory (count and basic descriptions)
            - Category breakdown (tool organization)
            - Configuration settings (presets, limits, logging)
            - Resource utilization (CPU, memory, disk)
            - Quick help commands (for user guidance)

    Usage:
        Use this function for system monitoring, diagnostics, and status reporting.
        Provides a comprehensive snapshot of the server's operational state.

        Common scenarios:
        - System health monitoring and alerting
        - Capacity planning and resource assessment
        - Integration testing and validation
        - Troubleshooting and diagnostics
        - User support and system documentation

    Examples:
        Basic system status check:
            status = get_system_status()
            print(status)
            # Returns: Comprehensive formatted status report

        Status parsing for monitoring:
            status_text = get_system_status()
            # Parse for specific metrics
            if "[RUNNING]" in status_text:
                print("System is operational")
            if "TOOLS:" in status_text:
                # Extract tool count
                pass

        Automated health monitoring:
            import time
            while True:
                status = get_system_status()
                if "error" in status.lower():
                    alert_admin("System error detected")
                time.sleep(300)  # Check every 5 minutes

        Resource monitoring:
            status = get_system_status()
            lines = status.split('\n')
            for line in lines:
                if 'CPU Usage:' in line:
                    cpu_usage = line.split(':')[1].strip()
                    print(f"Current CPU usage: {cpu_usage}")
                elif 'Memory Usage:' in line:
                    mem_usage = line.split(':')[1].strip()
                    print(f"Current memory usage: {mem_usage}")

    Raises:
        RuntimeError: If system components are unavailable
        ImportError: If required monitoring libraries are missing

    Notes:
        - Status information is gathered in real-time
        - Resource metrics use system monitoring libraries
        - Tool information reflects current registration state
        - Configuration shows active settings from config system
        - Function is safe to call frequently for monitoring
        - Results include both static and dynamic information

    See Also:
        - get_provider_status: For detailed system health information
        - get_multilevel_help: For comprehensive tool documentation
        - get_tool_categories: For programmatic category access
        - get_advanced_help: For troubleshooting and performance guidance
    """
    lines = []
    lines.append("  HANDBRAKE MCP SERVER STATUS")
    lines.append("=" * 50)

    # Server information
    lines.append("\n[INFO] SERVER INFO:")
    lines.append("  - Status: [RUNNING] Running")
    lines.append(f"  - Version: {__import__('sys').version}")
    lines.append(f"  - Platform: {__import__('platform').platform()}")
    lines.append("")

    # Tool information
    docs = get_all_tool_documentation()
    lines.append(f"[TOOLS]  TOOLS: {len(docs)} registered")
    for tool_name, doc in docs.items():
        lines.append(f"  - {tool_name}: {doc.get_basic_description()}")
    lines.append("")

    # Categories
    categories = get_tool_categories()
    lines.append(f"📂 CATEGORIES: {len(categories)}")
    for category, tools in categories.items():
        lines.append(f"  - {category}: {len(tools)} tools")
    lines.append("")

    # Configuration
    lines.append("[CONFIG]  CONFIGURATION:")
    lines.append(f"  - Default Preset: {settings.default_preset}")
    lines.append(f"  - Log Level: {settings.log_level}")
    lines.append(f"  - Max Concurrent Jobs: {getattr(settings, 'max_concurrent_jobs', 'Unknown')}")
    lines.append("")

    # Resources
    lines.append("💾 RESOURCES:")
    import psutil
    lines.append(f"  - CPU Usage: {psutil.cpu_percent()}%")
    lines.append(f"  - Memory Usage: {psutil.virtual_memory().percent}%")
    lines.append(f"  - Disk Usage: {psutil.disk_usage('/').percent}%")
    lines.append("")

    # Quick help
    lines.append("[TIP] QUICK HELP:")
    lines.append("  - help - Get tool-specific help")
    lines.append("  - get_multilevel_help('detailed') - Detailed help")
    lines.append("  - get_advanced_help('examples') - Usage examples")
    lines.append("  - get_provider_status() - System status")

    return "\n".join(lines)
