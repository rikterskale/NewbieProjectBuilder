[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$BuilderHome = Join-Path ([Environment]::GetFolderPath("MyDocuments")) "NewbieProjectBuilder"
$LogFolder = Join-Path $BuilderHome "logs"
New-Item -ItemType Directory -Force -Path $LogFolder | Out-Null
$BootstrapLog = Join-Path $LogFolder ("bootstrap-windows-{0}.log" -f (Get-Date -Format "yyyyMMdd-HHmmss"))

function Write-BootstrapLog {
    param([string]$Message)
    $Line = "{0} {1}" -f (Get-Date -Format "o"), $Message
    $Line | Tee-Object -FilePath $BootstrapLog -Append
}

Write-Host "============================================================"
Write-Host " NEWBIE PROJECT BUILDER"
Write-Host " Safe setup for people with no computer experience"
Write-Host "============================================================"
Write-Host ""
Write-Host "Nothing will be published or deleted without your permission."
Write-Host "Bootstrap log: $BootstrapLog"
Write-Host ""
Write-BootstrapLog "Launcher root: $Root"

$PythonCommand = $null
$PythonPrefix = @()
if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" 2>$null
    if ($LASTEXITCODE -eq 0) {
        $PythonCommand = "py"
        $PythonPrefix = @("-3")
    }
}
if (-not $PythonCommand -and (Get-Command python -ErrorAction SilentlyContinue)) {
    & python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)" 2>$null
    if ($LASTEXITCODE -eq 0) {
        $PythonCommand = "python"
    }
}

if (-not $PythonCommand) {
    Write-Host "Python 3.11 or newer was not found."
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        Write-BootstrapLog "ERROR NPB-010: WinGet is unavailable."
        Write-Host ""
        Write-Host "ERROR NPB-010: Windows Package Manager was not found."
        Write-Host "Open Microsoft Store, install or update App Installer, then run this file again."
        exit 10
    }
    $Answer = Read-Host "Install Python 3.12 using the exact WinGet package? Type YES to continue"
    if ($Answer -cne "YES") {
        Write-BootstrapLog "Python installation declined."
        Write-Host "No software was installed."
        exit 0
    }
    Write-BootstrapLog "Installing exact package Python.Python.3.12 through WinGet."
    & winget install --id Python.Python.3.12 --exact --accept-source-agreements --accept-package-agreements 2>&1 |
        Tee-Object -FilePath $BootstrapLog -Append
    if ($LASTEXITCODE -ne 0) {
        Write-BootstrapLog "ERROR NPB-103: Python installation returned $LASTEXITCODE."
        Write-Host ""
        Write-Host "ERROR NPB-103: Python installation failed."
        Write-Host "Review this log: $BootstrapLog"
        exit 103
    }
    Write-Host "Python was installed. Close this window, then double-click START-WINDOWS.cmd again."
    exit 0
}

$env:PYTHONPATH = Join-Path $Root "src"
Write-BootstrapLog "Starting shared Python builder with $PythonCommand."
& $PythonCommand @PythonPrefix -m newbie_project_builder --home $BuilderHome menu
$ExitCode = $LASTEXITCODE
Write-BootstrapLog "Builder exit code: $ExitCode"
if ($ExitCode -ne 0) {
    Write-Host "The builder stopped safely. Review the message above and log folder: $LogFolder"
}
exit $ExitCode
