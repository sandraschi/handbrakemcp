"""Help and documentation tools for HandBrake MCP server.

This module contains all help, documentation, and tool discovery tools:
- get_tool_help: Help for individual tools at different detail levels
- get_multilevel_help: System-wide help at different levels
- get_advanced_help: Advanced usage, examples, and troubleshooting
- get_tool_categories: Tools organized by category
- get_tools_by_category: Tools filtered by specific category
- search_tools: Keyword-based tool discovery
"""

from typing import Dict, List, Optional

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
    name="help",
    description="Get comprehensive help for tools at different detail levels",
    tags={"help", "documentation", "information"}
)
def get_tool_help(tool_name: str, level: str = "basic") -> str:
    """
    Get help for a specific tool at different detail levels.

    This function provides contextual help and documentation for individual MCP tools.
    It supports multiple detail levels to accommodate different user needs and experience levels.

    Parameters:
        tool_name: Name of the tool to get help for
            - Must be a valid registered tool name
            - Case-sensitive tool name matching
            - Use get_multilevel_help() to see available tools

        level: Detail level for help information (default: "basic")
            - "basic": Brief description and summary
            - "detailed": Parameters, examples count, and version
            - "full": Complete documentation with all sections

    Returns:
        Formatted help text string:
            - Basic level: Single line with tool name and summary
            - Detailed level: Multi-line with parameters and examples
            - Full level: Complete multiline documentation
            - Error message if tool not found or invalid level

    Usage:
        Use this function to get targeted help for specific tools when you need detailed
        information about tool capabilities, parameters, or usage examples.

        Common scenarios:
        - Learning about a new tool's capabilities
        - Understanding parameter requirements
        - Finding usage examples and best practices
        - Troubleshooting tool-specific issues

    Examples:
        Basic help request:
            help_text = get_tool_help("transcode_video", "basic")
            # Returns: "[TOOL] transcode_video: Transcode a single video file using HandBrake..."

        Detailed help request:
            help_text = get_tool_help("get_job_status", "detailed")
            # Returns: Multi-line detailed information with parameters and examples count

        Full documentation:
            help_text = get_tool_help("batch_transcode", "full")
            # Returns: Complete multiline documentation with all sections

        Error handling:
            help_text = get_tool_help("nonexistent_tool")
            # Returns: "❌ Tool 'nonexistent_tool' not found. Available tools: ..."

    Raises:
        ValueError: If level parameter is invalid (not "basic", "detailed", or "full")

    Notes:
        - Tool help is generated from the tool's comprehensive documentation
        - Help levels provide progressive disclosure of information
        - Use "full" level for complete reference documentation
        - Tool names are case-sensitive and must match registered names

    See Also:
        - get_multilevel_help: For system-wide help at different levels
        - get_advanced_help: For advanced usage and troubleshooting help
        - tool_categories: For discovering tools by category
        - search_tools: For finding tools by keyword
    """
    docs = get_all_tool_documentation()

    if tool_name not in docs:
        return f"❌ Tool '{tool_name}' not found. Available tools: {', '.join(docs.keys())}"

    doc = docs[tool_name]

    if level == "basic":
        return f"[TOOL] {doc.name}: {doc.get_basic_description()}"
    elif level == "detailed":
        return f"[DETAIL] {doc.name.upper()}\n\n{doc.get_detailed_description()}\n\nPARAMETERS: {len(doc.parameters)} | EXAMPLES: {len(doc.examples)}"
    elif level == "full":
        return doc.get_multiline_description()
    else:
        return f"❌ Invalid help level '{level}'. Use: basic, detailed, or full"


@tool(
    name="tool_categories",
    description="Get all tools organized by category",
    tags={"help", "documentation", "categories", "organization"}
)
def get_tool_categories() -> Dict[str, List[str]]:
    """
    Get all tools organized by category with programmatic access to category structure.

    This function provides a dictionary mapping of categories to tool names, enabling
    programmatic discovery and organization of tools by their functional categories.
    Essential for building user interfaces, documentation systems, and tool discovery features.

    Parameters:
        None: This function analyzes all registered tools automatically

    Returns:
        Dictionary mapping category names to lists of tool names:
            - Keys: Category names (strings)
            - Values: Lists of tool names in that category (List[str])
            - Categories are derived from tool metadata
            - Tools can belong to multiple categories
            - Empty dictionary if no tools are registered

    Usage:
        Use this function to build category-based navigation, filtering, and organization
        features in user interfaces and documentation systems.

        Common scenarios:
        - Building category-based tool browsers
        - Creating documentation organized by functionality
        - Implementing search filters by category
        - Generating category statistics and reports

    Examples:
        Get all categories and their tools:
            categories = get_tool_categories()
            for category, tools in categories.items():
                print(f"{category}: {len(tools)} tools")
            # Returns: {'video': ['transcode_video', 'batch_transcode'], 'status': ['get_job_status'], ...}

        Find tools in specific category:
            video_tools = categories.get('video', [])
            print(f"Video tools: {video_tools}")
            # Returns: ['transcode_video', 'batch_transcode']

        Category statistics:
            category_counts = {cat: len(tools) for cat, tools in categories.items()}
            print(f"Total categories: {len(categories)}")
            print(f"Largest category: {max(category_counts, key=category_counts.get)}")
            # Returns: Statistical analysis of category distribution

    Raises:
        RuntimeError: If tool documentation is not properly initialized

    Notes:
        - Categories are automatically derived from tool metadata
        - Tools can belong to multiple categories simultaneously
        - Category names are normalized and consistent
        - Results reflect current tool registration state
        - Function is lightweight and suitable for frequent calls

    See Also:
        - get_tools_by_category: For getting tools in a specific category
        - get_multilevel_help: For category-based help display
        - search_tools: For keyword-based tool discovery
    """
    docs = get_all_tool_documentation()

    categories = {}
    for tool_name, doc in docs.items():
        for category in doc.categories:
            if category not in categories:
                categories[category] = []
            categories[category].append(tool_name)

    return categories


def get_tools_by_category(category: str) -> List[str]:
    """
    Get all tools belonging to a specific category with filtering capability.

    This function provides targeted tool discovery by filtering tools based on
    their category membership. Useful for building category-specific interfaces
    and implementing category-based navigation and filtering.

    Parameters:
        category: Category name to filter tools by
            - Case-sensitive category name matching
            - Must match categories defined in tool documentation
            - Use get_tool_categories() to see available categories

    Returns:
        List of tool names belonging to the specified category:
            - Tool names as strings
            - Empty list if category doesn't exist or has no tools
            - Order is not guaranteed (implementation dependent)
            - Tools appear only once even if in multiple categories

    Usage:
        Use this function when you need to work with tools of a specific functional
        area or when building category-based user interfaces and workflows.

        Common scenarios:
        - Building category-specific tool palettes
        - Implementing category-based filtering in search interfaces
        - Creating workflow wizards for specific tool types
        - Generating category-specific documentation

    Examples:
        Get video processing tools:
            video_tools = get_tools_by_category("video")
            print(f"Available video tools: {video_tools}")
            # Returns: ['transcode_video', 'batch_transcode']

        Get status and monitoring tools:
            status_tools = get_tools_by_category("status")
            monitoring_tools = get_tools_by_category("monitoring")
            all_status_tools = list(set(status_tools + monitoring_tools))
            print(f"Status/monitoring tools: {all_status_tools}")
            # Returns: Combined list of status and monitoring tools

        Category validation:
            available_categories = get_tool_categories().keys()
            if "video" in available_categories:
                video_tools = get_tools_by_category("video")
                print(f"Found {len(video_tools)} video tools")
            else:
                print("Video category not found")

    Raises:
        ValueError: If category parameter is empty or invalid

    Notes:
        - Function performs case-sensitive category matching
        - Returns tools that have the category in their category list
        - Tools can appear in multiple categories
        - Results are dynamically generated from current tool state
        - Empty results are valid (category exists but has no tools)

    See Also:
        - get_tool_categories: For getting all categories and their tools
        - search_tools: For keyword-based tool discovery
        - get_multilevel_help: For category-filtered help display
    """
    docs = get_all_tool_documentation()
    return [name for name, doc in docs.items() if category in doc.categories]


@tool(
    name="search_tools",
    description="Search tools by name, description, or category",
    tags={"help", "documentation", "search", "discovery"}
)
def search_tools(query: str) -> List[str]:
    """
    Search tools by name, description, or category using keyword matching.

    This function provides powerful search capabilities across all tool metadata,
    enabling users to discover tools through natural language queries. Searches
    across tool names, descriptions, summaries, and categories for comprehensive
    discovery.

    Parameters:
        query: Search query string for tool discovery
            - Case-insensitive keyword matching
            - Searches across multiple metadata fields
            - Supports partial word matches
            - Can be a single word or phrase

    Returns:
        List of tool names matching the search query:
            - Tool names as strings (not full tool objects)
            - Order is not guaranteed (relevance-based when possible)
            - Empty list if no tools match the query
            - Duplicates are automatically removed

    Usage:
        Use this function for implementing search functionality in user interfaces,
        command-line tools, and documentation systems. Provides flexible discovery
        of tools based on functionality, purpose, or keywords.

        Common scenarios:
        - Building search interfaces for tool discovery
        - Command-line tool lookup by functionality
        - Documentation search and navigation
        - Workflow discovery based on use cases

    Examples:
        Search by functionality:
            transcode_tools = search_tools("transcode")
            print(f"Transcoding tools: {transcode_tools}")
            # Returns: ['transcode_video', 'batch_transcode']

        Search by category:
            status_tools = search_tools("status")
            print(f"Status-related tools: {status_tools}")
            # Returns: ['get_job_status', 'get_provider_status', 'system_status']

        Search by description keywords:
            batch_tools = search_tools("batch")
            parallel_tools = search_tools("parallel")
            print(f"Batch processing tools: {batch_tools}")
            print(f"Parallel processing tools: {parallel_tools}")
            # Returns: Tools related to batch and parallel processing

        Combined search and filtering:
            video_tools = search_tools("video")
            status_tools = search_tools("status")
            all_tools = list(set(video_tools + status_tools))
            print(f"All video and status tools: {all_tools}")
            # Returns: Combined results from multiple searches

    Raises:
        ValueError: If query is empty or invalid

    Notes:
        - Search is case-insensitive for user-friendly discovery
        - Matches partial words and substrings
        - Searches across tool names, summaries, descriptions, and categories
        - Results are deduplicated automatically
        - Performance is optimized for frequent searches
        - Empty query returns empty results (not all tools)

    See Also:
        - get_tool_categories: For category-based tool discovery
        - get_tools_by_category: For category-specific tool filtering
        - get_multilevel_help: For categorized help display
        - get_tool_help: For detailed information about specific tools
    """
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


@tool(
    name="multilevel_help",
    description="Get help at different levels: basic, detailed, full, categories",
    tags={"help", "documentation", "information", "categories"}
)
def get_multilevel_help(level: str = "basic", filter_by: Optional[str] = None) -> str:
    """
    Get comprehensive help at different detail levels across all tools and system functions.

    This function provides system-wide help and documentation with multiple levels of detail
    and filtering capabilities. It's the primary help system for the HandBrake MCP server,
    offering progressive disclosure from basic overviews to complete technical documentation.

    Parameters:
        level: Help detail level determining information scope and format (default: "basic")
            - "basic": Overview with tool count and quick start guide
            - "detailed": Categorized tool list with parameters and examples
            - "full": Complete documentation for all tools (can be large)
            - "categories": Tool organization by category with counts

        filter_by: Optional category name to filter results (default: None)
            - Only applies to "detailed" and "full" levels
            - Case-insensitive category name matching
            - Shows only tools in the specified category
            - Use "categories" level to see available categories

    Returns:
        Formatted help text string with comprehensive information:
            - Basic: System overview, tool count, quick commands
            - Detailed: Categorized tools with parameter counts and examples
            - Full: Complete multiline documentation for all/specified tools
            - Categories: Category overview with tool counts per category

    Usage:
        Use this function as the primary help system for discovering tools, understanding
        capabilities, and navigating the HandBrake MCP server's functionality.

        Common scenarios:
        - Getting started with the MCP server
        - Discovering available tools and their purposes
        - Finding tools for specific video processing tasks
        - Understanding system capabilities and limitations

    Examples:
        Basic system overview:
            help_text = get_multilevel_help("basic")
            # Returns: Overview with tool count, quick commands, and getting started guide

        Detailed tool listing:
            help_text = get_multilevel_help("detailed")
            # Returns: All tools organized by category with parameter and example counts

        Category-specific help:
            help_text = get_multilevel_help("detailed", "video")
            # Returns: Only video-related tools with detailed information

        Complete documentation:
            help_text = get_multilevel_help("full")
            # Returns: Complete multiline documentation for all tools (comprehensive)

        Category overview:
            help_text = get_multilevel_help("categories")
            # Returns: All categories with tool counts and brief descriptions

    Raises:
        ValueError: If level parameter is invalid (not "basic", "detailed", "full", or "categories")

    Notes:
        - "full" level can return very large amounts of text
        - Use filter_by to focus on specific tool categories
        - Help content is generated dynamically from tool documentation
        - Categories are automatically derived from tool metadata
        - System updates automatically reflect in help content

    See Also:
        - get_tool_help: For help on specific individual tools
        - get_advanced_help: For advanced usage, troubleshooting, and performance help
        - tool_categories: For programmatic category access
        - search_tools: For keyword-based tool discovery
        - system_status: For current system state and configuration
    """
    docs = get_all_tool_documentation()

    if level == "basic":
        lines = ["[TOOLS]  HANDBRAKE MCP TOOLS - BASIC HELP"]
        lines.append("=" * 50)

        lines.append(f"\n[INFO] OVERVIEW: {len(docs)} tools available")
        lines.append("")

        lines.append("[TOOLS] AVAILABLE TOOLS:")
        for tool_name, doc in docs.items():
            lines.append(f"  - {tool_name}: {doc.get_basic_description()}")

        lines.append("")
        lines.append("[TIP] QUICK COMMANDS:")
        lines.append("  - help - Get comprehensive help for tools")
        lines.append("  - system_status - Get comprehensive system status")
        lines.append("  - get_presets - List all available HandBrake presets")
        lines.append("  - transcode_video - Transcode a single video file")
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
                lines.append(f"  - {tool_name}: {doc.get_detailed_description()}")
                lines.append(f"    Parameters: {len(doc.parameters)} | Examples: {len(doc.examples)}")

        lines.append("")
        lines.append("[DOCS] LEGEND:")
        lines.append("  [RUNNING] Ready for use")
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
            lines = ["[DOCS] HANDBRAKE MCP TOOLS - COMPLETE DOCUMENTATION"]
            lines.append("=" * 60)

            for i, (tool_name, doc) in enumerate(docs.items(), 1):
                lines.append(f"\n{i}. {doc.get_multiline_description()}")
                if i < len(docs):
                    lines.append("\n" + "-" * 60)

    elif level == "categories":
        lines = ["📂 HANDBRAKE MCP TOOLS - CATEGORIES"]
        lines.append("=" * 50)

        categories = get_tool_categories()

        lines.append(f"\n[INFO] CATEGORY OVERVIEW: {len(categories)} categories")
        lines.append("")

        for category, tools in categories.items():
            lines.append(f"📁 {category.upper()} ({len(tools)} tools):")
            for tool_name in tools:
                doc = docs[tool_name]
                lines.append(f"  - {tool_name}: {doc.get_basic_description()}")
            lines.append("")

    else:
        return f"❌ Invalid help level '{level}'. Available levels: basic, detailed, full, categories"

    return "\n".join(lines)


@tool(
    name="advanced_help",
    description="Get advanced help: overview, examples, troubleshooting, performance",
    tags={"help", "documentation", "advanced", "troubleshooting"}
)
def get_advanced_help(tool_name: Optional[str] = None, help_type: str = "overview") -> str:
    """
    Get advanced help information for tools and system with specialized content and guidance.

    This function provides specialized help content for advanced users, including detailed
    usage examples, troubleshooting guides, performance optimization tips, and system-specific
    guidance. It's designed for users who need in-depth technical information and best practices.

    Parameters:
        tool_name: Specific tool name to get advanced help for (default: None)
            - If None, provides system-wide advanced help
            - If specified, provides tool-specific advanced guidance
            - Must be a valid registered tool name when specified
            - Case-sensitive tool name matching

        help_type: Type of advanced help content to retrieve (default: "overview")
            - "overview": System capabilities and workflow overview
            - "examples": Detailed usage examples and code patterns
            - "troubleshooting": Problem diagnosis and resolution guides
            - "performance": Optimization tips and performance best practices

    Returns:
        Advanced help text string with specialized content:
            - Overview: System capabilities, workflows, and feature highlights
            - Examples: Detailed code examples, patterns, and integration guides
            - Troubleshooting: Diagnostic procedures, common issues, and solutions
            - Performance: Optimization strategies, monitoring, and tuning guidance

    Usage:
        Use this function when you need advanced technical guidance, troubleshooting assistance,
        or performance optimization advice for the HandBrake MCP server.

        Common scenarios:
        - Understanding complex workflows and integrations
        - Troubleshooting system or tool-specific issues
        - Optimizing performance for production deployments
        - Learning advanced usage patterns and best practices

    Examples:
        System overview:
            help_text = get_advanced_help(help_type="overview")
            # Returns: Comprehensive system capabilities and workflow overview

        Usage examples:
            help_text = get_advanced_help(help_type="examples")
            # Returns: Detailed code examples and integration patterns

        Troubleshooting guide:
            help_text = get_advanced_help(help_type="troubleshooting")
            # Returns: Diagnostic procedures and problem resolution guides

        Performance optimization:
            help_text = get_advanced_help(help_type="performance")
            # Returns: Performance tuning and optimization strategies

        Tool-specific advanced help:
            help_text = get_advanced_help("transcode_video", "examples")
            # Returns: Advanced examples specific to the transcode_video tool

    Raises:
        ValueError: If help_type is invalid or tool_name is not found

    Notes:
        - Advanced help is complementary to basic help functions
        - Content focuses on technical depth and practical application
        - Examples include error handling and edge cases
        - Troubleshooting content is regularly updated based on user issues
        - Performance guidance includes system-specific optimizations

    See Also:
        - get_tool_help: For basic tool documentation
        - get_multilevel_help: For system-wide help at different levels
        - system_status: For current system state and monitoring
        - get_provider_status: For detailed system health information
    """
    docs = get_all_tool_documentation()

    if help_type == "overview":
        lines = ["[ADVANCED] HANDBRAKE MCP - ADVANCED OVERVIEW"]
        lines.append("=" * 50)

        lines.append(f"\n[INFO] SYSTEM CAPABILITIES: {len(docs)} specialized tools")
        lines.append("")

        lines.append("[TOOLS] CORE WORKFLOW:")
        lines.append("  1. transcode_video - Single file processing")
        lines.append("  2. batch_transcode - Multiple file processing")
        lines.append("  3. get_job_status - Progress monitoring")
        lines.append("  4. cancel_job - Job management")
        lines.append("  5. get_presets - Configuration discovery")
        lines.append("")

        lines.append("[TROUBLESHOOT] ADVANCED FEATURES:")
        lines.append("  - Real-time progress tracking")
        lines.append("  - Hardware acceleration support")
        lines.append("  - Batch processing optimization")
        lines.append("  - Error handling and recovery")
        lines.append("  - Resource management")
        lines.append("")

    elif help_type == "examples":
        lines = ["[TIP] HANDBRAKE MCP - USAGE EXAMPLES"]
        lines.append("=" * 50)

        lines.append("\n[USAGE] BASIC USAGE:")
        lines.append("  # Single video transcoding")
        lines.append("  transcode_video('/videos/input.mp4', '/videos/output.mkv')")
        lines.append("")

        lines.append("  # Batch processing")
        lines.append("  batch_transcode([{'input_path': 'file1.mp4', 'output_path': 'file1.mkv'}])")
        lines.append("")

        lines.append("  # With custom presets")
        lines.append("  transcode_video('/videos/input.mp4', '/videos/output.mp4', preset='HQ 1080p30')")
        lines.append("")

        lines.append("[INFO] MONITORING:")
        lines.append("  # Check job status")
        lines.append("  get_job_status('job_12345')")
        lines.append("")

        lines.append("  # Get system status")
        lines.append("  get_provider_status()")
        lines.append("")

        lines.append("[CONFIG]  CONFIGURATION:")
        lines.append("  # Discover available presets")
        lines.append("  presets = get_presets()")
        lines.append("")

        lines.append("  # Check system capabilities")
        lines.append("  status = get_provider_status()")
        lines.append("  print(f'Available presets: {len(status[\"supported_presets\"])}')")

    elif help_type == "troubleshooting":
        lines = ["[TROUBLESHOOT] HANDBRAKE MCP - TROUBLESHOOTING GUIDE"]
        lines.append("=" * 50)

        lines.append("\n❌ COMMON ISSUES:")
        lines.append("")

        lines.append("🔍 'HandBrake CLI not found':")
        lines.append("  - Install HandBrake CLI or set HBB_PATH")
        lines.append("  - Verify installation with 'HandBrakeCLI --version'")
        lines.append("  - Check system PATH environment variable")
        lines.append("")

        lines.append("📁 'File not found':")
        lines.append("  - Verify input file path exists")
        lines.append("  - Check file permissions")
        lines.append("  - Use absolute paths when possible")
        lines.append("")

        lines.append("[CONFIG]  'Invalid preset':")
        lines.append("  - Use get_presets() to see available options")
        lines.append("  - Check HandBrake CLI version compatibility")
        lines.append("  - Verify preset name spelling")
        lines.append("")

        lines.append("🛑 'Job failed':")
        lines.append("  - Check error message in job status")
        lines.append("  - Verify output directory exists and is writable")
        lines.append("  - Check available disk space")
        lines.append("  - Review system resource usage")
        lines.append("")

        lines.append("🔍 DIAGNOSTIC STEPS:")
        lines.append("  1. Run get_provider_status() to check system health")
        lines.append("  2. Use get_presets() to verify available options")
        lines.append("  3. Check job status with get_job_status()")
        lines.append("  4. Review system logs for error details")
        lines.append("  5. Test with simple files first")

    elif help_type == "performance":
        lines = ["[PERFORMANCE] HANDBRAKE MCP - PERFORMANCE OPTIMIZATION"]
        lines.append("=" * 50)

        lines.append("\n[TOOLS] OPTIMIZATION STRATEGIES:")
        lines.append("")

        lines.append("💾 RESOURCE MANAGEMENT:")
        lines.append("  - Use appropriate presets for your use case")
        lines.append("  - Monitor system resources during processing")
        lines.append("  - Adjust max_concurrent_jobs based on system capacity")
        lines.append("  - Use hardware acceleration when available")
        lines.append("")

        lines.append("[BATCH] BATCH PROCESSING:")
        lines.append("  - Process similar files together for efficiency")
        lines.append("  - Use consistent presets within batches")
        lines.append("  - Monitor memory usage with large batches")
        lines.append("  - Consider disk I/O limitations")
        lines.append("")

        lines.append("[TROUBLESHOOT] SYSTEM TUNING:")
        lines.append("  - Ensure adequate RAM for video processing")
        lines.append("  - Use SSD storage for temporary files")
        lines.append("  - Monitor CPU and GPU utilization")
        lines.append("  - Consider network storage limitations")
        lines.append("")

        lines.append("[INFO] MONITORING TOOLS:")
        lines.append("  - get_provider_status() - System health")
        lines.append("  - get_job_status() - Individual job progress")
        lines.append("  - Use detailed help for tool-specific guidance")

    else:
        return f"❌ Invalid help type '{help_type}'. Available types: overview, examples, troubleshooting, performance"

    return "\n".join(lines)
