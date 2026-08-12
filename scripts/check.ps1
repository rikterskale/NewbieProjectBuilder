[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Push-Location $Root
try {
    # Prefer `python` from the active PATH so virtual environments and
    # actions/setup-python use the interpreter where development tools were
    # installed. Fall back to the Windows Python launcher only when needed.
    $Python = if (Get-Command python -ErrorAction SilentlyContinue) {
        @("python")
    } elseif (Get-Command py -ErrorAction SilentlyContinue) {
        @("py", "-3")
    } else {
        throw "Python 3 was not found. Run the setup guide before running checks."
    }

    function Invoke-Python {
        param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments)
        if ($Python.Count -eq 2) {
            & $Python[0] $Python[1] @Arguments
        } else {
            & $Python[0] @Arguments
        }
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }

    Write-Host "[1/7] Compiling Python files..."
    Invoke-Python @("-m", "compileall", "-q", "src")
    Write-Host "[2/7] Running Ruff..."
    Invoke-Python @("-m", "ruff", "check", ".")
    Write-Host "[3/7] Running mypy..."
    Invoke-Python @("-m", "mypy", "src")
    Write-Host "[4/7] Running tests and coverage..."
    Invoke-Python @("-m", "pytest")
    Write-Host "[5/7] Running Bandit..."
    Invoke-Python @("-m", "bandit", "-r", "src", "-ll")
    Write-Host "[6/7] Auditing dependencies..."
    Invoke-Python @("-m", "pip_audit")
    Write-Host "[7/7] Building packages..."
    Invoke-Python @("-m", "build")
    Write-Host "All required checks passed."
} finally {
    Pop-Location
}
