# Copilot instructions — handbrake-mcp

## Session Context (HandBrake MCP)

You have video transcoding tools via HandBrakeCLI: transcode_video, batch_transcode, job monitoring.

**Before starting work:**
1. Check provider health: get_provider_status()
2. List presets for the task: get_presets()

**At end of work:**
- Report job IDs and final get_job_status() for any transcodes started
- Note failed jobs with their error strings

## Repo notes

- Canonical live server: `src/handbrake_mcp/server.py` (`handbrake_mcp.server:app`).
  `src/handbrake_mcp/main.py` is the legacy/Docker entry — prefer `server.py`.
- Responses are dialogic dicts with `success`/`message`; shared errors go through
  `_error_response()` in `tools/utility_tools.py` (logs via `logger.exception`).
- Never use bare `except: pass` (ruff S110/S112 are enforced, not ignored).
- Ports: backend 10875, frontend (`web_sota/`) 10874 — never hardcode others.
