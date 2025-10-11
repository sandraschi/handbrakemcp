"""HandBrake MCP Server Tools Package.

This package contains all MCP tools organized by functionality:
- handbrake_tools: Core HandBrake video transcoding operations
- help_tools: Help and documentation tools
- status_tools: System status and monitoring tools
- utility_tools: Shared utilities and base classes
"""

from .utility_tools import (
    ToolDocumentation,
    tool_documentation,
    get_all_tool_documentation,
    TranscodeRequest,
    TranscodeResponse,
    JobStatusResponse,
)

from .handbrake_tools import (
    transcode_video,
    batch_transcode,
    get_job_status,
    cancel_job,
    get_presets,
    get_loaded_models,
    get_provider_status,
)

from .help_tools import (
    get_tool_help,
    get_multilevel_help,
    get_advanced_help,
    get_tool_categories,
    get_tools_by_category,
    search_tools,
)

from .status_tools import (
    get_system_status,
)