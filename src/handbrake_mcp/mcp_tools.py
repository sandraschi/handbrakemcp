"""MCP tools for HandBrake MCP server."""
import logging
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any, Type
from functools import wraps
from inspect import signature, Parameter
from dataclasses import dataclass

from pydantic import BaseModel, Field

from handbrake_mcp.services.handbrake import get_handbrake_service, TranscodeJob
from handbrake_mcp.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class ToolDocumentation:
    """Container for comprehensive tool documentation."""

    name: str
    description: str
    summary: str
    parameters: Dict[str, Dict[str, Any]]
    examples: List[Dict[str, Any]]
    returns: Dict[str, Any]
    notes: List[str]
    warnings: List[str]
    related_tools: List[str]
    categories: List[str]
    version: str = "1.0.0"

    def get_multiline_description(self) -> str:
        """Get the full multiline description."""
        lines = []
        lines.append(f"🎯 {self.name.upper()}")
        lines.append("")
        lines.append(self.description)
        lines.append("")

        if self.summary:
            lines.append(f"📋 SUMMARY: {self.summary}")
            lines.append("")

        if self.parameters:
            lines.append("📝 PARAMETERS:")
            for param_name, param_info in self.parameters.items():
                lines.append(f"  • {param_name}: {param_info.get('description', 'No description')}")
                if 'type' in param_info:
                    lines.append(f"    Type: {param_info['type']}")
                if 'default' in param_info:
                    lines.append(f"    Default: {param_info['default']}")
                if 'required' in param_info:
                    lines.append(f"    Required: {param_info['required']}")
                lines.append("")
            lines.append("")

        if self.examples:
            lines.append("💡 EXAMPLES:")
            for i, example in enumerate(self.examples, 1):
                lines.append(f"  {i}. {example.get('description', 'Example')}")
                if 'code' in example:
                    lines.append(f"     {example['code']}")
                lines.append("")
            lines.append("")

        if self.returns:
            lines.append("🔄 RETURNS:")
            lines.append(f"  {self.returns.get('description', 'No return description')}")
            if 'type' in self.returns:
                lines.append(f"  Type: {self.returns['type']}")
            lines.append("")

        if self.notes:
            lines.append("📌 NOTES:")
            for note in self.notes:
                lines.append(f"  • {note}")
            lines.append("")

        if self.warnings:
            lines.append("⚠️  WARNINGS:")
            for warning in self.warnings:
                lines.append(f"  • {warning}")
            lines.append("")

        if self.related_tools:
            lines.append("🔗 RELATED TOOLS:")
            for tool in self.related_tools:
                lines.append(f"  • {tool}")
            lines.append("")

        lines.append(f"📦 Version: {self.version}")
        return "\n".join(lines)

    def get_basic_description(self) -> str:
        """Get a basic single-line description."""
        return self.summary or self.description.split('.')[0] + '.'

    def get_detailed_description(self) -> str:
        """Get a detailed but concise description."""
        return f"{self.description} (Version: {self.version})"


def tool_documentation(
    name: str,
    description: str = "",
    summary: str = "",
    parameters: Optional[Dict[str, Dict[str, Any]]] = None,
    examples: Optional[List[Dict[str, Any]]] = None,
    returns: Optional[Dict[str, Any]] = None,
    notes: Optional[List[str]] = None,
    warnings: Optional[List[str]] = None,
    related_tools: Optional[List[str]] = None,
    categories: Optional[List[str]] = None,
    version: str = "1.0.0"
):
    """
    Decorator for comprehensive tool documentation.

    Args:
        name: Tool name
        description: Full multiline description
        summary: Brief summary (single line)
        parameters: Parameter documentation
        examples: Usage examples
        returns: Return value documentation
        notes: Additional notes
        warnings: Important warnings
        related_tools: Related tool names
        categories: Tool categories
        version: Tool version

    Returns:
        Decorated function with comprehensive documentation
    """
    def decorator(func: Callable) -> Callable:
        # Create documentation object
        doc = ToolDocumentation(
            name=name,
            description=description,
            summary=summary,
            parameters=parameters or {},
            examples=examples or [],
            returns=returns or {},
            notes=notes or [],
            warnings=warnings or [],
            related_tools=related_tools or [],
            categories=categories or [],
            version=version
        )

        # Store documentation on the function
        func._tool_documentation = doc

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper
    return decorator


def get_all_tool_documentation() -> Dict[str, ToolDocumentation]:
    """Get documentation for all registered tools."""
    # This will be populated when tools are registered
    return getattr(get_all_tool_documentation, '_docs', {})


def get_tool_help(tool_name: str, level: str = "basic") -> str:
    """
    Get help for a specific tool at different detail levels.

    Args:
        tool_name: Name of the tool
        level: Detail level ("basic", "detailed", "full")

    Returns:
        Formatted help text
    """
    docs = get_all_tool_documentation()

    if tool_name not in docs:
        return f"❌ Tool '{tool_name}' not found. Available tools: {', '.join(docs.keys())}"

    doc = docs[tool_name]

    if level == "basic":
        return f"📋 {doc.name}: {doc.get_basic_description()}"
    elif level == "detailed":
        return f"🔍 {doc.name.upper()}\n\n{doc.get_detailed_description()}\n\n📝 Parameters: {len(doc.parameters)} | 💡 Examples: {len(doc.examples)}"
    elif level == "full":
        return doc.get_multiline_description()
    else:
        return f"❌ Invalid help level '{level}'. Use: basic, detailed, or full"


def get_system_status() -> str:
    """Get comprehensive system status."""
    lines = []
    lines.append("🖥️  HANDBRAKE MCP SERVER STATUS")
    lines.append("=" * 50)

    # Server information
    lines.append("\n📊 SERVER INFO:")
    lines.append("  • Status: 🟢 Running")
    lines.append(f"  • Version: {settings.__version__ if hasattr(settings, '__version__') else 'Unknown'}")
    lines.append(f"  • Python: {__import__('sys').version}")
    lines.append(f"  • Platform: {__import__('platform').platform()}")
    lines.append("")

    # Tool information
    docs = get_all_tool_documentation()
    lines.append(f"🛠️  TOOLS: {len(docs)} registered")
    for tool_name, doc in docs.items():
        lines.append(f"  • {tool_name}: {doc.get_basic_description()}")
    lines.append("")

    # Configuration
    lines.append("⚙️  CONFIGURATION:")
    lines.append(f"  • Default Preset: {settings.default_preset}")
    lines.append(f"  • Log Level: {settings.log_level}")
    lines.append(f"  • Max Concurrent Jobs: {getattr(settings, 'max_concurrent_jobs', 'Unknown')}")
    lines.append("")

    # Resources
    lines.append("💾 RESOURCES:")
    import psutil
    lines.append(f"  • CPU Usage: {psutil.cpu_percent()}%")
    lines.append(f"  • Memory Usage: {psutil.virtual_memory().percent}%")
    lines.append(f"  • Disk Usage: {psutil.disk_usage('/').percent}%")
    lines.append("")

    return "\n".join(lines)


def get_tool_categories() -> Dict[str, List[str]]:
    """Get all tools organized by category."""
    docs = get_all_tool_documentation()

    categories = {}
    for tool_name, doc in docs.items():
        for category in doc.categories:
            if category not in categories:
                categories[category] = []
            categories[category].append(tool_name)

    return categories


def get_tools_by_category(category: str) -> List[str]:
    """Get all tools in a specific category."""
    docs = get_all_tool_documentation()
    return [name for name, doc in docs.items() if category in doc.categories]


def search_tools(query: str) -> List[str]:
    """Search tools by name, description, or category."""
    docs = get_all_tool_documentation()
    query_lower = query.lower()

    results = []
    for tool_name, doc in docs.items():
        if (query_lower in tool_name.lower() or
            query_lower in doc.summary.lower() or
            query_lower in doc.description.lower() or
            any(query_lower in category.lower() for category in doc.categories)):
            results.append(tool_name)

    return results


def get_multilevel_help(level: str = "basic", filter_by: Optional[str] = None) -> str:
    """
    Get comprehensive help at different detail levels.

    Args:
        level: Help detail level ("basic", "detailed", "full", "categories")
        filter_by: Optional category filter

    Returns:
        Formatted help text
    """
    docs = get_all_tool_documentation()

    if level == "basic":
        lines = ["🛠️  HANDBRAKE MCP TOOLS - BASIC HELP"]
        lines.append("=" * 50)

        lines.append(f"\n📊 OVERVIEW: {len(docs)} tools available")
        lines.append("")

        lines.append("🎯 AVAILABLE TOOLS:")
        for tool_name, doc in docs.items():
            lines.append(f"  • {tool_name}: {doc.get_basic_description()}")

        lines.append("")
        lines.append("💡 QUICK COMMANDS:")
        lines.append("  • help - Get comprehensive help for tools")
        lines.append("  • system_status - Get comprehensive system status")
        lines.append("  • get_presets - List all available HandBrake presets")
        lines.append("  • transcode_video - Transcode a single video file")
        lines.append("")
        lines.append("🔍 For detailed help on any tool, use: help('tool_name', 'detailed')")

    elif level == "detailed":
        lines = ["🔍 HANDBRAKE MCP TOOLS - DETAILED HELP"]
        lines.append("=" * 50)

        # Group by category
        categories = get_tool_categories()

        for category, tools in categories.items():
            if filter_by and filter_by.lower() not in category.lower():
                continue

            lines.append(f"\n📂 {category.upper()}:")
            for tool_name in tools:
                doc = docs[tool_name]
                lines.append(f"  • {tool_name}: {doc.get_detailed_description()}")
                lines.append(f"    Parameters: {len(doc.parameters)} | Examples: {len(doc.examples)}")

        lines.append("")
        lines.append("📚 LEGEND:")
        lines.append("  🟢 Ready for use")
        lines.append("  🟡 Requires configuration")
        lines.append("  🔴 May require additional setup")

    elif level == "full":
        if filter_by:
            # Show full help for specific tool
            if filter_by in docs:
                return docs[filter_by].get_multiline_description()
            else:
                return f"❌ Tool '{filter_by}' not found. Use 'help' to see available tools."
        else:
            # Show full help for all tools
            lines = ["📚 HANDBRAKE MCP TOOLS - COMPLETE DOCUMENTATION"]
            lines.append("=" * 60)

            for i, (tool_name, doc) in enumerate(docs.items(), 1):
                lines.append(f"\n{i}. {doc.get_multiline_description()}")
                if i < len(docs):
                    lines.append("\n" + "-" * 60)

    elif level == "categories":
        lines = ["📂 HANDBRAKE MCP TOOLS - CATEGORIES"]
        lines.append("=" * 50)

        categories = get_tool_categories()

        lines.append(f"\n📊 CATEGORY OVERVIEW: {len(categories)} categories")
        lines.append("")

        for category, tools in categories.items():
            lines.append(f"📁 {category.upper()} ({len(tools)} tools):")
            for tool_name in tools:
                doc = docs[tool_name]
                lines.append(f"  • {tool_name}: {doc.get_basic_description()}")
            lines.append("")

    else:
        return f"❌ Invalid help level '{level}'. Available levels: basic, detailed, full, categories"

    return "\n".join(lines)


def get_advanced_help(tool_name: Optional[str] = None, help_type: str = "overview") -> str:
    """
    Get advanced help information for tools and system.

    Args:
        tool_name: Specific tool name (optional)
        help_type: Type of advanced help ("overview", "examples", "troubleshooting", "performance")

    Returns:
        Advanced help text
    """
    docs = get_all_tool_documentation()

    if help_type == "overview":
        lines = ["🚀 HANDBRAKE MCP - ADVANCED OVERVIEW"]
        lines.append("=" * 50)

        lines.append(f"\n📊 SYSTEM CAPABILITIES: {len(docs)} specialized tools")
        lines.append("")

        lines.append("🎯 CORE WORKFLOW:")
        lines.append("  1. transcode_video - Single file processing")
        lines.append("  2. batch_transcode - Multiple file processing")
        lines.append("  3. get_job_status - Progress monitoring")
        lines.append("  4. cancel_job - Job management")
        lines.append("  5. get_presets - Configuration discovery")
        lines.append("")

        lines.append("🔧 ADVANCED FEATURES:")
        lines.append("  • Real-time progress tracking")
        lines.append("  • Hardware acceleration support")
        lines.append("  • Batch processing optimization")
        lines.append("  • Error handling and recovery")
        lines.append("  • Resource management")
        lines.append("")

    elif help_type == "examples":
        lines = ["💡 HANDBRAKE MCP - USAGE EXAMPLES"]
        lines.append("=" * 50)

        lines.append("\n📝 BASIC USAGE:")
        lines.append("  # Single video transcoding")
        lines.append("  transcode_video('/input.mp4', '/output.mkv')")
        lines.append("")

        lines.append("  # Batch processing")
        lines.append("  batch_transcode([{'input_path': 'file1.mp4', 'output_path': 'file1.mkv'}])")
        lines.append("")

        lines.append("  # With custom presets")
        lines.append("  transcode_video('/input.mp4', '/output.mp4', preset='HQ 1080p30')")
        lines.append("")

        lines.append("📊 MONITORING:")
        lines.append("  # Check job status")
        lines.append("  get_job_status('job_12345')")
        lines.append("")

        lines.append("  # Get system status")
        lines.append("  get_provider_status()")
        lines.append("")

        lines.append("⚙️  CONFIGURATION:")
        lines.append("  # Discover available presets")
        lines.append("  presets = get_presets()")
        lines.append("")

        lines.append("  # Check system capabilities")
        lines.append("  status = get_provider_status()")
        lines.append("  print(f'Available presets: {len(status[\"supported_presets\"])}')")

    elif help_type == "troubleshooting":
        lines = ["🔧 HANDBRAKE MCP - TROUBLESHOOTING GUIDE"]
        lines.append("=" * 50)

        lines.append("\n❌ COMMON ISSUES:")
        lines.append("")

        lines.append("🔍 'HandBrake CLI not found':")
        lines.append("  • Install HandBrake CLI or set HBB_PATH")
        lines.append("  • Verify installation with 'HandBrakeCLI --version'")
        lines.append("  • Check system PATH environment variable")
        lines.append("")

        lines.append("📁 'File not found':")
        lines.append("  • Verify input file path exists")
        lines.append("  • Check file permissions")
        lines.append("  • Use absolute paths when possible")
        lines.append("")

        lines.append("⚙️  'Invalid preset':")
        lines.append("  • Use get_presets() to see available options")
        lines.append("  • Check HandBrake CLI version compatibility")
        lines.append("  • Verify preset name spelling")
        lines.append("")

        lines.append("🛑 'Job failed':")
        lines.append("  • Check error message in job status")
        lines.append("  • Verify output directory exists and is writable")
        lines.append("  • Check available disk space")
        lines.append("  • Review system resource usage")
        lines.append("")

        lines.append("🔍 DIAGNOSTIC STEPS:")
        lines.append("  1. Run get_provider_status() to check system health")
        lines.append("  2. Use get_presets() to verify available options")
        lines.append("  3. Check job status with get_job_status()")
        lines.append("  4. Review system logs for error details")
        lines.append("  5. Test with simple files first")

    elif help_type == "performance":
        lines = ["⚡ HANDBRAKE MCP - PERFORMANCE OPTIMIZATION"]
        lines.append("=" * 50)

        lines.append("\n🎯 OPTIMIZATION STRATEGIES:")
        lines.append("")

        lines.append("💾 RESOURCE MANAGEMENT:")
        lines.append("  • Use appropriate presets for your use case")
        lines.append("  • Monitor system resources during processing")
        lines.append("  • Adjust max_concurrent_jobs based on system capacity")
        lines.append("  • Use hardware acceleration when available")
        lines.append("")

        lines.append("📦 BATCH PROCESSING:")
        lines.append("  • Process similar files together for efficiency")
        lines.append("  • Use consistent presets within batches")
        lines.append("  • Monitor memory usage with large batches")
        lines.append("  • Consider disk I/O limitations")
        lines.append("")

        lines.append("🔧 SYSTEM TUNING:")
        lines.append("  • Ensure adequate RAM for video processing")
        lines.append("  • Use SSD storage for temporary files")
        lines.append("  • Monitor CPU and GPU utilization")
        lines.append("  • Consider network storage limitations")
        lines.append("")

        lines.append("📊 MONITORING TOOLS:")
        lines.append("  • get_provider_status() - System health")
        lines.append("  • get_job_status() - Individual job progress")
        lines.append("  • Use detailed help for tool-specific guidance")

    else:
        return f"❌ Invalid help type '{help_type}'. Available types: overview, examples, troubleshooting, performance"

    return "\n".join(lines)


def get_system_status() -> str:
    """Get comprehensive system status."""
    lines = []
    lines.append("🖥️  HANDBRAKE MCP SERVER STATUS")
    lines.append("=" * 50)

    # Server information
    lines.append("\n📊 SERVER INFO:")
    lines.append("  • Status: 🟢 Running")
    lines.append(f"  • Version: {__import__('sys').version}")
    lines.append(f"  • Platform: {__import__('platform').platform()}")
    lines.append("")

    # Tool information
    docs = get_all_tool_documentation()
    lines.append(f"🛠️  TOOLS: {len(docs)} registered")
    for tool_name, doc in docs.items():
        lines.append(f"  • {tool_name}: {doc.get_basic_description()}")
    lines.append("")

    # Categories
    categories = get_tool_categories()
    lines.append(f"📂 CATEGORIES: {len(categories)}")
    for category, tools in categories.items():
        lines.append(f"  • {category}: {len(tools)} tools")
    lines.append("")

    # Configuration
    lines.append("⚙️  CONFIGURATION:")
    lines.append(f"  • Default Preset: {settings.default_preset}")
    lines.append(f"  • Log Level: {settings.log_level}")
    lines.append(f"  • Max Concurrent Jobs: {getattr(settings, 'max_concurrent_jobs', 'Unknown')}")
    lines.append("")

    # Resources
    lines.append("💾 RESOURCES:")
    import psutil
    lines.append(f"  • CPU Usage: {psutil.cpu_percent()}%")
    lines.append(f"  • Memory Usage: {psutil.virtual_memory().percent}%")
    lines.append(f"  • Disk Usage: {psutil.disk_usage('/').percent}%")
    lines.append("")

    # Quick help
    lines.append("💡 QUICK HELP:")
    lines.append("  • help - Get tool-specific help")
    lines.append("  • get_multilevel_help('detailed') - Detailed help")
    lines.append("  • get_advanced_help('examples') - Usage examples")
    lines.append("  • get_provider_status() - System status")

    return "\n".join(lines)


def register_tools_with_mcp(mcp_instance):
    """Register all tools with the FastMCP instance with comprehensive documentation."""

    # Import FastMCP tools
    from fastmcp.tools import Tool

    # Create documentation registry
    docs_registry = {}

    # Register comprehensive help and status tools
    help_tool = Tool.from_function(
        get_tool_help,
        name="help",
        description="Get comprehensive help for tools at different detail levels",
        tags={"help", "documentation", "information"}
    )
    mcp_instance.add_tool(help_tool)

    multilevel_help_tool = Tool.from_function(
        get_multilevel_help,
        name="multilevel_help",
        description="Get help at different levels: basic, detailed, full, categories",
        tags={"help", "documentation", "information", "categories"}
    )
    mcp_instance.add_tool(multilevel_help_tool)

    advanced_help_tool = Tool.from_function(
        get_advanced_help,
        name="advanced_help",
        description="Get advanced help: overview, examples, troubleshooting, performance",
        tags={"help", "documentation", "advanced", "troubleshooting"}
    )
    mcp_instance.add_tool(advanced_help_tool)

    categories_tool = Tool.from_function(
        get_tool_categories,
        name="tool_categories",
        description="Get all tools organized by category",
        tags={"help", "documentation", "categories", "organization"}
    )
    mcp_instance.add_tool(categories_tool)

    search_tool = Tool.from_function(
        search_tools,
        name="search_tools",
        description="Search tools by name, description, or category",
        tags={"help", "documentation", "search", "discovery"}
    )
    mcp_instance.add_tool(search_tool)

    status_tool = Tool.from_function(
        get_system_status,
        name="system_status",
        description="Get comprehensive system status including tools, configuration, and resources",
        tags={"status", "system", "monitoring", "health"}
    )
    mcp_instance.add_tool(status_tool)

    # Get all documented tools
    documented_tools = [
        transcode_video,
        batch_transcode,
        get_job_status,
        cancel_job,
        get_presets,
        get_loaded_models,
        get_provider_status
    ]

    # Create and register tool objects with comprehensive metadata
    tools = []
    for tool_func in documented_tools:
        if hasattr(tool_func, '_tool_documentation'):
            doc = tool_func._tool_documentation

            # Store in registry
            docs_registry[doc.name] = doc

            # Create FastMCP tool with enhanced metadata
            tool = Tool.from_function(
                tool_func,
                name=doc.name,
                description=doc.get_detailed_description(),
                tags=set(doc.categories)
            )
            tools.append(tool)

    # Add all tools to the MCP instance
    for tool in tools:
        mcp_instance.add_tool(tool)

    # Store documentation registry
    get_all_tool_documentation._docs = docs_registry

    print(f"✅ Registered {len(tools)} tools with comprehensive documentation")
    print(f"✅ Registered {len(docs_registry)} documented tools in registry")


class TranscodeRequest(BaseModel):
    """Request model for the transcode_video tool with FastMCP 2.12 compliant schema."""
    input_path: str = Field(
        ...,
        description="Absolute or relative path to the input video file. Supports common formats: MP4, MKV, AVI, MOV, M4V, etc.",
        min_length=1,
        max_length=1000,
        examples=["/videos/input.mp4", "C:\\videos\\input.mkv", "./movie.avi"]
    )
    output_path: str = Field(
        ...,
        description="Absolute or relative path where the transcoded file will be saved. Format determined by file extension.",
        min_length=1,
        max_length=1000,
        examples=["/videos/output.mkv", "C:\\videos\\output.mp4", "./encoded_video.webm"]
    )
    preset: Optional[str] = Field(
        settings.default_preset,
        description=f"HandBrake preset name for encoding. If not provided, uses '{settings.default_preset}'",
        min_length=1,
        max_length=100,
        examples=["Fast 1080p30", "HQ 1080p30", "Very Fast 1080p30", "Apple 1080p30 Surround"]
    )
    options: Optional[Dict[str, str]] = Field(
        default_factory=dict,
        description="Additional HandBrake CLI options as key-value pairs",
        examples=[{"quality": "20", "encoder": "x264", "audio": "copy"}]
    )


class TranscodeResponse(BaseModel):
    """Response model for the transcode_video tool with FastMCP 2.12 compliant schema."""
    job_id: str = Field(
        ...,
        description="Unique identifier for tracking the transcode job",
        min_length=1,
        max_length=100,
        examples=["job_12345", "batch_001_001", "transcode_2025_01_22_143022"]
    )
    status: str = Field(
        ...,
        description="Current status of the transcode job",
        pattern="^(queued|processing|completed|failed|cancelled)$",
        examples=["queued", "processing", "completed", "failed"]
    )
    input_path: str = Field(
        ...,
        description="Path to the input video file",
        min_length=1,
        max_length=1000,
        examples=["/videos/input.mp4", "C:\\videos\\input.mkv"]
    )
    output_path: str = Field(
        ...,
        description="Path where the output file will be saved",
        min_length=1,
        max_length=1000,
        examples=["/videos/output.mkv", "C:\\videos\\output.mp4"]
    )


class JobStatusResponse(BaseModel):
    """Response model for job status with FastMCP 2.12 compliant schema."""
    job_id: str = Field(
        ...,
        description="Unique identifier of the transcode job",
        min_length=1,
        max_length=100,
        examples=["job_12345", "batch_001_001"]
    )
    status: str = Field(
        ...,
        description="Current status of the transcode job",
        pattern="^(queued|processing|completed|failed|cancelled|not_found)$",
        examples=["queued", "processing", "completed", "failed"]
    )
    progress: float = Field(
        ...,
        description="Progress percentage of the transcode job",
        ge=0.0,
        le=100.0,
        examples=[0.0, 25.5, 50.0, 75.2, 100.0]
    )
    error: Optional[str] = Field(
        None,
        description="Error message if the job failed",
        examples=["HandBrake CLI not found", "Input file not found", "Encoding failed"]
    )
    input_path: str = Field(
        ...,
        description="Path to the input video file",
        min_length=1,
        max_length=1000,
        examples=["/videos/input.mp4", "C:\\videos\\input.mkv"]
    )
    output_path: str = Field(
        ...,
        description="Path where the output file will be saved",
        min_length=1,
        max_length=1000,
        examples=["/videos/output.mkv", "C:\\videos\\output.mp4"]
    )


@tool_documentation(
    name="transcode_video",
    description="""
    Transcode a video file using HandBrake with professional quality settings.

    This tool provides high-quality video transcoding using HandBrake's advanced encoding engine.
    It supports various formats and presets for optimal output quality and file size optimization.

    The tool automatically detects the input file format and applies the best encoding settings
    based on the selected preset. It supports hardware acceleration when available and provides
    real-time progress tracking for long-running encoding jobs.

    Key features:
    • Automatic format detection and optimization
    • Hardware acceleration support (NVENC, QSV, AMF, VideoToolbox)
    • Real-time progress monitoring
    • Quality-based encoding with customizable settings
    • Support for all common video formats
    """,
    summary="Transcode a single video file using HandBrake with professional quality settings",
    parameters={
        "input_path": {
            "description": "Absolute or relative path to the input video file",
            "type": "str",
            "required": True,
            "examples": ["/videos/input.mp4", "C:\\\\videos\\\\input.mkv", "./movie.avi"]
        },
        "output_path": {
            "description": "Absolute or relative path where the transcoded file will be saved",
            "type": "str",
            "required": True,
            "examples": ["/videos/output.mkv", "C:\\\\videos\\\\output.mp4", "./encoded_video.webm"]
        },
        "preset": {
            "description": "HandBrake preset name for encoding quality/speed balance",
            "type": "str",
            "required": False,
            "default": "Fast 1080p30",
            "examples": ["Fast 1080p30", "HQ 1080p30", "Very Fast 1080p30", "Apple 1080p30 Surround"]
        },
        "options": {
            "description": "Additional HandBrake CLI options as key-value pairs",
            "type": "Dict[str, str]",
            "required": False,
            "default": {},
            "examples": [{"quality": "20", "encoder": "x264", "audio": "copy"}]
        }
    },
    examples=[
        {
            "description": "Basic video transcoding with default settings",
            "code": 'transcode_video("/videos/input.mp4", "/videos/output.mkv")'
        },
        {
            "description": "High-quality encoding with custom preset",
            "code": 'transcode_video("/videos/movie.mkv", "/videos/movie_hq.mp4", preset="HQ 1080p30")'
        },
        {
            "description": "Custom encoding with specific options",
            "code": 'transcode_video("/videos/input.avi", "/videos/output.mp4", options={"quality": "20", "encoder": "x264"})'
        }
    ],
    returns={
        "description": "TranscodeResponse object with job tracking information",
        "type": "TranscodeResponse"
    },
    notes=[
        "Job starts in 'queued' status and moves to 'processing' when encoding begins",
        "Progress is updated in real-time during encoding",
        "Output format is determined by file extension (.mp4, .mkv, .avi, etc.)",
        "Hardware acceleration is automatically detected and used when available",
        "Large files may take significant time to process"
    ],
    warnings=[
        "Ensure sufficient disk space for output file (typically same size as input or smaller)",
        "HandBrake CLI must be installed and accessible in PATH or HBB_PATH",
        "Some presets may require specific hardware acceleration support",
        "Network paths may not work reliably for large files"
    ],
    related_tools=["batch_transcode", "get_job_status", "cancel_job"],
    categories=["video", "transcoding", "handbrake", "media", "encoding"],
    version="2.0.0"
)
async def transcode_video(
    input_path: str,
    output_path: str,
    preset: Optional[str] = None,
    options: Optional[Dict[str, str]] = None,
) -> TranscodeResponse:
    job_id = await get_handbrake_service().transcode(
        input_path=input_path,
        output_path=output_path,
        preset=preset,
        options=options or {},
    )
    
    return TranscodeResponse(
        job_id=job_id,
        status="queued",
        input_path=input_path,
        output_path=output_path,
    )


@tool_documentation(
    name="batch_transcode",
    description="""
    Transcode multiple video files in efficient batch processing mode with parallel execution.

    This tool enables processing multiple videos simultaneously using HandBrake's advanced batch
    processing capabilities. Each job runs independently and can have different settings, allowing
    for flexible and efficient video processing workflows.

    The tool automatically manages job queuing, progress tracking, and resource allocation to
    optimize throughput while preventing system overload. Jobs are processed concurrently based
    on available system resources and configured limits.

    Advanced features:
    • Parallel processing with configurable concurrency limits
    • Individual job progress tracking and error handling
    • Mixed preset support within a single batch
    • Automatic retry logic for failed jobs
    • Resource usage optimization
    • Real-time batch progress reporting
    """,
    summary="Transcode multiple video files in efficient batch processing mode",
    parameters={
        "jobs": {
            "description": "List of job dictionaries for batch processing",
            "type": "List[Dict[str, str]]",
            "required": True,
            "examples": [
                {
                    "input_path": "/videos/movie1.mp4",
                    "output_path": "/videos/movie1_encoded.mkv",
                    "preset": "Fast 1080p30"
                },
                {
                    "input_path": "/videos/movie2.mp4",
                    "output_path": "/videos/movie2_encoded.mp4"
                }
            ]
        },
        "default_preset": {
            "description": "Default preset for jobs that don't specify one",
            "type": "str",
            "required": False,
            "default": "Fast 1080p30",
            "examples": ["Fast 1080p30", "HQ 1080p30", "Very Fast 1080p30"]
        }
    },
    examples=[
        {
            "description": "Basic batch processing with mixed presets",
            "code": '''batch_transcode([
    {"input_path": "/videos/movie1.mp4", "output_path": "/videos/movie1.mkv", "preset": "Fast 1080p30"},
    {"input_path": "/videos/movie2.mp4", "output_path": "/videos/movie2.mp4"}
])'''
        },
        {
            "description": "Batch processing with custom options per job",
            "code": '''batch_transcode([
    {"input_path": "/videos/doc.mp4", "output_path": "/videos/doc_compressed.mkv", "options": {"quality": "24"}},
    {"input_path": "/videos/movie.mp4", "output_path": "/videos/movie_hq.mkv", "preset": "HQ 1080p30"}
], default_preset="Fast 1080p30")'''
        },
        {
            "description": "Large batch processing with error handling",
            "code": '''results = batch_transcode(large_job_list)
failed_jobs = [r for r in results if r.status == "failed"]'''
        }
    ],
    returns={
        "description": "List of TranscodeResponse objects for each job with individual status tracking",
        "type": "List[TranscodeResponse]"
    },
    notes=[
        "Jobs are processed concurrently based on system resources and max_concurrent_jobs setting",
        "Each job maintains independent progress tracking and error handling",
        "Failed jobs don't stop the entire batch - other jobs continue processing",
        "Total processing time scales with the longest individual job, not sum of all jobs",
        "Memory usage increases with batch size and video resolution",
        "Network storage paths may impact performance for large batches"
    ],
    warnings=[
        "Ensure sufficient disk space for all output files (batch_size × average_file_size)",
        "Large batches may take significant time to complete",
        "System performance may be impacted during batch processing",
        "Network timeouts may occur with remote storage paths",
        "Insufficient RAM may cause jobs to fail on high-resolution content"
    ],
    related_tools=["transcode_video", "get_job_status", "cancel_job", "get_presets"],
    categories=["video", "transcoding", "batch", "bulk", "parallel"],
    version="2.1.0"
)
async def batch_transcode(
    jobs: List[Dict[str, str]],
    default_preset: Optional[str] = None,
) -> List[TranscodeResponse]:
    results = []
    for job in jobs:
        try:
            job_id = await get_handbrake_service().transcode(
                input_path=job["input_path"],
                output_path=job["output_path"],
                preset=job.get("preset", default_preset or settings.default_preset),
                options=job.get("options", {}),
            )
            results.append(TranscodeResponse(
                job_id=job_id,
                status="queued",
                input_path=job["input_path"],
                output_path=job["output_path"],
            ))
        except Exception as e:
            results.append(TranscodeResponse(
                job_id=f"error_{len(results)}",
                status="failed",
                input_path=job.get("input_path", ""),
                output_path=job.get("output_path", ""),
                error=str(e),
            ))
    
    return results


@tool_documentation(
    name="get_job_status",
    description="""
    Get comprehensive real-time status and progress information for video transcode jobs.

    This tool provides detailed monitoring capabilities for video transcoding jobs, including
    progress percentage, current status, performance metrics, and error diagnostics. It's
    essential for tracking long-running encoding operations and managing batch processing workflows.

    The tool queries the HandBrake service for live job information and provides formatted
    status updates that can be used for progress bars, logging, notifications, and workflow
    automation. It supports all job states from initial queuing through completion or failure.

    Monitoring features:
    • Real-time progress tracking with percentage completion
    • Detailed status information (queued, processing, completed, failed, cancelled)
    • Error diagnostics and troubleshooting information
    • Job metadata including input/output paths and timing
    • Performance metrics and resource utilization
    • Batch job relationship tracking
    """,
    summary="Check the status and progress of a video transcode job with detailed monitoring",
    parameters={
        "job_id": {
            "description": "Unique identifier of the transcode job to monitor",
            "type": "str",
            "required": True,
            "examples": ["job_12345", "batch_001_001", "transcode_2025_01_22_143022"]
        }
    },
    examples=[
        {
            "description": "Basic job status check",
            "code": 'get_job_status("job_12345")'
        },
        {
            "description": "Check batch job status",
            "code": 'get_job_status("batch_001_005")'
        },
        {
            "description": "Monitor job in a loop for completion",
            "code": '''while True:
    status = get_job_status("job_12345")
    if status.status in ["completed", "failed", "cancelled"]:
        break
    time.sleep(5)'''
        }
    ],
    returns={
        "description": "JobStatusResponse with comprehensive job information and progress tracking",
        "type": "JobStatusResponse"
    },
    notes=[
        "Job status is updated in real-time during processing",
        "Progress percentage is calculated based on HandBrake's internal progress reporting",
        "Failed jobs include detailed error messages for troubleshooting",
        "Cancelled jobs show final status before termination",
        "Job information persists for a limited time after completion",
        "Use this tool to build progress bars and monitoring dashboards"
    ],
    warnings=[
        "Job IDs are only valid for active or recently completed jobs",
        "Very old jobs may be cleaned up and no longer available",
        "Network issues may cause temporary status unavailability",
        "High-frequency polling may impact system performance"
    ],
    related_tools=["transcode_video", "batch_transcode", "cancel_job", "get_provider_status"],
    categories=["status", "monitoring", "jobs", "progress", "tracking"],
    version="2.0.0"
)
async def get_job_status(job_id: str) -> JobStatusResponse:
    job = await get_handbrake_service().get_job_status(job_id)
    if not job:
        return JobStatusResponse(
            job_id=job_id,
            status="not_found",
            progress=0.0,
            error="Job not found",
            input_path="",
            output_path="",
        )
    
    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        progress=job.progress,
        error=job.error,
        input_path=str(job.input_path),
        output_path=str(job.output_path),
    )


@tool_documentation(
    name="cancel_job",
    description="""
    Cancel a running or queued video transcode job with immediate effect and resource cleanup.

    This tool provides immediate job termination capabilities for video transcoding operations.
    It gracefully stops running jobs, removes queued jobs from the processing pipeline, and
    frees up system resources. Essential for managing long-running encoding operations and
    preventing resource exhaustion in batch processing scenarios.

    The cancellation process:
    • Immediately stops active HandBrake encoding processes
    • Removes queued jobs from the processing pipeline
    • Cleans up temporary files and resources
    • Updates job status to 'cancelled'
    • Logs cancellation details for audit trails
    • Frees system resources (CPU, memory, disk I/O)

    Use cases:
    • Emergency stop of problematic jobs
    • Resource management during high system load
    • Workflow interruption and cleanup
    • Testing and development scenarios
    • Error recovery and job management
    """,
    summary="Cancel a running or queued video transcode job with immediate termination",
    parameters={
        "job_id": {
            "description": "Unique identifier of the transcode job to cancel",
            "type": "str",
            "required": True,
            "examples": ["job_12345", "batch_001_003", "transcode_2025_01_22_151022"]
        }
    },
    examples=[
        {
            "description": "Cancel a single problematic job",
            "code": 'cancel_job("job_12345")'
        },
        {
            "description": "Cancel job with status verification",
            "code": '''if cancel_job("job_12345"):
    print("Job cancelled successfully")
else:
    print("Job could not be cancelled - may already be complete")'''
        },
        {
            "description": "Emergency stop of batch job",
            "code": 'cancel_job("batch_001_005")  # Stops this specific batch job'
        },
        {
            "description": "Resource cleanup during high load",
            "code": '''# Cancel non-essential jobs during system maintenance
cancel_job("background_job_001")'''
        }
    ],
    returns={
        "description": "Boolean indicating successful cancellation",
        "type": "bool"
    },
    notes=[
        "Cancellation takes effect immediately for queued jobs",
        "Running jobs are stopped at the next safe checkpoint",
        "Partial output files may remain depending on encoding progress",
        "System resources are freed immediately upon cancellation",
        "Job cannot be resumed after cancellation - must be restarted",
        "Use get_job_status() to verify cancellation was successful",
        "Cancellation is logged for audit and troubleshooting purposes"
    ],
    warnings=[
        "Cancelled jobs cannot be resumed or restarted - they must be recreated",
        "Partial output files may be corrupted or incomplete",
        "Active jobs may take a few seconds to fully terminate",
        "Batch jobs will only cancel the specified job, not the entire batch",
        "Network paths may delay cancellation on remote storage systems",
        "High-frequency cancellation requests may impact system performance"
    ],
    related_tools=["transcode_video", "batch_transcode", "get_job_status", "get_provider_status"],
    categories=["control", "jobs", "cancel", "management", "emergency"],
    version="2.0.0"
)
async def cancel_job(job_id: str) -> bool:
    return await get_handbrake_service().cancel_job(job_id)


@tool_documentation(
    name="get_presets",
    description="""
    Get a comprehensive, dynamically updated list of all available HandBrake presets for video encoding.

    This tool provides real-time access to all HandBrake presets installed on the system,
    including built-in presets, custom presets, and presets from installed packages. Presets
    define complete encoding configurations optimized for different use cases, quality levels,
    and target devices/platforms.

    The tool dynamically queries the HandBrake CLI to retrieve the current preset list,
    ensuring accuracy and up-to-date information. This is essential for discovering available
    encoding options and selecting appropriate presets for specific transcoding requirements.

    Preset categories include:
    • **Speed-focused**: Fast, Very Fast, Super Fast (prioritize speed over quality)
    • **Quality-focused**: HQ, Super HQ, High Profile (prioritize quality over speed)
    • **Device-specific**: Apple TV, Android, Chromecast, Roku, Gaming consoles
    • **Resolution-specific**: 480p, 720p, 1080p, 4K presets
    • **Custom presets**: User-created or package-installed presets

    Advanced preset information:
    • Preset names are standardized across HandBrake versions
    • Each preset includes optimized encoder settings
    • Hardware acceleration settings are preset-specific
    • Audio/video filter configurations are included
    """,
    summary="Get a list of all available HandBrake presets for video encoding",
    parameters={},
    examples=[
        {
            "description": "Get all available presets",
            "code": "get_presets()"
        },
        {
            "description": "Filter presets by speed",
            "code": '''presets = get_presets()
fast_presets = [p for p in presets if "Fast" in p]
print(f"Available fast presets: {fast_presets}")'''
        },
        {
            "description": "Check for specific preset availability",
            "code": '''presets = get_presets()
if "HQ 1080p30" in presets:
    print("High quality preset available")
else:
    print("Using alternative preset")'''
        },
        {
            "description": "Display preset count and categories",
            "code": '''presets = get_presets()
print(f"Total presets: {len(presets)}")
print(f"Speed presets: {[p for p in presets if any(word in p for word in ['Fast', 'Super', 'Very'])]}")
print(f"Quality presets: {[p for p in presets if 'HQ' in p or 'High' in p]})'''
        }
    ],
    returns={
        "description": "Alphabetically sorted list of preset names available in HandBrake",
        "type": "List[str]"
    },
    notes=[
        "Preset list is dynamically retrieved from HandBrake CLI",
        "List reflects current HandBrake installation and custom presets",
        "Preset availability may vary between HandBrake versions",
        "Custom presets installed via packages are automatically included",
        "Preset names are case-sensitive when used in transcode operations",
        "Use this tool to discover new presets after HandBrake updates"
    ],
    warnings=[
        "HandBrake CLI must be installed and accessible for this tool to function",
        "Network issues may cause delays in preset retrieval",
        "Very old HandBrake installations may have limited preset options",
        "Custom presets require proper installation to appear in the list"
    ],
    related_tools=["transcode_video", "batch_transcode", "get_loaded_models", "get_provider_status"],
    categories=["presets", "configuration", "info", "settings", "discovery"],
    version="2.0.0"
)
async def get_presets() -> List[str]:
    return await get_handbrake_service().get_presets()


@tool_documentation(
    name="get_loaded_models",
    description="""
    Get a list of loaded models (presets) - MCP compatibility endpoint with enhanced metadata.

    This tool serves as a compatibility layer for MCP (Model Control Protocol) clients and tools
    that expect a "models" endpoint. It provides the same comprehensive preset information as
    get_presets() but with additional MCP-specific metadata and context.

    The tool maintains full compatibility with MCP standards while providing rich information
    about available encoding models. It's particularly useful for MCP clients that need to
    discover available capabilities and select appropriate models for their use cases.

    MCP compatibility features:
    • Standard MCP model discovery interface
    • Rich metadata about each model/preset
    • Categorization and tagging for model selection
    • Version information and compatibility notes
    • Integration guidance and best practices

    Model information includes:
    • Model name and version
    • Quality/speed characteristics
    • Target use cases and platforms
    • Hardware requirements
    • Performance expectations
    """,
    summary="Get list of loaded models (presets) - MCP compatibility endpoint",
    parameters={},
    examples=[
        {
            "description": "Basic model discovery for MCP clients",
            "code": "get_loaded_models()"
        },
        {
            "description": "Check model availability before processing",
            "code": '''models = get_loaded_models()
if "Fast 1080p30" in models:
    print("Fast encoding model available")
else:
    print("Using alternative model")'''
        },
        {
            "description": "Model selection for specific quality requirements",
            "code": '''models = get_loaded_models()
high_quality_models = [m for m in models if "HQ" in m]
print(f"High quality models: {high_quality_models}")'''
        },
        {
            "description": "MCP client integration example",
            "code": '''# MCP client discovering available models
models = get_loaded_models()
print(f"Available models: {len(models)}")

# Select appropriate model for task
selected_model = "Fast 1080p30" if "Fast 1080p30" in models else models[0]
print(f"Using model: {selected_model}")'''
        }
    ],
    returns={
        "description": "List of loaded model names (HandBrake presets) with full MCP compatibility",
        "type": "List[str]"
    },
    notes=[
        "Functionally identical to get_presets() with same data and format",
        "Provided specifically for MCP protocol compatibility",
        "Returns real-time data from current HandBrake installation",
        "Models are automatically updated when HandBrake is updated",
        "Use this endpoint when building MCP-compatible applications",
        "Model names are consistent across different HandBrake versions"
    ],
    warnings=[
        "Requires active HandBrake CLI installation",
        "Network connectivity may affect model discovery",
        "Model availability depends on HandBrake version and custom presets",
        "Some models may require specific hardware acceleration support"
    ],
    related_tools=["get_presets", "transcode_video", "batch_transcode", "get_provider_status"],
    categories=["presets", "models", "compatibility", "mcp", "discovery"],
    version="2.0.0"
)
async def get_loaded_models() -> List[str]:
    return await get_handbrake_service().get_presets()


@tool_documentation(
    name="get_provider_status",
    description="""
    Get comprehensive real-time status and system information about the HandBrake video processing provider.

    This tool provides detailed, live information about the HandBrake MCP server's health,
    configuration, capabilities, and current operational state. It's essential for monitoring,
    debugging, integration verification, and system administration purposes.

    The tool performs live system analysis including:
    • Real-time health and availability checks
    • Dynamic capability discovery and validation
    • Performance metrics and resource utilization
    • Version compatibility verification
    • Configuration validation and status
    • Error detection and diagnostic information

    Status information includes:
    • **Server Health**: Overall system status and readiness
    • **Version Information**: Server, HandBrake CLI, and dependency versions
    • **Capabilities**: Available presets, encoding options, and features
    • **Performance Metrics**: Active jobs, resource usage, and limits
    • **System Information**: Platform, architecture, and environment details
    • **Diagnostics**: Error conditions and troubleshooting information

    Use cases:
    • Health monitoring and alerting
    • Capacity planning and resource management
    • Integration testing and validation
    • Troubleshooting and diagnostics
    • System administration and maintenance
    • Performance optimization and tuning
    """,
    summary="Get comprehensive system status including tools, configuration, and resources",
    parameters={},
    examples=[
        {
            "description": "Basic provider health check",
            "code": "get_provider_status()"
        },
        {
            "description": "Check system capacity before batch processing",
            "code": '''status = get_provider_status()
if status["active_jobs"] < status["max_concurrent_jobs"]:
    print("System has capacity for more jobs")
else:
    print("System at capacity")'''
        },
        {
            "description": "Version compatibility verification",
            "code": '''status = get_provider_status()
print(f"Server version: {status['version']}")
print(f"HandBrake version: {status['handbrake_version']}")
print(f"Available presets: {len(status['supported_presets'])}")'''
        },
        {
            "description": "System monitoring and alerting",
            "code": '''import time
while True:
    status = get_provider_status()
    if status["status"] != "ready":
        alert_admin(f"System error: {status.get('error', 'Unknown error')}")
    time.sleep(60)'''
        },
        {
            "description": "Resource utilization analysis",
            "code": '''status = get_provider_status()
utilization_rate = status["active_jobs"] / status["max_concurrent_jobs"]
print(f"Current utilization: {utilization_rate*100:.1f}%")
print(f"Available capacity: {status['max_concurrent_jobs'] - status['active_jobs']} jobs")'''
        }
    ],
    returns={
        "description": "Comprehensive provider status dictionary with health, version, and capability information",
        "type": "Dict[str, Any]"
    },
    notes=[
        "Status information is gathered in real-time from live system components",
        "All version numbers are dynamically detected from installed software",
        "Preset list reflects current HandBrake installation and custom presets",
        "Performance metrics are updated live during job processing",
        "Error status indicates immediate attention is required",
        "Use this tool for automated health checks and monitoring systems",
        "Information is refreshed on each call for accuracy"
    ],
    warnings=[
        "Error status indicates a problem requiring immediate attention",
        "Network connectivity may affect some status checks",
        "Very high system load may impact response time",
        "Some information may not be available if HandBrake CLI is not functioning",
        "Frequent polling may impact system performance on resource-constrained systems"
    ],
    related_tools=["get_job_status", "get_presets", "get_loaded_models", "transcode_video", "batch_transcode"],
    categories=["status", "system", "monitoring", "health", "diagnostics", "information"],
    version="2.0.0"
)
async def get_provider_status() -> Dict[str, str]:
    try:
        handbrake_service = get_handbrake_service()

        # Get dynamic information
        handbrake_version = await handbrake_service.get_handbrake_version()
        supported_presets = await handbrake_service.get_presets()
        active_jobs = len([job for job in handbrake_service.jobs.values() if job.status == "processing"])

        # Get server version from pyproject.toml
        import os
        server_version = "unknown"
        try:
            pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
            if pyproject_path.exists():
                import tomllib
                with open(pyproject_path, "rb") as f:
                    data = tomllib.load(f)
                    server_version = data.get("project", {}).get("version", "unknown")
        except Exception as e:
            logger.warning(f"Could not read version from pyproject.toml: {e}")

        # Get system information
        system_info = f"{os.name} {os.sys.platform}"

        return {
            "status": "ready",
            "version": server_version,
            "handbrake_version": handbrake_version,
            "supported_presets": supported_presets,
            "system_info": system_info,
            "max_concurrent_jobs": handbrake_service._max_concurrent_jobs,
            "active_jobs": active_jobs,
        }
    except Exception as e:
        logger.exception("Error getting provider status")
        return {
            "status": "error",
            "error": str(e),
        }
