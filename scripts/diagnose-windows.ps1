$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$env:PYTHONPATH = Join-Path $Root "src"
$HomePath = Join-Path ([Environment]::GetFolderPath("MyDocuments")) "NewbieProjectBuilder"
if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 -m newbie_project_builder --home $HomePath diagnose
} else {
    & python -m newbie_project_builder --home $HomePath diagnose
}
exit $LASTEXITCODE
