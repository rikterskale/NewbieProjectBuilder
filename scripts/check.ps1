[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Push-Location $Root
try {
    # Prefer `python` from the active PATH so virtual environments and
    # actions/setup-python use the interpreter where development tools were
    # installed. Fall back to the Windows Python launcher only when needed.
    $PythonCommand = $null
    [string[]]$PythonPrefix = @()
    if (Get-Command python -ErrorAction SilentlyContinue) {
        $PythonCommand = "python"
    } elseif (Get-Command py -ErrorAction SilentlyContinue) {
        $PythonCommand = "py"
        $PythonPrefix = @("-3")
    } else {
        throw "Python 3 was not found. Run the setup guide before running checks."
    }

    function Invoke-Python {
        param([Parameter(Mandatory = $true)][string[]]$PythonArguments)
        [string[]]$CommandArguments = @($PythonPrefix) + @($PythonArguments)
        & $PythonCommand @CommandArguments
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }

    Write-Host "[1/7] Compiling Python files..."
    Invoke-Python -PythonArguments @("-m", "compileall", "-q", "src")
    Write-Host "[2/7] Running Ruff..."
    Invoke-Python -PythonArguments @("-m", "ruff", "check", ".")
    Write-Host "[3/7] Running mypy..."
    Invoke-Python -PythonArguments @("-m", "mypy", "src")
    Write-Host "[4/7] Running tests and coverage..."
    Invoke-Python -PythonArguments @("-m", "pytest")
    Write-Host "[5/7] Running Bandit..."
    Invoke-Python -PythonArguments @("-m", "bandit", "-r", "src", "-ll")
    Write-Host "[6/7] Auditing dependencies..."
    Invoke-Python -PythonArguments @("-m", "pip_audit")
    Write-Host "[7/7] Building packages..."
    Invoke-Python -PythonArguments @("-m", "build")
    Write-Host "All required checks passed."
} finally {
    Pop-Location
}
