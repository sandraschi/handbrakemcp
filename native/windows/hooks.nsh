; Fleet Tauri: kill UI + backend before install/uninstall (backend locks resources/*.exe).
!macro KillFleetProcesses
  DetailPrint "Stopping HandBrake MCP processes..."
  ExecWait 'taskkill /F /IM handbrake-mcp-backend.exe /T' $0
  ExecWait 'taskkill /F /IM handbrake-mcp-native.exe /T' $0
  Sleep 2000
!macroend

!macro NSIS_HOOK_PREINSTALL
  !insertmacro KillFleetProcesses
!macroend

!macro NSIS_HOOK_PREUNINSTALL
  !insertmacro KillFleetProcesses
!macroend
