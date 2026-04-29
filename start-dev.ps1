param(
    [switch]$SkipInstall,
    [switch]$NoPortCleanup,
    [int]$BackendPort = 8000,
    [int]$FrontendPort = 5173
)

$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$OutputEncoding = [System.Text.UTF8Encoding]::new()
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendDir = Join-Path $ProjectRoot "backend"
$FrontendDir = Join-Path $ProjectRoot "frontend"
$RunDir = Join-Path $ProjectRoot ".run"

$BackendEnv = Join-Path $BackendDir ".env"
$FrontendEnv = Join-Path $FrontendDir ".env"
$BackendEnvExample = Join-Path $BackendDir ".env.example"
$FrontendEnvExample = Join-Path $FrontendDir ".env.example"

$VenvDir = Join-Path $BackendDir "venv"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
$ViteEntry = Join-Path $FrontendDir "node_modules\vite\bin\vite.js"

$BackendOutLog = Join-Path $RunDir "backend.out.log"
$BackendErrLog = Join-Path $RunDir "backend.err.log"
$FrontendOutLog = Join-Path $RunDir "frontend.out.log"
$FrontendErrLog = Join-Path $RunDir "frontend.err.log"

function Assert-InWorkspace {
    param([string]$Path)
    $resolved = (Resolve-Path -LiteralPath $Path -ErrorAction Stop).Path
    if (-not $resolved.StartsWith($ProjectRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to operate outside workspace: $resolved"
    }
    return $resolved
}

function Ensure-EnvFile {
    param(
        [string]$EnvPath,
        [string]$ExamplePath,
        [string]$Name
    )

    if (-not (Test-Path -LiteralPath $EnvPath)) {
        Copy-Item -LiteralPath $ExamplePath -Destination $EnvPath
        throw "$Name .env was created from .env.example. Please fill the required keys, then run this script again."
    }
}

function Get-ChildProcessIds {
    param([int]$ParentId)
    @(Get-CimInstance Win32_Process -Filter "ParentProcessId=$ParentId" -ErrorAction SilentlyContinue |
        Select-Object -ExpandProperty ProcessId)
}

function Stop-ProcessTree {
    param([int]$ProcessId)
    if ($ProcessId -le 0) { return }

    foreach ($childId in Get-ChildProcessIds -ParentId $ProcessId) {
        Stop-ProcessTree -ProcessId $childId
    }
    Stop-Process -Id $ProcessId -Force -ErrorAction SilentlyContinue
}

function Stop-PortOwners {
    param([int[]]$Ports)
    $owners = @(Get-NetTCPConnection -LocalPort $Ports -State Listen -ErrorAction SilentlyContinue |
        Select-Object -ExpandProperty OwningProcess -Unique |
        Where-Object { $_ -and $_ -ne $PID })

    foreach ($owner in $owners) {
        Write-Host "[setup] Stopping existing listener: PID $owner"
        Stop-ProcessTree -ProcessId $owner
    }
}

function Wait-Port {
    param(
        [int]$Port,
        [int]$TimeoutSeconds = 60
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        if (Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue) {
            return $true
        }
        Start-Sleep -Milliseconds 500
    }
    return $false
}

function Show-RecentLog {
    param(
        [string]$Path,
        [string]$Title
    )

    if (Test-Path -LiteralPath $Path) {
        Write-Host ""
        Write-Host "[$Title]"
        Get-Content -LiteralPath $Path -Tail 40 -ErrorAction SilentlyContinue | ForEach-Object {
            Write-Host $_
        }
    }
}

Assert-InWorkspace $BackendDir | Out-Null
Assert-InWorkspace $FrontendDir | Out-Null

Ensure-EnvFile -EnvPath $BackendEnv -ExamplePath $BackendEnvExample -Name "Backend"
Ensure-EnvFile -EnvPath $FrontendEnv -ExamplePath $FrontendEnvExample -Name "Frontend"

if (-not (Test-Path -LiteralPath $RunDir)) {
    New-Item -ItemType Directory -Path $RunDir -Force | Out-Null
}

if (-not (Test-Path -LiteralPath $VenvPython)) {
    Write-Host "[setup] Creating backend virtual environment..."
    python -m venv $VenvDir
}

if (-not $SkipInstall) {
    Write-Host "[setup] Installing backend dependencies..."
    & $VenvPython -m pip install -r (Join-Path $BackendDir "requirements.txt")

    Write-Host "[setup] Installing frontend dependencies..."
    Push-Location $FrontendDir
    try {
        npm.cmd install
    }
    finally {
        Pop-Location
    }
}

if (-not (Test-Path -LiteralPath $ViteEntry)) {
    throw "Frontend dependencies are missing. Run .\start-dev.ps1 once without -SkipInstall."
}

$NodeCommand = Get-Command node.exe -ErrorAction SilentlyContinue
if (-not $NodeCommand) {
    $NodeCommand = Get-Command node -ErrorAction Stop
}

if (-not $NoPortCleanup) {
    Stop-PortOwners -Ports @($BackendPort, $FrontendPort)
}

foreach ($logFile in @($BackendOutLog, $BackendErrLog, $FrontendOutLog, $FrontendErrLog)) {
    Set-Content -LiteralPath $logFile -Value "" -Encoding UTF8
}

Write-Host "[run] Starting backend on $BackendPort and frontend on $FrontendPort..."

$backendProcess = Start-Process `
    -FilePath $VenvPython `
    -ArgumentList @("-m", "uvicorn", "app.api.main:app", "--reload", "--host", "0.0.0.0", "--port", "$BackendPort") `
    -WorkingDirectory $BackendDir `
    -RedirectStandardOutput $BackendOutLog `
    -RedirectStandardError $BackendErrLog `
    -WindowStyle Hidden `
    -PassThru

$frontendProcess = Start-Process `
    -FilePath $NodeCommand.Source `
    -ArgumentList @("node_modules\vite\bin\vite.js", "--host", "0.0.0.0", "--port", "$FrontendPort") `
    -WorkingDirectory $FrontendDir `
    -RedirectStandardOutput $FrontendOutLog `
    -RedirectStandardError $FrontendErrLog `
    -WindowStyle Hidden `
    -PassThru

if (-not (Wait-Port -Port $BackendPort -TimeoutSeconds 60)) {
    Show-RecentLog -Path $BackendOutLog -Title "backend stdout"
    Show-RecentLog -Path $BackendErrLog -Title "backend stderr"
    throw "Backend did not start on port $BackendPort."
}

if (-not (Wait-Port -Port $FrontendPort -TimeoutSeconds 60)) {
    Show-RecentLog -Path $FrontendOutLog -Title "frontend stdout"
    Show-RecentLog -Path $FrontendErrLog -Title "frontend stderr"
    throw "Frontend did not start on port $FrontendPort."
}

Write-Host ""
Write-Host "Frontend: http://localhost:$FrontendPort"
Write-Host "Backend:  http://localhost:$BackendPort"
Write-Host "API Docs: http://localhost:$BackendPort/docs"
Write-Host ""
Write-Host "Logs:"
Write-Host "  $BackendOutLog"
Write-Host "  $BackendErrLog"
Write-Host "  $FrontendOutLog"
Write-Host "  $FrontendErrLog"
Write-Host ""
Write-Host "Press Ctrl+C to stop both servers."

try {
    while ($true) {
        foreach ($processInfo in @(
            @{ Name = "backend"; Process = $backendProcess; OutLog = $BackendOutLog; ErrLog = $BackendErrLog },
            @{ Name = "frontend"; Process = $frontendProcess; OutLog = $FrontendOutLog; ErrLog = $FrontendErrLog }
        )) {
            $process = $processInfo.Process
            if ($process.HasExited) {
                Show-RecentLog -Path $processInfo.OutLog -Title "$($processInfo.Name) stdout"
                Show-RecentLog -Path $processInfo.ErrLog -Title "$($processInfo.Name) stderr"
                throw "$($processInfo.Name) server exited unexpectedly."
            }
        }
        Start-Sleep -Seconds 2
    }
}
finally {
    Write-Host "[stop] Stopping dev servers..."
    Stop-ProcessTree -ProcessId $backendProcess.Id
    Stop-ProcessTree -ProcessId $frontendProcess.Id
    if (-not $NoPortCleanup) {
        Stop-PortOwners -Ports @($BackendPort, $FrontendPort)
    }
}
