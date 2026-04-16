# Changelog

All notable changes to this project will be documented in this file.

## [1.1.1] - 2026-04-09

### Added
- **SOTA Industrial Dashboard**: Finalized the `web_sota` frontend with premium aesthetics and hardening.
- **FastAPI REST Bridge**: Implemented a robust `/api/tools` discovery layer and enabled HTTP mode by default.
- **Agentic Workflow**: Registered high-level orchestration tools for automated transcoding sequences.
- **Documentation Hub**: Created `docs/index.md` as a unified entry point for industrial standards.

### Fixed
- **Tool Discovery**: Resolved 500/404 errors in tool registration via `FastMCP.to_mcp_tool()`.
- **Runtime Stability**: Implemented defensive null-safety in the React dashboard to prevent UI crashes.
- **Networking**: Standardized on IPv4 loopback (127.0.0.1) for reliable cross-service communication.

### Changed
- **Branding**: Updated repository to SOTA v13.1 Industrial Stable status.
- **Build Process**: Resolved TypeScript linting errors blocking production builds.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-04-09

### Added
- **Industrial Dashboard (v13.1)**: New React-based control plane in `web_sota` optimized for Stability and Telemetry.
- **FastAPI Mount Pattern**: Backend now uses regulated FastAPI mounting for FastMCP REST bridge compatibility.
- **127.0.0.1 Networking Standard**: Codified IPv4 loopback requirement for all cross-service communication to bypass Windows IPv6 resolution issues.

### Fixed
- **Frontend "Red Screen" Crash**: Fixed JavaScript hoisting/initialization error in `logger-panel.tsx` where telemetry polling preceded variable initialization.
- **IPv6 Connectivity Loop**: Resolved connectivity failures where `localhost` resolution to `::1` caused requests to bypass the IPv4-bound backend.
- **Build Breakage**: Removed unmanaged `framer-motion` dependency and resolved `APPS_CATALOG` naming mismatches in the frontend.
- **TypeScript Compliance**: Resolved multiple implicit `any` errors and schema-interface mismatches.

### Changed
- Dashboard layout aligned with **OSC MCP "Gold Standard"** for industrial-grade reliability.
- Updated `README.md` and `PLAN.md` to reflect SOTA v13.1 status.

---

## [1.0.0] - 2025-09-23

### Added
- Initial release of HandBrake MCP Server.
- Core transcoding tools and job management.
- Enterprise CI/CD pipeline and professional documentation system.
