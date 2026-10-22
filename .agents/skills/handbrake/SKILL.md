---
name: handbrake
description: Video transcoding with HandBrakeCLI — transcode, batch-queue, and monitor encoding jobs
---

# HandBrake skill

Transcode videos with HandBrakeCLI through the handbrake-mcp tool surface.

## Before starting work

1. Check provider health: `get_provider_status()`
2. List presets for the task: `get_presets()`

## Core workflow

- Single file: `transcode_video(input_path, output_path, preset?)` → returns `job_id`
- Many files: `batch_transcode(jobs, default_preset?)` → returns one response per job
- Monitor: `get_job_status(job_id)` (poll every 5–30 s); stop with `cancel_job(job_id)`

## At end of work

- Report job IDs and final `get_job_status()` for any transcodes started
- Note failed jobs with their error strings
