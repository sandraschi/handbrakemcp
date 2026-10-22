# Onboarding — handbrake-mcp

## What this is for

handbrake-mcp gives AI agents (and you, via the dashboard) a safe control plane
for **video transcoding with HandBrakeCLI**: queue single files, batch whole
folders, watch folders for new arrivals, and track progress with ETA. It is a
bridge to the HandBrake engine — **not** a video player, not an editor, and it
does not ship the encoder itself. Without HandBrakeCLI installed, the bridge
stands but every transcode fails: that one install is the whole onboarding.

## Cost and accounts (money / CC)

| Question | Answer |
|----------|--------|
| Do I need an account? | No |
| Free tier? | Yes — everything here is free and unlimited |
| Credit card required? | No |
| Ongoing cost? | Free (electricity for your GPU) |
| Who bills? | Nobody. HandBrake is free open source (GPLv2) |

## Prerequisites outside this repo

- **HandBrakeCLI** (the engine — this is the one hard requirement):
  - Windows: `winget install -e --id HandBrake.HandBrake.CLI`, **then restart
    your terminal** so the new PATH entry (a `HandBrakeCLI` command alias)
    becomes visible. ~15 MB download.
  - macOS: `brew install handbrake` (includes `HandBrakeCLI`).
  - Linux: `sudo apt install handbrake-cli` (Debian/Ubuntu).
- Optional but recommended: an **NVIDIA GPU + current drivers** for
  hardware-accelerated presets (`nvidia-smi` on PATH proves it). CPU encoding
  works everywhere, just slower.
- `ffmpeg` — only needed if you run the integration tests (it fabricates the
  test video). Not needed for real use.

## First-timer setup steps

1. Install the engine (Windows):
   ```powershell
   winget install -e --id HandBrake.HandBrake.CLI --silent --accept-package-agreements --accept-source-agreements
   ```
   Close and reopen your terminal afterwards — winget command aliases only
   appear in new shells.
2. Prove the engine works:
   ```powershell
   HandBrakeCLI --version
   # HandBrake 1.11.2 (...) — plus nvenc/nvdec lines on NVIDIA machines
   ```
3. Start the stack (`just bootstrap` once, then `just serve` for the backend
   on :10875 and the frontend on :10874 — see INSTALL.md Options A–D).
4. Open the dashboard and confirm the HandBrake panel shows **CLI detected**.
   If it shows the red onboarding button instead, go back to step 1.

## Pitfalls

- **New terminal required.** The #1 failure: installing HandBrakeCLI and
  testing in the *same* shell. The `HandBrakeCLI` alias does not exist there.
  Open a fresh terminal (same reason the service checks PATH at startup).
- **The bridge is not the engine.** `get_presets()` returns a small fallback
  list (`Fast 1080p30`, …) when the CLI is missing — a working tool call with
  fallback presets does NOT mean onboarding is done. Trust the
  `instance_configured` field, not vibes.
- **CPU vs GPU presets.** Presets with NVENC in the name need NVIDIA drivers;
  on CPU-only machines they fail at encode time. Check `nvidia-smi` first.
- **RAM gate.** The service refuses new encodes when host RAM exceeds 85%.
  If jobs fail instantly on a busy machine, that is the gate working — free
  memory, don't hammer retries.
- **HBB_PATH override.** If your CLI lives somewhere exotic, set the `HBB_PATH`
  env var (or `handbrake_path` in MCPB user config) to its full path instead
  of relying on PATH detection.
- **Transcoding is slow and lossy.** Keep originals until you have watched the
  output. `delete_original` defaults to off for a reason.

## Sanity check

Onboarding worked when ALL of these are true:

- `GET http://127.0.0.1:10875/health` returns
  `"handbrake": {"cli_available": true, "instance_configured": true}` with a
  real `cli_version` (not `"unknown"`).
- Dashboard shows the green CLI panel (no red onboarding button).
- `get_provider_status()` returns `"status": "ready"` with a populated
  `supported_presets` list (dozens of entries, not just the 3 fallbacks).
- Optional end-to-end: transcode a small clip and watch it reach
  `completed` at `progress: 100.0` via `get_job_status()`.

## Declared doubles

What works **without** finishing onboarding (no silent fakes):

- Everything read-only works: `system_status`, `show_status_card`,
  `get_job_status` for existing jobs, help tools, the full dashboard shell.
- `get_presets()` / `get_loaded_models()` return the **declared 3-item
  fallback list** when the CLI is missing — the service logs a warning, and
  the dashboard red CTA stays up. Fallback presets are labelled as such;
  they are not presented as the live set.
- The dashboard has **no mock jobs, no sample KPIs, no MOCK badges needed**:
  empty states are honest ("No active jobs in stream"). There is nothing that
  looks live but isn't, so there is nothing to clear after onboarding.
