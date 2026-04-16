# HandBrake MCP Documentation Hub

> [!NOTE]
> **Status**: SOTA v13.1 Industrial Stable
> **Last Updated**: 2026-04-09

Welcome to the HandBrake MCP documentation. This repository provides a high-fidelity control plane for HandBrake transcoding operations, exposed via the Model Context Protocol (MCP) and a dedicated SOTA Industrial Dashboard.

## 🗂️ Documentation Sections

### 🚀 Getting Started
- [Installation Guide](installation.md) - System requirements and deployment steps.
- [SOTA Industrial Dashboard](index.md#dashboard) - Navigating the premium control interface.

### 🛠️ Tool Reference
- **Transcoding**: `transcode_file`, `agentic_workflow`.
- **Media Information**: `get_media_info`.
- **System**: `health_check`, `metrics`.

### 📑 Standards & Protocols
- [Tool Docstring Standards](TOOL_DOCSTRING_STANDARD.md) - v13.1 Gold Standard compliance.
- [MCP Production Checklist](MCP_PRODUCTION_CHECKLIST.md) - Industrial hardening requirements.

## 📊 Dashboard <a name="dashboard"></a>
The HandBrake MCP Dashboard is a SOTA v13.1 compliant web application located in `web_sota/`. It provides:
- **Real-time Job Tracking**: Visual progress monitoring of transcoding tasks.
- **REST API Bridge**: Direct tool execution via FastMCP REST interface.
- **Universal Fleet Discovery**: Integration with the broader `mcp-central-docs` ecosystem.

## 🔧 Technical Details
- **Backend**: Python 3.12+, FastMCP 3.2.
- **Frontend**: React + TypeScript + Vite.
- **Port Allocation**: 51594 (Backend), 51595 (Frontend).

---
*Developed by Sandra Schipal | Vienna, Austria | 2026*
