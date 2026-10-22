
## [Unreleased] — 2026-10-23 (onboarding)

### Added
- **GUI-vs-CLI trap closed**: the #1 new-user confusion — `C:\Program Files\HandBrake\HandBrake.exe` exists but no engine. `probe_handbrake_cli()` now reports `gui_present`, `/health` passes it through with a `hint`, the Dashboard CTA and Settings panel name the trap explicitly, and ONBOARDING documents it. Probe unit test added.
- **Onboarding gate (HIGH → closed)**: `docs/ONBOARDING.md` (7-section standard: purpose, free-forever cost table, CLI prerequisites, winget steps, 6 pitfalls, `/health` sanity check, declared doubles). INSTALL.md top quote + README onboarding pointer.
- **Backend signal**: `/health` now returns `handbrake: {cli_available, cli_path, cli_version, instance_configured}` via non-raising `probe_handbrake_cli()` (PATH + WinGet fallback). Missing-CLI error now names the winget command and the onboarding doc.
- **Webapp cues**: red under-hero `data-testid="onboarding-cue"` CTA on the Dashboard when `instance_configured === false`; Transcoding Engine panel in Settings (live badge + install command); Help page onboarding pointer. No MOCK content anywhere — empty states were already honest, declared in ONBOARDING § Declared doubles.
- Probe unit tests (present/missing); suite: **8 passed, 3 skipped**.

## [Unreleased] — 2026-10-23 (assfix deferreds)

### Added
- HandBrakeCLI 1.11.2 installed on Goliath (winget) — integration tests run against the real engine.
- `show_status_card` Prefab tool (`app=True`) for in-chat status cards.
- Session-context injection on all channels: `.cursorrules` block, `.windsurfrules`, `.github/copilot-instructions.md`, `.claude-plugin/plugin.json` + `hooks/hooks.json`, `.opencode/skills/handbrake/`, `.agents/skills/handbrake/`.
- Shared `_error_response()` helper (TECH §7.1 Pattern 3), wired into provider-status + job/transcode routes.
- Rebuilt `skills/handbrake-expert/SKILL.md` (frontmatter, agent routing, verified tool catalog, 3 workflows, error recovery).
- `web_sota/bun.lock` (bun 1.3.14 migration).

### Fixed
- **Test harness**: dead unittest-style `asyncSetUp` (never ran under pytest) replaced with `integration_test_setup` fixture; unit fixture now isolates the RAM gate; RAM-gated transcode tests skip honestly on loaded hosts; wrong `progress == 1.0` assertion → `100.0`; dead `unittest.main()` removed. Suite: **6 passed, 3 skipped** (was 2 passed / 7 failed).
- **Legacy entry**: `main.py` CORS wildcard removed, deprecated `@app.on_event` → lifespan, `mcp.app` (missing in FastMCP 3.x, crashed on import) → `mcp.http_app`.
- **Docstring wave**: every tool now carries `## Return Format` + `## Examples`; signatures use `Annotated[..., Field(...)]` (agentic `ctx` untouched).
- Removed 11 tracked `.bak` dross files; deduped ruff `ignore` list.
- Live-proven: `uvicorn handbrake_mcp.server:app` → `/health` 200 (17 tools), `/api/capabilities` 200.

### Notes
- Docker stack still maps host port 8000 (container-internal convention; not the live path — native Windows on 10874/10875 is). `manifest.json`/`glama.json` remain git-ignored via the `*.json` line (pre-existing) — on-disk fixes are local-only until that ignore is narrowed.

## [Unreleased] — 2026-10-22 (assfix)

### Fixed (assfix handbrake-mcp, SOTA Score 14/100 → in progress)
- **CRITICAL CORS wildcard**: `allow_origins` no longer contains `"*"`; explicit localhost/goliath/tauri origins + unconditional LAN/Tauri `allow_origin_regex` (`src/handbrake_mcp/server.py`).
- **CRITICAL MCPB `${PWD}`**: `manifest.json` + `mcpb/manifest.json` `PYTHONPATH` now `${__dirname}` (Claude Desktop does not expand `${PWD}`); manifests bumped to 1.1.1 to match pyproject.
- **HIGH silent swallows**: removed `S110`/`S112` from ruff `ignore`; fixed 3 real `except: pass` sites (bridge proxy, nvidia-smi probe, disk-space check) to log warnings.
- **HIGH lifespan**: FastAPI app now composes `mcp_app.lifespan` (session manager starts for real clients, BUG-038 class).
- **HIGH shutdown**: new `handbrake_shutdown` MCP tool + `POST /api/shutdown` (200 now, exit ~500 ms later) for the fleet launcher.
- **HIGH justfile gaps**: added `serve`, `test`, `fmt`, `mcpb-pack` recipes.
- **HIGH pyright source errors**: widened `transcode_video options` type, `batch_transcode jobs` typing with safe casts, `os.sys.platform` → `sys.platform`, `get_provider_status` return `dict[str, Any]`.
- **MEDIUM gates**: added `T20` to ruff select; added `pytest-cov` to `dependency-groups dev` (collect works, 9 tests); added `.pre-commit-config.yaml` + `scripts/pre-commit-biome.ps1`; `.gitignore` now covers `node_modules/`, `*.mcpb`, `reports/`, `*.bak.*`.

### Known remaining (deferred, still OPEN)
- 7 pytest failures are environmental (Goliath RAM ~87% trips the 85% resource gate; HandBrakeCLI not installed → integration tests cannot run).
- Runt sole domain skill (`SUGGESTED: skillbuild handbrake-mcp`), docstring `## Return Format`/`## Examples` + `Annotated` wave, bun migration, Prefab cards, session-context channels, launcher unification.

## [Unreleased] — 2026-06-14

### Added
- Tauri native wrapper (native/ directory) with bundle.resources + std::process::Command
- CUA-NSIS: just cua-nsis-test recipe, scripts/cua-smoke.py, scripts/cua-nsis-config.json
- Tauri CORS: tauri://localhost origins for WebView API access
- NSIS installer at dist/ and native/target/release/bundle/nsis/

### Changed
- Frontend API calls use absolute http://127.0.0.1:{port} URLs in production build
- CORS middleware includes allow_origin_regex for tauri.localhost
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
