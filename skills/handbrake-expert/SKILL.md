# HandBrake Expert Skill (SOTA 2026)

This skill provides expert guidance for autonomous and manual video transcoding workflows using the HandBrake MCP server.

## CORE CAPABILITIES

1. **Hardware-Accelerated Transcoding (NVENC)**
   - Specialized for RTX 4090 architecture.
   - Use `AV1 NVENC` for the best quality/bitrate ratio in 2026.
   - Target CRF (Constant Quality): 24-28 (equivalent to x265 slow).

2. **Autonomous Optimization**
   - Use `handbrake_agentic_workflow` for multi-step goals.
   - Agents should leverage `sampling` to determine optimal bitrates for target devices (e.g. iPad, Vision Pro, Plex).

3. **Watch Folder Orchestration**
   - Automated detection and ingestion of raw media files.
   - Collision detection and parallel processing management.

## BEST PRACTICES

### 1. Codec Selection
| Scenario | Codec | Rationale |
|----------|-------|-----------|
| **Archival** | x265 (HEVC 10-bit) | Maximum compatibility/efficiency |
| **Speed** | AV1 NVENC | Peak 4090 performance |
| **Web/Misc** | x264 | Universal playback |

### 2. Audio Standards
- **Downmixing**: Use `AAC (avcodec)` for mobile compatibility.
- **Pass-through**: Always use `Auto Passthru` for DTS/AC3 if preservation is required.

### 3. Container Management
- Default to **MKV** for library preservation (multi-track support).
- Use **MP4** for direct web injection and older hardware support.

## TROUBLESHOOTING

- **Black Screen Dashboard**: Ensure backend is running on port 10875 and `/health` is reachable.
- **NVENC Failure**: Verify latest NVIDIA drivers are installed and `nvidia-smi` is in the system path.
