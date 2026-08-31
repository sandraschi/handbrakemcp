# Per-repo fleet start config for handbrake-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'handbrake-mcp'
    BackendPort  = 10875
    FrontendPort = 10874
    HealthPath   = '/health'
    WebRoot      = 'D:\Dev\repos\handbrake-mcp\web_sota'
    Backend = @{
        Kind          = 'uvicorn'
        UvicornTarget = 'handbrake_mcp.server:app'
        SyncExtras    = @('dev')
        Env           = @{ WEB_PORT = '10875' }
    }
    Frontend = @{
        Kind           = 'vite-npm'
        PackageManager = 'npm'
        PortEnvVar     = 'VITE_PORT'
        ApiTargetEnv   = 'VITE_API_TARGET'
    }
}
