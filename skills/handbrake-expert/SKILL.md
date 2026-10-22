---
name: handbrake-expert
description: Expert video transcoding with HandBrakeCLI — transcode, batch, monitor, optimize for devices, troubleshoot
---

# HandBrake Expert Skill

Domain skill for the handbrake-mcp server. Two audiences: **agents** (tool-first
workflows below) and **humans** (codec guidance at the bottom).

## Agent routing

- Single file or a defined list → `transcode_video` / `batch_transcode` directly.
  Do NOT invoke the agentic workflow for something one tool call answers.
- Vague multi-step goal ("make my library iPad-ready") →
  `handbrake_agentic_workflow(goal)` for a sampled plan, then execute it.
- Fleet maintenance, launcher, or packaging questions → repo docs
  (`docs/`, `INSTALL.md`), not these tools.

## Tool catalog (real names — verified against `mcp.list_tools()`)

| Operation | Signature | Returns |
|---|---|---|
| `transcode_video` | `(input_path, output_path, preset?, options?)` | `TranscodeResponse(job_id, status, ...)` |
| `batch_transcode` | `(jobs[{input_path, output_path, preset?, options?}], default_preset?)` | `list[TranscodeResponse]`, one per job |
| `get_job_status` | `(job_id)` | `JobStatusResponse(status, progress 0–100, ...)` |
| `cancel_job` | `(job_id)` | `bool` |
| `get_presets` / `get_loaded_models` | `()` | `list[str]` preset names |
| `get_provider_status` / `system_status` / `show_status_card` | `()` | health dict / text / Prefab card |
| `help` / `multilevel_help` / `advanced_help` / `tool_categories` / `search_tools` | `(...)` | formatted help strings |
| `handbrake_agentic_workflow` | `(goal)` + sampling ctx | Markdown plan |
| `handbrake_optimize_library` | `(source_dir, target_device)` + sampling ctx | device strategy |
| `handbrake_shutdown` | `()` | exits ~500 ms after responding |

## Workflows

### Workflow 1 — transcode and track to completion

```python
r = await transcode_video("/videos/in.mp4", "/videos/out.mkv", preset="Fast 1080p30")
# poll every 5–30 s until terminal
s = await get_job_status(r.job_id)   # queued → processing → completed
```

### Workflow 2 — batch a folder, then report

```python
jobs = [{"input_path": str(p), "output_path": str(p.with_suffix(".mkv"))} for p in Path("/watch").glob("*.mp4")]
results = await batch_transcode(jobs, default_preset="Fast 1080p30")
failed = [x for x in results if x.status == "failed"]
for x in results: await get_job_status(x.job_id)   # final states for the report
```

### Workflow 3 — stuck or unwanted job

```python
s = await get_job_status("job_12345")
if s.status in ("queued", "processing"): await cancel_job("job_12345")
```

## Errors and recovery

- `transcode_video` returns `status="failed"` with `error` (file missing,
  unwritable output dir, CLI unavailable) — no exception, check the field.
- `get_job_status` returns `status="not_found"` for expired/unknown ids.
- Starting encodes while host RAM is over the 85% service gate raises
  `ValueError` — free memory or wait; do NOT retry in a tight loop.
- Integration tests skip transcode cases on a loaded host for the same reason
  (see `tests/test_handbrake.py::skip_if_host_loaded`).

## Configuration

- `HandBrakeCLI` must be on PATH (`winget install HandBrake.HandBrake.CLI`).
- Server: stdio via `handbrake_mcp.stdio_main`; HTTP bridge
  `handbrake_mcp.server:app` on 127.0.0.1:10875 (`/health`, `/api/shutdown`).
- Dashboard (`web_sota/`) on 10874. Canonical entry is `server.py`;
  `main.py` is the legacy/Docker entry.

## Human guidance — codec selection (RTX 4090 / Goliath)

| Scenario | Codec | Rationale |
|---|---|---|
| Archival | x265 HEVC 10-bit | efficiency + compatibility |
| Speed | AV1 NVENC | peak 4090 throughput |
| Universal playback | x264 | plays everywhere |

- Audio: AAC for mobile, Auto Passthru for DTS/AC3 preservation.
- Containers: MKV for library preservation, MP4 for web/older hardware.
- Quality starting point: CRF-equivalent 24–28; verify on your own eyes.

## Troubleshooting

- Dashboard unreachable → backend on 10875? `GET /health` 200?
- NVENC failure → NVIDIA drivers current? `nvidia-smi` on PATH?
- Empty preset list → CLI missing (fallback list engages) — install HandBrakeCLI.
- `POST /api/shutdown` is the orderly stop (fleet launcher calls it pre-restart).
