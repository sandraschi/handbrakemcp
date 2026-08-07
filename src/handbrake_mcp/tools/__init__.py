"""HandBrake MCP Server Tools Package.

This package contains all MCP tools organized by functionality:
- handbrake_tools: Core HandBrake video transcoding operations
- help_tools: Help and documentation tools
- status_tools: System status and monitoring tools
- utility_tools: Shared utilities and base classes
"""

from .handbrake_tools import (
    batch_transcode,
    cancel_job,
    get_job_status,
    get_loaded_models,
    get_presets,
    get_provider_status,
    transcode_video,
)
from .help_tools import (
    get_advanced_help,
    get_multilevel_help,
    get_tool_categories,
    get_tool_help,
    get_tools_by_category,
    search_tools,
)
from .status_tools import (
    get_system_status,
)
from .utility_tools import (
    JobStatusResponse,
    ToolDocumentation,
    TranscodeRequest,
    TranscodeResponse,
    get_all_tool_documentation,
    tool_documentation,
)
